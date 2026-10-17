#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path
from match_jp_us_exact import JP_SHA, US_SHA, load_prg
from match_jp_us_normalized import build

EXPECTED_MATCHES = 24014
EXPECTED_NORM_BYTES = 68009
EXPECTED_UNION_BYTES = 149607
EXPECTED_EXACT_SUPPORTED = 13232
EXPECTED_CONSISTENT = 13232
EXPECTED_INCONSISTENT = 0
EXPECTED_UNION_PER_BANK = [
3618,6300,5193,5198,6369,5492,5275,5942,
313,686,254,722,8033,8013,6823,7306,
8180,7677,5626,4189,4389,2582,5571,4365,
397,4165,5882,5661,4900,6545,921,3020,
]

def main(jp_path: str, us_path: str) -> None:
    jp = load_prg(Path(jp_path), JP_SHA)
    us = load_prg(Path(us_path), US_SHA)
    r = build(jp, us, 16)
    assert r["jp_unique_signature_matches"] == EXPECTED_MATCHES
    assert r["normalized_candidate_bytes"] == EXPECTED_NORM_BYTES
    assert r["exact_or_normalized_candidate_bytes"] == EXPECTED_UNION_BYTES
    assert r["calibration_exact_supported_starts"] == EXPECTED_EXACT_SUPPORTED
    assert r["calibration_consistent_us_offsets"] == EXPECTED_CONSISTENT
    assert r["calibration_inconsistent_us_offsets"] == EXPECTED_INCONSISTENT
    assert [b["exact_or_normalized_candidate_bytes"] for b in r["banks"]] == EXPECTED_UNION_PER_BANK
    print("JP/US identities: OK")
    print("16-instruction normalized unique matches:", EXPECTED_MATCHES)
    print("normalized candidate bytes:", EXPECTED_NORM_BYTES)
    print("exact-or-normalized candidate bytes:", EXPECTED_UNION_BYTES, "= 57.07054138183594% PRG")
    print("exact-baseline calibration:", EXPECTED_CONSISTENT, "/", EXPECTED_EXACT_SUPPORTED, "consistent; 0 inconsistent")
    print("NOTE: structural correspondence is candidate evidence only; JP semantic verification is separate")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: audit_jp_us_normalized_match.py JP.nes US.nes")
    main(sys.argv[1], sys.argv[2])
