#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path
from extract_raw0b_action_dispatch import load, build

EXPECTED_SHA="eb075c21401906325dc497d6537978590dccf193abc3897d42a4935533800a13"
EXPECTED_DISTINCT=217

def main(path: str):
    r=build(load(Path(path)))
    assert r["raw_512_byte_table_sha256"]==EXPECTED_SHA
    assert r["distinct_targets"]==EXPECTED_DISTINCT
    assert r["all_targets_inside_8000_BFFF"]
    rows=r["rows"]
    assert len(rows)==256
    assert rows[0]["entry_cpu"]==0xBD67
    assert rows[0x7F]["entry_cpu"]==0xBE65
    assert rows[0x80]["entry_cpu"]==0xBE67
    assert rows[0x9D]["entry_cpu"]==0xBEA1
    assert rows[0x9E]["entry_cpu"]==0xBEA3
    assert rows[0x9E]["target_cpu"]==0xBF79
    assert rows[0xFF]["entry_cpu"]==0xBF65
    print("raw-bank $0B action dispatch atlas: OK")
    print("256 mechanical action slots; 217 distinct target words")
    print("512-byte table SHA-256:", EXPECTED_SHA)
    print("$9E secondary entry aliases $BEA3 script-pointer data -> $BF79")
    print("NOTE: structural coverage only; live action-domain proof is separate")

if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("usage: audit_raw0b_action_dispatch.py JP.nes")
    main(sys.argv[1])
