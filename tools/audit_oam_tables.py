#!/usr/bin/env python3
"""Audit PRG26 sprite-set table structure and key OAM-renderer invariants."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

EXPECTED_SHA256 = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
EXPECTED_SET_PTRS = [
    0x819D, 0x820D, 0x8265, 0x82AF, 0x8AB0,
    0x9545, 0xAAA6, 0xABEA, 0x9E6D, 0x8BB0,
    0xABA6, 0x819D, 0x820D, 0x8265, 0x82AF,
]


def cpu26_offset(addr: int) -> int:
    if not 0x8000 <= addr <= 0x9FFF:
        raise ValueError(f"PRG26 CPU address out of range: {addr:04X}")
    return 26 * 0x2000 + (addr - 0x8000)


def u16(data: bytes, off: int) -> int:
    return data[off] | (data[off + 1] << 8)


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {Path(sys.argv[0]).name} <Akumajou Densetsu (Japan).nes>")
        return 2

    rom = Path(sys.argv[1]).read_bytes()
    sha256 = hashlib.sha256(rom).hexdigest()
    if sha256 != EXPECTED_SHA256:
        print("ERROR: ROM SHA-256 mismatch", file=sys.stderr)
        return 1

    if rom[:4] != b"NES\x1a":
        print("ERROR: not iNES", file=sys.stderr)
        return 1

    prg = rom[16:16 + 0x40000]

    table_off = cpu26_offset(0x817F)
    raw = prg[table_off:table_off + 0x1E]
    ptrs = [u16(raw, i) for i in range(0, len(raw), 2)]
    if ptrs != EXPECTED_SET_PTRS:
        print("ERROR: $817F selector table does not match expected pointers", file=sys.stderr)
        return 1

    # High selector aliases reuse the first four geometry/frame-pointer tables.
    if ptrs[11:15] != ptrs[0:4]:
        print("ERROR: $16/$18/$1A/$1C alias relationship changed", file=sys.stderr)
        return 1

    # First byte immediately after canonical selector block is the first byte
    # of the $819D second-level table. Entry 0 points exactly there.
    if ptrs[0] != 0x819D or 0x817F + len(raw) != 0x819D:
        print("ERROR: canonical first-level table boundary mismatch", file=sys.stderr)
        return 1

    # Verify key renderer opcode signatures instead of relying on documentation.
    signatures = {
        0x8070: bytes.fromhex("bc8c04840fb97f818508b980818509"),
        0x808B: bytes.fromhex("a000b10a8503"),
        0x8117: bytes.fromhex("b10a494085109d0202"),
        0x8172: bytes.fromhex("a50fc9169006b10a1869803860"),
    }
    for addr, expected in signatures.items():
        off = cpu26_offset(addr)
        actual = prg[off:off + len(expected)]
        if actual != expected:
            print(f"ERROR: renderer signature mismatch at ${addr:04X}", file=sys.stderr)
            return 1

    # Producer table at PRG25:$ADA3 is outside PRG26, so use physical mapping.
    # PRG25 is mapped at CPU $A000-$BFFF when its 16 KiB pair is active.
    ada3_off = 25 * 0x2000 + (0xADA3 - 0xA000)
    producer = prg[ada3_off:ada3_off + 12]
    high_selectors = [producer[i] for i in (0, 3, 6, 9)]
    if high_selectors != [0x16, 0x18, 0x1A, 0x1C]:
        print("ERROR: PRG25 $ADA3 high-selector producer table changed", file=sys.stderr)
        return 1

    print("ROM identity: OK")
    print("PRG26 first-level sprite-set table: $817F-$819C (15 pointers)")
    for index, ptr in enumerate(ptrs):
        selector = index * 2
        suffix = " alias +$80 tile class" if selector >= 0x16 else ""
        print(f"  selector ${selector:02X} -> ${ptr:04X}{suffix}")
    print("PRG25 high-selector producer: $16 $18 $1A $1C")
    print("Renderer opcode signatures: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
