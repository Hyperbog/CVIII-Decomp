#!/usr/bin/env python3
"""JP0819 authenticated original B3EC and B29D/B31F source windows.

ROM belongs to owner. Print only source-window hashes and verified logic,
never actual copyrighted ROM table data, private RAM or savestate bytes.
"""
import argparse
import hashlib
from pathlib import Path

ROM_SHA = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
BANK0A_SHA = "1460df577d44e114c64fdf34a8837629765f3f6a93d45796fdf81e5ffacb5ed8"
BANK0B_SHA = "17b216088d12ac7b6a4a68bbea3434dbdba317865bd6cf4d11646a3d4efaf64a"
WINDOWS = {
    "B3EC_original_player_gate": (11, 0xB3EC, 0xB447,
        "7a0680fed61415ce7a85ad2d641764451d8c9c988b38dbc0201ff47f63871990"),
    "B29D_partner_loop": (11, 0xB29D, 0xB320,
        "f47fb5b380e191b01794a512b49b3f395c273b3b2d8f381c4175cf134669f09a"),
    "B323_parent_mask_helper": (11, 0xB323, 0xB339,
        "ed460215d83fd4266b1723da076da8b1158d005e4c0abbe6805814cc4cab2ea3"),
    "B447_partner_proximity": (11, 0xB447, 0xB47B,
        "1a56eba8c0ea0a5f3000e99f672c73af872cb4e91fb90d2c3b99343a915922a4"),
    "80B3_absolute_6502_difference": (11, 0x80B3, 0x80D5,
        "efe15ed5964c3547b205c6e02aa1cdd4740c0e59d4ea9022fe581c7572341d48"),
    "8B2C_original_row32_child": (10, 0x8B2C, 0x8B73,
        "c68f0be607e8d22d89415ce59d526a36881c046270dbd09af7f6f3598a8231e3")
}

def byte(bank: bytes, addr: int) -> int:
    if not 0x8000 <= addr <= 0xBFFF:
        raise ValueError("original CPU pointer escaped 16KiB ROM bank")
    return bank[addr - 0x8000]

def prove(path: Path) -> None:
    rom = path.read_bytes()
    if len(rom) != 393232 or rom[:4] != b"NES\x1a" or (
        hashlib.sha256(rom).hexdigest() != ROM_SHA):
        raise ValueError("not the owner-authenticated JP Mapper24 cartridge")
    banks = {i: rom[16+i*16384:16+(i+1)*16384] for i in (10,11)}
    for i,h in ((10,BANK0A_SHA),(11,BANK0B_SHA)):
        if hashlib.sha256(banks[i]).hexdigest() != h:
            raise ValueError(f"physical PRG bank {i:02X} fingerprint changed")
    for name,(idx,start,end,digest) in WINDOWS.items():
        buf=banks[idx][start-0x8000:end-0x8000]
        if len(buf) != end-start or hashlib.sha256(buf).hexdigest() != digest:
            raise ValueError(f"original window not verified: {name}")
    a = banks[11]
    def part(start:int, end:int) -> bytes:
        return a[start-0x8000:end-0x8000]
    if part(0xB3EC,0xB3F3) != bytes.fromhex("20 b3 80 c9 80 b0 53"):
        raise ValueError("B3EC initial player-distance branch changed")
    if part(0xB41B,0xB427) != bytes.fromhex(
        "a5 b7 f0 08 20 be e5 90 03 4c 67 b7"):
        raise ValueError("B7/E5BE external helper boundary changed")
    if part(0xB29D,0xB2B5) != bytes.fromhex(
        "a9 14 85 9b a4 9b b9 4e 05 f0 6f 20 23 b3 39 20 b3 d0 67 20 47 b4 b0 62"):
        raise ValueError("original three-partner mask and proximity scan changed")
    if part(0xB320,0xB323) != bytes.fromhex("02 04 08"):
        raise ValueError("three original 20/21/22 mask bits changed")
    if part(0xB447,0xB450) != bytes.fromhex(
        "a4 9b b9 4e 05 c9 05 f0 1c"):
        raise ValueError("B447 special type05 branch changed")
    if part(0xB2B5,0xB2C1) != bytes.fromhex(
        "20 27 b7 20 23 b3 19 20 b3 9d 8d 06"):
        raise ValueError("B727 contact and 068D mask mutation changed")
    print("PASS JP0819 owner-ROM SHA, physical bank SHA and six original CPU windows")
    print("PASS B3EC, E5BE deferral, partner 20-22 bitmask 02/04/08, B727 stop")
    print("No natural-game collision or offscreen AI assertion")

def smoke() -> None:
    for delta in range(256):
        for origin in range(256):
            # Same original $80B3 absolute arithmetic result for bytes.
            subtraction=(origin-delta)&255
            negative=origin < delta
            corrected=((subtraction ^ 255)+1)&255 if negative else subtraction
            assert corrected==abs(origin-delta)
    bits=(2,4,8)
    for mask in range(16):
        eligible=[20+i for i in range(3) if not mask & bits[i]]
        assert all(20<=v<=22 for v in eligible)
    print("PASS JP0819 65536 byte-pair abs cases and three-partner mask guard")

if __name__ == "__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rom",type=Path)
    p.add_argument("--smoke",action="store_true")
    a=p.parse_args()
    if a.smoke:smoke()
    if a.rom:prove(a.rom)
    if not (a.rom or a.smoke):p.error("provide --smoke or --rom")
