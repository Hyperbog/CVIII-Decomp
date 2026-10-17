#!/usr/bin/env python3
"""Negative and positive SHA-pinned sound-bank source tests, original ROM optional."""
from __future__ import annotations
import argparse
from pathlib import Path
import lift_bank04_parser_0532 as proof
import build_whole_cart_recomp_0529 as generator

def expect_rejection(callback, label):
    try:callback()
    except (ValueError, AssertionError):return
    raise AssertionError('Corrupted original sound source unexpectedly accepted: '+label)

def tests(rom):
    proof.smoke()
    generator.smoke()
    if rom is None:return
    image=Path(rom).read_bytes()
    if len(image)!=393232 or generator.digest(image)!=generator.proof.ROM_SHA:
        raise ValueError('Wrong original JP ROM for 0532 test')
    prg=image[16:16+262144]
    fragments,report=proof.lift(prg)
    assert report['newly_classified_source_bytes']==19927
    assert report['per_parser_instruction_starts']==786
    assert report['per_parser_opcode_operand_bytes']==1716
    assert report['per_parser_lookup_and_local_data_bytes']==249
    assert [len(fragments[f'raw{b:02X}']) for b in (4,5,12)]==[2,1,1]
    damaged=bytearray(prg)
    damaged[4*16384+0x9000-0x8000]^=1
    expect_rejection(lambda:proof.lift(bytes(damaged)),'04F7 command hash')
    damaged=bytearray(prg)
    damaged[5*16384+0x8100-0x8000]^=1
    expect_rejection(lambda:proof.lift(bytes(damaged)),'bank05 parser correspondence')
    damaged=bytearray(prg)
    damaged[12*16384+0x8f60-0x8000+(90-1)*2]^=1
    expect_rejection(lambda:proof.lift(bytes(damaged)),'raw0C metadata source reference')
    fake=bytearray(image);fake[100]^=1
    expect_rejection(lambda:generator.generate_sources(bytes(fake),Path('/tmp/should-not-exist-0532')),'wrong full-ROM identity')
    print('PASS four original-ROM negative controls and 786-instruction source provenance')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path)
    a=p.parse_args()
    tests(a.rom)
