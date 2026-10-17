#!/usr/bin/env python3
"""JP0664: source-verified Beginning NSF -> original sound directory bridge.

This proves a STATIC ripped-NSF command mapping, not an original-game runtime
request, decoded soundtrack, music/SFX ownership, or APU/VRC6 timing parity.
All copyrighted source and FamiStudio TXT bytes stay local.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jp_famistudio_reference_0664 import census, source_identity
from jp_sound_catalog_0652 import catalog, original_bank

INIT_SHA = "dcb05368b636ff14a9125bea67fd9489bc8d78466eec0ecc7a32f326a0906aeb"
TRACK_TABLE_SHA = "6a1931c4ffa9b7e300d32264b0b461bae9d13b38935b620d5912598cb441c178"
DISPATCH_TAIL = bytes.fromhex("68 aa bd 00 e1 4c 50 88")
TRACK_COUNT = 28


def require(ok: bool, msg: str) -> None:
    if not ok:
        raise ValueError(msg)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rip_byte(nsf: bytes, cpu: int) -> int:
    """Address in NSF's HEADER-declared initial virtual 4KiB mapping."""
    require(len(nsf) >= 128 and 0x8000 <= cpu <= 0xFFFF,
            "invalid NSF virtual read")
    bank_index = (cpu >> 12) - 8
    bank = nsf[0x70 + bank_index]
    position = 128 + bank * 0x1000 + (cpu & 0xFFF)
    require(position < len(nsf), "NSF virtual address outside payload")
    return nsf[position]


def selected_id(init: bytes, table: bytes, index: int, authentic: bool) -> int:
    require(0 <= index < TRACK_COUNT and len(init) == 32 and
            len(table) == TRACK_COUNT, "invalid track/header source span")
    require(init[21:29] == DISPATCH_TAIL,
            "NSF wrapper does not pull track index and dispatch table byte")
    if authentic:
        require(digest(init) == INIT_SHA and digest(table) == TRACK_TABLE_SHA,
                "modified NSF init code or song selection table")
    result = table[index]
    require(1 <= result <= 0x7D, "selected command outside authenticated sound directory")
    return result


def bridge(rom: bytes, nsf: bytes, m3u: bytes, txt: bytes,
           owner_confirmed: bool) -> dict:
    proof = source_identity(rom, nsf, m3u, 0)
    reference = census(txt, 0, rom, nsf)
    init = bytes(rip_byte(nsf, a) for a in range(0xE0E0, 0xE100))
    table = bytes(rip_byte(nsf, a) for a in range(0xE100, 0xE100 + TRACK_COUNT))
    command = selected_id(init, table, 0, True)
    require(command == 0x51, "Beginning NSF command selection changed")
    # NSF payload banks 4–7 are byte-identical copies of physical raw05.
    # This specifically protects the six original $51 program source roots.
    raw05 = rom[16 + 5 * 0x4000:16 + 6 * 0x4000]
    nsf05 = nsf[128 + 4 * 0x1000:128 + 8 * 0x1000]
    require(len(raw05) == 0x4000 and raw05 == nsf05,
            "original $51 source bank 05 is not byte-identical in NSF")
    original = catalog(original_bank(rom), authenticate=True)
    entry = original["entries"][command - 1]
    require(entry["original_sound_id"] == "51" and
            entry["structural_kind"] == "banked_reference_list" and
            entry["raw_variant"] == "05" and len(entry["references"]) == 6,
            "authenticated original sound program $51 changed")
    require(all(r["raw_prg_bank16"] == "05" for r in entry["references"]),
            "original song source bank mismatch")

    return {
        "schema": "jp0664-beginning-nsf-original-command-bridge/v1",
        "reference_track": "Beginning (Block-1)",
        "reference_track_confirmed_by_owner": owner_confirmed,
        "nsf_track_one_based": 1,
        "nsf_track_zero_based": 0,
        "rip_initialization_table_sha256": TRACK_TABLE_SHA,
        "rip_wrapper_sha256": INIT_SHA,
        "nsf_rip_selected_command_hex": f"{command:02X}",
        "nsf_rip_command_mapping_evidence": "exact NSF wrapper and lookup bytes, not original game execution",
        "original_command_id_hex": entry["original_sound_id"],
        "original_sound_directory_verified": True,
        "original_program_bank05_byte_identical_in_nsf": True,
        "original_program_variant_raw_bank16": entry["raw_variant"],
        "original_program_source_reference_count": len(entry["references"]),
        "original_program_refs_are_opaque_not_verified_voices": True,
        "reference_famistudio_version": reference["famistudio_version"],
        "reference_famistudio_txt_sha256": reference["famistudio_txt_sha256"],
        "reference_active_channels": reference["active_channel_count"],
        "reference_note_trigger_rows": reference["total_note_triggers"],
        "reference_dpcm_sample_matches_both_sources":
            reference["dpcm_payloads_matching_both_original_rom_and_nsf"],
        "authenticated_source_rom_sha256": proof["original_rom_sha256"],
        "original_game_sound_command_liveness": "not_exercised",
        "famistudio_note_to_original_stream_opcode_parity": "not_exercised",
        "independent_music_sfx_playback": "not_implemented",
    }


def smoke() -> None:
    # Invented track table values, never derived from original code/data.
    init = bytes(21) + DISPATCH_TAIL + bytes(3)
    table = bytes(i + 1 for i in range(TRACK_COUNT))
    require(selected_id(init, table, 0, False) == 1,
            "synthetic first track selection failed")
    require(selected_id(init, table, 27, False) == 28,
            "synthetic final track selection failed")
    invalid = [
        (init[:21] + bytes(8) + init[29:], table, 0),
        (init[:-1], table, 0),
        (init, table[:-1], 0),
        (init, bytes([0]) + table[1:], 0),
        (init, table, -1),
        (init, table, 28),
        (init, bytes([0x7E]) + table[1:], 0),
    ]
    for k, (code, ids, index) in enumerate(invalid):
        try:
            selected_id(code, ids, index, False)
        except ValueError:
            continue
        raise AssertionError(f"invalid artificial command selector accepted: {k}")
    print(f"PASS JP0664 synthetic ripped-NSF selector and {len(invalid)} negative cases")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--rom", type=Path)
    parser.add_argument("--nsf", type=Path)
    parser.add_argument("--m3u", type=Path)
    parser.add_argument("--famistudio-txt", type=Path)
    parser.add_argument("--owner-confirmed", action="store_true",
                        help="record explicit owner statement; not inferred from TXT")
    parser.add_argument("--json", type=Path, help="private compact metadata-only output")
    args = parser.parse_args()
    if args.smoke:
        smoke()
        if not args.rom:
            return
    if not all((args.rom, args.nsf, args.m3u, args.famistudio_txt)):
        parser.error("--rom --nsf --m3u --famistudio-txt are required together")
    out = bridge(args.rom.read_bytes(), args.nsf.read_bytes(),
                 args.m3u.read_bytes(), args.famistudio_txt.read_bytes(),
                 args.owner_confirmed)
    if args.json:
        args.json.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n",
                             encoding="utf-8")
    print("PASS JP0664 static NSF track 1 -> $51 -> original bank05 / six references;"
          " original game liveness NOT EXERCISED")


if __name__ == "__main__":
    main()
