#!/usr/bin/env python3
"""ROM-free, source-independent VRC6a/b register and bank-state contract."""
from pathlib import Path
import sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from nes_mapper_family import BankContext,prg_physical_location,vrc6_canonical_write

class TestVrc6(unittest.TestCase):
    def test_register_swap_exhaustive(self):
        for base in range(0x8000,0x10000,0x1000):
            for sub in range(4):
                orig=base|sub
                self.assertEqual(vrc6_canonical_write(24,orig),orig)
                expect=base|((sub&1)<<1)|((sub&2)>>1)
                self.assertEqual(vrc6_canonical_write(26,orig),expect)
                self.assertEqual(vrc6_canonical_write(26,expect),orig)
    def test_register_mirrors(self):
        self.assertEqual(vrc6_canonical_write(24,0xFABC),0xF000)
        self.assertEqual(vrc6_canonical_write(26,0xF9FD),0xF002)
        self.assertEqual(vrc6_canonical_write(26,0xF7FE),0xF001)
        self.assertEqual(vrc6_canonical_write(26,0xB003),0xB003)
    def test_mapper_rejection(self):
        with self.assertRaisesRegex(ValueError,'VRC6'):
            vrc6_canonical_write(5,0xF000)
    def test_register_below_prg(self):
        with self.assertRaisesRegex(ValueError,'not mapped'):
            vrc6_canonical_write(24,0x4000)
    def test_prg_explicit_banks(self):
        c=BankContext(24,262144,10,30,'test:mapper-write')
        self.assertEqual(prg_physical_location(c,0x8000)['physical_8k_bank'],20)
        self.assertEqual(prg_physical_location(c,0xBFFF)['physical_8k_bank'],21)
        self.assertEqual(prg_physical_location(c,0xC000)['physical_8k_bank'],30)
        self.assertEqual(prg_physical_location(c,0xE000)['physical_8k_bank'],31)
        self.assertEqual(prg_physical_location(c,0xFFFF)['physical_prg_file_offset'],262143)
    def test_mapper26_same_offset_given_same_banks(self):
        a=BankContext(24,262144,10,30,'trace-24')
        b=BankContext(26,262144,10,30,'trace-26')
        for pc in (0x8000,0x80F1,0xA000,0xBFFF,0xC000,0xDFFF,0xE000,0xFFFF):
            x=prg_physical_location(a,pc)['physical_prg_file_offset']
            y=prg_physical_location(b,pc)['physical_prg_file_offset']
            self.assertEqual(x,y)
    def test_unobserved_bank_not_allowed(self):
        with self.assertRaisesRegex(ValueError,'provenance'):
            prg_physical_location(BankContext(24,262144,0,30,''),0x8000)
    def test_out_of_bounds(self):
        with self.assertRaisesRegex(ValueError,'outside actual PRG'):
            prg_physical_location(BankContext(24,32768,10,0,'test'),0x8000)
    def test_invalid_mapper(self):
        with self.assertRaisesRegex(ValueError,'24/26'):
            prg_physical_location(BankContext(5,262144,0,0,'test'),0x8000)

if __name__=='__main__':unittest.main(verbosity=2)
