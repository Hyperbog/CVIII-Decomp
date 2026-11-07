#!/usr/bin/env python3
"""JP0651: fail-closed classification of JP0650 exception-only DMC sidecar.

This validates held CPU addresses, not original ROM bytes. The returned set
contains only fetch ordinals whose actual bus bytes differ from PRG and whose
conflict context is independently accounted for. No guest state is changed.
"""
from __future__ import annotations
import csv
import io

COLUMNS = [
    "epoch", "cycle", "dmc_addr", "physical", "held_cpu_addr",
    "cpu_reading", "register_alias", "alias_conditions_met",
]
CAP = 200000


def unsigned(value: str) -> int:
    if not value or value.strip() != value or not value.isascii() or not value.isdecimal():
        raise ValueError("Noncanonical unsigned JP0650 conflict value")
    result = int(value)
    if result > 0xFFFFFFFFFFFFFFFF:
        raise ValueError("JP0650 conflict value exceeds uint64")
    return result


def classified_ordinals(
    native_fetches: list[tuple[int, int, int, int]],
    prg: bytes,
    sidecar: str | None,
) -> frozenset[int]:
    """Match every native ROM-byte exception to one same-session, in-order row."""
    exceptions = [
        (index, fetch) for index, fetch in enumerate(native_fetches)
        if fetch[3] != prg[fetch[2]]
    ]
    if sidecar is None:
        if exceptions:
            raise ValueError("Native DMC byte differences require JP0650 conflict sidecar")
        return frozenset()

    try:
        reader = csv.DictReader(io.StringIO(sidecar), strict=True)
        if reader.fieldnames != COLUMNS:
            raise ValueError("Invalid JP0650 conflict sidecar schema")
        rows = []
        for row in reader:
            if None in row or any(v is None for v in row.values()):
                raise ValueError("Missing or extra JP0650 sidecar fields")
            rows.append(row)
            if len(rows) > CAP:
                raise ValueError("Oversized JP0650 conflict sidecar")
    except csv.Error as exc:
        raise ValueError("Malformed JP0650 conflict sidecar CSV") from exc
    if len(rows) != len(exceptions):
        raise ValueError(
            f"JP0650 sidecar count {len(rows)} does not cover "
            f"{len(exceptions)} native ROM-byte exceptions"
        )

    for row, (index, fetch) in zip(rows, exceptions):
        values = {key: unsigned(row[key]) for key in COLUMNS}
        cycle, addr, physical, _actual = fetch
        held = values["held_cpu_addr"]
        alias = 0x4000 | (addr & 0x1F)
        if not (
            values["epoch"] == 1
            and values["cycle"] == cycle
            and values["dmc_addr"] == addr
            and values["physical"] == physical
            and 0x4000 <= held <= 0x401F
            and values["cpu_reading"] == 1
            and 0x4015 <= alias <= 0x4017
            and values["register_alias"] == alias
            and values["alias_conditions_met"] == 1
        ):
            raise ValueError(
                f"Unverified JP0650 held-CPU DMA conflict at native fetch #{index}"
            )
    return frozenset(index for index, _fetch in exceptions)
