#!/usr/bin/env python3
from __future__ import annotations
import hashlib, sys
from collections import Counter, deque
from pathlib import Path

EXPECTED_SHA256 = '958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
EXPECTED_SPAN_SHA256 = 'ee8b2de23022f715d3934907e7caaab91e824b4a9a31ccb75a69dae7d55c178b'
SPAN_START, SPAN_END = 0x8000, 0x9200
CODE_END = 0x87AE
META_TABLE, META_COUNT = 0x8F60, 0x7D
SIZE = bytes.fromhex('01020000000202000102010000030300020200000002020001030000000303000302000002020200010201000303030002020000000202000103000000030300010200000002020001020100030303000202000000020200010300000003030001020000000202000102010003030300020200000002020001030000000303000002000002020200010001000303030002020000020202000103010000030000020202000202020001020100030303000202000002020200010301000303030002020000020202000102010003030300020200000002020001030000000303000202000002020200010201000303030002020000000202000103000000030300')
BRANCH = {0x10,0x30,0x50,0x70,0x90,0xB0,0xD0,0xF0}
TERM = {0x00,0x40,0x60}
ZP_DIRECT = {0x84,0x85,0x86,0x06,0x26,0x46,0x66,0xC6,0xE6}
ZP_INDEXED = {0x94,0x95,0x96,0x16,0x36,0x56,0x76,0xD6,0xF6}
INDIRECT_STORE = {0x81,0x91}
ABS_DIRECT = {0x8C,0x8D,0x8E,0x0E,0x2E,0x4E,0x6E,0xCE,0xEE}
ABS_INDEXED = {0x99,0x9D,0x1E,0x3E,0x5E,0x7E,0xDE,0xFE}
DISPATCH_TARGETS = {
    0x833D,0x837E,0x83B7,0x85B3,
    0x83F8,0x840F,0x8456,0x845A,0x848C,0x849F,0x84ED,0x851D,0x852A,
    0x8444,
    0x86A9,0x86B4,0x86BF,0x8644,0x8668,0x869E,
}
EXPECTED_CALLS = {0xE1B8,0xE1C8,0xE1D6,0xE1F6,0xE249}
EXPECTED_JUMPS = {0xE190,0xE195,0xE1E4,0xE1EE}
EXPECTED_INDIRECTS = {0x802E,0x83E1,0x842D,0x8641}
EXPECTED_SOUND_IDS = {0x5A,0x5D,0x5E,0x5F,0x60,0x61,0x62,0x63,0x64,0x65,0x66,0x67,0x68,0x6A,0x6C,0x6D,0x6E}


def main(path: str) -> None:
    rom = Path(path).read_bytes()
    assert hashlib.sha256(rom).hexdigest() == EXPECTED_SHA256
    prg = rom[16:16+0x40000]
    raw04 = prg[8*0x2000:10*0x2000]
    raw0c = prg[24*0x2000:26*0x2000]

    def r04(cpu: int, n: int = 1) -> bytes:
        assert 0x8000 <= cpu < 0xC000 and cpu+n <= 0xC000
        return raw04[cpu-0x8000:cpu-0x8000+n]

    def r0c(cpu: int, n: int = 1) -> bytes:
        assert 0x8000 <= cpu < 0xC000 and cpu+n <= 0xC000
        return raw0c[cpu-0x8000:cpu-0x8000+n]

    span = r04(SPAN_START, SPAN_END-SPAN_START)
    assert len(span) == 4608
    assert hashlib.sha256(span).hexdigest() == EXPECTED_SPAN_SHA256
    assert r04(0x8000) == b'\x04' and r0c(0x8000) == b'\x0c'
    assert r04(0x8001, CODE_END-0x8001) == r0c(0x8001, CODE_END-0x8001)

    ptrs = []
    for sid in range(1, META_COUNT+1):
        b = r0c(META_TABLE+(sid-1)*2, 2)
        ptrs.append(b[0] | (b[1] << 8))
    refs = []
    for sid, ptr in enumerate(ptrs, 1):
        bank = r0c(ptr)[0]
        if bank == 0:
            continue
        nminus = r0c(ptr+1)[0]
        rec = r0c(ptr, 2+3*(nminus+1))
        for j in range(nminus+1):
            inst = rec[2+3*j]
            addr = rec[3+3*j] | (rec[4+3*j] << 8)
            if bank == 0x04:
                refs.append((sid, inst, addr, r04(addr)[0]))

    roots = sorted({a for _,_,a,_ in refs})
    assert len(refs) == 102
    assert len(roots) == 96
    assert {sid for sid,_,_,_ in refs} == EXPECTED_SOUND_IDS
    assert Counter(inst for _,inst,_,_ in refs) == Counter({0:17,1:17,2:17,3:17,4:17,7:17})
    assert all(first >= 0x10 and inst not in (5,6) for _,inst,_,first in refs)
    assert roots[0] == 0x87AE and roots[-1] == 0xBE7D and r04(0xBE7D) == b'\xff'

    stream_e7 = [a for a in range(roots[0], roots[-1]+1) if r04(a)[0] == 0xE7]
    assert stream_e7 == [0xB81A]
    assert r04(0xB818, 4) == bytes.fromhex('feffe7b7')
    assert r04(0x8543, 0x20) == bytes.fromhex(
        'c8b1e0c9ffd022c8b1e09d2d0185e2c8b1e09d360185e1a5e285e0a000bd1b01'
    )
    loop_ptrs = []
    for a in range(roots[0], roots[-1]-3):
        if r04(a, 2) == b'\xfe\xff':
            t = r04(a+2)[0] | (r04(a+3)[0] << 8)
            loop_ptrs.append((a, t))
    assert len(loop_ptrs) == 59
    assert all(roots[0] <= t <= roots[-1] for _,t in loop_ptrs)

    all_e7 = [0x8000+i for i,b in enumerate(raw04) if b == 0xE7]
    assert all_e7 == [0xB81A, 0xBFEB]
    assert r04(0xBFE9, 6) == bytes.fromhex('2005e7a66960')

    assert r04(0x8410, 0x42) == r0c(0x8410, 0x42)
    assert r04(0x8410, 8) == bytes.fromhex('bd8e0109809d8e01')
    assert r04(0x844A, 8) == bytes.fromhex('bd8e01297f9d8e01')

    def rb(addr: int) -> int:
        return raw04[addr-0x8000]

    pending = deque([0x8001, *sorted(DISPATCH_TARGETS)])
    visited, calls, jumps, indirects = set(), set(), set(), set()
    risks = []
    while pending:
        pc = pending.popleft()
        if not (0x8001 <= pc < CODE_END) or pc in visited:
            continue
        while 0x8001 <= pc < CODE_END and pc not in visited:
            visited.add(pc)
            op = rb(pc); size = SIZE[op]
            assert size != 0, (hex(pc), hex(op))
            o8 = rb(pc+1) if size >= 2 else None
            o16 = (o8 | (rb(pc+2) << 8)) if size == 3 else None

            if op in ZP_DIRECT and o8 == 0x10: risks.append((pc, op, o8))
            if op in ZP_INDEXED or op in INDIRECT_STORE: risks.append((pc, op, o8))
            if op in ABS_DIRECT and o16 == 0x0010: risks.append((pc, op, o16))
            if op in ABS_INDEXED and any(((o16+i)&0xFFFF) == 0x0010 for i in range(256)):
                risks.append((pc, op, o16))

            nxt = pc + size
            if op == 0x20:
                if 0x8001 <= o16 < CODE_END: pending.append(o16)
                else: calls.add(o16)
                pc = nxt; continue
            if op == 0x4C:
                if 0x8001 <= o16 < CODE_END: pending.append(o16)
                else: jumps.add(o16)
                break
            if op == 0x6C:
                indirects.add(pc); break
            if op in TERM: break
            if op in BRANCH:
                d = o8 if o8 < 0x80 else o8-0x100
                target = (pc+2+d) & 0xFFFF
                if 0x8001 <= target < CODE_END: pending.append(target)
                else: jumps.add(target)
                pc = nxt; continue
            pc = nxt

    assert len(visited) == 786
    assert not risks, risks
    assert calls == EXPECTED_CALLS, calls
    assert jumps == EXPECTED_JUMPS, jumps
    assert indirects == EXPECTED_INDIRECTS, indirects

    print('ROM identity: OK')
    print(f'raw bank $04 span: ${SPAN_START:04X}-${SPAN_END-1:04X} (4608 bytes)')
    print('span SHA-256:', EXPECTED_SPAN_SHA256)
    print('common alternate-parser code: $8001-$87AD, byte-identical to bank $0C')
    print('bank-$04 metadata refs:', len(refs), 'distinct roots:', len(roots), 'sound IDs:', len(EXPECTED_SOUND_IDS))
    print('all bank-$04 references initialize alternate-parser mode')
    print('stream-storage raw $E7 bytes:', [f'${a:04X}' for a in stream_e7])
    print('$B81A is FE FF pointer payload -> $B7E7, not an E7 command')
    print('reachable accepted instruction starts:', len(visited))
    print('reachable write forms that can alias ZP $10: 0')
    print('04F7 result: live raw bank $04 alternate-parser paths preserve ZP $10; $842D is not live')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit(f'usage: {Path(sys.argv[0]).name} ROM.nes')
    main(sys.argv[1])
