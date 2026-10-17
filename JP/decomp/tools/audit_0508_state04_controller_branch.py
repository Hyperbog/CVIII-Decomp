#!/usr/bin/env python3
"""Finite controller-branch search from synthetic NMI392 ($18=04).

ROM-instruction execution, copied RAM/CPU/mapper state, no reference emulator or
cycle-correct PPU/NMI timing. Search/negative result is never a global proof.
"""
from __future__ import annotations
import argparse,copy,hashlib,json
from pathlib import Path
from trace_6502_vrc6_0508 import Bus,CPU,ROM_SHA

SEEDS={
 'none':lambda f:0,
 'A held':lambda f:1,'B held':lambda f:2,'Select held':lambda f:4,'Start held':lambda f:8,
 'Up held':lambda f:16,'Down held':lambda f:32,'Left held':lambda f:64,'Right held':lambda f:128,
 'Start pulse 2':lambda f:8 if f%2==1 else 0,
 'Start pulse 30':lambda f:8 if f%30==1 else 0,
 'A pulse 5':lambda f:1 if f%5==1 else 0,
 'Up pulse 5':lambda f:16 if f%5==1 else 0,
 'Down pulse 5':lambda f:32 if f%5==1 else 0,
 'Select+Start':lambda f:12 if f%10==1 else 0,
 'A+Down':lambda f:33 if f%5==1 else 0,
 'B+Start':lambda f:10 if f%10==1 else 0,
 '4-directions':lambda f:(16,32,64,128)[(f//8)%4],
 'face+Start':lambda f:(1,2,8,0)[(f//8)%4],
}
def run(rom,n=120):
    prg=rom[16:16+0x40000]
    fixed=lambda a,n:prg[31*0x2000+a-0xE000:31*0x2000+a-0xE000+n]
    assert fixed(0xF6AE,10)==bytes.fromhex('A5 1F 05 2E 05 1D 05 A8 D0 2B')
    # Room-state transition handler increments or directly assigns $18.
    assert fixed(0xE551,7)==bytes.fromhex('E6 18 A9 00 85 19 60')
    b=Bus(rom,raw_bank=0,ppu_status=0x80);c=CPU(b,0xE00B)
    c.run_until(0xE04B,15000);assert c.steps==6417 and c.sp==255
    b.ppu_status=0
    for f in range(1,393):
        b.controller1_bits=8 if f%30==1 else 0
        c.interrupt(0xFFFA);c.run_until(0xE04B,c.steps+70000)
        assert c.sp==255
    assert b.ram[0x18]==4 and b.ram[0x19]==0,(b.ram[0x18],b.ram[0x19])
    anchor={'original_instructions_through_manual_NMI392':c.steps,
            '18':b.ram[0x18],'19':b.ram[0x19],
            '2C':b.ram[0x2C],'2D':b.ram[0x2D],
            '07A0':b.ram[0x7A0],'07A6':b.ram[0x7A6],
            'PC':f'{c.pc:04X}','raw_bank':b.raw_bank,'stack_pointer':c.sp}
    assert c.pc==0xE04B
    # Output register histories need not be part of cloned machine state.
    b.ppu_writes.clear();b.vram_writes.clear();b.apu_writes.clear();b.mapper_writes.clear()
    b.unknown_io_reads.clear();b.unknown_io_writes.clear()
    results=[]
    for name,fn in SEEDS.items():
        bus,cpu=copy.deepcopy((b,c))
        start=cpu.steps
        values18={int(bus.ram[0x18])}; values2c={int(bus.ram[0x2C])}
        changes=[];old=None;failure=None;first_target=None
        for t in range(1,n+1):
            bus.controller1_bits=fn(t)
            try:
                cpu.interrupt(0xFFFA);cpu.run_until(0xE04B,cpu.steps+70000)
                assert cpu.sp==255
            except (AssertionError,IndexError,ValueError) as e:
                failure={'NMI_after_fork':t,'pc':f'{cpu.pc:04X}','error':str(e)[:220]}
                break
            state=(int(bus.ram[0x18]),int(bus.ram[0x19]),int(bus.ram[0x2C]),int(bus.ram[0x2D]),int(bus.ram[0x7A0]),int(bus.ram[0x7A6]))
            values18.add(state[0]);values2c.add(state[2])
            if state!=old:
                changes.append({'NMI_after_fork':t,'18':state[0],'19':state[1],'2C':state[2],
                                '2D':state[3],'07A0':state[4],'07A6':state[5]})
                old=state
            if state[0] in (0x0C,0x0D):
                first_target={'at_NMI':t,'18':state[0],'19':state[1]}
                break
        else:t=n
        out={'controller_policy':name,'NMIs_successfully_executed':t-(1 if failure else 0),
             'additional_instruction_steps':cpu.steps-start,
             'observed_18_values':sorted(values18),'observed_2C_values':sorted(values2c),
             'first_room_selector_0C_or_0D':first_target,'changes':changes[:120],
             'failure':failure}
        results.append(out)
        print('BRANCH',name,'NMIs',out['NMIs_successfully_executed'],
              'steps',out['additional_instruction_steps'],'selectors',out['observed_18_values'],
              'room',bool(first_target),'fail',failure is not None,flush=True)
    return {'status':'CONDITIONAL_STATE04_ARTIFICIAL_CONTROLLER_BRANCH_SEARCH_NOT_GAMEPLAY',
        'jp_ROM_SHA256':ROM_SHA,'anchor':anchor,'per_branch_NMI_budget':n,
        'branches':results,'policies_tested':len(results),
        'total_NMIs_executed_after_anchor':sum(x['NMIs_successfully_executed'] for x in results),
        'total_branch_instruction_steps':sum(x['additional_instruction_steps'] for x in results),
        'observed_global_18':sorted(set().union(*(set(x['observed_18_values']) for x in results))),
        'room_entry_witnesses':[x['controller_policy'] for x in results if x['first_room_selector_0C_or_0D']],
        'exclusions':['Manual NMI schedule, simplified PPUSTATUS, no mapper IRQ timing',
                       'Input from fork of artificial Start-pulse path, not original controller playthrough',
                       'Negative search does not establish unreachable states',
                       'No strict PRG bytes, no VPP credit'],
        'strict_new_PRG_bytes':0,'strict_PRG_floor':49404,'vpp':24}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('rom');p.add_argument('output');p.add_argument('--nmis',type=int,default=120);a=p.parse_args()
    assert a.nmis>=1
    rom=Path(a.rom).read_bytes();assert len(rom)==393232 and hashlib.sha256(rom).hexdigest()==ROM_SHA
    report=run(rom,a.nmis)
    Path(a.output).write_text(json.dumps(report,indent=2)+'\n')
    print('PASS',report['policies_tested'],'branches',report['total_NMIs_executed_after_anchor'],
          'NMIs',report['total_branch_instruction_steps'],'instr; room witnesses',report['room_entry_witnesses'])
