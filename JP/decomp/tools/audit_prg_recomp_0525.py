#!/usr/bin/env python3
"""Auditable 0500-0508 PRG interval union and 0510-0517 source reconciliation.

The pre-0500 43,475-byte baseline has NO complete public physical mask.
Do not mistake bytes outside the incremental mask for new strict coverage.
--emit-literal-fragments creates verified .byte source slices: recompilation
scaffolding only, NOT a semantic 6502 disassembly.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ROM_SHA="958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
PRG_SIZE=262144
# Six originally certified 0500 spans recovered from historic Git SHA
# 75545a83604f512695f88c4479d38271baec678e (deleted audit script).
EARLY=[
 ("F706","F713","8745c6e3d3acdd90bf3b1cafaf32f9e981a606070ba5d2b365cace8f56fa3025"),
 ("F724","F739","41cad7c7b722c299f4111083f871fd996a0cfa517bd990d3b37ddce6ac30072e"),
 ("F782","F792","17bbb4663de8e617686c27ab5ad5554a69c0062d9c8bff1d353fd6487028546b"),
 ("F7B7","F7CF","0d93fcf865fdae96f01a0640e3769924b558f1cb0aaa0dbe7d2fedfdf17462be"),
 ("F800","FAA0","6dea651f93c64d59355c4180907677d367bb705ed84cbfa6ec59da79009028a8"),
 ("FAAA","FB96","5d32479e3af38c5477b4a3c076b3c3d0a0bd07f4c572a35a115bd6e347720402"),
]
def H(b):return hashlib.sha256(b).hexdigest()
def J(name):return json.loads((ROOT/name).read_text(encoding="utf-8"))
def block(checkpoint,offset,length,digest,kind="mixed"):
    if not (0<=offset<PRG_SIZE and 0<length<=PRG_SIZE-offset):
        raise ValueError("Physical PRG range out of bounds")
    if not re.fullmatch("[0-9a-f]{64}",digest):
        raise ValueError("Missing ROM SHA256")
    return dict(checkpoint=checkpoint,offset=offset,length=length,sha256=digest,kind=kind)
def source_offset(tag,address):
    if tag=="fixed31":
        if not 0xE000<=address<=0xFFFF:raise ValueError("fixed31 address")
        return 31*8192+address-0xE000
    if tag=="raw0b":
        if not 0x8000<=address<0xC000:raise ValueError("raw0b address")
        return 11*16384+address-0x8000
    raise ValueError("unrecognized mapped source bank")

def certified():
    rows=[]
    for a,b,d in EARLY:
        lo,hi=int(a,16),int(b,16)
        rows.append(block("0500",source_offset("fixed31",lo),hi-lo,d,"code/data"))
    first=J("SharedNES/JP_0501_CERTIFIED_REGIONS.json")
    if first["source_rom_sha256"]!=ROM_SHA or first["total_certified_source_bytes"]!=4364:
        raise ValueError("0501 original certificate changed")
    for r in first["regions"]:
        rows.append(block("0501",r["source_prg_offset"],r["size"],r["sha256"]))
    rows.append(block("0502",source_offset("raw0b",0xB394),2,
        "9f1afa4dc124cba73134e82ff50f17c8f7164257c79fed9a13f5943a6acb8e3d","data"))
    source=(ROOT/"tools/audit_ai_script_seed_0504.py").read_text(encoding="utf-8")
    match=re.search(r'RANGES="""([\s\S]*?)"""',source)
    if match is None:raise ValueError("0504 interval certificate not found")
    for line in match.group(1).strip().splitlines():
        tag,kind,begin,end,digest=line.split()
        lo,hi=int(begin,16),int(end,16)
        rows.append(block("0504",source_offset(tag,lo),hi-lo,digest,kind))
    rows.append(block("0507",10*16384+0xB4CC-0x8000,5,
        "0cbfd39d34523da29edaa6a2dcf5cdb4b62de628d0e5568ea3879d7de5a1c0c7","code"))
    state=J("analysis/RESUME_STATE.json")
    if state["rom_sha256"]!=ROM_SHA or state["progress_metrics"]["strict_verified_prg_floor_bytes"]!=49504:
        raise ValueError("RESUME_STATE strict PRG floor drift")
    last=state["prior_dependency_manifest"]
    if last["checkpoint"]!="0508" or last["exact_new_bytes_in_checkpoint"]!=100:
        raise ValueError("0508 certificate drift")
    for r in last["exact_new_ranges"]:
        rows.append(block("0508",int(r["prg_offset_start"],16),
                          r["length"],r["sha256"],"code"))
    return rows

def source_windows():
    manifest=J("analysis/0518_NATIVE_COVERAGE_WINDOWS.json")
    if manifest["rom_sha256"]!=ROM_SHA or len(manifest["windows"])!=25:
        raise ValueError("0518 source manifest drift")
    rows=[]
    for r in manifest["windows"]:
        bank=int(r["raw_or_fixed_bank"],16)
        lo,hi=int(r["start_cpu"],16),int(r["end_cpu_exclusive"],16)
        if bank==31 and 0xE000<=lo<hi<=0x10000:
            off=31*8192+lo-0xE000
        elif bank==30 and 0xC000<=lo<hi<=0xE000:
            off=30*8192+lo-0xC000
        elif 0<=bank<16 and 0x8000<=lo<hi<=0xC000:
            off=bank*16384+lo-0x8000
        else:raise ValueError("0518 mapper window invalid")
        if r["prg_offset"]!=off or r["length"]!=hi-lo:
            raise ValueError("0518 physical mapping mismatch")
        rows.append(block(r["checkpoint"],off,r["length"],r["sha256"],r["kind"]))
    return rows

def make_mask(rows,disjoint):
    mask=bytearray(PRG_SIZE)
    for r in rows:
        a,b=r["offset"],r["offset"]+r["length"]
        if disjoint and any(mask[a:b]):
            raise ValueError("Source interval overlaps another interval")
        mask[a:b]=b"\x01"*(b-a)
    return mask

def emit_fragment(path,reg,data):
    lines=["; Original-JP source-byte recomp scaffold; no semantic CPU claims\n",
           "; Physical PRG 0x%06X, checkpoint %s, kind %s\n"%(
            reg["offset"],reg["checkpoint"],reg["kind"]),
           "; SHA256 %s\n"%reg["sha256"]]
    for i in range(0,len(data),16):
        lines.append("    .byte "+",".join("$%02X"%n for n in data[i:i+16])+"\n")
    path.write_text("".join(lines),encoding="ascii")
    rebuilt=bytes(int(n,16) for line in lines[3:]
                  for n in re.findall(r"\$([0-9A-F]{2})",line))
    if rebuilt!=data:raise ValueError("Literal-source roundtrip mismatch")

def audit(romfile=None,emit=None):
    rows=certified()
    mask=make_mask(rows,True)
    counts={f"{i:04d}":sum(r["length"] for r in rows
                               if r["checkpoint"]==f"{i:04d}")
            for i in (500,501,502,504,507,508)}
    if counts!={"0500":982,"0501":4364,"0502":2,"0504":576,"0507":5,"0508":100}:
        raise ValueError("Certified historical interval breakdown drift")
    if len(rows)!=59 or sum(mask)!=6029:raise ValueError("Expected 6029 byte union")
    windows=source_windows()
    observed=make_mask(windows,True)
    if sum(observed)!=1365:raise ValueError("Expected 1365 source bytes")
    stage_masks={stage:make_mask([r for r in rows if r["checkpoint"]==stage],True)
                 for stage in counts}
    per_stage={stage:sum(a and b for a,b in zip(observed,sm))
               for stage,sm in stage_masks.items()}
    missing=bytearray(int(a and not b) for a,b in zip(observed,mask))
    if per_stage!={"0500":0,"0501":546,"0502":2,
                   "0504":0,"0507":0,"0508":78} or sum(missing)!=739:
        raise ValueError("Full incremental reconciliation mismatch")
    if emit and not romfile:raise ValueError("--emit requires --rom")
    if romfile:
        rom=Path(romfile).read_bytes()
        if len(rom)!=393232 or H(rom)!=ROM_SHA:raise ValueError("Original JP ROM SHA mismatch")
        prg=rom[16:16+PRG_SIZE]
        for r in rows+windows:
            chunk=prg[r["offset"]:r["offset"]+r["length"]]
            if H(chunk)!=r["sha256"]:
                raise ValueError("Original ROM fingerprint mismatch: "+str(r))
        if emit:
            emit=Path(emit);emit.mkdir(parents=True,exist_ok=True)
            for idx,r in enumerate(sorted(rows,key=lambda x:x["offset"])):
                data=prg[r["offset"]:r["offset"]+r["length"]]
                emit_fragment(emit/("%02d_%s_%06x.asm"%(
                    idx,r["checkpoint"],r["offset"])),r,data)
    return {
        "schema":"JP-0525-PRG-incremental-reconciliation/v1",
        "original_rom_sha256":ROM_SHA,
        "original_rom_checked":bool(romfile),
        "source_recomp_fragments":len(rows) if emit else 0,
        "incremental_intervals":len(rows),
        "incremental_bytes":sum(mask),
        "incremental_certificate_by_checkpoint":counts,
        "incremental_mask_sha256":H(mask),
        "pre_0500_unmapped_baseline_bytes":49504-sum(mask),
        "total_strict_prg_unchanged":49504,
        "0510_to_0517_source_bytes":sum(observed),
        "previously_certified_by_checkpoint":per_stage,
        "outside_explicit_incremental_mask":sum(missing),
        "outside_mask_sha256":H(missing),
        "new_globally_promoted_bytes":0,
        "limitation":"Pre-0500 43475-byte physical certified union missing; 739 is NOT a global novel-byte count",
        "recomp_limitation":"Verified literal source fragments only; no assembler-instruction semantic closure"
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rom",type=Path)
    p.add_argument("--report",type=Path)
    p.add_argument("--emit-literal-fragments",type=Path)
    a=p.parse_args()
    result=audit(a.rom,a.emit_literal_fragments)
    if a.report:a.report.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("PASS PRG source reconciliation:",result["incremental_bytes"],
          "disjoint certified bytes; 739 need earlier baseline; strict=49504")
if __name__=="__main__":main()
