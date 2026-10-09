#!/usr/bin/env python3
"""Check experimental IRQ model against JP repo Vrc6Irq source semantics.

No reference NES trace or 2A03/PuP/APU parity claimed.
"""
from __future__ import annotations
import json,hashlib,argparse
from pathlib import Path
from trace_vrc6_irq_frames_0508 import Vrc6Irq, IrqBus, IrqCPU
from trace_cycle_vblank_0508 import ROM_SHA
from trace_6502_vrc6_0508 import I


def run(path):
    rom=Path(path).read_bytes()
    assert len(rom)==393232 and hashlib.sha256(rom).hexdigest()==ROM_SHA
    tests=0
    q=Vrc6Irq();q.write(0xF000,0xFE);q.write(0xF001,0x06)
    assert q.enabled and q.cycle_mode and q.counter==0xFE;tests+=1
    q.advance(1);assert q.counter==0xFF and not q.pending;tests+=1
    q.advance(1);assert q.counter==0xFE and q.pending;tests+=1
    q.write(0xF002,0);assert not q.pending and not q.enabled;tests+=1
    q.advance(100);assert q.counter==0xFE;tests+=1

    q=Vrc6Irq();q.write(0xF000,0xFE);q.write(0xF001,0x07)
    q.advance(2);assert q.pending and q.counter==0xFE;tests+=1
    q.write(0xF002,0);assert not q.pending and q.enabled;tests+=1
    q.advance(1);assert q.counter==0xFF and not q.pending;tests+=1
    q.advance(1);assert q.counter==0xFE and q.pending;tests+=1

    q=Vrc6Irq();q.write(0xF000,0xFC);q.write(0xF001,0x02)
    for cycles,value in [(113,0xFC),(1,0xFD),(113,0xFD),(1,0xFE),(112,0xFE),(1,0xFF)]:
        q.advance(cycles);assert q.counter==value;tests+=1
    q.advance(114);assert q.pending and q.counter==0xFC;tests+=1
    q=Vrc6Irq();q.write(0xF000,0x80);q.write(0xF001,0x02)
    q.advance(114);assert q.counter==0x81;tests+=1
    q.write(0xF001,0x01);assert not q.pending and not q.enabled;tests+=1
    q.advance(1000);assert q.counter==0x81;tests+=1
    q.write(0xF002,0);assert q.enabled;tests+=1
    q.advance(113);assert q.counter==0x81;tests+=1
    q.advance(1);assert q.counter==0x82;tests+=1

    q=Vrc6Irq();q.write(0xFABC,0xAA);assert q.latch==0xAA;tests+=1
    q.write(0xF9FD,0x06);assert q.enabled and q.counter==0xAA;tests+=1
    q.write(0xF7FE,0);assert not q.pending and not q.enabled;tests+=1
    # Compare batched advancement to unbatched, including pending assertions.
    for latch in (0x00,0x80,0xFC,0xFE,0xFF):
        for ctrl in (0x00,0x01,0x02,0x03,0x06,0x07):
            for total in (0,1,2,113,114,227,341,500):
                a,b=Vrc6Irq(),Vrc6Irq()
                for v in (a,b):v.write(0xF000,latch);v.write(0xF001,ctrl)
                a.advance(total)
                for _ in range(total):b.advance(1)
                keys=('latch','counter','cycle_mode','enabled','enable_after_ack','pending','prescaler','counter_clocks','assertions')
                assert all(getattr(a,k)==getattr(b,k) for k in keys),(latch,ctrl,total)
                tests+=1
    # ROM vector path, preserving NMI-vs-IRQ priority and stack effects.
    b=IrqBus(rom);c=IrqCPU(b)
    assert b.rw(0xFFFE)==0xE0F5
    c.p &= ~I
    c.pc=0xE200
    b.irq.pending=True
    c.step()
    assert c.irq_entries==1 and c.NMI_count==0 and c.last_instruction[0]==0xE0F5
    tests+=1
    b2=IrqBus(rom);c2=IrqCPU(b2)
    c2.p &= ~I;c2.pc=0xE200
    b2.irq.pending=True;b2.nmi_pending=True
    c2.step()
    assert c2.NMI_count==1 and c2.irq_entries==0 and c2.last_instruction[0]==0xE057
    tests+=1
    return {'status':'IRQ_COMPONENT_REGRESSION_NOT_REFERENCE_EMULATOR_PARITY',
            'rom_sha256':ROM_SHA,'tests_passed':tests,
            'source_relation':'Mirrors already-committed JP/src/vrc6_irq.cpp, validates batch equivalence',
            'cpu_irq_vector':'E0F5','cpu_nmi_vector':'E057',
            'strict_new_prg_bytes':0,'vpp':24}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('rom');p.add_argument('out');a=p.parse_args()
    v=run(a.rom);Path(a.out).write_text(json.dumps(v,indent=2)+'\n')
    print('VRC6 IRQ component PASS',v['tests_passed'],'tests')
