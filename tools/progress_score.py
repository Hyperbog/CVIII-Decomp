#!/usr/bin/env python3
"""Validate and print the repository's Verified Parity Progress score."""
from __future__ import annotations
import csv
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    path = root / "analysis" / "PROGRESS_SCORE.csv"
    rows = list(csv.DictReader(path.open(newline="", encoding="utf-8")))
    weight = sum(int(row["weight"]) for row in rows)
    earned = sum(int(row["earned"]) for row in rows)
    if weight != 100:
        raise SystemExit(f"ERROR: VPP weights total {weight}, expected 100")
    for row in rows:
        w = int(row["weight"])
        e = int(row["earned"])
        if e < 0 or e > w:
            raise SystemExit(f"ERROR: invalid score for {row['category']}: {e}/{w}")
    print(f"Verified Parity Progress: {earned}/100 ({earned}%)")
    for row in rows:
        print(f"  {row['category']}: {row['earned']}/{row['weight']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
