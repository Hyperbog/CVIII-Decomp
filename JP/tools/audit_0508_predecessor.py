#!/usr/bin/env python3
"""0508 preliminary: ROM-exact NMI state-$0C predecessor and room loader gate.

The identified pointer tables and conditional paths are NOT live-state proofs.
No new bytes are admitted to the strict PRG coverage ledger by this audit.
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

JP_SHA = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
ENTRY_SHA = "0cbfd39d34523da29edaa6a2dcf5cdb4b62de628d0e5568ea3879d7de5a1c0c7"
PREV_SHA = "e4fa5e06e439ca12a84d935eb80224f448276c722399fe76fe0ce60013cc4ee7"
FRONT_SHA = "a5437f0f20034ba34d65afeec353d28846a321134061f765814d28eaa3f69157"
TABLE_SHA = "422e65c2a5a5c30ea2e6a7c77978d54c2d1cd64b99628e7f94662a29f9f7d396"
HANDLER_SHA = "bf540ae8289f46a474fb7e476e43fffca9c6da8bf8ac48c2e67f62e497c0668c"
DESCRIPTORS_SHA = "2f19ecd60020f0c3bfa81ce07448a7bba7d4c75857a9fe47951bb31fe5792c25"


def audit(path: str) -> dict:
    rom = Path(path).read_bytes()
    assert len(rom) == 393232
    assert hashlib.sha256(rom).hexdigest() == JP_SHA
    prg = rom[16:16 + 0x40000]
    fixed = prg[31 * 0x2000:32 * 0x2000]
    raw0a = prg[0x0A * 0x4000:0x0B * 0x4000]

    def f(cpu: int, length: int) -> bytes:
        assert 0xE000 <= cpu < 0x10000 and cpu + length <= 0x10000
        return fixed[cpu - 0xE000:cpu - 0xE000 + length]

    def b(cpu: int, length: int) -> bytes:
        assert 0x8000 <= cpu < 0xC000 and cpu + length <= 0xC000
        return raw0a[cpu - 0x8000:cpu - 0x8000 + length]

    assert hashlib.sha256(f(0xFB76, 32)).hexdigest() == PREV_SHA
    assert hashlib.sha256(f(0xFB96, 32)).hexdigest() == FRONT_SHA
    assert f(0xE360, 3) == bytes.fromhex('20 fb e7')
    ptr = lambda address: int.from_bytes(f(address, 2), 'little')
    assert ptr(0xE363 + 12 * 2) == 0xE51E
    assert ptr(0xE363 + 13 * 2) == 0xE526
    assert f(0xE51E, 8) == bytes.fromhex('a9 0a 20 d0 e2 4c a4 af')
    assert f(0xE526, 8) == bytes.fromhex('a9 0a 20 d0 e2 4c cc b4')
    assert f(0xE2D0, 6) == bytes.fromhex('85 23 8d 00 80 60')

    preceding = b(0xAFA4, 5)
    successor = b(0xB4CC, 5)
    assert preceding == successor == bytes.fromhex('a5 19 20 fb e7')
    assert hashlib.sha256(preceding).hexdigest() == ENTRY_SHA
    table = b(0xAFA9, 40)
    assert hashlib.sha256(table).hexdigest() == TABLE_SHA
    pointers = [int.from_bytes(table[i:i+2], 'little') for i in range(0, 40, 2)]
    assert len(pointers) == 20 and pointers[0] == 0xAFD1 and pointers[19] == 0xB36B
    assert b(0xAFD1, 3) == bytes.fromhex('20 16 e6')

    state_13 = b(0xB36B, 15)
    assert hashlib.sha256(state_13).hexdigest() == HANDLER_SHA
    assert state_13 == bytes.fromhex('ad 89 07 8d 81 07 a9 0d 85 18 a9 00 85 19 60')

    assert b(0xB626, 9) == bytes.fromhex('a9 00 8d a6 07 e6 19 60 a5')
    assert b(0xB6A8, 12) == bytes.fromhex('20 73 b8 b0 01 60 20 85 e7 20 f7 b7')
    assert b(0xB64E, 6) == bytes.fromhex('20 73 b8 b0 01 60')
    loader = b(0xB873, 51)
    assert loader == bytes.fromhex(
        'ad a6 07 0a 18 6d a6 07 a8 b9 a6 b8 c9 ff f0 21 '
        '85 5f b9 a7 b8 85 5e b9 a8 b8 85 10 20 43 e8 '
        'a9 00 9d 00 03 e8 c6 10 d0 f8 20 6b e8 '
        'ee a6 07 18 60 38 60')
    descriptors = b(0xB8A6, 28)
    assert hashlib.sha256(descriptors).hexdigest() == DESCRIPTORS_SHA
    records = [descriptors[i*3:i*3+3].hex() for i in range(9)]
    assert all(descriptors[(3*n) & 0xFF] != 0xFF for n in range(9))
    assert descriptors[27] == 0xFF  # $07A6=9 -> Y=$1B -> sentinel

    return {
        'status': 'preliminary_0508_source_proof',
        'jp_rom_sha256': JP_SHA,
        'predecessor': 'fixed slot $0C -> $E51E sets bank $0A -> $AFA4',
        'predecessor_verified_entry': '$AFA4-$AFA8, five bytes',
        'encoded_predecessor_state_count': 20,
        'conditional_transition': '$19=$13 -> $B36B -> $18=$0D, $19=$00',
        'successor': 'fixed slot $0D -> $E526 sets bank $0A -> $B4CC',
        'gate': '$B873 indexes $B8A6 + ((3*$07A6)&$FF); $FF sets carry',
        'gate_data_records': records,
        'gate_sentinel_when_index_9': True,
        'unproven': [
            'live state selector $18=$0C and predecessor $19=$13',
            'cross-frame mutation and true $07A6 index domain',
            'callee mapper/state preservation across room loading',
            'whole-program pointer-table bounds'
        ],
        'strict_new_bytes': 0,
        'strict_cumulative_prg_bytes': 49404,
        'vpp': 24
    }


if __name__ == '__main__':
    if len(sys.argv) not in (2, 3):
        raise SystemExit('usage: audit_0508_predecessor.py JP.nes [report.json]')
    report = audit(sys.argv[1])
    if len(sys.argv) == 3:
        Path(sys.argv[2]).write_text(json.dumps(report, indent=2) + '\n')
    print('0508 preliminary JP ROM PASS')
    print('Conditional $18: $0C -> $0D through $19=$13; not live-proven')
    print('Room loader $07A6=9 local sentinel: PASS; global domain OPEN')
    print('Verified PRG floor unchanged: 49404, VPP 24')