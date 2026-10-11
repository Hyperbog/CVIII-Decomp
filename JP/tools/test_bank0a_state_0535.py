#!/usr/bin/env python3
"""0535 authenticated JP bank0A and structural bank0C source regression.

ROM-free test runs in CI; ROM-backed checks true independent original-image
source classification, corruption resistance and complete 25-bank roundtrip.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import tempfile
import lift_bank0a_state_0535 as stage
import build_whole_cart_recomp_0529 as cart


def must_reject(fn,name):
    try:fn()
    except (ValueError,AssertionError):return
    raise AssertionError('Accepted original-JP input corruption: '+name)


def main(rom_file=None):
    stage.smoke()
    if rom_file is None:
        print('PASS 0535 ROM-free rooted-state machine smoke')
        return
    image=Path(rom_file).read_bytes()
    if len(image)!=393232 or cart.digest(image)!=stage.ORIGINAL_ROM_SHA:
        raise ValueError('Expected original Japanese commercial ROM identity')
    prg=image[16:16+262144]
    result,report=stage.classify(prg)
    if (report['bank0A_state_instructions'],report['bank0A_state_instruction_bytes'],
        report['bank0A_state_table_bytes'],report['bank0C_structural_helper_instruction_bytes'],
        report['bank0C_structural_lookup_table_bytes'],report['classified_additional_bytes'])!=\
       (244,502,24,79,18,623):
        raise ValueError('0535 precise original instruction/table census changed')
    if (sum(x['b']-x['a'] for x in result['raw0A']),
        sum(x['b']-x['a'] for x in result['raw0C']))!=(526,97):
        raise ValueError('0535 physical fragment occupancy changed')
    # Target each authenticated graph/producer/table and two crossbank roots.
    for k,a,reason in (
        (10,0xb49a,'0506 state-handler branch'),
        (10,0xb4cc,'0506 original selector producer'),
        (10,0xb4d1,'12-word state table'),
        (10,0xb689,'bank0A state $68 selector'),
        (10,0xb7f7,'bank0A $B7F7 loader'),
        (12,0xa992,'bank0C loop helper opcode'),
        (12,0xa9d5,'bank0C fixed-caller helper'),
        (12,0xa9e7,'bank0C helper lookup table'),
        (1,0xab88,'raw01 direct JSR to bank0C candidate'),
        (31,0xe39c,'fixed-side JSR to bank0C candidate'),
    ):
        bad=bytearray(prg)
        pos=k*(8192 if k==31 else 16384)+(a-(0xe000 if k==31 else 0x8000))
        bad[pos]^=1
        must_reject(lambda:stage.classify(bytes(bad)),reason)
    with tempfile.TemporaryDirectory(prefix='jp0535-') as temp:
        manifest=cart.generate_sources(image,Path(temp))
        actual=(manifest['total_prg_classified_code_table_and_script_bytes'],
                manifest['symbolic_6502_instruction_bytes'],
                manifest['total_dispatch_parser_and_sound_metadata_bytes'],
                manifest['unclassified_prg_bytes'])
        if actual!=(50846,14978,2526,211298):
            raise ValueError('0535 whole-cartridge source counts changed: '+str(actual))
    print('PASS 0535 original-JP ROM 393232-byte exact recompilation and 10 mutation negatives')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path);a=p.parse_args()
    main(a.rom)
