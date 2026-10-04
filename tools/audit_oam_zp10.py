#!/usr/bin/env python3
"""Audit zero-page $10 state at the proven PRG26 OAM renderer boundary."""
from __future__ import annotations
import hashlib
import sys
from pathlib import Path

EXPECTED_SHA256 = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"


def find_all(data: bytes, pattern: bytes) -> list[int]:
    return [i for i in range(len(data) - len(pattern) + 1) if data[i:i + len(pattern)] == pattern]


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {Path(sys.argv[0]).name} <Akumajou Densetsu (Japan).nes>")
        return 2

    rom = Path(sys.argv[1]).read_bytes()
    if hashlib.sha256(rom).hexdigest() != EXPECTED_SHA256:
        print("ERROR: ROM SHA-256 mismatch", file=sys.stderr)
        return 1
    prg = rom[16:16 + 0x40000]

    bank13 = prg[26 * 0x2000:28 * 0x2000]
    # Restrict opcode-pattern assertions to the already proven executable
    # renderer region $8001-$817E. Raw matches elsewhere in the 16 KiB window
    # are not automatically executable instructions and are intentionally not
    # classified here.
    renderer = bank13[0x0001:0x017F]
    base = 0x8001
    sta10 = [base + i for i in find_all(renderer, b"\x85\x10")]
    stx10 = [base + i for i in find_all(renderer, b"\x86\x10")]
    sty10 = [base + i for i in find_all(renderer, b"\x84\x10")]
    lda10 = [base + i for i in find_all(renderer, b"\xA5\x10")]

    if sta10 != [0x80BF, 0x811B] or stx10 or sty10:
        print(f"ERROR: unexpected renderer $10 stores: STA={sta10} STX={stx10} STY={sty10}", file=sys.stderr)
        return 1
    if lda10 != [0x8064, 0x8166]:
        print(f"ERROR: unexpected renderer LDA $10 sites: {lda10}", file=sys.stderr)
        return 1

    # Top-level fixed-bank NMI bytes from vector entry through the instruction
    # immediately before JSR $8001. This proves no direct $10 initializer in
    # the visible NMI body; it intentionally makes no transitive-callee claim.
    fixed = prg[31 * 0x2000:32 * 0x2000]
    nmi = fixed[0x0057:0x00C7]
    direct_stores = []
    for opcode, name in ((0x85, "STA"), (0x86, "STX"), (0x84, "STY")):
        for i in range(len(nmi) - 1):
            if nmi[i] == opcode and nmi[i + 1] == 0x10:
                direct_stores.append((0xE057 + i, name))
    if direct_stores:
        print(f"ERROR: top-level NMI acquired direct $10 stores: {direct_stores}", file=sys.stderr)
        return 1

    # Directly reconciled gameplay scratch use in VRC6 bank $03 / PRG06.
    pair03 = prg[6 * 0x2000:8 * 0x2000]
    scratch_store = 0x9752 - 0x8000
    scratch_read = 0x9769 - 0x8000
    if pair03[scratch_store:scratch_store + 2] != b"\x85\x10":
        print("ERROR: expected gameplay STA $10 at $9752 changed", file=sys.stderr)
        return 1
    if pair03[scratch_read:scratch_read + 2] != b"\xA5\x10":
        print("ERROR: expected gameplay LDA $10 at $9769 changed", file=sys.stderr)
        return 1

    # $9FA9 starts with count 4 then an odd Y/control byte ($DF), proving the
    # first sprite consumes cached $10 rather than an explicit attribute.
    first = 0x9FA9 - 0x8000
    expected = bytes.fromhex("04 DF 8A F0 E1 8C F8 E5 8E 00 04 E4 90 03")
    if bank13[first:first + len(expected)] != expected:
        print("ERROR: $9FA9 descriptor bytes changed", file=sys.stderr)
        return 1

    print("ROM identity: OK")
    print("proven renderer $10 stores: $80BF, $811B")
    print("proven renderer $10 reads:  $8064, $8166")
    print("top-level NMI $E057-$E0C6 direct $10 stores: none")
    print("shared gameplay scratch proof: STA $10 at bank03:$9752; LDA $10 at $9769")
    print("descriptor $9FA9 begins with compressed attribute reuse: confirmed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
