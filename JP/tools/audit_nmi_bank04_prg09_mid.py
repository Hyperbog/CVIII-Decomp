#!/usr/bin/env python3
"""Checkpoint 04F9: close the first 32 remaining raw-bank $04 PRG09 stream roots."""
from __future__ import annotations

import hashlib
import sys
from collections import Counter, deque
from pathlib import Path

ROM_SHA = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
SPAN_START = 0xA012
SPAN_END = 0xB1F0  # exclusive
SPAN_SHA = "796390314526db34b3a63e6abc838c06bebf1194456f98dda39f40743dd816d7"
META_TABLE = 0x8F60
META_COUNT = 0x7D

EXPECTED_REFS = [
    (0x60, 1, 0xA014), (0x60, 2, 0xA199),
    (0x61, 0, 0xA536), (0x61, 1, 0xA6DB), (0x61, 2, 0xA775),
    (0x61, 3, 0xA355), (0x61, 4, 0xA41C), (0x61, 7, 0xA4CA),
    (0x62, 0, 0xABCC), (0x62, 1, 0xAD14), (0x62, 2, 0xAE63),
    (0x62, 3, 0xA84A), (0x62, 4, 0xA973), (0x62, 7, 0xAAB5),
    (0x63, 0, 0xABC7), (0x63, 1, 0xAD0F), (0x63, 2, 0xAE5E),
    (0x63, 3, 0xA840), (0x63, 4, 0xA96E), (0x63, 7, 0xAABF),
    (0x64, 0, 0xAF62), (0x64, 1, 0xB03A), (0x64, 2, 0xB102),
    (0x64, 3, 0xB147), (0x64, 4, 0xB185), (0x64, 7, 0xB1B3),
    (0x66, 0, 0xA2A0), (0x66, 1, 0xA2CF), (0x66, 2, 0xA2FA),
    (0x66, 3, 0xA201), (0x66, 4, 0xA24E), (0x66, 7, 0xA280),
]

def main(path: str) -> None:
    rom = Path(path).read_bytes()
    assert hashlib.sha256(rom).hexdigest() == ROM_SHA
    prg = rom[16:16 + 0x40000]
    raw04 = prg[8 * 0x2000:10 * 0x2000]
    raw0c = prg[24 * 0x2000:26 * 0x2000]

    def r04(a: int, n: int = 1) -> bytes:
        assert 0x8000 <= a < 0xC000 and a + n <= 0xC000
        return raw04[a - 0x8000:a - 0x8000 + n]

    def r0c(a: int, n: int = 1) -> bytes:
        assert 0x8000 <= a < 0xC000 and a + n <= 0xC000
        return raw0c[a - 0x8000:a - 0x8000 + n]

    span = r04(SPAN_START, SPAN_END - SPAN_START)
    assert len(span) == 4574
    assert hashlib.sha256(span).hexdigest() == SPAN_SHA

    ptrs = []
    for sid in range(1, META_COUNT + 1):
        b = r0c(META_TABLE + (sid - 1) * 2, 2)
        ptrs.append(b[0] | (b[1] << 8))

    refs = []
    for sid, ptr in enumerate(ptrs, 1):
        if r0c(ptr)[0] != 0x04:
            continue
        nminus = r0c(ptr + 1)[0]
        rec = r0c(ptr, 2 + 3 * (nminus + 1))
        for j in range(nminus + 1):
            inst = rec[2 + 3 * j]
            addr = rec[3 + 3 * j] | (rec[4 + 3 * j] << 8)
            refs.append((sid, inst, addr, r04(addr)[0]))

    roots = sorted({a for _, _, a, _ in refs})
    assert len(refs) == 102
    assert len(roots) == 96
    assert all(first >= 0x10 and inst not in (5, 6) for _, inst, _, first in refs)

    # 04F7 already counted one root-mode probe byte for every root after $9209.
    assert len([r for r in roots if r >= 0x920A]) == 73
    assert len([r for r in roots if r < SPAN_START]) == 34

    current = [(sid, inst, a) for sid, inst, a, _ in refs if SPAN_START <= a < SPAN_END]
    assert current == EXPECTED_REFS
    current_roots = sorted({a for _, _, a in current})
    assert len(current_roots) == 32
    assert len(span) - len(current_roots) == 4542

    remaining = [r for r in roots if r >= SPAN_END]
    assert len(remaining) == 30
    assert remaining[0] == 0xB1F0

    def decode(root: int, inst: int):
        q = deque([(root, None, None)])
        seen = set()
        commands = set()
        edges = set()
        e7 = []
        outside = []
        missing_anchor = []

        while q:
            pc, ret, anchor = q.popleft()
            state = (pc, ret, anchor)
            if state in seen:
                continue
            seen.add(state)

            if not (SPAN_START <= pc < SPAN_END):
                outside.append(state)
                continue

            cmd = r04(pc)[0]
            commands.add(pc)
            top = cmd >> 4
            sub = cmd & 0x0F
            nxt = []

            if inst == 7 and top != 0xF:
                nxt = [(pc + 1, ret, anchor)]
            elif inst != 7 and top != 0xF:
                if top <= 0xC:
                    nxt = [(pc + 1, ret, anchor)]
                elif top == 0xD:
                    nxt = [(pc + 4, ret, anchor)]
                elif top == 0xE:
                    if sub <= 5:
                        nxt = [(pc + 1, ret, anchor)]
                    elif sub == 6:
                        nxt = [(pc + 2, ret, anchor)]
                    elif sub == 7:
                        e7.append(pc)
                        nxt = [(pc + 2, ret, anchor)]
                    elif sub in (8, 9, 10, 12, 13, 14, 15):
                        nxt = [(pc + 2, ret, anchor)]
                    elif sub == 11:
                        p = r04(pc + 1)[0]
                        nxt = [(pc + (2 if p == 0 else 3), ret, anchor)]

            if top == 0xF:
                if sub <= 0xA or sub == 0xC:
                    nxt = [(pc + 1, ret, anchor)]
                elif sub == 0xB:
                    nxt = [(pc + 1, ret, pc + 1)]
                elif sub == 0xD:
                    if ret is None:
                        target = r04(pc + 1)[0] | (r04(pc + 2)[0] << 8)
                        edges.add((pc, "FD-call", target))
                        nxt = [(target, pc + 3, anchor)]
                    else:
                        edges.add((pc, "FD-ret", ret))
                        nxt = [(ret, None, anchor)]
                elif sub == 0xE:
                    p = r04(pc + 1)[0]
                    if p == 0xFF:
                        target = r04(pc + 2)[0] | (r04(pc + 3)[0] << 8)
                        edges.add((pc, "FE-jmp", target))
                        nxt = [(target, ret, anchor)]
                    else:
                        nxt = [(pc + 2, ret, anchor)]
                        if anchor is None:
                            missing_anchor.append(pc)
                        else:
                            edges.add((pc, "FE-loop", anchor))
                            nxt.append((anchor, ret, anchor))
                elif sub == 0xF:
                    nxt = []

            q.extend(nxt)

        return seen, commands, edges, e7, outside, missing_anchor

    total_states = 0
    all_commands = set()
    all_edges = set()
    all_e7 = []
    all_outside = []
    all_missing = []

    for _, inst, root in current:
        seen, commands, edges, e7, outside, missing = decode(root, inst)
        total_states += len(seen)
        all_commands |= commands
        all_edges |= edges
        all_e7 += e7
        all_outside += outside
        all_missing += missing

    assert total_states == 5869
    assert len(all_commands) == 3776
    assert min(all_commands) == 0xA014
    assert max(all_commands) == 0xB1EC
    assert not all_e7
    assert not all_outside
    assert not all_missing
    assert not [a for a in range(SPAN_START, SPAN_END) if r04(a)[0] == 0xE7]
    assert all(SPAN_START <= target < SPAN_END for _, _, target in all_edges)

    edge_counts = Counter(kind for _, kind, _ in all_edges)
    assert edge_counts == Counter({"FE-loop": 62, "FE-jmp": 20, "FD-call": 9, "FD-ret": 4})

    print("ROM identity: OK")
    print(f"04F9 dependency span: ${SPAN_START:04X}-${SPAN_END-1:04X} ({len(span)} bytes)")
    print("span SHA-256:", SPAN_SHA)
    print("32 root bytes overlap 04F7 mode probes; exact new-byte footprint: 4542")
    print("closed roots: 32; cumulative bank-$04 roots closed: 66/96")
    print("sound IDs represented: $60 $61 $62 $63 $64 $66")
    print("abstract parser states:", total_states)
    print("unique decoded command addresses:", len(all_commands))
    print("raw/decoded E7 commands in closed span: 0")
    print("pointer edges:", dict(sorted(edge_counts.items())))
    print("all FD/FE pointer targets stay inside the closed span")
    print("remaining bank-$04 roots: 30; next root/frontier: $B1F0")
    print("04F9 result: these 32 additional bank-$04 roots cannot activate $842D and preserve ZP $10")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {Path(sys.argv[0]).name} ROM.nes")
    main(sys.argv[1])
