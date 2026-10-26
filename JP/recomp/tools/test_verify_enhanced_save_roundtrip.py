#!/usr/bin/env python3
"""ROM-free tests of private Windows Enhanced full-machine save/load gate."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import verify_enhanced_save_roundtrip as gate


def rows(count):
    return [
        (f"{i} trace={i+11:016x} mem={i+21:016x} PC=E000 A=00 X=00 "
         f"Y=00 S=FD P=24 int=00 cycles={30000*(i+1)} hw={i+31:016x}\n").encode("ascii")
        for i in range(count)
    ]


class RoundtripContract(unittest.TestCase):
    def test_saved_state_two_modes_and_negative_cases(self):
        with tempfile.TemporaryDirectory(prefix="cviii-state-test-") as tmp:
            base = Path(tmp)
            exe, rom, replay = (base/f for f in ("game.exe", "original.nes", "route.input"))
            exe.write_bytes(b"fake native binary")
            rom.write_bytes(bytes(393232))
            replay.write_bytes(b"0 1:-\n0 2:-\n")
            accepted = base/"accepted"
            accepted.mkdir()
            trace = b"".join(rows(4))
            (accepted/"native.machinehash").write_bytes(trace)
            (accepted/"interp-only.machinehash").write_bytes(trace)
            certificate = accepted/"compiled_product_acceptance.json"
            certificate.write_text(json.dumps({
                "schema": "cviii-compiled-enhanced-acceptance/v1",
                "acceptance_status": "PASS", "edition": "enhanced",
                "compiled_prg_coverage_accepted": True,
                "same_machine_compiled_interpreter_match": True, "frames": 4,
                "original_rom_sha256": gate.JP_SHA,
                "private_executable_sha256": gate.sha(exe),
                "controller_schedule_sha256": gate.sha(replay),
                "machine_hash_sha256": gate.sha(accepted/"native.machinehash"),
                "minimum_compiled_prg_percent": 90,
                "compiled": {"compiled_prg_percent": 99.99},
            }), encoding="utf-8")
            real_sha = gate.sha
            def local_sha(file):
                return gate.JP_SHA if Path(file) == rom else real_sha(file)
            def runner(args, corrupt=False, **kwargs):
                self.assertIn("--no-save", args)
                self.assertEqual(kwargs["cwd"], Path(args[args.index("--hash-out")+1]).parent)
                path = Path(args[args.index("--hash-out")+1])
                if "--save-state" in args:
                    frame, state = args[args.index("--save-state")+1].split(":", 1)
                    self.assertEqual(frame, "1")
                    Path(state).write_bytes(b"synthetic full machine state")
                    image = rows(4)
                    message = f"state: saved {state} after frame 1\n"
                else:
                    image = rows(4)[2:]
                    message = "state: loaded synthetic, continuing at frame 2\n"
                if corrupt and path.name == "resume-native.machinehash":
                    image[0] = rows(4)[1]
                path.write_bytes(b"".join(image))
                mode = "interp-only" if "--interp-only" in args else "native"
                return subprocess.CompletedProcess(args, 0,
                    stdout=message+f"mode={mode} frames=4 cycles=120000 native_cycles={0 if mode=='interp-only' else 119999}\n",
                    stderr="")
            with patch.object(gate, "sha", side_effect=local_sha):
                with patch.object(gate.subprocess, "run", side_effect=runner):
                    report = gate.verify(exe,rom,replay,certificate,base/"good",1)
                self.assertEqual(report["status"], "PASS")
                self.assertEqual(report["continuation_frames_per_mode"], 2)
                with patch.object(gate.subprocess, "run", side_effect=lambda a, **kw: runner(a, corrupt=True, **kw)):
                    with self.assertRaisesRegex(ValueError, "diverged|invalid machine hash"):
                        gate.verify(exe,rom,replay,certificate,base/"divergence",1)
                wrong = json.loads(certificate.read_text())
                wrong["private_executable_sha256"] = "0"*64
                certificate.write_text(json.dumps(wrong))
                with self.assertRaisesRegex(ValueError, "identity drift"):
                    gate.verify(exe,rom,replay,certificate,base/"wrong",1)


if __name__ == "__main__":
    unittest.main()
