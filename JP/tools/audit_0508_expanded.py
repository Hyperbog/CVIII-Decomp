#!/usr/bin/env python3
"""Checkpoint 0508 foundation: exact bank-$0A predecessor and room dispatch atlas.

Usage: python audit_0508_expanded.py JP.nes [report.json]
This performs a whole-16KiB bank discovery pass, then a ROM-locked
conditional CFG. It never treats encoded pointer slots as live selectors.
"""
from __future__ import annotations
from collections import Counter, deque
from pathlib import Path
import hashlib
import json
import sys

try:
    from audit_nmi_fixed_scheduler_banked import OPS, BR, TERM
except ImportError:  # standalone local execution alongside prior review tool
    from dis6502_0508 import D as OPS
    BR = {'BPL', 'BMI', 'BVC', 'BVS', 'BCC', 'BCS', 'BNE', 'BEQ'}
    TERM = {'RTS', 'RTI', 'BRK'}

JP_SHA = '958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
OVERLAP_SHA = 'e4fa5e06e439ca12a84d935eb80224f448276c722399fe76fe0ce60013cc4ee7'
FRONT_SHA = 'a5437f0f20034ba34d65afeec353d28846a321134061f765814d28eaa3f69157'
ROOM_ENTRY_SHA = '0cbfd39d34523da29edaa6a2dcf5cdb4b62de628d0e5568ea3879d7de5a1c0c7'
OLD_GRAPH_SHA = '807363d09368f7ae6ceaeae000df0fc50f56bba5bd2871ca749d7236ec9f3828'
PREDECESSOR_TABLE_SHA = '422e65c2a5a5c30ea2e6a7c77978d54c2d1cd64b99628e7f94662a29f9f7d396'
FIRST_LEVEL = [(0xAFA4, 0xAFA6), (0xB4CC, 0xB4CE)]
# E7FB performs a tail JMP; the following bytes are caller-owned pointer data.
INLINE = {0xAFA6: (0xAFA9, 20),
          0xB122: (0xB125, 22),
          0xB4CE: (0xB4D1, 12),
          0xB68B: (0xB68E, 11)}
WRITE = {'STA', 'STX', 'STY', 'INC', 'DEC', 'ASL', 'LSR', 'ROL', 'ROR'}
WATCH = {0x18, 0x19, 0x68, 0x07A0, 0x07A6, 0x054E}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def intervals(values: set[int]) -> list[tuple[int, int]]:
    result: list[list[int]] = []
    for v in sorted(values):
        if not result or v != result[-1][1]:
            result.append([v, v + 1])
        else:
            result[-1][1] = v + 1
    return [(a, b) for a, b in result]


def decode(bank: bytes, pc: int):
    assert 0x8000 <= pc < 0xC000
    op = bank[pc - 0x8000]
    assert op in OPS, (hex(pc), hex(op))
    name, mode, n = OPS[op]
    assert pc + n <= 0xC000
    data = bank[pc - 0x8000:pc - 0x8000 + n]
    assert len(data) == n
    arg = (None if n == 1 else data[1] if n == 2
           else int.from_bytes(data[1:3], 'little'))
    if mode == 'rel':
        arg = (pc + 2 + (arg if arg < 0x80 else arg - 0x100)) & 0xFFFF
    return name, mode, n, arg


def walk(bank: bytes, roots: list[int]):
    queue = deque(roots)
    starts = {}
    claimed = {}
    outside = []
    inline = []
    stores = []
    while queue:
        pc = queue.popleft()
        if pc in starts:
            continue
        if not 0x8000 <= pc < 0xC000:
            outside.append(('external-root', None, pc))
            continue
        name, mode, n, arg = decode(bank, pc)
        for byte in range(pc, pc + n):
            assert byte not in claimed, (hex(pc), hex(byte), hex(claimed[byte]))
            claimed[byte] = pc
        starts[pc] = (name, mode, n, arg)
        if name in WRITE and mode != 'acc':
            stores.append((pc, name, mode, arg))
        if pc in INLINE:
            assert name == 'JSR' and arg == 0xE7FB
            inline.append(pc)
            continue
        def edge(kind: str, target: int):
            if 0x8000 <= target < 0xC000:
                queue.append(target)
            else:
                outside.append((kind, pc, target))
        if name in BR:
            edge('branch', arg)
            edge('fallthrough', pc + n)
        elif name == 'JSR':
            edge('jsr', arg)
            edge('return', pc + n)
        elif name == 'JMP':
            if mode == 'ind':
                outside.append(('indirect', pc, arg))
            else:
                edge('jmp', arg)
        elif name not in TERM:
            edge('fallthrough', pc + n)
        assert len(starts) < 10000, 'unexpected root explosion'
    return starts, set(claimed), outside, inline, stores


def audit(path: Path) -> dict:
    rom = path.read_bytes()
    assert len(rom) == 393232 and sha(rom) == JP_SHA
    prg = rom[16:16+0x40000]
    assert len(prg) == 0x40000
    bank = prg[0x0A*0x4000:0x0B*0x4000]
    fixed = prg[31*0x2000:32*0x2000]
    assert len(bank) == 16384 and len(fixed) == 8192
    f = lambda addr, size: fixed[addr-0xE000:addr-0xE000+size]
    b = lambda addr, size: bank[addr-0x8000:addr-0x8000+size]
    word = lambda addr: int.from_bytes(b(addr, 2), 'little')
    assert sha(f(0xFB76, 32)) == OVERLAP_SHA
    assert sha(f(0xFB96, 32)) == FRONT_SHA
    assert f(0xE2D0, 6) == bytes.fromhex('85 23 8d 00 80 60')
    assert f(0xE51E, 8) == bytes.fromhex('a9 0a 20 d0 e2 4c a4 af')
    assert f(0xE526, 8) == bytes.fromhex('a9 0a 20 d0 e2 4c cc b4')
    assert f(0xE360, 3) == bytes.fromhex('20 fb e7')
    assert int.from_bytes(f(0xE363 + 2*12, 2), 'little') == 0xE51E
    assert int.from_bytes(f(0xE363 + 2*13, 2), 'little') == 0xE526
    assert sha(b(0xAFA4, 5)) == sha(b(0xB4CC, 5)) == ROOM_ENTRY_SHA
    assert b(0xAFA4, 5) == b(0xB4CC, 5) == bytes.fromhex('a5 19 20 fb e7')
    assert sha(b(0xAFA9, 40)) == PREDECESSOR_TABLE_SHA

    tables = {}
    for site, (base, count) in INLINE.items():
        assert b(site, 3) == bytes.fromhex('20 fb e7')
        assert base == site + 3
        values = [word(base + 2*i) for i in range(count)]
        assert all(0x8000 <= x < 0xC000 for x in values)
        tables[f'{site:04X}'] = {
            'data_cpu_range': f'{base:04X}-{base+2*count-1:04X}',
            'encoded_words': count,
            'unique_targets': len(set(values)),
            'sha256': sha(b(base, 2*count)),
            'targets': [f'{v:04X}' for v in values]
        }

    assert word(0xAFA9 + 2*19) == 0xB36B
    assert b(0xB36B, 15) == bytes.fromhex('ad 89 07 8d 81 07 a9 0d 85 18 a9 00 85 19 60')
    assert b(0xB11B, 4) == bytes([0x00, 0x03, 0x10, 0x13])
    assert b(0xB626, 7) == bytes.fromhex('a9 00 8d a6 07 e6 19')
    assert b(0xB873, 51) == bytes.fromhex(
        'ad a6 07 0a 18 6d a6 07 a8 b9 a6 b8 c9 ff f0 21 '
        '85 5f b9 a7 b8 85 5e b9 a8 b8 85 10 20 43 e8 '
        'a9 00 9d 00 03 e8 c6 10 d0 f8 20 6b e8 '
        'ee a6 07 18 60 38 60')
    descriptor = b(0xB8A6, 28)
    assert [descriptor[3*i] for i in range(9)] == [0x24, 0x25, 0x25, 0x25, 0x25, 0x26, 0x26, 0x26, 0x26]
    assert descriptor[27] == 0xFF

    roots_0507 = [0xB4CC, *[word(0xB4D1 + 2*i) for i in range(12)], 0xB6A4]
    old, old_bytes, _, old_inline, _ = walk(bank, roots_0507)
    assert (len(old), len(old_bytes)) == (281, 582)
    assert sorted(old_inline) == [0xB4CE, 0xB68B]
    old_ranges = [{
        'start_cpu': f'{a:04X}', 'end_cpu_inclusive': f'{c-1:04X}',
        'length': c-a, 'sha256': sha(b(a, c-a))
    } for a, c in intervals(old_bytes)]
    digest = sha(json.dumps(old_ranges, sort_keys=True, separators=(',', ':')).encode())
    assert digest == OLD_GRAPH_SHA, (digest, OLD_GRAPH_SHA)

    roots = [0xAFA4, 0xB4CC] + [int(x, 16) for v in tables.values() for x in v['targets']]
    starts, code, external, actual_inline, writes = walk(bank, roots)
    assert len(starts) == 935 and len(code) == 2042
    assert sorted(actual_inline) == sorted(INLINE)
    assert old_bytes <= code
    assert len(code - old_bytes) == 2042 - 582
    data = set().union(*(set(range(base, base+count*2)) for base,count in INLINE.values()))
    assert not (data & code), 'inline pointer data is being misclassified as code'

    # Exhaustive 16KiB *discovery* sweep: test every physical byte as a
    # possible opcode start. These are NOT verified executable locations.
    opcode_candidates = 0
    control_candidates = 0
    raw_direct_writers = {f'{v:04X}': [] for v in sorted(WATCH)}
    for pc in range(0x8000, 0xC000):
        opbyte = bank[pc - 0x8000]
        if opbyte not in OPS:
            continue
        name, mode, size = OPS[opbyte]
        if pc + size > 0xC000:
            continue
        opcode_candidates += 1
        if name in BR or name in ('JSR', 'JMP'):
            control_candidates += 1
        if name in WRITE and mode in ('zp', 'abs'):
            _, _, _, operand = decode(bank, pc)
            key = f'{operand:04X}'
            if key in raw_direct_writers:
                raw_direct_writers[key].append(f'{pc:04X}')

    direct = {f'{addr:04X}': [{'cpu':f'{pc:04X}', 'opcode':op, 'mode':mode}
            for pc,op,mode,a in sorted(writes) if a == addr]
        for addr in sorted(WATCH)}
    records = [b(0xB8A6+3*i, 3).hex().upper() for i in range(9)]
    return {
        'status': '0508_FOUNDATION_CANDIDATE_NOT_COMMITTED',
        'jp_rom_sha256': JP_SHA,
        'whole_raw_bank_0a_prg_bytes_examined': len(bank),
        'whole_raw_bank_0a_sha256': sha(bank),
        'full_bank_byte_start_discovery': {
            'physical_start_offsets_checked':16384,
            'legal_official_opcode_start_candidates':opcode_candidates,
            'candidate_control_flow_starts':control_candidates,
            'candidate_direct_writes_to_watched_address':raw_direct_writers,
            'warning':'all-offset byte-pattern sweep; not proof of executed code'
        },
        'mapping': {'raw_vrc6_bank': '0A', 'physical_prg_banks': [20,21],
                    'cpu_window': '8000-BFFF'},
        'nmi_fixed_indices': {'0C': 'E51E -> AFA4', '0D': 'E526 -> B4CC'},
        'independently_replayed_0507': {'instruction_starts':len(old),
            'instruction_operand_bytes':len(old_bytes), 'range_fingerprint':digest},
        'new_candidate_control_flow_atlas': {
            'instruction_starts':len(starts), 'instruction_operand_bytes':len(code),
            'new_candidate_vs_0507':len(code-old_bytes),
            'external_edges':len(external),
            'external_destinations': {f'{addr:04X}':num for addr,num in sorted(
                Counter(v[2] for v in external).items(), key=lambda x: (-x[1],x[0]))},
            'code_ranges': [{'start_cpu':f'{a:04X}', 'end_cpu_inclusive':f'{c-1:04X}',
                             'length':c-a, 'sha256':sha(b(a,c-a))} for a,c in intervals(code)],
            'all_4_inline_tables': tables,
            'direct_instruction_writes_to_watchlist': direct,
            'semantic_status': 'conditional decode only; no live selector or external bank proof'
        },
        'conditional_state_transition': 'AFA4 $19=$13 -> B36B writes $18=$0D, $19=$00',
        'room_loader': {'descriptor_records':records, 'index_9_sentinel_byte':'B8C1:FF',
                        'effect': 'B873 branches to SEC for $07A6=9; global index bound unproved'},
        'strict_0508_entry_candidate': {'cpu':'AFA4-AFA8', 'bytes':5,
            'sha256':ROOM_ENTRY_SHA,
            'reason':'fixed E51E explicitly establishes raw bank 0A before jumping to AFA4',
            'promotion_status':'NOT YET LEDGERED'},
        'strict_prg_floor_unchanged':49404,
        'vpp_unchanged':24,
        'open_edges':['live $18=$0C and $19=$13 reachability',
            '$0783 and $19 selector domains; aliases beyond inline table widths',
            'inter-frame mutations of $18/$19/$68 and $07A0/$07A6',
            'callee mapper/context restoration for banked returns',
            'fixed FB96 and indexed room pointer $B8C2 domain',
            'full 0507 native and repository recovery suite not rerun here']
    }


if __name__ == '__main__':
    if len(sys.argv) not in (2,3):
        sys.exit('usage: audit_0508_expanded.py JP.nes [report.json]')
    report = audit(Path(sys.argv[1]))
    if len(sys.argv) == 3:
        Path(sys.argv[2]).write_text(json.dumps(report,indent=2)+'\n')
    print('JP SHA256 PASS; 0507 281/582 regression PASS; 16KiB bank indexed')
    print('0508 candidate CFG: 935 starts, 2042 code+operand bytes, 4 inline tables')
    print('Strict ledger unchanged: 49404; VPP unchanged: 24')