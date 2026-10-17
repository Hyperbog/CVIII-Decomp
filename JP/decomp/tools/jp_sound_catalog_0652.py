#!/usr/bin/env python3
"""JP0652: read-only catalog of all 125 original JP sound metadata slots.

This is a structural source importer, not an audio emulator or a music/SFX
classifier. ROM bytes are never written to the JSON output. The 16 KiB raw
bank IDs below describe physical provenance, NOT observed runtime mapping.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

ROM_SHA = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
META_SHA = "ff50c2a4cd6273ca001535a5e319a68526b7e0b7a1ab173b2ced00f5a32f7154"
STREAM_SHA = "0df689b5769e50d65d736abe77cbe5752c2b6980de172164991ef32f78d38721"
DMC_SHA = "02d705700fcb42b0b1fa7c5520e54734f8180458265f1286aa132613b4fc6b45"
ROM_SIZE, RAW_BANK_SIZE = 393232, 0x4000
PTR_BASE, DESC_BASE, DMC_DESC_BASE = 0x8F60, 0x905A, 0x9505
POOL_START, POOL_END = 0x9541, 0xA304
SLOTS, ORDINARY, DMC_SLOTS = 125, 110, 15


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(condition: bool, why: str) -> None:
    if not condition:
        raise ValueError(why)


def original_bank(rom: bytes) -> bytes:
    require(len(rom) == ROM_SIZE and sha(rom) == ROM_SHA,
            "not the authenticated original JP cartridge")
    require(rom[:4] == b"NES\x1a" and rom[4:6] == b"\x10\x10"
            and (rom[6] >> 4 | rom[7] & 0xF0) == 24,
            "not the Japanese iNES Mapper24 256KiB/128KiB cartridge")
    start = 16 + 12 * RAW_BANK_SIZE
    return rom[start:start + RAW_BANK_SIZE]


def read(bank: bytes, cpu: int, count: int = 1) -> bytes:
    require(len(bank) == RAW_BANK_SIZE and 0x8000 <= cpu < 0xC000
            and count > 0 and cpu + count <= 0xC000,
            "out-of-range physical raw0C CPU-window access")
    return bank[cpu - 0x8000:cpu - 0x8000 + count]


def physical_source(raw_bank: int, cpu: int) -> dict:
    require(raw_bank in (4, 5, 12) and 0x8000 <= cpu < 0xC000,
            "invalid bank-qualified sound source address")
    offset = raw_bank * RAW_BANK_SIZE + cpu - 0x8000
    return {"raw_prg_bank16": f"{raw_bank:02X}",
            "physical_prg_bank8": offset // 0x2000,
            "physical_prg_offset": offset,
            "conditional_cpu_address": f"{cpu:04X}"}


def catalog(bank: bytes, *, authenticate: bool) -> dict:
    require(len(bank) == RAW_BANK_SIZE, "requires exactly one physical 16KiB raw0C")
    if authenticate:
        require(sha(read(bank, PTR_BASE, POOL_START - PTR_BASE)) == META_SHA,
                "original sound directory SHA changed")
        require(sha(read(bank, POOL_START, POOL_END - POOL_START)) == STREAM_SHA,
                "original sound stream pool SHA changed")
        require(sha(read(bank, 0xA957, 60)) == DMC_SHA,
                "original DMC parameters SHA changed")

    pointers = [int.from_bytes(read(bank, PTR_BASE + 2*i, 2), "little")
                for i in range(SLOTS)]
    require(len(set(pointers)) == SLOTS, "repeated original descriptor pointers")
    claimed = bytearray(POOL_START - DESC_BASE)
    entries = []
    per_variant, per_source = Counter(), Counter()
    all_local_sources = set()

    for index, address in enumerate(pointers):
        require(DESC_BASE <= address < POOL_START, "descriptor pointer outside directory")
        variant = read(bank, address)[0]
        original_id = index + 1
        roots = []
        if index < ORDINARY:
            require(variant in (4, 5, 12), "invalid ordinary sound bank discriminator")
            count = read(bank, address + 1)[0] + 1
            require(1 <= count <= 6, "unbounded ordinary sound reference count")
            width = 2 + 3 * count
            payload = read(bank, address, width)
            for r in range(count):
                mode = payload[2 + 3*r]
                dest = int.from_bytes(payload[3 + 3*r:5 + 3*r], "little")
                require(0x8000 <= dest < 0xC000,
                        "source pointer escaped physical raw PRG CPU window")
                require((POOL_START <= dest < POOL_END) if variant == 12
                        else (0x87AE <= dest < 0xBF06),
                        "sound reference outside previously audited source pool")
                if variant == 12:
                    all_local_sources.add(dest)
                per_source[variant] += 1
                roots.append({"ordinal": r, "opaque_mode_byte": mode,
                              **physical_source(variant, dest)})
            kind = "banked_reference_list"
            special = None
        else:
            require(variant == 0 and read(bank, address + 1)[0] == 9,
                    "original DMC descriptor discriminator mismatch")
            width = 4
            target = int.from_bytes(read(bank, address + 2, 2), "little")
            require(target == 0xA957 + 4 * (index - ORDINARY),
                    "DMC program slot is not the indexed original parameter record")
            kind = "special_dmc_parameter_pointer"
            special = {"source_raw_prg_bank16": "0C",
                       "parameter_cpu_address": f"{target:04X}",
                       "parameter_physical_prg_offset": 12 * RAW_BANK_SIZE + target - 0x8000}
        require(address + width <= POOL_START, "descriptor overruns sound metadata")
        for at in range(address - DESC_BASE, address + width - DESC_BASE):
            require(claimed[at] == 0, "overlapping sound descriptors")
            claimed[at] = 1
        per_variant[variant] += 1
        entries.append({"original_sound_id": f"{original_id:02X}",
                        "internal_evidence_id": f"cviii.jp.sound.source.{original_id:02x}",
                        "record_cpu_address": f"{address:04X}",
                        "record_length": width,
                        "raw_variant": f"{variant:02X}",
                        "structural_kind": kind,
                        "references": roots,
                        "special_dmc": special})

    require(all(claimed), "sound directory has unclassified bytes")
    require(sum(len(e["references"]) for e in entries) == 325,
            "sound producer-reference count changed")
    require(per_variant == {12: 79, 4: 17, 5: 14, 0: 15},
            "original sound variant histogram changed")
    require(per_source == {12: 139, 4: 102, 5: 84},
            "original sound producer-bank histogram changed")
    require(len(all_local_sources) == 125 and min(all_local_sources) == POOL_START
            and max(all_local_sources) == POOL_END - 1,
            "original sound-stream root census changed")
    return {"schema": "cviii-jp-sound-evidence-catalog/v1",
            "evidence": "source_structure_only_no_live_gameplay_proof",
            "original_rom_sha256": ROM_SHA if authenticate else None,
            "source_metadata_sha256": META_SHA if authenticate else None,
            "source_stream_pool_sha256": STREAM_SHA if authenticate else None,
            "directory_cpu_range": "8F60-9540",
            "programs": len(entries),
            "producer_references": sum(per_source.values()),
            "physical_bank_variants": {f"{i:02X}": per_variant[i] for i in (0, 4, 5, 12)},
            "physical_source_references": {f"{i:02X}": per_source[i] for i in (4, 5, 12)},
            "actual_runtime_mapper_liveness_verified": False,
            "sound_music_sfx_ownership_verified": False,
            "entries": entries}


def artificial_bank() -> bytes:
    """Construct an original-independent, count-correct synthetic directory."""
    bank = bytearray(RAW_BANK_SIZE)
    choices = ([12] * 79) + ([4] * 17) + ([5] * 14)
    counts = ([1] * 30) + ([2] * 38) + ([3] * 11) + ([6] * 31)
    require(len(choices) == len(counts) == ORDINARY and sum(counts) == 325,
            "fixture accounting")
    # Select 125 distinct bank0C producer roots, including both endpoints.
    local = [POOL_START + i for i in range(124)] + [POOL_END - 1]
    loc = 0
    address = DESC_BASE
    for index in range(SLOTS):
        bank[PTR_BASE-0x8000+2*index:PTR_BASE-0x8000+2*index+2] = address.to_bytes(2, "little")
        if index >= ORDINARY:
            payload = bytes((0, 9)) + (0xA957+4*(index-ORDINARY)).to_bytes(2, "little")
        else:
            variant, count = choices[index], counts[index]
            payload = bytearray((variant, count-1))
            for j in range(count):
                if variant == 12:
                    dest = local[loc % len(local)]; loc += 1
                else:
                    dest = 0x87AE + ((index * 17 + j) % 0x1500)
                payload += bytes(((index+j) % 16,)) + dest.to_bytes(2, "little")
        bank[address-0x8000:address-0x8000+len(payload)] = payload
        address += len(payload)
    require(address == POOL_START, "synthetic descriptor geometry mismatch")
    # The 79 raw0C records produce 139 synthetic references spread over
    # all 125 local target roots; this proves catalog census handling only.
    return bytes(bank)


def smoke() -> None:
    baseline = bytearray(artificial_bank())
    catalog(bytes(baseline), authenticate=False)
    ptr = int.from_bytes(read(baseline, PTR_BASE, 2), "little")
    mutations = [
        (PTR_BASE + 2, baseline[PTR_BASE-0x8000]),
        (ptr, 0xFF),
        (ptr + 1, 0xFF),
        (ptr + 3, 0x00),
        (DMC_DESC_BASE + 2, 0x00),
    ]
    for cpu, replacement in mutations:
        altered = bytearray(baseline)
        altered[cpu - 0x8000] = replacement
        try:
            catalog(bytes(altered), authenticate=False)
        except ValueError:
            continue
        raise AssertionError(f"damaged artificial metadata accepted at ${cpu:04X}")
    for invalid in (b"", bytes(RAW_BANK_SIZE - 1)):
        try:
            catalog(invalid, authenticate=False)
        except ValueError:
            continue
        raise AssertionError("incorrect synthetic bank length was accepted")
    print("PASS JP0652 artificial 125-slot/325-reference catalog and tamper guards")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", type=Path, help="private authentic JP .nes")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--json", type=Path, help="metadata-only output; no sound bytes")
    options = parser.parse_args()
    if not options.rom and not options.smoke:
        parser.error("specify --smoke or --rom ORIGINAL_JP_ROM")
    if options.smoke:
        smoke()
    if options.rom:
        parsed = catalog(original_bank(options.rom.read_bytes()), authenticate=True)
        if options.json:
            options.json.write_text(json.dumps(parsed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print("PASS JP0652 original JP 125 programs, 325 source refs, 15 DMC slots")


if __name__ == "__main__":
    main()
