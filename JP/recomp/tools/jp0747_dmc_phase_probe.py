#!/usr/bin/env python3
"""ROM-free pinned-source DMC initial timer phase A/B probe; NOT certified."""
from __future__ import annotations
import argparse
from pathlib import Path

START='    apu.dmc_timer = 1022;'

def patch(src,offset):
    if offset not in (52,54,56):raise ValueError('JP0747 unsupported phase probe')
    if src.count(START)!=1:raise ValueError('pinned NESRecomp DMC power-on timer anchor missing')
    return src.replace(START,
       f'    apu.dmc_timer = {1022+offset}; /* JP0747 bounded DMC phase probe +{offset} */',1)

def smoke():
    for offset in (52,54,56):
        assert f'{1022+offset}' in patch(START,offset)
    try:patch(START,53)
    except ValueError:pass
    else:raise AssertionError('unverified odd phase accepted')
    print('PASS JP0747 ROM-free source-pinned DMC timer phase probe')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--smoke',action='store_true')
    p.add_argument('--apu',type=Path)
    p.add_argument('--output',type=Path)
    p.add_argument('--offset',type=int)
    a=p.parse_args()
    if a.smoke:smoke();return
    if not(a.apu and a.output and a.offset is not None):
        p.error('--apu --output --offset required')
    if a.apu.resolve()==a.output.resolve():raise ValueError('upstream in-place rewrite')
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(patch(a.apu.read_text(encoding='utf8'),a.offset),encoding='utf8')

if __name__=='__main__':main()
