#!/usr/bin/env python3
"""ROM-free regression for deterministic reference PC trace digest handling."""
import hashlib,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from test_native_mesen_pc_0509 import GOLDENS,digest_pc,ROM_SHA
class TestDigest(unittest.TestCase):
    def test_shape(self):
        self.assertEqual(sorted(GOLDENS),[100,3000,7828]);self.assertEqual(len(ROM_SHA),64)
    def test_pc_hash(self):
        self.assertEqual(digest_pc(['E00B  CLD','E00C  SEI'],2),hashlib.sha256(b'E00B\nE00C\n').hexdigest())
    def test_reject_truncation(self):
        with self.assertRaises(ValueError):digest_pc(['E00B  CLD'],2)
    def test_reject_lowercase(self):
        with self.assertRaises(ValueError):digest_pc(['e00b  CLD'],1)
    def test_reject_invalid(self):
        with self.assertRaises(ValueError):digest_pc(['00  CLD'],1)
if __name__=='__main__':unittest.main(verbosity=2)
