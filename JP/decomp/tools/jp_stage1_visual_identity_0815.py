#!/usr/bin/env python3
"""Owner-local ROM witness for Stage1 original source/visual lookup.

Original ROM and CHR data never leave the owner's machine. This script
does NOT equate actor type $80 with a named candle or enemy.
"""
import argparse
import hashlib
from pathlib import Path

ROM_SHA = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
RAW0A_SHA = "1460df577d44e114c64fdf34a8837629765f3f6a93d45796fdf81e5ffacb5ed8"
PRG26_SHA = "042d91a4fe2be444465b4ebdac1ee419ed58f74976bc1e9edbb92995a7fb6959"


def word(bank: bytes, addr: int) -> int:
    if len(bank) != 16384 or not 0x8000 <= addr <= 0xBFFE:
        raise ValueError("CPU pointer outside mapped 16 KiB bank")
    i = addr - 0x8000
    return bank[i] | (bank[i + 1] << 8)


def original_descriptor(prg26: bytes, selector: int, frame: int) -> tuple[int, int]:
    if not 0 <= selector <= 255 or not 0 <= frame <= 255:
        raise ValueError("selector/frame must be original byte offsets")
    ptr = word(prg26, 0x817F + selector)
    descriptor = word(prg26, ptr + frame)
    if not 0x8000 <= descriptor <= 0xBFFF:
        raise ValueError("invalid PRG26 graphics descriptor")
    count = prg26[descriptor - 0x8000]
    if count > 27:
        raise ValueError("oversized compressed sprite")
    return descriptor, count


def audit(rom: bytes) -> None:
    if len(rom) != 393232 or rom[:4] != b"NES\x1a" or (
        hashlib.sha256(rom).hexdigest() != ROM_SHA
    ):
        raise ValueError("not the authenticated owner-supplied Japanese cartridge")
    bank0a = rom[16 + 10 * 16384:16 + 11 * 16384]
    bank26 = rom[16 + 26 * 8192:16 + 28 * 8192]
    if hashlib.sha256(bank0a).hexdigest() != RAW0A_SHA:
        raise ValueError("raw0A physical bank hash changed")
    if hashlib.sha256(bank26).hexdigest() != PRG26_SHA:
        raise ValueError("original PRG26 visual-source bank hash changed")
    root = 0xAB1F - 0x8000
    body = bank0a[root:root + 64]
    if len(body) != 64 or body[-1] != 0xFF:
        raise ValueError("chapel source terminator or extent differs")
    rows = [body[i * 7:(i + 1) * 7] for i in range(9)]
    if sorted(row[2] for row in rows) != [0x0D] * 3 + [0x80] * 6:
        raise ValueError("authenticated nine-row event/direct source partition changed")
    # The natural Mesen slot-15/type-$80 observation authenticates this
    # *type family*, not a specific $AB1F record or animation frame.
    descriptor, pieces = original_descriptor(bank26, 0x0E, 0x00)
    if (descriptor, pieces) != (0xAC5C, 4):
        raise ValueError("original PRG26 pointer tree no longer agrees")
    print("PASS: ROM SHA + raw0A SHA + PRG26 SHA")
    print("PASS: 9 resident seven-byte source records; $0D=3, $80=6")
    print("PASS: selector $0E/frame-offset $00 -> PRG26:$AC5C, four pieces")
    print("LIMIT: visual object identity and offscreen collisions unverified")


def smoke() -> None:
    bank = bytearray(16384)
    bank[0x818D - 0x8000:0x818F - 0x8000] = b"\x00\x90"
    bank[0x9001 - 0x8000:0x9003 - 0x8000] = b"\x00\x91"
    bank[0x9100 - 0x8000] = 4
    assert original_descriptor(bytes(bank), 0x0E, 1) == (0x9100, 4)
    bank[0x9100 - 0x8000] = 28
    try:
        original_descriptor(bytes(bank), 0x0E, 1)
    except ValueError:
        print("PASS: artificial visual pointer and fail-closed count checks")
    else:
        raise AssertionError("invalid artificial 28-piece descriptor accepted")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rom", type=Path)
    p.add_argument("--smoke", action="store_true")
    a = p.parse_args()
    if a.smoke:
        smoke()
    if a.rom:
        audit(a.rom.read_bytes())
    if not a.smoke and not a.rom:
        p.error("provide --smoke or a private original ROM")
