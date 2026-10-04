#!/usr/bin/env python3
"""Audit PRG26:$8000-$81FF OAM attribute-cache boundary in the JP ROM."""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROM_SHA256 = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
WINDOW_SHA256 = "c45429bfae7777f783641b5206e41d501c67d96a4dee92f6b572961276a43f5a"


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {Path(sys.argv[0]).name} <Akumajou Densetsu (Japan).nes>")
        return 2

    rom = Path(sys.argv[1]).read_bytes()
    if hashlib.sha256(rom).hexdigest() != ROM_SHA256:
        print("ERROR: ROM SHA-256 mismatch", file=sys.stderr)
        return 1

    prg = rom[16:16 + 0x40000]
    prg26 = prg[26 * 0x2000:27 * 0x2000]
    window = prg26[:0x200]  # CPU $8000-$81FF
    if len(window) != 0x200 or hashlib.sha256(window).hexdigest() != WINDOW_SHA256:
        print("ERROR: PRG26:$8000-$81FF signature mismatch", file=sys.stderr)
        return 1

    # $8031 JSR $8070; $8034 INC $05; $8036 BNE $8012.
    # The next object is selected without touching ZP $10.
    if window[0x31:0x38] != bytes.fromhex("207080e605d0da"):
        print("ERROR: object-loop boundary signature mismatch", file=sys.stderr)
        return 1

    expected = {
        (0xA5, 0x10): [0x8064, 0x8166],  # LDA $10: compressed record reuse
        (0x85, 0x10): [0x80BF, 0x811B],  # STA $10: full-record final attribute
    }
    for pattern, addresses in expected.items():
        found = []
        needle = bytes(pattern)
        start = 0
        while True:
            i = window.find(needle, start)
            if i < 0:
                break
            found.append(0x8000 + i)
            start = i + 1
        if found != addresses:
            print(
                f"ERROR: {needle.hex()} locations {found} != expected {addresses}",
                file=sys.stderr,
            )
            return 1

    # No direct ZP-$10 initialization/mutation forms besides the two STA sites.
    forbidden_ops = [
        0x86, 0x84,  # STX/STY zp
        0xE6, 0xC6,  # INC/DEC zp
        0x06, 0x26, 0x46, 0x66,  # shifts/rotates zp
    ]
    for op in forbidden_ops:
        if bytes((op, 0x10)) in window:
            print(f"ERROR: unexpected direct ZP $10 mutation opcode ${op:02X}", file=sys.stderr)
            return 1

    print("ROM identity: OK")
    print("PRG26:$8000-$81FF (512 bytes): OK")
    print("object boundary $8031-$8037 does not initialize $10")
    print("compressed reads $10 at $8064/$8166")
    print("full records write final attribute to $10 at $80BF/$811B")
    print("renderer cache contract: $10 persists across object calls")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
