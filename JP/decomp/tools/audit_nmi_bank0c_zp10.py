#!/usr/bin/env python3
"""Checkpoint 04F5: bound PRG24 $89E2 ZP $10 preservation and remaining E7 parameter dependency."""
from __future__ import annotations
import hashlib, sys
from collections import deque
from pathlib import Path

EXPECTED_SHA256 = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
SPAN_START = 0x8000
SPAN_END = 0x9200
EXPECTED_SPAN_SHA256 = "2bd1badec12d9f68bf829c272105d85097966d6fb0419c206566eb54c7011734"
SIZE = bytes.fromhex("01020000000202000102010000030300020200000002020001030000000303000302000002020200010201000303030002020000000202000103000000030300010200000002020001020100030303000202000000020200010300000003030001020000000202000102010003030300020200000002020001030000000303000002000002020200010001000303030002020000020202000103010000030000020202000202020001020100030303000202000002020200010301000303030002020000020202000102010003030300020200000002020001030000000303000202000002020200010201000303030002020000000202000103000000030300")
BRANCH = {0x10,0x30,0x50,0x70,0x90,0xB0,0xD0,0xF0}
TERM = {0x00,0x40,0x60}
ZP_DIRECT = {0x84,0x85,0x86,0x06,0x26,0x46,0x66,0xC6,0xE6}
ZP_INDEXED = {0x94,0x95,0x96,0x16,0x36,0x56,0x76,0xD6,0xF6}
INDIRECT_STORE = {0x81,0x91}
ABS_DIRECT = {0x8C,0x8D,0x8E,0x0E,0x2E,0x4E,0x6E,0xCE,0xEE}
ABS_INDEXED = {0x99,0x9D,0x1E,0x3E,0x5E,0x7E,0xDE,0xFE}

# Finite indirect-dispatch targets proven from local masks/compares.
# $842D is the one exception: its E7 parameter uses a 10-entry table.
# Only the format-valid $0-$9 high-nibble target ($8444) is seeded here;
# proving that stream-parameter producer domain is deliberately deferred.
DISPATCH_TARGETS = {
    0x833D,0x837E,0x83B7,0x85B3,
    0x83F8,0x840F,0x8456,0x845A,0x848C,0x849F,0x84ED,0x851D,0x852A,
    0x8444,
    0x86A9,0x86B4,0x86BF,0x8644,0x8668,0x869E,
    0x8B2C,0x8C16,0x8C2A,0x8C83,
    0x8E20,0x8E2A,0x8E34,0x8E3D,0x8E45,0x8E4B,
}
EXPECTED_EXTERNAL_CALLS = {0xE1B8,0xE1C8,0xE1D6,0xE1F6,0xE249}
EXPECTED_EXTERNAL_JUMPS = {0xE190,0xE195,0xE1AF,0xE1E4,0xE1EE}
EXPECTED_INDIRECT_JUMPS = {0x802E,0x83E1,0x842D,0x8641,0x8B10,0x8E1D}

def main(path: str) -> None:
    rom = Path(path).read_bytes()
    assert hashlib.sha256(rom).hexdigest() == EXPECTED_SHA256
    prg = rom[16:16+0x40000]
    bank = prg[24*0x2000:25*0x2000]
    def read(addr: int) -> int:
        assert 0x8000 <= addr < 0xA000
        return bank[addr-0x8000]

    span = bytes(read(a) for a in range(SPAN_START, SPAN_END))
    assert len(span) == 4608
    assert hashlib.sha256(span).hexdigest() == EXPECTED_SPAN_SHA256

    assert bytes(read(a) for a in range(0x870B,0x8713)) == bytes.fromhex("3d837e83b783b385")
    assert bytes(read(a) for a in range(0x83E4,0x83F8)) == bytes.fromhex("f8830f8456845a848c849f84ed841d852a851d85")
    assert bytes(read(a) for a in range(0x8430,0x8444)) == bytes.fromhex("4484"*10)
    assert bytes(read(a) for a in range(0x86F9,0x870B)) == bytes.fromhex("a986b486bf8644864486688668869e864486")
    assert bytes(read(a) for a in range(0x8B14,0x8B1C)) == bytes.fromhex("2c8b168c2a8c838c")
    assert bytes(read(a) for a in range(0x8DD6,0x8DEA)) == bytes.fromhex("208e2a8e348e3d8e458e1d851d851d851d854b8e")

    assert bytes(read(a) for a in range(0x8DEA,0x8E11)) == bytes.fromhex(
        "b1e0c9e6b0034c558ec9f0900d290fc90b90034cb385b1e0d051e008f04d"
        "b1e0290f38e9060aaa"
    )

    pending = deque([0x89E2, *sorted(DISPATCH_TARGETS)])
    visited: set[int] = set()
    ext_calls: set[int] = set()
    ext_jumps: set[int] = set()
    indirect_jumps: set[int] = set()
    risks: list[tuple[int,int,int|None]] = []

    while pending:
        pc = pending.popleft()
        if not (SPAN_START <= pc < SPAN_END) or pc in visited:
            continue
        while SPAN_START <= pc < SPAN_END and pc not in visited:
            visited.add(pc)
            op = read(pc)
            size = SIZE[op]
            if size == 0:
                break
            o8 = read(pc+1) if size >= 2 else None
            o16 = (o8 | (read(pc+2)<<8)) if size == 3 else None

            if op in ZP_DIRECT and o8 == 0x10:
                risks.append((pc,op,o8))
            if op in ZP_INDEXED or op in INDIRECT_STORE:
                risks.append((pc,op,o8))
            if op in ABS_DIRECT and o16 == 0x0010:
                risks.append((pc,op,o16))
            if op in ABS_INDEXED and any(((o16+i)&0xFFFF)==0x0010 for i in range(256)):
                risks.append((pc,op,o16))

            nxt = pc + size
            if op == 0x20:
                if SPAN_START <= o16 < SPAN_END:
                    pending.append(o16)
                else:
                    ext_calls.add(o16)
                pc = nxt
                continue
            if op == 0x4C:
                if SPAN_START <= o16 < SPAN_END:
                    pending.append(o16)
                else:
                    ext_jumps.add(o16)
                break
            if op == 0x6C:
                indirect_jumps.add(pc)
                break
            if op in TERM:
                break
            if op in BRANCH:
                delta = o8 if o8 < 0x80 else o8 - 0x100
                target = (pc + 2 + delta) & 0xFFFF
                if SPAN_START <= target < SPAN_END:
                    pending.append(target)
                else:
                    ext_jumps.add(target)
                pc = nxt
                continue
            pc = nxt

    assert len(visited) == 1488
    assert not risks, risks
    assert ext_calls == EXPECTED_EXTERNAL_CALLS, ext_calls
    assert ext_jumps == EXPECTED_EXTERNAL_JUMPS, ext_jumps
    assert indirect_jumps == EXPECTED_INDIRECT_JUMPS, indirect_jumps

    print("ROM identity: OK")
    print(f"PRG24 span: ${SPAN_START:04X}-${SPAN_END-1:04X} ({len(span)} bytes)")
    print(f"span SHA-256: {EXPECTED_SPAN_SHA256}")
    print(f"reachable accepted instruction starts: {len(visited)}")
    print("reachable write forms that can alias ZP $10: 0")
    print("external calls/jumps are only fixed helpers already covered by 04F3")
    print("unresolved producer-domain boundary: $842D E7 next-byte high nibble")
    print("04F5 result: banked helper is $10-clean on the closed graph; E7 parameter domain remains open")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {Path(sys.argv[0]).name} ROM.nes")
    main(sys.argv[1])
