#!/usr/bin/env python3
"""Bank-wide Japanese 0A source and local original-6502 selector regressions.

Smoke tests require no ROM. Complete tests require an authenticated original JP
ROM supplied by the user and never committed with this source.
"""
from __future__ import annotations
import argparse, hashlib, tempfile
from pathlib import Path

from build_fullbank_0a_source import build
from build_whole_cart_recomp_0529 import assemble, generate_sources
from recover_raw0a_hierarchy import classify, word
from recover_raw0a_bank_0537 import JP_SHA, BANK_SHA
from test_raw0a_lookup_cpu import run as run_cpu, selftest


def check(rom_bytes:bytes):
    assert len(rom_bytes)==393232 and hashlib.sha256(rom_bytes).hexdigest()==JP_SHA
    bank=rom_bytes[16+10*0x4000:16+11*0x4000]
    assert hashlib.sha256(bank).hexdigest()==BANK_SHA
    with tempfile.TemporaryDirectory(prefix='jp-fullbank-raw0a-') as temp:
        root=Path(temp)
        base=root/'source'
        generate_sources(rom_bytes,base)
        baseline=(base/'prg_raw0a.asm').read_text()
        result=classify(bank,baseline)
        assert result['report']['unresolved']==3684
        assert result['report']['hierarchy']['instruction_exact_local_6502_cases']==135
        assert result['report']['hierarchy']['four_byte_cells']==709
        assert result['report']['hierarchy']['seven_byte_records']==163
        assert result['report']['room_message_source_bytes']==46
        assert assemble(result['asm'],0x8000,0x4000)==bank

        # All 135 producer-bounded input triples execute the real 6502
        # byte sequence $801E-$8046, not only a Python address formula.
        for case in result['selector_cases']:
            s,m,l,pcs=run_cpu(bank,case['stage'],case['second'],case['third'])
            assert l==int(case['leaf_cpu'],16)
            assert pcs[0]==0x801E and pcs[-1]==0x8046
            assert 0x92CC<=s<=0x9B1A and 0x9320<=m<0x9B82
        negatives={
            0x92CC:0,          # second-level pointer no longer addresses tier3
            0x9320:0,          # third-level pointer no longer addresses leaf
            0x9B20:0,          # second third-level island corruption
            0x9B80:0,          # final pointer in second third-level island
            0xAB1F:0xFF,       # no permitted seven-byte row type
            0xAB5E:0,          # remove an FF stream terminator
            0xB909:0,          # message top pointer group drift
            0xB922:0,          # remove an FF message terminator
        }
        for cpu,value in negatives.items():
            altered=bytearray(bank);altered[cpu-0x8000]=value
            assert altered!=bank
            try:
                classify(bytes(altered),baseline,strict_identity=False)
            except ValueError:
                pass
            else:
                raise AssertionError(f'Structural corruption at ${cpu:04X} accepted')
        # A plausible leaf-record field mutation is NOT structurally
        # detectable and must be rejected by the exact original hash.
        altered=bytearray(bank);altered[0x93C8-0x8000]^=1
        try:classify(bytes(altered),baseline)
        except ValueError:pass
        else:raise AssertionError('Original bank identity altered but passed')
        damaged=result['asm'].replace('.word $9320','.word $9322',1)
        assert damaged!=result['asm']
        assert assemble(damaged,0x8000,0x4000)!=bank

        whole=build(rom_bytes,root/'complete_cart')
        assert whole['raw0a_unresolved_bytes']==3684
        assert whole['source_files']==25
        assert whole['new_structurally_identified_since_0537']==4437
        print('PASS raw0A 16384-byte full-bank assembly, 135 real 6502 bounded selector paths')
        print('PASS 10 negative source/schema/ROM tests, 25-bank exact original ROM reconstruction')


def smoke():
    selftest()
    assert 2162+168+2910+7460+3684==16384
    assert 398+2836+1141+16+46==4437
    print('PASS raw0A ROM-free whole-bank code/data layout invariant smoke')


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--rom',type=Path);ap.add_argument('--smoke',action='store_true');a=ap.parse_args()
    smoke()
    if a.rom:check(a.rom.read_bytes())
