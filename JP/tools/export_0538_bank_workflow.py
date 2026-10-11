#!/usr/bin/env python3
"""Translate the authenticated 0538 Japanese raw0A atlas into the common bank gate.

This does not certify static candidates. It is a bank-wide audit input and
bounded AI context source; optional ROM auth is a separate, local-only gate.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "SharedDecomp"))
from workflow import (VERSION, EvidenceError, atomic_json, as_addr,
                      context_packet, sha, validate_bank)

ORIGINAL_SHA = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
RAW0A_SHA = "1460df577d44e114c64fdf34a8837629765f3f6a93d45796fdf81e5ffacb5ed8"
EXPECTED = {"verified_code":2162,"verified_tables":168,"candidate_code":2910,
            "structural_data":7460,"unresolved":3684}


def convert_atlas(atlas: dict) -> dict:
    if atlas.get("rom_sha256") != ORIGINAL_SHA or atlas.get("raw_bank_0a_sha256") != RAW0A_SHA:
        raise EvidenceError("0538 atlas ROM/bank provenance mismatch")
    if atlas.get("complete_original_bank_size") != 16384:
        raise EvidenceError("0538 atlas does not describe a whole 16KiB bank")
    mapping={
        "AUDITED 6502":("code","STATIC_PROVED"),
        "AUDITED TABLE":("data","PRODUCER_TYPED_DATA"),
        "STATIC 6502 CANDIDATE (UNPROVED)":("code","STRUCTURAL_CANDIDATE"),
        "UNRESOLVED":("unknown","RAW_FALLBACK"),
    }
    segments=[]
    for i,s in enumerate(atlas.get("address_partition",[])):
        kind=s["kind"]
        if kind in mapping:
            typ,ev=mapping[kind]
        elif kind in {
            "STRUCTURAL PTR (0537)", "FIXED-WIDTH RECORD (0537)",
            "TIER-2/3 SELECTOR PTR", "FOUR-BYTE PAYLOAD CELL",
            "SEVEN-BYTE PAYLOAD RECORD", "FF STREAM TERMINATOR",
            "ROOM MESSAGE POINTERS", "FF TERMINATED ROOM MESSAGE"}:
            typ,ev="data","STRUCTURAL_CANDIDATE"
        else:
            raise EvidenceError(f"unknown source atlas classification {kind!r}")
        segment={"start":s["start_cpu"],"end_exclusive":s["end_cpu_exclusive"],
                 "type":typ,"evidence":ev,"original_kind":kind}
        if ev in ("STATIC_PROVED","PRODUCER_TYPED_DATA"):
            segment["source"]="0538 fullbank audit; original 0507/0508 source certificates"
        segments.append(segment)
    doc={"schema_version":VERSION,
         "bank":{"physical_id":"NES:JP:VRC6:raw0A", "cpu_base":"8000",
                 "size":16384,"sha256":RAW0A_SHA,
                 "mapper":"VRC6 24", "source_prg_index":10},
         "segments":segments,
         "limitations":["NOT a complete executable bank", "static candidate code has no trace-executed entry proof",
                        "structure is not proof of live selector domains", "native parity not established"],
         "certificate":{"original_rom_sha256":ORIGINAL_SHA, "strict_prg_new_bytes":0,
                        "historical_provenance":"0538+0507/0508"}}
    report=validate_bank(doc)
    if (report["verified_instruction_bytes"]!=EXPECTED["verified_code"] or
        report["raw_fallback_bytes"]!=EXPECTED["unresolved"] or
        report["structural_or_unverified_bytes"] != EXPECTED["candidate_code"]+EXPECTED["structural_data"] or
        report["proven_semantic_bytes"]!=EXPECTED["verified_code"]+EXPECTED["verified_tables"]):
        raise EvidenceError(f"0538 category census drift: {report}")
    return doc


def authenticated_bank(path: Path) -> bytes:
    rom=path.read_bytes()
    if len(rom)!=393232 or sha(rom)!=ORIGINAL_SHA:
        raise EvidenceError("wrong retail JP original-ROM identity")
    bank=rom[16+10*0x4000:16+11*0x4000]
    if len(bank)!=16384 or sha(bank)!=RAW0A_SHA:
        raise EvidenceError("raw0A original physical bank mismatch")
    return bank


def smoke() -> None:
    # A structurally sound tiny bank shows the common gate is alive without
    # requiring copyrighted ROM bytes on public GitHub Actions.
    from workflow import validate_bank
    tiny={"schema_version":VERSION,"bank":{"physical_id":"example:rawA","cpu_base":"8000",
        "size":4,"sha256":sha(b'\x00\x00\x00\x00')},
          "segments":[{"start":"8000","end_exclusive":"8004","type":"unknown","evidence":"RAW_FALLBACK"}]}
    assert validate_bank(tiny)["raw_fallback_bytes"]==4
    print("PASS ROM-free JP bank evidence exporter")


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--atlas",type=Path);p.add_argument("--out",type=Path)
    p.add_argument("--rom",type=Path);p.add_argument("--smoke",action="store_true")
    args=p.parse_args(argv)
    if args.smoke:
        smoke();return
    if not args.atlas or not args.out:
        p.error("--atlas and --out required except for --smoke")
    atlas=json.loads(args.atlas.read_text(encoding="utf-8"))
    doc=convert_atlas(atlas)
    bank=authenticated_bank(args.rom) if args.rom else None
    # SHA lock and every physical partition byte are verified when ROM present.
    result=validate_bank(doc,bank)
    if bank is not None:
        for s in doc["segments"]:
            lo,hi=as_addr(s["start"])-0x8000,as_addr(s["end_exclusive"])-0x8000
            s["sha256"]=sha(bank[lo:hi])
    args.out.mkdir(parents=True,exist_ok=True)
    atomic_json(args.out/"raw0a_bank_evidence_v1.json",doc)
    atomic_json(args.out/"raw0a_bank_gate_report.json",result)
    atomic_json(args.out/"raw0a_801e_ai_context.json",context_packet(doc,cpu=0x801E,radius=0x110))
    print(json.dumps(result,sort_keys=True))

if __name__=="__main__":
    try:main()
    except (ValueError,KeyError,OSError) as err:
        print(f"BANK WORKFLOW FAIL: {err}",file=sys.stderr)
        raise SystemExit(2)
