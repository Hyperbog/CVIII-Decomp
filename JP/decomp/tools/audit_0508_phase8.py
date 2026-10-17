#!/usr/bin/env python3
"""0508 Phase 8: bounded PRG31:E7B6 clear and raw-$0A:B570 state-zero prefix.

Executes 2A03-compatible subset using exact JP bytes, 6502 stack/branch semantics.
Stops BEFORE fixed EB82; no reset-to-NMI or EB82 callee liveness claim.
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

ROM_SHA = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
BANK = 0x0A
ENTRY = 0xB570
STOP = 0xEB82

class CPU:
    def __init__(self, prg: bytes, saved_0781: int, seed: int):
        self.prg = prg
        self.ram = bytearray(((i * 17 + seed) & 255) for i in range(0x800))
        self.ram[0x18] = 0x0D
        self.ram[0x19] = 0
        self.ram[0x23] = BANK
        self.ram[0x781] = saved_0781
        self.ram[0x7A0] = (seed * 3 + 67) & 255
        self.ram[0x7A6] = (seed * 7 + 141) & 255
        self.ram[0x7F6] = 0xA5
        self.ram[0x6A0] = 0x7C
        self.ram[0x3C0] = 0xE9
        self.a = 0x9C
        self.x = seed
        self.y = seed ^ 0x96
        self.sp = 0xFD
        self.pc = ENTRY
        self.c = False
        self.z = False
        self.n = False
        self.hw = []
        self.writes = {}
        self.steps = 0
        self.stack_parent()
    def stack_parent(self):
        self.push(0x8F)
        self.push(0xFF)
    def push(self, v: int):
        self.ram[0x100 + self.sp] = v & 255
        self.sp = (self.sp - 1) & 255
    def pop(self) -> int:
        self.sp = (self.sp + 1) & 255
        return self.ram[0x100 + self.sp]
    def nz(self, v: int):
        self.z = (v & 255) == 0
        self.n = bool(v & 128)
    def rd(self, addr: int) -> int:
        addr &= 0xFFFF
        if addr < 0x2000:
            return self.ram[addr & 0x7FF]
        if 0x8000 <= addr < 0xC000:
            return self.prg[BANK*0x4000 + addr - 0x8000]
        if addr >= 0xE000:
            return self.prg[31*0x2000 + addr - 0xE000]
        raise AssertionError(f"unsupported CPU read {addr:04X}")
    def wr(self, addr: int, value: int):
        addr &= 0xFFFF
        value &= 255
        if addr < 0x2000:
            dest = addr & 0x7FF
            self.ram[dest] = value
            self.writes[dest] = self.writes.get(dest, 0) + 1
            return
        if addr in (0xC000, 0xB003):
            self.hw.append((self.pc, addr, value))
            return
        raise AssertionError(f"unsupported CPU write {addr:04X}")
    def step(self):
        pc = self.pc
        op = self.rd(pc)
        v = self.rd(pc + 1)
        word = v | self.rd(pc + 2) << 8
        nxt = (pc + 1) & 0xFFFF
        if op == 0xA9:             # LDA #imm
            self.a = v; self.nz(self.a); nxt = pc + 2
        elif op == 0xA2:           # LDX #imm
            self.x = v; self.nz(self.x); nxt = pc + 2
        elif op == 0xA5:           # LDA zp
            self.a = self.rd(v); self.nz(self.a); nxt = pc + 2
        elif op == 0xAD:           # LDA abs
            self.a = self.rd(word); self.nz(self.a); nxt = pc + 3
        elif op == 0x85:           # STA zp
            self.wr(v, self.a); nxt = pc + 2
        elif op == 0x8D:           # STA abs
            self.wr(word, self.a); nxt = pc + 3
        elif op == 0x95:           # STA zp,X (wraps at $FF)
            self.wr((v + self.x) & 255, self.a); nxt = pc + 2
        elif op == 0x9D:           # STA abs,X
            self.wr((word + self.x) & 0xFFFF, self.a); nxt = pc + 3
        elif op == 0x48:           # PHA
            self.push(self.a)
        elif op == 0x68:           # PLA
            self.a = self.pop(); self.nz(self.a)
        elif op == 0xAA:           # TAX
            self.x = self.a; self.nz(self.x)
        elif op == 0xE8:           # INX
            self.x = (self.x + 1) & 255; self.nz(self.x)
        elif op == 0xE0:           # CPX #imm
            d = (self.x - v) & 255
            self.c = self.x >= v
            self.nz(d)
            nxt = pc + 2
        elif op in (0xD0, 0x90, 0xB0):  # BNE/BCC/BCS
            branch = ((not self.z) if op == 0xD0 else
                      (not self.c) if op == 0x90 else self.c)
            offset = v if v < 128 else v - 256
            nxt = (pc + 2 + (offset if branch else 0)) & 0xFFFF
        elif op == 0x20:           # JSR
            self.push((pc + 2) >> 8)
            self.push((pc + 2) & 255)
            nxt = word
        elif op == 0x60:           # RTS
            nxt = ((self.pop() | self.pop() << 8) + 1) & 0xFFFF
        else:
            raise AssertionError(f"Unsupported opcode {op:02X} at {pc:04X}")
        self.pc = nxt & 0xFFFF
        self.steps += 1
    def run(self):
        while self.pc != STOP:
            assert self.steps < 20000, (self.pc, self.steps)
            self.step()

def audit(path: str) -> dict:
    rom = Path(path).read_bytes()
    assert len(rom) == 393232
    assert hashlib.sha256(rom).hexdigest() == ROM_SHA
    prg = rom[16:16+0x40000]
    f = lambda pc, n: prg[31*0x2000 + pc - 0xE000:31*0x2000 + pc - 0xE000 + n]
    b = lambda pc, n: prg[BANK*0x4000 + pc - 0x8000:BANK*0x4000 + pc - 0x8000 + n]
    assert b(0xB570, 25) == bytes.fromhex(
        "20 c4 e2 20 16 e6 a5 21 8d 03 b0 ad 81 07 48 20 b6 e7 "
        "68 8d 81 07 20 82 eb")
    assert f(0xE2C4, 6) == bytes.fromhex("a9 1e 8d 00 c0 60")
    assert f(0xE616, 15) == bytes.fromhex(
        "a9 20 85 21 a9 00 85 6a 85 43 85 40 85 6f 60")
    assert f(0xE7B6, 69) == bytes.fromhex(
        "a2 4d a9 00 95 00 e8 e0 e0 d0 f9 a2 00 "
        "9d 00 04 9d 00 05 e0 f6 b0 03 9d 00 07 e8 d0 f0 "
        "a9 00 aa 9d 00 06 e8 e0 a0 90 f8 a2 e0 "
        "9d 00 06 e8 d0 fa a2 00 9d 00 03 e8 e0 c0 d0 f8 "
        "a9 00 aa 95 f0 e8 e0 08 90 f9 60")
    ranges = [(0x4D,0xE0),(0xF0,0xF8),(0x300,0x3C0),
              (0x400,0x500),(0x500,0x600),(0x600,0x6A0),
              (0x6E0,0x700),(0x700,0x7F6)]
    cleared = {i for lo,hi in ranges for i in range(lo,hi)}
    assert len(cleared) == sum(hi-lo for lo,hi in ranges)
    assert len(cleared) == 1297, len(cleared)
    cases = 0
    first_steps = None
    first_total = None
    for seed in range(256):
        for variant in range(3):
            saved = (seed + 83 * variant) & 255
            cpu = CPU(prg, saved, seed ^ (variant * 71))
            orig = cpu.ram[:]
            cpu.run()
            assert cpu.pc == STOP and cpu.sp == 0xF9
            assert cpu.ram[0x1FA] == 0x88 and cpu.ram[0x1FB] == 0xB5
            assert cpu.ram[0x1FC] == 0xFF and cpu.ram[0x1FD] == 0x8F
            assert (cpu.ram[0x18], cpu.ram[0x19], cpu.ram[0x23]) == (0x0D,0,BANK)
            assert cpu.ram[0x21] == 0x20 and cpu.ram[0x68] == 0
            assert cpu.ram[0x781] == saved
            assert (cpu.ram[0x789],cpu.ram[0x7A0],cpu.ram[0x7A6]) == (0,0,0)
            assert cpu.ram[0x7F6] == orig[0x7F6] == 0xA5
            assert cpu.ram[0x6A0] == orig[0x6A0] == 0x7C
            assert cpu.ram[0x3C0] == orig[0x3C0] == 0xE9
            assert all(cpu.ram[i] == 0 for i in cleared if i != 0x781)
            assert cpu.hw == [(0xE2C6,0xC000,0x1E),(0xB578,0xB003,0x20)]
            assert all(k in (cleared | {0x21,0x6A,0x43,0x40,0x6F,0x781}) for k in cpu.writes)
            # One write per cleared RAM byte; $68 and $0781 are explicitly
            # updated by their owning paths; $0781 restored after the clear.
            assert all(cpu.writes.get(i) == (2 if i in (0x6A,0x6F,0x781) else 1) for i in cleared)
            assert cpu.writes[0x781] == 2
            if first_steps is None:
                first_steps = cpu.steps
                first_total = len(cpu.writes)
            else:
                assert cpu.steps == first_steps
                assert len(cpu.writes) == first_total
            cases += 1
    return {
        "status":"0508_PHASE8_BOUNDED_INITIALIZATION_PREFIX_NOT_FULL_NMI",
        "rom_sha256": ROM_SHA, "cases": cases,
        "entry_raw_bank":"0A", "entry_cpu":"B570",
        "stops_before_fixed_callee":"EB82",
        "executed_instructions_per_case":first_steps,
        "unique_RAM_destinations_per_case":first_total,
        "cleared_distinct_ram_bytes":len(cleared),
        "clear_ranges_half_open":[[f"{a:04X}",f"{b:04X}"] for a,b in ranges],
        "restored_ram_0781":"incoming value", "ram_0789":"00",
        "ram_07A0":"00", "ram_07A6":"00", "ram_68":"00",
        "ram_18":"0D", "ram_19":"00",
        "writes_hardware":[["C000","1E"],["B003","20"]],
        "strict_new_prg_bytes":0,
        "strict_cumulative_prg_bytes":49404, "vpp":24,
        "caveat":"Conditional B570 state-zero entry; stops at EB82. No full NMI execution, no proof of external callee preservation or reset-to-frame liveness."
    }

if __name__ == "__main__":
    if len(sys.argv) not in (2,3):
        raise SystemExit("usage: audit_0508_phase8.py JP-ROM.nes [report.json]")
    report = audit(sys.argv[1])
    if len(sys.argv) == 3:
        Path(sys.argv[2]).write_text(json.dumps(report,indent=2)+"\n")
    print(f"Phase 8 bounded room-state initialization PASS: {report['cases']} cases")
    print(f"Per-case instructions: {report['executed_instructions_per_case']}")
    print(f"RAM clear: {report['cleared_distinct_ram_bytes']} bytes; next callee EB82")
