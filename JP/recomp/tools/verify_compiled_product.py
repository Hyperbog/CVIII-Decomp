#!/usr/bin/env python3
"""Private acceptance of compiled 6502 execution in the Windows Enhanced product.

Runs the SAME private, ROM-generated jp_akumajou_densetsu executable in
compiled and interpreter-only modes on the pinned hardware model. No Mesen,
new controller recording, public ROM, or ROM-derived C is required.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROM_SHA256 = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
SUMMARY = re.compile(
    r"^mode=(native|interp-only) frames=(\d+) cycles=(\d+) native_cycles=(\d+)",
    re.MULTILINE,
)
FALLBACK = re.compile(r"^\s+interpreted: ROM (\d+) \([^\n]*?RAM (\d+)", re.MULTILINE)
NATIVE_SPLIT = re.compile(r"^\s+native: ROM (\d+) \([^\n]*?RAM views (\d+)", re.MULTILINE)
FRAME = re.compile(
    r"^(\d+) trace=[0-9a-fA-F]{16} mem=[0-9a-fA-F]{16} "
    r"PC=[0-9a-fA-F]{4} A=[0-9a-fA-F]{2} X=[0-9a-fA-F]{2} "
    r"Y=[0-9a-fA-F]{2} S=[0-9a-fA-F]{2} P=[0-9a-fA-F]{2} "
    r"int=\d+ cycles=(\d+) hw=[0-9a-fA-F]{16}$"
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def outside_git(path: Path) -> bool:
    path = path.resolve()
    return not any((part / ".git").exists() for part in (path, *path.parents))


def read_frames(path: Path, frames: int) -> bytes:
    raw = path.read_bytes()
    rows = raw.decode("ascii").splitlines()
    if len(rows) != frames:
        raise ValueError(f"expected {frames} machine hashes, got {len(rows)}")
    previous_index = previous_cycles = None
    for row in rows:
        m = FRAME.fullmatch(row)
        if m is None:
            raise ValueError("malformed compiled/interpreted machine hash")
        index, cycles = int(m.group(1)), int(m.group(2))
        if previous_index is not None and (index != previous_index + 1 or cycles <= previous_cycles):
            raise ValueError("missing/repeated frame or non-increasing CPU cycles")
        previous_index, previous_cycles = index, cycles
    return raw


def parse_stats(output: str, mode: str, frames: int) -> dict:
    matches = list(SUMMARY.finditer(output))
    if len(matches) != 1 or matches[0].group(1) != mode:
        raise ValueError(f"missing or ambiguous {mode} CPU accounting")
    _, actual, total, native = matches[0].groups()
    actual, total, native = int(actual), int(total), int(native)
    if actual != frames or total <= 0 or native > total:
        raise ValueError(f"invalid {mode} frame/cycle counters")
    if mode == "interp-only":
        if native != 0:
            raise ValueError("reference execution unexpectedly used compiled instructions")
        return {"frames": actual, "cpu_cycles": total, "native_cpu_cycles": 0}

    split = NATIVE_SPLIT.search(output)
    rom, ram_views = (int(split.group(1)), int(split.group(2))) if split else (native, 0)
    if rom + ram_views != native:
        raise ValueError("compiled ROM/RAM accounting disagrees with native cycle total")
    fallback = FALLBACK.search(output)
    if not fallback and native != total:
        raise ValueError("interpreter ROM/RAM counters missing")
    interpreted_rom, interpreted_ram = (
        (int(fallback.group(1)), int(fallback.group(2))) if fallback else (0, 0)
    )
    return {
        "frames": actual, "cpu_cycles": total, "native_cpu_cycles": native,
        "compiled_prg_cpu_cycles": rom, "compiled_ram_view_cpu_cycles": ram_views,
        "interpreted_rom_cpu_cycles": interpreted_rom,
        "interpreted_cpu_ram_cycles": interpreted_ram,
        "compiled_prg_percent": round(100.0 * rom / total, 6),
    }


def verify(exe: Path, rom: Path, replay: Path, out: Path,
           frames: int, edition: str, minimum_prg_percent: float) -> dict:
    if not 1 <= frames <= 12000:
        raise ValueError("frames must be 1..12000")
    if not 0.0 <= minimum_prg_percent <= 100.0:
        raise ValueError("minimum compiled PRG percent must be 0..100")
    if not exe.is_file() or not replay.is_file() or not replay.stat().st_size:
        raise ValueError("compiled executable or nonempty controller input missing")
    if not rom.is_file() or rom.stat().st_size != 393232 or sha256_file(rom) != ROM_SHA256:
        raise ValueError("original Japanese Mapper24 ROM SHA-256/size mismatch")
    if not outside_git(out):
        raise ValueError("private verification artifacts must stay outside the repository")
    out.mkdir(parents=True, exist_ok=True)
    miss_path = out / "compiled_rom_fallback.seed"
    miss_path.unlink(missing_ok=True)  # no stale compiled-miss evidence
    stats = {}
    images = {}
    for mode in ("native", "interp-only"):
        hash_path = out / f"{mode}.machinehash"
        log_path = out / f"{mode}.log"
        hash_path.unlink(missing_ok=True)  # never accept stale hashes from an earlier run
        # Pinned NESRecomp supports --no-save: acceptance must not read/write
        # player cartridge saves. Isolate incidental relative host outputs too.
        args = [str(exe), str(rom), "--edition", edition,
                "--headless", "--no-save", "--frames", str(frames),
                "--input", str(replay), "--hash-out", str(hash_path)]
        if mode == "interp-only":
            args.append("--interp-only")
        else:
            # Mapper-qualified interpreter ROM misses are actionable
            # NESRecomp --cycle-seed-file inputs for a private rebuild.
            args.extend(["--miss-log", str(miss_path)])
        proc = subprocess.run(args, capture_output=True, text=True,
                              cwd=out, timeout=max(120, min(1800, frames * 3)))
        output = proc.stdout + "\n" + proc.stderr
        log_path.write_text(output, encoding="utf-8")
        if proc.returncode:
            raise RuntimeError(f"{mode} execution failed ({proc.returncode}); inspect {log_path}")
        stats[mode] = parse_stats(output, mode, frames)
        images[mode] = read_frames(hash_path, frames)
    if images["native"] != images["interp-only"]:
        raise ValueError("compiled execution differs from interpreter-only machine hashes")
    prg_percent = stats["native"]["compiled_prg_percent"]
    coverage_ok = prg_percent >= minimum_prg_percent
    if not miss_path.is_file():
        raise ValueError("pinned native runner failed to write interpreter ROM-miss seeds")
    # The host uses physical 4 KiB bank + mapped CPU address: 4k:BB:AAAA.
    seed_lines = [
        line for line in miss_path.read_text(encoding="ascii").splitlines()
        if line and not line.startswith("#")
    ]
    if any(re.fullmatch(r"4k:[0-9A-Fa-f]{2,}:[89A-Fa-f][0-9A-Fa-f]{3} \d+", s) is None
           for s in seed_lines):
        raise ValueError("malformed pinned NESRecomp bank-qualified ROM-miss entry")
    report = {
        "schema": "cviii-compiled-enhanced-acceptance/v1",
        "edition": edition, "frames": frames,
        "original_rom_sha256": ROM_SHA256,
        "private_executable_sha256": sha256_file(exe),
        "controller_schedule_sha256": sha256_file(replay),
        "machine_hash_sha256": hashlib.sha256(images["native"]).hexdigest(),
        "same_machine_compiled_interpreter_match": True,
        "compiled": stats["native"],
        "reference": stats["interp-only"],
        "minimum_compiled_prg_percent": minimum_prg_percent,
        "compiled_prg_coverage_accepted": coverage_ok,
        "acceptance_status": "PASS" if coverage_ok else "FAIL_COMPILED_PRG_COVERAGE",
        "private_rom_seed_file": str(miss_path),
        "interpreted_rom_seed_entries": len(seed_lines),
        "original_hardware_parity_verified": False,
        "independent_gameplay_or_release_qa": False,
        "strict_semantic_prg_credit_added": 0,
    }
    (out / "compiled_product_acceptance.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if not coverage_ok:
        native = stats["native"]
        raise ValueError(
            f"same-machine frames MATCHED, but compiled PRG {prg_percent}% "
            f"below required {minimum_prg_percent}%; "
            f"interpreted ROM={native['interpreted_rom_cpu_cycles']} CPU cycles, "
            f"interpreted CPU RAM={native['interpreted_cpu_ram_cycles']}, "
            f"compiled RAM views={native['compiled_ram_view_cpu_cycles']}; "
            f"{len(seed_lines)} bank-qualified PRG seeds. "
            f"Private breakdown: {out / 'compiled_product_acceptance.json'}"
        )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", required=True, type=Path)
    parser.add_argument("--rom", required=True, type=Path)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--frames", type=int, default=2100)
    parser.add_argument("--edition", choices=("original", "enhanced"), default="enhanced")
    parser.add_argument("--min-compiled-prg-percent", type=float, default=90.0)
    options = parser.parse_args()
    report = verify(options.exe.resolve(), options.rom.resolve(),
                    options.input.resolve(), options.out.resolve(),
                    options.frames, options.edition, options.min_compiled_prg_percent)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, UnicodeError,
            subprocess.TimeoutExpired) as exc:
        print(f"CVIII compiled product acceptance FAILED: {exc}", file=sys.stderr)
        raise SystemExit(2)
