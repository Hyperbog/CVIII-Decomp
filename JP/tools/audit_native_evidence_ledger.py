#!/usr/bin/env python3
"""ROM-free native decomp evidence integrity gate.

This acts as durable, executable 'learning' for future research sessions:
every historical original-Mesen comparison must declare natural-vs-injected
provenance, exact compared RAM bytes, a replay source, and no unearned PRG/VPP.
Do not treat multiple overlapping source windows as independent live events.

When a new checkpoint is verified, append one manifest entry, use explicit
case/byte field names, and run this checker before making the checkpoint claim.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM_SHA = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
CHECKSUM = re.compile(r"^[0-9a-f]{64}$")
CERT_KEYS = (
    "strict_new_prg_bytes", "new_strict_prg_bytes", "strict_PRG_bytes_added",
    "certified_PRG_addition", "certified_new_prg_bytes",
    "additional_prg_certified_bytes", "new_VPP", "vpp_added",
    "VPP_added", "VPP_addition", "new_vpp", "additional_vpp_points",
)

def insist(ok: bool, problem: str) -> None:
    if not ok:
        raise ValueError(problem)

def read(path: str) -> dict:
    file = ROOT / path
    insist(file.is_file(), f"Missing required decomp evidence file: {path}")
    result = json.loads(file.read_text(encoding="utf-8"))
    insist(isinstance(result, dict), f"Evidence JSON object expected: {path}")
    return result

def validate() -> dict:
    ledger = read("analysis/NATIVE_EVIDENCE_LEDGER.json")
    insist(ledger.get("schema") == "JP-native-original-evidence-ledger/v1",
           "Unexpected evidence ledger schema")
    insist(ledger.get("rom_sha256") == ROM_SHA, "Evidence ledger ROM identity drift")
    entries = ledger["entries"]
    insist(isinstance(entries, list) and len(entries) >= 7,
           "Missing historical original-JP Mesen evidence checkpoints")
    seen: set[str] = set()
    count = natural = synthetic = comparisons = independent_events = 0
    for e in entries:
        ident = e["id"]
        insist(re.fullmatch(r"\d{4}", ident) is not None and ident not in seen,
               f"Duplicate/malformed checkpoint {ident}")
        seen.add(ident)
        for field in ("report","native","test","replay"):
            file = ROOT / e[field]
            insist(file.is_file() and file.stat().st_size > 0,
                   f"{ident}: {field} evidence file missing or empty: {e[field]}")
        report = read(e["report"])
        insist(report.get("rom_sha256") == ROM_SHA,
               f"{ident}: physical original-JP ROM identity mismatch")
        n = e["natural"]; s = e["synthetic"]; c = e["cases"]
        live = e["independent_natural_events"]
        insist(all(type(value) is int and value >= 0 for value in
                   (n,s,c,live,e["compared_ram"])), f"{ident}: invalid evidence counts")
        insist(c == n + s and 0 <= live <= n,
               f"{ident}: case provenance vs count does not reconcile")
        insist(bool(e.get("note")) and len(e["note"]) > 25,
               f"{ident}: missing provenance/caveat description")
        if n > live:
            insist(any(word in e["note"].lower()
                       for word in ("overlap", "source window", "different")),
                   f"{ident}: repeated natural windows must describe independent events")
        for config_key, expected in (("case_key",c), ("ram_key",e["compared_ram"]),
                                      ("natural_key",n), ("synthetic_key",s)):
            source_key=e.get(config_key)
            if source_key is not None:
                insist(source_key in report and type(report[source_key]) is int
                       and report[source_key] == expected,
                       f"{ident}: {source_key} does not match evidence ledger ({expected})")
        insist(1792*c <= e["compared_ram"] <= 2048*c,
               f"{ident}: impossible original 2KiB RAM comparison count")
        for field in CERT_KEYS:
            if field in report:
                insist(report[field] == 0, f"{ident}: unapproved new PRG/VPP claim: {field}")
        # Every source-block digest must be a SHA-256 value; use the original
        # report field names rather than pretending all reports share a schema.
        for field,value in report.items():
            if "sha256" in field and isinstance(value,str):
                insist(CHECKSUM.fullmatch(value) is not None,
                       f"{ident}: malformed SHA-256 in report field {field}")
        count+=c;natural+=n;synthetic+=s;comparisons+=e["compared_ram"]
        independent_events+=live
    # These historical anchors are intentionally locked. Additional entries
    # may expand totals but must not silently erase or rewrite prior evidence.
    insist({"0513","0514","0515","0516","0517","0519","0520"} <= seen,
           "A verified source checkpoint has disappeared from the evidence ledger")
    state = read("analysis/RESUME_STATE.json")
    expected = ledger["certification"]
    insist(state["last_completed_checkpoint"] == expected["certified_checkpoint"],
           "Source-certified semantic checkpoint changed without ledger review")
    insist(state["progress_metrics"]["strict_verified_prg_floor_bytes"] ==
           expected["strict_prg_floor"],
           "PRG byte floor changed without overlap-deduplicated audit/ledger review")
    insist(state["vpp"]["earned"] == expected["vpp_earned"],
           "VPP changed without evidence/rubric ledger review")
    with (ROOT/"analysis/PROGRESS_SCORE.csv").open(newline="",encoding="utf-8") as source:
        rubric=list(csv.DictReader(source))
    insist(sum(int(row["earned"]) for row in rubric) == expected["vpp_earned"],
           "VPP CSV differs from current evidence/RESUME_STATE")
    insist(sum(int(row["weight"]) for row in rubric) == 100,
           "VPP scoring weights must sum to 100")
    return {"checkpoint_reports":len(entries), "original_mesen_windows":count,
            "natural_windows":natural, "synthetic_windows":synthetic,
            "independent_natural_events_at_most":independent_events,
            "compared_ram_bytes_not_unique":comparisons,
            "strict_prg_floor":expected["strict_prg_floor"],
            "vpp":expected["vpp_earned"]}

def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json",action="store_true",help="Print machine-readable verification totals")
    opts=p.parse_args()
    result=validate()
    if opts.json:
        print(json.dumps(result,indent=2))
    else:
        print("PASS original-JP evidence contract:",
              result["checkpoint_reports"],"reports,",
              result["original_mesen_windows"],"CPU comparison windows (",
              result["natural_windows"],"natural /",
              result["synthetic_windows"],"synthetic ),",
              result["compared_ram_bytes_not_unique"],"compared RAM bytes;",
              "strict PRG=",result["strict_prg_floor"],
              "VPP=",result["vpp"])

if __name__=="__main__":
    main()
