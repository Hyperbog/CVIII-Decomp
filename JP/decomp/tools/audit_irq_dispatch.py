#!/usr/bin/env python3
"""Audit the bank-1 VRC6 IRQ dispatch table and IRQ-state producers.

This script does not disassemble arbitrary code. It verifies byte-level facts that the
manual analysis depends on, so table-boundary and state-domain claims can be
rechecked against an immutable ROM.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

EXPECTED_SHA256 = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
EXPECTED_TARGETS = [
    0xE118, 0xA078, 0xA0A8, 0xA0CF, 0xA102, 0xA10D, 0xA120, 0xA14B,
    0xA16F, 0xA1D5, 0xA1FA, 0xA10D, 0xA120, 0xA18B, 0xA1B1, 0xA1FA,
    0xA235, 0xA243, 0xA249, 0xA293, 0xA2E2, 0xA310, 0xA01C, 0x9FD5,
    0x9FE3, 0x9FA1, 0xA323, 0xA340, 0xA357, 0xA36B, 0xA3A8, 0xA3ED,
    0xA405, 0xA3A8, 0xA420, 0x9F99, 0xA293, 0xA2DD, 0xA316, 0xA2EA,
    0xA310, 0xA497, 0xA4B2, 0xA4DF, 0xA4EC,
]


def prg_offset_for_bank1_cpu(cpu: int) -> int:
    if not 0x8000 <= cpu <= 0xBFFF:
        raise ValueError(f"CPU address ${cpu:04X} is not in the bank-1 16 KiB window")
    return 0x4000 + (cpu - 0x8000)


def find_all(data: bytes, pattern: bytes) -> list[int]:
    out: list[int] = []
    pos = 0
    while True:
        pos = data.find(pattern, pos)
        if pos < 0:
            return out
        out.append(pos)
        pos += 1


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {Path(sys.argv[0]).name} <Akumajou Densetsu (Japan).nes>")
        return 2

    rom = Path(sys.argv[1]).read_bytes()
    actual_sha256 = hashlib.sha256(rom).hexdigest()
    if actual_sha256 != EXPECTED_SHA256:
        print(f"ERROR: wrong ROM SHA-256: {actual_sha256}", file=sys.stderr)
        return 1

    if rom[:4] != b"NES\x1a":
        print("ERROR: not an iNES ROM", file=sys.stderr)
        return 1

    prg_size = rom[4] * 0x4000
    prg = rom[16 : 16 + prg_size]
    if len(prg) != 0x40000:
        print(f"ERROR: unexpected PRG size {len(prg):#x}", file=sys.stderr)
        return 1

    table_cpu = 0x9F01
    table_off = prg_offset_for_bank1_cpu(table_cpu)
    targets = []
    for state in range(0x2D):
        lo = prg[table_off + state * 2]
        hi = prg[table_off + state * 2 + 1]
        targets.append(lo | (hi << 8))

    if targets != EXPECTED_TARGETS:
        print("ERROR: IRQ dispatch table differs from expected analysis", file=sys.stderr)
        for i, (actual, expected) in enumerate(zip(targets, EXPECTED_TARGETS)):
            if actual != expected:
                print(f"  state {i:02X}: actual=${actual:04X} expected=${expected:04X}", file=sys.stderr)
        return 1

    first_after_table = table_off + len(EXPECTED_TARGETS) * 2
    expected_code_prefix = bytes.fromhex("CE 81 07 D0 26 A5 7A 29 0F 0A A8")
    actual_prefix = prg[first_after_table : first_after_table + len(expected_code_prefix)]
    if actual_prefix != expected_code_prefix:
        print("ERROR: code entry after table does not match $9F5B", file=sys.stderr)
        return 1

    print("ROM identity: OK")
    print("IRQ table: $9F01-$9F5A, 45 states ($00-$2C): OK")
    for state, target in enumerate(targets):
        print(f"  {state:02X} -> ${target:04X}")
    print("post-table code: $9F5B begins CE 81 07 (DEC $0781): OK")

    # Raw whole-PRG producer-pattern inventory. These are byte-pattern hits only;
    # manual analysis decides which hits are executable instruction boundaries.
    print("\nraw $6A mutation-pattern hits (PRG offsets):")
    for opcode, name in (
        (0x85, "STA zp"), (0x86, "STX zp"), (0x84, "STY zp"),
        (0xE6, "INC zp"), (0xC6, "DEC zp"), (0x06, "ASL zp"),
        (0x46, "LSR zp"), (0x26, "ROL zp"), (0x66, "ROR zp"),
    ):
        hits = find_all(prg, bytes((opcode, 0x6A)))
        if hits:
            print(f"  {name:7s}: " + " ".join(f"{x:05X}" for x in hits))

    print("\nraw $43 mutation-pattern hits (PRG offsets):")
    for opcode, name in (
        (0x85, "STA zp"), (0x86, "STX zp"), (0x84, "STY zp"),
        (0xE6, "INC zp"), (0xC6, "DEC zp"), (0x06, "ASL zp"),
        (0x46, "LSR zp"), (0x26, "ROL zp"), (0x66, "ROR zp"),
    ):
        hits = find_all(prg, bytes((opcode, 0x43)))
        if hits:
            print(f"  {name:7s}: " + " ".join(f"{x:05X}" for x in hits))

    immediate_seeds = []
    for i in range(len(prg) - 3):
        if prg[i] == 0xA9 and prg[i + 2] == 0x85 and prg[i + 3] == 0x43:
            immediate_seeds.append((i, prg[i + 1]))

    print("\nraw adjacent LDA #imm / STA $43 sequences:")
    for off, value in immediate_seeds:
        print(f"  {off:05X}: ${value:02X}")

    allowed_raw_immediates = {
        0x01, 0x05, 0x0B, 0x10, 0x12, 0x13, 0x16, 0x17,
        0x19, 0x1A, 0x1E, 0x21, 0x23, 0x29, 0x80,
    }
    actual_values = {value for _, value in immediate_seeds}
    if not actual_values <= allowed_raw_immediates:
        print(
            "ERROR: unexpected raw immediate seed(s): "
            + ", ".join(f"${x:02X}" for x in sorted(actual_values - allowed_raw_immediates)),
            file=sys.stderr,
        )
        return 1

    print("IRQ producer byte-level audit: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
