#!/usr/bin/env python3
"""Audit PRG06/07 direct selector-$10 and frame-$0400 setup paths."""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

EXPECTED_SHA256 = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"


def hits(data: bytes, pattern: bytes, base: int) -> list[int]:
    out: list[int] = []
    pos = 0
    while True:
        pos = data.find(pattern, pos)
        if pos < 0:
            return out
        out.append(base + pos)
        pos += 1


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {Path(sys.argv[0]).name} <Akumajou Densetsu (Japan).nes>")
        return 2

    rom = Path(sys.argv[1]).read_bytes()
    if hashlib.sha256(rom).hexdigest() != EXPECTED_SHA256:
        print("ERROR: ROM SHA-256 mismatch", file=sys.stderr)
        return 1

    prg = rom[16 : 16 + 0x40000]
    pair = prg[6 * 0x2000 : 8 * 0x2000]  # VRC6 16 KiB bank value $03
    fixed = prg[31 * 0x2000 : 32 * 0x2000]

    def at(address: int, size: int) -> bytes:
        return pair[address - 0x8000 : address - 0x8000 + size]

    def fixed_at(address: int, size: int) -> bytes:
        return fixed[address - 0xE000 : address - 0xE000 + size]

    selector_x = hits(pair, bytes.fromhex("9d8c04"), 0x8000)
    selector_y = hits(pair, bytes.fromhex("998c04"), 0x8000)
    if selector_x != [0x8EF9, 0x9479]:
        raise SystemExit(f"unexpected X selector stores: {selector_x}")
    if selector_y != [0x8D4F, 0x8EB9, 0x9482]:
        raise SystemExit(f"unexpected Y selector stores: {selector_y}")

    frame_x = hits(pair, bytes.fromhex("9d0004"), 0x8000)
    frame_y = hits(pair, bytes.fromhex("990004"), 0x8000)
    if frame_x != [0x8E34, 0x8EF4, 0x9474, 0x9ADB, 0x9C58, 0x9D19]:
        raise SystemExit(f"unexpected X frame stores: {frame_x}")
    if frame_y != [0x8D4A, 0x8DFA, 0x8ED5, 0x947D]:
        raise SystemExit(f"unexpected Y frame stores: {frame_y}")

    # The one direct literal frame-$14 setup immediately selects $0E.
    if at(0x8D48, 10) != bytes.fromhex("a914990004a90e998c04"):
        raise SystemExit("frame-$14 / selector-$0E signature mismatch")

    # Direct selector-$10 spawn/root setup.
    if at(0x8EB7, 5) != bytes.fromhex("a910998c04"):
        raise SystemExit("$8EB7 selector-$10 signature mismatch")
    spawn_frames = list(at(0x9158, 6))
    if spawn_frames != [0xF4, 0xF6, 0xF8, 0xFA, 0xFC, 0xFE]:
        raise SystemExit(f"spawn frame table mismatch: {spawn_frames}")
    if at(0x8EF2, 10) != bytes.fromhex("a9f09d0004a9109d8c04"):
        raise SystemExit("$8EF2 root selector/frame signature mismatch")

    # Canonical helpers: store A as frame, then force selector $10.
    if at(0x9474, 9) != bytes.fromhex("9d0004a9109d8c0460"):
        raise SystemExit("$9474 helper signature mismatch")
    if at(0x947D, 9) != bytes.fromhex("990004a910998c0460"):
        raise SystemExit("$947D helper signature mismatch")

    jsr_9474 = hits(pair, bytes.fromhex("207494"), 0x8000)
    jmp_9474 = hits(pair, bytes.fromhex("4c7494"), 0x8000)
    jsr_947d = hits(pair, bytes.fromhex("207d94"), 0x8000)
    if jsr_9474 != [0x9262, 0x92C7, 0x93FB, 0x975C]:
        raise SystemExit(f"unexpected JSR $9474 sites: {jsr_9474}")
    if jmp_9474 != [0x9383, 0x93ED, 0x9432, 0x943E, 0x9492]:
        raise SystemExit(f"unexpected JMP $9474 sites: {jmp_9474}")
    if jsr_947d != [0x9279]:
        raise SystemExit(f"unexpected JSR $947D sites: {jsr_947d}")

    base_frames = list(at(0x95F1, 6))
    if base_frames != [0xD2, 0xC0, 0xC6, 0xCC, 0xC0, 0xC6]:
        raise SystemExit(f"$9559 frame table mismatch: {base_frames}")
    e0_frames = list(at(0x9828, 3))
    if e0_frames != [0xE4, 0xE0, 0xE0]:
        raise SystemExit(f"$975C frame table mismatch: {e0_frames}")

    helper_frames = {
        0xF0,
        0xD2,
        *base_frames,
        *((value + 2) & 0xFF for value in base_frames),
        *((value + 4) & 0xFF for value in base_frames),
        *e0_frames,
    }
    expected_helper_frames = {
        0xC0, 0xC2, 0xC4, 0xC6, 0xC8, 0xCA, 0xCC, 0xCE,
        0xD0, 0xD2, 0xD4, 0xD6, 0xE0, 0xE4, 0xF0,
    }
    if helper_frames != expected_helper_frames:
        raise SystemExit(f"helper frame domain mismatch: {sorted(helper_frames)}")

    # $9ADB stores A after JSR $FF24. $FF24 sets A=0 and only STA's after
    # that load, therefore it returns with A still zero.
    if at(0x9AD5, 9) != bytes.fromhex("2024ff9d4e059d0004"):
        raise SystemExit("$9AD5/$9ADB signature mismatch")
    ff24 = bytes.fromhex(
        "2015ffa9009d7b069d8d069d54049d7004a9009d65059dc4049ddb04"
        "9dc1059dd8059def059d06069d1d069d33069d450660"
    )
    if fixed_at(0xFF24, len(ff24)) != ff24:
        raise SystemExit("$FF24 zero-return helper signature mismatch")

    direct_selector10_frames = helper_frames | set(spawn_frames) | {0xF0}
    if 0x14 in direct_selector10_frames:
        raise SystemExit("ERROR: direct selector-$10 domain unexpectedly contains frame $14")

    print("ROM identity: OK")
    print("selector stores:", " ".join(f"${x:04X}" for x in sorted(selector_x + selector_y)))
    print("frame stores:", " ".join(f"${x:04X}" for x in sorted(frame_x + frame_y)))
    print(
        "direct selector-$10 frame domain:",
        " ".join(f"${value:02X}" for value in sorted(direct_selector10_frames)),
    )
    print("literal frame $14 site $8D4A forces selector $0E at $8D4F")
    print("checkpoint result: no direct PRG06/07 selector-$10 setup produces frame $14")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
