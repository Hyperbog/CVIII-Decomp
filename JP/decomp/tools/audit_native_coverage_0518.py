#!/usr/bin/env python3
"""Deterministic 0518 physical-PRG reconciliation against named prior certificates.

This is a PARTIAL overlap audit: only original 0501 certified-region manifest
and separately certified 0508 fixed-bank additions. It NEVER grants strict PRG
credit to a byte absent from those two references; the complete intervening
historical 49,504-byte ledger must be reconciled separately.

Usage:
  python3 JP/decomp/tools/audit_native_coverage_0518.py
  python3 JP/decomp/tools/audit_native_coverage_0518.py --rom "Akumajou Densetsu (Japan).nes"
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM_HASH = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"

def die_if(condition: bool, detail: str) -> None:
    if condition:
        raise ValueError(detail)

def physical_window(record: dict) -> tuple[int, int]:
    bank = int(record["raw_or_fixed_bank"], 16)
    lo = int(record["start_cpu"], 16)
    hi = int(record["end_cpu_exclusive"], 16)
    if bank == 0x1f:
        die_if(not (0xe000 <= lo < hi <= 0x10000), "fixed bank 31 window")
        offset = bank * 0x2000 + lo - 0xe000
    elif bank == 0x1e:
        die_if(not (0xc000 <= lo < hi <= 0xe000), "bank 30 window")
        offset = bank * 0x2000 + lo - 0xc000
    else:
        die_if(not (0 <= bank < 0x10 and 0x8000 <= lo < hi <= 0xc000),
               "raw VRC6 16KiB bank window")
        offset = bank * 0x4000 + lo - 0x8000
    die_if(record["prg_offset"] != offset or record["length"] != hi-lo,
           "physical bank mapping or width mismatch")
    die_if(offset < 0 or offset + hi-lo > 0x40000, "outside JP 256 KiB PRG")
    die_if(len(record["sha256"]) != 64, "missing physical-ROM fingerprint")
    return offset, hi-lo

def offsets(ranges: list[tuple[int,int]]) -> set[int]:
    seen = set()
    for start, length in ranges:
        die_if(length <= 0, "invalid source range width")
        block = set(range(start, start+length))
        die_if(bool(block & seen), "overlapping certified reference regions")
        seen.update(block)
    return seen

def audit(rom_file: Path | None = None) -> dict:
    registry = json.loads((ROOT/"analysis/0518_NATIVE_COVERAGE_WINDOWS.json").read_text())
    original = json.loads((ROOT/"SharedNES/JP_0501_CERTIFIED_REGIONS.json").read_text())
    state = json.loads((ROOT/"analysis/RESUME_STATE.json").read_text())
    die_if(registry["rom_sha256"] != ROM_HASH or original["source_rom_sha256"] != ROM_HASH
           or state["rom_sha256"] != ROM_HASH, "original ROM identity mismatch")
    die_if(registry["schema"] != "JP-0518-native-source-window-ledger/v1",
           "invalid source-window schema")
    first = [(r["source_prg_offset"], r["size"]) for r in original["regions"]]
    first_set = offsets(first)
    die_if(len(first_set) != original["total_certified_source_bytes"] or len(first_set)!=4364,
           "0501 region count or claimed byte total changed")
    last_ranges = state["prior_dependency_manifest"]["exact_new_ranges"]
    die_if(state["last_completed_checkpoint"] != "0508"
           or state["prior_dependency_manifest"]["checkpoint"] != "0508",
           "checkpoint 0508 dependency ledger changed")
    last_set = offsets([(int(r["prg_offset_start"],16),r["length"]) for r in last_ranges])
    die_if(len(last_set)!=100 or bool(first_set & last_set),
           "0508 100-byte addition no longer disjoint from 0501 reference")
    windows = registry["windows"]
    die_if(len(windows)!=25, "unexpected 0510-0517 window inventory")
    observed = set()
    for window in windows:
        die_if(window["kind"] not in ("code","data","mixed"), "unknown classification")
        off,size=physical_window(window)
        span=set(range(off,off+size))
        die_if(bool(span & observed), "tracking windows overlap without deduplication")
        observed.update(span)
    previously_0501 = observed & first_set
    previously_0508 = (observed & last_set) - first_set
    not_in_these_two = observed - first_set - last_set
    result = {
        "schema":"JP-0518-native-coverage-reconciliation/v1",
        "original_rom_sha256":ROM_HASH,
        "tracked_windows":len(windows),
        "tracked_unique_source_bytes":len(observed),
        "already_in_0501_reference":len(previously_0501),
        "already_in_0508_reference_only":len(previously_0508),
        "outside_both_named_reference_manifests":len(not_in_these_two),
        "reference_0501_certified_bytes":len(first_set),
        "reference_0508_addition_bytes":len(last_set),
        "full_strict_prg_floor_unchanged":state["progress_metrics"]["strict_verified_prg_floor_bytes"],
        "promotable_strict_prg_bytes":0,
        "warning":"The outside-both count is NOT globally novel against the 49,504-byte historical ledger; 0502-0507 and other strict intervals still need a unified audit.",
    }
    die_if((result["tracked_unique_source_bytes"],
            result["already_in_0501_reference"],
            result["already_in_0508_reference_only"],
            result["outside_both_named_reference_manifests"]) != (1365,546,78,741),
           "original source window reconciliation drift")
    die_if(result["full_strict_prg_floor_unchanged"] != 49504,
           "unexpected certified strict PRG floor")

    if rom_file:
        rom = rom_file.read_bytes()
        die_if(len(rom) != 393232 or hashlib.sha256(rom).hexdigest()!=ROM_HASH,
               "original JP retail ROM identity/size mismatch")
        prg = rom[16:16+0x40000]
        # Validate every recorded source byte fingerprint against actual
        # physical PRG, including the two older reference certificates.
        for r in original["regions"]:
            begin=r["source_prg_offset"]; data=prg[begin:begin+r["size"]]
            die_if(hashlib.sha256(data).hexdigest()!=r["sha256"],
                   "0501 certified source ROM fingerprint drift")
        for r in last_ranges:
            begin=int(r["prg_offset_start"],16)
            data=prg[begin:begin+r["length"]]
            die_if(hashlib.sha256(data).hexdigest()!=r["sha256"],
                   "0508 certified source ROM fingerprint drift")
        for r in windows:
            begin,width=physical_window(r)
            die_if(hashlib.sha256(prg[begin:begin+width]).hexdigest()!=r["sha256"],
                   "0510-0517 tracked physical-source fingerprint drift")
        result["optional_original_rom_hash_audit"]="PASS: all 25 windows and 35 prior reference intervals"
    # The VPP rubric can evolve independently of strict PRG credit.
    with (ROOT/"analysis/PROGRESS_SCORE.csv").open(newline="",encoding="utf-8") as source:
        score=list(csv.DictReader(source))
    die_if(sum(int(x["weight"]) for x in score)!=100,"VPP weights changed")
    earned=sum(int(x["earned"]) for x in score)
    die_if(earned!=state["vpp"]["earned"],"VPP CSV/resume state diverged")
    result["vpp"]=earned
    return result

def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom",type=Path,default=None)
    parser.add_argument("--report",type=Path,default=None)
    args=parser.parse_args()
    result=audit(args.rom)
    if args.report: args.report.write_text(json.dumps(result,indent=2)+"\n")
    print("PASS 0518 physical PRG partial-reference reconciliation",
          result["tracked_unique_source_bytes"],
          "source bytes; 0501=",result["already_in_0501_reference"],
          "0508=",result["already_in_0508_reference_only"],
          "requires historical full-ledger review=",result["outside_both_named_reference_manifests"],
          "VPP=",result["vpp"])
if __name__=="__main__":main()
