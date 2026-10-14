#!/usr/bin/env python3
"""JP0611 ROM-locked, non-liveness census of calls to sound entry $E249.

Scans PHYSICAL PRG bytes, including potential data false positives.  This is
not a 6502 CFG, a music/SFX attribution, or an executable sound emulator.
Does not extract sound payloads or make any changes to game audio.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

JP_SHA256 = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
ROM_SIZE = 393232
PRG_SIZE = 262144
# The 6502 program counter uses fixed PRG31:$E249, which restores the
# bank after calling raw-$0C:$8850. These are original-JP byte witnesses.
WITNESSES = (
    ("fixed_E249", 31, 0xE249, 27, "5a5d7b8a0f857c8062faee305b4d752522f281bda0271e402cd4c66759b37324"),
    ("raw0C_8850", 24, 0x8850, 15, "848ae942487e859efb2d937c69e6b151bdd55cc5c118b804321a5cb52436e0d8"),
    ("raw0C_8908", 24, 0x8908, 78, "1e54134add843940335ffe23f13a988643e505bdbffc2f20496be5d67ed0269b"),
    ("raw0A_B58C", 21, 0xB58C, 11, "753c598e794761b9ac19ae468525ee15991d0ce4cf91f68db97570d908ae83dd"),
)
CALL_BYTES = {"JSR": bytes.fromhex("20 49 E2"), "JMP": bytes.fromhex("4C 49 E2")}
EXPECTED = {"JSR": (123, 115), "JMP": (8, 5)}  # (candidate bytes, LDA-immediate prefix)


def physical_offset(bank: int, cpu: int) -> int:
    """Returns offset within PRG, with CPU address based on physical mapping."""
    if not 0 <= bank < 32:
        raise ValueError("invalid physical bank")
    base = (0xE000 if bank == 31 else 0xC000 if bank == 30
            else 0x8000 + (bank & 1) * 0x2000)
    if not base <= cpu < base + 0x2000:
        raise ValueError("invalid CPU address for physical bank")
    return bank * 0x2000 + cpu - base


def check_witnesses(prg: bytes) -> None:
    if len(prg) != PRG_SIZE:
        raise ValueError("expected exactly 256 KiB JP PRG")
    for name, bank, cpu, count, digest in WITNESSES:
        at = physical_offset(bank, cpu)
        if sha256(prg[at:at + count]).hexdigest() != digest:
            raise ValueError(f"JP sound witness changed: {name}")
    wrapper = prg[physical_offset(31, 0xE249):physical_offset(31, 0xE249) + 27]
    if wrapper != bytes.fromhex(
        "48 a9 ff 85 26 a5 23 85 25 a9 0c 20 d0 e2 68 20 50 88"
        " a9 00 85 26 a5 25 4c d0 e2"
    ):
        raise ValueError("fixed mapper-restoring wrapper changed")
    dispatch = prg[physical_offset(24, 0x8850):physical_offset(24, 0x8850) + 15]
    if dispatch != bytes.fromhex("85 ef c9 6f 90 03 4c 08 89 c9 50 90 e5 20 ae"):
        raise ValueError("sound dispatch branch bytecode changed")
    dmc = prg[physical_offset(24, 0x8908):physical_offset(24, 0x8908) + 78]
    if not all(p in dmc for p in (
        bytes.fromhex("8d 15 40"), bytes.fromhex("8d 10 40"),
        bytes.fromhex("8d 11 40"), bytes.fromhex("8d 12 40"),
        bytes.fromhex("8d 13 40")
    )):
        raise ValueError("DMC register writes changed")


def dispatch_class(command: int) -> str:
    if command < 0x50:
        return "low_command_8842"
    if command < 0x6F:
        return "record_install_885D"
    return "dmc_path_8908"


def locate(prg_offset: int) -> dict:
    bank, local = divmod(prg_offset, 0x2000)
    if bank == 31:
        window, cpu = "fixed_E000", 0xE000 + local
    elif bank == 30:
        window, cpu = "prg30_C000", 0xC000 + local
    else:
        window, cpu = f"raw{bank // 2:02X}_window", 0x8000 + (bank % 2) * 0x2000 + local
    return {"prg_offset": f"{prg_offset:05X}", "physical_prg_bank": bank,
            "cpu_address_if_mapped": f"{cpu:04X}", "window": window}


def census(prg: bytes) -> dict:
    check_witnesses(prg)
    entries = []
    for mnemonic, pattern in CALL_BYTES.items():
        # Nonoverlapping byte signatures; no decoding or instruction-liveness
        # assumption is made, even when preceded by A9 XX.
        for at in range(len(prg) - len(pattern) + 1):
            if prg[at:at + len(pattern)] != pattern:
                continue
            const_id = (prg[at - 1] if at >= 2 and prg[at - 2] == 0xA9
                        and at // 0x2000 == (at - 2) // 0x2000 else None)
            record = {"opcode": mnemonic, **locate(at),
                      "preceding_lda_immediate_candidate": const_id is not None}
            if const_id is not None:
                record["candidate_command_id"] = f"{const_id:02X}"
                record["dispatch_class_if_A_preserved"] = dispatch_class(const_id)
            entries.append(record)
    entries.sort(key=lambda x: int(x["prg_offset"], 16))
    totals = {name: sum(e["opcode"] == name for e in entries) for name in CALL_BYTES}
    immediate = {name: sum(e["opcode"] == name and
                           e["preceding_lda_immediate_candidate"] for e in entries)
                 for name in CALL_BYTES}
    if any((totals[name], immediate[name]) != EXPECTED[name] for name in CALL_BYTES):
        raise ValueError("JP0611 call-pattern census unexpectedly changed")
    by_class = Counter(e["dispatch_class_if_A_preserved"] for e in entries
                       if e["preceding_lda_immediate_candidate"])
    by_bank = Counter(e["physical_prg_bank"] for e in entries)
    return {
        "jp_sha256": JP_SHA256, "kind": "ROM physical pattern candidates only",
        "counted_sites_are_live_execution": False,
        "prefix_proves_accumulator_on_entry": False,
        "sound_request_call_candidates": sum(totals.values()),
        "opcode_pattern_counts": totals,
        "preceding_LDA_immediate_candidates": immediate,
        "no_immediate_prefix": sum(totals.values()) - sum(immediate.values()),
        "candidate_dispatch_classes": dict(sorted(by_class.items())),
        "candidate_sites_by_physical_prg_bank": dict(sorted(by_bank.items())),
        "candidates": entries,
    }


def load_rom(path: Path) -> bytes:
    image = path.read_bytes()
    if len(image) != ROM_SIZE or sha256(image).hexdigest() != JP_SHA256:
        raise ValueError("requires unmodified 393232-byte Japanese Mapper-24 ROM")
    if image[:16] != bytes.fromhex("4e45531a101080100000000000000000"):
        raise ValueError("unexpected JP iNES header")
    return image[16:16 + PRG_SIZE]


def self_test(prg: bytes) -> None:
    result = census(prg)
    assert result["sound_request_call_candidates"] == 131
    assert result["no_immediate_prefix"] == 11
    assert result["candidate_dispatch_classes"] == {
        "dmc_path_8908": 12, "low_command_8842": 91,
        "record_install_885D": 17,
    }
    for name, bank, cpu, _count, _digest in WITNESSES:
        broken = bytearray(prg)
        broken[physical_offset(bank, cpu)] ^= 1
        try:
            census(bytes(broken))
        except ValueError:
            continue
        raise AssertionError("failed to reject damaged JP witness " + name)
    assert dispatch_class(0x4F) == "low_command_8842"
    assert dispatch_class(0x50) == "record_install_885D"
    assert dispatch_class(0x6E) == "record_install_885D"
    assert dispatch_class(0x6F) == "dmc_path_8908"
    print("PASS JP0611 ROM-locked 131-site mechanical census; 4 corrupted witnesses rejected")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("rom", type=Path)
    p.add_argument("--json", type=Path, help="optional owner-local non-lossless derived candidate-site report")
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    prg = load_rom(args.rom)
    report = census(prg)
    if args.self_test:
        self_test(prg)
    if args.json:
        args.json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"JP0611 original ROM: {report['jp_sha256']}")
    print(f"Mechanical call-site bytes: {report['sound_request_call_candidates']}"
          f" ({report['opcode_pattern_counts']})")
    print(f"Preceding A9 immediate patterns: {sum(report['preceding_LDA_immediate_candidates'].values())};"
          f" dynamic/unknown: {report['no_immediate_prefix']}")
    print(f"Conditional command buckets: {report['candidate_dispatch_classes']}")
    print("NOT a liveness, priority, caller provenance, music/SFX, or playback proof")


if __name__ == "__main__":
    main()
