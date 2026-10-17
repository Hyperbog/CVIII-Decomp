#!/usr/bin/env python3
"""Synthetic-only safety checks for narrow fixed-bank 0508 byte admission."""
import hashlib,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from audit_mesen_fixed_live_0508 import LIVE,UNCLAIMED,sha,static_audit,original_data

class TestStrictFixed(unittest.TestCase):
    def test_manifest_accounting(self):
        self.assertEqual((len(LIVE),sum(hi-lo+1 for _,lo,hi,_ in LIVE)),(4,100))
        seen=set()
        for _,a,b,_ in LIVE:
            self.assertTrue(any(x<=a and b<=y for x,y in UNCLAIMED))
            for pc in range(a,b+1):
                self.assertNotIn(pc,seen);seen.add(pc)
        self.assertEqual(len(seen),100)
    def test_five_uncredited_boundaries(self):
        self.assertEqual((LIVE[0][1],LIVE[1][2],LIVE[2][1],LIVE[3][2]),(0xFBA5,0xFBBA,0xFF06,0xFF55))
        self.assertNotIn(0xFF12,set(range(LIVE[2][1],LIVE[2][2]+1)))
    def test_no_original_rom_forgery(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"fake.nes";p.write_bytes(bytes(393232))
            with self.assertRaises(ValueError):original_data(p)
            with self.assertRaises(ValueError):static_audit(p)
    def test_counters_do_not_claim_nmi_closure(self):
        import audit_mesen_fixed_live_0508 as a
        self.assertEqual(a.JP,"958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28")
        self.assertTrue(any("0C" not in row[0] for row in LIVE))
    def test_sha_opaque(self):
        self.assertEqual(len(sha(b"\0"*100)),64)
    def test_private_emulator_required_for_reference(self):
        import inspect
        from audit_mesen_fixed_live_0508 import audit
        self.assertIn("emulator",inspect.signature(audit).parameters)
        self.assertIn("private",inspect.signature(audit).parameters)

if __name__=="__main__":unittest.main(verbosity=2)
