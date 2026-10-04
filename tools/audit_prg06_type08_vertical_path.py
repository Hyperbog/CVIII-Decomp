#!/usr/bin/env python3
"""Verify the PRG06 type-$08 state-$01 vertical path toward Y=$A0-$A7."""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

EXPECTED_SHA256 = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {Path(sys.argv[0]).name} <Akumajou Densetsu (Japan).nes>")
        return 2

    rom = Path(sys.argv[1]).read_bytes()
    if hashlib.sha256(rom).hexdigest() != EXPECTED_SHA256:
        print("ERROR: ROM SHA-256 mismatch", file=sys.stderr)
        return 1

    prg = rom[16:16 + 0x40000]
    bank3 = prg[6 * 0x2000:8 * 0x2000]
    bank0b = prg[22 * 0x2000:24 * 0x2000]
    fixed = prg[31 * 0x2000:32 * 0x2000]

    def b3(addr: int, n: int) -> bytes:
        return bank3[addr - 0x8000:addr - 0x8000 + n]

    def b0b(addr: int, n: int) -> bytes:
        return bank0b[addr - 0x8000:addr - 0x8000 + n]

    def fx(addr: int, n: int) -> bytes:
        return fixed[addr - 0xE000:addr - 0xE000 + n]

    # State 0: base Y=$C0, clear velocities, high vertical velocity=$FE, advance state.
    if b3(0x816C, 0x15) != bytes.fromhex(
        "a9c09d1c042015ffa9fe9d2005a92f2049e2fe0606"
    ):
        print("ERROR: PRG06 state-$00 Y/velocity initialization mismatch", file=sys.stderr)
        return 1

    if fx(0xFF15, 0x0F) != bytes.fromhex(
        "a9009df2049d09059d20059d370560"
    ):
        print("ERROR: fixed $FF15 movement reset mismatch", file=sys.stderr)
        return 1

    # State 1: table target gate.
    if b3(0x81E5, 0x1C) != bytes.fromhex(
        "bd3306187d4506a8b90f84dd1c04900c9d1c04fe0606a9209dd80560"
    ):
        print("ERROR: PRG06 state-$01 target gate mismatch", file=sys.stderr)
        return 1

    # No direct state-$01 writes to the vertical velocity pair before $8254.
    state1 = b3(0x81DD, 0x8254 - 0x81DD)
    for sig, label in [
        (bytes.fromhex("9d2005"), "STA $0520,X"),
        (bytes.fromhex("9d3705"), "STA $0537,X"),
        (bytes.fromhex("fe2005"), "INC $0520,X"),
        (bytes.fromhex("de2005"), "DEC $0520,X"),
        (bytes.fromhex("fe3705"), "INC $0537,X"),
        (bytes.fromhex("de3705"), "DEC $0537,X"),
    ]:
        if sig in state1:
            print(f"ERROR: unexpected state-$01 vertical mutation: {label}", file=sys.stderr)
            return 1

    # Fixed bank-$0B vertical integration: low byte then high byte + carry.
    if b0b(0x8024, 0x13) != bytes.fromhex(
        "18bddb047d37059ddb04bd1c047d20059d1c0460"
    ):
        print("ERROR: bank-$0B vertical integrator mismatch", file=sys.stderr)
        return 1

    # The same index is consumed by state 0 at $81CE; $81DD is direct code target.
    if b3(0x8148, 3) != bytes.fromhex("4cdd81"):
        print("ERROR: $81DD executable entry proof mismatch", file=sys.stderr)
        return 1
    index_map = b3(0x81CE, 0x0F)
    if index_map != bytes.fromhex("010003020100030201000100010201"):
        print("ERROR: $81CE-$81DC state-0 index map mismatch", file=sys.stderr)
        return 1

    targets = b3(0x840F, 0x0F)
    expected_targets = bytes.fromhex("709070987898709070605060706050")
    if targets != expected_targets:
        print("ERROR: state-$01 target table prefix mismatch", file=sys.stderr)
        return 1
    if max(targets) != 0x98:
        print("ERROR: target prefix maximum is not $98", file=sys.stderr)
        return 1

    # For any established target <=$98, exact -2 motion from $C0 reaches $A6
    # before the target can terminate state 1.
    trajectory = list(range(0xC0, 0x97, -2))
    required = [0xA8, 0xA6, 0xA4, 0xA2, 0xA0]
    if not all(v in trajectory for v in required):
        print("ERROR: expected -2 trajectory values missing", file=sys.stderr)
        return 1

    # $823E maps $A0-$A7 to animation ID $09.
    if b3(0x823E, 0x15) != bytes.fromhex(
        "a008bd1c04c9a8b008a009c9a0b002a00aa9104c7fef"
    ):
        print("ERROR: $823E Y-to-animation selector mismatch", file=sys.stderr)
        return 1

    print("ROM identity: OK")
    print("type $08 state $00: Y=$C0, vertical fraction=$00, high velocity=$FE")
    print("state $01 preserves vertical velocity; bank-$0B integration is exact -2 per tick")
    print("established state-0 index domain: $00-$0E")
    print("corresponding state-$01 target maximum: $98")
    print("trajectory necessarily reaches $A6, selecting animation ID $09")
    print("remaining open producer question: root type-$08 $0645 domain")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
