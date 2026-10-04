#!/usr/bin/env python3
"""Verify the PRG22:$8745 owner/state-machine relationship."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

EXPECTED_SHA256 = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"


def u16(data: bytes, off: int) -> int:
    return data[off] | (data[off + 1] << 8)


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {Path(sys.argv[0]).name} <Akumajou Densetsu (Japan).nes>")
        return 2

    rom = Path(sys.argv[1]).read_bytes()
    if hashlib.sha256(rom).hexdigest() != EXPECTED_SHA256:
        print("ERROR: ROM SHA-256 mismatch", file=sys.stderr)
        return 1

    prg = rom[16 : 16 + 0x40000]
    bank22 = prg[22 * 0x2000 : 23 * 0x2000]
    bank23 = prg[23 * 0x2000 : 24 * 0x2000]

    def b22(addr: int, n: int) -> bytes:
        return bank22[addr - 0x8000 : addr - 0x8000 + n]

    def b23(addr: int, n: int) -> bytes:
        return bank23[addr - 0xA000 : addr - 0xA000 + n]

    obj_table = 0xBEA3
    type26_ptr = u16(bank23, obj_table - 0xA000 + 2 * 0x26)
    if type26_ptr != 0xAE6A:
        print(f"ERROR: object type $26 table is ${type26_ptr:04X}", file=sys.stderr)
        return 1

    def action_ptr(action: int) -> int:
        if action < 0x80:
            return u16(bank23, 0xBD67 - 0xA000 + 2 * action)
        return u16(bank23, 0xBE67 - 0xA000 + ((action << 1) & 0xFF))

    expected_actions = {0x0B: 0x8519, 0x5C: 0x871E, 0x8A: 0x86F2}
    for action, expected in expected_actions.items():
        actual = action_ptr(action)
        if actual != expected:
            print(
                f"ERROR: action ${action:02X} -> ${actual:04X}, expected ${expected:04X}",
                file=sys.stderr,
            )
            return 1

    records = [b23(0xAE6A + 4 * state, 4) for state in range(48)]

    expected = {
        0x07: bytes.fromhex("0B 12 12 00"),
        0x08: bytes.fromhex("5C 00 00 00"),
        0x13: bytes.fromhex("0B 12 12 00"),
        0x14: bytes.fromhex("5C 00 00 00"),
        0x2B: bytes.fromhex("8A 00 00 00"),
    }
    for state, value in expected.items():
        if records[state] != value:
            print(
                f"ERROR: type $26 state ${state:02X} = {records[state].hex(' ')}, "
                f"expected {value.hex(' ')}",
                file=sys.stderr,
            )
            return 1

    selectors = [rec[1] for rec in records if rec[0] == 0x0B]
    if set(selectors) != {0x08, 0x12}:
        print(f"ERROR: type $26 selector set = {sorted(set(selectors))}", file=sys.stderr)
        return 1
    if 0x10 in selectors:
        print("ERROR: selector $10 unexpectedly present in type $26 state table", file=sys.stderr)
        return 1

    if b22(0x8519, 16) != bytes.fromhex(
        "A0 01 B1 02 9D 8C 04 C8 B1 02 9D 00 04 4C 57 83"
    ):
        print("ERROR: action $0B setter signature changed", file=sys.stderr)
        return 1

    if b22(0x8745, 8) != bytes.fromhex("A9 14 9D 00 04 20 09 83"):
        print("ERROR: $8745 frame-$14 signature changed", file=sys.stderr)
        return 1

    print("ROM identity: OK")
    print("object type $26 state table: $AE6A-$AF29 (48 states)")
    print("action $5C -> $871E; action $8A -> $86F2; both reach shared $8745 tail")
    print("state $07 -> selector $12/frame $12; state $08 -> action $5C")
    print("state $13 -> selector $12/frame $12; state $14 -> action $5C")
    print("type $26 explicit selector values:", " ".join(f"${v:02X}" for v in sorted(set(selectors))))
    print("selector $10 is absent from type $26's explicit selector-setting records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
