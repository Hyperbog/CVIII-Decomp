#!/usr/bin/env python3
from __future__ import annotations
import hashlib, sys
from pathlib import Path

ROM_SHA = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"

MAIN_START, MAIN_END = 0xE35C, 0xE559
MAIN_SHA = "b22290e667392d25d75176c8685f9263794c20b9ce7e951b089dc09c4a1620bf"
MAIN_PRIOR_END = 0xE366
MAIN_NEW_SHA = "abf6303fbc6aaffd176abb96abb4e9a7150e4420498ccf438da6b2f4156baea0"

DISP_START, DISP_END = 0xE7FB, 0xE827
DISP_SHA = "1475029da3717f4674b4ed14f88cd238ef0612744133cfcbaad593722b37ff99"

GAME_START, GAME_END = 0xF390, 0xF3DD
GAME_SHA = "534f1b3ff2e7b25348a1a4c66479018ec9153d63b3e9f9b964f9e07483905b15"

MAIN_TARGETS = [
    0xE383,0xE436,0xE437,0xE449,0xF390,0xE459,0xE49B,0xE539,
    0xE50E,0xE516,0xE541,0xE549,0xE51E,0xE526,0xE52E,0xE531,
]
GAME_TARGETS = [
    0xF3FC,0xF402,0xF48D,0xF531,0xF5A8,0xF5D2,0xF61D,0xF62C,
    0xF965,0xF638,0xF511,0xF831,0xF839,0xF841,0xF841,0xF4E7,
    0xF849,0xF65B,0xF652,0xF713,0xF739,0xF792,0xF7CF,0xF653,
    0xF6EC,0xF3F4,0xF6E4,0xF4FA,0xF6F4,0xF6FE,0xF3EC,0xF3DD,
]

DIRECT_ZP10 = [
    bytes([0x85,0x10]),
    bytes([0x86,0x10]),
    bytes([0x84,0x10]),
    bytes([0xE6,0x10]),
    bytes([0xC6,0x10]),
    bytes([0x06,0x10]),
    bytes([0x46,0x10]),
    bytes([0x26,0x10]),
    bytes([0x66,0x10]),
]

def main(path: str) -> None:
    rom = Path(path).read_bytes()
    assert hashlib.sha256(rom).hexdigest() == ROM_SHA
    prg = rom[16:16+0x40000]
    assert len(prg) == 0x40000
    p31 = prg[31*0x2000:32*0x2000]

    def fixed(a: int, n: int = 1) -> bytes:
        assert 0xE000 <= a and a+n <= 0x10000
        return p31[a-0xE000:a-0xE000+n]

    main_span = fixed(MAIN_START, MAIN_END-MAIN_START)
    disp_span = fixed(DISP_START, DISP_END-DISP_START)
    game_span = fixed(GAME_START, GAME_END-GAME_START)
    assert len(main_span) == 509 and hashlib.sha256(main_span).hexdigest() == MAIN_SHA
    assert len(disp_span) == 44 and hashlib.sha256(disp_span).hexdigest() == DISP_SHA
    assert len(game_span) == 77 and hashlib.sha256(game_span).hexdigest() == GAME_SHA

    main_new = fixed(0xE366, 0xE559-0xE366)
    assert len(main_new) == 499
    assert hashlib.sha256(main_new).hexdigest() == MAIN_NEW_SHA
    assert 499 + 44 + 77 == 620

    assert fixed(0xE35C, 7) == bytes.fromhex("e61ba51820fbe7")
    table = fixed(0xE363, 0x20)
    targets = [table[i] | table[i+1] << 8 for i in range(0,0x20,2)]
    assert targets == MAIN_TARGETS
    assert len(targets) == 16
    assert targets[4] == 0xF390

    e7fb = bytes.fromhex(
        "0a"
        "8403"
        "a8"
        "c8"
        "68"
        "8500"
        "68"
        "8501"
        "b100"
        "8502"
        "c8"
        "b100"
        "a403"
        "8503"
        "6c0200"
    )
    assert fixed(0xE7FB, len(e7fb)) == e7fb
    assert len(e7fb) == 25

    e814 = bytes.fromhex(
        "c8"
        "68"
        "8500"
        "68"
        "8501"
        "b100"
        "8502"
        "c8"
        "b100"
        "8503"
        "6c0200"
    )
    assert fixed(0xE814, len(e814)) == e814
    assert len(e814) == 19
    assert 0xE814 + len(e814) == DISP_END

    for pat in DIRECT_ZP10:
        assert pat not in main_span
        assert pat not in disp_span
        assert pat not in game_span

    assert fixed(0xF390, 13) == bytes.fromhex("20aef6a52df00160a52c20fbe7")
    game_table = fixed(0xF39D, 0x40)
    game_targets = [game_table[i] | game_table[i+1] << 8 for i in range(0,0x40,2)]
    assert game_targets == GAME_TARGETS
    assert len(game_targets) == 32
    assert game_targets[-1] == 0xF3DD

    print("ROM identity: OK")
    print("04FE dependency A: $E35C-$E558, 509 bytes, SHA-256", MAIN_SHA)
    print("  prior 04F3 overlap: $E35C-$E365 = 10 bytes")
    print("  genuinely new A bytes: 499; new-tail SHA-256", MAIN_NEW_SHA)
    print("04FE dependency B: $E7FB-$E826, 44 new bytes, SHA-256", DISP_SHA)
    print("04FE dependency C: $F390-$F3DC, 77 new bytes, SHA-256", GAME_SHA)
    print("04FE genuinely new bytes: 620")
    print("E7FB A-indexed stack-consuming inline dispatcher: exact bytes OK")
    print("E814 Y-indexed sibling inline dispatcher: exact bytes OK")
    print("E360 main-script inline table: 16 entries; targets:",
          " ".join(f"${x:04X}" for x in targets))
    print("state $04 target $F390: nested $2C dispatcher with 32-entry inline table")
    print("direct ZP $10 write/RMW encodings in the three audited spans: 0")
    print("NOT CLOSED: $18 producer-domain bound, selected handler transitive banked edges, $2C producer domain/targets")
    print("04FE result: dispatcher ABI/table structure closed; transitive NMI-helper closure remains open")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: audit_nmi_main_script_dispatch.py ROM.nes")
    main(sys.argv[1])
