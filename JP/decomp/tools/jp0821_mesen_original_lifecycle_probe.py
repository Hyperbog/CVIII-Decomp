#!/usr/bin/env python3
"""JP0821: bounded natural Mesen2 actor creation/contact/deallocation probe.

Replays *the published JP0509 controller sequence* from cold reset. No
CPU/RAM/PC/bank edits. Uses the same external mesen-agent interface
and an owner's authenticated Japanese original cartridge.

Runs one proven creation baseline and three independent probes starting
from its bit-identical post-creation state: contact at mapped bank0B
$B727, and the first original writes to actor types $054F and $0550.
A first write is NOT necessarily a deallocation. A contact may involve
another actor. Reports partial evidence instead of making up a life cycle.
Never exports raw RAM, trace files, or savestates to a Git repository.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
from audit_mesen_actor_live_0509 import run, memory, file_sha

ROM_SHA="958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
CREATION_TRACE="dce02d6ce15c65a4b2dbdeea880b3171206514eeb7d35bb9168fcff56db48d93"

def inputs(ticks:int)->list[str]:
    result=["--input",f"0:right@0-{ticks-1}"]
    for frame in range(0,ticks,43):
        if frame+4<ticks:
            result += ["--input",f"0:a@{frame+4}-{min(frame+9,ticks-1)}"]
    for frame in range(0,ticks,107):
        if frame+34<ticks:
            result += ["--input",f"0:up@{frame+34}-{min(frame+65,ticks-1)}"]
    return result

def bounded_probe(mesen:Path,rom:Path,root:Path,state:Path,
                  label:str,bp:str,ticks:int)->dict:
    saved=root/f"{label}.mss"
    state_json=root/f"{label}.json"
    options=["--load-state",str(state),"--frames",str(ticks),
             "--timeout","65","--breakpoint",bp,"--pc",
             "--read-memory","NesInternalRam:0x540:160",
             "--read-memory","NesInternalRam:0x400:160",
             "--read-memory","NesInternalRam:0x640:96",
             "--read-memory","NesInternalRam:0x7C2:56",
             "--read-memory","NesInternalRam:0x40:128",
             "--state-json",str(state_json),
             "--save-state",str(saved)] + inputs(ticks)
    events,summary=run(mesen,rom,root,label,options)
    report={"status":"not_observed",
            "reason":summary.get("reason"),
            "frame":summary.get("final_frame")}
    if summary.get("reason")!="debugger_break":
        return report
    cpu=json.loads(state_json.read_text())
    slot=cpu.get("cpu.x")
    typelist=memory(events,0x540)
    original_types=[typelist[0x054e+i-0x540] for i in (1,2)]
    report={"status":"original_breakpoint_hit",
            "frame":summary.get("final_frame"),
            "cycles":cpu.get("cpu.cycleCount"),
            "pc":f"{cpu['cpu.pc']:04X}",
            "actor_slot":slot,
            "type1_type2":original_types}
    if isinstance(slot,int) and 1<=slot<=18:
        type_now=typelist[0x054e+slot-0x540]
        flags=memory(events,0x400)[0x0470+slot-0x400] if False else memory(events,0x400)[0x470+slot-0x400]
        parent=memory(events,0x640)[0x645+slot-0x640]
        report["actor_type"]=type_now
        report["original_row32_child_witness"]=(
              type_now==0x3d and bool(flags&4) and parent<6)
    # If debugging a memory WRITE, the breakpoint can stop before
    # executing its store. Step exactly one original instruction using
    # its unmodified private savestate and inspect the poststate.
    if label.startswith("write_"):
        post_events,_=run(mesen,rom,root,label+"_one_instruction",
          ["--load-state",str(saved),"--frames","0","--step","1",
           "--timeout","30",
           "--read-memory","NesInternalRam:0x540:160"])
        post=memory(post_events,0x540)
        tested=1 if label=="write_054f" else 2
        before=original_types[tested-1]
        after=post[0x054e+tested-0x540]
        report.update({"original_slot":tested,
                       "type_before":before,"type_after_one_instruction":after,
                       "deallocation_proved":before!=0 and after==0})
    return report

def replay(mesen:Path,rom:Path,ticks:int)->dict:
    if file_sha(rom)!=ROM_SHA:
        raise ValueError("not the authenticated original Japanese Mapper24 ROM")
    if not mesen.is_file():
        raise FileNotFoundError(f"external mesen-agent unavailable: {mesen}")
    with tempfile.TemporaryDirectory(prefix="jp0821_original_mesen_private_") as tmp:
        root=Path(tmp)
        phase0=["--frames","1502","--timeout","65"]
        for frame in (50,170,270,370):
            phase0+=["--input",f"0:start@{frame}-{frame+4}"]
        phase0+=["--input","0:right@780-1501",
                 "--input","0:a@820-1501",
                 "--save-state",str(root/"boot.mss")]
        _,s0=run(mesen,rom,root,"boot",phase0)
        if (s0.get("reason"),s0.get("final_frame"))!=("frame_limit",1503):
            raise AssertionError("original JP0509 controller-reached boot drift")
        _,s1=run(mesen,rom,root,"stage1",
             ["--load-state",str(root/"boot.mss"),"--frames","1100",
              "--timeout","65","--input","0:right@0-1099",
              "--input","0:a@0-1099",
              "--save-state",str(root/"stage1.mss")])
        if (s1.get("reason"),s1.get("final_frame"))!=("frame_limit",2603):
            raise AssertionError("original JP0509 frame2603 drift")
        options=["--load-state",str(root/"stage1.mss"),
            "--frames","1200","--timeout","65",
            "--breakpoint","NesMemory:0x84F3:x:[$23]==$0A",
            "--pc","--read-memory","NesInternalRam:0x7C2:56",
            "--save-state",str(root/"hit.mss")]+inputs(1200)
        hit,hits=run(mesen,rom,root,"original_source",options)
        if (hits.get("reason"),hits.get("final_frame"))!=("debugger_break",3092):
            raise AssertionError("natural frame3092 source entry missing")
        selected=memory(hit,0x7c2)
        if selected[3]!=0x32:
            raise AssertionError("frame3092 original source row is not $32")
        tr=root/"created.trace"
        post,summary=run(mesen,rom,root,"created",
             ["--load-state",str(root/"hit.mss"),
              "--frames","0","--step","600","--timeout","30",
              "--trace",str(tr),
              "--read-memory","NesInternalRam:0x540:160",
              "--save-state",str(root/"created.mss")])
        trace_sha=hashlib.sha256(tr.read_bytes()).hexdigest()
        types=memory(post,0x540)
        if (trace_sha!=CREATION_TRACE or
            [types[0x54e+i-0x540] for i in (1,2)]!=[0x3d,0x3d]):
            raise AssertionError("real 600-instruction creation witness drift")
        baseline={"proof":"genuine natural Mesen original type3D creation",
                  "creation_frame":3092,
                  "source_index":3,
                  "created_actor_slots":[1,2],
                  "original_trace_sha256":trace_sha}
        probes={}
        # These independent probes replay the same postcreation state,
        # do NOT assume either event will be reached in the window.
        for label,bp in (
             ("contact_b727","NesMemory:0xB727:x:[$23]==$0B"),
             ("write_054f","NesMemory:0x054F:w"),
             ("write_0550","NesMemory:0x0550:w")):
            probes[label]=bounded_probe(
                mesen,rom,root,root/"created.mss",label,bp,ticks)
        natural_contact=probes["contact_b727"]
        valid_contact=natural_contact.get("status")=="original_breakpoint_hit" and              natural_contact.get("original_row32_child_witness",False)
        deallocated=any(probes[k].get("deallocation_proved",False)
                        for k in ("write_054f","write_0550"))
        return {"schema":"JP0821-controller-only-original-lifetime-v1",
                "rom_sha256":ROM_SHA,
                "mesen_sha256":file_sha(mesen),
                "baseline":baseline,"probes":probes,
                "complete_lifecycle_proved":bool(valid_contact and deallocated),
                "limits":"first writes may not deallocate; no false offscreen parity claim"}

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom",type=Path,required=True)
    parser.add_argument("--mesen",type=Path,required=True,
                        help="external original Mesen2.1.1 mesen-agent executable")
    parser.add_argument("--frames",type=int,default=1200,
                        help="bounded postcreation original-game capture window")
    parser.add_argument("--report",type=Path,
                        help="optional PRIVATE compact result; no RAM or trace")
    a=parser.parse_args()
    if not 1<=a.frames<=2400:
        parser.error("--frames must be 1..2400")
    result=replay(a.mesen,a.rom,a.frames)
    serial=json.dumps(result,indent=2,sort_keys=True)
    if a.report:
        a.report.write_text(serial+"\n")
    print(serial)
