#!/usr/bin/env python3
"""Verify checkpoint 04E1: PRG18 type $E1 selector-$10 frame domain."""
from __future__ import annotations
import hashlib
import sys
from pathlib import Path

EXPECTED_SHA256 = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {Path(sys.argv[0]).name} <Akumajou Densetsu (Japan).nes>")
        return 2
    rom = Path(sys.argv[1]).read_bytes()
    if hashlib.sha256(rom).hexdigest() != EXPECTED_SHA256:
        print("ERROR: ROM SHA-256 mismatch", file=sys.stderr)
        return 1
    prg = rom[16:16 + 0x40000]
    pair = prg[18 * 0x2000:20 * 0x2000]

    def r(addr: int, n: int) -> bytes:
        if not 0x8000 <= addr <= 0xBFFF:
            raise ValueError(addr)
        return pair[addr - 0x8000:addr - 0x8000 + n]

    def u16(addr: int) -> int:
        b = r(addr, 2)
        return b[0] | (b[1] << 8)

    # Creation path: frame E8/EC, selector 10, type E1, state 0.
    setup = bytes.fromhex(
        "b93b9e8507a404996505c90e9004c9129004a9ecd002a9e8"
        "990004a910998c04"
    )
    if r(0x9DE0, len(setup)) != setup:
        print("ERROR: E1 creation/render setup signature changed", file=sys.stderr)
        return 1
    if r(0x9E0F, 10) != bytes.fromhex("a9e199ef05a90099c105"):
        print("ERROR: E1 type/state initialization signature changed", file=sys.stderr)
        return 1

    # Type E1 owns exactly $8FC4-$8FCF because E2 begins at $8FD0.
    if u16(0x89E8) != 0x8FC4 or u16(0x89EA) != 0x8FD0:
        print("ERROR: E1/E2 state-table boundaries changed", file=sys.stderr)
        return 1
    states = r(0x8FC4, 12)
    expected_states = bytes.fromhex("3a690b0f0500222246582101")
    if states != expected_states:
        print("ERROR: E1 six-state records changed", file=sys.stderr)
        return 1

    expected_actions = {
        0x3A: 0x9C68,
        0x0B: 0x9482,
        0x05: 0x9623,
        0x22: 0x9897,
        0x46: 0x9B3F,
        0x21: 0x8662,
    }
    for action, target in expected_actions.items():
        if u16(0x85CC + action * 2) != target:
            print(f"ERROR: action ${action:02X} target changed", file=sys.stderr)
            return 1

    # Parameter index $58 => FF 00 FF.
    param_addr = 0x8FE2 + 3 * 0x58
    if r(param_addr, 3) != bytes.fromhex("ff00ff"):
        print("ERROR: E1 state-4 action parameters changed", file=sys.stderr)
        return 1

    # Action $46: FF parameter branches to two INC $0400,X operations.
    if r(0x9B4D, 0x24) != bytes.fromhex(
        "a001b102c9fff015c9fef00a9d8c04c8b1029d000460"
        "de0004de000460fe0004fe000460"
    ):
        print("ERROR: action $46 selector/frame mutation signature changed", file=sys.stderr)
        return 1

    # Other E1 action bodies contain no direct frame mutation opcodes in their
    # reconciled body ranges.
    frame_mutations = [bytes.fromhex("9d0004"), bytes.fromhex("fe0004"), bytes.fromhex("de0004")]
    ranges = [(0x9C68, 0x9C7E), (0x9482, 0x9490), (0x9623, 0x962C), (0x9897, 0x9927), (0x8662, 0x8663)]
    for start, end in ranges:
        body = r(start, end - start)
        if any(pat in body for pat in frame_mutations):
            print(f"ERROR: unexpected frame mutation in action body ${start:04X}", file=sys.stderr)
            return 1

    print("ROM identity: OK")
    print("type E1 state table: $8FC4-$8FCF (6 states)")
    print("setup frames: $E8 or $EC; selector: $10")
    print("state 4 action $46 parameter $FF increments frame by 2")
    print("proven frame evolution: $E8->$EA or $EC->$EE")
    print("selector $10 + frame $14 is unreachable through the E1 state table")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
