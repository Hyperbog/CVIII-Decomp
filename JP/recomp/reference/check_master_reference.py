#!/usr/bin/env python3
"""Validate the permanent NES Recomp reference catalog without private ROM data."""
import csv
import re
from pathlib import Path

CATALOG = Path(__file__).with_name("NES_Recomp_Master_Reference.csv")
DOMAINS = {"PRG", "PPU", "CHR", "OAM", "VRC6", "CPU_RAM", "LEVELS", "TAS", "DOCUMENTS", "SOURCES"}
HEADERS = ["Domain", "Rows", "Canonical_Export", "Workbook_Sheet", "CSV_SHA256", "Verification_Scope", "Availability", "Last_Indexed_UTC"]

def validate():
    with CATALOG.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == HEADERS, "Master reference header changed"
        rows = list(reader)
    names = [row["Domain"] for row in rows]
    assert len(names) == len(set(names)) == 10 and set(names) == DOMAINS, "Missing or duplicate reference domain"
    for row in rows:
        domain = row["Domain"]
        assert row["Workbook_Sheet"] == domain and row["Canonical_Export"] == domain + ".csv", domain
        assert row["Rows"].isdigit() and int(row["Rows"]) > 0, domain
        assert re.fullmatch(r"[0-9a-f]{64}", row["CSV_SHA256"]), domain
        assert row["Verification_Scope"].strip() and row["Availability"] == "owner-local", domain
        assert re.fullmatch(r"20[0-9]{2}-[01][0-9]-[0-3][0-9]", row["Last_Indexed_UTC"]), domain
    print(f"PASS: permanent master index, {len(rows)} unique domains")

if __name__ == "__main__":
    validate()
