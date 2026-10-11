#!/usr/bin/env python3
"""Original JP ROM identity and physical source provenance for 0522."""
import argparse
import hashlib
from pathlib import Path
ROM_SHA = '958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
SPANS = {
    'fixed_E2D0_E2D5': (0x03E2D0, 0x03E2D6,
        '8d1a2898917458f00a455757ee9471327e1d4f51bee3d841d98e23055fb51380'),
    'fixed_FE63_FE75': (0x03FE63, 0x03FE76,
        'bfe287c26149b305403019d54a537ab15137c4a46933803ddc82e8e6f291631e'),
    'raw0B_8161_81B1': (0x02C161, 0x02C1B2,
        'ea381a34b2fe3df6c5b2c4fc40f89aaab3fe421de3d49a6852f00663195b5728'),
    'raw0B_826C_8281': (0x02C26C, 0x02C282,
        '210667cf666f4bec07e356c74ee535bdb1303568600aadf9c4bcad7d215511e2'),
}
def verify(path: Path):
    data = path.read_bytes()
    assert len(data) == 0x60010, 'unexpected iNES ROM length'
    assert data[:4] == b'NES\x1a', 'not an iNES ROM'
    assert data[4:6] == bytes([16, 16]), 'unexpected PRG/CHR configuration'
    assert ((data[6] >> 4) | (data[7] & 0xf0)) == 24, 'not VRC6 mapper 24'
    digest = hashlib.sha256(data).hexdigest()
    assert digest == ROM_SHA, f'JP identity mismatch: {digest}'
    prg = data[16:16 + 0x40000]
    for name, (start, end, expected) in SPANS.items():
        actual = hashlib.sha256(prg[start:end]).hexdigest()
        assert actual == expected, f'{name} mismatch: {actual}'
        print(f'PASS {name}: {end-start} bytes at PRG 0x{start:06X}')
    print('PASS original JP 0522 physical source provenance')
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('rom', type=Path)
    verify(parser.parse_args().rom)
