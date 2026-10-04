#!/usr/bin/env python3
"""Verify primary-type $08 root constructors establish $0645=0 in the JP ROM."""
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
    prg = rom[16:16+0x40000]
    def bank(n: int) -> bytes:
        return prg[n*0x2000:(n+1)*0x2000]
    b18, b20, b21, fixed = bank(18), bank(20), bank(21), bank(31)

    expected_ff24 = bytes.fromhex(
        "2015ffa9009d7b069d8d069d54049d7004"
        "a9009d65059dc4049ddb049dc1059dd8059def05"
        "9d06069d1d069d33069d450660"
    )
    off = 0xFF24 - 0xE000
    if fixed[off:off+len(expected_ff24)] != expected_ff24:
        print("ERROR: fixed $FF24 reset signature mismatch", file=sys.stderr)
        return 1

    expected_alloc = bytes.fromhex(
        "85118610200387d01320d186a9009d54048aa8a5119d4e05a6103860"
    )
    off = 0x86E3 - 0x8000
    if b18[off:off+len(expected_alloc)] != expected_alloc:
        print("ERROR: PRG18 $86E3 allocator signature mismatch", file=sys.stderr)
        return 1

    expected_reset = bytes.fromhex(
        "a9009d4e059d00049d8c04a9009dd8059def059d06069d1d069d33069d4506"
        "9d57069d69069d7b069d8d0660"
    )
    off = 0x8692 - 0x8000
    if b18[off:off+len(expected_reset)] != expected_reset:
        print("ERROR: PRG18 $8692 reset signature mismatch", file=sys.stderr)
        return 1

    expected_spawn = bytes.fromhex(
        "2024ffa000b1009d4e05c8b1009dd805c8b1001865099d3804"
        "a50a690029019d7004c8b1009d1c04bd4e0538e980a8b92983"
        "9def05a5739d450660"
    )
    off = 0x81AF - 0x8000
    if b20[off:off+len(expected_spawn)] != expected_spawn:
        print("ERROR: PRG20 $81AF spawner signature mismatch", file=sys.stderr)
        return 1

    def read16(addr: int) -> int:
        if 0x8000 <= addr < 0xA000:
            return b20[addr-0x8000]
        if 0xA000 <= addr < 0xC000:
            return b21[addr-0xA000]
        raise ValueError(addr)

    valid_records = 0
    type08_records = []
    low_types = set()
    for base in (0xA56B, 0xA66B):
        for y in range(0, 0x100, 2):
            lo = read16(base + y)
            hi = read16(base + y + 1)
            ptr = lo | (hi << 8)
            if 0x8000 <= ptr < 0xC000:
                valid_records += 1
                t = read16(ptr)
                if t < 0x80:
                    low_types.add(t)
                if t == 0x08:
                    type08_records.append((base, y, ptr))
    if type08_records:
        print(f"ERROR: high-type spawner table contains type $08: {type08_records}", file=sys.stderr)
        return 1
    if low_types != {0x00}:
        print(f"ERROR: unexpected low first-byte types in PRG20 spawner records: {sorted(low_types)}", file=sys.stderr)
        return 1

    if bytes.fromhex("a9089d4e05") in prg:
        print("ERROR: unexpected literal type-$08 constructor found", file=sys.stderr)
        return 1

    print("ROM identity: OK")
    print("fixed $FF24 clears $0606/$061D/$0633/$0645")
    print("PRG18 $86E3 low-slot allocator resets through $86D1/$8692 before storing requested type")
    print(f"PRG20 high-type spawner records checked: {valid_records}; type $08 records: 0")
    print("PRG-wide literal LDA #$08 / STA $054E,X constructors: 0")
    print("primary type $08 root constructor contract: $0645=$00")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
