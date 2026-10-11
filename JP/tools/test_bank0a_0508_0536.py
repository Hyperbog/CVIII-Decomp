#!/usr/bin/env python3
"""0536 ROM-free + original-JP bank0A/0E conditional mapper-source audits.

The ROM-backed gate verifies SHA-locked control-flow instructions, inline
pointer tables, and 5 structured bank0E object streams, then independently
reassembles the entire original cartridge from 25 bank ASM sources.
Mapper-selected entrypoints are proven encodings; frame liveness and $07A0
index bounds are NOT certified.
"""
import argparse
from pathlib import Path
import tempfile
import build_whole_cart_recomp_0529 as cart
import lift_bank0a_state_0535 as previous
import lift_bank0a_0508_0536 as stage


def reject(fn,what):
    try:fn()
    except (ValueError,AssertionError):return
    raise AssertionError('Tampered original JP 0536 source accepted: '+what)


def check(image=None):
    stage.smoke()
    if image is None:
        print('PASS 0536 ROM-free mapper-aware source and table schema')
        return
    rom=Path(image).read_bytes()
    if len(rom)!=393232 or cart.digest(rom)!=stage.ROM_SHA:
        raise ValueError('Only original Japanese NES ROM is an accepted reference')
    prg=rom[16:16+262144]
    prev,_=previous.classify(prg)
    taken=set(a for f in prev['raw0A'] for a in range(f['a'],f['b']))
    classified,report=stage.lift(prg,taken)
    if (report['original_0508_graph_instruction_count'],
        report['original_0508_graph_opcode_bytes'],
        report['new_instruction_count'],
        report['new_instruction_bytes'],
        report['new_inline_pointer_bytes'],
        report['new_descriptor_pointer_bytes'],
        report['bank0E_mapper_read_stream_bytes'],
        report['bank0E_object_count'],
        report['new_total_classified_bytes'])!=(935,2042,691,1540,106,38,175,30,1859):
        raise ValueError('0536 byte or source-graph accounting changed')
    if sum(f['b']-f['a'] for r in classified.values() for f in r)!=1859:
        raise ValueError('0536 original source fragments duplicate old classification')
    for bank,addr,name in ((10,0xafa4,'fixed-bank selected room entry'),
                           (10,0xafa9,'first inline dispatch word'),
                           (10,0xb125,'second inline dispatch word'),
                           (10,0xb68e,'fourth inline dispatch word'),
                           (10,0xb8a6,'room ID descriptor'),
                           (10,0xb8c2,'five-stream mapper pointer'),
                           (14,0xbe8b,'first stream header'),
                           (14,0xbea7,'ten-object stream record'),
                           (14,0xbf39,'final stream sentinel'),
                           (31,0xe51e,'fixed mapper write caller')):
        bad=bytearray(prg)
        base=31*8192 if bank==31 else bank*16384
        bad[base+addr-(0xe000 if bank==31 else 0x8000)]^=1
        reject(lambda:stage.lift(bytes(bad),taken),name)
    with tempfile.TemporaryDirectory(prefix='jp0536-') as tmp:
        m=cart.generate_sources(rom,tmp)
        expected=(52705,16518,2670,209439,25)
        actual=(m['total_prg_classified_code_table_and_script_bytes'],
                m['symbolic_6502_instruction_bytes'],
                m['total_dispatch_parser_and_sound_metadata_bytes'],
                m['unclassified_prg_bytes'],m['source_files'])
        if actual!=expected:raise AssertionError((actual,expected))
    print('PASS 0536 exact original JP 393232-byte 25-bank recompilation; 10 tamper negatives')


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--rom',type=Path);a=ap.parse_args()
    check(a.rom)
