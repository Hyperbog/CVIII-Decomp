#!/usr/bin/env python3
"""JP0641: deterministic replay *preflight*; never claims original gameplay.

No subprocess runs. Source-only, ROM-free CI; private media/binaries are optional
owner-local inputs authenticated before later independent replay phases.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROM_SHA = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
SCHEMA = "CVIII-JP-replay-scenario/v1"
REPORT = "CVIII-JP-replay-preflight/v1"
HEX = re.compile(r"[0-9a-f]{64}\Z")
NAME = re.compile(r"[a-z][a-z0-9-]{2,47}\Z")
BUTTONS = {"START", "SELECT", "A", "B", "UP", "DOWN", "LEFT", "RIGHT"}
LIMIT = 1 << 20


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fp:
        for buf in iter(lambda: fp.read(262144), b""):
            h.update(buf)
    return h.hexdigest()


def unique_json(raw: str) -> dict:
    def pairs(items):
        result = {}
        for k, v in items:
            if k in result:
                raise ValueError("duplicate JSON key: " + k)
            result[k] = v
        return result
    value = json.loads(raw, object_pairs_hook=pairs)
    if not isinstance(value, dict):
        raise ValueError("manifest must be a JSON object")
    return value


def keys(obj: object, expected: set[str], title: str) -> None:
    if not isinstance(obj, dict) or set(obj) != expected:
        raise ValueError(title + " must contain exactly: " + ", ".join(sorted(expected)))


def local_file(path: Path, *, limit: int = LIMIT) -> Path:
    if path.is_symlink() or not path.is_file():
        raise ValueError("missing or symlinked evidence file: " + path.name)
    if not 0 < path.stat().st_size <= limit:
        raise ValueError("empty or oversized evidence file: " + path.name)
    return path


def child_file(parent: Path, name: str) -> Path:
    if (not isinstance(name, str) or not NAME.fullmatch(name.rsplit(".", 1)[0])
            or not re.fullmatch(r"[a-z][a-z0-9-]{2,47}\.txt", name)):
        raise ValueError("input file must be a single safe lowercase .txt filename")
    return local_file(parent / name)


def input_events(data: bytes, frames: int) -> dict:
    try:
        content = data.decode("ascii")
    except UnicodeDecodeError as exc:
        raise ValueError("input schedule must be ASCII") from exc
    last = -1
    count = 0
    for line_no, line in enumerate(content.splitlines(), 1):
        if not line or line.startswith("#"):
            continue
        if "\t" in line or line.strip() != line:
            raise ValueError(f"schedule line {line_no}: unexpected whitespace")
        parts = line.split(" ")
        if len(parts) != 2 or not re.fullmatch(r"(?:0|[1-9][0-9]*)", parts[0]):
            raise ValueError(f"schedule line {line_no}: expected FRAME BUTTONS")
        frame = int(parts[0])
        if not last < frame < frames:
            raise ValueError(f"schedule line {line_no}: frame out of range or reordered")
        sequence = parts[1].split("+")
        if parts[1] != "-" and (not sequence or any(b not in BUTTONS for b in sequence)
                                      or len(sequence) != len(set(sequence))):
            raise ValueError(f"schedule line {line_no}: invalid/repeated button")
        last, count = frame, count + 1
    if count == 0:
        raise ValueError("empty controller schedule")
    return {"events": count, "last_input_frame": last,
            "schedule_parser": "JP0641 strict subset"}


def manifest(path: Path) -> tuple[dict, dict]:
    path = local_file(path, limit=65536)
    data = unique_json(path.read_text(encoding="utf-8"))
    keys(data, {"schema", "id", "rom_sha256", "frames", "start", "config",
                "input", "reference", "native"}, "scenario")
    if data["schema"] != SCHEMA or not isinstance(data["id"], str) or not NAME.fullmatch(data["id"]):
        raise ValueError("scenario schema or ID invalid")
    if data["rom_sha256"] != ROM_SHA:
        raise ValueError("non-Japanese original ROM identity in scenario")
    frames = data["frames"]
    if type(frames) is not int or not 1 <= frames <= 12000:
        raise ValueError("frames must be an integer in 1..12000")
    keys(data["start"], {"type"}, "start")
    if data["start"]["type"] != "power_on":
        raise ValueError("JP0641 only supports fresh power-on (no shared savestates)")
    keys(data["config"], {"ppu", "edition"}, "config")
    if data["config"] != {"ppu": "LLE", "edition": "Original"}:
        raise ValueError("JP0641 baseline requires LLE and internal Original presentation")
    keys(data["input"], {"file", "sha256", "format"}, "input")
    if data["input"]["format"] != "nesrecomp-frame-schedule/v1":
        raise ValueError("unrecognized native input format")
    for role, engine in (("reference", "mesen2"), ("native", "nesrecomp-cycle")):
        keys(data[role], {"engine", "sha256"}, role)
        pin = data[role]["sha256"]
        if data[role]["engine"] != engine or (pin is not None and
            (not isinstance(pin, str) or not HEX.fullmatch(pin))):
            raise ValueError("invalid engine or executable fingerprint: " + role)
    pin = data["input"]["sha256"]
    if not isinstance(pin, str) or not HEX.fullmatch(pin):
        raise ValueError("input schedule hash must be exact lowercase SHA-256")
    schedule = child_file(path.parent, data["input"]["file"])
    raw = schedule.read_bytes()
    if hashlib.sha256(raw).hexdigest() != pin:
        raise ValueError("controller schedule digest mismatch")
    return data, input_events(raw, frames)


def preflight(source: Path, *, rom: Path | None = None,
              reference: Path | None = None, native: Path | None = None) -> dict:
    result: dict = {"schema": REPORT, "status": "FAIL", "checks": {},
                    "gameplay_parity_proved": False, "strict_new_prg_bytes": 0,
                    "new_vpp_points": 0}
    checks = result["checks"]
    checks.update(manifest_and_input="FAIL",
                  retail_rom="NOT_EXERCISED",
                  reference_executable="NOT_EXERCISED",
                  native_executable="NOT_EXERCISED")
    try:
        data, schedule = manifest(source)
        result.update(scenario_id=data["id"], frames=data["frames"],
                      scenario_sha256=sha_file(source),
                      controller_sha256=data["input"]["sha256"],
                      input_contract=schedule)
        checks["manifest_and_input"] = "PASS"
        if rom is None:
            checks["retail_rom"] = "NOT_EXERCISED"
        else:
            # Import the existing strict JP retail cartridge header/mapper/size gate.
            from nesrecomp_cycle_0568 import authenticated
            checks["retail_rom"] = "FAIL"
            original = local_file(rom, limit=400000)
            result["rom"] = authenticated(original)
            checks["retail_rom"] = "PASS"
        for role, provided in (("reference", reference), ("native", native)):
            if provided is None:
                checks[role + "_executable"] = "NOT_EXERCISED"
                continue
            checks[role + "_executable"] = "FAIL"
            fingerprint = data[role]["sha256"]
            if fingerprint is None:
                raise ValueError(role + " executable provided without manifest SHA-256 pin")
            candidate = local_file(provided, limit=100000000)
            digest = sha_file(candidate)
            if digest != fingerprint:
                raise ValueError(role + " executable fingerprint mismatch")
            result[role + "_executable_sha256"] = digest
            checks[role + "_executable"] = "PASS"
        result["status"] = "PASS"
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        result["error"] = str(exc)
    for stage in ("reference_gameplay", "native_gameplay", "frame_comparison",
                  "cpu_trace_comparison", "rendering_parity"):
        checks[stage] = "NOT_EXERCISED"
    return result


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--rom", type=Path)
    p.add_argument("--reference-exe", type=Path)
    p.add_argument("--native-exe", type=Path)
    p.add_argument("--out", type=Path)
    a = p.parse_args()
    record = preflight(a.manifest, rom=a.rom,
                       reference=a.reference_exe, native=a.native_exe)
    text = json.dumps(record, indent=2, sort_keys=True) + "\n"
    if a.out is not None:
        a.out.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0 if record["status"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
