#!/usr/bin/env python3
"""ROM-free regression/negative tests for the split native product and decomp data."""
import copy
import csv
import json
import unittest
from pathlib import Path

import audit_workstreams as audit

ROOT = Path(__file__).resolve().parents[2]


class WorkstreamSeparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = audit.read_json(ROOT / audit.MANIFEST)
        cls.product = audit.read_json(ROOT / audit.PRODUCT)
        cls.semantic = audit.read_json(ROOT / audit.SEMANTIC)
        cls.state = audit.read_json(ROOT / "JP/analysis/RESUME_STATE.json")
        cls.ledger = audit.read_json(ROOT / "JP/analysis/NATIVE_EVIDENCE_LEDGER.json")
        with (ROOT / "JP/analysis/PROGRESS_SCORE.csv").open(
                newline="", encoding="utf-8") as f:
            cls.rubric = list(csv.DictReader(f))

    def test_actual_repository_product_and_semantic_boundaries(self):
        r = audit.validate(ROOT)
        self.assertEqual(r["native_release"], "0.2.0-alpha.1")
        self.assertEqual(r["semantic_vpp"], 31)
        self.assertEqual(r["semantic_strict_prg_bytes"], 49504)

    def test_clear_unique_ownership(self):
        owners = audit.validate_manifest_shape(self.manifest)
        self.assertEqual(owners["JP/native/nesrecomp_cycle/CMakeLists.txt"],
                         "native_recompilation")
        self.assertEqual(owners["JP/native/enhanced/cviii_room_stream_0659.c"],
                         "semantic_decompilation")
        self.assertEqual(owners["JP/docs/ROM_IDENTITY.md"], "shared")

    def test_no_product_source_mislabeled_as_semantic(self):
        m = copy.deepcopy(self.manifest)
        product_rows = m["streams"]["native_recompilation"]["files"]
        row = next(x for x in product_rows if x["path"] ==
                   "JP/native/enhanced/cviii_edition.c")
        product_rows.remove(row)
        m["streams"]["semantic_decompilation"]["files"].append(row)
        with self.assertRaisesRegex(ValueError, "Playable product"):
            audit.validate_manifest_shape(m)

    def test_no_same_file_owned_by_two_workstreams(self):
        m = copy.deepcopy(self.manifest)
        m["streams"]["native_recompilation"]["files"].append(
            copy.deepcopy(m["streams"]["semantic_decompilation"]["files"][0]))
        with self.assertRaisesRegex(ValueError, "Double-owned"):
            audit.validate_manifest_shape(m)

    def test_reject_repository_traversal(self):
        for path in ("../secrets", "/etc/passwd", "JP/../NA/foo",
                     "JP\\analysis\\RESUME_STATE.json", ""):
            with self.subTest(path=path), self.assertRaises(ValueError):
                audit.safe_relative(path)

    def test_fixed_semantic_score_not_product_progress(self):
        earned, prg = audit.validate_semantic_counters(
            self.rubric, self.state, self.ledger)
        self.assertEqual((earned, prg), (31, 49504))
        self.assertNotIn("vpp", self.product)
        self.assertNotIn("strict_prg_floor", self.product)

    def test_reject_counter_divergence(self):
        bad = copy.deepcopy(self.ledger)
        bad["certification"]["vpp_earned"] += 1
        with self.assertRaisesRegex(ValueError, "VPP disagree"):
            audit.validate_semantic_counters(self.rubric, self.state, bad)
        bad = copy.deepcopy(self.state)
        bad["progress_metrics"]["strict_verified_prg_floor_bytes"] += 1
        with self.assertRaisesRegex(ValueError, "Strict PRG"):
            audit.validate_semantic_counters(self.rubric, bad, self.ledger)

    def test_reject_doubled_semantic_counter_in_product(self):
        p = copy.deepcopy(self.product)
        p["vpp_earned"] = 31
        with self.assertRaisesRegex(ValueError, "Semantic progress counter"):
            audit.validate_product_index(
                p, self.semantic, audit.validate_manifest_shape(self.manifest))

    def test_reject_native_feature_evidence_misfiled_under_decomp(self):
        p = copy.deepcopy(self.product)
        p["capabilities"][0]["source"] = "JP/analysis/PROGRESS_SCORE.csv"
        with self.assertRaisesRegex(ValueError, "outside product workstream"):
            audit.validate_product_index(
                p, self.semantic, audit.validate_manifest_shape(self.manifest))

    def test_reject_forked_semantic_vpp_authority(self):
        sem = copy.deepcopy(self.semantic)
        sem["canonical_sources"]["vpp_csv"] = (
            "JP/workstreams/semantic-decompilation/another-score.csv")
        with self.assertRaisesRegex(ValueError, "Duplicated or diverted"):
            audit.validate_product_index(
                self.product, sem, audit.validate_manifest_shape(self.manifest))


if __name__ == "__main__":
    unittest.main(verbosity=2)
