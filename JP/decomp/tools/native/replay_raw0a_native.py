#!/usr/bin/env python3
"""Real original 6502 $801E execution vs compiled host-C++ routine replay.

*Only* the locally bounded room-pointer lookup is compared, for 135 cases.
This does not certify bank-wide gameplay/PPU/VRC6 frame equivalence.
Original JP ROM supplied locally; never packaged or uploaded to GitHub CI.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'SharedDecomp'))
sys.path.insert(0,str(ROOT/'JP/decomp/tools'))
from workflow import EvidenceError, trace_diff, atomic_json, sha
from test_raw0a_lookup_cpu import run as original_6502

JP_SHA="958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
BANK_SHA="1460df577d44e114c64fdf34a8837629765f3f6a93d45796fdf81e5ffacb5ed8"

def rows(bank:bytes,cases:list[dict]):
    assert len(cases)==135, "expected complete 135-case producer-bounded test set"
    seen=set()
    for step,case in enumerate(cases):
        keys=tuple(case[k] for k in ("stage","second","third"))
        if keys in seen:raise EvidenceError("duplicate selector case")
        seen.add(keys)
        p1,p2,leaf,pcs=original_6502(bank,*keys)
        if pcs[0]!=0x801E or pcs[-1]!=0x8046:
            raise EvidenceError("original instruction interpreter entered wrong path")
        if leaf!=int(case["leaf_cpu"],16):
            raise EvidenceError("selector case expected leaf does not match original 6502")
        yield {"step":step,"physical_bank":"NES:JP:VRC6:raw0A", "pc":"801E-8046",
               "selectors":list(keys),"stage_ptr":f"{p1:04X}","second_ptr":f"{p2:04X}",
               "leaf_ptr":f"{leaf:04X}"}

def write_jsonl(p:Path,frames:list[dict]):
    p.write_text(''.join(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n' for x in frames),encoding='utf-8')

def compare(rom:Path,cases_file:Path,compiler:str,output:Path):
    game=rom.read_bytes()
    if len(game)!=393232 or sha(game)!=JP_SHA:raise EvidenceError("Japanese retail ROM mismatch")
    bank=game[16+10*0x4000:16+11*0x4000]
    if sha(bank)!=BANK_SHA:raise EvidenceError("physical raw0A SHA mismatch")
    cases=json.loads(cases_file.read_text())
    if not isinstance(cases,list):raise EvidenceError("expected list of selector cases")
    original=list(rows(bank,cases))
    output.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='raw0a-cpu-native-') as tmp:
        td=Path(tmp);bf=td/'raw0a.bin';bf.write_bytes(bank)
        pairs=td/'cases.tsv';pairs.write_text(''.join(f"{c['stage']} {c['second']} {c['third']}\n" for c in cases))
        binary=td/'host_lookup'
        source=Path(__file__).with_name('raw0a_lookup_native.cpp')
        subprocess.run([compiler,'-std=c++17','-O2','-Wall','-Wextra','-Werror','-pedantic',str(source),'-o',str(binary)],check=True)
        run=subprocess.run([str(binary),str(bf),str(pairs)],check=True,capture_output=True,text=True)
    expected=output/'original_6502.jsonl'
    actual=output/'host_cpp.jsonl'
    write_jsonl(expected,original)
    actual.write_text(run.stdout,encoding='utf-8')
    report=trace_diff(expected,actual)
    report.update({'scope':'bounded-original-6502-$801E-through-$8046-only',
                   'original_rom_sha256':JP_SHA,'physical_bank_sha256':BANK_SHA,
                   'actual_gameplay_frame_parity':False, 'native_engine_gameplay':False,
                   'mapper_and_hardware_events_verified':False})
    atomic_json(output/'raw0a_native_lookup_parity.json',report)
    if report['status']!='PASS':raise EvidenceError(f"first native mismatch: {report}")
    print(json.dumps(report,sort_keys=True))
    return report

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--rom',type=Path,required=True)
    ap.add_argument('--cases',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--cxx',default='g++')
    a=ap.parse_args()
    compare(a.rom,a.cases,a.cxx,a.out)

if __name__=='__main__':
    try:main()
    except (subprocess.CalledProcessError,ValueError,OSError) as e:
        print(f"NATIVE PARITY FAIL: {e}",file=sys.stderr)
        raise SystemExit(2)
