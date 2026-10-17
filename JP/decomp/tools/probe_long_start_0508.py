#!/usr/bin/env python3
import sys,hashlib,json
from pathlib import Path
from trace_6502_vrc6_0508 import Bus,CPU,ROM_SHA
rom=Path(sys.argv[1]).read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_SHA
bus=Bus(rom,raw_bank=0,ppu_status=0x80)
cpu=CPU(bus,0xE00B);cpu.run_until(0xE04B,15000);bus.ppu_status=0
MAX=1200
changes=[];prev=None
for f in range(1,MAX+1):
    bus.controller1_bits=0x08 if f%30==1 else 0
    try:
        cpu.interrupt(0xFFFA)
        cpu.run_until(0xE04B,cpu.steps+70000)
    except Exception as ex:
        print('FAIL',f,cpu.pc,bus.raw_bank,ex)
        break
    state=(bus.ram[0x18],bus.ram[0x19],bus.ram[0x68],bus.ram[0x7A0],bus.ram[0x7A6])
    if state!=prev:
        changes.append({'frame':f,'18':state[0],'19':state[1],'68':state[2],'7A0':state[3],'7A6':state[4],'bank':bus.raw_bank})
        print('CHANGE',changes[-1])
        prev=state
    if state[0] in (0x0C,0x0D):
        print('TARGET REACHED',f,state)
        break
else:
    print('Reached max',MAX)
report={'environment':'synthetic fixed PPU status 00, no IRQ, Start pulses on frame index mod30=1','changes':changes,'total_instructions':cpu.steps,'frames_attempted':f,'final_pc':cpu.pc,'final_bank':bus.raw_bank}
Path('/mnt/data/0508_long_pulse_probe_report.json').write_text(json.dumps(report,indent=2)+'\n')
print('TOTAL',cpu.steps,'states',sorted(set(x['18'] for x in changes)))
