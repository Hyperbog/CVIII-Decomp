#!/usr/bin/env python3
"""Verify PRG26/27 master frame tables and compressed sprite descriptors."""
from __future__ import annotations
import hashlib
import sys
from pathlib import Path

EXPECTED_SHA256 = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
MASTERS = [
    (0x819D, 0x82F5, 172),
    (0x8AB0, 0x8C2E, 191),
    (0x9545, 0x9621, 110),
    (0x9E6D, 0x9F6D, 128),
    (0xAAA6, 0xAC5C, 219),
]
EXPECTED_UNIQUE = 745
EXPECTED_FIRST_REUSE = {0x9FA9}
EXPECTED_MAX_COUNT = 27


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {Path(sys.argv[0]).name} <Akumajou Densetsu (Japan).nes>")
        return 2

    rom = Path(sys.argv[1]).read_bytes()
    if hashlib.sha256(rom).hexdigest() != EXPECTED_SHA256:
        print("ERROR: ROM SHA-256 mismatch", file=sys.stderr)
        return 1

    prg = rom[16 : 16 + 0x40000]
    bank13 = prg[26 * 0x2000 : 28 * 0x2000]
    pointers: list[int] = []

    for start, end, count in MASTERS:
        if (end - start) // 2 != count:
            raise AssertionError("internal master-table size mismatch")
        first_off = start - 0x8000
        first = bank13[first_off] | (bank13[first_off + 1] << 8)
        if first != end:
            print(
                f"ERROR: ${start:04X} first pointer is ${first:04X}, "
                f"expected boundary ${end:04X}",
                file=sys.stderr,
            )
            return 1
        for address in range(start, end, 2):
            off = address - 0x8000
            pointer = bank13[off] | (bank13[off + 1] << 8)
            if not 0x8000 <= pointer <= 0xBFFF:
                print(f"ERROR: non-window pointer ${pointer:04X} at ${address:04X}", file=sys.stderr)
                return 1
            pointers.append(pointer)

    unique = sorted(set(pointers))
    if len(unique) != EXPECTED_UNIQUE:
        print(f"ERROR: unique descriptor count {len(unique)} != {EXPECTED_UNIQUE}", file=sys.stderr)
        return 1

    first_reuse: set[int] = set()
    max_count = 0
    max_encoded = 0
    reuse_records = 0

    for pointer in unique:
        pos = pointer - 0x8000
        count = bank13[pos]
        max_count = max(max_count, count)
        cursor = 1
        for sprite_index in range(count):
            y_code = bank13[pos + cursor]
            cursor += 1
            _tile = bank13[pos + cursor]
            cursor += 1
            if y_code & 1:
                reuse_records += 1
                if sprite_index == 0:
                    first_reuse.add(pointer)
            else:
                _attribute = bank13[pos + cursor]
                cursor += 1
            _x = bank13[pos + cursor]
            cursor += 1
            if cursor > 0x100:
                print(f"ERROR: descriptor ${pointer:04X} exceeds 8-bit cursor window", file=sys.stderr)
                return 1
        max_encoded = max(max_encoded, cursor)

    if first_reuse != EXPECTED_FIRST_REUSE:
        print(f"ERROR: first-record reuse descriptors {sorted(first_reuse)}", file=sys.stderr)
        return 1
    if max_count != EXPECTED_MAX_COUNT:
        print(f"ERROR: max sprite count {max_count}", file=sys.stderr)
        return 1

    print("ROM identity: OK")
    for start, end, count in MASTERS:
        print(f"master ${start:04X}-${end - 1:04X}: {count} pointers; entry0 -> ${end:04X}")
    print(f"unique descriptors: {len(unique)}")
    print(f"max sprites/descriptor: {max_count}")
    print(f"max encoded descriptor length: {max_encoded} bytes")
    print(f"compressed attribute-reuse records: {reuse_records}")
    print("only descriptor whose first sprite reuses prior attribute: $9FA9")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
