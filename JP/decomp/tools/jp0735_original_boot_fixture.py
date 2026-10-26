#!/usr/bin/env python3
"""JP0735: invented Mapper24 fixed-bank boot instruction fixture.

Exercises the same *opcodes and addresses* as four authentic Japanese
reset-path instructions without copying any game resource/level/graphics.
Emitted media is artificial and never accepted by production SHA256.
"""
from pathlib import Path
import argparse
import hashlib
from test_cycle_synthetic_rom_0569 import create, PRG, FIXED, SIZE

RESET_PC = 0xE00B
BASE = 16 + FIXED

def build() -> bytes:
    fixture=bytearray(create())
    # Distinct invented program. 10 NOPs are deliberately used where the
    # real game's PPU status poll happens; no original code is included.
    program=bytes((0xD8, 0x78)) + bytes([0xEA]*10) + bytes((
        0xA2, 0xFF,   # synthetic LDX, reset-path instruction at $E017
        0x9A,         # TXS at $E019
        0x4C,0x1A,0xE0,  # safe single JMP loop, no game code
    ))
    assert len(program)==18
    fixture[BASE+0x0B:BASE+0x0B+len(program)]=program
    # The NMI/IRQ stubs remain from JP0569's synthetic fixture.
    fixture[BASE+0x1FFC:BASE+0x1FFE]=RESET_PC.to_bytes(2,"little")
    result=bytes(fixture)
    assert len(result)==SIZE and result[:4]==b"NES\x1a"
    assert result[BASE+0x0B]==0xD8 and result[BASE+0x0C]==0x78
    assert result[BASE+0x17:BASE+0x1A]==b"\xA2\xFF\x9A"
    assert result[BASE+0x1FFC:BASE+0x1FFE]==b"\x0b\xe0"
    assert hashlib.sha256(result).hexdigest()!=(
      "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28")
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path)
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    data=build()
    if args.self_test:
        print("PASS JP0735 invented fixed-bank bootstrap and 4 opcode addresses")
    elif args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_bytes(data)
        print("SYNTHETIC_ONLY",hashlib.sha256(data).hexdigest())
    else:
        p.error("specify --out or --self-test")
