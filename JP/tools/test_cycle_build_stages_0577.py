#!/usr/bin/env python3
"""JP 0577 targeted build-vs-execution reporting test, no ROM reconstruction.

Mock the external compiler to test report durability and generated binary
fingerprints. Never claims source/emulator/gameplay parity from a stub.
"""
from __future__ import annotations
import hashlib,json,tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import nesrecomp_cycle_0568 as cycle
from validate_frame_artifacts_0578 import synthetic_png,fake_hash_lines

FAKE_ROM=b"synthetic-rom-only"
FAKE_BINARY=b"synthetic-c11-binary-fixture"
NATIVE_STATS=("mode=native frames=3 cycles=86958 native_cycles=86951 (100.0%)\n"
              "  interpreted: ROM 0 (0.0%, add to cycle_seed_file)"
              "  RAM 0 (0.0%, CPU RAM code no view covers: --capture-log)\n")

def fake_run_factory(output:Path,events:list[str],guest_error:bool=False):
    def invoke(command,**kwargs):
        if command[0]=="cmake":
            phase="build" if "--build" in command else "configure"
            events.append(phase)
            if phase=="build":
                (output/"jp_akumajou_densetsu").write_bytes(FAKE_BINARY)
            return SimpleNamespace(returncode=0,stdout="OK",stderr="")
        events.append("execute")
        if "--hash-out" in command and "--screenshot" in command:
            hashfile=Path(command[command.index("--hash-out")+1])
            png=Path(command[command.index("--screenshot")+1])
            hashfile.write_text(fake_hash_lines(3),encoding="ascii")
            png.write_bytes(synthetic_png())
        return SimpleNamespace(returncode=1 if guest_error else 0,
                               stdout=NATIVE_STATS,stderr="guest error" if guest_error else "")
    return invoke

def verify():
    with tempfile.TemporaryDirectory(prefix="jp0577-") as directory:
        root=Path(directory);rom=root/"fake.nes";rom.write_bytes(FAKE_ROM)
        engine=root/"external";engine.mkdir()
        out=root/"generated";events=[]
        args=SimpleNamespace(rom=rom,engine=engine,out=out,frames=3,
                             windowed=False,plan=False,build_only=True)
        fake=fake_run_factory(out,events)
        with patch.object(cycle,"authenticated",return_value={"synthetic":True}),\
             patch.object(cycle,"validate_engine",return_value=None),\
             patch.object(cycle.subprocess,"run",side_effect=fake):
            report=cycle.run(args)
        assert events==["configure","build"],events
        assert report["build_completed"] and not report["frame_execution_attempted"]
        assert report["runner_sha256"]==hashlib.sha256(FAKE_BINARY).hexdigest()
        assert json.loads((out/"jp_cycle_build.json").read_text())["runner_sha256"]==report["runner_sha256"]
        assert not (out/"headless_run.log").exists()
        args.build_only=False;events.clear()
        with patch.object(cycle,"authenticated",return_value={"synthetic":True}),\
             patch.object(cycle,"validate_engine",return_value=None),\
             patch.object(cycle.subprocess,"run",side_effect=fake_run_factory(out,events)):
            executed=cycle.run(args)
        assert events==["configure","build","execute"] and executed["cpu_execution"]["frames"]==3
        assert executed["frame_artifacts"]["frame_records"]==3
        assert executed["runner_sha256"]==report["runner_sha256"]
        assert (out/"jp_cycle_0568.json").exists()
        events.clear()
        with patch.object(cycle,"authenticated",return_value={"synthetic":True}),\
             patch.object(cycle,"validate_engine",return_value=None),\
             patch.object(cycle.subprocess,"run",side_effect=fake_run_factory(out,events,True)):
            try:cycle.run(args)
            except RuntimeError:pass
            else:raise AssertionError("guest error was reported as success")
        assert events==["configure","build","execute"]
        assert json.loads((out/"jp_cycle_build.json").read_text())["build_completed"]
    print("PASS JP0577 separate original-game build status, executable SHA256 and guest errors")

if __name__=="__main__":
    verify()
