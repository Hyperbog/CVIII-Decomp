"""Independent ROM-free checks of the current 16KiB Castlevania III bank atlas."""
from __future__ import annotations
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'SharedDecomp'))
from workflow import EvidenceError, validate_bank
from export_0538_bank_workflow import convert_atlas, EXPECTED, ORIGINAL_SHA, RAW0A_SHA


class AdapterTests(unittest.TestCase):
    def dummy(self):
        # Validate rejection without requiring published original bytes.
        return {"rom_sha256":ORIGINAL_SHA,"raw_bank_0a_sha256":RAW0A_SHA,
                "complete_original_bank_size":16384,
                "address_partition":[{"start_cpu":"8000","end_cpu_exclusive":"C000",
                                      "kind":"STATIC 6502 CANDIDATE (UNPROVED)","bytes":16384}]}

    def test_reject_wrong_rom(self):
        d=self.dummy();d['rom_sha256']='0'*64
        with self.assertRaisesRegex(EvidenceError,'provenance'):convert_atlas(d)

    def test_reject_incomplete_census(self):
        with self.assertRaisesRegex(EvidenceError,'census drift'):convert_atlas(self.dummy())

    def test_reject_unknown_confidence(self):
        d=self.dummy();d['address_partition'][0]['kind']='VERIFIED BY LLM'
        with self.assertRaisesRegex(EvidenceError,'unknown source atlas'):convert_atlas(d)

    def test_exact_generated_atlas_if_present(self):
        # Existing user-provided ROM/evidence are never uploaded to CI.
        path=ROOT/'JP/analysis/0538_raw0a_hierarchy_atlas.json'
        if not path.exists():self.skipTest('original atlas generated on demand')
        d=convert_atlas(json.loads(path.read_text()))
        r=validate_bank(d)
        self.assertEqual(r['verified_instruction_bytes'],2162)
        self.assertFalse(r['parity_proved'])

if __name__=='__main__':unittest.main()
