#!/usr/bin/env python3
"""Original 0523 raw-bank $0B $8193 source and fixed-context check."""
import argparse
import hashlib
from pathlib import Path

ORIGINAL_SHA = '958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
RESET_SHA = '0b9f9559ee19ffcdb30d51a70bb887aa7f5430b648f886eb5a261987e3989ed2'

def verify(path):
    rom=Path(path).read_bytes()
    assert len(rom)==393232 and hashlib.sha256(rom).hexdigest()==ORIGINAL_SHA, 'incorrect original JP ROM'
    prg=rom[16:16+0x40000]
    src=prg[0x02c193:0x02c1a9]
    assert hashlib.sha256(src).hexdigest()==RESET_SHA, 'original bank0B $8193-$81A8 changed'
    assert src==bytes.fromhex('BD 4E 05 C9 4D F0 18 A9 00 9D 4E 05 9D 70 04 9D 00 04 9D EF 05 60')
    # The $8198 BEQ +$18 targets $81B2, outside the lifted return path.
    assert 0x819a + (src[6] if src[6]<0x80 else src[6]-256)==0x81b2
    print('PASS original JP raw0B $8193-$81A8 source, BEQ->$81B2 preserved; no certification')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('rom');args=p.parse_args();verify(args.rom)
