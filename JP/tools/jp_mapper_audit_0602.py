#!/usr/bin/env python3
"""JP0602: validate frame-end mapper/palette records against PPU evidence.

Original JP gameplay traces stay on the owner's machine. No ROM, graphics,
or executable is accepted or emitted by this reader. All self-tests synthetic.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
from pathlib import Path

FIELDS = ("sample", "frame", "mode", "ctrl") + tuple(
    f"bank{i}" for i in range(8)
) + ("palette32", "mapper_match")
PALETTE = re.compile(r"^[0-9A-Fa-f]{64}$")


def inspect_csv(source: str, expected_frames: list[int]) -> dict:
    """Fail closed for malformed/out-of-sync evidence, count real mismatches."""
    if not expected_frames or any(frame != 1 + 60 * i for i, frame in enumerate(expected_frames)):
        raise ValueError("Original PPU frame list is not contiguous 1-in-60 sampling")
    reader = csv.DictReader(io.StringIO(source))
    if tuple(reader.fieldnames or ()) != FIELDS:
        raise ValueError("Unexpected JP0599 mapper/palette CSV header")
    failures = 0
    encountered: set[int] = set()
    observed = 0
    for number, row in enumerate(reader, 1):
        if number > len(expected_frames):
            raise ValueError("Unexpected extra mapper sample")
        if (set(row) != set(FIELDS) or any(v is None or not v or v.strip() != v for v in row.values())):
            raise ValueError(f"Incomplete or malformed mapper record {number}")
        try:
            sample = int(row["sample"], 10)
            frame = int(row["frame"], 10)
            mode = int(row["mode"], 10)
            ctrl = int(row["ctrl"], 16)
            banks = [int(row[f"bank{i}"], 10) for i in range(8)]
        except ValueError as exc:
            raise ValueError(f"Non-numeric mapper record {number}") from exc
        if (sample != number or frame != expected_frames[number - 1] or
                not 0 <= mode <= 3 or not 0 <= ctrl <= 255 or mode != (ctrl & 3)):
            raise ValueError(f"Mapper sample/frame/control mismatch at record {number}")
        if row["mapper_match"] not in ("PASS", "FAIL") or not PALETTE.fullmatch(row["palette32"]):
            raise ValueError(f"Invalid palette or mapper status in record {number}")
        if any(bank < -1 or bank > 127 for bank in banks):
            raise ValueError(f"Physical CHR bank outside JP 0..127 at record {number}")
        if row["mapper_match"] == "PASS" and -1 in banks:
            raise ValueError("Mapper reports PASS without eight resolved physical banks")
        if row["mapper_match"] == "FAIL":
            failures += 1
        encountered.update(bank for bank in banks if bank >= 0)
        observed += 1
    if observed != len(expected_frames):
        raise ValueError("Missing JP0599 mapper snapshots for sampled PPU frames")
    return {
        "schema": "CVIII-JP-mapper-frame-alignment/v1",
        "mapper_samples": observed,
        "mapper_mismatch_samples": failures,
        "mapper_parity_observed": failures == 0,
        "distinct_end_of_frame_chr_pages": sorted(encountered),
        "scope": "Sampled frame-end VRC6 register mapping, not mid-frame pattern fetches",
    }


def smoke() -> None:
    def sample(n: int, match: str = "PASS") -> dict[str, str]:
        row = {"sample": str(n), "frame": str(1 + 60 * (n - 1)),
               "mode": "2", "ctrl": "22", "palette32": "1A" * 32,
               "mapper_match": match}
        row.update({f"bank{i}": str(i + 10) for i in range(8)})
        return row

    def encode(rows: list[dict[str, str]]) -> str:
        target = io.StringIO()
        writer = csv.DictWriter(target, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        return target.getvalue()

    a, b = sample(1), sample(2)
    good = encode([a, b])
    outcome = inspect_csv(good, [1, 61])
    assert outcome["mapper_samples"] == 2
    assert outcome["mapper_mismatch_samples"] == 0
    assert outcome["distinct_end_of_frame_chr_pages"] == list(range(10, 18))
    broken_mapping = inspect_csv(encode([a, sample(2, "FAIL")]), [1, 61])
    assert not broken_mapping["mapper_parity_observed"]
    for bad, frames in (
        (encode([a]), [1, 61]),
        (encode([a, b]), [1]),
        (encode([a, b]), [1, 121]),
        (encode([dict(a, sample="2"), b]), [1, 61]),
        (encode([dict(a, frame="61"), b]), [1, 61]),
        (encode([dict(a, ctrl="23"), b]), [1, 61]),
        (encode([dict(a, palette32="ZZ" * 32), b]), [1, 61]),
        (encode([dict(a, bank0="128"), b]), [1, 61]),
        (encode([dict(a, bank0="-1"), b]), [1, 61]),
        (encode([dict(a, mapper_match="UNKNOWN"), b]), [1, 61]),
        (good.replace("bank3", "bank9", 1), [1, 61]),
    ):
        try:
            inspect_csv(bad, frames)
        except ValueError:
            continue
        raise AssertionError("Bad JP0599 mapper trace unexpectedly accepted")
    print("PASS JP0602 mapper audit: complete frame alignment, bank/palette validation, mismatch gate")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--smoke", action="store_true")
    group.add_argument("--csv", type=Path)
    p.add_argument("--frames", help="Comma-separated sampled frame IDs; for isolated checks")
    args = p.parse_args()
    if args.smoke:
        smoke()
        return
    if not args.frames:
        p.error("--frames is required with --csv")
    try:
        frames = [int(f) for f in args.frames.split(",")]
        print(json.dumps(inspect_csv(args.csv.read_text(encoding="utf-8"), frames), indent=2))
    except (ValueError, OSError) as exc:
        p.exit(1, str(exc) + "\n")


if __name__ == "__main__":
    main()
