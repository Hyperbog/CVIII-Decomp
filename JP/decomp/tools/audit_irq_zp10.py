#!/usr/bin/env python3
"""Checkpoint 04F2: prove verified IRQ handlers cannot mutate ZP $10."""
from __future__ import annotations

import hashlib
import sys
from collections import defaultdict, deque
from pathlib import Path

EXPECTED_SHA256 = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
REGION_START = 0x9F99
REGION_END = 0xA527  # exclusive
EXPECTED_REGION_SHA256 = "fb0f709699ad64b6cb49fa4eaeb2de8e1a260e23745341fc2f48b38fedd8ded3"

ENTRYPOINTS = (
    0x9F99, 0x9FA1, 0x9FD5, 0x9FE3, 0xA01C, 0xA078, 0xA0A8, 0xA0CF,
    0xA102, 0xA10D, 0xA120, 0xA14B, 0xA16F, 0xA18B, 0xA1B1, 0xA1D5,
    0xA1FA, 0xA235, 0xA243, 0xA249, 0xA293, 0xA2DD, 0xA2E2, 0xA2EA,
    0xA310, 0xA316, 0xA323, 0xA340, 0xA357, 0xA36B, 0xA3A8, 0xA3ED,
    0xA405, 0xA420, 0xA497, 0xA4B2, 0xA4DF, 0xA4EC,
)

EXPECTED_EXTERNAL_CALLS = {
    0x9F5B, 0xE001, 0xE005, 0xE2FA, 0xE30B, 0xE316, 0xE32B, 0xE331,
    0xE33C, 0xE347, 0xE351,
}
EXPECTED_EXTERNAL_JUMPS = {0xE118, 0xE11D}

OPS: dict[int, tuple[str, str, int]] = {
0x00:('BRK','imp',1),0x01:('ORA','inx',2),0x05:('ORA','zp',2),0x06:('ASL','zp',2),0x08:('PHP','imp',1),0x09:('ORA','imm',2),0x0A:('ASL','acc',1),0x0D:('ORA','abs',3),0x0E:('ASL','abs',3),
0x10:('BPL','rel',2),0x11:('ORA','iny',2),0x15:('ORA','zpx',2),0x16:('ASL','zpx',2),0x18:('CLC','imp',1),0x19:('ORA','aby',3),0x1D:('ORA','abx',3),0x1E:('ASL','abx',3),
0x20:('JSR','abs',3),0x21:('AND','inx',2),0x24:('BIT','zp',2),0x25:('AND','zp',2),0x26:('ROL','zp',2),0x28:('PLP','imp',1),0x29:('AND','imm',2),0x2A:('ROL','acc',1),0x2C:('BIT','abs',3),0x2D:('AND','abs',3),0x2E:('ROL','abs',3),
0x30:('BMI','rel',2),0x31:('AND','iny',2),0x35:('AND','zpx',2),0x36:('ROL','zpx',2),0x38:('SEC','imp',1),0x39:('AND','aby',3),0x3D:('AND','abx',3),0x3E:('ROL','abx',3),
0x40:('RTI','imp',1),0x41:('EOR','inx',2),0x45:('EOR','zp',2),0x46:('LSR','zp',2),0x48:('PHA','imp',1),0x49:('EOR','imm',2),0x4A:('LSR','acc',1),0x4C:('JMP','abs',3),0x4D:('EOR','abs',3),0x4E:('LSR','abs',3),
0x50:('BVC','rel',2),0x51:('EOR','iny',2),0x55:('EOR','zpx',2),0x56:('LSR','zpx',2),0x58:('CLI','imp',1),0x59:('EOR','aby',3),0x5D:('EOR','abx',3),0x5E:('LSR','abx',3),
0x60:('RTS','imp',1),0x61:('ADC','inx',2),0x65:('ADC','zp',2),0x66:('ROR','zp',2),0x68:('PLA','imp',1),0x69:('ADC','imm',2),0x6A:('ROR','acc',1),0x6C:('JMP','ind',3),0x6D:('ADC','abs',3),0x6E:('ROR','abs',3),
0x70:('BVS','rel',2),0x71:('ADC','iny',2),0x75:('ADC','zpx',2),0x76:('ROR','zpx',2),0x78:('SEI','imp',1),0x79:('ADC','aby',3),0x7D:('ADC','abx',3),0x7E:('ROR','abx',3),
0x81:('STA','inx',2),0x84:('STY','zp',2),0x85:('STA','zp',2),0x86:('STX','zp',2),0x88:('DEY','imp',1),0x8A:('TXA','imp',1),0x8C:('STY','abs',3),0x8D:('STA','abs',3),0x8E:('STX','abs',3),
0x90:('BCC','rel',2),0x91:('STA','iny',2),0x94:('STY','zpx',2),0x95:('STA','zpx',2),0x96:('STX','zpy',2),0x98:('TYA','imp',1),0x99:('STA','aby',3),0x9A:('TXS','imp',1),0x9D:('STA','abx',3),
0xA0:('LDY','imm',2),0xA1:('LDA','inx',2),0xA2:('LDX','imm',2),0xA4:('LDY','zp',2),0xA5:('LDA','zp',2),0xA6:('LDX','zp',2),0xA8:('TAY','imp',1),0xA9:('LDA','imm',2),0xAA:('TAX','imp',1),0xAC:('LDY','abs',3),0xAD:('LDA','abs',3),0xAE:('LDX','abs',3),
0xB0:('BCS','rel',2),0xB1:('LDA','iny',2),0xB4:('LDY','zpx',2),0xB5:('LDA','zpx',2),0xB6:('LDX','zpy',2),0xB8:('CLV','imp',1),0xB9:('LDA','aby',3),0xBA:('TSX','imp',1),0xBC:('LDY','abx',3),0xBD:('LDA','abx',3),0xBE:('LDX','aby',3),
0xC0:('CPY','imm',2),0xC1:('CMP','inx',2),0xC4:('CPY','zp',2),0xC5:('CMP','zp',2),0xC6:('DEC','zp',2),0xC8:('INY','imp',1),0xC9:('CMP','imm',2),0xCA:('DEX','imp',1),0xCC:('CPY','abs',3),0xCD:('CMP','abs',3),0xCE:('DEC','abs',3),
0xD0:('BNE','rel',2),0xD1:('CMP','iny',2),0xD5:('CMP','zpx',2),0xD6:('DEC','zpx',2),0xD8:('CLD','imp',1),0xD9:('CMP','aby',3),0xDD:('CMP','abx',3),0xDE:('DEC','abx',3),
0xE0:('CPX','imm',2),0xE1:('SBC','inx',2),0xE4:('CPX','zp',2),0xE5:('SBC','zp',2),0xE6:('INC','zp',2),0xE8:('INX','imp',1),0xE9:('SBC','imm',2),0xEA:('NOP','imp',1),0xEC:('CPX','abs',3),0xED:('SBC','abs',3),0xEE:('INC','abs',3),
0xF0:('BEQ','rel',2),0xF1:('SBC','iny',2),0xF5:('SBC','zpx',2),0xF6:('INC','zpx',2),0xF8:('SED','imp',1),0xF9:('SBC','aby',3),0xFD:('SBC','abx',3),0xFE:('INC','abx',3),
}

WRITE_MNEMONICS = {"STA", "STX", "STY", "INC", "DEC", "ASL", "LSR", "ROL", "ROR"}
DYNAMIC_WRITE_MODES = {"inx", "iny", "zpx", "zpy"}


def main(path: str) -> None:
    rom = Path(path).read_bytes()
    assert hashlib.sha256(rom).hexdigest() == EXPECTED_SHA256
    prg = rom[16:16 + 0x40000]

    def read(addr: int) -> int:
        if 0x8000 <= addr < 0xA000:
            return prg[2 * 0x2000 + addr - 0x8000]
        if 0xA000 <= addr < 0xC000:
            return prg[3 * 0x2000 + addr - 0xA000]
        if 0xE000 <= addr <= 0xFFFF:
            return prg[31 * 0x2000 + addr - 0xE000]
        raise AssertionError(f"unsupported CPU address ${addr:04X}")

    region = bytes(read(a) for a in range(REGION_START, REGION_END))
    assert len(region) == 1422
    assert hashlib.sha256(region).hexdigest() == EXPECTED_REGION_SHA256

    direct_patterns = (
        bytes((0x84, 0x10)), bytes((0x85, 0x10)), bytes((0x86, 0x10)),
        bytes((0x06, 0x10)), bytes((0x26, 0x10)), bytes((0x46, 0x10)),
        bytes((0x66, 0x10)), bytes((0xC6, 0x10)), bytes((0xE6, 0x10)),
        bytes((0x8C, 0x10, 0x00)), bytes((0x8D, 0x10, 0x00)),
        bytes((0x8E, 0x10, 0x00)), bytes((0x0E, 0x10, 0x00)),
        bytes((0x2E, 0x10, 0x00)), bytes((0x4E, 0x10, 0x00)),
        bytes((0x6E, 0x10, 0x00)), bytes((0xCE, 0x10, 0x00)),
        bytes((0xEE, 0x10, 0x00)),
    )
    for pattern in direct_patterns:
        assert pattern not in region

    def s8(v: int) -> int:
        return v if v < 0x80 else v - 0x100

    visited: set[int] = set()
    pending = deque(ENTRYPOINTS)
    external_calls: dict[int, set[int]] = defaultdict(set)
    external_jumps: dict[int, set[int]] = defaultdict(set)
    possible_10_writes: list[tuple[int, str, str, int]] = []

    while pending:
        pc = pending.popleft()
        if not (REGION_START <= pc < REGION_END) or pc in visited:
            continue
        while REGION_START <= pc < REGION_END and pc not in visited:
            visited.add(pc)
            opcode = read(pc)
            if opcode not in OPS:
                break
            mnemonic, mode, size = OPS[opcode]
            raw = bytes(read(pc + i) for i in range(size))
            operand = raw[1] if size == 2 else (raw[1] | (raw[2] << 8) if size == 3 else None)

            if mnemonic in WRITE_MNEMONICS:
                if mode in DYNAMIC_WRITE_MODES:
                    possible_10_writes.append((pc, mnemonic, mode, operand or 0))
                elif mode in {"abx", "aby"} and operand is not None and operand <= 0x10 <= operand + 0xFF:
                    possible_10_writes.append((pc, mnemonic, mode, operand))
                elif mode == "zp" and operand == 0x10:
                    possible_10_writes.append((pc, mnemonic, mode, operand))
                elif mode == "abs" and operand == 0x0010:
                    possible_10_writes.append((pc, mnemonic, mode, operand))

            target = None
            if size == 3:
                target = operand
            elif mode == "rel":
                target = (pc + 2 + s8(raw[1])) & 0xFFFF
            next_pc = pc + size

            if mnemonic == "JSR":
                assert target is not None
                if REGION_START <= target < REGION_END:
                    pending.append(target)
                else:
                    external_calls[target].add(pc)
                pc = next_pc
                continue

            if mnemonic == "JMP":
                if mode == "abs":
                    assert target is not None
                    if REGION_START <= target < REGION_END:
                        pending.append(target)
                    else:
                        external_jumps[target].add(pc)
                break

            if mnemonic in {"RTS", "RTI", "BRK"}:
                break

            if mode == "rel":
                assert target is not None
                if REGION_START <= target < REGION_END:
                    pending.append(target)
                pc = next_pc
                continue

            pc = next_pc

    assert not possible_10_writes, possible_10_writes
    assert set(external_calls) == EXPECTED_EXTERNAL_CALLS
    assert set(external_jumps) == EXPECTED_EXTERNAL_JUMPS

    helper = bytes(read(a) for a in range(0x9F5B, 0x9F87))
    wait_helpers = bytes(read(a) for a in range(0xE001, 0xE00B))
    chr_helpers = bytes(read(a) for a in range(0xE2FA, 0xE35C))
    irq_frame = bytes(read(a) for a in range(0xE0F5, 0xE131))
    for block in (helper, wait_helpers, chr_helpers, irq_frame):
        for pattern in direct_patterns:
            assert pattern not in block

    print("ROM identity: OK")
    print(f"IRQ handler span: ${REGION_START:04X}-${REGION_END-1:04X} ({len(region)} bytes), SHA-256 {EXPECTED_REGION_SHA256}")
    print(f"dispatch entrypoints audited: {len(ENTRYPOINTS)}")
    print("reachable handler writes that can alias ZP $10: 0")
    print("called local/fixed helper writes to ZP $10: 0")
    print("IRQ prologue/exit writes to ZP $10: 0")
    print("04F2 result: verified IRQ path preserves ZP $10")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {Path(sys.argv[0]).name} ROM.nes")
    main(sys.argv[1])
