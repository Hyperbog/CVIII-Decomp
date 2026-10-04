#!/usr/bin/env python3
import hashlib
import sys
from pathlib import Path

EXPECTED_SHA256 = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"


def main(path: str) -> None:
    rom = Path(path).read_bytes()
    assert hashlib.sha256(rom).hexdigest() == EXPECTED_SHA256

    prg = rom[16:16 + 0x40000]
    prg26 = prg[26 * 0x2000:27 * 0x2000]
    prg28 = prg[28 * 0x2000:29 * 0x2000]

    def p26(cpu: int, count: int) -> bytes:
        return prg26[cpu - 0x8000:cpu - 0x8000 + count]

    def p28(cpu: int, count: int) -> bytes:
        return prg28[cpu - 0x8000:cpu - 0x8000 + count]

    # PRG26:$8001 outer loop: slot 0 upward, stopping at $1C.
    assert p26(0x8001, 0x37) == bytes.fromhex(
        "a9 00 85 05 a9 40 85 07 a5 22 18 69 44 85 22 85 04 "
        "a6 05 e0 1c b0 20 bd 00 04 f0 17 bd 70 04 30 12 bd 54 04 "
        "85 00 bd 1c 04 85 01 bd 38 04 85 02 20 70 80 e6 05 d0 da"
    )

    # Compressed records read $10; full records update it.
    assert p26(0x8064, 2) == bytes.fromhex("a5 10")
    assert p26(0x80BF, 2) == bytes.fromhex("85 10")
    assert p26(0x811B, 2) == bytes.fromhex("85 10")
    assert p26(0x8166, 2) == bytes.fromhex("a5 10")

    # $9FA9: four sprites, first three compressed, fourth explicit attr=$03.
    assert p26(0x9FA9, 14) == bytes.fromhex(
        "04 df 8a f0 e1 8c f8 e5 8e 00 04 e4 90 03"
    )

    # JP slot-0 mirror field has immediate stores of both values.
    assert p28(0x823E, 5) == bytes.fromhex("a9 01 8d a8 04")
    assert p28(0x8249, 5) == bytes.fromhex("a9 00 8d a8 04")

    print(
        "04F1 audit OK: ascending renderer order, persistent $10, "
        "$9FA9 starts compressed, slot-0 mirror state can be 0 or 1"
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} ROM.nes")
    main(sys.argv[1])
