#!/usr/bin/env python3
"""Audit source arithmetic feeding raw-$0A:$8CDD's $53 / $07E0,X gates.

Real original-JP instruction fetch; deliberately synthetic initial RAM and
explicit mapper raw-$0A; no global producer completeness or game-frame claim.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from audit_actor_cpu_abi_0509 import BoundedCpu, authenticated_prg, ROM_SHA

STOP = 0xD000
RAW_HASH = 'f302ac2b3ac985520f5d7780d6583a5cbed3f9164b33136484b157b2c99f4a90'
INIT_HASH = 'c866e8b5baf03e06e6de4c026259946d99d6f10e3c5502ea9b151d07316cf70b'
CARRY_HASH = 'c943a5c9efd4ef4b341be5bc5ebfab559d89c89f706b07b8b72f11decd083410'
FIXED_HASH = '1d17a17feea36624e293df0ec5e794394fd6b6df8f706ade139a238d6d04e5c2'

class ProducerCpu(BoundedCpu):
    def __init__(self, prg: bytes, entry: int, ram: bytearray, x: int = 1):
        super().__init__(prg, entry, ram, x)
        self.y = 0xD7
        self.path: set[int] = set()

    def read(self, at: int) -> int:
        if at < 0x800:
            return self.ram[at]
        if 0x8000 <= at <= 0xBFFF:
            return self.prg[0x0A * 0x4000 + at - 0x8000]
        if 0xE000 <= at <= 0xFFFF:
            return self.prg[31 * 8192 + at - 0xE000]
        raise ValueError(f'Unmapped source read ${at:04X}')

    def add(self, rhs: int, subtract: bool) -> None:
        lhs = self.a
        old_c = self.p & 1
        b = rhs ^ 255 if subtract else rhs
        total = lhs + b + old_c
        result = total & 255
        overflow = ((~(lhs ^ b) & (lhs ^ result)) & 0x80) != 0
        self.p = (self.p & ~0x41) | int(total > 255) | (0x40 if overflow else 0)
        self.a = result
        self.nz(result)

    def execute(self, stop: int = STOP) -> None:
        while self.pc != stop:
            at = self.pc
            if not (0x814E <= at <= 0x8156 or
                    0x829E <= at <= 0x82AB or
                    0x83D1 <= at <= 0x840F or
                    0xFB7A <= at <= 0xFB95):
                raise ValueError(f'Unexpected producer source PC ${at:04X}')
            self.path.add(at)
            self.steps += 1
            if self.steps > 32:
                raise ValueError('Source producer failed to reach original RTS')
            op = self.fetch()
            if op == 0xA0:
                self.y = self.fetch(); self.nz(self.y)
            elif op == 0xA5:
                self.a = self.read(self.fetch()); self.nz(self.a)
            elif op == 0x88:
                self.y = (self.y - 1) & 255; self.nz(self.y)
            elif op == 0x84:
                dst = self.fetch(); self.ram[dst] = self.y; self.stores.append(dst)
            elif op == 0xBD:
                address = self.fetch() | (self.fetch() << 8)
                self.a = self.read((address + self.x) & 0xFFFF); self.nz(self.a)
            elif op == 0x9D:
                address = self.fetch() | (self.fetch() << 8)
                dst = (address + self.x) & 0xFFFF
                if dst >= 0x800: raise ValueError(f'Out-of-RAM store ${dst:04X}')
                self.ram[dst] = self.a; self.stores.append(dst)
            elif op == 0x85:
                dst = self.fetch(); self.ram[dst] = self.a; self.stores.append(dst)
            elif op == 0xA9:
                self.a = self.fetch(); self.nz(self.a)
            elif op in (0x10, 0x30, 0xF0):
                off = self.fetch()
                taken = ((self.p & 0x80) == 0 if op == 0x10 else
                         (self.p & 0x80) != 0 if op == 0x30 else
                         (self.p & 0x02) != 0)
                if taken: self.pc = (self.pc + (off if off < 0x80 else off-256)) & 0xFFFF
            elif op == 0x18:
                self.p &= ~1
            elif op == 0x38:
                self.p |= 1
            elif op == 0x65:
                self.add(self.read(self.fetch()), False)
            elif op == 0xE5:
                self.add(self.read(self.fetch()), True)
            elif op == 0x69:
                self.add(self.fetch(), False)
            elif op == 0xE9:
                self.add(self.fetch(), True)
            elif op == 0x29:
                self.a &= self.fetch(); self.nz(self.a)
            elif op == 0x60:
                self.pc = ((self.pop() | (self.pop() << 8)) + 1) & 0xFFFF
            else:
                raise ValueError(f'Unexpected source opcode ${op:02X} at ${at:04X}')
        if self.sp != (0xFD if stop == STOP else 0xFB):
            raise ValueError('Bounded original source stack depth mismatch')


def audit(prg: bytes) -> dict:
    raw=prg[0x0A*16384:0x0B*16384]
    fix=prg[31*8192:]
    checks=((raw,0x83D1,0x8410,0x8000,RAW_HASH),
            (raw,0x829E,0x82AC,0x8000,INIT_HASH),
            (raw,0x814E,0x8157,0x8000,CARRY_HASH),
            (fix,0xFB7A,0xFB96,0xE000,FIXED_HASH))
    for bank,start,end,base,want in checks:
        got=hashlib.sha256(bank[start-base:end-base]).hexdigest()
        if got!=want: raise ValueError(f'Original ROM producer block hash mismatch ${start:04X}: {got}')
    # Offset census is ONLY literal STA abs,X instruction encoding, not a
    # disassembly or a complete proof of indirect/aliased writers.
    stores=[]; p=0
    while True:
        p=raw.find(b'\x9d\xe0\x07',p)
        if p<0: break
        stores.append(p+0x8000);p+=1
    if stores != [0x8154,0x82A5,0x83EE,0x8402]:
        raise ValueError(f'Original raw $0A $07E0,X candidate census drift: {stores}')
    digest=hashlib.sha256(); steps=0; starts=set()
    # All 256 low-coordinate bytes x 256 delta bytes, both actual ROM
    # directional exits: 131072 original source executions.
    for direction in range(2):
        for delta in range(256):
            signext=255 if delta & 128 else 0
            for low in range(256):
                x=1+((low+delta)%12)
                ram=bytearray([0xA5])*0x800
                high=(low*37+delta*13+direction*11)&255
                ram[0x6B]=delta;ram[0x65]=0x80 if direction else 0
                ram[0x07E0+x]=high
                ram[0x07DA+x]=low;ram[0x07D4+x]=low
                ram[0x07C2+x]=0x7D
                cpu=ProducerCpu(prg,0x83D1,ram,x);cpu.execute()
                if direction==0:
                    value=(low-delta)&255
                    borrow=int(low<delta)
                    hi=(high-signext-borrow)&1
                    order=[0x00,0x07DA+x,0x07E0+x]
                    expc=int(high>=signext+borrow)
                else:
                    value=(low+delta)&255
                    carry=int(low+delta>=256)
                    hi=(high+signext+carry)&1
                    order=[0x00,0x07D4+x,0x07E0+x]
                    if hi: order.append(0x07C2+x)
                    expc=int(high+signext+carry>=256)
                expected00=signext
                if (ram[0]!=expected00 or
                    ram[(0x07D4 if direction else 0x07DA)+x]!=value or
                    ram[0x07E0+x]!=hi or
                    ram[0x07C2+x]!=(0 if direction and hi else 0x7D) or
                    cpu.stores!=order or (cpu.p&1)!=expc):
                    raise ValueError(f'ROM indexed coordinate producer mismatch dir={direction} d={delta} lo={low}')
                starts.update(cpu.path);steps+=cpu.steps
                digest.update(bytes((direction,delta,low,high,hi,cpu.p,cpu.steps)))
    # Original fourth raw-bank literal writer: carry from the upstream ADC
    # is an explicitly modeled input, not fabricated evidence for that ADC.
    for carry in (0,1):
        for value in range(256):
            x=1+((value+carry)%12)
            ram=bytearray([0xA5])*0x800
            ram[0x0A]=value
            cpu=ProducerCpu(prg,0x814E,ram,x)
            cpu.p=(cpu.p&~1)|carry
            cpu.execute(0x8157)
            rawsum=value+carry
            expected=rawsum&1
            if (cpu.pc!=0x8157 or ram[0x07E0+x]!=expected or
                cpu.stores != [0x07E0+x] or (cpu.p&1)!=int(rawsum>=256)):
                raise ValueError('Original $8154 coordinate carry-bit store differs')
            starts.update(cpu.path);steps+=cpu.steps
            digest.update(bytes((carry,value,expected,cpu.p,cpu.steps)))
    # Original raw $0A initializer: LDA $0A / STA $07D4,X ;
    # LDA #0 / STA $07E0,X / STA $07C8,X / RTS.
    for src in range(256):
        x=1+(src%12);ram=bytearray([0xA5])*0x800
        ram[0x0A]=src
        cpu=ProducerCpu(prg,0x829E,ram,x);cpu.execute()
        if (cpu.stores!=[0x07D4+x,0x07E0+x,0x07C8+x] or
            [ram[i+x] for i in (0x07D4,0x07E0,0x07C8)]!=[src,0,0]):
            raise ValueError('ROM indexed coordinate initial clear mismatch')
        starts.update(cpu.path);steps+=cpu.steps
        digest.update(bytes((src,cpu.p,cpu.steps)))
    # Original fixed-bank paired $53/$54 arithmetic. Verify every 16-bit
    # input for both source routines; these fixed bytes are already credited.
    for entry, step in ((0xFB7A,1),(0xFB88,-1)):
        for value in range(65536):
            ram=bytearray([0xA5])*0x800
            ram[0x53]=value&255;ram[0x54]=value>>8
            cpu=ProducerCpu(prg,entry,ram);cpu.execute()
            expected=(value+step)&0xFFFF
            if ((ram[0x54]<<8)|ram[0x53])!=expected or cpu.stores!=[0x53,0x54]:
                raise ValueError(f'ROM $53/$54 16-bit arithmetic mismatch {entry:04X} {value}')
            starts.update(cpu.path);steps+=cpu.steps
            digest.update(bytes((entry&255,value&255,value>>8,ram[0x53],ram[0x54],cpu.p)))
    return {'schema':'JP-0509-actor-guard-producer-arithmetic/v1',
      'rom_sha256':ROM_SHA,
      'raw0A_indexed_direct_store_encodings':[f'{i:04X}' for i in stores],
      'source_block_sha256':{'raw0A_83D1_840F':RAW_HASH,'raw0A_829E_82AB':INIT_HASH,'raw0A_814E_8156':CARRY_HASH,'fixed31_FB7A_FB95':FIXED_HASH},
      'raw0A_velocity_cases':131072,'raw0A_initialization_cases':256,'raw0A_carry_bit_cases':512,
      'fixed53_54_increment_cases':65536,'fixed53_54_decrement_cases':65536,
      'total_original_instructions':steps,'distinct_source_pcs':len(starts),
      'outcome_digest_sha256':digest.hexdigest(),
      'verified_local_invariant':'all four raw $0A literal $07E0,X stores have bounded source witnesses; $83D1 masks high-bit to {0,1}, $829E clears it, $814E uses incoming C; fixed $FB7A/$FB88 wrap $53/$54 as a 16-bit pair',
      'proof_limit':'synthetic initial RAM, bounded source routines, direct-encoding candidate census only; no live actor producer/frame/IRQ or global writer-domain proof',
      'new_strict_prg_bytes':0,'new_vpp_points':0}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('rom',type=Path);p.add_argument('--report',type=Path)
    args=p.parse_args();result=audit(authenticated_prg(args.rom))
    if args.report:args.report.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS JP actor guard producer arithmetic:',result['raw0A_velocity_cases'],
      'direction cases;',result['fixed53_54_increment_cases']*2,'fixed counter cases;',
      result['total_original_instructions'],'source instructions')

if __name__=='__main__':main()
