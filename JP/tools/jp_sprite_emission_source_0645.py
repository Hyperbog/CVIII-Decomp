#!/usr/bin/env python3
"""JP0645: authenticated original JP PRG26 OAM emission and permutation gate.

Only source-byte motifs and a mathematical bijection, not live CPU execution.
No original ROM bytes are saved to disk or committed as fixtures.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

ROM_SHA = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
PRG26_BANK = 26
BANK_SIZE = 8192
PHASE = bytes.fromhex("a5 22 18 69 44 85 22 85 04")
STRIDE = bytes.fromhex("8a 18 69 c4 aa 88 d0 f3")


def check_bank(bank: bytes) -> None:
    if len(bank) != BANK_SIZE:
        raise ValueError("PRG26 bank must be exactly 8192 bytes")
    if bank[0x09:0x09 + len(PHASE)] != PHASE:
        raise ValueError("original $22 += $44 PRG26 opcode window changed")
    if bank[0x41:0x41 + len(STRIDE)] != STRIDE:
        raise ValueError("original X += $C4 PRG26 opcode window changed")


def check_permutation() -> int:
    cases = 0
    for phase in range(0, 256, 4):
        slots = set()
        for emitted in range(64):
            slot = ((phase >> 2) + emitted * 49) & 63
            inverse = ((slot - (phase >> 2)) * 17) & 63
            if inverse != emitted or slot in slots:
                raise ValueError("logical OAM emission is not bijective")
            slots.add(slot)
            cases += 1
        if len(slots) != 64:
            raise ValueError("rotating OAM emission omits a slot")
    if cases != 4096:
        raise AssertionError("unexpected OAM permutation test bound")
    return cases


def check_retail(path: Path) -> None:
    data = path.read_bytes()
    if len(data) != 393232 or hashlib.sha256(data).hexdigest() != ROM_SHA:
        raise ValueError("owner cartridge is not authenticated Japanese retail ROM")
    if data[:4] != b"NES\x1a" or data[4:6] != bytes([16, 16]) or \
       ((data[6] >> 4) | (data[7] & 0xf0)) != 24:
        raise ValueError("iNES header/mapper is not 16x16 mapper24")
    at = 16 + PRG26_BANK * BANK_SIZE
    check_bank(data[at:at + BANK_SIZE])


def smoke() -> None:
    bank = bytearray(BANK_SIZE)
    bank[0x09:0x09 + len(PHASE)] = PHASE
    bank[0x41:0x41 + len(STRIDE)] = STRIDE
    check_bank(bytes(bank))
    for offset in (0x09, 0x41):
        damaged = bytearray(bank)
        damaged[offset] ^= 1
        try:
            check_bank(bytes(damaged))
        except ValueError:
            pass
        else:
            raise AssertionError("altered PRG26 motif accepted")
    for invalid in (b"", bytes(bank[:8100]), bytes(bank + b"\x00")):
        try:
            check_bank(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError("wrong PRG26 length accepted")
    print("PASS JP0645 ROM-free PRG26 motif-negative fixtures and",
          check_permutation(), "inverse OAM emission cases")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", type=Path)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    if not args.smoke and args.rom is None:
        parser.error("provide --rom with private retail JP cartridge or --smoke")
    if args.smoke:
        smoke()
    if args.rom:
        check_retail(args.rom)
        print("PASS JP0645 authentic Japanese PRG26 bytecode",
              "$22 += $44 at bank 0x09, X += $C4 at 0x41;",
              check_permutation(), "emission-permutation cases")


if __name__ == "__main__":
    main()
