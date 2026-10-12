#!/usr/bin/env python3
"""ROM-free integrity tests for optional NESRecomp mapper24 cycle probe."""
from __future__ import annotations
import tempfile,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from probe_nesrecomp_cycle_0566 import mapper_header,authenticate
def main():
    h=bytearray(16);h[:4]=b'NES\x1a';h[6]=0x80;h[7]=0x10
    assert mapper_header(h)==24
    h[6]=0x90;assert mapper_header(h)==25
    h[0]=0
    try:mapper_header(h)
    except ValueError:pass
    else:raise AssertionError('non-iNES header accepted')
    with tempfile.TemporaryDirectory(prefix='jp0566-mapper-') as root:
        f=Path(root)/'short.nes';f.write_bytes(b'NES\x1a')
        try:authenticate(f)
        except ValueError:pass
        else:raise AssertionError('short private original incorrectly accepted')
    print('PASS JP0566 mapper24/25 identification and SHA-required fail-closed gate')
if __name__=='__main__':main()
