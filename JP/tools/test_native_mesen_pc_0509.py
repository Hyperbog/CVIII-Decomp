#!/usr/bin/env python3
"""Pinned independent Mesen2 original-JP reset-PC prefix witness for native C++.

This is *not* a general CPU/PPU/IRQ/mapper parity claim. Mesen2 PC trace
was independently generated with --frames 0 --step 16000 --trace <private>.
At step 7829 the native PPU timing approximation diverges by one loop branch.
Only normalized PC SHA-256 and first 7828 states may be certified here.
"""
from __future__ import annotations
import argparse
import hashlib
import subprocess
import tempfile
from pathlib import Path

ROM_SHA = '958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
MESEN_VERSION = '2.1.1'
GOLDENS = {
    100: '82ed21d964962ba4ed1a5e225f96f747d335b84c4d1135a6acfe4c2b816b32e9',
    3000: '01b4fc177cf759b44dd6b90685ae8a0600409044e1f613da0afcdac8f23318d8',
    7828: 'ac29c14add24b11f8ca4355dc2c2f0a6feb16723502ad9ee33f196d7842e8402',
}

def digest_pc(lines: list[str], limit: int) -> str:
    if len(lines)<limit:raise ValueError('incomplete instruction trace')
    sequence=[]
    for line in lines[:limit]:
        pc=line.split(' ',1)[0]
        if len(pc)!=4 or any(ch not in '0123456789ABCDEF' for ch in pc):
            raise ValueError(f'invalid PC {pc!r}')
        sequence.append(pc)
    return hashlib.sha256(('\n'.join(sequence)+'\n').encode('ascii')).hexdigest()

def verify(native_program:Path,rom:Path)->dict:
    data=rom.read_bytes()
    if len(data)!=393232 or hashlib.sha256(data).hexdigest()!=ROM_SHA:
        raise ValueError('wrong original Japanese ROM')
    with tempfile.TemporaryDirectory(prefix='native-mesen0509-') as tmp:
        trace=Path(tmp)/'native.txt'
        child=subprocess.run([str(native_program),str(rom),'7828',str(trace)],
               capture_output=True,text=True,check=True,timeout=30)
        lines=trace.read_text().splitlines()
        actual={n:digest_pc(lines,n) for n in GOLDENS}
        for n,want in GOLDENS.items():
            assert actual[n]==want,(n,actual[n],want)
        assert 'NATIVE_2A03_HEADLESS_TEST steps=7828' in child.stdout
        return {'source':'independent Mesen2 v2.1.1 original-JP CPU PC trace',
            'golden_PC_prefix_states':7828,'native_PC_prefix_matches':7828,
            'reference_PC_hashes':actual,'ROM_identity_SHA256':ROM_SHA,
            'scope':'pre-vblank startup PC stream only; first divergence step 7829 due to modeled PPU vblank timing',
            'not_claimed':['gameplay native frame parity','playable PC port','general 2A03 timing parity',
               'mapper IRQ cycle parity','audio parity','new strict JP PRG bytes'],
            'strict_verified_PRG_bytes':49504,'VPP':26}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('native_program',type=Path);p.add_argument('JP_ROM',type=Path)
    a=p.parse_args();r=verify(a.native_program,a.JP_ROM)
    print('PASS native independent Mesen original-JP startup PC prefix',r['native_PC_prefix_matches'],'instructions')
