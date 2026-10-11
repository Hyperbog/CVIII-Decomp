#!/usr/bin/env python3
"""Bank0C sound metadata/recomp regression: authenticated original JP source.

Runs ROM-free on GitHub; pass --rom to verify authentic mapper24 JP ROM,
full 25-bank exact assembly, and independent corruption rejection cases.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import tempfile
import build_whole_cart_recomp_0529 as cart
import lift_bank0c_sound_0533 as sound


def rejection(callable_,label):
    try:callable_()
    except (ValueError,AssertionError):return
    raise AssertionError('Tampered original source was not rejected: '+label)


def test(rom=None):
    cart.smoke();sound.smoke()
    if not rom:return
    data=Path(rom).read_bytes()
    if len(data)!=393232 or cart.digest(data)!=cart.proof.ROM_SHA:
        raise ValueError('Only original Japanese Akumajou Densetsu ROM accepted')
    prg=data[16:16+262144]
    regions,stats=sound.classify(prg)
    if sum(r['b']-r['a'] for r in regions)!=6627 or len(regions)!=8:
        raise ValueError('Bank0C source interval partition drift')
    if (stats['source_interpreter_instructions'],stats['source_interpreter_6502_opcode_operand_bytes'])!=(702,1599):
        raise ValueError('Bounded 04F5 NMOS code graph drift')
    if (stats['original_sound_header_count'],stats['original_sound_producer_ref_count'])!=(125,325):
        raise ValueError('Sound descriptor producer-domain drift')
    for address,label in ((0x8b6b,'04F5 authenticated interpreter'),
                          (0x8f60,'sound index'),
                          (0x9400,'original descriptor'),
                          (0xa303,'last producer sound root')):
        modified=bytearray(prg)
        modified[12*16384+address-0x8000]^=0x01
        rejection(lambda:sound.classify(bytes(modified)),label)
    with tempfile.TemporaryDirectory(prefix='c3jp-0533-') as folder:
        manifest=cart.generate_sources(data,Path(folder))
    if (manifest['total_prg_classified_code_table_and_script_bytes'],
        manifest['unclassified_prg_bytes'],
        manifest['symbolic_6502_instruction_bytes'])!=(50846,211298,14978):
        raise ValueError('0533 bank0C source remains integrated into 0535 whole cart')
    print('PASS original JP ROM 0533 25-bank exact recomp, 6627 new classified bytes, 4 tampering tests')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path)
    args=p.parse_args()
    test(args.rom)
