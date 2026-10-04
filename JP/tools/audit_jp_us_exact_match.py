#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path
from match_jp_us_exact import JP_SHA, US_SHA, build, load_prg

EXPECTED_MATCHED = 115865
EXPECTED_RUNS = 821
EXPECTED_AMBIG = 73
EXPECTED_BANK_BYTES = [
3217,4389,3039,2981,3605,3471,2357,5942,
313,686,254,660,8033,7982,6796,7306,
8180,7622,4023,2298,3303,1894,2549,3693,
311,2950,5734,5083,1699,2777,480,2238,
]
EXPECTED_LARGEST = (59617,59361,5919)

def main(jp_path: str, us_path: str) -> None:
    jp = load_prg(Path(jp_path), JP_SHA)
    us = load_prg(Path(us_path), US_SHA)
    r = build(jp, us, 32)
    assert r["matched_jp_bytes"] == EXPECTED_MATCHED
    assert r["exact_runs"] == EXPECTED_RUNS
    assert r["ambiguous_jp_bytes_excluded"] == EXPECTED_AMBIG
    assert [b["matched_bytes"] for b in r["banks"]] == EXPECTED_BANK_BYTES
    lr = r["largest_runs"][0]
    assert (lr["jp_offset"],lr["us_offset"],lr["length"]) == EXPECTED_LARGEST
    print("JP ROM identity: OK")
    print("US ROM identity: OK")
    print("unique-anchor exact correspondence: 115865 / 262144 bytes = 44.19898986816406%")
    print("exact correspondence runs:", EXPECTED_RUNS)
    print("ambiguous JP bytes excluded:", EXPECTED_AMBIG)
    print("largest exact run: JP +$%05X -> US +$%05X, %d bytes" % EXPECTED_LARGEST)
    print("NOTE: correspondence is an accelerator only; it does not promote semantic verification")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: audit_jp_us_exact_match.py JP.nes US.nes")
    main(sys.argv[1], sys.argv[2])
