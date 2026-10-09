#!/usr/bin/env python3
"""Synthetic controller button-pattern stress exploration, not live reachability."""
import sys,hashlib,time,json
from pathlib import Path
from trace_6502_vrc6_0508 import Bus,CPU,ROM_SHA

rom=Path(sys.argv[1]).read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_SHA
FRAME_COUNT=300
patterns={
 'none': lambda f:0,
 'A held':lambda f:0x01,
 'B held':lambda f:0x02,
 'Select held':lambda f:0x04,
 'Start held':lambda f:0x08,
 'Up held':lambda f:0x10,
 'Down held':lambda f:0x20,
 'Left held':lambda f:0x40,
 'Right held':lambda f:0x80,
 'A+Start held':lambda f:0x09,
 'Select+Start held':lambda f:0x0C,
 'Start single at frame 1':lambda f:0x08 if f==1 else 0,
 'Start single at frame 20':lambda f:0x08 if f==20 else 0,
 'Start pulse every 30':lambda f:0x08 if f%30==1 else 0,
 'Start then A':lambda f:0x08 if 2<=f<=4 else 0x01 if 5<=f<=20 else 0,
 'A,B,Start cadence':lambda f:[0x01,0x02,0x08,0x00][(f-1)//10%4],
}
rows=[]
for name,fn in patterns.items():
    bus=Bus(rom,raw_bank=0,ppu_status=0x80);cpu=CPU(bus,0xE00B)
    cpu.run_until(0xE04B,15000);bus.ppu_status=0
    transitions=[];prev=None;seen18=set();seen19=set();failure=None
    for f in range(1,FRAME_COUNT+1):
        bus.controller1_bits=fn(f)
        try:
            cpu.interrupt(0xFFFA)
            cpu.run_until(0xE04B,cpu.steps+70000)
        except Exception as e:
            failure={'frame':f,'pc':f'{cpu.pc:04X}','raw_bank':f'{bus.raw_bank:02X}','error':str(e)}
            break
        s=(bus.ram[0x18],bus.ram[0x19],bus.ram[0x68])
        seen18.add(s[0]);seen19.add(s[1])
        if s!=prev:
            transitions.append({'frame':f,'18':s[0],'19':s[1],'68':s[2], 'F8':bus.ram[0xF8]})
            prev=s
    result={'name':name,'frames_completed':f if failure is None else f-1,'total_steps':cpu.steps,'seen_18':sorted(seen18),'seen_19':sorted(seen19),'state_changes':transitions[:40],'change_count':len(transitions),'failure':failure}
    print(name, result['frames_completed'],'18',result['seen_18'],'19',result['seen_19'],'changes',result['change_count'], 'error',str(failure)[:100])
    rows.append(result)
report={'status':'SYNTHETIC_BUTTON_PATTERN_SWEEP_NOT_ORIGINAL_GAMEPLAY','source_ROM_SHA256':ROM_SHA,'scenarios':rows,'total_original_instruction_steps':sum(r['total_steps'] for r in rows),'tested_manual_NMIs':sum(r['frames_completed'] for r in rows),'distinct_18_values':sorted(set().union(*map(lambda x:set(x['seen_18']),rows))),'notes':['No IRQ scheduling','Controller values forced per artificial injection','PPU $2002 forced 0 outside synthetic reset waits','No real video/audio/timing or live original controller transcript','Never promote strict PRG from this sweep']}
Path('/mnt/data/0508_controller_pattern_sweep_report.json').write_text(json.dumps(report,indent=2)+'\n')
print('TOTAL',report['total_original_instruction_steps'],'steps',report['tested_manual_NMIs'],'NMIs','selector18',report['distinct_18_values'])
