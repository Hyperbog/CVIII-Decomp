#!/usr/bin/env python3
"""Recover 04FE/04FF strict physical PRG source intervals from original git.

This is *not* a new coverage certificate: the reconstructed locations are
already part of the reported 49,504 bytes. It makes physical overlap tests
possible. The remaining pre-04FE baseline MUST NOT be assumed disjoint.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM_SHA = '958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
N = 262144
# 04FE original evidence preserved in JP/decomp/analysis/RESUME_STATE.json at
# git 78896c70544bdf926c3f97d29013995a261e1e1a
HIST_04FE = [
 ('E366','E434','b1bb37d98f9d0c9992ec2c9bc0c8a99cb3a1a2db8eb9359ecdc686ed1a7d6f46'),
 ('E436','E577','faa4c0e4033694f4e0bbadc1ac18fb500d3b746c8c1c1c46bb9523124c9ba3f9'),
 ('E62D','E632','40038e39a56b11e71412ead62b2574002c961973fe122d0aaca3b89f0ac0d52c'),
 ('E63D','E648','0b6bd8d5b060c86180149316236f21750165b786917ccf3dcd636db5071a8d34'),
 ('E710','E718','42e14ed3d9e6686c8e5b7b2f9c4639ddeafdc43a2156d6776c3ca07754096dd5'),
 ('E7A7','E814','77fdf616b9dcf810b95d87fbad15f22842b277c8a28e7bc6b0911084e493bdb2'),
 ('E827','E831','fe9dab3a7ce1bb29399af19923cf2e12165f9d17a0ed4bd6bebce71da6410060'),
 ('EB44','EB6B','7a534ebcac80d8c2e919184621381e3b944ae0ee161d474705cfe5cb199760c6'),
 ('EB82','EBF7','e69aaaa7f343f00621a23d78aab2b018057a6ba29ac50d07aa1c34bc8ed287e8'),
 ('F390','F3DD','534f1b3ff2e7b25348a1a4c66479018ec9153d63b3e9f9b964f9e07483905b15'),
 ('F6AE','F6E4','d79b617b7e27190b6556464a37cc024a1837e949ebe9446d12815da908233dfb'),
]
# 04FF corrected *noncontiguous* certificate, NOT abandoned 1005-byte
# bounding window: JP/decomp/analysis/RESUME_STATE.json at git
# a7d31bf1e7d608fa356b94eb54d4d17c8caa1a50.
HIST_04FF = [
 ('F3DD','F6AE','371c27c08f71624463d2c63097938a30fa57253bd073d2554d454111708f6852'),
 ('F6E4','F706','cd2f26e03fcfab69f12aec4fbe3ff9571f8a2633b3c84eb4365a0d8e777378c5'),
 ('F713','F724','4bc45df46fbab59efc9b70eb7d577001b8474818f921b86e618b43c4653c8300'),
 ('F739','F782','b8cc2cdf6b04eb86ff7693b53c006afb6710098252d7a921e199c22355d462ac'),
 ('F792','F7B7','b564a74ff4c6ba3a55b76472c1462ff1b915f0c333c8dc54ccae3b9a76d1e5e1'),
 ('F7CF','F800','13b6de6ba1671ce00afec40ee8b7886d6ed9126a6261b5a090a15f0cc73b1574'),
]

def historical():
    regions = []
    for stage,entries in [('04FE',HIST_04FE),('04FF',HIST_04FF)]:
        for begin,end,digest in entries:
            a,b=int(begin,16),int(end,16)
            assert 0xe000 <= a < b <= 0x10000
            assert len(digest)==64
            regions.append({'checkpoint':stage,'offset':31*8192+a-0xe000,
                            'length':b-a,'sha256':digest,'kind':'code/data'})
    count=lambda stage:sum(r['length'] for r in regions if r['checkpoint']==stage)
    assert (count('04FE'),count('04FF'),len(regions))==(957,931,17)
    return regions

def mask(regions):
    result=bytearray(N)
    for r in regions:
        start,end=r['offset'],r['offset']+r['length']
        if not 0<=start<end<=N or any(result[start:end]):
            raise ValueError('Overlapping or invalid physical PRG interval '+str(r))
        result[start:end]=b'\x01'*(end-start)
    return result

def verify_rom(rom,intervals):
    raw=Path(rom).read_bytes()
    if len(raw)!=393232 or hashlib.sha256(raw).hexdigest()!=ROM_SHA:
        raise ValueError('Original retail JP ROM SHA256 or size mismatch')
    prg=raw[16:16+N]
    for r in intervals:
        span=prg[r['offset']:r['offset']+r['length']]
        if hashlib.sha256(span).hexdigest()!=r['sha256']:
            raise ValueError('Original PRG source SHA256 mismatch '+str(r))

def audit(rom=None, historic_only=False):
    recovered=historical()
    histmask=mask(recovered)
    assert sum(histmask)==1888
    if historic_only:
        all_intervals=recovered
        inventory={}
    else:
        # The prior-0525 auditor verifies all 0500-0508 fragments and requires
        # their original committed manifests. Unlike a guessed baseline mask,
        # this is an actual union of all available certified intervals.
        import audit_prg_recomp_0525 as previous
        after=previous.certified()
        all_intervals=recovered+after
        combined=mask(all_intervals)
        if len(all_intervals)!=76 or sum(combined)!=7917:
            raise ValueError('Expected 04FE-0508 union mismatch')
        tracked=mask(previous.source_windows())
        overlapping=sum(a and b for a,b in zip(combined,tracked))
        outside=sum(a and not b for a,b in zip(tracked,combined))
        if (sum(tracked),overlapping,outside)!=(1365,626,739):
            raise ValueError('Previously recorded source window overlap changed')
        inventory={'tracked_native_source_bytes':1365,
                   'already_in_restored_strict_union':overlapping,
                   'outside_restored_strict_union_not_proven_novel':outside,
                   'known_strict_union_mask_sha256':hashlib.sha256(combined).hexdigest()}
    if rom:
        verify_rom(rom,all_intervals)
    result={'schema':'JP-historic-04FE-to-0508-union/v1',
            'original_rom_sha256':ROM_SHA,'rom_checked':bool(rom),
            'historical_04FE_bytes':957,'historical_04FF_bytes':931,
            'added_to_known_mask_not_new_credit':1888,
            'recovered_physical_interval_count':len(all_intervals),
            'recovered_certified_physical_bytes':sum(mask(all_intervals)),
            'unmapped_older_reported_strict_bytes':49504-sum(mask(all_intervals)),
            'strict_prg_floor_unchanged':49504,
            'incremental_04FE_04FF_mask_sha256':hashlib.sha256(histmask).hexdigest(),
            'source_accounting':inventory,
            'new_globally_certified_bytes':0,
            'limitation':'Pre-04FE physical strict PRG intervals not yet recovered'}
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path)
    p.add_argument('--historic-only',action='store_true')
    p.add_argument('--report',type=Path)
    a=p.parse_args()
    result=audit(a.rom,a.historic_only)
    if a.report:a.report.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS',result['recovered_certified_physical_bytes'],'known disjoint PRG bytes',
          result['recovered_physical_interval_count'],'intervals;',
          'opaque older baseline',result['unmapped_older_reported_strict_bytes'])
