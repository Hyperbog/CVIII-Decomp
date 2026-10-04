#!/usr/bin/env python3
"""Checkpoint 04F3: verify fixed-bank pre-render NMI code preserves ZP $10."""
from __future__ import annotations
import hashlib
import sys
from pathlib import Path

EXPECTED_SHA256 = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
SPAN_START = 0xE057
SPAN_END = 0xE366  # exclusive
EXPECTED_SPAN_SHA256 = "b0e367bb5971310da3bbd066f54cc3def543e82134f4df6b7b82feef06166176"

DIRECT_PATTERNS = (
    bytes((0x84,0x10)), bytes((0x85,0x10)), bytes((0x86,0x10)),
    bytes((0x06,0x10)), bytes((0x26,0x10)), bytes((0x46,0x10)),
    bytes((0x66,0x10)), bytes((0xC6,0x10)), bytes((0xE6,0x10)),
    bytes((0x8C,0x10,0x00)), bytes((0x8D,0x10,0x00)), bytes((0x8E,0x10,0x00)),
    bytes((0x0E,0x10,0x00)), bytes((0x2E,0x10,0x00)), bytes((0x4E,0x10,0x00)),
    bytes((0x6E,0x10,0x00)), bytes((0xCE,0x10,0x00)), bytes((0xEE,0x10,0x00)),
)

def main(path: str) -> None:
    rom = Path(path).read_bytes()
    assert hashlib.sha256(rom).hexdigest() == EXPECTED_SHA256
    prg = rom[16:16+0x40000]
    fixed = prg[31*0x2000:32*0x2000]

    def fixed_bytes(cpu: int, count: int) -> bytes:
        assert 0xE000 <= cpu <= 0xFFFF
        off = cpu - 0xE000
        return fixed[off:off+count]

    span = fixed_bytes(SPAN_START, SPAN_END-SPAN_START)
    assert len(span) == 783
    assert hashlib.sha256(span).hexdigest() == EXPECTED_SPAN_SHA256

    for pat in DIRECT_PATTERNS:
        assert pat not in span, f"direct $10 write/RMW pattern found: {pat.hex()}"

    # NMI renderer-reaching call sequence through JSR $8001.
    assert fixed_bytes(0xE08C, 62) == bytes.fromhex(
        "206ce12046eda5fea61df006c61df00229e78d01202031e120d6e2"
        "a57210064a4a4a4a8572a553856ca554856d2038e22064e2205ce3"
        "a90d20d0e2200180"
    )

    # $E238 selects raw bank $0C before external JSR $89E2.
    assert fixed_bytes(0xE238, 17) == bytes.fromhex(
        "a9ff8526a90c20d0e220e289a900852660"
    )

    # Indexed write sites and their local X-domain setup.
    assert fixed_bytes(0xE264, 92) == bytes.fromhex(
        "a200209be2a202209be2a500c502d01ca501c503d016a2002080e2e8"
        "b500a855fa3500952895f8942a94fa60a900852885f8852985f960"
        "a0018c1640888c1640a008ad164085044a05044a3600ad174085054a"
        "05054a360188d0e760"
    )

    # $E35C leaves the span only through fixed helper $E7FB.
    assert fixed_bytes(0xE35C, 7) == bytes.fromhex("e61ba51820fbe7")

    # Exact direct external dependencies relevant before the renderer.
    assert fixed_bytes(0xE08F, 3) == bytes.fromhex("2046ed")
    assert fixed_bytes(0xE241, 3) == bytes.fromhex("20e289")
    assert fixed_bytes(0xE360, 3) == bytes.fromhex("20fbe7")

    print("ROM identity: OK")
    print(f"fixed NMI span: ${SPAN_START:04X}-${SPAN_END-1:04X} (783 bytes)")
    print(f"span SHA-256: {EXPECTED_SPAN_SHA256}")
    print("direct writes/RMW to ZP $10 in span: 0")
    print("indexed-write alias domains: $00-$03, $28-$2B, $F8-$FB only")
    print("external pre-render dependencies: $ED46, bank-$0C:$89E2, $E7FB")
    print("04F3 result: fixed-bank span preserves ZP $10; external dependencies remain open")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {Path(sys.argv[0]).name} ROM.nes")
    main(sys.argv[1])
