#!/usr/bin/env python3
"""JP0613: conservative original sound-entry/hardware-write timing proximity.

Paired owner-local JP0612 E249 requests and JP0610 2A03/VRC6 register writes.
This tool NEVER attributes a hardware voice or rejected event to a command.
Rejects backwards cycle epochs (save-state loads) rather than guessing joins.
"""
from __future__ import annotations
import argparse
from collections import Counter
import csv
import io
import json
import re
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'recomp'/'tools'))
import jp_audio_bus_report_0610 as chip

REQUEST_FIELDS=("cycle","pc","command","x","y","s","p",
                "tracked_prg_bank","stack_next_lo","stack_next_hi")
HEX_BYTE=re.compile(r"[0-9A-Fa-f]{2}\Z")
MAX_ROWS=1_000_000

def requests(text: str) -> list[tuple[int,int]]:
    reader=csv.DictReader(io.StringIO(text))
    if tuple(reader.fieldnames or ())!=REQUEST_FIELDS:
        raise ValueError("Unexpected JP0612 sound request CSV schema")
    out=[]
    previous=-1
    for row in reader:
        if (set(row)!=set(REQUEST_FIELDS) or
                any(v is None or v!=v.strip() for v in row.values())):
            raise ValueError("Malformed JP0612 sound request row")
        if len(out)>=MAX_ROWS:
            raise ValueError("Sound request row cap exceeded")
        raw=row["cycle"]
        if not re.fullmatch(r"[0-9]+",raw):
            raise ValueError("Bad JP0612 decimal CPU cycle")
        cycle=int(raw)
        if cycle>2**64-1 or cycle<previous:
            raise ValueError("Nonmonotonic requests: split save-state epochs first")
        if row["pc"].upper()!="E249":
            raise ValueError("Request not from authenticated fixed E249")
        for key in REQUEST_FIELDS[2:]:
            if not HEX_BYTE.fullmatch(row[key]):
                raise ValueError("Bad JP0612 byte field: "+key)
        a=int(row["command"],16)
        out.append((cycle,a))
        previous=cycle
    if not out:
        raise ValueError("No original E249 request entries captured")
    return out

def writes(text: str) -> list[tuple[int,str]]:
    # Reuse the existing JP0610 strict checks: channel, delta, previous,
    # register identity, rapid flag, monotonicity and bounded count.
    chip.analyze(text)
    reader=csv.DictReader(io.StringIO(text))
    return [(int(r["cycle"]),r["chip"]+"/"+r["voice"]) for r in reader]

def correlate(request_csv: str, register_csv: str, window: int=6000) -> dict:
    if not 0<=window<=100000:
        raise ValueError("Proximity window must be 0..100000 CPU cycles")
    req=requests(request_csv)
    reg=writes(register_csv)
    # Both loggers count CPU cycles of the same machine, but their CSVs
    # contain no session UUID or save/load epoch marker. Ordering of each
    # stream alone cannot prove that two files share an uninterrupted run.
    # This is conditional proximity only, never music/SFX or causality.
    overlaps=Counter()
    observed=0
    lone=0
    ambiguous=0
    j=0
    for i,(cycle,command) in enumerate(req):
        while j<len(reg) and reg[j][0]<cycle:
            j+=1
        end=cycle+window
        if i+1<len(req):
            end=min(end,req[i+1][0])
        k=j
        voices=set()
        while k<len(reg) and reg[k][0]<=end:
            # When the next request is at end, even a same-cycle write
            # cannot be ordered uniquely across distinct CSV streams.
            if i+1<len(req) and reg[k][0]>=req[i+1][0]:
                break
            voices.add(reg[k][1])
            k+=1
        if voices:
            observed+=1
            for voice in voices:
                overlaps[voice]+=1
        else:
            lone+=1
        # More than one voice observed does not imply independent events.
        if len(voices)>1:
            ambiguous+=1
    return {
        "schema":"CVIII-JP-request-register-proximity/v1",
        "request_count":len(req),
        "register_write_count":len(reg),
        "requested_window_cycles":window,
        "requests_with_subsequent_register_writes":observed,
        "requests_without_writes_inside_window":lone,
        "multi_voice_windows":ambiguous,
        "voice_window_occurrences":dict(sorted(overlaps.items())),
        "cross_file_session_identity_verified":False,
        "save_state_epoch_consistency_verified":False,
        "causality_or_ownership_proven":False,
        "sound_events_rejected_by_original_driver_proven":False,
        "interpretation":"Time proximity only; independent original execution needed.",
    }

def fixture_request() -> str:
    o=io.StringIO()
    writer=csv.writer(o,lineterminator="\n")
    writer.writerow(REQUEST_FIELDS)
    writer.writerows([
        ("100","E249","6B","00","00","FD","24","0A","00","00"),
        ("250","E249","10","01","00","FC","24","0C","00","00"),
        ("500","E249","70","00","01","FD","20","0C","00","00"),
    ])
    return o.getvalue()

def fixture_write() -> str:
    o=io.StringIO()
    w=csv.writer(o,lineterminator="\n")
    w.writerow(chip.FIELDS)
    w.writerows([
        ("150","2a03","pulse1","4000","30","00","0","0"),
        ("260","vrc6","saw","B002","44","00","0","0"),
        ("270","2a03","pulse1","4000","31","30","120","1"),
    ])
    return o.getvalue()

def smoke() -> None:
    q=fixture_request(); w=fixture_write()
    r=correlate(q,w,100)
    assert r["request_count"]==3 and r["register_write_count"]==3
    assert r["requests_with_subsequent_register_writes"]==2
    assert r["requests_without_writes_inside_window"]==1
    assert r["multi_voice_windows"]==1
    assert r["voice_window_occurrences"]=={"2a03/pulse1":2,"vrc6/saw":1}
    bad=[
        (q.replace("E249","E248",1),w),
        (q.replace("6B","GG",1),w),
        (q.replace("250,E249","50,E249"),w),
        (q.replace("cycle,pc","time,pc"),w),
        (q,w.replace("150,2a03,pulse1","150,2a03,noise")),
        (q,w.replace("260,vrc6","60,vrc6")),
    ]
    for a,b in bad:
        try: correlate(a,b,100)
        except ValueError: continue
        raise AssertionError("JP0613 accepted corrupted synthetic capture")
    for invalid in (-1,100001):
        try: correlate(q,w,invalid)
        except ValueError: continue
        raise AssertionError("JP0613 accepted invalid temporal window")
    print("PASS JP0613 strict paired schemas, 2 proximity windows, 8 negative tests")

def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--smoke",action="store_true")
    p.add_argument("--requests",type=Path)
    p.add_argument("--registers",type=Path)
    p.add_argument("--json",type=Path)
    p.add_argument("--window-cycles",type=int,default=6000)
    a=p.parse_args()
    if a.smoke:
        smoke()
        return
    if not a.requests or not a.registers:
        p.error("Both --requests and --registers are required")
    report=correlate(a.requests.read_text(encoding="utf-8"),
                     a.registers.read_text(encoding="utf-8"),
                     a.window_cycles)
    if a.json:
        a.json.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",
                          encoding="utf-8")
    print(json.dumps(report,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
