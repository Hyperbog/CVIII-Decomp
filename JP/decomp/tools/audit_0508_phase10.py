#!/usr/bin/env python3
"""0508 phase 10: state-1 sound-call entry and conditional bank return.

ROM-fetched 6502 subset. The cut at bank 0C:$8860 is deliberate:
the remaining sound dispatcher is NOT executed. Separate hypothetical RTS
continuation establishes obligations, not a live complete music-command path.
"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
from audit_0508_phase9 import CPU as PriorCPU
from audit_0508_phase8 import ROM_SHA

class CPU(PriorCPU):
    def __init__(self, prg: bytes, seed: int):
        super().__init__(prg, (seed * 31) & 255, seed, 0)
        self.pc = 0xB58C
        self.ram[0x19] = 1
        self.ram[0x18] = 0x0D
        self.ram[0x23] = 0x0A
        self.ram[0x25] = 0xA5
        self.ram[0x26] = 0xA5
        self.ram[0x68] = (seed * 17 + 7) & 255
        self.sound_writes: list[tuple[int,int,int]] = []
        self.banks: list[tuple[int,int]] = []
        self.entry_x = self.x
        self.entry_y = self.y
    def rd(self, addr: int) -> int:
        addr &= 65535
        # The previous CPU used a fixed raw $0A reader; this model selects
        # the physical 16 KiB bank using the *actual mapped* $8000 writes.
        if 0x8000 <= addr < 0xC000:
            return self.prg[self.ram[0x23]*0x4000 + addr - 0x8000]
        return super().rd(addr)
    def wr(self, addr: int, value: int):
        addr &= 65535
        value &= 255
        if addr == 0x8000:
            assert value < 16
            assert self.ram[0x23] == value, (self.pc, value)
            self.banks.append((self.pc, value))
            return
        if addr in (0x4000,0x4001,0x4004,0x4005,0x400C,0x4015,
                    0x9000,0xA000,0xB000):
            self.sound_writes.append((self.pc,addr,value))
            return
        return super().wr(addr,value)
    def step(self):
        pc=self.pc
        op=self.rd(pc)
        if op == 0xEA: # NOP, including APU reset delay
            self.pc=(pc+1)&65535
            self.steps+=1
        elif op in (0x86, 0xA6, 0x84): # STX/LDX/STY ZP
            loc=self.rd(pc+1)
            if op==0x86:self.wr(loc,self.x)
            if op==0x84:self.wr(loc,self.y)
            if op==0xA6:self.x=self.rd(loc); self.nz(self.x)
            self.pc=pc+2; self.steps+=1
        else:
            super().step()
    def run_to(self, target: int):
        while self.pc!=target:
            assert self.steps<4000,(hex(self.pc),self.steps)
            self.step()

# Independently derived sound reset values for the 0x6B >= 0x50 entry.
EXPECTED_SOUND=[
    (0x4000,0x30),(0x4004,0x30),(0x400C,0x30),
    (0x4001,0x7F),(0x4005,0x7F),
    (0x9000,0x00),(0xA000,0x00),(0xB000,0x00),
    (0x4015,0x0F),
]

def audit(path: str) -> dict:
    rom=Path(path).read_bytes()
    assert len(rom)==393232 and hashlib.sha256(rom).hexdigest()==ROM_SHA
    prg=rom[16:16+0x40000]
    fb=lambda a,n:prg[31*0x2000+a-0xE000:31*0x2000+a-0xE000+n]
    raw=lambda a,n:prg[12*0x4000+a-0x8000:12*0x4000+a-0x8000+n]
    own=lambda a,n:prg[10*0x4000+a-0x8000:10*0x4000+a-0x8000+n]
    assert own(0xB58C,11)==bytes.fromhex('a9 6b 20 49 e2 20 e9 b4 e6 19 60')
    assert own(0xB4E9,5)==bytes.fromhex('a9 00 85 68 60')
    assert fb(0xE249,27)==bytes.fromhex(
        '48 a9 ff 85 26 a5 23 85 25 a9 0c 20 d0 e2 68 '
        '20 50 88 a9 00 85 26 a5 25 4c d0 e2')
    assert fb(0xE2D0,6)==bytes.fromhex('85 23 8d 00 80 60')
    assert raw(0x8850,16)==bytes.fromhex(
        '85 ef c9 6f 90 03 4c 08 89 c9 50 90 e5 20 ae 87')
    assert raw(0x87AE,2)==bytes.fromhex('a9 00')
    assert raw(0x8F55,11)==bytes.fromhex('ea ea ea ea ea ea ea ea ea ea 60')
    seed_count=256
    sound_steps=None
    post_steps=None
    for seed in range(seed_count):
        c=CPU(prg,seed)
        orig_ram=c.ram[:]
        orig_68=c.ram[0x68]
        c.run_to(0x8860)
        assert c.ram[0x23]==0x0C and c.ram[0x25]==0x0A
        assert c.ram[0x26]==0xFF and c.ram[0xEF]==0x6B
        assert c.x==c.entry_x and c.y==c.entry_y
        assert c.ram[0xE2]==seed and c.ram[0xE4]==orig_ram[0xE4]
        assert c.ram[0xEB]==0
        assert all(c.ram[x]==0 for x in range(0x0109,0x0112))
        assert all(c.ram[x]==0 for x in range(0x06D3,0x06DC))
        assert all(c.ram[x]==0 for x in (0x0173,0x017C,0x016A,0x01BF,0x01BE,0x01BD,0x06DC,0x06DD))
        assert [(a,v) for _,a,v in c.sound_writes]==EXPECTED_SOUND
        assert c.banks==[(0xE2D2,0x0C)]
        assert c.ram[0x19]==1 and c.ram[0x68]==orig_68
        assert all(c.ram[k]==orig_ram[k] for k in (0x10,0x7A0,0x7A6,0x18,0x19))
        # Sound routine $8850 is *not* yet followed from $8860. Pop its
        # pending return to model a conditional RTS continuation explicitly.
        lo=c.pop();hi=c.pop()
        assert (lo | hi<<8)==0xE25A
        c.pc=0xE25B
        if sound_steps is None: sound_steps=c.steps
        assert c.steps==sound_steps
        c.run_to(0x9000)  # returns to synthetic parent of $B58C
        assert c.sp==0xFD and c.ram[0x23]==0x0A
        assert c.ram[0x25]==0x0A and c.ram[0x26]==0
        assert c.ram[0x19]==2 and c.ram[0x68]==0
        assert c.banks==[(0xE2D2,0x0C),(0xE2D2,0x0A)]
        assert c.ram[0x18]==0x0D
        post_steps=c.steps if post_steps is None else post_steps
        assert c.steps==post_steps
    return {
        'checkpoint':'0508 phase10 provisional',
        'jp_rom_sha256':ROM_SHA,
        'initial_bank':'0A','sound_bank':'0C',
        'caller':'0A:B58C','helper':'fixed:E249',
        'sound_reset':'0C:87AE','stop_before':'0C:8860',
        'sound_A':0x6B,'sound_reset_register_writes':len(EXPECTED_SOUND),
        'bounded_initial_x_cases':seed_count,
        'instructions_to_music_stream_cutpoint':sound_steps,
        'conditional_post_return_instructions':post_steps-sound_steps,
        'conditional_final_state':{'bank':'0A','19':2,'68':0,'26':0},
        'not_proved':[
            'sound music dispatcher from 0C:8860 and downstream parser returns',
            'external callee never clobbers saved bank byte $25',
            'live reset-to-NMI selector domain or contiguous frames',
            'clock-correct audio, IRQ/NMI interleaving, full-frame parity'
        ],
        'new_strict_prg_bytes':0,'strict_cumulative_prg_bytes':49404,'vpp':24}

if __name__=='__main__':
    if len(sys.argv) not in (2,3):
        raise SystemExit('usage: audit_0508_phase10.py JP-ROM.nes [report.json]')
    r=audit(sys.argv[1]);
    if len(sys.argv)==3:Path(sys.argv[2]).write_text(json.dumps(r,indent=2)+'\n')
    print('Phase10 ROM-mapped audio reset and conditional return PASS',r['bounded_initial_x_cases'])
