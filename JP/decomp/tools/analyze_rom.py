#!/usr/bin/env python3
"""Verify the Akumajou Densetsu target and print its physical PRG bank map."""

from __future__ import annotations

import hashlib
import sys
import zlib
from pathlib import Path

EXPECTED_SHA256 = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
EXPECTED_COMBINED_CRC32 = "E349AF38"


def digest(data: bytes, name: str) -> str:
    return hashlib.new(name, data).hexdigest()


def crc32(data: bytes) -> str:
    return f"{zlib.crc32(data) & 0xFFFFFFFF:08X}"


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {Path(sys.argv[0]).name} <Akumajou Densetsu (Japan).nes>")
        return 2

    path = Path(sys.argv[1])
    rom = path.read_bytes()
    if len(rom) < 16 or rom[:4] != b"NES\x1a":
        raise SystemExit("not an iNES ROM")

    sha256 = digest(rom, "sha256")
    prg_size = rom[4] * 0x4000
    chr_size = rom[5] * 0x2000
    flags6, flags7 = rom[6], rom[7]
    mapper = (flags6 >> 4) | (flags7 & 0xF0)

    trainer_size = 512 if flags6 & 0x04 else 0
    prg_start = 16 + trainer_size
    prg = rom[prg_start : prg_start + prg_size]
    chr_ = rom[prg_start + prg_size : prg_start + prg_size + chr_size]

    print(f"file: {path}")
    print(f"size: {len(rom)} (0x{len(rom):X})")
    print(f"sha256: {sha256}")
    print(f"header: {rom[:16].hex()}")
    print(f"mapper: {mapper}")
    print(f"PRG: {len(prg)} bytes crc32={crc32(prg)} sha1={digest(prg, 'sha1')}")
    print(f"CHR: {len(chr_)} bytes crc32={crc32(chr_)} sha1={digest(chr_, 'sha1')}")
    print(f"PRG+CHR: crc32={crc32(prg + chr_)} sha1={digest(prg + chr_, 'sha1')}")

    if sha256 != EXPECTED_SHA256:
        print("ERROR: full-file SHA-256 does not match the documented target", file=sys.stderr)
        return 1
    if crc32(prg + chr_) != EXPECTED_COMBINED_CRC32:
        print("ERROR: PRG+CHR CRC32 does not match the documented target", file=sys.stderr)
        return 1
    if mapper != 24 or len(prg) != 0x40000 or len(chr_) != 0x20000:
        print("ERROR: mapper or ROM sizes do not match the target", file=sys.stderr)
        return 1

    print("\nphysical 8 KiB PRG banks:")
    for bank_no in range(len(prg) // 0x2000):
        bank = prg[bank_no * 0x2000 : (bank_no + 1) * 0x2000]
        print(
            f"PRG{bank_no:02d} off={bank_no * 0x2000:05X} "
            f"crc32={crc32(bank)} sha1={digest(bank, 'sha1')[:12]}"
        )

    fixed = prg[-0x2000:]
    print("\nvectors:")
    for name, offset in (("NMI", 0x1FFA), ("RESET", 0x1FFC), ("IRQ", 0x1FFE)):
        vector = fixed[offset] | (fixed[offset + 1] << 8)
        print(f"{name:5s} ${vector:04X}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
