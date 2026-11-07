#!/usr/bin/env python3
"""Owner-private Enhanced full-machine save/load continuation gate."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

JP_SHA = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
FRAME = re.compile(
    r"(\d+) trace=[0-9a-f]{16} mem=[0-9a-f]{16} PC=[0-9a-f]{4} "
    r"A=[0-9a-f]{2} X=[0-9a-f]{2} Y=[0-9a-f]{2} S=[0-9a-f]{2} "
    r"P=[0-9a-f]{2} int=\d+ cycles=(\d+) hw=[0-9a-f]{16}", re.I)
SUMMARY = re.compile(r"^mode=(native|interp-only) frames=(\d+) cycles=(\d+) native_cycles=(\d+)", re.M)


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def frame_rows(path: Path, first: int, last: int) -> list[bytes]:
    lines = path.read_bytes().splitlines(keepends=True)
    if len(lines) != last - first:
        raise ValueError(f"{path.name}: expected {last-first} frames, got {len(lines)}")
    previous_cycles = -1
    for frame, raw in enumerate(lines, first):
        m = FRAME.fullmatch(raw.rstrip(b"\r\n").decode("ascii"))
        if m is None or int(m.group(1)) != frame:
            raise ValueError(f"{path.name}: invalid machine hash at frame {frame}")
        cycles = int(m.group(2))
        if cycles <= previous_cycles:
            raise ValueError(f"{path.name}: non-increasing CPU cycles")
        previous_cycles = cycles
    return lines


def verify(exe: Path, rom: Path, replay: Path, certificate: Path,
           out: Path, save_after: int | None = None) -> dict:
    if not all(p.is_file() for p in (exe, rom, replay, certificate)):
        raise ValueError("private EXE, ROM, input and acceptance certificate must exist")
    if rom.stat().st_size != 393232 or sha(rom) != JP_SHA:
        raise ValueError("original Japanese ROM SHA-256/size mismatch")
    out = out.resolve()
    if any((p / ".git").exists() for p in (out, *out.parents)):
        raise ValueError("private states and machine hashes must stay outside Git")
    if out == certificate.parent.resolve():
        raise ValueError("refuse to replace original compiled acceptance evidence")
    cert = json.loads(certificate.read_text(encoding="utf-8"))
    frames = cert.get("frames")
    if (cert.get("schema") != "cviii-compiled-enhanced-acceptance/v1"
        or cert.get("acceptance_status") != "PASS"
        or cert.get("edition") != "enhanced"
        or cert.get("compiled_prg_coverage_accepted") is not True
        or cert.get("same_machine_compiled_interpreter_match") is not True
        or type(frames) is not int or not 4 <= frames <= 12000):
        raise ValueError("missing successful compiled Enhanced acceptance certificate")
    if (cert.get("original_rom_sha256") != JP_SHA
        or cert.get("private_executable_sha256") != sha(exe)
        or cert.get("controller_schedule_sha256") != sha(replay)):
        raise ValueError("certificate versus ROM/EXE/controller identity drift")
    if cert.get("compiled", {}).get("compiled_prg_percent", 0) < cert.get("minimum_compiled_prg_percent", 90):
        raise ValueError("source compiled coverage did not meet acceptance threshold")
    accepted_native = certificate.parent / "native.machinehash"
    accepted_interp = certificate.parent / "interp-only.machinehash"
    if not (accepted_native.is_file() and accepted_interp.is_file()
        and sha(accepted_native) == cert.get("machine_hash_sha256")
        and accepted_native.read_bytes() == accepted_interp.read_bytes()):
        raise ValueError("accepted full-machine frame hash evidence missing or changed")
    baseline = frame_rows(accepted_native, 0, frames)
    if save_after is None:
        save_after = frames // 2 - 1
    if not 0 <= save_after < frames-1:
        raise ValueError("save-after must precede final frame")
    out.mkdir(parents=True, exist_ok=True)
    state = out / "private-midpoint.cycstate"
    state.unlink(missing_ok=True)
    stages = (
        ("save", ["--save-state", f"{save_after}:{state}"], 0, "native"),
        ("resume-native", ["--load-state", str(state)], save_after + 1, "native"),
        ("resume-interp", ["--load-state", str(state), "--interp-only"], save_after + 1, "interp-only"),
    )
    for label, extra, first, mode in stages:
        trace = out / (label + ".machinehash")
        trace.unlink(missing_ok=True)
        cmd = [str(exe), str(rom), "--edition", "enhanced", "--headless", "--no-save",
               "--frames", str(frames), "--input", str(replay), "--hash-out", str(trace), *extra]
        result = subprocess.run(cmd, cwd=out, capture_output=True, text=True,
                                timeout=max(120, min(1800, frames*3)))
        log = out / (label + ".log")
        log.write_text(result.stdout + "\n" + result.stderr, encoding="utf-8")
        if result.returncode:
            raise RuntimeError(f"{label} returned {result.returncode}: inspect {log}")
        summary = list(SUMMARY.finditer(result.stdout + "\n" + result.stderr))
        if (len(summary) != 1 or summary[0].group(1) != mode
            or int(summary[0].group(2)) != frames
            or (mode == "interp-only" and int(summary[0].group(4)) != 0)):
            raise ValueError(f"{label}: invalid CPU mode/frame counters; inspect {log}")
        actual = frame_rows(trace, first, frames)
        expected = baseline[first:]
        if actual != expected:
            mismatch = next((i+first for i,(a,b) in enumerate(zip(actual,expected)) if a!=b), first)
            raise ValueError(f"{label}: saved full-machine state diverged at frame {mismatch}")
        if label == "save":
            if not state.is_file() or state.stat().st_size == 0:
                raise ValueError("saved full-machine state absent or empty")
            if f"state: saved {state} after frame {save_after}" not in result.stdout:
                raise ValueError("host did not acknowledge state save at exact frame")
        elif f"continuing at frame {save_after + 1}" not in result.stdout:
            raise ValueError(f"{label}: resume frame does not match saved epoch")
    report = {
        "schema": "cviii-enhanced-save-roundtrip/v1",
        "status": "PASS", "frames": frames, "saved_after": save_after,
        "resumed_at": save_after + 1, "continuation_frames_per_mode": frames-save_after-1,
        "original_acceptance_sha256": sha(certificate),
        "private_executable_sha256": sha(exe), "input_sha256": sha(replay),
        "original_rom_sha256": JP_SHA, "reference_hash_sha256": cert["machine_hash_sha256"],
        "saved_baseline_match": True, "compiled_resume_match": True, "interpreter_resume_match": True,
        "interactive_windows_menu_verified": False, "original_hardware_parity_verified": False,
        "private_state_file": str(state),
    }
    (out / "enhanced_save_roundtrip.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("exe", "rom", "input", "acceptance-report", "out"):
        p.add_argument("--"+name, required=True, type=Path)
    p.add_argument("--save-after", type=int)
    a = p.parse_args()
    print(json.dumps(verify(a.exe.resolve(), a.rom.resolve(), a.input.resolve(),
                            a.acceptance_report.resolve(), a.out.resolve(), a.save_after),
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, OSError, UnicodeError,
            subprocess.TimeoutExpired, json.JSONDecodeError) as e:
        print(f"CVIII Enhanced save/load acceptance FAILED: {e}", file=sys.stderr)
        raise SystemExit(2)
