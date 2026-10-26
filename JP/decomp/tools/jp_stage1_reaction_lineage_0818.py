#!/usr/bin/env python3
"""JP0818 original source reaction and horizontal actor ancestry audit.

Uses the owner's private original Japanese ROM. Never exports original
ROM bytes, sprite art, live RAM or original-game savestates.
"""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path

ROM_SHA = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
BANK0A_SHA = "1460df577d44e114c64fdf34a8837629765f3f6a93d45796fdf81e5ffacb5ed8"
BANK0B_SHA = "17b216088d12ac7b6a4a68bbea3434dbdba317865bd6cf4d11646a3d4efaf64a"
WINDOWS = {
    "B249_direction": (11, 0xB249, 0xB258, "e2c4832d62f3eb716272064da6cd6073922aaffe585137d034059b94dc6d8fe3"),
    "B258_type_returns": (11, 0xB258, 0xB27A, "74a13a1e6f65fbd9bc8df370a7af57bd815933b9604bf1e5d973cd087179405a"),
    "B27A_early_contact": (11, 0xB27A, 0xB2A0, "fa4e6c6889b6bc94a7776a0a5e2bdb0547babb3e221299d166c2a03d204961e1"),
    "B1F5_return_operand": (11, 0xB1F5, 0xB1F9, "edae93011debbff5c3171749760292851faa42d47315fd95bca03fb56bf71da1"),
    "8B2C_row32": (10, 0x8B2C, 0x8B73, "c68f0be607e8d22d89415ce59d526a36881c046270dbd09af7f6f3598a8231e3"),
    "8B50_parent_writer": (10, 0x8B50, 0x8B73, "2cfd850e104e77eb6b6de7b3dad0b4205e0c24bb2608cb799abb798cf2a968b1"),
    "8D5E_descriptor": (10, 0x8D5E, 0x8D90, "5307cc48cdffeb1bbee7529cce80d94112ac2da158f427baec682da8d5142fbb"),
}

def stop(type_id: int, flag: int, ready_a: int, ready_b: int) -> int:
    """Independent bounded original B258 branch structure."""
    if type_id in (0x16, 0x37) or 0x61 <= type_id < 0x7f:
        return 0xb1f7
    if flag or not ready_a or not ready_b:
        return 0xb29d
    return 0xb27c

def smoke() -> None:
    for t in range(256):
        for bits in range(8):
            pc = stop(t, bits & 1, bits & 2, bits & 4)
            assert pc in (0xb1f7, 0xb29d, 0xb27c)
            if 0x61 <= t <= 0x7e:
                assert pc == 0xb1f7
    assert stop(0x7f, 0, 1, 1) == 0xb27c
    assert stop(0x3d, 1, 1, 1) == 0xb29d
    print("PASS JP0818: 2048 bounded original B258 decisions; no DEC at RTS")

def audit(path: Path) -> None:
    raw = path.read_bytes()
    if (len(raw) != 393232 or raw[:4] != b"NES\x1a" or
            hashlib.sha256(raw).hexdigest() != ROM_SHA):
        raise ValueError("not the authenticated Japanese retail ROM")
    banks = {
        i: raw[16 + i * 16384:16 + (i + 1) * 16384]
        for i in (10, 11)
    }
    for index, digest in ((10, BANK0A_SHA), (11, BANK0B_SHA)):
        if hashlib.sha256(banks[index]).hexdigest() != digest:
            raise ValueError(f"original physical bank {index:02X} changed")
    for name, (bank, begin, end, digest) in WINDOWS.items():
        source = banks[bank][begin - 0x8000:end - 0x8000]
        if len(source) != end - begin or hashlib.sha256(source).hexdigest() != digest:
            raise ValueError(f"original {name} opcode window changed")

    def span(bank: int, start: int, end: int) -> bytes:
        return banks[bank][start - 0x8000:end - 0x8000]

    if span(11, 0xB249, 0xB258) != bytes.fromhex(
        "86 8E A0 00 BD 38 04 CD 38 04 B0 01 C8 84 8D"):
        raise ValueError("original B249 X direction and scratch writes changed")
    if span(11, 0xB258, 0xB26B) != bytes.fromhex(
        "BD 4E 05 C9 16 F0 98 C9 37 F0 94 C9 61 90 04 C9 7F 90 8C"):
        raise ValueError("original B258 branch bytes changed")
    if span(11, 0xB1F4, 0xB1F8) != bytes.fromhex("DE 8D 06 60"):
        raise ValueError("the real DEC $068D and following RTS changed")
    if span(11, 0xB26B, 0xB281) != bytes.fromhex(
        "BD 8D 06 29 01 D0 2B AD 30 06 F0 26 AD 13 04 F0 21 20 EC B3 B0 1C"):
        raise ValueError("original B26B/B3EC prerequisite changed")
    if span(10, 0x8B50, 0x8B5F) != bytes.fromhex(
        "BD 70 04 09 04 9D 70 04 A5 69 9D 45 06 8A 48 A6"):
        raise ValueError("original B8B50 child $0645 parent installation changed")
    if banks[10][0x91C6 - 0x8000] != 0x13 or banks[10][0x921E - 0x8000] != 0x3D:
        raise ValueError("row32 script/type ($13/$3D) lookup differs")
    print("PASS JP0818 original Japanese ROM, raw0A/raw0B hashes, seven source windows")
    print("PASS B249 scratch, B258->B1F7 RTS, B3EC guard, B8B50 parent and row32 type")
    print("BOUNDARY: no natural Mesen frame witness, no offscreen actor interaction")

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rom", type=Path)
    p.add_argument("--smoke", action="store_true")
    a = p.parse_args()
    if a.smoke:
        smoke()
    if a.rom:
        audit(a.rom)
    if not a.rom and not a.smoke:
        p.error("supply --smoke and/or --rom")
