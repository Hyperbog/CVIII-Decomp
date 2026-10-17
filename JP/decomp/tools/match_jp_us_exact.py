#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

JP_SHA = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
US_SHA = "1c7b2ed2c1fb5839a6764006aa476f5c9d48f99465b6141980f3a5af1dfec0d6"
PRG_SIZE = 0x40000
BANK_SIZE = 0x2000

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def load_prg(path: Path, expected_sha: str) -> bytes:
    rom = path.read_bytes()
    assert sha(rom) == expected_sha, (path, sha(rom), expected_sha)
    assert rom[:4] == b"NES\x1a"
    prg = rom[16:16+PRG_SIZE]
    assert len(prg) == PRG_SIZE
    return prg

def build(jp: bytes, us: bytes, n: int) -> dict:
    unique = {}
    repeated = set()
    for j in range(len(us)-n+1):
        key = us[j:j+n]
        if key in repeated:
            continue
        if key in unique:
            del unique[key]
            repeated.add(key)
        else:
            unique[key] = j

    anchors = []
    for i in range(len(jp)-n+1):
        j = unique.get(jp[i:i+n])
        if j is not None:
            anchors.append((i, j))

    mapping = [-1] * len(jp)
    ambiguous = set()
    for i, j in anchors:
        for k in range(n):
            p, q = i+k, j+k
            if mapping[p] == -1:
                mapping[p] = q
            elif mapping[p] != q:
                ambiguous.add(p)
    for p in ambiguous:
        mapping[p] = -2

    runs = []
    i = 0
    while i < len(jp):
        if mapping[i] < 0:
            i += 1
            continue
        s, u = i, mapping[i]
        delta = u - s
        i += 1
        while i < len(jp) and mapping[i] >= 0 and mapping[i] == mapping[i-1] + 1 and mapping[i] - i == delta:
            i += 1
        assert jp[s:i] == us[u:u+(i-s)]
        runs.append({"jp_offset": s, "us_offset": u, "length": i-s, "delta": delta})

    matrix = [[0] * 32 for _ in range(32)]
    for p, q in enumerate(mapping):
        if q >= 0:
            matrix[p // BANK_SIZE][q // BANK_SIZE] += 1

    banks = []
    for jb in range(32):
        total = sum(matrix[jb])
        dest = [
            {"us_prg_bank": ub, "bytes": c}
            for ub, c in sorted(enumerate(matrix[jb]), key=lambda x: (-x[1], x[0]))
            if c
        ]
        banks.append({
            "jp_prg_bank": jb,
            "matched_bytes": total,
            "coverage": total / BANK_SIZE,
            "top_us_destinations": dest[:4],
        })

    covered = sum(1 for q in mapping if q >= 0)
    return {
        "method": {
            "anchor_length": n,
            "anchor_requirement": "anchor bytes occur exactly once in US PRG",
            "coverage_rule": "byte must be covered by at least one unique exact anchor; bytes with conflicting anchor mappings are excluded",
            "semantic_status": "accelerator only; exact correspondence is not JP semantic verification",
        },
        "jp_rom_sha256": JP_SHA,
        "us_rom_sha256": US_SHA,
        "prg_size": PRG_SIZE,
        "unique_us_anchor_count": len(unique),
        "repeated_us_anchor_keys": len(repeated),
        "jp_unique_anchor_hits": len(anchors),
        "ambiguous_jp_bytes_excluded": len(ambiguous),
        "matched_jp_bytes": covered,
        "matched_jp_fraction": covered / PRG_SIZE,
        "exact_runs": len(runs),
        "largest_runs": sorted(runs, key=lambda r: (-r["length"], r["jp_offset"]))[:32],
        "banks": banks,
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("jp_rom", type=Path)
    ap.add_argument("us_rom", type=Path)
    ap.add_argument("--anchor", type=int, default=32)
    ap.add_argument("--output", type=Path)
    ns = ap.parse_args()
    assert ns.anchor >= 16
    report = build(load_prg(ns.jp_rom, JP_SHA), load_prg(ns.us_rom, US_SHA), ns.anchor)
    text = json.dumps(report, indent=2) + "\n"
    if ns.output:
        ns.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")

if __name__ == "__main__":
    main()
