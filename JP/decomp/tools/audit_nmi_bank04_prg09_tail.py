#!/usr/bin/env python3
"""Checkpoint 04FA: finish all remaining raw-bank $04 PRG09 stream roots."""
from __future__ import annotations

import hashlib
import sys
from collections import Counter, deque
from pathlib import Path

ROM_SHA = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
SPAN_START = 0xB1F0
SPAN_END = 0xBE7E  # exclusive; final reachable command is one-byte $FF at $BE7D
SPAN_SHA = "a7f0a8308ed9335b27de8eaf3df440f0d28cd6f57fb97e4123222e3116fc5f55"
META_TABLE = 0x8F60
META_COUNT = 0x7D
REFS_SHA = "0231954086948dd7e7039a6828ec6397b5cb93fb71b7614a6b8a7ab049a02ad7"
ROOTS_SHA = "193a8f5ae97a1ec7a729d4b6954d1561a699fa16bda7eca0140cc299a380ae2b"


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
    assert len(span) == 3214
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
    assert len(refs) == 102 and len(roots) == 96
    assert all(first >= 0x10 and inst not in (5, 6) for _, inst, _, first in refs)
    assert len([r for r in roots if r < SPAN_START]) == 66

    current = [(sid, inst, a) for sid, inst, a, _ in refs if a >= SPAN_START]
    current_roots = sorted({a for _, _, a in current})
    ref_ser = "\n".join(f"{sid:02X},{inst:02X},{a:04X}" for sid, inst, a in current).encode()
    root_ser = "\n".join(f"{a:04X}" for a in current_roots).encode()
    assert hashlib.sha256(ref_ser).hexdigest() == REFS_SHA
    assert hashlib.sha256(root_ser).hexdigest() == ROOTS_SHA
    assert len(current) == 36 and len(current_roots) == 30
    assert current_roots[0] == 0xB1F0 and current_roots[-1] == 0xBE7D
    assert len(span) - len(current_roots) == 3184
    assert {sid for sid, _, _ in current} == {0x5F, 0x68, 0x6A, 0x6C, 0x6D, 0x6E}

    def decode(root: int, inst: int):
        q = deque([(root, None, None)])
        seen = set(); commands = set(); edges = set()
        e7 = []; outside = []; missing_anchor = []
        max_read = SPAN_START

        def need(pc: int, n: int) -> None:
            assert SPAN_START <= pc < SPAN_END and pc + n <= SPAN_END, (
                f"command/operand escapes accounted span: pc=${pc:04X} len={n} "
                f"span=${SPAN_START:04X}-${SPAN_END-1:04X}"
            )

        while q:
            pc, ret, anchor = q.popleft()
            state = (pc, ret, anchor)
            if state in seen:
                continue
            seen.add(state)
            if not (SPAN_START <= pc < SPAN_END):
                outside.append(state)
                continue

            need(pc, 1)
            cmd = r04(pc)[0]
            commands.add(pc)
            top, sub = cmd >> 4, cmd & 0x0F
            nxt = []
            width = 1

            if inst == 7 and top != 0xF:
                nxt = [(pc + 1, ret, anchor)]
            elif inst != 7 and top != 0xF:
                if top <= 0xC:
                    nxt = [(pc + 1, ret, anchor)]
                elif top == 0xD:
                    width = 4; need(pc, width); nxt = [(pc + 4, ret, anchor)]
                elif top == 0xE:
                    if sub <= 5:
                        nxt = [(pc + 1, ret, anchor)]
                    elif sub in (6, 7, 8, 9, 10, 12, 13, 14, 15):
                        width = 2; need(pc, width)
                        if sub == 7:
                            e7.append(pc)
                        nxt = [(pc + 2, ret, anchor)]
                    elif sub == 11:
                        width = 2; need(pc, width)
                        if r04(pc + 1)[0] == 0:
                            nxt = [(pc + 2, ret, anchor)]
                        else:
                            width = 3; need(pc, width); nxt = [(pc + 3, ret, anchor)]

            if top == 0xF:
                if sub <= 0xA or sub == 0xC:
                    nxt = [(pc + 1, ret, anchor)]
                elif sub == 0xB:
                    nxt = [(pc + 1, ret, pc + 1)]
                elif sub == 0xD:
                    if ret is None:
                        width = 3; need(pc, width)
                        target = r04(pc + 1)[0] | (r04(pc + 2)[0] << 8)
                        edges.add((pc, "FD-call", target))
                        nxt = [(target, pc + 3, anchor)]
                    else:
                        edges.add((pc, "FD-ret", ret))
                        nxt = [(ret, None, anchor)]
                elif sub == 0xE:
                    width = 2; need(pc, width)
                    p = r04(pc + 1)[0]
                    if p == 0xFF:
                        width = 4; need(pc, width)
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

            max_read = max(max_read, pc + width)
            q.extend(nxt)

        return seen, commands, edges, e7, outside, missing_anchor, max_read

    total_states = 0
    all_commands = set(); all_edges = set(); all_e7 = []
    all_outside = []; all_missing = []; max_read = SPAN_START
    for _, inst, root in current:
        seen, commands, edges, e7, outside, missing, local_max = decode(root, inst)
        total_states += len(seen)
        all_commands |= commands; all_edges |= edges
        all_e7 += e7; all_outside += outside; all_missing += missing
        max_read = max(max_read, local_max)

    assert total_states == 3426
    assert len(all_commands) == 2595
    assert min(all_commands) == 0xB1F0 and max(all_commands) == 0xBE7D
    assert max_read == SPAN_END
    assert not all_e7 and not all_outside and not all_missing
    assert all(SPAN_START <= target < SPAN_END for _, _, target in all_edges)

    edge_counts = Counter(kind for _, kind, _ in all_edges)
    assert edge_counts == Counter({"FD-call": 20, "FD-ret": 20, "FE-jmp": 17, "FE-loop": 16})

    assert r04(0xB818, 4) == bytes.fromhex("feffe7b7")
    assert (0xB818, "FE-jmp", 0xB7E7) in all_edges
    assert [a for a in range(SPAN_START, SPAN_END) if r04(a)[0] == 0xE7] == [0xB81A]
    assert r04(0xBFEB)[0] == 0xE7 and 0xBFEB not in all_commands

    print("ROM identity: OK")
    print("strict operand-in-span checks: OK")
    print("04FA dependency span: $B1F0-$BE7D (3214 bytes), SHA-256", SPAN_SHA)
    print("30 root bytes overlap 04F7 mode probes; exact new-byte footprint: 3184")
    print("metadata refs: 36; distinct roots: 30; cumulative bank-$04 roots closed: 96/96")
    print("sound IDs represented: $5F $68 $6A $6C $6D $6E")
    print("abstract parser states:", total_states)
    print("unique decoded command addresses:", len(all_commands))
    print("decoded E7 commands: 0")
    print("raw $E7 at $B81A is FE-FF pointer-low operand; raw $E7 at $BFEB is outside reachable dependency")
    print("pointer edges:", dict(sorted(edge_counts.items())))
    print("all FD/FE pointer targets stay inside the closed span")
    print("04FA result: all raw-bank $04 roots are closed and preserve ZP $10")
    print("next sound-side domain: raw instrument bank $05")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {Path(sys.argv[0]).name} ROM.nes")
    main(sys.argv[1])
