#!/usr/bin/env python3
"""ROM-free guardrails for the physical code-run/cross-edition candidate census."""
from __future__ import annotations
import hashlib,os,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from audit_0508_synthetic_crossedition_0501 import code_runs,decode_full_region,verified_image,audit

class TestCodeRuns(unittest.TestCase):
    def test_only_codebits_and_minimum_length(self):
        m=bytearray(16384)
        m[10:26]=bytes([1])*16
        m[100:115]=bytes([1])*15
        m[117:134]=bytes([1])*17
        r=code_runs(m,bytes(range(256))*64)
        self.assertEqual([(x['source_prg_offset'],x['size']) for x in r],[(10,16),(117,17)])
    def test_split_at_physical_8k_boundary(self):
        m=bytearray(16384);m[8180:8210]=bytes([1])*30
        result=code_runs(m,bytes(16384),min_length=10)
        self.assertEqual([(x['source_prg_offset'],x['size']) for x in result],[(8180,12),(8192,18)])
    def test_out_of_range_minimum(self):
        with self.assertRaises(ValueError):code_runs(bytes(10),bytes(10),7)
    def test_mismatched_lengths(self):
        with self.assertRaises(ValueError):code_runs(bytes(5),bytes(6))
    def test_linear_decode(self):
        self.assertEqual(decode_full_region(bytes.fromhex('A90185008D000860')),4)
    def test_decode_bad_opcode(self):
        self.assertIsNone(decode_full_region(b'\x02'))
    def test_decode_truncated_immediate(self):
        self.assertIsNone(decode_full_region(b'\xA9'))
    def test_code_flags_nonzero(self):
        m=bytearray(8192);m[1:17]=b'\x03'*16
        self.assertEqual(code_runs(m,bytes(8192))[0]['size'],16)
    def test_image_identity(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'test.bin';p.write_bytes(b'hello')
            with self.assertRaises(ValueError):verified_image(str(p),'bad')
    def test_optional_rom_pair(self):
        jp=os.getenv('NES_REUSE_JP_ROM');us=os.getenv('NES_REUSE_US_ROM')
        if not jp or not us:self.skipTest('legal commercial ROM pair absent from CI')
        manifest=str(Path(__file__).resolve().parents[1]/'SharedNES/JP_0501_CERTIFIED_REGIONS.json')
        out=audit(jp,us,manifest,[('start30',300),('none',120)])
        self.assertEqual(out['distinct_synthetic_executed_code_operand_bytes'],4979)
        self.assertEqual(out['synthetic_code_bytes_overlapping_checkpoint_0501_regions'],0)
        self.assertEqual(out['source_span_to_target_exact_candidates']['synthetic_executed_bytes_with_unique_US_windows'],909)
        self.assertEqual(out['strongest_example']['official_opcodes_in_linear_decode'],50)
        self.assertEqual(out['new_strict_prg_bytes'],0)

if __name__=='__main__':unittest.main(verbosity=2)
