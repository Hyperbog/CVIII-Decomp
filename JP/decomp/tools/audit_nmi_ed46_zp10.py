#!/usr/bin/env python3
"""Checkpoint 04F4: prove NMI-called fixed helper $ED46 preserves ZP $10."""
from __future__ import annotations

import hashlib
import sys
from collections import deque
from pathlib import Path

EXPECTED_SHA256 = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
START = 0xEC00
END = 0xF000
ENTRY = 0xED46
EXPECTED_REGION_SHA256 = "e83c0d832fc23590c0dde2448a9943ef217ada4e4f520d0da0e3f85f863dc797"
EXPECTED_VISITED = 323
EXPECTED_WRITE_DESTS = {
    ("zp", 0x00), ("zp", 0x1E), ("abs", 0x0300),
    ("abs", 0x2000), ("abs", 0x2006), ("abs", 0x2007),
}

# Official opcodes reachable from $ED46 inside $EC00-$EFFF.
OPS = {
    0x1D: ("ORA", "abx", 3),
    0x29: ("AND", "imm", 2),
    0x4C: ("JMP", "abs", 3),
    0x60: ("RTS", "imp", 1),
    0x85: ("STA", "zp", 2),
    0x86: ("STX", "zp", 2),
    0x8D: ("STA", "abs", 3),
    0x90: ("BCC", "rel", 2),
    0xA0: ("LDY", "imm", 2),
    0xA2: ("LDX", "imm", 2),
    0xA5: ("LDA", "zp", 2),
    0xA6: ("LDX", "zp", 2),
    0xA9: ("LDA", "imm", 2),
    0xAD: ("LDA", "abs", 3),
    0xB0: ("BCS", "rel", 2),
    0xB9: ("LDA", "aby", 3),
    0xBE: ("LDX", "aby", 3),
    0xC8: ("INY", "imp", 1),
    0xC9: ("CMP", "imm", 2),
    0xCA: ("DEX", "imp", 1),
    0xD0: ("BNE", "rel", 2),
    0xE0: ("CPX", "imm", 2),
    0xF0: ("BEQ", "rel", 2),
}

WRITE_MNEMONICS = {"STA", "STX", "STY", "INC", "DEC", "ASL", "LSR", "ROL", "ROR"}
DYNAMIC_WRITE_MODES = {"inx", "iny", "zpx", "zpy", "abx", "aby"}


def main(path: str) -> None:
    rom = Path(path).read_bytes()
    assert hashlib.sha256(rom).hexdigest() == EXPECTED_SHA256
    prg = rom[16:16 + 0x40000]
    fixed = prg[31 * 0x2000:32 * 0x2000]

    def read(addr: int) -> int:
        assert 0xE000 <= addr <= 0xFFFF
        return fixed[addr - 0xE000]

    region = bytes(read(a) for a in range(START, END))
    assert len(region) == 1024
    assert hashlib.sha256(region).hexdigest() == EXPECTED_REGION_SHA256

    visited: set[int] = set()
    pending = deque([ENTRY])
    external_targets: set[int] = set()
    dynamic_writes = []
    writes: set[tuple[str, int]] = set()

    while pending:
        pc = pending.popleft()
        if not (START <= pc < END) or pc in visited:
            continue

        while START <= pc < END and pc not in visited:
            visited.add(pc)
            opcode = read(pc)
            assert opcode in OPS, f"unexpected opcode ${opcode:02X} at ${pc:04X}"
            mnemonic, mode, size = OPS[opcode]
            raw = bytes(read(pc + i) for i in range(size))

            operand = None
            if size == 2:
                operand = raw[1]
            elif size == 3:
                operand = raw[1] | (raw[2] << 8)

            if mnemonic in WRITE_MNEMONICS:
                if mode in DYNAMIC_WRITE_MODES:
                    dynamic_writes.append((pc, mnemonic, mode, operand))
                elif mode in {"zp", "abs"}:
                    assert operand is not None
                    writes.add((mode, operand))

            next_pc = pc + size

            if mnemonic == "JMP":
                assert mode == "abs" and operand is not None
                if START <= operand < END:
                    pending.append(operand)
                else:
                    external_targets.add(operand)
                break

            if mnemonic in {"RTS", "RTI", "BRK"}:
                break

            if mode == "rel":
                disp = raw[1] if raw[1] < 0x80 else raw[1] - 0x100
                target = (pc + 2 + disp) & 0xFFFF
                if START <= target < END:
                    pending.append(target)
                else:
                    external_targets.add(target)
                pc = next_pc
                continue

            pc = next_pc

    assert len(visited) == EXPECTED_VISITED
    assert not external_targets, sorted(external_targets)
    assert not dynamic_writes, dynamic_writes
    assert writes == EXPECTED_WRITE_DESTS, writes
    assert ("zp", 0x10) not in writes
    assert ("abs", 0x0010) not in writes

    print("ROM identity: OK")
    print(f"04F4 span: ${START:04X}-${END-1:04X} ({END-START} bytes)")
    print(f"span SHA-256: {EXPECTED_REGION_SHA256}")
    print(f"reachable instruction starts from $ED46: {len(visited)}")
    print("external call/jump/branch targets: 0")
    print("dynamic/indexed writes on reachable graph: 0")
    print("reachable write destinations: $00 $1E $0300 $2000 $2006 $2007")
    print("04F4 result: $ED46 path preserves ZP $10")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {Path(sys.argv[0]).name} ROM.nes")
    main(sys.argv[1])
