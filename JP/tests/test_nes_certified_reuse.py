#!/usr/bin/env python3
"""ROM-free evidence manifest and cross-game correspondence acceptance tests."""
from __future__ import annotations
import hashlib,json,os,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from nes_certified_reuse import sha,input_regions,match_source,audit

def rec(data:bytes,at=0):
    return {'source_prg_offset':at,'size':len(data),'sha256':sha(data),
            'source_bank':'TEST','source_cpu_start':'8000'}

class MatchTest(unittest.TestCase):
    def setUp(self):
        self.p=bytes(range(64))
        self.region=rec(self.p)
        self.man={'schema':'nes-semantic-origin-regions/v1','source_rom_sha256':'a',
             'target_rom_sha256':'b','total_certified_source_bytes':64,'regions':[self.region]}
    def validate(self,**updates):
        x={**self.man,**updates}
        return input_regions(x,self.p,b'', 'a','b')
    def test_hash_locked_manifest(self):
        self.assertEqual(len(self.validate()),1)
    def test_reject_wrong_rom(self):
        with self.assertRaisesRegex(ValueError,'image identity'):input_regions(self.man,self.p,b'','x','b')
    def test_reject_unknown_schema(self):
        with self.assertRaisesRegex(ValueError,'schema'):self.validate(schema='bad')
    def test_reject_empty(self):
        with self.assertRaisesRegex(ValueError,'no regions'):self.validate(regions=[])
    def test_reject_bad_hash(self):
        with self.assertRaisesRegex(ValueError,'SHA-256'):self.validate(regions=[{**self.region,'sha256':'0'*64}])
    def test_reject_out_of_bounds(self):
        with self.assertRaisesRegex(ValueError,'outside'):self.validate(regions=[rec(self.p,10)])
    def test_reject_overlap(self):
        a=rec(self.p[:40]);b=rec(self.p[20:50],20)
        with self.assertRaisesRegex(ValueError,'overlapping'):self.validate(regions=[a,b])
    def test_reject_total_mismatch(self):
        with self.assertRaisesRegex(ValueError,'total mismatch'):self.validate(total_certified_source_bytes=63)
    def test_reject_boolean_offset(self):
        with self.assertRaisesRegex(ValueError,'bad offset'):self.validate(regions=[{**self.region,'source_prg_offset':True}])
    def test_unique_source_bytes(self):
        r=match_source(self.p, b'\x99'*20+self.p+b'\xFE'*20,[self.region],16)
        self.assertEqual(r['source_certified_bytes_with_unique_exact_target_windows'],64)
        self.assertEqual(r['source_certified_bytes_without_target_windows'],0)
        self.assertEqual(r['representative_nonoverlapping_unique_target_candidates'][0]['target_prg_offset'],20)
    def test_ambiguous(self):
        r=match_source(self.p,self.p+b'\xff'*15+self.p,[self.region],16)
        self.assertEqual(r['source_certified_bytes_with_unique_exact_target_windows'],0)
        self.assertEqual(r['source_certified_bytes_with_only_ambiguous_target_windows'],64)
    def test_no_match(self):
        r=match_source(self.p,b'\xff'*100,[self.region],16)
        self.assertEqual(r['source_certified_bytes_without_target_windows'],64)
    def test_short_segment(self):
        r=match_source(self.p,self.p,[rec(self.p[:9])],16)
        self.assertEqual((r['source_certified_bytes'],r['source_certified_bytes_without_target_windows']),(9,9))
    def test_minimum_window_guard(self):
        with self.assertRaises(ValueError):match_source(self.p,self.p,[self.region],7)
    def test_max_candidate_zero(self):
        r=match_source(self.p,self.p,[self.region],16,max_candidates=0)
        self.assertEqual(len(r['representative_nonoverlapping_unique_target_candidates']),0)
    def test_no_original_bytes_serialized(self):
        r=match_source(self.p,b'\xAA'*10+self.p,[self.region])
        s=json.dumps(r)
        self.assertNotIn('00010203',s)
        self.assertEqual(r['strict_new_verified_target_bytes'],0)
    def test_counts_sum(self):
        r=match_source(self.p,self.p[:10]+b'\xff'*54,[self.region],16)
        self.assertEqual(sum(r[k] for k in ('source_certified_bytes_with_unique_exact_target_windows','source_certified_bytes_with_only_ambiguous_target_windows','source_certified_bytes_without_target_windows')),64)
    def test_optional_pair_original_rom_locked(self):
        jp=os.getenv('NES_REUSE_JP_ROM');us=os.getenv('NES_REUSE_US_ROM')
        if not jp or not us:self.skipTest('original ROM pair deliberately absent from GitHub CI')
        mf=str(Path(__file__).resolve().parents[1]/'SharedNES/JP_0501_CERTIFIED_REGIONS.json')
        x=audit(jp,us,mf)
        self.assertEqual(x['source_certified_bytes'],4364)
        self.assertEqual(x['source_certified_bytes_with_unique_exact_target_windows'],1273)
        self.assertEqual(x['source_certified_bytes_with_only_ambiguous_target_windows'],5)
        self.assertEqual(x['source_certified_bytes_without_target_windows'],3086)
        self.assertEqual((x['source_mapper'],x['target_mapper']),(24,5))
        self.assertEqual(x['strict_new_verified_target_bytes'],0)

if __name__=='__main__':unittest.main(verbosity=2)
