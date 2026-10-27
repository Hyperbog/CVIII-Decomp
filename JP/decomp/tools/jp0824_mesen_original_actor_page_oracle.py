#!/usr/bin/env python3
"""JP0824 original-Mesen CPU oracle for a REAL source-linked type3D actor.

Input saved state MUST be a private natural controller-reached Mesen
state with slot1 original type3D, source3, sprite frame94. Never edits
ROM, and no patched state is committed; controlled virtual-page
CPU RAM variants are run in independent single original-game frames.

Unlike a generic smoke test, all three results are checked against
the original Mesen 6502 and can disprove the native projection gate.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
ROM="958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
AGENT="95bcda9d4ff6428937183093386d993649c2d740273871ced78217d3d8f234d0"
CORES={
  "d2831c26d42aba675ed5d2cf392b2e12a67cb25274d981ef2c7741e552b72040",
  "fa0e7af858dce0171f5857837f8cad92090078c354631ce74f8279185df97bd1"
}
def digest(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
def run(mesen:Path,rom:Path,home:Path,state:Path,x:int,flags:int|None):
    cmd=[str(mesen),str(rom),"--home",str(home),
         "--load-state",str(state),"--frames",str(1 if flags is not None else 0),
         "--timeout","20","--read-memory","NesInternalRam:0x400:800"]
    if flags is not None:
        cmd+=["--write-memory",f"NesInternalRam:0x471:{flags:02X}",
              "--write-memory",f"NesInternalRam:0x439:{x:02X}"]
    p=subprocess.run(cmd,capture_output=True,text=True,timeout=28)
    if p.returncode:raise RuntimeError(f"Mesen agent returned {p.returncode}: {p.stderr[:200]}")
    seen=None
    result=None
    for line in p.stdout.splitlines():
        obj=json.loads(line)
        if obj.get("event")=="memory_read" and obj.get("start")==0x400:
            raw=bytes.fromhex(obj["hex"])
            def at(addr:int)->int:return raw[addr-0x400]
            seen={"actor_type":at(0x54f),"source":at(0x646),
                  "frame":at(0x401),"flags":at(0x471),"x":at(0x439)}
        elif obj.get("event")=="summary":result=obj
    if seen is None or not result or result.get("reason")!="frame_limit":
        raise RuntimeError("Mesen original CPU did not complete expected frame")
    return seen
def verify(mesen:Path,rom:Path,home:Path,state:Path):
    if digest(rom)!=ROM:raise ValueError("Not owner-authenticated Japanese VRC6 ROM")
    if digest(mesen)!=AGENT or digest(mesen.parent/"MesenCore.so") not in CORES:
        raise ValueError("Mesen original agent/core identity changed")
    before=run(mesen,rom,home,state,0,None)
    if [before[k] for k in ("actor_type","source","frame")]!=[0x3d,3,0x94]:
        raise ValueError("Input state is NOT original controller-reached type3D actor")
    for x,alive in ((0x0c,True),(0xf0,True),(0x81,False)):
        got=run(mesen,rom,home,state,x,0xc5)
        if alive:
            if not (got["actor_type"]==0x3d and got["source"]==3 and
                    got["frame"]==0x94 and got["flags"]==0xc5 and
                    got["x"]==x):
                raise AssertionError(f"Original Mesen actor did not survive at X={x:02X}: {got}")
        else:
            if got["actor_type"]!=0 or got["frame"]!=0:
                raise AssertionError(f"Original Mesen did not remove mid-page actor: {got}")
        print(f"PASS JP0824 original CPU page1 X={x:02X}: {'allocated' if alive else 'deallocated'}")
    # The SAME genuine actor enters the ORIGINAL $B1F8 collision
    # dispatcher. This is CPU-oracle behavior, not a guessed native hit.
    with tempfile.TemporaryDirectory(prefix="jp0824_private_cpu_") as tmp:
        root=Path(tmp)
        for flags,steps,needle in (
            (0xc5,4,"B1F7  RTS"),
            (0x44,32,"B232  JSR $B339")
        ):
            state_out=root/f"hit_{flags:02x}.mss"
            argv=[str(mesen),str(rom),"--home",str(home),
                  "--load-state",str(state),"--frames","5",
                  "--timeout","20","--breakpoint",
                  "NesMemory:0xB1F8:x:[$23]==$0B && X==1",
                  "--write-memory",f"NesInternalRam:0x471:{flags:02X}",
                  "--write-memory","NesInternalRam:0x439:0C",
                  "--save-state",str(state_out)]
            call=subprocess.run(argv,capture_output=True,text=True,timeout=28)
            if call.returncode or '"reason":"debugger_break"' not in call.stdout:
                raise AssertionError("original B1F8 slot1 breakpoint not reached")
            trace=root/f"trace_{flags:02x}.txt"
            call=subprocess.run([str(mesen),str(rom),"--home",str(home),
                  "--load-state",str(state_out),"--frames","0",
                  "--step",str(steps),"--timeout","20",
                  "--trace",str(trace)],
                  capture_output=True,text=True,timeout=28)
            if call.returncode or needle not in trace.read_text():
                raise AssertionError(f"Original B1F8 branch differs for flag {flags:02X}")
            print(f"PASS JP0824 original B1F8 actor1 flags={flags:02X}: {needle}")
    print("LIMIT: controlled CPU RAM page variants, not new natural offscreen source spawns")
if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rom",type=Path,required=True)
    ap.add_argument("--mesen",type=Path,required=True)
    ap.add_argument("--state",type=Path,required=True,help="PRIVATE natural original Mesen frame3122 state")
    ap.add_argument("--home",type=Path,required=True)
    a=ap.parse_args()
    verify(a.mesen,a.rom,a.home,a.state)
