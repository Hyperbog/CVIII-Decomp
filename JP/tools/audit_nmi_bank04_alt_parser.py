#!/usr/bin/env python3
"""Checkpoint 04F7: bound raw bank $04 alternate-parser code and ZP $10 risk."""
from __future__ import annotations

import hashlib
import sys
from collections import deque
from pathlib import Path

EXPECTED_SHA256 = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
SPAN_START = 0x8000
SPAN_END = 0x9200
EXPECTED_SPAN_SHA256 = "ee8b2de23022f715d3934907e7caaab91e824b4a9a31ccb75a69dae7d55c178b"
COMMON_CODE_END = 0x87AE
META_TABLE = 0x8F60
META_COUNT = 0x7D

SIZE = bytes.fromhex("01020000000202000102010000030300020200000002020001030000000303000302000002020200010201000303030002020000000202000103000000030300010200000002020001020100030303000202000000020200010300000003030001020000000202000102010003030300020200000002020001030000000303000002000002020200010001000303030002020000020202000103010000030000020202000202020001020100030303000202000002020200010301000303030002020000020202000102010003030300020200000002020001030000000303000202000002020200010201000303030002020000000202000103000000030300")
BRANCH = {0x10, 0x30, 0x50, 0x70, 0x90, 0xB0, 0xD0, 0xF0}
TERM = {0x00, 0x40, 0x60}
ZP_DIRECT = {0x84, 0x85, 0x86, 0x06, 0x26, 0x46, 0x66, 0xC6, 0xE6}
ZP_INDEXED = {0x94, 0x95, 0x96, 0x16, 0x36, 0x56, 0x76, 0xD6, 0xF6}
INDIRECT_STORE = {0x81, 0x91}
ABS_DIRECT = {0x8C, 0x8D, 0x8E, 0x0E, 0x2E, 0x4E, 0x6E, 0xCE, 0xEE}
ABS_INDEXED = {0x99, 0x9D, 0x1E, 0x3E, 0x5E, 0x7E, 0xDE, 0xFE}

# Locally bounded targets used by the alternate-parser core copied across raw banks.
DISPATCH_TARGETS = {
    0x833D, 0x837E, 0x83B7, 0x85B3,
    0x83F8, 0x840F, 0x8456, 0x845A, 0x848C, 0x849F, 0x84ED, 0x851D, 0x852A,
    0x8444,
    0x86A9, 0x86B4, 0x86BF, 0x8644, 0x8668, 0x869E,
}
EXPECTED_EXTERNAL_CALLS = {0xE1B8, 0xE1C8, 0xE1D6, 0xE1F6, 0xE249}
EXPECTED_EXTERNAL_JUMPS = {0xE190, 0xE195, 0xE1E4, 0xE1EE}
EXPECTED_INDIRECT_JUMPS = {0x802E, 0x83E1, 0x842D, 0x8641}
EXPECTED_WINDOW_SOUNDS = {0x5A, 0x5D, 0x65, 0x67}


def main(path: str) -> None:
    rom = Path(path).read_bytes()
    assert hashlib.sha256(rom).hexdigest() == EXPECTED_SHA256
    prg = rom[16:16 + 0x40000]
    raw04 = prg[8 * 0x2000:10 * 0x2000]
    raw0c = prg[24 * 0x2000:26 * 0x2000]

    span = raw04[SPAN_START - 0x8000:SPAN_END - 0x8000]
    assert len(span) == 4608
    assert hashlib.sha256(span).hexdigest() == EXPECTED_SPAN_SHA256

    # Same alternate-parser executable core as raw bank $0C; only $8000 identifies the bank.
    assert raw04[0] == 0x04 and raw0c[0] == 0x0C
    assert raw04[1:COMMON_CODE_END - 0x8000] == raw0c[1:COMMON_CODE_END - 0x8000]
    assert raw04[COMMON_CODE_END - 0x8000] != raw0c[COMMON_CODE_END - 0x8000]

    def read(addr: int) -> int:
        assert SPAN_START <= addr < SPAN_END
        return raw04[addr - 0x8000]

    # Re-prove the finite local alternate-parser tables in this physical bank.
    assert bytes(read(a) for a in range(0x870B, 0x8713)) == bytes.fromhex("3d837e83b783b385")
    assert bytes(read(a) for a in range(0x83E4, 0x83F8)) == bytes.fromhex(
        "f8830f8456845a848c849f84ed841d852a851d85"
    )
    assert bytes(read(a) for a in range(0x8430, 0x8444)) == bytes.fromhex("4484" * 10)
    assert bytes(read(a) for a in range(0x86F9, 0x870B)) == bytes.fromhex(
        "a986b486bf8644864486688668869e864486"
    )

    pending = deque([0x8001, *sorted(DISPATCH_TARGETS)])
    visited: set[int] = set()
    ext_calls: set[int] = set()
    ext_jumps: set[int] = set()
    indirect_jumps: set[int] = set()
    risks: list[tuple[int, int, int | None]] = []

    while pending:
        pc = pending.popleft()
        if not (0x8001 <= pc < COMMON_CODE_END) or pc in visited:
            continue
        while 0x8001 <= pc < COMMON_CODE_END and pc not in visited:
            visited.add(pc)
            op = read(pc)
            size = SIZE[op]
            assert size != 0, (hex(pc), hex(op))
            o8 = read(pc + 1) if size >= 2 else None
            o16 = (o8 | (read(pc + 2) << 8)) if size == 3 else None

            if op in ZP_DIRECT and o8 == 0x10:
                risks.append((pc, op, o8))
            if op in ZP_INDEXED or op in INDIRECT_STORE:
                risks.append((pc, op, o8))
            if op in ABS_DIRECT and o16 == 0x0010:
                risks.append((pc, op, o16))
            if op in ABS_INDEXED and any(((o16 + i) & 0xFFFF) == 0x0010 for i in range(256)):
                risks.append((pc, op, o16))

            nxt = pc + size
            if op == 0x20:  # JSR
                if 0x8001 <= o16 < COMMON_CODE_END:
                    pending.append(o16)
                else:
                    ext_calls.add(o16)
                pc = nxt
                continue
            if op == 0x4C:  # JMP abs
                if 0x8001 <= o16 < COMMON_CODE_END:
                    pending.append(o16)
                else:
                    ext_jumps.add(o16)
                break
            if op == 0x6C:  # JMP (ind)
                indirect_jumps.add(pc)
                break
            if op in TERM:
                break
            if op in BRANCH:
                delta = o8 if o8 < 0x80 else o8 - 0x100
                target = (pc + 2 + delta) & 0xFFFF
                if 0x8001 <= target < COMMON_CODE_END:
                    pending.append(target)
                else:
                    ext_jumps.add(target)
                pc = nxt
                continue
            pc = nxt

    assert len(visited) == 786
    assert not risks, risks
    assert ext_calls == EXPECTED_EXTERNAL_CALLS, ext_calls
    assert ext_jumps == EXPECTED_EXTERNAL_JUMPS, ext_jumps
    assert indirect_jumps == EXPECTED_INDIRECT_JUMPS, indirect_jumps

    # Reuse the already-established bank-$0C metadata table to enumerate bank-$04 streams.
    def rd0c(cpu: int, n: int = 1) -> bytes:
        assert 0x8000 <= cpu < 0xC000 and cpu + n <= 0xC000
        return raw0c[cpu - 0x8000:cpu - 0x8000 + n]

    ptrs = []
    for sid in range(1, META_COUNT + 1):
        b = rd0c(META_TABLE + (sid - 1) * 2, 2)
        ptrs.append(b[0] | (b[1] << 8))

    refs = []
    for sid, ptr in enumerate(ptrs, 1):
        bank = rd0c(ptr, 1)[0]
        if bank != 0x04:
            continue
        nminus = rd0c(ptr + 1, 1)[0]
        rec = rd0c(ptr, 2 + 3 * (nminus + 1))
        for j in range(nminus + 1):
            inst = rec[2 + 3 * j]
            addr = rec[3 + 3 * j] | (rec[4 + 3 * j] << 8)
            first = raw04[addr - 0x8000]
            refs.append((sid, inst, addr, first))

    assert len(refs) == 102
    assert len({a for _, _, a, _ in refs}) == 96
    assert all(first >= 0x10 and inst not in (5, 6) for _, inst, _, first in refs)

    window_refs = [r for r in refs if r[2] < SPAN_END]
    assert len(window_refs) == 23
    assert len({a for _, _, a, _ in window_refs}) == 23
    assert {sid for sid, _, _, _ in window_refs} == EXPECTED_WINDOW_SOUNDS

    # Absolute byte absence: $E7 cannot be consumed as a command while the stream cursor is in this span.
    assert 0xE7 not in span
    assert max(a for _, _, a, _ in window_refs) == 0x9133

    print("ROM identity: OK")
    print("raw bank $04 / PRG08 span: $8000-$91FF (4608 bytes)")
    print("span SHA-256:", EXPECTED_SPAN_SHA256)
    print("alternate-parser common code: $8001-$87AD")
    print("reachable accepted instruction starts:", len(visited))
    print("reachable write forms that can alias ZP $10: 0")
    print("bank-$04 metadata refs:", len(refs), "distinct roots:", len({a for _, _, a, _ in refs}))
    print("refs rooted inside current span:", len(window_refs), "sounds:", [f"${x:02X}" for x in sorted(EXPECTED_WINDOW_SOUNDS)])
    print("raw $E7 bytes anywhere in $8000-$91FF: 0")
    print("04F7 boundary: parser core is $10-clean; later bank-$04 stream data remains unresolved")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {Path(sys.argv[0]).name} ROM.nes")
    main(sys.argv[1])
