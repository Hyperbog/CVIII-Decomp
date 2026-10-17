#!/usr/bin/env python3
"""ROM-locked 0508 follow-up: NMI predecessor and room-loader conditional proof.

Usage: python3 audit_0508_phase2.py 'Akumajou Densetsu (Japan).nes' [report.json]
Scope: original JP ROM bytes, mapped CPU windows, E7FB pointer-fetch/flag
contract, and exact direct-encoding scans. NO runtime liveness inference.
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import hashlib
import json
import sys

ROM_SHA = '958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
BEFORE_SHA = 'e4fa5e06e439ca12a84d935eb80224f448276c722399fe76fe0ce60013cc4ee7'
FRONT_SHA = 'a5437f0f20034ba34d65afeec353d28846a321134061f765814d28eaa3f69157'
ENTRY_SHA = '0cbfd39d34523da29edaa6a2dcf5cdb4b62de628d0e5568ea3879d7de5a1c0c7'
TABLE_AFA9_SHA = '422e65c2a5a5c30ea2e6a7c77978d54c2d1cd64b99628e7f94662a29f9f7d396'


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def audit(rom_path: str) -> dict:
    rom = Path(rom_path).read_bytes()
    assert len(rom) == 393232 and digest(rom) == ROM_SHA
    assert rom[:16] == bytes.fromhex('4E 45 53 1A 10 10 80 10 00 00 00 00 00 00 00 00')
    prg = rom[16:0x40010]
    assert len(prg) == 0x40000
    bank0a = prg[0x0A*0x4000:0x0B*0x4000]
    fixed = prg[31*0x2000:32*0x2000]
    f = lambda a, n: fixed[a-0xE000:a-0xE000+n]
    b = lambda a, n: bank0a[a-0x8000:a-0x8000+n]
    word = lambda a: int.from_bytes(b(a, 2), 'little')
    assert digest(f(0xFB76, 32)) == BEFORE_SHA
    assert digest(f(0xFB96, 32)) == FRONT_SHA

    # CPU fixed-bank trampoline / NMI first-level inline data.
    assert f(0xE35C, 7) == bytes.fromhex('E6 1B A5 18 20 FB E7')
    assert f(0xE2D0, 6) == bytes.fromhex('85 23 8D 00 80 60')
    fixed_paths = {}
    for selector, at, destination in ((0x0C, 0xE51E, 0xAFA4),
                                      (0x0D, 0xE526, 0xB4CC)):
        ptr = int.from_bytes(f(0xE363 + 2*selector, 2), 'little')
        assert ptr == at
        assert f(at, 8) == bytes([0xA9, 0x0A, 0x20, 0xD0, 0xE2,
                                 0x4C, destination&0xFF, destination>>8])
        assert b(destination, 5) == bytes.fromhex('A5 19 20 FB E7')
        assert digest(b(destination, 5)) == ENTRY_SHA
        prg_off = 0x0A*0x4000 + destination - 0x8000
        fixed_paths[f'{selector:02X}'] = {
            'cpu_trampoline': f'{at:04X}',
            'raw_bank': '0A',
            'target_cpu': f'{destination:04X}',
            'target_physical_8k_prg': prg_off//0x2000,
            'target_prg_offset': f'{prg_off:05X}',
            'target_rom_file_offset': f'{prg_off+16:05X}',
            'entry_sha256': ENTRY_SHA,
            'note': 'mapped edge is exact; selector liveness remains unproved'
        }
    assert digest(b(0xAFA9, 40)) == TABLE_AFA9_SHA
    assert word(0xAFA9 + 2*0x13) == 0xB36B
    assert b(0xB36B, 15) == bytes.fromhex(
        'AD 89 07 8D 81 07 A9 0D 85 18 A9 00 85 19 60')

    # Earlier 0507 room-state transition; no implicit claim that indices run.
    assert b(0xB4CC, 5) == bytes.fromhex('A5 19 20 FB E7')
    assert word(0xB4D1+2*1) == 0xB58C
    assert word(0xB4D1+2*2) == 0xB597
    assert b(0xB58C, 11) == bytes.fromhex('A9 6B 20 49 E2 20 E9 B4 E6 19 60')
    assert b(0xB4E9, 5) == bytes.fromhex('A9 00 85 68 60')
    assert b(0xB597, 12) == bytes.fromhex('20 89 B6 A5 68 C9 FF D0 02 E6 19 60')
    assert word(0xB68E) == 0xB6A4
    assert b(0xB6A4, 16) == bytes.fromhex(
        'A9 02 85 1D 20 73 B8 B0 01 60 20 85 E7 20 F7 B7')

    # 07A6 is converted into uint8_t(3*value) for record indexing.
    assert b(0xB873, 23) == bytes.fromhex(
        'AD A6 07 0A 18 6D A6 07 A8 B9 A6 B8 C9 FF F0 21 '
        '85 5F B9 A7 B8 85 5E')
    assert b(0xB88A, 8) == bytes.fromhex('B9 A8 B8 85 10 20 43 E8')
    assert b(0xB898, 14) == bytes.fromhex(
        'C6 10 D0 F8 20 6B E8 EE A6 07 18 60 38 60')
    records = [b(0xB8A6 + 3*i, 3) for i in range(9)]
    assert [r.hex() for r in records] == [
        '24c040', '250040', '254040', '258040', '25c040',
        '260040', '264040', '268040', '26c040']
    sentinel = b(0xB8C1, 1)[0]
    assert sentinel == 0xFF
    for i in range(10):
        y = (3*i)&0xFF
        value = b(0xB8A6+y, 1)[0]
        assert (value == 0xFF) == (i == 9), (i, value)
    assert b(0xB7DE, 5) == bytes.fromhex('A9 00 8D A6 07')
    assert b(0xB626, 5) == bytes.fromhex('A9 00 8D A6 07')

    # Exact byte-aligned whole-PRG direct write patterns: CANDIDATES only.
    # Other absolute-indexed / indirect / PPU writes and instruction boundaries
    # are NOT ruled out by these counts.
    patterns = {'STA_abs':bytes([0x8D]), 'STX_abs':bytes([0x8E]),
                'STY_abs':bytes([0x8C]), 'INC_abs':bytes([0xEE]),
                'DEC_abs':bytes([0xCE]), 'ASL_abs':bytes([0x0E]),
                'LSR_abs':bytes([0x4E]), 'ROL_abs':bytes([0x2E]),
                'ROR_abs':bytes([0x6E])}
    direct = {}
    for addr in (0x07A6, 0x07A0):
        hits = []
        for physical in range(32):
            region_start = physical*0x2000
            # Scan every physical start, including the final two bytes of
            # each 8 KiB chunk. A candidate crossing a chunk boundary
            # would still need independent CPU mapper-contiguity proof.
            for o in range(0x2000):
                pos = region_start + o
                if pos + 3 > len(prg):
                    continue
                if prg[pos+1:pos+3] != addr.to_bytes(2, 'little'):
                    continue
                for name, opc in patterns.items():
                    if prg[pos:pos+1] == opc:
                        cpu = (0xE000 if physical == 31 else 0x8000+(physical%2)*0x2000)+o
                        hits.append({'physical_prg_bank':physical,
                                     'candidate_cpu':f'{cpu:04X}', 'opcode':name})
        direct[f'{addr:04X}'] = hits
    assert direct['07A6'] == [
        {'physical_prg_bank':21,'candidate_cpu':'B628','opcode':'STA_abs'},
        {'physical_prg_bank':21,'candidate_cpu':'B7E0','opcode':'STA_abs'},
        {'physical_prg_bank':21,'candidate_cpu':'B89F','opcode':'INC_abs'}]
    assert len(direct['07A0']) == 3

    # Model E7FB's 8-bit ASL/selector alias and final restored-Y flags for
    # all input combinations; CPU BUS FETCH ONLY, no native CPU execution.
    dispatches = [(0xAFA6,0xAFA9,20),(0xB122,0xB125,22),
                  (0xB4CE,0xB4D1,12),(0xB68B,0xB68E,11)]
    dispatch_report=[]
    for jsr, base, count in dispatches:
        assert b(jsr,3)==bytes.fromhex('20 FB E7')
        arr=[word(base+2*i) for i in range(count)]
        assert all(0x8000<=t<0xC000 for t in arr)
        for a in range(256):
            off=(a<<1)&0xFF
            # E7FB first INY uses Y=(2*A+1)&FF; second INY is
            # 8-bit too. At selector 7F/FF it wraps to 00 and fetches
            # the opcode operand at JSR+2 rather than adjacent hi data.
            lowaddr=(jsr+2)+((off+1)&0xFF)
            highaddr=(jsr+2)+((off+2)&0xFF)
            target=b(lowaddr,1)[0] | (b(highaddr,1)[0]<<8)
            assert target==(b((jsr+2)+((2*(a&0x7F)+1)&255),1)[0] |
                           (b((jsr+2)+((2*(a&0x7F)+2)&255),1)[0]<<8))
            if (a&0x7F)!=0x7F:assert target==word(base+off)
            else:assert highaddr==jsr+2 and target!=word(base+off)
            carry=(a>>7)&1
            for saved_y in range(256):
                # Final LDY $03 determines final N,Z; A retains pointer-high.
                nz=((saved_y==0), bool(saved_y&0x80))
                assert (bool(carry),*nz)==(a>=0x80,saved_y==0,saved_y>=128)
        dispatch_report.append({
            'jsr_cpu':f'{jsr:04X}','table_cpu':f'{base:04X}',
            'encoded_word_count':count,
            'encoded_data_sha256':digest(b(base,2*count)),
            'first_out_of_width_pointer_word':f'{word(base+2*count):04X}',
            'selector_80_aliases_00':True,
            'selector_7F_8bit_INY_wrap_high_byte_cpu':f'{jsr+2:04X}',
            'selector_7F_correct_destination':f'{b((jsr+2)+255,1)[0] | (b(jsr+2,1)[0]<<8):04X}',
            'cases_checked':65536,
            'liveness':'unknown; arithmetic can index beyond encoded words'
        })

    # B873 can overwrite $10 and its $10 decrement loop; final value
    # after later external fixed helpers is NOT proved by local bytes.
    assert b(0xB88D, 3)==bytes.fromhex('85 10 20')
    return {
        'status':'0508_PHASE2_LOCAL_AUDIT_PASS_NO_COMMIT',
        'jp_rom_sha256':ROM_SHA,
        'recovery_overlap_sha256':BEFORE_SHA,
        'recovery_frontier_sha256':FRONT_SHA,
        'nmi_trampoline_edges':fixed_paths,
        'conditional_predecessor':{'selector_19':'13','target':'B36B',
                                   'next_selector_18':'0D','next_19':'00',
                                   'current_selector_liveness':'UNPROVED'},
        'room_sentinel':{'07A6_initializers':['B628','B7E0'],
                         'incrementer':'B89F','record_start':'B8A6',
                         'record_count_before_sentinel':9,
                         'record_hex':[r.hex().upper() for r in records],
                         'sentinel_address':'B8C1',
                         'index9_carry_out':True,
                         'global_07A6_bound':'UNPROVED'},
        'room_zp10':{'record_value_store':'B88D: STA $10',
                     'countdown_write':'B898: DEC $10',
                     'fixed_external_calls':['E843','E86B'],
                     'final_renderer_value':'UNPROVED'},
        'whole_prg_direct_encoding_candidates':direct,
        'e7fb_partial_math':dispatch_report,
        'e7fb_partial_math_total_cases':sum(x['cases_checked'] for x in dispatch_report),
        'physical_prg_bytes_swept':262144,
        'strict_0508_new_entry_eligible_bytes':5,
        'strict_0508_bytes_committed':0,
        'strict_floor_unchanged':49404,
        'vpp_unchanged':24,
        'blocking_dependencies':['full $18/$19 and $68 producer liveness',
            'mapper/callee state and indexed-write alias closure',
            '$07A0 / $07A6 full producer ranges',
            'original repo 0507 native test and full recovery checker',
            'preservation archive/progress/resume-state transaction']
    }


if __name__ == '__main__':
    if len(sys.argv) not in (2,3):
        sys.exit('usage: audit_0508_phase2.py JP.nes [report.json]')
    report=audit(sys.argv[1])
    if len(sys.argv)==3:
        Path(sys.argv[2]).write_text(json.dumps(report,indent=2)+'\n')
    print('0508 phase-2 ROM-locked independent audit: PASS')
    print('direct 07A6 writer candidates:',len(report['whole_prg_direct_encoding_candidates']['07A6']))
    print('partial E7FB tests:',report['e7fb_partial_math_total_cases'])
    print('strict coverage committed: 0; prior floor 49,404; VPP 24')
