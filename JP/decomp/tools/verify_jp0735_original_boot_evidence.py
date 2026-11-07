#!/usr/bin/env python3
"""JP0735 authenticated owner-local comparison: original ROM/MesenCE/native.

Reads existing private captures; prints only structural counts and mismatches.
Never exports/re-uploads the ROM, screenshots, RAM or copyrighted artwork.
This check does NOT replace a fresh JP0735 retail-game cycle trace; archived
JP0719 native was built BEFORE JP0735 and differs in ending from original.
"""
from __future__ import annotations
import argparse, hashlib, io, json, zipfile
from pathlib import Path

JP_SHA="958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
EXPECTED=((0xE00B,0xD8),(0xE00C,0x78),(0xE017,0xA2),(0xE019,0x9A))
FILE_PRG_START=16 + 31*8192
CART_BYTES=393232

def source_identity(data:bytes)->dict:
    if len(data)!=CART_BYTES or hashlib.sha256(data).hexdigest()!=JP_SHA:
        raise ValueError("expected exact legally owned original JP mapper24 media")
    if data[:8]!=b"NES\x1a\x10\x10\x80\x10":
        raise ValueError("unexpected source header")
    reset=int.from_bytes(data[16+262144-4:16+262144-2],"little")
    if reset!=0xE00B:raise ValueError("original reset vector drift")
    for address,opcode in EXPECTED:
        at=FILE_PRG_START+address-0xE000
        if data[at]!=opcode:raise ValueError(f"boot instruction drift at ${address:04X}")
    if data[FILE_PRG_START+0x18]!=0xFF:raise ValueError("original LDX operand drift")
    return {"reset_pc":"E00B","physical_4k_bank":62,
            "native_original_entries":len(EXPECTED),
            "native_bytes":["E00B/D8","E00C/78","E017/A2FF","E019/9A"]}

def mesen_evidence(path:Path)->dict:
    with zipfile.ZipFile(path) as z:
        entry=next((n for n in z.namelist() if n.endswith("-events.tsv")),None)
        if not entry:raise ValueError("original MesenCE events missing")
        rows=z.read(entry).decode("utf8").splitlines()
    resets=[r.split("\t") for r in rows if "RAM_CHANGE" in r]
    boot=[r for r in resets if len(r)>9 and r[5]=="0035" and
          r[6]=="03" and r[7]=="00" and r[8]=="E02C" and r[9]=="3E02C"]
    snapshots=[r.split("\t") for r in rows if "\tSNAPSHOT\t" in r]
    if len(boot)!=1 or not snapshots:raise ValueError("Mesen boot/scene evidence changed")
    last=snapshots[-1]
    if len(last)<8 or last[6]!="000300":
        raise ValueError("original Mesen final route selector changed")
    return {"first_native_boot_continuation_pc":"E02C",
            "first_boot_event_frame":int(boot[0][2]),
            "original_snapshots":len(snapshots),
            "last_selector":last[6],"last_snapshot_frame":int(last[2])}

def old_native_baseline(path:Path)->dict:
    with zipfile.ZipFile(path) as z:
        manifest=next(n for n in z.namelist() if n.endswith("-manifest.tsv"))
        rows=z.read(manifest).decode().splitlines()
        input_path=next(n for n in z.namelist() if n.endswith("-original-controller-input.input"))
        original_input_hash=hashlib.sha256(z.read(input_path)).hexdigest()
        samples=[r.split("\t") for r in rows[1:] if r]
    if original_input_hash!="27b502aaeca9f5d5381f9f9a812cc188043d083d8ac8b3a89bc40c70f3c30196":
        raise ValueError("controller replay identity changed")
    if not samples or samples[-1][3]!="000100":
        raise ValueError("old native end-stage selector changed")
    return {"old_native_snapshots":len(samples),
            "old_native_final_selector":samples[-1][3],
            "old_native_capture_predates_boot_native":True}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rom",type=Path,required=True)
    p.add_argument("--mesen-zip",type=Path,required=True)
    p.add_argument("--old-native-zip",type=Path,required=True)
    args=p.parse_args()
    result={"original_source":source_identity(args.rom.read_bytes()),
            "original_mesen":mesen_evidence(args.mesen_zip),
            "earlier_native_reference":old_native_baseline(args.old_native_zip)}
    result["retail_jp0735_native_parity_certified"]=False
    result["note"]="Original and JP0719 native reach different final selectors; current native boot patch has not yet been run on the private retail image."
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
