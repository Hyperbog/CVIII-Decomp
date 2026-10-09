#!/usr/bin/env python3
"""Checkpoint 0508/Phase 3: bounded JP room-descriptor execution witness.

Reads original ROM, interprets only the exact executed 6502 instruction subset
within raw VRC6 bank $0A and fixed PRG31. Models binary ALU, N/Z/C, RAM
writes and nested JSR/RTS; NOT interrupts, mapper cycles, hardware, or timing.
Does NOT prove room-state liveness or unrestricted RAM[$07A6] bounds.
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

ROM_SHA = '958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
ZERO_PAGE = 0x10
RECORD_BASE = 0xB8A6


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Mini6502:
    """Exact-on-this-path 2A03 subset; explicit failure on unsupported opcode."""
    def __init__(self, prg: bytes, descriptor: int, x_base: int, prior_10: int):
        self.prg = prg
        self.ram = bytearray(0x800)
        self.ram[0x07A6] = descriptor
        self.ram[0x1E] = x_base
        self.ram[ZERO_PAGE] = prior_10
        self.a = self.x = self.y = 0
        self.c = self.z = self.n = False
        self.pc = 0xB873
        self.return_stack: list[int] = []
        self.steps = 0
        self.writes: list[tuple[int, int, int]] = []
        self.visited: set[int] = set()
        self.ended = False

    def rd(self, addr: int) -> int:
        addr &= 0xFFFF
        if addr < 0x2000:
            return self.ram[addr & 0x7FF]
        if 0x8000 <= addr <= 0xBFFF:
            return self.prg[0x0A*0x4000 + addr - 0x8000]
        if 0xE000 <= addr <= 0xFFFF:
            return self.prg[31*0x2000 + addr - 0xE000]
        raise AssertionError(f'unsupported CPU read ${addr:04X}')

    def wr(self, addr: int, v: int, pc: int):
        addr &= 0xFFFF
        assert addr < 0x2000, (hex(pc), hex(addr))
        self.ram[addr & 0x7FF] = v & 0xFF
        self.writes.append((pc, addr & 0x7FF, v & 0xFF))

    def flags(self, value: int):
        self.z = (value & 0xFF) == 0
        self.n = bool(value & 0x80)

    def run(self):
        while not self.ended:
            at = self.pc
            op = self.rd(at)
            self.visited.add(at)
            self.steps += 1
            assert self.steps < 5000, f'runaway at ${at:04X}'
            nxt = (at + 1) & 0xFFFF
            imm = self.rd(nxt)
            word = imm | (self.rd((nxt+1)&0xFFFF) << 8)
            if op == 0xAD:  # LDA absolute
                self.a = self.rd(word); self.flags(self.a); nxt += 2
            elif op == 0xA5:  # LDA zero page
                self.a = self.rd(imm); self.flags(self.a); nxt += 1
            elif op == 0xB9:  # LDA absolute,Y
                self.a = self.rd((word+self.y)&0xFFFF); self.flags(self.a); nxt += 2
            elif op == 0xA9:  # LDA immediate
                self.a = imm; self.flags(self.a); nxt += 1
            elif op == 0xA6:  # LDX zero page
                self.x = self.rd(imm); self.flags(self.x); nxt += 1
            elif op == 0x0A:  # ASL A
                self.c = bool(self.a & 0x80)
                self.a = (self.a << 1) & 0xFF; self.flags(self.a)
            elif op == 0x18:  # CLC
                self.c = False
            elif op == 0x38:  # SEC
                self.c = True
            elif op == 0x6D:  # ADC absolute, binary mode
                val = self.a + self.rd(word) + int(self.c)
                self.c = val > 255
                self.a = val & 0xFF; self.flags(self.a); nxt += 2
            elif op == 0xA8:  # TAY
                self.y = self.a; self.flags(self.y)
            elif op == 0xC9:  # CMP immediate
                self.c = self.a >= imm
                self.flags((self.a - imm) & 0xFF); nxt += 1
            elif op == 0x85:  # STA zero page
                self.wr(imm, self.a, at); nxt += 1
            elif op == 0x86:  # STX zero page
                self.wr(imm, self.x, at); nxt += 1
            elif op == 0x9D:  # STA absolute,X
                self.wr((word+self.x)&0xFFFF, self.a, at); nxt += 2
            elif op == 0xE8:  # INX
                self.x = (self.x + 1) & 0xFF; self.flags(self.x)
            elif op == 0xC6:  # DEC zero page
                v = (self.rd(imm) - 1) & 0xFF
                self.wr(imm, v, at); self.flags(v); nxt += 1
            elif op == 0xEE:  # INC absolute
                v = (self.rd(word) + 1) & 0xFF
                self.wr(word, v, at); self.flags(v); nxt += 2
            elif op in (0xD0, 0xF0, 0xB0):  # BNE, BEQ, BCS
                take = (op == 0xD0 and not self.z) or (op == 0xF0 and self.z) or (op == 0xB0 and self.c)
                nxt += 1
                if take: nxt = (nxt + (imm if imm < 0x80 else imm-256)) & 0xFFFF
            elif op == 0x20:  # JSR absolute (return-address behavior only)
                self.return_stack.append((at+3)&0xFFFF)
                nxt = word
            elif op == 0x4C:  # JMP absolute
                nxt = word
            elif op == 0x60:  # RTS
                if self.return_stack: nxt = self.return_stack.pop()
                else: self.ended = True
            else:
                raise AssertionError(f'unsupported opcode ${op:02X} at ${at:04X}')
            self.pc = nxt & 0xFFFF
        return self


def audit(path: Path):
    rom = path.read_bytes()
    assert len(rom) == 393232 and sha(rom) == ROM_SHA
    prg = rom[16:16+262144]
    assert len(prg) == 262144
    raw = prg[0x0A*0x4000:0x0B*0x4000]
    b = lambda a, n: raw[a-0x8000:a-0x8000+n]
    fixed = prg[31*0x2000:32*0x2000]
    f = lambda a, n: fixed[a-0xE000:a-0xE000+n]
    assert b(0xB873, 51) == bytes.fromhex(
        'ad a6 07 0a 18 6d a6 07 a8 b9 a6 b8 c9 ff f0 21 '
        '85 5f b9 a7 b8 85 5e b9 a8 b8 85 10 20 43 e8 '
        'a9 00 9d 00 03 e8 c6 10 d0 f8 20 6b e8 '
        'ee a6 07 18 60 38 60')
    assert f(0xE843, 45) == bytes.fromhex(
        'a6 1e a9 01 d0 0e a6 1e d0 0e a6 1e a9 05 d0 04 '
        'a6 1e a9 04 9d 00 03 e8 a5 5e 9d 00 03 e8 a5 5f '
        '9d 00 03 e8 86 1e 60 e8 86 1e 4c 70 ec')
    assert f(0xEC70, 11) == bytes.fromhex('a9 ff a6 1e 9d 00 03 e8 86 1e 60')
    # Conditional NMI predecessor chain. Every *mapping* and byte is exact;
    # selector values $18=$0C and $19=$13 are NOT established as live.
    assert f(0xE2D0, 6) == bytes.fromhex('85 23 8d 00 80 60')
    assert f(0xE51E, 8) == bytes.fromhex('a9 0a 20 d0 e2 4c a4 af')
    assert f(0xE526, 8) == bytes.fromhex('a9 0a 20 d0 e2 4c cc b4')
    assert int.from_bytes(f(0xE363 + 0x0C*2,2),'little') == 0xE51E
    assert int.from_bytes(f(0xE363 + 0x0D*2,2),'little') == 0xE526
    assert b(0xAFA4,5) == b(0xB4CC,5) == bytes.fromhex('a5 19 20 fb e7')
    assert int.from_bytes(b(0xAFA9 + 0x13*2,2),'little') == 0xB36B
    assert b(0xB36B,15) == bytes.fromhex('ad 89 07 8d 81 07 a9 0d 85 18 a9 00 85 19 60')
    assert int.from_bytes(b(0xB4D1,2),'little') == 0xB570
    assert b(0xB570,28) == bytes.fromhex(
        '20 c4 e2 20 16 e6 a5 21 8d 03 b0 ad 81 07 48 20 b6 e7 '
        '68 8d 81 07 20 82 eb e6 19 60')
    assert int.from_bytes(b(0xB4D3,2),'little') == 0xB58C
    assert int.from_bytes(b(0xB4D5,2),'little') == 0xB597
    records = [b(RECORD_BASE + 3*i, 3) for i in range(9)]
    assert all(rec[2] == 0x40 and rec[0] != 0xFF for rec in records)
    assert b(0xB8C1, 1) == b'\xff'
    # 3 is coprime with 256: all input descriptor values access distinct
    # bytes in the 256-byte possible indexed source span, NOT only records.
    mapped = b(RECORD_BASE, 256)
    sentinels = [i for i in range(256) if mapped[(3*i)&255] == 0xFF]
    assert sentinels == [9,28,42,44,45,46,48,54,128,132,141,212,214,218,251]
    count = 0; visited = set(); max_steps = 0
    for record in range(10):
        for starting_x in range(256):
            for prior in (0, 1, 255):
                m = Mini6502(prg, record, starting_x, prior).run()
                visited |= m.visited
                max_steps = max(max_steps, m.steps)
                count += 1
                writes_10 = [(pc,v) for pc,a,v in m.writes if a == ZERO_PAGE]
                writes_buf = [(pc,a,v) for pc,a,v in m.writes if 0x300 <= a < 0x400]
                if record == 9:
                    assert m.c and m.ram[0x07A6] == 9
                    assert m.ram[ZERO_PAGE] == prior
                    assert m.ram[0x1E] == starting_x
                    assert not writes_10 and not writes_buf
                    assert not m.return_stack
                else:
                    assert not m.c and m.ram[0x07A6] == record+1
                    assert m.ram[ZERO_PAGE] == 0
                    assert m.ram[0x1E] == (starting_x + 68) & 255
                    assert len(writes_10) == 65
                    assert writes_10[0] == (0xB88D, 0x40)
                    assert len([w for w in writes_10 if w[0] == 0xB898]) == 64
                    assert len(writes_buf) == 68
                    assert [v for _,_,v in writes_buf[:3]] == [1,records[record][1],records[record][0]]
                    assert all(v == 0 for _,_,v in writes_buf[3:67])
                    assert writes_buf[67][2] == 255
                    assert not m.return_stack
    assert 0xB8A4 in visited and {0xE843,0xE857,0xE86B,0xEC70} <= visited
    return {
        'checkpoint': '0508_phase3_provisional', 'jp_sha256': ROM_SHA,
        'unit_scope': 'ROM-backed partial 6502 execution, bank0A B873 and fixed E843/E86B/EC70',
        'simulated_cases': count, 'instruction_sites_visited': len(visited),
        'conditional_nmi_chain': '$18=0C -> fixed E51E -> raw0A AFA4; $19=13 -> B36B -> $18=0D,$19=00; next NMI fixed E526 -> raw0A B4CC -> state 00 B570, subject to cross-frame/external effects',
        'worst_case_instruction_steps': max_steps,
        'for_descriptor_00_08': {'source_records':9,'third_byte':'40',
          'queue_bytes_per_record':68,'queue_format':'01, second, first, 64x00, FF',
          'zp10_writes_per_record':65,'zp10_final':'00', 'ram_07a6_increment':1,
          'carry_at_return':0,'ram_1e_change_mod256':68},
        'for_descriptor_09': {'first_byte':'FF','carry_at_return':1,
          'ram_07a6_change':0,'ram_1e_change':0,'zp10':'preserved'},
        'possible_sentinel_descriptor_values_for_all_256':sentinels,
        'proof_limit': 'Not a full emulator, frame trace, interrupt proof, dynamic liveness proof, or global descriptor-index bound. No new strict PRG bytes credited.',
        'strict_verified_cumulative':49404,'strict_new':0,'vpp':24}


if __name__ == '__main__':
    if len(sys.argv) not in (2,3):
        sys.exit('usage: audit_0508_phase3.py JP_ROM [output.json]')
    report = audit(Path(sys.argv[1]))
    if len(sys.argv) == 3:
        Path(sys.argv[2]).write_text(json.dumps(report, indent=2)+'\n')
    print('0508 phase3 ROM-backed execution PASS', report['simulated_cases'], 'cases')
    print('source records', report['for_descriptor_00_08']['source_records'],
          'candidate FF descriptor indices', len(report['possible_sentinel_descriptor_values_for_all_256']))
    print('strict new coverage 0, last committed 0507 49404 bytes, VPP 24')