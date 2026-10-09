#!/usr/bin/env python3
"""ROM-free differential C++ vs Python VRC6 IRQ trace for Mapper 24.

Cross-implementation agreement is NOT an independent original-hardware timing
trace and earns no reference-emulator-parity credit.
"""
from __future__ import annotations
import argparse, hashlib, json, random, subprocess
from trace_vrc6_irq_frames_0508 import Vrc6Irq

SEED = 0xC508_2406
REGS = (0xF000, 0xF001, 0xF002, 0xFABC, 0xF9FD, 0xF7FE)

def produce():
    rng=random.Random(SEED)
    events=[]
    # Cover latch/control/ack across selected full control-bit domain.
    for latch in (0,1,0x7f,0x80,0xfc,0xfe,0xff):
        for control in range(8):
            events.extend([('W',0xF000,latch),('W',0xF001,control),
                           ('S',114,0),('S',227,0),('W',0xF002,0),
                           ('S',341,0),('W',0xF001,control^2)])
    # Deterministic randomized mixed mirror writes and time advancement.
    for i in range(4096):
        switch=rng.randrange(5)
        if switch in (0,1):
            reg=REGS[rng.randrange(len(REGS))]
            val=rng.randrange(256)
            events.append(('W',reg,val))
        elif switch==2:events.append(('S',rng.randrange(513),0))
        elif switch==3:events.append(('S',rng.randrange(1025),0))
        else:events.append(('S',rng.randrange(4),0))
    return events

def state(q):
    return (q.latch,q.counter,int(q.cycle_mode),int(q.enabled),
            int(q.enable_after_ack),int(q.pending))

def run(binary):
    ops=produce()
    q=Vrc6Irq()
    expected=[];cycles=0
    for kind,a,b in ops:
        if kind=='W':q.write(a,b)
        else:q.advance(a);cycles+=a
        expected.append(state(q))
    data=''.join(f'{t} {a} {b}\n' for t,a,b in ops)
    p=subprocess.run([binary],input=data,capture_output=True,text=True,check=True)
    actual=[tuple(int(n) for n in line.split()) for line in p.stdout.splitlines()]
    assert len(actual)==len(ops),('output count',len(actual),len(ops))
    for idx,(got,want) in enumerate(zip(actual,expected)):
        assert got==want,('IRQ trace mismatch at event',idx,ops[idx],got,want)
    assert cycles>500000 and len(ops)>4000
    digest=hashlib.sha256(p.stdout.encode()).hexdigest()
    return {'model':'VRC6 IRQ C++ vs Python differential (not NES reference parity)',
            'seed':SEED,'events':len(ops),'cpu_cycles_advanced':cycles,
            'matching_state_snapshots':len(ops),'trace_sha256':digest,
            'original_rom_required':False,'strict_new_prg_bytes':0,
            'reference_hardware_parity':False}

if __name__=='__main__':
    cli=argparse.ArgumentParser()
    cli.add_argument('native_driver')
    cli.add_argument('--report',default=None)
    a=cli.parse_args()
    result=run(a.native_driver)
    print('PASS',result['matching_state_snapshots'],'mapped IRQ state snapshots,',result['cpu_cycles_advanced'],'CPU cycles')
    if a.report:
        from pathlib import Path
        Path(a.report).write_text(json.dumps(result,indent=2)+'\n')
