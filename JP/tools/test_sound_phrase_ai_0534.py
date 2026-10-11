#!/usr/bin/env python3
"""0534 original JP ROM / source reassembly / independent tamper gates.

ROM-free --smoke works in GitHub CI, --rom authenticates every generated bank
against the user's own 393,232-byte original retail Japanese ROM.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import tempfile
import build_whole_cart_recomp_0529 as cart
import lift_sound_phrase_ai_0534 as stage


def reject(f,label):
    try:f()
    except (ValueError,AssertionError):return
    raise AssertionError('0534 source accepted altered original evidence: '+label)


def main(path=None):
    stage.smoke();cart.smoke()
    if path is None:
        print('PASS 0534 ROM-free source contract and 6502 assembler smoke')
        return
    rom=Path(path).read_bytes()
    if len(rom)!=393232 or cart.digest(rom)!=cart.proof.ROM_SHA:
        raise ValueError('Original Japanese Akumajou Densetsu ROM identity mismatch')
    prg=rom[16:16+262144]
    files,stats=stage.source(prg)
    if ({key:sum(x['b']-x['a'] for x in part) for key,part in files.items()}
        != {'raw0B':229,'fixed31':347,'raw0C':1619}):
        raise ValueError('0534 audited 0504 source plus phrase-source footprints drift')
    if (stats['new_0504_6502_instruction_operand_bytes'],
        stats['new_0504_typed_table_bytes'],
        stats['sound_table_entries'],
        stats['sound_phrase_distinct_roots'])!=(504,72,148,140):
        raise ValueError('0534 original-JP graph and pointer structure drift')
    # Independently change source ROM bytes before reclassification, not the
    # generator's output, to verify real fingerprints rather than bookkeeping.
    for bank,address,reason in (
        (12,0x8b32,'original indexed table consumer A304'),
        (12,0xa304,'original phrase pointer table A304'),
        (12,0xa404,'original phrase pointer subtable A404'),
        (12,0xa500,'original phrase stream'),
        (12,0xa956,'last producer-associated terminated phrase'),
        (11,0x8519,'0504 raw0B original AI code'),
        (11,0x968c,'0504 bounded indexed AI data'),
        (31,0xfc1f,'0504 fixed31 original AI opcode graph'),
        (31,0xfd4d,'0504 fixed31 bounded AI table'),
    ):
        mutated=bytearray(prg)
        base=bank*(8192 if bank==31 else 16384)
        offset=(address-0xe000 if bank==31 else address-0x8000)
        mutated[base+offset]^=1
        reject(lambda:stage.source(bytes(mutated)),reason)
    with tempfile.TemporaryDirectory(prefix='jp0534-') as temp:
        report=cart.generate_sources(rom,Path(temp))
        if (report['total_prg_classified_code_table_and_script_bytes'],
            report['symbolic_6502_instruction_bytes'],
            report['unclassified_prg_bytes'],
            report['bank0c_secondary_phrase_table_and_pool_bytes'])!=(50846,14978,211298,1619):
            raise ValueError('0534 exact ROM round-trip manifest mismatch')
    print('PASS 0534 exact original-JP ROM 25-bank 393232-byte recompilation; 9 negative source mutations')


if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--rom',type=Path)
    args=a.parse_args()
    main(args.rom)
