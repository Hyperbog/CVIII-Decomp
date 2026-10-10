#!/usr/bin/env python3
"""Bounded original-JP raw-$0A actor allocation -> fixed-$FF06 execution.

Runs source opcodes (no source bank data exported) across the complete 12-slot
occupancy domain. A branch target is a stop boundary, not proof the caller
or target executes during gameplay. This is provisional, not PRG/VPP credit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from audit_actor_cpu_abi_0509 import BoundedCpu, authenticated_prg

RAW_BANK = 0x0A
START = 0x90CA
FREE_EXIT = 0x90F7
FULL_EXIT = 0x9128
SOURCE_END = 0x90DF
SOURCE_SHA = 'f4300055beb08d35061b4687f3f479782abc71957523304ad9fb0a685efa069a'
# This digest is for $90CE-$90DE; the source preamble at $90CA is separately
# asserted by opcode and operand. Keep both spans uncredited as new bytes.


class ActorSpawnCpu(BoundedCpu):
    def __init__(self, prg: bytes, ram: bytearray, start: int = START, x: int = 0xD7):
        super().__init__(prg, start, ram)
        self.sp = 0xFB  # artificial outer caller, FF06 JSR returns to $90D1
        self.x = x  # scanner must override caller's incoming X on allocation
        self.a = 0xA9
        self.p = 0xA5
        self.terminal = None
        self.path: list[int] = []

    def read(self, at: int) -> int:
        if at < 0x800:
            return self.ram[at]
        if 0x8000 <= at <= 0xBFFF:
            return self.prg[RAW_BANK * 16384 + (at - 0x8000)]
        if 0xE000 <= at <= 0xFFFF:
            return self.prg[31 * 8192 + (at - 0xE000)]
        raise ValueError(f'Unmapped source read ${at:04X}')

    def execute(self) -> None:
        while self.pc not in (FREE_EXIT, FULL_EXIT):
            if not (0x90C5 <= self.pc < SOURCE_END or
                    0x8CDD <= self.pc <= 0x8CE9 or
                    0xFF06 <= self.pc <= 0xFF14):
                raise ValueError(f'Unproved actor path at ${self.pc:04X}')
            self.steps += 1
            if self.steps > 200:
                raise ValueError('Bounded actor call exceeded 200 source instructions')
            self.path.append(self.pc)
            op = self.fetch()
            if op in (0xA9, 0xA2):  # LDA/LDX immediate
                v = self.fetch()
                if op == 0xA9:
                    self.a = v
                else:
                    self.x = v
                self.nz(v)
            elif op == 0xA5:  # LDA zero page
                self.a = self.read(self.fetch())
                self.nz(self.a)
            elif op == 0x85:  # STA zero page
                dst = self.fetch()
                self.ram[dst] = self.a
                self.stores.append(dst)
            elif op in (0x9D, 0xBD):  # STA / LDA abs,X
                addr = self.fetch() | (self.fetch() << 8)
                dst = (addr + self.x) & 0xFFFF
                if op == 0xBD:
                    self.a = self.read(dst)
                    self.nz(self.a)
                else:
                    if dst >= 0x800:
                        raise ValueError('Actor writes outside CPU RAM')
                    self.ram[dst] = self.a
                    self.stores.append(dst)
            elif op == 0xE8:  # INX
                self.x = (self.x + 1) & 255
                self.nz(self.x)
            elif op == 0xE0:  # CPX immediate
                v = self.fetch()
                self.p = (self.p & ~1) | int(self.x >= v)
                self.nz((self.x - v) & 255)
            elif op in (0xF0, 0xD0, 0x90):  # BEQ, BNE, BCC
                rel = self.fetch()
                taken = (bool(self.p & 2) if op == 0xF0 else
                         not bool(self.p & 2) if op == 0xD0 else
                         not bool(self.p & 1))
                if taken:
                    self.pc = (self.pc + (rel if rel < 128 else rel - 256)) & 0xFFFF
            elif op == 0x20:  # JSR absolute
                lo = self.fetch()
                hi = self.fetch()
                self.push((self.pc - 1) >> 8)
                self.push((self.pc - 1) & 255)
                self.pc = (hi << 8) | lo
            elif op == 0x4C:  # JMP absolute
                self.pc = self.fetch() | (self.fetch() << 8)
            elif op == 0x60:  # RTS, including FF06 scanner return
                self.pc = ((self.pop() | (self.pop() << 8)) + 1) & 0xFFFF
            else:
                raise ValueError(f'Unexpected source opcode ${op:02X}')
        self.terminal = self.pc
        if self.sp != 0xFB:
            raise ValueError('FF06 JSR/RTS failed to restore the caller stack')


def audit(prg: bytes) -> dict:
    raw = prg[RAW_BANK * 16384:RAW_BANK * 16384 + 16384]
    code = raw[0x90CE - 0x8000:SOURCE_END - 0x8000]
    if hashlib.sha256(code).hexdigest() != SOURCE_SHA:
        raise ValueError('Original raw-bank $0A actor callsite source drift')
    if raw[START - 0x8000:START - 0x8000 + 4] != bytes.fromhex('A9 00 85 10'):
        raise ValueError('Original actor preamble does not clear ZP $10')
    digest = hashlib.sha256()
    executed = 0
    free_cases = 0
    full_cases = 0
    start_offsets = set()
    for occupancy in range(4096):
        ram = bytearray([0xA5]) * 0x800
        for i in range(12):
            ram[0x054F + i] = 0x81 if occupancy & (1 << i) else 0
        ram[0x10] = 0x7F
        cpu = ActorSpawnCpu(prg, ram)
        cpu.execute()
        expected = next((i + 1 for i in range(12) if not occupancy & (1 << i)), 13)
        has_free = expected != 13
        stop = FREE_EXIT if has_free else FULL_EXIT
        mutated = [0x10]
        if has_free:
            mutated += [0x054E + expected, 0x05EF + expected]
            free_cases += 1
        else:
            full_cases += 1
        if cpu.x != expected or cpu.pc != stop or cpu.stores != mutated:
            raise ValueError(f'Actor callsite control/store mismatch {occupancy:03X}')
        if cpu.a != (0 if has_free else 1) or ram[0x10] != 0:
            raise ValueError('Actor caller changed scan accumulator or failed $10 clear')
        if has_free and (ram[0x054E + expected] != 0x13 or ram[0x05EF + expected] != 0):
            raise ValueError('Actor caller field assignment mismatch')
        for index in range(12):
            slot = index + 1
            original = 0x81 if occupancy & (1 << index) else 0
            actual = ram[0x054E + slot]
            if actual != (0x13 if has_free and slot == expected else original):
                raise ValueError('Actor slot occupancy unrelated mutation')
        # Only the explicitly proved store destinations, plus 6502 JSR return
        # stack bytes at $01FA/$01FB (and the synthetic parent's $01FC/$01FD),
        # may differ from initial memory. Every other address stays unchanged.
        altered = set(mutated) | {0x1FA, 0x1FB, 0x1FC, 0x1FD}
        for i in range(0x800):
            if i in altered or 0x054F <= i <= 0x055A:
                continue
            if ram[i] != 0xA5:
                raise ValueError(f'Unexpected raw-bank actor RAM modification at ${i:04X}')
        start_offsets.update(cpu.path)
        digest.update(bytes([expected, cpu.a, cpu.p, cpu.sp, cpu.steps,
                             cpu.pc & 255, cpu.pc >> 8]))
        executed += cpu.steps
    return {
        'schema': 'JP-0509-original-raw0A-actor-spawn-path/v1',
        'rom_sha256': '958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28',
        'mapper_raw_bank': '0A',
        'source_entry_cpu': f'{START:04X}',
        'source_callee_cpu': 'FF06',
        'source_sha256_90CE_90DE': SOURCE_SHA,
        'occupancy_cases': 4096,
        'available_slot_cases': free_cases,
        'full_slot_cases': full_cases,
        'total_original_instructions_executed': executed,
        'distinct_instruction_pcs': len(start_offsets),
        'result_digest_sha256': digest.hexdigest(),
        'on_available': 'first free slot X=1..12; $054E,X=$13; $05EF,X=0; branch to $90F7',
        'on_full': 'X=$0D, A=$01; conditional branch to $9128; no $054E/$05EF write',
        'common': '$10=0 before fixed $FF06 call; caller JSR stack restored',
        'scope': 'synthetic occupancy memory and authentic instruction fetch only, no proven game entry/mapper lifetime',
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
    print('PASS raw-$0A $90CA original actor spawn:', result['occupancy_cases'],
          'configurations,', result['total_original_instructions_executed'], 'source instructions')


if __name__ == '__main__':
    main()
