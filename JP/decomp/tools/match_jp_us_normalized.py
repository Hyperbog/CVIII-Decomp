#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path

from build_whole_prg_atlas import OPS, BR
from match_jp_us_exact import JP_SHA, US_SHA, PRG_SIZE, BANK_SIZE, build as build_exact, load_prg

def norm_sig(prg: bytes, off: int, instruction_count: int):
    tokens = bytearray()
    p = off
    for _ in range(instruction_count):
        if p >= len(prg):
            return None
        op = prg[p]
        if op not in OPS:
            return None
        mn, mode, n = OPS[op]
        if p+n > len(prg):
            return None
        raw = prg[p:p+n]
        tokens.append(op)
        if n == 2:
            tokens.append(0 if mode == "rel" else raw[1])
        elif n == 3:
            val = raw[1] | raw[2] << 8
            if mn in ("JSR", "JMP") or val >= 0x8000:
                tokens.extend((0, 0))
            else:
                tokens.extend((raw[1], raw[2]))
        p += n
    return bytes(tokens), p-off

def build(jp: bytes, us: bytes, instruction_count: int = 16) -> dict:
    unique = {}
    repeated = set()
    valid_us = 0
    for off in range(len(us)):
        r = norm_sig(us, off, instruction_count)
        if r is None:
            continue
        valid_us += 1
        sig, length = r
        if sig in repeated:
            continue
        if sig in unique:
            del unique[sig]
            repeated.add(sig)
        else:
            unique[sig] = (off, length)

    matches = []
    coverage = bytearray(len(jp))
    for off in range(len(jp)):
        r = norm_sig(jp, off, instruction_count)
        if r is None:
            continue
        sig, length = r
        u = unique.get(sig)
        if u is None:
            continue
        us_off, us_len = u
        matches.append((off, us_off, length, us_len))
        coverage[off:off+length] = b"\x01" * length

    exact = build_exact(jp, us, 32)
    n = 32
    uexact = {}
    repeated_exact = set()
    for j in range(len(us)-n+1):
        key = us[j:j+n]
        if key in repeated_exact:
            continue
        if key in uexact:
            del uexact[key]
            repeated_exact.add(key)
        else:
            uexact[key] = j
    mapping = [-1] * len(jp)
    ambiguous = set()
    for i in range(len(jp)-n+1):
        j = uexact.get(jp[i:i+n])
        if j is None:
            continue
        for k in range(n):
            p, q = i+k, j+k
            if mapping[p] == -1:
                mapping[p] = q
            elif mapping[p] != q:
                ambiguous.add(p)
    for p in ambiguous:
        mapping[p] = -2

    exact_mask = bytearray(1 if q >= 0 else 0 for q in mapping)
    exact_supported = consistent = inconsistent = 0
    for jpo, uso, _, _ in matches:
        if mapping[jpo] >= 0:
            exact_supported += 1
            if mapping[jpo] == uso:
                consistent += 1
            else:
                inconsistent += 1

    banks = []
    for b in range(32):
        s, e = b*BANK_SIZE, (b+1)*BANK_SIZE
        norm = sum(coverage[s:e])
        union = sum(1 for i in range(s, e) if coverage[i] or exact_mask[i])
        banks.append({
            "jp_prg_bank": b,
            "normalized_candidate_bytes": norm,
            "exact_or_normalized_candidate_bytes": union,
            "exact_or_normalized_fraction": union / BANK_SIZE,
        })

    norm_bytes = sum(coverage)
    union_bytes = sum(1 for i in range(len(jp)) if coverage[i] or exact_mask[i])
    return {
        "method": {
            "instruction_count": instruction_count,
            "normalization": [
                "preserve opcode byte",
                "replace relative-branch displacement with zero",
                "replace JSR/JMP absolute operand with zero",
                "replace absolute/absolute-indexed ROM operands >= $8000 with zero",
                "preserve immediates and RAM/I/O operands",
            ],
            "semantic_status": "candidate structural correspondence only; not semantic verification",
        },
        "jp_rom_sha256": JP_SHA,
        "us_rom_sha256": US_SHA,
        "valid_us_start_offsets": valid_us,
        "unique_us_signatures": len(unique),
        "repeated_signature_keys": len(repeated),
        "jp_unique_signature_matches": len(matches),
        "normalized_candidate_bytes": norm_bytes,
        "normalized_candidate_fraction": norm_bytes / PRG_SIZE,
        "exact_baseline_bytes": exact["matched_jp_bytes"],
        "exact_or_normalized_candidate_bytes": union_bytes,
        "exact_or_normalized_candidate_fraction": union_bytes / PRG_SIZE,
        "calibration_exact_supported_starts": exact_supported,
        "calibration_consistent_us_offsets": consistent,
        "calibration_inconsistent_us_offsets": inconsistent,
        "banks": banks,
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("jp_rom", type=Path)
    ap.add_argument("us_rom", type=Path)
    ap.add_argument("--instructions", type=int, default=16)
    ap.add_argument("--output", type=Path)
    ns = ap.parse_args()
    assert ns.instructions >= 8
    report = build(load_prg(ns.jp_rom, JP_SHA), load_prg(ns.us_rom, US_SHA), ns.instructions)
    text = json.dumps(report, indent=2) + "\n"
    if ns.output:
        ns.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")

if __name__ == "__main__":
    main()
