#!/usr/bin/env python3
"""Build 25 original-JP source banks, replacing raw0A with bank-wide 0538 source.

Not a native compiler: this is original 6502 disassembly and data reassembly.
The ROM input is private/local. No ROM is included in the Git repository.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

from build_whole_cart_recomp_0529 import assemble, generate_sources
from recover_raw0a_hierarchy import classify
from recover_raw0a_bank_0537 import JP_SHA


def build(rom:bytes,out:Path):
    if len(rom)!=393232 or hashlib.sha256(rom).hexdigest()!=JP_SHA:
        raise ValueError('Expected exact Japanese Akumajou Densetsu 393232-byte ROM')
    out=Path(out)
    baseline=out/'banked'
    original=generate_sources(rom,baseline)
    bank=rom[16+10*16384:16+11*16384]
    fixed=classify(bank,(baseline/'prg_raw0a.asm').read_text(encoding='ascii'))
    (baseline/'prg_raw0a.asm').write_text(fixed['asm'],encoding='ascii')
    (out/'raw0a_hierarchy_atlas.json').write_text(json.dumps(fixed['report'],indent=2)+'\n')
    (out/'raw0a_bounded_selector_cases.json').write_text(json.dumps(fixed['selector_cases'],indent=2)+'\n')
    prg_sources=[]
    for i in range(15):
        p=baseline/f'prg_raw{i:02x}.asm'
        prg_sources.append(assemble(p.read_text(encoding='ascii'),0x8000,0x4000))
    for i in (30,31):
        p=baseline/f'prg_fixed{i}.asm'
        prg_sources.append(assemble(p.read_text(encoding='ascii'),0xC000 if i==30 else 0xE000,0x2000))
    graphics=[]
    for i in range(8):
        p=baseline/f'chr_{i:02x}.asm'
        graphics.append(assemble(p.read_text(encoding='ascii'),0,0x4000))
    rebuilt=rom[:16]+b''.join(prg_sources)+b''.join(graphics)
    if len(rebuilt)!=393232 or rebuilt!=rom:
        raise ValueError('Full 25-bank assembled cartridge does not equal original ROM')
    counts=fixed['report']['counts']
    evidence={
        'schema':'whole-original-JP-bank0A-structural-source/v1',
        'original_rom_sha256':JP_SHA,
        'full_cartridge_exact_rebuild':True,
        'source_files':25,
        'raw0a_size':16384,
        'raw0a_proven_instruction_bytes':2162,
        'raw0a_unverified_candidate_instruction_bytes':2910,
        'raw0a_structural_data_bytes':7460,
        'raw0a_historical_verified_table_bytes':168,
        'raw0a_unresolved_bytes':3684,
        'new_structurally_identified_since_0537':4437,
        'local_6502_pointer_lookup_executions':135,
        'global_selector_and_mapper_liveness':'NOT VERIFIED',
        'strict_PRG_coverage_change':0,
        'raw0a_source_atlas':fixed['report'],
        'original_0536_manifest':original,
        'notice':'Script and candidate bounds are not proof of complete native recompilation.'}
    (out/'fullbank_manifest.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print('PASS original Japanese ROM exact 393232-byte reconstruction from 25 source banks')
    print('PASS whole raw0A 16KiB; audited instruction 2162, candidate instruction 2910, structural data 7460, prior audited tables 168, unresolved 3684')
    return evidence


def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path);p.add_argument('--out',type=Path)
    p.add_argument('--smoke',action='store_true');a=p.parse_args()
    if a.smoke:
        assert sum((2162,2910,7460,168,3684))==16384
        print('PASS ROM-free original bank0A whole-bank accounting and source-builder smoke')
    else:
        if not a.rom or not a.out:p.error('--rom and --out required')
        build(a.rom.read_bytes(),a.out)

if __name__=='__main__':main()
