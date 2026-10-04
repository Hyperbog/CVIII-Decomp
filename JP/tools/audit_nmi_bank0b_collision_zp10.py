#!/usr/bin/env python3
from __future__ import annotations
import hashlib, sys
from pathlib import Path

ROM_SHA = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"

SNIPPETS = {
    "fixed_scheduler_FDEA_FE7D": ("fixed", 0xFDEA, 0xFE7E, "d6562ab4903c967e7b15ece681f25c96bc144f7479f356f06014bdccb9787b46"),
    "collision_sweep_B1F8_B31F": ("raw0b", 0xB1F8, 0xB320, "cfb178bf4eaeafb33f258534cac6954c68812430fe158e55efb6402fef81e3ec"),
    "probe_family_B339_B3EB": ("raw0b", 0xB339, 0xB3EC, "5639543d7a6f8b055eb264ff3267ec52279c9876c25aee698e455b99a2750197"),
    "weapon_probe_B3EC_B446": ("raw0b", 0xB3EC, 0xB447, "7a0680fed61415ce7a85ad2d641764451d8c9c988b38dbc0201ff47f63871990"),
    "peer_probe_B447_B47A": ("raw0b", 0xB447, 0xB47B, "1a56eba8c0ea0a5f3000e99f672c73af872cb4e91fb90d2c3b99343a915922a4"),
    "vertical_probe_B634_B672": ("raw0b", 0xB634, 0xB673, "7fb2a283cdf0c3a7a372286b91a4e9d4d2a7395d9641d5c8a8295e791bd1930c"),
    "distance_tail_B707_B781": ("raw0b", 0xB707, 0xB782, "b3e29bd1654b5269a6550cadefd94b5903b233b83aac8592306ea9096b58cc8c"),
    "two_byte_probe_table_B394_B395": ("raw0b", 0xB394, 0xB396, "9f1afa4dc124cba73134e82ff50f17c8f7164257c79fed9a13f5943a6acb8e3d"),
}

WRITERS = {
    0xB3B6: bytes.fromhex("85 10"),
    0xB3D2: bytes.fromhex("85 10"),
    0xB40E: bytes.fromhex("85 10"),
    0xB460: bytes.fromhex("85 10"),
    0xB65F: bytes.fromhex("85 10"),
    0xB740: bytes.fromhex("85 10"),
    0xB76C: bytes.fromhex("85 10"),
}

def main(path: str) -> None:
    rom = Path(path).read_bytes()
    got = hashlib.sha256(rom).hexdigest()
    assert got == ROM_SHA, (got, ROM_SHA)
    prg = rom[16:16+0x40000]
    assert len(prg) == 0x40000
    raw0b = prg[0x0B*0x4000:0x0C*0x4000]
    fixed = prg[31*0x2000:32*0x2000]

    def rr(a: int, n: int) -> bytes:
        assert 0x8000 <= a and a+n <= 0xC000
        return raw0b[a-0x8000:a-0x8000+n]
    def fr(a: int, n: int) -> bytes:
        assert 0xE000 <= a and a+n <= 0x10000
        return fixed[a-0xE000:a-0xE000+n]

    for name,(kind,s,e,expected) in SNIPPETS.items():
        data = fr(s,e-s) if kind == "fixed" else rr(s,e-s)
        digest = hashlib.sha256(data).hexdigest()
        assert digest == expected, (name, digest, expected)

    # Fixed scheduler: slots 1..18 and raw-$0B collision sweep first.
    assert fr(0xFDEA,2) == bytes.fromhex("A2 01")
    assert fr(0xFDF5,3) == bytes.fromhex("20 D0 E2")
    assert fr(0xFDF8,3) == bytes.fromhex("20 E3 80")
    assert fr(0xFDFB,3) == bytes.fromhex("20 F8 B1")
    assert fr(0xFE6E,8) == bytes.fromhex("E8 E0 13 B0 03 4C EC FD")
    assert fr(0xFE76,8) == bytes.fromhex("A9 0A 20 D0 E2 20 EA 84")

    # B1F8 writer-family ordering.
    assert rr(0xB182,3) == bytes.fromhex("20 34 B6")
    assert rr(0xB1D8,3) == bytes.fromhex("20 4B B6")
    assert rr(0xB1E9,3) == bytes.fromhex("20 39 B3")
    assert rr(0xB232,3) == bytes.fromhex("20 39 B3")
    assert rr(0xB27C,3) == bytes.fromhex("20 EC B3")
    assert rr(0xB29D,4) == bytes.fromhex("A9 14 85 9B")
    assert rr(0xB2B0,3) == bytes.fromhex("20 47 B4")
    assert rr(0xB317,8) == bytes.fromhex("E6 9B A5 9B C9 17 90 82")

    for a, op in WRITERS.items():
        assert rr(a, len(op)) == op, hex(a)

    # Exact JP writer formulas.
    assert rr(0xB3B0,8) == bytes.fromhex("40 BB 18 7D 38 04 85 10")
    assert rr(0xB3CC,8) == bytes.fromhex("50 BB 18 7D 1C 04 85 10")
    assert rr(0xB404,12) == bytes.fromhex("A8 04 A8 18 B9 1F BB 6D 38 04 85 10")
    assert rr(0xB456,12) == bytes.fromhex("B9 6B BB 85 01 A6 9B BD 38 04 85 10")
    assert rr(0xB659,8) == bytes.fromhex("73 B6 18 6D 1C 04 85 10")
    assert rr(0xB73A,8) == bytes.fromhex("AD 38 04 18 65 0C 85 10")
    assert rr(0xB766,8) == bytes.fromhex("60 A5 10 18 65 0C 85 10")

    assert rr(0xB460,8) == bytes.fromhex("85 10 BD 1C 04 85 11 A6")
    assert rr(0xB740,10) == bytes.fromhex("85 10 AD 1C 04 18 65 0D 85 11")
    assert rr(0xB76C,9) == bytes.fromhex("85 10 A5 11 18 65 0D 85 11")

    # Shared absolute-difference primitives.
    assert rr(0xB707,13) == bytes.fromhex("38 A5 11 E5 10 B0 04 49 FF 69 01 60 38")
    assert rr(0xB713,10) == bytes.fromhex("38 A5 10 ED 38 04 B0 F7 90 F1")
    assert rr(0xB71D,10) == bytes.fromhex("38 A5 10 ED 1C 04 B0 ED 90 E7")

    # Previously unclaimed two-byte dependency; local selector is Y=0/1.
    assert rr(0xB394,2) == bytes.fromhex("00 05")
    assert rr(0xB3D4,11) == bytes.fromhex("A0 00 A5 7F C9 04 90 01 C8 18 B9")
    assert rr(0xB3DF,3) == bytes.fromhex("94 B3 6D")

    print("ROM identity: OK", ROM_SHA)
    print("0502 collision snippets: OK", len(SNIPPETS))
    print("outer scheduler slots: X=$01..$12; raw-$0B $B1F8 before later per-slot calls")
    print("peer loop order: $9B=$14,$15,$16")
    print("verified direct ZP $10 stores:", " ".join(f"${a:04X}" for a in WRITERS))
    print("two-byte dependency $B394-$B395: 00 05; locally indexed only by Y=0/1")
    print("new semantic bytes attributable to 0502 table dependency: 2")
    print("NOTE: symbolic writer ordering/formulas proven; runtime path liveness remains object/state-dependent")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: audit_nmi_bank0b_collision_zp10.py JP.nes")
    main(sys.argv[1])
