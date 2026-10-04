#!/usr/bin/env python3
"""Verify PRG06 selector-$10 animation ID $09 reaches frame $14 via fixed $EF93."""
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
    bank3 = prg[6 * 0x2000:8 * 0x2000]
    fixed = prg[31 * 0x2000:32 * 0x2000]

    def b3(addr: int, n: int) -> bytes:
        return bank3[addr - 0x8000:addr - 0x8000 + n]

    def fx(addr: int, n: int) -> bytes:
        return fixed[addr - 0xE000:addr - 0xE000 + n]

    expected_prg06 = bytes.fromhex(
        "a008bd1c04c9a8b008a009c9a0b002a00aa9104c7fef"
    )
    if b3(0x823E, len(expected_prg06)) != expected_prg06:
        print("ERROR: PRG06 $823E selector/animation branch mismatch", file=sys.stderr)
        return 1

    expected_init = bytes.fromhex(
        "9d8c049884aa05a9009d9305a9019d7c0560"
    )
    if fx(0xEF7F, len(expected_init)) != expected_init:
        print("ERROR: fixed $EF7F animation initializer mismatch", file=sys.stderr)
        return 1

    # selector $10 pointer from fixed table $EFD2
    selector = 0x10
    p = fx(0xEFD2 + selector, 2)
    table = p[0] | (p[1] << 8)
    if table != 0xF272:
        print(f"ERROR: selector $10 table is ${table:04X}, expected $F272", file=sys.stderr)
        return 1

    # selector-$10 block ends at next selector table pointer $F37D.
    if (0xF37D - table) != 267 or (0xF37D - table) % 3:
        print("ERROR: selector-$10 animation table extent mismatch", file=sys.stderr)
        return 1

    anim_id = 0x09
    rec_addr = table + 3 * anim_id
    rec = fx(rec_addr, 3)
    if rec != bytes([0x14, 0x08, 0x02]):
        print(f"ERROR: animation $09 record at ${rec_addr:04X} is {rec.hex()}", file=sys.stderr)
        return 1

    # $EF93 decrements timer and $EFB5 performs STA $0400,X.
    if fx(0xEF93, 6) != bytes.fromhex("de7c05f00160"):
        print("ERROR: $EF93 timer gate mismatch", file=sys.stderr)
        return 1
    if fx(0xEFAF, 9) != bytes.fromhex("b108187d93059d0004"):
        print("ERROR: $EFAF/$EFB5 frame write sequence mismatch", file=sys.stderr)
        return 1

    # Fixed active-object loop post-behavior animation tick.
    if fx(0xFE54, 15) != bytes.fromhex("bd4e05f015bd70042920d0032093ef"):
        print("ERROR: fixed $FE54-$FE62 animation scheduling sequence mismatch", file=sys.stderr)
        return 1

    # PRG06 path explicitly writes $40 to flags before the branch family;
    # bit $20 is therefore clear on this local path.
    if b3(0x81E0, 5) != bytes.fromhex("a9409d7004"):
        print("ERROR: PRG06 $81E0 flag write mismatch", file=sys.stderr)
        return 1

    print("ROM identity: OK")
    print("PRG06 $823E: base-Y selects animation IDs $08/$09/$0A under selector $10")
    print("selector $10 animation table: $F272-$F37C (89 records)")
    print("animation ID $09: $F28D = 14 08 02 -> frame $14")
    print("fixed object-loop animation tick: $FE60 JSR $EF93")
    print("transitive selector $10 -> frame $14 mechanism: VERIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
