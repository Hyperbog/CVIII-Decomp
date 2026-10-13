#!/usr/bin/env python3
"""JP 0593: ROM-authenticated Castlevania III Japanese stage/password study.

This ROM-free source reads owner-supplied original JP cartridge locally.
The password algorithm is modeled independently using the observed JP ROM
constants plus published USA/PAL research as an *unverified JP algorithm
hypothesis*. The JP decoder/level transition has NOT been game-replayed.
No game ROM, generated game instructions, or password graphic is embedded.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

JP_SHA = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
# JP ROM offset is 16-byte iNES header + the 256 KiB PRG offset below.
# All are JP mapper24 physical PRG bank 03 except the save-point table, bank 00.
JP_TABLES = {
    "scrambles": (0x078DD, 27),
    "name_seeds": (0x07911, 8),
    "selectors": (0x07B62, 9),
    "leaders": (0x07A0A, 3),
    "valid_partners": (0x07AE1, 6),
    "save_points": (0x00EF1, 45),
}
# ROM-grounded values to reject a wrong mapped bank or coincidental match.
EXPECTED = {
    "scrambles": bytes.fromhex("00 33 20 13 22 01 11 03 32 12 10 02 32 23 13 30 21 01 31 13 01 22 10 30 33 03 21"),
    "name_seeds": bytes.fromhex("07 03 01 06 02 04 05 00"),
    "selectors": bytes.fromhex("01 1B 02 35 19 03 37 1A 36"),
    "leaders": bytes.fromhex("00 12 31"),
    "valid_partners": bytes.fromhex("07 03 2F FF 00 3D"),
    "save_points": bytes.fromhex("10 00 00 02 01 02 10 03 04 10 05 05 10 06 06 10 07 07 10 08 08 04 09 0A 10 0B 0B 10 0C 0C 10 0D 0D 10 0E 0E 10 0F 0F 10 10 10 10 11 11"),
}
# Each save point is a stage checkpoint, not an arbitrary in-level screen.
# The two 6-1 entries are distinct physical routes.
STAGES = (
    "1-01 Warakiya Village", "2-01 Clock Tower ascent", "2-04 Clock Tower descent",
    "3-00 Forest from village", "3-01 Forest from Clock Tower",
    "4-0A Haunted Ship", "5-0A Tower of Terror", "6-0A Causeway",
    "4-01 Marsh", "5-01 Caves entrance", "5-06 Caves exit",
    "6-01 Sunken City", "6-01 Castle Basement", "7-01 Mountain",
    "7-0A Lookout Tower", "8-01 Castle Entrance", "9-01 Villa",
    "A-01 Castle Keep",
)
PARTNERS = ("none", "sypha", "grant", "alucard")
MARKS = ".WRH"  # '.' blank, W whip, R rosary/cross, H heart


def load_tables(path: Path) -> dict[str, bytes]:
    cart = path.read_bytes()
    if len(cart) != 393232 or hashlib.sha256(cart).hexdigest() != JP_SHA:
        raise ValueError("Original Japanese VRC6a ROM SHA-256 / length mismatch")
    if cart[:4] != b"NES\x1a" or cart[4:6] != bytes([16, 16]):
        raise ValueError("Not the expected JP iNES PRG/CHR layout")
    tables = {name: cart[16 + start:16 + start + n]
              for name, (start, n) in JP_TABLES.items()}
    for name, data in tables.items():
        if data != EXPECTED[name]:
            raise ValueError(f"Japanese ROM {name} table disagrees with pinned evidence")
    return tables


def name_hash(name: str, seeds: bytes) -> int:
    if len(name) > 8 or name != name.upper():
        raise ValueError("Name must contain at most 8 uppercase characters")
    padded = name.ljust(8)
    def tile(c: str) -> int:
        if c == " ": return 0
        if c == ".": return 0x4B
        if c == "!": return 0x6A
        if c == "?": return 0x6B
        if "A" <= c <= "Z": return 0x50 + ord(c) - ord("A")
        raise ValueError(f"Unsupported original name character: {c!r}")
    return (sum(tile(c) + seeds[i] for i, c in enumerate(padded))) & 7


def valid_partner(save: int, partner: int, mode: int, tables: dict[str, bytes]) -> bool:
    if not 0 <= save < len(STAGES) or not 0 <= partner < 4 or mode not in (0, 1):
        return False
    if partner == 0 or mode == 1 or save >= 16:
        return True
    offset = (partner - 1) * 2 + (save >> 3)
    return bool(tables["valid_partners"][offset] & (0x80 >> (save & 7)))


def encoded_hash(payload: int, save: int, toggle: int) -> int:
    mask = (0x55, 0xAA)[toggle]
    def nibble_sum(byte: int) -> int:
        return ((byte >> 4) + (byte & 15)) & 15
    return (save + (nibble_sum(payload) << 4) + nibble_sum(payload ^ mask)) & 255


def scrambles(tables: dict[str, bytes]) -> tuple[tuple[int, ...], ...]:
    v = tables["scrambles"]
    return tuple(tuple(v[i:i+9]) for i in range(0, 27, 9))


def encode(name: str, save: int, partner: int, mode: int,
           toggle: int, tables: dict[str, bytes]) -> tuple[str, ...]:
    if toggle not in (0, 1) or not valid_partner(save, partner, mode, tables):
        raise ValueError("Invalid save point / partner / difficulty combination")
    selector = tables["selectors"][save >> 1]
    leader = (selector & 0x30) | ((selector >> 2) & 3)
    sequence = next((x for x in scrambles(tables) if x[0] == leader), None)
    if sequence is None:
        raise ValueError("JP ROM scramble table has no selector leader")
    payload = (name_hash(name, tables["name_seeds"]) << 5) | ((save & 1) << 4) | (toggle << 3) | (partner << 1) | mode
    digest = encoded_hash(payload, save, toggle)
    cells = [0] * 16
    for n, pos in enumerate(sequence):
        symbol = (selector & 3) if n == 0 else (((payload >> (n-1)) & 1) << 1) | ((digest >> (n-1)) & 1)
        cells[((pos >> 4) * 4) + (pos & 3)] = symbol
    return tuple("".join(MARKS[c] for c in cells[i:i+4]) for i in range(0, 16, 4))


def decode(name: str, matrix: tuple[str, ...], tables: dict[str, bytes]) -> dict[str, int]:
    if len(matrix) != 4 or any(len(row) != 4 or any(c not in MARKS for c in row) for row in matrix):
        raise ValueError("Expected four rows of four symbols (.WRH)")
    cells = [MARKS.index(c) for row in matrix for c in row]
    seqs = scrambles(tables)
    options = [seq for seq in seqs if cells[(seq[0] >> 4) * 4 + (seq[0] & 3)] != 0]
    if len(options) != 1:
        raise ValueError("Password must have exactly one nonblank leader")
    seq = options[0]
    used = {(i >> 4) * 4 + (i & 3) for i in seq}
    if any(cells[i] and i not in used for i in range(16)):
        raise ValueError("Unexpected password marks outside scramble")
    lead = seq[0]
    selector = (lead & 0x30) | ((lead & 3) << 2) | cells[(lead >> 4) * 4 + (lead & 3)]
    try:
        save = tables["selectors"].index(selector) * 2
    except ValueError as exc:
        raise ValueError("Invalid stage selector") from exc
    payload = digest = 0
    for i, pos in enumerate(seq[1:]):
        c = cells[(pos >> 4) * 4 + (pos & 3)]
        payload |= ((c >> 1) & 1) << i
        digest |= (c & 1) << i
    save |= (payload >> 4) & 1
    partner = (payload >> 1) & 3
    mode = payload & 1
    toggle = (payload >> 3) & 1
    if (payload >> 5) != name_hash(name, tables["name_seeds"]):
        raise ValueError("Name hash mismatch")
    if not valid_partner(save, partner, mode, tables):
        raise ValueError("Stage/partner combination invalid")
    if digest != encoded_hash(payload, save, toggle):
        raise ValueError("Password checksum invalid")
    return dict(save_point=save, partner=partner, hard_mode=mode, toggle=toggle)


def parse_password_grid(pasted: str) -> tuple[str, ...]:
    """Normalize a 4x4 password copied from text, preserving row order.

    Accept dots, W (whip), R (rosary), H (heart), and separating
    whitespace or commas. Reject any other characters, and wrong sizes.
    This parses marks only; decode() must still validate the checksum and name.
    """
    compact = re.sub(r"[\s,|;]+", "", pasted.upper())
    if len(compact) != 16 or any(c not in MARKS for c in compact):
        raise ValueError("Clipboard must contain exactly 16 password symbols: ., W, R, H")
    return tuple(compact[i:i + 4] for i in range(0, 16, 4))


def self_test(tables: dict[str, bytes]) -> int:
    cases = 0
    for name in ("", "TREVOR", "RALPH", "SYMPHONY"):
        for stage in range(18):
            for partner in range(4):
                for mode in (0, 1):
                    if not valid_partner(stage, partner, mode, tables):
                        continue
                    for toggle in (0, 1):
                        matrix = encode(name, stage, partner, mode, toggle, tables)
                        value = decode(name, matrix, tables)
                        assert value == dict(save_point=stage, partner=partner, hard_mode=mode, toggle=toggle)
                        cases += 1
    matrix = encode("TREVOR", 13, 0, 0, 0, tables)
    text = "\n".join(" ".join(row) for row in matrix)
    assert parse_password_grid(text) == matrix
    assert parse_password_grid("".join(matrix).lower()) == matrix
    for bad in ("", "W R H", "W " * 16 + "X", "W" * 15, "W" * 17):
        try:
            parse_password_grid(bad)
        except ValueError:
            pass
        else:
            raise AssertionError("Malformed pasted password accepted")
    try:
        decode("ALUCARD", matrix, tables)
    except ValueError:
        pass
    else:
        raise AssertionError("Incorrect password name was accepted")
    print(f"PASS JP authenticated tables and {cases} encode/decode roundtrips (not original-game replay)")
    return cases


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rom", type=Path, required=True, help="Locally owned original Japanese cartridge")
    p.add_argument("--stage", type=lambda s: int(s, 0), help="Save-point index: 0..17 (supports 0x hex)")
    p.add_argument("--name", default="TREVOR", help="Original game name, uppercase, maximum eight characters")
    p.add_argument("--partner", choices=PARTNERS, default="none")
    p.add_argument("--hard", action="store_true")
    p.add_argument("--toggle", type=int, choices=(0, 1), default=0)
    p.add_argument("--list", action="store_true", help="Show all 18 ROM-supported checkpoints")
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--json", action="store_true", help="Machine-readable output for future stage debug host")
    a = p.parse_args()
    tables = load_tables(a.rom)
    if a.self_test:
        self_test(tables)
    if a.list:
        for idx, label in enumerate(STAGES):
            print(f"{idx:2d} [0x{idx:02X}] {label}")
    if a.stage is not None:
        which = PARTNERS.index(a.partner)
        matrix = encode(a.name, a.stage, which, int(a.hard), a.toggle, tables)
        check = decode(a.name, matrix, tables)
        if a.json:
            print(json.dumps(dict(stage_label=STAGES[a.stage], name=a.name,
                                  symbols=matrix, **check), indent=2))
        else:
            print(f"Save point {a.stage:02X}: {STAGES[a.stage]} | {a.name} | {a.partner}")
            for row in matrix:
                print(" ".join(row))


if __name__ == "__main__":
    main()
