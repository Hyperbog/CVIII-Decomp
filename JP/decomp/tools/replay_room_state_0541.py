#!/usr/bin/env python3
"""Original JP fixed E526 -> raw0A state2/substate0 -> 0E room loader.

Scoped to RAM $19=2,$68=0,$07A6=9 (sentinel), room index 0..4.
Executes authentic 6502 instructions including two E7FB inline-pointer tail
jumps, B873 sentinel gate, E785 slot clearing, FB96/E2D0 bank reads.
Compares host-translated C++ and CPU trace; NOT a live NMI/whole-game proof.
"""
from __future__ import annotations
import argparse, hashlib, json, subprocess, tempfile, sys
from pathlib import Path
from replay_room_loader_0540 import CPU, original_frame, JP_SHA, BANK0A_SHA, BANK0E_SHA, ROOT
sys.path.insert(0,str(ROOT/'SharedDecomp'))
from workflow import trace_diff, atomic_json, EvidenceError

FIELDS=(0x400,0x41C,0x438,0x454,0x470,0x48C,0x4A8,0x54E)

def fixture(seed:int,idx:int):
    ram=bytearray(2048)
    for x in range(1,23):
        for k,base in enumerate(FIELDS):
            ram[base+x]=(seed*13+x*17+k*31)&255
    ram[0x19]=2;ram[0x68]=0;ram[0x7A6]=9;ram[0x7A0]=idx
    return ram

class StateCPU(CPU):
    def __init__(self,prg:bytes,idx:int,seed:int):
        super().__init__(prg,idx,seed)
        self.ram=fixture(seed,idx)
        # The superclass created a synthetic caller return $8FFF on the
        # 6502 stack; preserve its two bytes after installing RAM fixtures.
        self.ram[0x1FD]=0x8F
        self.ram[0x1FC]=0xFF
        self.pc=0xE526
        self.state_visits=[];self.state_mapper_writes=0
        self.mapper_writes=[];self.read_0e=[];self.steps=0

    def run(self):
        while self.pc!=0xB6B4:
            self.steps+=1
            if self.steps>25000:raise EvidenceError(f'CPU state chain did not reach loader exit: {self.pc:04X}')
            at=self.pc;self.state_visits.append(at)
            op=self.read(at)
            # Operand is fetched lazily for valid instructions at bank windows.
            v=self.read((at+1)&65535)
            def word():return v|(self.read((at+2)&65535)<<8)
            p=at+1
            if op==0xAD:self.a=self.read(word());self.nz(self.a);p=at+3
            elif op==0xA9:self.a=v;self.nz(self.a);p=at+2
            elif op==0xA0:self.y=v;self.nz(self.y);p=at+2
            elif op==0xA2:self.x=v;self.nz(self.x);p=at+2
            elif op==0xA5:self.a=self.read(v);self.nz(self.a);p=at+2
            elif op==0xA4:self.y=self.read(v);self.nz(self.y);p=at+2
            elif op==0x0A:self.c=bool(self.a&128);self.a=(self.a<<1)&255;self.nz(self.a)
            elif op==0x4A:self.c=bool(self.a&1);self.a>>=1;self.nz(self.a)
            elif op==0xA8:self.y=self.a;self.nz(self.y)
            elif op==0x84:self.write(v,self.y);p=at+2
            elif op==0xB9:self.a=self.read((word()+self.y)&65535);self.nz(self.a);p=at+3
            elif op==0xB1:
                ptr=self.read(v)|(self.read((v+1)&255)<<8)
                addr=(ptr+self.y)&65535
                self.a=self.read(addr);self.nz(self.a)
                if self.bank==14:
                    if not 0x8000<=addr<0xC000:raise EvidenceError('mapped read outside bank')
                    self.read_0e.append((at,addr,self.y,self.a))
                elif self.bank!=10 or not (0xB4D1<=addr<=0xB6A3):
                    raise EvidenceError(f'indirect read outside audited inline tables {self.bank}: {addr:04X}')
                p=at+2
            elif op==0x85:self.write(v,self.a);p=at+2
            elif op==0x8D:self.write(word(),self.a);p=at+3
            elif op==0x9D:self.write((word()+self.x)&65535,self.a);p=at+3
            elif op==0x29:self.a&=v;self.nz(self.a);p=at+2
            elif op==0xC9:self.c=self.a>=v;self.nz((self.a-v)&255);p=at+2
            elif op==0xE0:self.c=self.x>=v;self.nz((self.x-v)&255);p=at+2
            elif op==0xF0:
                p=at+2
                if self.z:p=(p+(v if v<128 else v-256))&65535
            elif op==0xD0:
                p=at+2
                if not self.z:p=(p+(v if v<128 else v-256))&65535
            elif op==0x90:
                p=at+2
                if not self.c:p=(p+(v if v<128 else v-256))&65535
            elif op==0xB0:
                p=at+2
                if self.c:p=(p+(v if v<128 else v-256))&65535
            elif op==0x18:self.c=False
            elif op==0x38:self.c=True
            elif op==0x6D:
                value=self.read(word());s=self.a+value+int(self.c)
                self.c=s>255;self.a=s&255;self.nz(self.a);p=at+3
            elif op==0xE8:self.x=(self.x+1)&255;self.nz(self.x)
            elif op==0xC8:self.y=(self.y+1)&255;self.nz(self.y)
            elif op==0x48:self.push(self.a)
            elif op==0x68:self.a=self.pop();self.nz(self.a)
            elif op==0x20:
                target=word()
                if target not in (0xFB96,0xE2D0,0xE7FB,0xB689,0xB873,0xE785,0xB7F7):
                    raise EvidenceError(f'unexpected JSR {target:04X} at {at:04X}')
                self.push((at+2)>>8);self.push((at+2)&255);p=target
            elif op==0x60:p=(self.pop()|(self.pop()<<8))+1
            elif op==0x4C:p=word()
            elif op==0x6C:
                ptr=word();lo=self.read(ptr);hi=self.read((ptr&0xff00)|((ptr+1)&255))
                p=lo|(hi<<8)
                if at!=0xE811 or p not in (0xB597,0xB6A4):
                    raise EvidenceError(f'unexpected indirect jump from {at:04X} to {p:04X}')
            else:raise EvidenceError(f'unsupported 6502 opcode {op:02X} @ {at:04X} bank {self.bank:02X}')
            self.pc=p&65535
        required=(0xE526,0xE2D0,0xB4CC,0xE7FB,0xE811,0xB597,0xB689,
                  0xB6A4,0xB873,0xB8A4,0xE785,0xB7F7,0xFB96)
        missing=[a for a in required if a not in self.state_visits]
        if missing:raise EvidenceError(f'original state chain skipped required sites {missing}')
        if self.sp!=0xF9 or self.bank!=10 or self.ram[0x23]!=10:
            raise EvidenceError(f'state chain stack/bank restoration failed SP={self.sp:02X} bank={self.bank}')
        if self.ram[0x19]!=2 or self.ram[0x68]!=0 or self.ram[0x7A6]!=9:
            raise EvidenceError('unexpected state selector mutation')
        return self

def frame(cpu:StateCPU,index:int,seed:int,step:int)->dict:
    saved=cpu.mapper_writes
    if saved[0]!=(0xE2D2,10):raise EvidenceError('missing initial E526 bank switch')
    cpu.mapper_writes=saved[1:]
    try:base=original_frame(cpu,index,seed,step)
    finally:cpu.mapper_writes=saved
    base.update({'cpu_path':'E526/B4CC/E7FB/B597/B689/B6A4/B873/E785/B7F7/FB96/E2D0',
        'state_19':cpu.ram[0x19], 'substate_68':cpu.ram[0x68],
        'room_stream_state_7a6':cpu.ram[0x7A6], 'pc_after_loader':cpu.pc,
        'sp_after_loader':cpu.sp,'original_steps':None,
        'slot_fields':[[cpu.ram[base+x] for base in FIELDS] for x in range(1,23)],
        'state_dispatch_targets':[0xB597,0xB6A4],
        'state_gate':'B8A4_07A6_9_sentinel',
        'state_mapper_write_count':1})
    base.pop('original_steps')
    return base

def _write(path:Path,frames):
    path.write_text(''.join(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n' for x in frames),encoding='utf-8')

def compare(rom:Path,out:Path,compiler:str='g++'):
    game=rom.read_bytes()
    if len(game)!=393232 or hashlib.sha256(game).hexdigest()!=JP_SHA:
        raise EvidenceError('original ROM fingerprint mismatch')
    prg=game[16:16+262144]
    a=prg[10*16384:11*16384]; e=prg[14*16384:15*16384]
    if hashlib.sha256(a).hexdigest()!=BANK0A_SHA or hashlib.sha256(e).hexdigest()!=BANK0E_SHA:
        raise EvidenceError('physical-bank fingerprint mismatch')
    out.mkdir(parents=True,exist_ok=True)
    reference=[]
    for idx in range(5):
        for seed in range(256):
            c=StateCPU(prg,idx,seed).run()
            reference.append(frame(c,idx,seed,len(reference)))
    ref=out/'original_state_chain.jsonl';host=out/'native_state_chain.jsonl'
    _write(ref,reference)
    with tempfile.TemporaryDirectory(prefix='jp-0541-state-') as t:
        tmp=Path(t); pa=tmp/'raw0a.bin';pe=tmp/'raw0e.bin';pa.write_bytes(a);pe.write_bytes(e)
        exe=tmp/'state_native';src=ROOT/'JP/recomp/native/room0a/room_loader_native.cpp'
        subprocess.run([compiler,'-std=c++17','-O2','-Wall','-Wextra','-Werror','-pedantic',str(src),'-o',str(exe)],check=True)
        proc=subprocess.run([str(exe),str(pa),str(pe),'--state-bridge'],check=True,capture_output=True,text=True)
        host.write_text(proc.stdout,encoding='utf-8')
    report=trace_diff(ref,host)
    report.update({'scope':'E526_to_B6B4_state2_substate0_room7a6_9_sentinel',
                   'cases':len(reference), 'original_rom_sha256':JP_SHA,
                   'actual_gameplay_reachability':False,'hardware_frame_parity':False,
                   'partial_state_chain_stops_at_B6B4':True})
    atomic_json(out/'state_bridge_0541_report.json',report)
    if report.get('status')!='PASS':raise EvidenceError('first mismatch '+json.dumps(report))
    print(json.dumps(report,sort_keys=True))
    return report

def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--cxx',default='g++')
    a=p.parse_args();compare(a.rom,a.out,a.cxx)
if __name__=='__main__':main()
