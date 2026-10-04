#!/usr/bin/env python3
"""Verify the committed resume frontier before continuing a decomp checkpoint."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


def cpu_slice(raw_bank: bytes, start: int, end_inclusive: int) -> bytes:
    assert 0x8000 <= start <= end_inclusive < 0xC000
    return raw_bank[start - 0x8000 : end_inclusive - 0x8000 + 1]


def main(rom_path: str) -> None:
    root = Path(__file__).resolve().parents[1]
    state_path = root / "analysis" / "RESUME_STATE.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))

    rom = Path(rom_path).read_bytes()
    rom_sha = hashlib.sha256(rom).hexdigest()
    assert rom_sha == state["rom_sha256"], (rom_sha, state["rom_sha256"])

    prg = rom[16 : 16 + 0x40000]
    first_prg = state["execution_context"]["physical_prg_banks"][0]
    raw_bank = prg[first_prg * 0x2000 : (first_prg + 2) * 0x2000]
    assert len(raw_bank) == 0x4000

    overlap = state["verification_overlap"]
    ostart = int(overlap["start_cpu"], 16)
    oend = int(overlap["end_cpu_inclusive"], 16)
    obytes = cpu_slice(raw_bank, ostart, oend)
    assert len(obytes) == overlap["length"]
    osha = hashlib.sha256(obytes).hexdigest()
    assert osha == overlap["sha256"], (osha, overlap["sha256"])

    fp = state["frontier_fingerprint"]
    fstart = int(fp["start_cpu"], 16)
    fend = int(fp["end_cpu_inclusive"], 16)
    fbytes = cpu_slice(raw_bank, fstart, fend)
    assert len(fbytes) == fp["length"]
    fsha = hashlib.sha256(fbytes).hexdigest()
    assert fsha == fp["sha256"], (fsha, fp["sha256"])

    frontier = state["frontier"]
    assert int(frontier["last_closed_cpu"], 16) + 1 == int(frontier["next_unprocessed_cpu"], 16)
    assert int(overlap["end_cpu_inclusive"], 16) == int(frontier["last_closed_cpu"], 16)
    assert int(fp["start_cpu"], 16) == int(frontier["next_unprocessed_cpu"], 16)

    print("ROM identity: OK", rom_sha)
    print(
        "pre-frontier overlap: OK",
        f"${ostart:04X}-${oend:04X}",
        f"({len(obytes)} bytes)",
        osha,
    )
    print(
        "frontier fingerprint: OK",
        f"${fstart:04X}-${fend:04X}",
        f"({len(fbytes)} bytes)",
        fsha,
    )
    print("last completed checkpoint:", state["last_completed_checkpoint"])
    print("last completed checkpoint commit:", state["last_completed_checkpoint_commit"])
    print("safe resume CPU frontier: $" + frontier["next_unprocessed_cpu"])
    print("next checkpoint:", frontier["next_checkpoint"])
    print("NOTE: verification overlap is not new coverage")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {Path(sys.argv[0]).name} ROM.nes")
    main(sys.argv[1])
