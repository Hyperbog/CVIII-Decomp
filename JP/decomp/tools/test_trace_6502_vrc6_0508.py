#!/usr/bin/env python3
"""Independent cross-audit regression of the reusable 2A03/VRC6 trace harness.

Uses earlier independently audited 0508 partial CPU initialization fixtures;
compares complete ROM-fetched instruction counts, RAM, bus writes and stack.
These remain conditional local executions, not reference emulator traces.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,json,sys
from trace_6502_vrc6_0508 import Bus,CPU,ROM_SHA
from audit_0508_phase9 import CPU as OldPPUCPU
from audit_0508_phase11 import CPU as OldSoundCPU,INSTRUMENTS
from audit_0508_phase10 import EXPECTED_SOUND

SEEDS=(0,1,2,7,17,63,127,255)

def make(rom,fixture,bank=10):
    bus=Bus(rom,bank)
    bus.ram[:]=fixture.ram
    cpu=CPU(bus,fixture.pc)
    cpu.a=fixture.a;cpu.x=fixture.x;cpu.y=fixture.y;cpu.sp=fixture.sp
    cpu.setflag(1,fixture.c);cpu.setflag(2,fixture.z);cpu.setflag(128,fixture.n)
    return cpu

def run(path):
    rom=Path(path).read_bytes()
    assert hashlib.sha256(rom).hexdigest()==ROM_SHA
    prg=rom[16:16+262144]
    tests=0
    original_steps=0
    cases=[]
    for seed in SEEDS:
        for ctrl in (0,4):
            old=OldPPUCPU(prg,(seed*37+17)&255,seed,ctrl)
            cpu=make(rom,old,10)
            cpu.run_until(0x9000,30000)
            assert cpu.steps==10532,cpu.steps
            assert cpu.sp==0xFD
            assert cpu.bus.ram[0x19]==1 and cpu.bus.ram[0x23]==10
            assert cpu.bus.ram[0x7A0]==0 and cpu.bus.ram[0x7A6]==0
            assert cpu.bus.ram[0x781]==(seed*37+17)&255
            assert len(cpu.bus.vram_writes)==2048
            expected=[(((base +i*(32 if ctrl else 1))&0x3FFF),0)
                  for base in (0x2000,0x2400) for i in range(1024)]
            assert cpu.bus.vram_writes==expected
            assert cpu.bus.ppu_ctrl==ctrl
            assert cpu.bus.ram[0x00]==0x46 and cpu.bus.ram[0x01]==0xEC
            cases.append(['room_state_zero_ppu',seed,ctrl,cpu.steps]);tests+=1;original_steps+=cpu.steps
    for seed in range(256):
        old=OldSoundCPU(prg,seed)
        cpu=make(rom,old,10)
        cpu.run_until(0x9000,3000)
        assert cpu.steps==650,(seed,cpu.steps,hex(cpu.pc))
        assert cpu.sp==0xFD
        assert cpu.bus.raw_bank==10 and cpu.bus.ram[0x23]==10
        assert cpu.bus.ram[0x25]==10 and cpu.bus.ram[0x26]==0
        assert cpu.bus.ram[0x19]==2 and cpu.bus.ram[0x68]==0
        assert cpu.bus.ram[0xEF]==0x6B
        assert cpu.bus.ram[0xEB]==5 and cpu.bus.ram[0xEA]==0xFF
        assert [(a,v) for a,v in cpu.bus.apu_writes if (a,v) in EXPECTED_SOUND]==EXPECTED_SOUND
        assert len([x for x in cpu.bus.mapper_writes if x[0]==0x8000])==14
        for slot,ptr in INSTRUMENTS:
            assert cpu.bus.ram[0x06D3+slot]==5
            assert cpu.bus.ram[0x012D+slot]==ptr&255
            assert cpu.bus.ram[0x0136+slot]==ptr>>8
        tests+=1;original_steps+=cpu.steps
    # Page-wrap, stack ABI, carry/overflow, binary 2A03 arithmetic and RMW
    # are also covered separately in the instruction micro-program tests.
    result={
      'status':'BOUNDED_GENERIC_6502_VRC6_REGRESSION_NOT_REFERENCE_FRAME_PARITY',
      'rom_sha256':ROM_SHA,'test_cases':tests,
      'original_instruction_steps':original_steps,
      'ppu_cases':16,'sound_cases':256,
      'ppu_steps_per_case':10532,'sound_steps_per_case':650,
      'per_ppu_case_port_writes':2048,
      'per_sound_case_mapper_8000_writes':14,
      'strict_new_prg_bytes':0,'strict_cumulative_prg_bytes':49404,'vpp':24,
      'limits':['ROM-fetched instructions but synthetic entry state',
            'no reference emulator trace, cycles, IRQ/NMI timing, PPU pixels, or audio waveforms']}
    return result

if __name__=='__main__':
    if len(sys.argv) not in (2,3):raise SystemExit('usage: test_trace_6502_vrc6_0508.py JP_ROM.nes [report.json]')
    result=run(sys.argv[1]);
    if len(sys.argv)==3:Path(sys.argv[2]).write_text(json.dumps(result,indent=2)+'\n')
    print('Generic CPU/mapper ROM parity with earlier independent audits PASS:',result['test_cases'],'cases;',result['original_instruction_steps'],'instructions')
