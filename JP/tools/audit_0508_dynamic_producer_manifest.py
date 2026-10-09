#!/usr/bin/env python3
"""ROM-locked physical instruction/operand/read manifest for synthetic reset-to-NMI runs.

Discovery evidence ONLY: fixed PPUSTATUS and manually scheduled NMIs; no claimed
original console timing, input reachability, native frame parity or strict credit.
"""
from __future__ import annotations
import argparse, hashlib, json
from collections import Counter, defaultdict
from pathlib import Path
from trace_6502_vrc6_0508 import Bus, CPU, ROM_SHA, OPS

WATCH=(0x18,0x19,0x68,0x7A0,0x7A6,0x1F,0x2E,0x1D,0xA8,0x2C,0x2D,0xF8,0x23,0x25)

def phys(bus:Bus,addr:int):
    if 0x8000<=addr<0xC000:return (bus.raw_bank*0x4000)+(addr-0x8000)
    if 0xC000<=addr<0xE000:return (bus.upper_bank*0x2000)+(addr-0xC000)
    if addr>=0xE000:return 31*0x2000+(addr-0xE000)
    return None

class TraceBus(Bus):
    def __init__(self,rom):
        super().__init__(rom,raw_bank=0,ppu_status=0x80)
        self.read_seen=bytearray(262144)
        self.cpu=None
        self.frame=0
        self.producers=defaultdict(Counter)
        self.events=[]
        self.value_domains=defaultdict(set)
        self.unknown_rw_start=(0,0)
    def rb(self,addr:int):
        p=phys(self,addr&65535)
        if p is not None:self.read_seen[p]=1
        return super().rb(addr)
    def wb(self,addr:int,value:int):
        dest=addr&0x7FF
        if (addr&65535)<0x2000 and dest in WATCH:
            old=self.ram[dest]
            site=self.cpu.last_instruction if self.cpu is not None else None
            if site is None:label='unknown'
            else:label=f'{site[1]:02X}:{site[0]:04X}' if site[0]<0xC000 else f'fixed:{site[0]:04X}' if site[0]>=0xE000 else f'upper:{site[0]:04X}'
            self.producers[dest][label]+=1
            self.value_domains[dest].add(value&255)
            if (old!=value and dest in {0x18,0x19,0x68,0x7A0,0x7A6,0x1D,0x2C,0x2D,0xF8}
                and len(self.events)<300):
                self.events.append({'NMI':self.frame,'RAM':f'{dest:04X}','old':old,'new':value&255,
                    'writer':label,'step':self.cpu.steps if self.cpu else 0})
        return super().wb(addr,value)

class TraceCPU(CPU):
    def __init__(self,bus):
        super().__init__(bus,0xE00B)
        bus.cpu=self
        self.code_seen=bytearray(262144)
        self.starts=set()
        self.executions_per_bank=Counter()
        self.opcode_count=Counter()
    def step(self):
        at=self.pc; p=phys(self.bus,at)
        # The official opcode table is ROM-derived and checked by CPU.step.
        op=self.bus.rb(at)
        if op in OPS:
            _,_,size=OPS[op]
            for i in range(size):
                q=phys(self.bus,(at+i)&65535)
                if q is not None:self.code_seen[q]=1
        if p is not None:
            self.starts.add(p)
            self.executions_per_bank[p//8192]+=1
        self.opcode_count[op]+=1
        return super().step()

def run(rom:bytes,pattern:str,nmis:int):
    cb={'none':lambda f:0,'start30':lambda f:8 if f%30==1 else 0,
        'abstart':lambda f:(1,2,8,0)[((f-1)//10)%4],
        'startheld':lambda f:8,'start20':lambda f:8 if f==20 else 0}[pattern]
    bus=TraceBus(rom);cpu=TraceCPU(bus)
    cpu.run_until(0xE04B,15000)
    assert cpu.steps==6417 and cpu.sp==255
    bus.ppu_status=0
    states=[];prev=None
    for f in range(1,nmis+1):
        bus.frame=f;bus.controller1_bits=cb(f)
        cpu.interrupt(0xFFFA)
        cpu.run_until(0xE04B,cpu.steps+70000)
        assert cpu.sp==255
        tup=(bus.ram[0x18],bus.ram[0x19],bus.ram[0x68],bus.ram[0x7A0],bus.ram[0x7A6],bus.ram[0x2C])
        if tup!=prev:
            states.append({'NMI':f,'18':tup[0],'19':tup[1],'68':tup[2],
                           '07A0':tup[3],'07A6':tup[4],'2C':tup[5]})
            prev=tup
    code=cpu.code_seen; reads=bus.read_seen
    bank_rows=[]
    for i in range(32):
        x=i*8192
        cc=sum(code[x:x+8192]); rr=sum(reads[x:x+8192]);xx=sum(1 for t in cpu.starts if x<=t<x+8192)
        if cc or rr:bank_rows.append({'physical_PRG8k':f'{i:02X}','executed_code_and_operand_bytes':cc,
            'all_ROM_read_bytes':rr,'instruction_starts':xx,'instruction_executions':cpu.executions_per_bank[i]})
    sites={f'{k:04X}': [{'writer':site,'writes':count} for site,count in sorted(counter.items())]
           for k,counter in sorted(bus.producers.items())}
    return {'status':'SYNTHETIC_CPU_ROM_EXECUTION_NOT_STRICT_COVERAGE',
        'pattern':pattern,'manual_NMIs':nmis,'total_instructions_including_reset':cpu.steps,
        'distinct_instruction_starts':len(cpu.starts),
        'distinct_executed_code_operand_bytes':sum(code),
        'distinct_all_ROM_read_bytes':sum(reads),
        'code_offsets_digest_sha256':hashlib.sha256(bytes(code)).hexdigest(),
        'all_ROM_read_offsets_digest_sha256':hashlib.sha256(bytes(reads)).hexdigest(),
        'bank_rows':bank_rows,'state_changes':states,'watch_writers':sites,
        'writer_value_domains':{f'{k:04X}':sorted(v) for k,v in sorted(bus.value_domains.items())},
        'sampled_RAM_changes':bus.events,'unknown_io_read_count':len(bus.unknown_io_reads),
        'unknown_io_write_count':len(bus.unknown_io_writes),
        'caveat':'Manually injected NMI; fixed PPU readiness/no IRQ/cycle timing; not authentic gameplay, no strict byte promotion',
        '_masks':(code,reads)}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('rom');parser.add_argument('output');
    parser.add_argument('--nmis',type=int,default=1200);parser.add_argument('--patterns',default='start30,abstart,none');
    parser.add_argument('--scenarios',default=None,help='comma list pattern:count, e.g. start30:1200,abstart:300,none:300')
    a=parser.parse_args()
    rom=Path(a.rom).read_bytes();assert len(rom)==393232 and hashlib.sha256(rom).hexdigest()==ROM_SHA
    results=[];merged_code=bytearray(262144);merged_reads=bytearray(262144)
    jobs=([(x.split(':')[0],int(x.split(':')[1])) for x in a.scenarios.split(',')] if a.scenarios
          else [(x,a.nmis) for x in a.patterns.split(',')])
    assert all(1<=n<=3000 for _,n in jobs)
    for pattern,n in jobs:
        r=run(rom,pattern,n)
        code,reads=r.pop('_masks')
        for i in range(262144):
            if code[i]:merged_code[i]=1
            if reads[i]:merged_reads[i]=1
        results.append(r)
        print('ROM trace',pattern,r['manual_NMIs'],'NMIs',r['total_instructions_including_reset'],
              'instructions',r['distinct_executed_code_operand_bytes'],'unique executed bytes',flush=True)
    baselines={('start30',1200):2966527,('abstart',300):647426,('none',300):1055395}
    for row in results:
        known=baselines.get((row['pattern'],row['manual_NMIs']))
        if known is not None: assert row['total_instructions_including_reset']==known,(row['pattern'],known,row['total_instructions_including_reset'])
    data={'status':'MULTI_BANK_SYNTHETIC_EXECUTION_MANIFEST_NOT_STRICT_CERTIFICATE',
        'rom_sha256':ROM_SHA,'patterns':results,
        'aggregate_scenarios':len(results),
        'aggregate_manual_NMIs':sum(r['manual_NMIs'] for r in results),
        'aggregate_original_instructions':sum(r['total_instructions_including_reset'] for r in results),
        'union_executed_code_operand_bytes':sum(merged_code),
        'union_all_ROM_read_bytes':sum(merged_reads),
        'union_executed_byte_mask_sha256':hashlib.sha256(merged_code).hexdigest(),
        'union_read_byte_mask_sha256':hashlib.sha256(merged_reads).hexdigest(),
        'strict_new_bytes':0,'strict_floor':49404,'vpp':24,
        'proof_limit':'Only synthetic input/manual-NMI conditional execution; overlapping prior ledger not reconciled; no byte promotion'}
    Path(a.output).write_text(json.dumps(data,indent=2)+'\n')
    print('AGGREGATE',data['aggregate_original_instructions'],'steps; unique code/operand',data['union_executed_code_operand_bytes'])
if __name__=='__main__':main()
