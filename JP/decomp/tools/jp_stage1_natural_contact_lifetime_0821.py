#!/usr/bin/env python3
"""JP0821 private original-Mesen controller-only contact/lifetime follow-up.

Reuses the *independently proven* JP0509 Mesen2 controller-only
1503 -> 2603 -> 3092 original-ROM sequence and post-hit 600 original
6502 CPU instructions. Follows the original (unmodified) game for a
bounded additional frame horizon; does not set CPU PC/RAM, patch ROM,
modify savestates, or upload private bytes. Merely running this tool
does NOT guarantee that B727 or either eventual actor death occurs.

REQUIRES: owner-original ROM and the existing mesen-agent 2.1.1 binary
(and MesenCore.so) as documented in JP0509. Not run in public CI.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from audit_mesen_actor_live_0509 import run, memory, ROM_SHA

AGENT_SHA="95bcda9d4ff6428937183093386d993649c2d740273871ced78217d3d8f234d0"
CORE_SHA="d2831c26d42aba675ed5d2cf392b2e12a67cb25274d981ef2c7741e552b72040"

def hashfile(p:Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def schedule(start:int,length:int)->list[str]:
    """Original JP0509 phase2 input epoch: 489 frames already reached."""
    result=[f"0:right@0-{length-1}"]
    for key,period,startp,endp in (("a",43,4,9),("up",107,34,65)):
        on=False;from_i=0
        for i in range(length+1):
            tick=start+i
            pressed=(i<length and startp<=tick%period<=endp)
            if pressed and not on:
                from_i=i;on=True
            elif on and not pressed:
                result.append(f"0:{key}@{from_i}-{i-1}");on=False
    return result

def snapshot(events:list, frame:int)->dict:
    t=memory(events,0x540)
    flags=memory(events,0x400)
    tail=memory(events,0x630)
    src=memory(events,0x7c2)
    selector=memory(events,0x30)
    assert len(t)>=0x40 and len(flags)>=0x80 and len(tail)>=0x5e
    children=[]
    for x in (1,2):
        original_type=t[0x54e-0x540+x]
        a=flags[0x470-0x400+x]
        parent=tail[0x645-0x630+x]
        children.append({
           "slot":x,"original_type":original_type,
           "linked":original_type==0x3d and (a&4)!=0 and parent<6,
           "parent_source":parent if original_type==0x3d and (a&4)!=0 and parent<6 else None,
           "source_row":src[parent] if parent<6 else None,
           "allocated":original_type!=0,
           "visual_candidate":original_type!=0 and flags[x]!=0 and not(a&0x80),
        })
    return {"frame":frame,
            "selector":[selector[4],selector[5],selector[6]],
            "children":children}

def validate_snapshots(prev:dict,cur:dict)->list[dict]:
    out=[]
    for old,new in zip(prev["children"],cur["children"]):
        if old["original_type"]!=new["original_type"]:
            label=("observed_slot_deallocated" if old["allocated"] and not new["allocated"]
                else "observed_slot_type_changed")
            out.append({"event":label,"slot":new["slot"],
                        "frame_after":prev["frame"],"frame_at_or_before":cur["frame"],
                        "old_type":old["original_type"],"new_type":new["original_type"],
                        "note":"sample interval, not exact original writer PC"})
        elif old["linked"] and new["linked"] and old["parent_source"]!=new["parent_source"]:
            out.append({"event":"parent_index_changed",
                        "slot":new["slot"],"frame_at_or_before":cur["frame"],
                        "note":"source slot reuse prevents historical identity inference"})
    return out

def witness(mesen:Path,rom:Path,horizon:int,sample:int)->dict:
    if hashfile(rom)!=ROM_SHA:raise ValueError("JP original ROM SHA mismatch")
    if hashfile(mesen)!=AGENT_SHA or hashfile(mesen.parent/"MesenCore.so")!=CORE_SHA:
        raise ValueError("JP0509 independent Mesen agent/core identity mismatch")
    with tempfile.TemporaryDirectory(prefix="jp0821_original_owner_") as name:
        root=Path(name)
        p0=["--frames","1502","--timeout","65"]
        for frame in (50,170,270,370):
            p0+=["--input",f"0:start@{frame}-{frame+4}"]
        p0+=["--input","0:right@780-1501","--input","0:a@820-1501",
             "--save-state",str(root/"phase0.mss")]
        _,summary=run(mesen,rom,root,"boot",p0)
        if summary["final_frame"]!=1503:raise AssertionError("original boot frame differs")
        p1=["--load-state",str(root/"phase0.mss"),"--frames","1100","--timeout","65",
            "--input","0:right@0-1099","--input","0:a@0-1099",
            "--save-state",str(root/"phase1.mss")]
        _,summary=run(mesen,rom,root,"follow",p1)
        if summary["final_frame"]!=2603:raise AssertionError("original Stage1 frame differs")
        p2=["--load-state",str(root/"phase1.mss"),"--frames","1200","--timeout","65",
            "--breakpoint","NesMemory:0x84F3:x:[$23]==$0A",
            "--input","0:right@0-1199","--save-state",str(root/"hit.mss")]
        for f in range(0,1200,43):
            if f+4<1200:p2+=["--input",f"0:a@{f+4}-{min(f+9,1199)}"]
        for f in range(0,1200,107):
            if f+34<1200:p2+=["--input",f"0:up@{f+34}-{min(f+65,1199)}"]
        _,summary=run(mesen,rom,root,"row32",p2)
        if summary.get("reason")!="debugger_break" or summary["final_frame"]!=3092:
            raise AssertionError("original row32 controller reached breakpoint differed")
        args=["--load-state",str(root/"hit.mss"),"--frames","0","--step","600",
              "--timeout","30","--save-state",str(root/"spawn.mss")]
        for a in ("0x540:160","0x400:256","0x630:224","0x7C2:56","0x30:32"):
            args+=["--read-memory","NesInternalRam:"+a]
        events,_=run(mesen,rom,root,"spawn600",args)
        start=snapshot(events,3092)
        if any(x["original_type"]!=0x3d for x in start["children"]):
            raise AssertionError("natural type3D created original slots 1/2 differ")
        observations=[start];transitions=[]
        prev=start;elapsed=0;active_state=root/"spawn.mss"
        first_room=start["selector"]
        while elapsed<horizon:
            n=min(sample,horizon-elapsed)
            next_state=root/("follow"+str(elapsed+n)+".mss")
            args=["--load-state",str(active_state),"--frames",str(n),
                  "--timeout","65","--save-state",str(next_state)]
            for i in schedule(489+elapsed,n):args+=["--input",i]
            for a in ("0x540:160","0x400:256","0x630:224","0x7C2:56","0x30:32"):
                args+=["--read-memory","NesInternalRam:"+a]
            ev,sm=run(mesen,rom,root,"step"+str(elapsed+n),args)
            cur=snapshot(ev,sm["final_frame"])
            transitions+=validate_snapshots(prev,cur)
            observations.append(cur)
            elapsed+=n;active_state=next_state;prev=cur
            if cur["selector"]!=first_room:
                transitions.append({"event":"room_discontinuity","frame":cur["frame"],
                    "note":"stop; actor slot reuse across rooms is ambiguous"})
                break
            if all(not c["allocated"] for c in cur["children"]):break
        # Independently replay the SAME controller sequence from the
        # source-confirmed original post-creation state and ask Mesen for
        # the original raw-bank-$0B B727 execution breakpoint. It is
        # NOT enough for B727 to fire for an unrelated actor type.
        args=["--load-state",str(root/"spawn.mss"),"--frames",str(horizon),
              "--timeout","65","--breakpoint","NesMemory:0xB727:x:[$23]==$0B",
              "--state-json",str(root/"contact.json"),
              "--save-state",str(root/"contact.mss")]
        for i in schedule(489,horizon):args+=["--input",i]
        for a in ("0x540:160","0x630:224","0x400:256"):
            args+=["--read-memory","NesInternalRam:"+a]
        ev,s=run(mesen,rom,root,"contactB727",args)
        reached=s.get("reason")=="debugger_break"
        contact={"reached":reached,
                 "frame":s.get("final_frame") if reached else None,
                 "bank_qualified_breakpoint":"NesMemory:0xB727:x:[$23]==$0B",
                 "source_linked_type3d":False,
                 "note":"only original PC reachability until source ancestry and poststate are proved"}
        if reached:
            cpu=json.loads((root/"contact.json").read_text())
            actor=cpu["cpu.x"]
            owner=memory(ev,0x540)
            tail=memory(ev,0x630)
            flags=memory(ev,0x400)
            if 1<=actor<=12:
                t=owner[0x054eu-0x540u+actor]
                mark=flags[0x0470u-0x400u+actor]
                src=tail[0x0645u-0x630u+actor]
                linked=t==0x3d and (mark&4)!=0 and src<6
                contact.update({"actor_slot":actor,"actor_type":t,
                    "source_index":src if linked else None,
                    "source_linked_type3d":linked,
                    "cpu_cycle":cpu.get("cpu.cycleCount")})
            contact["note"]=("bank-qualified B727 entry only; "
                "actor-source correlation requires source-linked type3D, "
                "and exact downstream poststate requires separate CPU step trace")
        return {"original_rom_sha256":ROM_SHA,"agent_sha256":AGENT_SHA,
                "creation":{"frame":3092,"original_type":"3D","slots":[1,2],
                            "original_source_handler":"raw0A:8B2C"},
                "sample_interval_frames":sample,"sampled_snapshots":observations,
                "sampled_transitions":transitions,"b727":contact,
                "lifetime_proof":"bounded snapshots only; no exact PC of original deallocation",
                "real_contact_effect_proof":"B727 breakpoint only, later RAM writer parity not established"}

def smoke()->None:
    assert schedule(489,30)[0]=="0:right@0-29"
    a={"frame":11,"children":[{"slot":1,"original_type":0x3d,"allocated":True,"linked":True,
        "parent_source":3},{"slot":2,"original_type":0x3d,"allocated":True,"linked":True,
        "parent_source":3}]}
    b={"frame":22,"children":[{"slot":1,"original_type":0,"allocated":False,"linked":False,
        "parent_source":None},{"slot":2,"original_type":0x3d,"allocated":True,"linked":True,
        "parent_source":4}]}
    r=validate_snapshots(a,b)
    assert len(r)==2 and r[0]["event"]=="observed_slot_deallocated" and r[1]["event"]=="parent_index_changed"
    print("PASS JP0821 private Mesen controller schedule and bounded lifetime labeling")

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mesen",type=Path)
    parser.add_argument("--rom",type=Path)
    parser.add_argument("--follow-frames",type=int,default=360)
    parser.add_argument("--sample-frames",type=int,default=30)
    parser.add_argument("--smoke",action="store_true")
    a=parser.parse_args()
    if a.smoke:smoke()
    if a.rom or a.mesen:
        if not a.rom or not a.mesen:parser.error("both --mesen and --rom are required")
        if not(1<=a.follow_frames<=1200 and 1<=a.sample_frames<=120):
            parser.error("bounded horizon 1..1200 and sample 1..120 required")
        print(json.dumps(witness(a.mesen,a.rom,a.follow_frames,a.sample_frames),
                         indent=2,sort_keys=True))
    if not(a.smoke or a.rom or a.mesen):parser.error("provide --smoke or --mesen and --rom")
