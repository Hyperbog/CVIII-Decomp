#!/usr/bin/env python3
"""Bounded JP RESET→150 manually injected NMIs with synthetic PPU/IO.

Uses the *same* general 2A03/Mapper24 instruction core as the room/audio
regressions. This is a ROM-fetched trace under declared environment stubs,
NOT a real console frame/timing/input trace or live 0C/0D room proof.
"""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
from trace_6502_vrc6_0508 import Bus,CPU,ROM_SHA

FRAME_COUNT=150
IDLE_STEPS=(0,12,384)  # six instructions per main-loop rotation
WATCH=(0x18,0x19,0x68,0x7A0,0x7A6)

def test(path):
    rom=Path(path).read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_SHA
    runs=[]
    for idle in IDLE_STEPS:
        bus=Bus(rom,raw_bank=0,ppu_status=0x80)
        cpu=CPU(bus,0xE00B)
        cpu.run_until(0xE04B,15000)
        reset_steps=cpu.steps
        assert reset_steps==6417
        assert cpu.sp==0xFF and bus.raw_bank==0
        assert tuple(bus.ram[k] for k in WATCH)==(0,0,0,0,0)
        assert bus.ram[0]==0 and bus.ram[1]==8
        # The reset wait loops use vblank-ready $2002=80; the deterministic
        # synthetic next-NMI state reads $2002=00. The emulator does not
        # synthesize a PPU clock or IRQ or controller serial input.
        bus.ppu_status=0
        frames=[]
        ppu0=len(bus.ppu_writes)
        for frame in range(1,FRAME_COUNT+1):
            for _ in range(idle):cpu.step()
            assert cpu.pc==0xE04B,(frame,cpu.pc)
            prior=cpu.steps
            cpu.interrupt(0xFFFA)
            assert cpu.pc==0xE057
            cpu.run_until(0xE04B,cpu.steps+70000)
            vals=tuple(bus.ram[k] for k in WATCH)
            assert vals==(0,1,0,0,0),(idle,frame,vals)
            assert cpu.sp==0xFF and bus.ram[0x1C]==0
            assert bus.ram[0x1B]==(frame&255)
            frames.append({'frame':frame,'instructions':cpu.steps-prior,
                'room_18':vals[0],'room_19':vals[1],
                'secondary_68':vals[2], 'room_idx_07A0':vals[3],
                'descriptor_idx_07A6':vals[4],
                'mapped_bank':bus.raw_bank})
        assert len(frames)==FRAME_COUNT
        assert frames[0]['instructions']==5321
        assert bus.raw_bank==0x0D
        runs.append({'idle_instructions_before_each_NMI':idle,
             'reset_instructions':reset_steps,'frame_count':len(frames),
             'total_original_instruction_steps':cpu.steps,
             'NMI_150_steps_last':frames[-1]['instructions'],
             'first_frame':frames[0],'last_frame':frames[-1],
             'frame_trace_sha256':hashlib.sha256(
                json.dumps(frames,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
             'state_domain':sorted({f'{f["room_18"]:02X}/{f["room_19"]:02X}' for f in frames}),
             'ppu_writes_during_NMIs':len(bus.ppu_writes)-ppu0,
             'mapped_PRG_end':f'{bus.raw_bank:02X}'})
    return {'status':'SYNTHETIC_VBLANK_AND_MANUAL_NMI_TRACE_NOT_REFERENCE_PLAYTHROUGH',
        'rom_sha256':ROM_SHA,
        'runs':runs,'synthetic_NMI_injections':FRAME_COUNT*len(runs),
        'total_ROM_instructions_across_runs':sum(x['total_original_instruction_steps'] for x in runs),
        'environment':{
            'RESET_PPUSTATUS':'80 at both VBlank wait reads',
            'NMI_PPUSTATUS':'00 on each $2002 read',
            'IRQ':'none scheduled',
            'controller':'$4016/$4017 synthetic zero',
            'NMI_schedule':'manual after configurable main-loop instruction steps; NOT CPU cycles',
            'PPU':'register writes captured, not rendered/timed'},
        'positive_facts':['RESET instruction path to E04B executes',
            'all tested first NMIs start with 18=19=68=07A0=07A6=0',
            'first NMI changes 19 00->01 under zero controller stub',
            '150 manual NMIs per scenario stay at 18=00/19=01'],
        'proof_limits':['This shows what the JP CPU program does under artificial environment inputs; it is NOT a natural console trace',
            'Real controller input, PPU timing and mapper IRQ are not modeled; 18=0C and room-state liveness not established',
            'No full reference CPU/PPU/APU trace or native full-game parity'],
        'new_strict_prg_bytes':0,'strict_cumulative_prg_bytes':49404,'vpp':24}

if __name__=='__main__':
    if len(sys.argv) not in (2,3):raise SystemExit('usage: test_reset_nmi_trace_0508.py JP_ROM.nes [report.json]')
    r=test(sys.argv[1]);
    if len(sys.argv)==3:Path(sys.argv[2]).write_text(json.dumps(r,indent=2)+'\n')
    print('JP RESET-to-manual-NMI partial trace passed',r['synthetic_NMI_injections'],'NMI injections,',r['total_ROM_instructions_across_runs'],'original ROM instruction steps')
