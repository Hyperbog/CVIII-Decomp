#!/usr/bin/env python3
"""Execute authentic JP PRG31 actor helpers in a bounded independent 6502 model.

No ROM bytes are exported. The model executes only opcodes present in the
hash-locked $FF06/$FF15/$FF24 helper regions, with exact 8-bit status and
6502 JSR/RTS stack behavior. This is a local ABI regression, NOT liveness
or game-state parity evidence and NOT new strict PRG/VPP credit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROM_SHA = '958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
PINNED = (
    (0xFF06, 12, 'c75f2332e11e13763245741d3f4ddb690f63dce3930c946cae3160090ac1488c'),
    (0xFF14, 66, '9f4374fdf490e30015a28e44abdc20c87259b501064c1d8eb9f4fee353d40d1a'),
)
FOUR = (0x04F2, 0x0509, 0x0520, 0x0537)
EXTRA = (0x067B, 0x068D, 0x0454, 0x0470, 0x0565, 0x04C4, 0x04DB,
         0x05C1, 0x05D8, 0x05EF, 0x0606, 0x061D, 0x0633, 0x0645)
RETURN_PC = 0xD000


def authenticated_prg(path: Path) -> bytes:
    image = path.read_bytes()
    if len(image) != 393232 or hashlib.sha256(image).hexdigest() != ROM_SHA:
        raise ValueError('Original Japanese mapper-24 ROM identity mismatch')
    prg = image[16:16 + 0x40000]
    for pc, size, digest in PINNED:
        data = prg[31 * 8192 + pc - 0xE000:31 * 8192 + pc - 0xE000 + size]
        if hashlib.sha256(data).hexdigest() != digest:
            raise ValueError(f'PRG31 ${pc:04X} checkpoint hash mismatch')
    return prg


class BoundedCpu:
    """Original instruction stepping only within the audited fixed helper."""

    def __init__(self, prg: bytes, entry: int, memory: bytearray, x: int = 0):
        self.prg, self.ram, self.pc = prg, memory, entry
        self.a, self.x, self.p, self.sp = 0x91, x, 0xA5, 0xFB
        self.ram[0x1FD] = (RETURN_PC - 1) >> 8
        self.ram[0x1FC] = (RETURN_PC - 1) & 255
        self.stores: list[int] = []
        self.steps = 0

    def read(self, at: int) -> int:
        if at < 0x800:
            return self.ram[at]
        if 0xE000 <= at <= 0xFFFF:
            return self.prg[31 * 8192 + at - 0xE000]
        raise ValueError(f'Unmapped source read ${at:04X}')

    def fetch(self) -> int:
        value = self.read(self.pc)
        self.pc = (self.pc + 1) & 0xFFFF
        return value

    def nz(self, v: int) -> None:
        self.p = (self.p & ~0x82) | (0x02 if v == 0 else 0) | (v & 0x80)

    def push(self, v: int) -> None:
        self.ram[0x100 + self.sp] = v
        self.sp = (self.sp - 1) & 255

    def pop(self) -> int:
        self.sp = (self.sp + 1) & 255
        return self.ram[0x100 + self.sp]

    def execute(self) -> None:
        while self.pc != RETURN_PC:
            if not 0xFF06 <= self.pc <= 0xFF55:
                raise ValueError(f'Unexpected control flow to ${self.pc:04X}')
            self.steps += 1
            if self.steps > 200:
                raise ValueError('Actor helper failed to return within 200 instructions')
            at = self.pc
            op = self.fetch()
            if op == 0xA2:  # LDX #imm
                self.x = self.fetch(); self.nz(self.x)
            elif op == 0xBD:  # LDA abs,X
                lo = self.fetch(); hi = self.fetch()
                self.a = self.read(((hi << 8) | lo) + self.x); self.nz(self.a)
            elif op in (0xF0, 0x90):  # BEQ, BCC relative signed offset
                delta = self.fetch()
                taken = bool(self.p & 2) if op == 0xF0 else not bool(self.p & 1)
                if taken:
                    self.pc = (self.pc + (delta if delta < 128 else delta - 256)) & 0xFFFF
            elif op == 0xE8:  # INX
                self.x = (self.x + 1) & 255; self.nz(self.x)
            elif op == 0xE0:  # CPX #imm
                rhs = self.fetch()
                difference = (self.x - rhs) & 255
                self.p = (self.p & ~1) | (1 if self.x >= rhs else 0)
                self.nz(difference)
            elif op == 0xA9:  # LDA #imm
                self.a = self.fetch(); self.nz(self.a)
            elif op == 0x9D:  # STA abs,X
                lo = self.fetch(); hi = self.fetch()
                dest = (((hi << 8) | lo) + self.x) & 0xFFFF
                if dest >= 0x800:
                    raise ValueError(f'Unexpected source store ${dest:04X}')
                self.ram[dest] = self.a
                self.stores.append(dest)
            elif op == 0x20:  # JSR abs: stack contains PC of final operand
                lo = self.fetch(); hi = self.fetch()
                self.push(((self.pc - 1) >> 8) & 255)
                self.push((self.pc - 1) & 255)
                self.pc = (hi << 8) | lo
            elif op == 0x60:  # RTS
                self.pc = ((self.pop() | (self.pop() << 8)) + 1) & 0xFFFF
            else:
                raise ValueError(f'Unexpected opcode ${op:02X} at ${at:04X}')
        if self.sp != 0xFD:
            raise ValueError('Actor helper did not balance the 6502 return stack')


def audit(prg: bytes) -> dict:
    outcomes = hashlib.sha256()
    total_steps = 0
    for pattern in range(4096):
        ram = bytearray(0x800)
        for i in range(12):
            ram[0x054F + i] = 0x80 if (pattern >> i) & 1 else 0
        before = bytes(ram[0x054F:0x055B])
        cpu = BoundedCpu(prg, 0xFF06, ram)
        cpu.execute()
        expected = next((i + 1 for i in range(12) if not ((pattern >> i) & 1)), 13)
        if (cpu.x, cpu.a) != (expected, int(expected == 13)):
            raise ValueError(f'Original actor scan mismatch for occupancy {pattern:03X}')
        if cpu.p & 0x83 != (2 if expected != 13 else 0) | (1 if expected in (1, 13) else 0):
            raise ValueError(f'Original actor scan NZ/carry mismatch for {pattern:03X}')
        if cpu.stores or bytes(ram[0x054F:0x055B]) != before:
            raise ValueError('Original actor slot scan unexpectedly modified RAM')
        outcomes.update(bytes((cpu.x, cpu.a, cpu.p, cpu.sp, cpu.steps)))
        total_steps += cpu.steps

    for entry, bases in ((0xFF15, FOUR), (0xFF24, FOUR + EXTRA)):
        for x in range(256):
            ram = bytearray([0xA5]) * 0x800
            cpu = BoundedCpu(prg, entry, ram, x)
            initial_p = cpu.p
            cpu.execute()
            addresses = [base + x for base in bases]
            if cpu.stores != addresses:
                raise ValueError(f'STA order mismatch at ${entry:04X}, X={x}')
            expected = set(addresses)
            for at in range(0x800):
                if 0x1FA <= at <= 0x1FD:
                    continue  # test-injected RTS frame and JSR stack traffic
                if ram[at] != (0 if at in expected else 0xA5):
                    raise ValueError(f'Unexpected RAM mutation at ${at:04X}, X={x}')
            if (cpu.a, cpu.x, cpu.p) != (0, x, (initial_p & ~0x82) | 2):
                raise ValueError(f'A/X/NZ/carry ABI mismatch at ${entry:04X}, X={x}')
            outcomes.update(bytes((entry & 255, x, cpu.a, cpu.p, cpu.steps)))
            total_steps += cpu.steps
    return {
        'schema': 'JP-0509-original-actor-CPU-ABI-differential/v1',
        'rom_sha256': ROM_SHA,
        'physical_prg_bank': 31,
        'entries_cpu': ['FF06', 'FF15', 'FF24'],
        'slot_occupancy_patterns': 4096,
        'indexed_field_clear_cases': 512,
        'total_6502_instructions_executed': total_steps,
        'original_instruction_abi_sha256': outcomes.hexdigest(),
        'comparison': 'ROM-instruction stepping versus native actor scan and indexed-field contracts; stack/flags checked',
        'limits': 'bounded routines only; no proof of original gameplay state, frame timing, or unobserved source liveness',
        'new_strict_prg_bytes': 0,
        'new_vpp_points': 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('original_jp_rom', type=Path)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    result = audit(authenticated_prg(args.original_jp_rom))
    if args.report:
        args.report.write_text(json.dumps(result, indent=2) + '\n')
    print(f"PASS original JP actor CPU ABI: {result['slot_occupancy_patterns']} masks, "
          f"{result['indexed_field_clear_cases']} field-clear cases, "
          f"{result['total_6502_instructions_executed']} source instructions")


if __name__ == '__main__':
    main()
