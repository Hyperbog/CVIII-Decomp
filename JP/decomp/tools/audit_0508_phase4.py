#!/usr/bin/env python3
"""0508 Phase 4: exhaustive bounded ROM-backed $07A0/$07A6 producer tests.

No assertion of live NMI reachability, no global producer/index bound, and no
new strict PRG bytes. Requires the phase-3 bounded opcode interpreter for the
B873 descriptor writer. All CPU reads use explicitly named raw VRC6 banks.
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path
from audit_0508_phase3 import Mini6502

ROM_SHA = '958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'


class BoundedCPU:
    """6502 instruction subset for the four short producer blocks only."""
    def __init__(self, prg: bytes, raw_bank: int, entry: int):
        self.prg, self.bank, self.pc = prg, raw_bank, entry
        self.ram = bytearray(2048)
        self.a = self.y = 0
        self.c = self.z = self.n = False
        self.writes = []
        self.visited = set()
        self.steps = 0

    def rd(self, addr):
        assert 0 <= addr <= 65535
        if addr < 0x2000:
            return self.ram[addr & 2047]
        if 0x8000 <= addr < 0xC000:
            return self.prg[self.bank*16384 + addr - 0x8000]
        if 0xE000 <= addr <= 0xFFFF:
            return self.prg[31*8192 + addr - 0xE000]
        raise AssertionError(f'unknown CPU bus read {addr:04X}')

    def wr(self, addr, value, pc):
        assert 0 <= addr < 0x2000, (hex(addr), hex(pc))
        self.ram[addr & 2047] = value & 255
        self.writes.append((pc, addr & 2047, value & 255))

    def nz(self, x):
        self.z = (x & 255) == 0
        self.n = bool(x & 128)

    def run(self):
        while True:
            at = self.pc
            self.visited.add(at)
            self.steps += 1
            assert self.steps <= 30, f'unbounded block reached {at:04X}'
            op = self.rd(at)
            v = self.rd(at + 1)
            word = v | (self.rd(at + 2) << 8)
            nxt = at + 1
            if op == 0xA9:  # LDA #imm
                self.a = v; self.nz(self.a); nxt += 1
            elif op == 0xA5:  # LDA zp
                self.a = self.rd(v); self.nz(self.a); nxt += 1
            elif op == 0xAD:  # LDA abs
                self.a = self.rd(word); self.nz(self.a); nxt += 2
            elif op == 0xB9:  # LDA abs,Y
                self.a = self.rd((word + self.y) & 65535)
                self.nz(self.a); nxt += 2
            elif op == 0x8D:  # STA abs
                self.wr(word, self.a, at); nxt += 2
            elif op == 0x85:  # STA zp
                self.wr(v, self.a, at); nxt += 1
            elif op == 0xEE:  # INC abs
                b = (self.rd(word) + 1) & 255
                self.wr(word, b, at); self.nz(b); nxt += 2
            elif op == 0xE6:  # INC zp
                b = (self.rd(v) + 1) & 255
                self.wr(v, b, at); self.nz(b); nxt += 1
            elif op == 0xC6:  # DEC zp
                b = (self.rd(v) - 1) & 255
                self.wr(v, b, at); self.nz(b); nxt += 1
            elif op == 0xC9:  # CMP #imm
                self.c = self.a >= v; self.nz((self.a-v)&255)
                nxt += 1
            elif op == 0x4A:  # LSR A
                self.c = bool(self.a & 1)
                self.a >>= 1; self.nz(self.a)
            elif op == 0xA8:  # TAY
                self.y = self.a; self.nz(self.y)
            elif op == 0xD0:  # BNE
                nxt += 1
                if not self.z:
                    nxt = (nxt + (v if v < 128 else v-256)) & 65535
            elif op == 0x60:  # RTS to a bounded external caller
                return self
            else:
                raise AssertionError(f'unsupported opcode {op:02X} at {at:04X}')
            self.pc = nxt & 65535


def audit(path: Path):
    rom = path.read_bytes()
    assert len(rom) == 393232 and hashlib.sha256(rom).hexdigest() == ROM_SHA
    prg = rom[16:16+0x40000]
    f = lambda raw, pc, n: prg[raw*16384+pc-0x8000:raw*16384+pc-0x8000+n]
    # Precisely mapped ROM instructions for four independently bounded entries.
    assert f(0, 0xA099, 16) == bytes.fromhex(
        'a9 00 8d a0 07 a9 3f 8d a1 07 a9 ff 8d c2 07 60')
    assert f(1, 0xBB57, 11) == bytes.fromhex(
        'a5 30 4a a8 b9 62 bb 8d a0 07 60')
    assert f(10, 0xB622, 12) == bytes.fromhex(
        'c6 32 d0 08 a9 00 8d a6 07 e6 19 60')
    assert f(10, 0xB7DE, 24) == bytes.fromhex(
        'a9 00 8d a6 07 ee a0 07 ad a0 07 c9 05 d0 04 '
        'a9 ff d0 02 a9 00 85 68 60')
    assert f(10, 0xB7F7, 17) == bytes.fromhex(
        'ad a0 07 0a a8 b9 c2 b8 85 08 b9 c3 b8 85 09 a0 00')
    assert f(10, 0xB89F, 5) == bytes.fromhex('ee a6 07 18 60')
    assert f(10, 0xB8C2, 10) == bytes.fromhex('a4 be db be 03 bf 8b be 1c bf')

    # Exact all-offset direct-encoding discovery; not a proof of code liveness.
    opcodes = {0x8D,0x8E,0x8C,0xEE,0xCE,0x0E,0x4E,0x2E,0x6E}
    direct = {}
    for addr in (0x07A0, 0x07A6):
        occurrences = []
        for physical in range(32):
            for offset in range(8192):
                pos = physical*8192+offset
                if pos+3 <= len(prg) and prg[pos] in opcodes and prg[pos+1:pos+3] == addr.to_bytes(2,'little'):
                    occurrences.append((physical, pos, prg[pos]))
        direct[f'{addr:04X}'] = [{'physical_bank':p,'prg_offset':f'{pos:05X}',
                                   'opcode':f'{op:02X}'} for p,pos,op in occurrences]
    assert [(x['physical_bank'],x['opcode']) for x in direct['07A0']] == [(1,'8D'),(3,'8D'),(21,'EE')]
    assert [(x['physical_bank'],x['opcode']) for x in direct['07A6']] == [(21,'8D'),(21,'8D'),(21,'EE')]

    # Complete 8-bit independent input domains for each short bounded block.
    for old in range(256):
        m = BoundedCPU(prg,0,0xA099)
        m.ram[0x07A0] = old
        m.run()
        assert (m.ram[0x07A0],m.ram[0x07A1],m.ram[0x07C2]) == (0,0x3f,0xff)
        assert [p for p,a,v in m.writes] == [0xA09B,0xA0A0,0xA0A5]

    bank01_values = []
    for ram30 in range(256):
        m = BoundedCPU(prg,1,0xBB57)
        m.ram[0x30] = ram30
        m.ram[0x07A0] = 0xAA
        m.run()
        expected = f(1,0xBB62+(ram30>>1),1)[0]
        assert m.ram[0x07A0] == expected
        assert (m.c, m.z, m.n) == (bool(ram30 & 1), expected == 0, bool(expected & 0x80))
        assert m.y == ram30 >> 1
        assert [(p,a) for p,a,v in m.writes] == [(0xBB5E,0x07A0)]
        bank01_values.append(expected)
    assert bank01_values[6] == 0x35  # source $BB65, index 3
    assert any(v > 4 for v in bank01_values)

    reset_cases = 0
    for prev_idx in range(256):
        for prev_68 in range(256):
            m = BoundedCPU(prg,10,0xB7DE)
            m.ram[0x07A0] = prev_idx
            m.ram[0x07A6] = 0xA5
            m.ram[0x68] = prev_68
            m.run()
            assert m.ram[0x07A0] == (prev_idx+1)&255
            assert m.ram[0x07A6] == 0
            assert m.ram[0x68] == (0xFF if prev_idx == 4 else 0)
            assert (m.c, m.z, m.n) == (((prev_idx+1)&255) >= 5,
                prev_idx != 4, prev_idx == 4)
            assert [p for p,a,v in m.writes] == [0xB7E0,0xB7E3,0xB7F3]
            reset_cases += 1

    countdown_cases = 0
    for prev_idx in range(256):
        for prev_19 in range(256):
            m = BoundedCPU(prg,10,0xB622)
            m.ram[0x32] = 1
            m.ram[0x07A6] = prev_idx
            m.ram[0x19] = prev_19
            m.run()
            assert (m.ram[0x32],m.ram[0x07A6],m.ram[0x19]) == (0,0,(prev_19+1)&255)
            assert (m.z, m.n) == (((prev_19+1)&255) == 0, bool((prev_19+1)&128))
            assert [p for p,a,v in m.writes] == [0xB622,0xB628,0xB62B]
            countdown_cases += 1

    # Local 9-record + sentinel progression with no intervening state writes.
    # All individual B873 variants were exhaustively checked in Phase 3.
    initial_x = (0,1,16,31,63,64,100,127,128,160,192,200,224,253,254,255)
    sequences = 0
    for x in initial_x:
        for prev10 in (0,1,255):
            previous = bytearray(2048)
            previous[0x07A6],previous[0x1E],previous[0x10] = 0,x,prev10
            for i in range(10):
                m = Mini6502(prg,0,0,0)
                m.ram[:] = previous
                m.run()
                assert m.ram[0x07A6] == min(i+1,9)
                assert m.c == (i==9)
                assert m.ram[0x1E] == (x+68*min(i+1,9))&255
                assert m.ram[0x10] == 0
                previous = m.ram
                sequences += 1
    ptrs = [int.from_bytes(f(10,0xB8C2+2*i,2),'little') for i in range(5)]
    assert ptrs == [0xBEA4,0xBEDB,0xBF03,0xBE8B,0xBF1C]
    # Neither this five-word shape nor B7DE's comparison proves a global bound.
    return {
        'checkpoint':'0508_phase4_provisional', 'jp_sha256':ROM_SHA,
        'validated_short_producer_blocks':['raw00:A099-A0A8','raw01:BB57-BB61',
            'raw0A:B622-B62D (only RAM[$32]=1)', 'raw0A:B7DE-B7F5'],
        'direct_encoding_candidates':direct,
        'bounded_cases':{'A099':256,'BB57':256,'B7DE':reset_cases,
            'B622_countdown_zero':countdown_cases,'B873_cross_record_calls':sequences},
        'BB57_example':{'incoming_ram30':'06','source_cpu':'BB65',
            '07A0_written':'35','live_proven':False},
        'B7DE_relation':{'07A6':'00','07A0':'(old+1)&FF',
            '68':'FF iff old 07A0==04, else 00',
            'final_C':'old+1 modulo256 >= 5', 'final_Z':'old != 04',
            'final_N':'old == 04'},
        'B622_countdown_zero_relation':{'07A6':'00','19':'(old+1)&FF',
            'final_Z':'new 19==0', 'final_N':'new 19 bit7'},
        'B873_no_interference_sequence':{'records_written':9,'sentinel_index':9,
            'buffer_bytes':612,'end_index_07A6':9,'end_10':0},
        'B7F7_first_five_encoded_pointer_words':[f'{v:04X}' for v in ptrs],
        'scope_exclusion':'The $07A0/$07A6 writer census is only direct operand encodings; RAM aliases, live selector domains, cross-frame interference, CPU/PPU/IRQ and mapper-dependent call closure remain unproved.',
        'strict_new_bytes':0,'strict_cumulative':49404,'vpp':24}


if __name__=='__main__':
    if len(sys.argv) not in (2,3):
        raise SystemExit('usage: audit_0508_phase4.py JP.nes [report.json]')
    report = audit(Path(sys.argv[1]))
    if len(sys.argv)==3:Path(sys.argv[2]).write_text(json.dumps(report,indent=2)+'\n')
    print('0508 phase4 ROM-backed bounded producer audit PASS')
    print('case counts', report['bounded_cases'])
    print('strict new bytes 0; cumulative 49404; VPP 24')