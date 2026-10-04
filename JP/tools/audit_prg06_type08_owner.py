#!/usr/bin/env python3
"""Verify the PRG06 primary-type $08 owner/scheduler path to descriptor $9FA9."""
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
    bank3 = prg[6 * 0x2000 : 8 * 0x2000]
    bank9 = prg[18 * 0x2000 : 20 * 0x2000]
    bank13 = prg[26 * 0x2000 : 28 * 0x2000]
    fixed = prg[31 * 0x2000 : 32 * 0x2000]

    def b3(addr: int, n: int) -> bytes:
        return bank3[addr - 0x8000 : addr - 0x8000 + n]

    def b9(addr: int, n: int) -> bytes:
        return bank9[addr - 0x8000 : addr - 0x8000 + n]

    def fx(addr: int, n: int) -> bytes:
        return fixed[addr - 0xE000 : addr - 0xE000 + n]

    # Fixed loop X range and low-type dispatch to bank $09/$8001.
    if fx(0xFDEA, 7) != bytes.fromhex("A201BD4E05F07D"):
        print("ERROR: fixed object-loop start mismatch", file=sys.stderr)
        return 1
    if fx(0xFE05, 15) != bytes.fromhex("C930B00DA90920D0E2200180A6694C"):
        print("ERROR: fixed low-type bank-$09 dispatch mismatch", file=sys.stderr)
        return 1
    if fx(0xFE6E, 8) != bytes.fromhex("E8E013B0034CECFD"):
        print("ERROR: fixed object-loop X bound mismatch", file=sys.stderr)
        return 1

    primary_type = 0x08
    bank_select = b9(0x8163 + primary_type, 1)[0]
    behavior_ptr = u16(bank9, 0x81E9 - 0x8000 + 2 * (primary_type - 1))
    if bank_select != 0x03 or behavior_ptr != 0x8021:
        print(
            f"ERROR: type $08 maps to bank ${bank_select:02X}, ptr ${behavior_ptr:04X}",
            file=sys.stderr,
        )
        return 1

    # Internal state-$01 route and animation selector branch.
    if b3(0x8143, 8) != bytes.fromhex("BC0606F0054CDD81"):
        print("ERROR: PRG06 $8143 state dispatch mismatch", file=sys.stderr)
        return 1
    if b3(0x81DD, 8) != bytes.fromhex("88D074A9409D7004"):
        print("ERROR: PRG06 state-$01 entry mismatch", file=sys.stderr)
        return 1
    if b3(0x823E, 21) != bytes.fromhex(
        "A008BD1C04C9A8B008A009C9A0B002A00AA9104C7F"
    ):
        print("ERROR: PRG06 $823E animation branch mismatch", file=sys.stderr)
        return 1

    # Same fixed-loop iteration: bit-$40 movement integration then bit-$20 animation gate.
    if fx(0xFE45, 32) != bytes.fromhex(
        "BD70042940F008A90B20D0E2200180BD4E05F015BD70042920D0032093EFA90B"
    ):
        print("ERROR: fixed post-behavior movement/animation scheduling mismatch", file=sys.stderr)
        return 1

    # Selector $10 -> master table $9E6D -> frame offset $14 -> descriptor $9FA9.
    selector_ptr = u16(bank13, 0x817F - 0x8000 + 0x10)
    if selector_ptr != 0x9E6D:
        print(f"ERROR: selector $10 -> ${selector_ptr:04X}, expected $9E6D", file=sys.stderr)
        return 1
    descriptor_ptr = u16(bank13, selector_ptr - 0x8000 + 0x14)
    if descriptor_ptr != 0x9FA9:
        print(f"ERROR: selector $10/frame $14 -> ${descriptor_ptr:04X}", file=sys.stderr)
        return 1

    print("ROM identity: OK")
    print("fixed object-loop slots: X=$01-$12")
    print("primary type $08 -> common bank $09 -> bank $03 / PRG06:$8021")
    print("internal state $01 -> PRG06:$81E0 path; base Y $A0-$A7 -> animation ID $09")
    print("same fixed-loop iteration reaches movement integration and $EF93 animation tick")
    print("selector $10/frame $14 -> PRG26 descriptor $9FA9")
    print("owner/scheduler chain: VERIFIED")
    print("normal-gameplay provenance of base Y $A0-$A7: still open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
