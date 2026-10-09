#!/usr/bin/env python3
"""ROM-locked 0508 Phase 9: conditional B570 -> EB82 PPU stream -> B589 return.

No reset-to-NMI provenance, frame/IRQ timing, full PPU bus, or strict-byte
promotion. Imports the proven Phase 8 partial CPU as the starting state.
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path
from audit_0508_phase8 import CPU as Phase8CPU, ROM_SHA, BANK

END = 0x9000
STREAM_START = 0xEC1D
STREAM_END_EXCLUSIVE = 0xEC47

class CPU(Phase8CPU):
    def __init__(self, prg: bytes, saved_0781: int, seed: int, ppuctrl: int):
        super().__init__(prg, saved_0781, seed)
        self.ram[0xFF] = ppuctrl
        self.ram[0xFE] = 0x1E ^ seed
        self.ppu_events: list[tuple[int,int,int]] = []
        self.vram_writes: list[tuple[int,int]] = []
        self.ppu_control = 0
        self.ppu_pointer = 0
        self.ppu_latch = False
        self.ppu_high = 0
        self.rom_reads: list[int] = []
        self.reached_eb82 = False
        self.reached_b589 = False
    def rd(self, addr: int) -> int:
        addr &= 0xFFFF
        if addr == 0x2002:
            self.ppu_latch = False
            return 0x00  # fixed bounded PPUSTATUS witness; no PPU timing claim
        value = super().rd(addr)
        if addr >= 0xE000 and STREAM_START <= addr < STREAM_END_EXCLUSIVE:
            self.rom_reads.append(addr)
        return value
    def wr(self, addr: int, value: int):
        addr &= 0xFFFF
        value &= 255
        if 0x2000 <= addr <= 0x2007:
            assert addr in (0x2000,0x2001,0x2006,0x2007), hex(addr)
            self.ppu_events.append((self.pc,addr,value))
            if addr == 0x2000:
                self.ppu_control=value
            elif addr == 0x2006:
                if not self.ppu_latch:
                    self.ppu_high = value & 0x3f
                    self.ppu_latch = True
                else:
                    self.ppu_pointer = ((self.ppu_high << 8) | value) & 0x3fff
                    self.ppu_latch = False
            elif addr == 0x2007:
                self.vram_writes.append((self.ppu_pointer,value))
                self.ppu_pointer = (self.ppu_pointer + (32 if self.ppu_control & 0x04 else 1)) & 0x3fff
            return
        super().wr(addr,value)
    def step(self):
        op = self.rd(self.pc)
        if self.pc == 0xEB82: self.reached_eb82 = True
        if self.pc == 0xB589: self.reached_b589 = True
        if op in (0xA0,0xBD,0xB1,0x88,0xC9,0xF0,0xA8,0x10,
                  0x29,0xC4,0xC8,0x18,0x65,0x75,0x4C,0xA4,0xF6,0xE6):
            pc=self.pc
            v=self.rd(pc+1)
            target = v | self.rd(pc+2)<<8
            nxt=pc+1
            if op==0xA0: # LDY #imm
                self.y=v; self.nz(self.y); nxt=pc+2
            elif op==0xBD: # LDA abs,X
                self.a=self.rd((target+self.x)&0xffff); self.nz(self.a); nxt=pc+3
            elif op==0xB1: # LDA (zp),Y
                low=self.rd(v); high=self.rd((v+1)&255)
                adr=((high<<8)|low)+self.y
                self.a=self.rd(adr & 0xffff); self.nz(self.a); nxt=pc+2
            elif op==0x88: # DEY
                self.y=(self.y-1)&255; self.nz(self.y)
            elif op==0xC9: # CMP #imm
                delta=(self.a-v)&255; self.c=self.a>=v; self.nz(delta); nxt=pc+2
            elif op==0xF0: # BEQ
                delta=v if v<0x80 else v-256
                nxt=(pc+2+(delta if self.z else 0))&0xffff
            elif op==0xA8: # TAY
                self.y=self.a; self.nz(self.y)
            elif op==0x10: # BPL
                delta=v if v<0x80 else v-256
                nxt=(pc+2+(delta if not self.n else 0))&0xffff
            elif op==0x29: # AND #imm
                self.a &= v; self.nz(self.a); nxt=pc+2
            elif op==0xC4: # CPY zp
                lhs=self.y; rhs=self.rd(v)
                self.c=lhs>=rhs; self.nz((lhs-rhs)&255); nxt=pc+2
            elif op==0xC8: # INY
                self.y=(self.y+1)&255; self.nz(self.y)
            elif op==0x18: # CLC
                self.c=False
            elif op==0x65: # ADC zp (2A03 binary even if decimal bit set)
                summ=self.a+self.rd(v)+int(self.c)
                self.c=summ>255; self.a=summ&255; self.nz(self.a); nxt=pc+2
            elif op==0x75: # ADC zp,X
                summ=self.a+self.rd((v+self.x)&255)+int(self.c)
                self.c=summ>255; self.a=summ&255; self.nz(self.a); nxt=pc+2
            elif op==0x4C: # JMP abs
                nxt=target
            elif op==0xA4: # LDY zp
                self.y=self.rd(v); self.nz(self.y); nxt=pc+2
            elif op==0xE6: # INC zp
                vv=(self.rd(v)+1)&255
                self.wr(v,vv); self.nz(vv); nxt=pc+2
            elif op==0xF6: # INC zp,X, zero page wraps
                addr=(v+self.x)&255
                vv=(self.rd(addr)+1)&255
                self.wr(addr,vv); self.nz(vv); nxt=pc+2
            self.pc=nxt
            self.steps+=1
        else:
            super().step()
    def run(self):
        while self.pc!=END:
            assert self.steps < 30000,(hex(self.pc),self.steps)
            self.step()

def reference_stream(data:bytes)->tuple[int,list[tuple[int,int]],list[int]]:
    """Independent stream parser, not tied to emulated E827 or CPU flags."""
    assert data[:2] == bytes((0x00,0x20))
    index=2; dest=0x2000; entries=[]; stream_positions=[]
    while True:
        op=data[index]; stream_positions.append(STREAM_START+index)
        if op==0xff:
            assert index==len(data)-1
            break
        if op==0x7f:
            index+=1
            assert index+2<len(data)
            dest=data[index]|(data[index+1]<<8)
            index+=2
        elif op & 0x80:
            n=op & 0x7f; v=data[index+1]
            entries.extend((dest+j,v) for j in range(n))
            dest+=n; index+=2
        else:
            n=op
            entries.extend((dest+j,data[index+1]) for j in range(n))
            dest+=n; index+=2
        assert index < len(data)
    return index,entries,stream_positions

def audit(path: str)->dict:
    rom=Path(path).read_bytes()
    assert len(rom)==393232 and hashlib.sha256(rom).hexdigest()==ROM_SHA
    prg=rom[16:16+0x40000]
    fixed=prg[31*8192:32*8192]
    rf=lambda a,n:fixed[a-0xe000:a-0xe000+n]
    assert rf(0xEB82,6)==bytes.fromhex('a2 00 bd f7 eb 85')
    assert rf(0xEBF7,2)==bytes.fromhex('1d ec')
    assert rf(0xEBF4,3)==bytes.fromhex('4c 89 ed')
    assert rf(0xED89,6)==bytes.fromhex('a5 ff 8d 00 20 60')
    assert rf(0xE827,10)==bytes.fromhex('18 75 00 95 00 90 02 f6 01 60')
    data=rf(STREAM_START,STREAM_END_EXCLUSIVE-STREAM_START)
    expected_sum,expected_writes,control_positions=reference_stream(data)
    assert (expected_sum,len(expected_writes))==(41,2048),(expected_sum,len(expected_writes))
    assert len(data)==42 and data[-1]==0xff
    assert len(set((a//1024) for a,_ in expected_writes))==2
    assert expected_writes[0]==(0x2000,0) and expected_writes[1023]==(0x23ff,0)
    assert expected_writes[1024]==(0x2400,0) and expected_writes[-1]==(0x27ff,0)
    test_cases=0
    steps=None
    for seed in range(256):
        for ppuctrl in (0x00,0x04):
            initial_saved=(seed*37+17)&255
            cpu=CPU(prg,initial_saved,seed,ppuctrl)
            cpu.run()
            assert cpu.reached_eb82 and cpu.reached_b589
            assert cpu.pc==END and cpu.sp==0xFD
            assert (cpu.ram[0x18],cpu.ram[0x19],cpu.ram[0x23])==(0x0d,1,BANK)
            assert (cpu.ram[0x7A0],cpu.ram[0x7A6],cpu.ram[0x68])==(0,0,0)
            assert cpu.ram[0x781]==initial_saved
            assert (cpu.ram[0x00],cpu.ram[0x01])==(0x46,0xEC)  # pointer after sentinel
            assert (cpu.ram[0xFC],cpu.ram[0xFD])==(0,0)
            assert len(cpu.vram_writes)==2048
            expected_addrs=[((base + j*(32 if ppuctrl==0x04 else 1)) & 0x3fff,0)
                 for base in (0x2000,0x2400) for j in range(1024)]
            assert cpu.vram_writes==expected_addrs
            assert cpu.ppu_pointer==(0x2400 +1024*(32 if ppuctrl==0x04 else 1))&0x3fff
            assert cpu.ppu_control == (ppuctrl & 0x7f)
            assert set(cpu.rom_reads).issubset(set(range(STREAM_START,STREAM_END_EXCLUSIVE)))
            assert STREAM_END_EXCLUSIVE-1 in cpu.rom_reads
            assert len(cpu.ppu_events)>2048
            if steps is None: steps=cpu.steps
            else: assert cpu.steps==steps
            test_cases+=1
    return dict(phase='0508-09',status='PROVISIONAL_CONDITIONAL_PPU_STREAM',
         jp_rom_sha256=ROM_SHA,cases=test_cases,instructions_per_case=steps,
         entry='raw VRC6 0A:$B570',fixed_callee='PRG31:$EB82',
         entry_pointer='PRG31:$EBF7-$EBF8',stream=f'{STREAM_START:04X}-{STREAM_END_EXCLUSIVE-1:04X}',
         stream_length=len(data),stream_sha256=hashlib.sha256(data).hexdigest(),
         original_stream_command_positions=[f'{p:04X}' for p in control_positions],
         original_stream_bytes_consumed=expected_sum+1,per_case_ppudata_writes=2048,
         ram_19_after_return=1,ram_07A0_after_return=0,ram_07A6_after_return=0,
         strict_new_prg_bytes=0,strict_cumulative_prg_bytes=49404,vpp=24,
         limitations='conditional $B570 entry, fixed PPUSTATUS=0, no IRQ/NMI scheduling, no pixel or reference emulator parity, live reset-to-frame producer missing')

if __name__=='__main__':
    if len(sys.argv) not in (2,3):raise SystemExit('usage: audit_0508_phase9.py JP-ROM.nes [report.json]')
    o=audit(sys.argv[1])
    if len(sys.argv)==3:Path(sys.argv[2]).write_text(json.dumps(o,indent=2)+'\n')
    print('0508 phase9 PASS',o['cases'],'cases',o['instructions_per_case'],'instructions/case')
