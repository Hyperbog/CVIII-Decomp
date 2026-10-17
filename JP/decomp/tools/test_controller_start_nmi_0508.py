#!/usr/bin/env python3
"""ROM-fetched RESET + artificial NMI/controller-edge traces, no frame timing.

The source is always the immutable JP ROM. The synthetic environment supplies
PPU readiness and a fixed Start-button schedule (NMI injections 2,3,4).
This is an input-driven bounded program execution proof, not a reference
emulator trace, audio/PPU/IRQ timing certificate, or game-progress liveness.
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path
from trace_6502_vrc6_0508 import Bus, CPU, ROM_SHA

NMIS = 300
IDLE_STEPS = (0,12,384)
WATCH=(0x18,0x19,0x68,0x07A0,0x07A6)
EXPECTED_CHANGES={1:(0,1),2:(0,2),3:(0,3),4:(0,4),261:(0,0),262:(0,1)}

def run(rom_path: str) -> dict:
    rom=Path(rom_path).read_bytes()
    assert len(rom)==393232 and hashlib.sha256(rom).hexdigest()==ROM_SHA
    scenarios=[]
    for idle in IDLE_STEPS:
        bus=Bus(rom,raw_bank=0,ppu_status=0x80)
        cpu=CPU(bus,0xE00B)
        cpu.run_until(0xE04B,15000)
        assert cpu.steps==6417
        assert tuple(bus.ram[p] for p in WATCH)==(0,0,0,0,0)
        assert cpu.sp==0xFF
        bus.ppu_status=0
        change_records=[]
        last=None
        first_start_value=None
        held_edge_value=None
        ppu_writes_before=len(bus.ppu_writes)
        for frame in range(1,NMIS+1):
            for _ in range(idle):cpu.step()
            assert cpu.pc==0xE04B,(idle,frame,cpu.pc)
            # Controller serialization is A,B,Select,Start,Up,Down,Left,Right.
            bus.controller1_bits=0x08 if frame in (2,3,4) else 0x00
            prior=cpu.steps
            cpu.interrupt(0xFFFA)
            assert cpu.pc==0xE057
            cpu.run_until(0xE04B,cpu.steps+70000)
            current=tuple(bus.ram[p] for p in WATCH)
            if last!=current:
                change_records.append({'NMI':frame,'18':current[0],
                                       '19':current[1],'68':current[2],
                                       '07A0':current[3],'07A6':current[4],
                                       'F8':bus.ram[0xF8],
                                       'original_instructions':cpu.steps-prior})
                last=current
            if frame in EXPECTED_CHANGES:
                assert current[:2]==EXPECTED_CHANGES[frame],(idle,frame,current)
            assert current[0]==0 and current[2:]==(0,0,0),(idle,frame,current)
            assert cpu.sp==0xFF and bus.ram[0x1C]==0
            assert bus.ram[0x1B]==frame&255
            if frame==2:
                first_start_value=bus.ram[0xF8]
                assert first_start_value==0x10,(idle,first_start_value)
            if frame==3:
                held_edge_value=bus.ram[0xF8]
                assert held_edge_value==0,(idle,held_edge_value)
        assert bus.raw_bank==0x0D
        assert [x['NMI'] for x in change_records]==[1,2,3,4,261,262],change_records
        scenarios.append({
            'idle_instructions_between_manual_NMI':idle,
            'original_instructions_including_RESET':cpu.steps,
            'manual_NMI_count':NMIS,
            'RESET_to_idle_original_instructions':6417,
            'held_Start_1_bits':0x08,
            'first_Start_flag_F8':first_start_value,
            'held_repeat_Start_flag_F8':held_edge_value,
            'changes':change_records,
            'after_NMI_300':[bus.ram[p] for p in WATCH],
            'final_mapped_raw_prg_bank':bus.raw_bank,
            'PPU_register_writes_during_manual_NMIs':len(bus.ppu_writes)-ppu_writes_before,
        })
    assert [x['original_instructions_including_RESET'] for x in scenarios]==[529829,533429,645029]
    assert sum(x['original_instructions_including_RESET'] for x in scenarios)==1708287
    return {
        'status':'SYNTHETIC_CONTROLLER_INPUT_ORIGINAL_ROM_EXECUTION_NOT_FRAME_REFERENCE',
        'ROM_SHA256':ROM_SHA,
        'NMI_scenarios':scenarios,
        'total_manual_NMIs':NMIS*len(scenarios),
        'total_original_instruction_steps':sum(x['original_instructions_including_RESET'] for x in scenarios),
        'controller_model':'Serial $4016/$4017 latch; 8 ordered bits and post-8 constant one; synthetic Start held for NMI injections 2-4',
        'PPU_status':'$80 during RESET waits; $00 for all manual NMIs',
        'IRQ':'none scheduled',
        'NMI_clock':'manually injected at original ROM idle loop after 0, 12 or 384 original main instructions, NOT frame/cycle-based',
        'proved_under_assumptions':[
            'RESET initializes $18=$19=$68=$07A0=$07A6=$00',
            'first zero-input NMI advances $19 to $01',
            'synthetic Start press sets $F8=$10 and causes $19 to advance from $01 to $02',
            'held Start does not repeatedly set $F8 trigger; states $02, $03, $04 follow',
            'at NMI 261 room state $19 wraps/returns from 04 to 00, next NMI becomes 01',
            'all three declared injection schedules produce the same state-change boundaries',
        ],
        'limits':[
            'This is original ROM instruction execution under stubs, NOT reference emulator or actual gameplay liveness',
            'Mapper IRQ scheduling, frame timing, PPU rendering and open-bus controller bits are not simulated',
            'No tested path reached room selector $18=$0C or $0D; their global live producer domains remain OPEN',
            'No new strict PRG-byte coverage or VPP milestone is justified by these partial conditions',
        ],
        'new_strict_prg_bytes':0,
        'strict_cumulative_prg_bytes':49404,
        'VPP':24,
        'last_completed_checkpoint':'0507'
    }

if __name__=='__main__':
    if len(sys.argv) not in (2,3):
        raise SystemExit('usage: test_controller_start_nmi_0508.py JP_ROM.nes [report.json]')
    result=run(sys.argv[1])
    if len(sys.argv)==3:Path(sys.argv[2]).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('JP controller input manual-NMI replay PASS:',result['total_manual_NMIs'],
          'injections;',result['total_original_instruction_steps'],'original instructions')
    for r in result['NMI_scenarios']:
        print(' idle',r['idle_instructions_between_manual_NMI'],
              'step total',r['original_instructions_including_RESET'],
              'NMI changes',[(v['NMI'],v['18'],v['19'],v['F8']) for v in r['changes']])
