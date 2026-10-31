#!/usr/bin/env python3
"""Validate the one permanent, Japanese-ROM-derived-only reference index."""
import csv
import re
from pathlib import Path

MASTER = Path(__file__).with_name("NES_Recomp_Master_Reference.csv")
DOMAINS = {"PRG", "LEVELS", "CHR", "METATILES", "VRC6"}
HEADERS = [
    "Domain", "Rows", "Canonical_Export", "Workbook_Sheet", "CSV_SHA256",
    "Verification_Scope", "Availability", "Last_Indexed_UTC",
]
FORBIDDEN = re.compile(
    r"\b(?:TAS|BK2|FCM|MesenCE|BizHawk|debugger|snapshot|capture|emulator trace|controller callback)\b",
    re.I,
)

def validate():
    source = MASTER.read_text(encoding="utf-8")
    assert not FORBIDDEN.search(source), "Non-ROM evidence in permanent master CSV"
    with MASTER.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        assert reader.fieldnames == HEADERS, "Permanent master schema changed"
        rows = list(reader)
    names = [row["Domain"] for row in rows]
    assert len(names) == len(set(names)) == 5 and set(names) == DOMAINS, "Non-ROM or duplicate domain"
    for row in rows:
        domain = row["Domain"]
        assert row["Workbook_Sheet"] == domain
        assert row["Canonical_Export"] == domain + ".csv"
        assert row["Rows"].isdigit() and int(row["Rows"]) > 0
        assert re.fullmatch(r"[a-f0-9]{64}", row["CSV_SHA256"])
        assert row["Verification_Scope"].startswith("Japanese ROM")
        assert row["Availability"] == "owner-local"
        assert re.fullmatch(r"20[0-9]{2}-[01][0-9]-[0-3][0-9]", row["Last_Indexed_UTC"])
    assert next(int(row["Rows"]) for row in rows if row["Domain"] == "VRC6") == 12, "Runtime traces reintroduced"
    print("PASS: five ROM-derived domains, no TAS or emulator runtime records")

if __name__ == "__main__":
    validate()
