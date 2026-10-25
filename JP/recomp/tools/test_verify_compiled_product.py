#!/usr/bin/env python3
"""ROM-free tests for the private Windows compiled PRG acceptance command."""
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import verify_compiled_product as gate


def frame_rows(n, changed=False):
    return "".join(
        f"{i} trace={i+11:016x} mem={i+21:016x} "
        "PC=E000 A=00 X=00 Y=00 S=FD P=24 int=00 "
        f"cycles={30000*(i+1)} hw={i+31+(int(changed)):016x}\n"
        for i in range(n)
    )


class CompiledProductAcceptanceTests(unittest.TestCase):
    def test_private_product_run_and_mismatch_rejection(self):
        with tempfile.TemporaryDirectory(prefix="cviii-compiled-gate-") as dirname:
            d = Path(dirname)
            exe, rom, replay = d/"game.exe", d/"original.nes", d/"input.txt"
            exe.write_bytes(b"synthetic binary")
            rom.write_bytes(bytes(393232))  # not a licensed game image
            replay.write_text("0 START\n", encoding="ascii")
            original_sha = gate.sha256_file

            def local_sha(path):
                return gate.ROM_SHA256 if Path(path) == rom else original_sha(path)

            def runner(args, changed=False, **kwargs):
                self.assertIn("--no-save", args)
                self.assertEqual(kwargs["cwd"], Path(args[args.index("--hash-out") + 1]).parent)
                interpreter = "--interp-only" in args
                hash_out = Path(args[args.index("--hash-out") + 1])
                hash_out.write_text(frame_rows(3, changed and interpreter), encoding="ascii")
                if not interpreter:
                    Path(args[args.index("--miss-log") + 1]).write_text(
                        "4k:00:E00B 1\n", encoding="ascii"
                    )
                summary = (
                    "mode=interp-only frames=3 cycles=90000 native_cycles=0 (0.0%)\n"
                    if interpreter else
                    "mode=native frames=3 cycles=90000 native_cycles=89990 (100.0%)\n"
                    "  native: ROM 89990 (100.0%) RAM views 0 (0.0%)\n"
                    "  interpreted: ROM 10 (0.0%) RAM 0 (0.0%)\n"
                )
                return subprocess.CompletedProcess(args, 0, stdout=summary, stderr="")

            with patch.object(gate, "sha256_file", side_effect=local_sha):
                with patch.object(gate.subprocess, "run", side_effect=runner):
                    report = gate.verify(exe, rom, replay, d/"report", 3, "enhanced", 90)
                self.assertEqual(report["compiled"]["compiled_prg_cpu_cycles"], 89990)
                self.assertTrue(report["same_machine_compiled_interpreter_match"])
                self.assertEqual(report["interpreted_rom_seed_entries"], 1)
                self.assertTrue(report["compiled_prg_coverage_accepted"])
                self.assertTrue((d/"report"/"compiled_product_acceptance.json").is_file())

                with patch.object(gate.subprocess, "run", side_effect=runner):
                    with self.assertRaisesRegex(ValueError, "same-machine frames MATCHED"):
                        gate.verify(exe, rom, replay, d/"under-threshold", 3, "enhanced", 100)
                rejected = __import__("json").loads(
                    (d/"under-threshold"/"compiled_product_acceptance.json").read_text()
                )
                self.assertEqual(rejected["acceptance_status"], "FAIL_COMPILED_PRG_COVERAGE")
                self.assertEqual(rejected["interpreted_rom_seed_entries"], 1)

                with patch.object(gate.subprocess, "run",
                                  side_effect=lambda args, **kw: runner(args, changed=True, **kw)):
                    with self.assertRaisesRegex(ValueError, "machine hashes"):
                        gate.verify(exe, rom, replay, d/"broken", 3, "enhanced", 90)

    def test_missing_accounting_and_invalid_hash(self):
        with self.assertRaisesRegex(ValueError, "counters missing"):
            gate.parse_stats("mode=native frames=3 cycles=90000 native_cycles=100\n", "native", 3)
        with tempfile.TemporaryDirectory(prefix="cviii-invalid-hashes-") as dirname:
            p = Path(dirname)/"broken.txt"
            p.write_text(frame_rows(3).replace("PC=E000", "PC=XXXX", 1))
            with self.assertRaisesRegex(ValueError, "malformed"):
                gate.read_frames(p, 3)


if __name__ == "__main__":
    unittest.main()
