#!/usr/bin/env python3
"""0508 phase 5: ROM-locked mapped-bus loader execution and five bounded streams.

This is a conditional local proof with no IRQ/cycle simulation or proof that
$07A0 is globally within 0..4. It DOES execute 6502 JSR/RTS stack effects,
mapper writes and zero-page-indirect bank-$0E reads. Never claims full parity.
"""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
ROM_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
PTRS=(0xBEA4,0xBEDB,0xBF03,0xBE8B,0xBF1C)

class CPU:
    def __init__(self,prg,idx,seed):
        self.prg=prg;self.bank=10;self.ram=bytearray(2048)
        self.pc=0xB7F7;self.sp=0xFD;self.a=(seed*13)&255;self.x=(seed*5)&255;self.y=(seed*7)&255
        self.c=bool(seed&1);self.z=bool(seed&2);self.n=bool(seed&4)
        self.ram[0x7A0]=idx;self.ram[0x23]=10
        self.writes=[];self.mapper_writes=[];self.read_0e=[];self.visits={};self.steps=0
        self.push(0x8F);self.push(0xFF) # synthetic caller return $8FFF; RTS -> $9000
    def read(self,a):
        a&=65535
        if a<0x2000:return self.ram[a&2047]
        if 0x8000<=a<=0xBFFF:return self.prg[self.bank*0x4000+a-0x8000]
        if a>=0xE000:return self.prg[31*0x2000+a-0xE000]
        raise AssertionError(f'unmapped bus read {a:04X}')
    def write(self,a,v):
        a&=65535;v&=255
        if a<0x2000:
            self.ram[a&2047]=v;self.writes.append((self.pc,a&2047,v));return
        if a==0x8000:
            assert v in (10,14),v
            self.bank=v;self.mapper_writes.append((self.pc,v));return
        raise AssertionError(f'unmapped bus write {a:04X} at {self.pc:04X}')
    def push(self,v):
        self.ram[0x100+self.sp]=v&255;self.sp=(self.sp-1)&255
    def pop(self):
        self.sp=(self.sp+1)&255;return self.ram[0x100+self.sp]
    def nz(self,v):
        self.z=(v&255)==0;self.n=bool(v&128)
    def run(self):
        while self.pc!=0x9000:
            assert self.steps<20000,(self.pc,self.steps)
            self.steps+=1;at=self.pc;self.visits[at]=self.visits.get(at,0)+1
            op=self.read(at);v=self.read((at+1)&65535)
            w=v|(self.read((at+2)&65535)<<8)
            p=at+1
            if op==0xAD: # LDA abs
                self.a=self.read(w);self.nz(self.a);p=at+3
            elif op==0xA9: # LDA imm
                self.a=v;self.nz(self.a);p=at+2
            elif op==0xA0: # LDY imm
                self.y=v;self.nz(self.y);p=at+2
            elif op==0xA2: # LDX imm
                self.x=v;self.nz(self.x);p=at+2
            elif op==0x0A: # ASL A
                self.c=bool(self.a&128);self.a=(self.a<<1)&255;self.nz(self.a)
            elif op==0x4A: # LSR A
                self.c=bool(self.a&1);self.a>>=1;self.nz(self.a)
            elif op==0xA8: # TAY
                self.y=self.a;self.nz(self.y)
            elif op==0xB9: # LDA abs,Y
                self.a=self.read((w+self.y)&65535);self.nz(self.a);p=at+3
            elif op==0xB1: # LDA (zp),Y
                ptr=self.read(v)|(self.read((v+1)&255)<<8)
                addr=(ptr+self.y)&65535
                assert self.bank==14 and 0x8000<=addr<0xC000,(self.bank,addr)
                self.a=self.read(addr);self.nz(self.a);self.read_0e.append((self.pc,addr,self.y,self.a));p=at+2
            elif op==0x85: # STA zp
                self.write(v,self.a);p=at+2
            elif op==0x8D: # STA abs
                self.write(w,self.a);p=at+3
            elif op==0x9D: # STA abs,X
                self.write((w+self.x)&65535,self.a);p=at+3
            elif op==0x29: # AND imm
                self.a&=v;self.nz(self.a);p=at+2
            elif op==0xC9: # CMP imm
                self.c=self.a>=v;self.nz((self.a-v)&255);p=at+2
            elif op==0xF0: # BEQ rel
                p=at+2
                if self.z:p=(p+(v if v<128 else v-256))&65535
            elif op==0xE8: # INX
                self.x=(self.x+1)&255;self.nz(self.x)
            elif op==0xC8: # INY
                self.y=(self.y+1)&255;self.nz(self.y)
            elif op==0x48: # PHA
                self.push(self.a)
            elif op==0x68: # PLA
                self.a=self.pop();self.nz(self.a)
            elif op==0x20: # JSR absolute
                assert w in (0xFB96,0xE2D0),(hex(at),hex(w))
                self.push(((at+2)>>8)&255);self.push((at+2)&255);p=w
            elif op==0x60: # RTS
                p=((self.pop()|(self.pop()<<8))+1)&65535
            elif op==0x4C: # JMP abs
                p=w
            else:raise AssertionError(f'unsupported {op:02X} at {at:04X}, bank {self.bank:02X}')
            self.pc=p&65535
        assert self.sp==0xFD and self.bank==10 and self.ram[0x23]==10
        return self

def audit(path):
    rom=Path(path).read_bytes();assert len(rom)==393232 and hashlib.sha256(rom).hexdigest()==ROM_SHA
    p=rom[16:16+262144]
    b=lambda raw,a,n:p[raw*16384+a-0x8000:raw*16384+a-0x8000+n]
    f=lambda a,n:p[31*8192+a-0xE000:31*8192+a-0xE000+n]
    assert f(0xFB96,15)==bytes.fromhex('a9 0e 20 d0 e2 b1 08 48 a9 0a 20 d0 e2 68 60')
    assert f(0xE2D0,6)==bytes.fromhex('85 23 8d 00 80 60')
    assert b(10,0xB8C2,10)==bytes.fromhex('a4 be db be 03 bf 8b be 1c bf')
    assert tuple(int.from_bytes(b(10,0xB8C2+2*i,2),'little') for i in range(5))==PTRS
    assert b(10,0xB7F7,3)==bytes.fromhex('ad a0 07')
    assert b(10,0xB872,1)==b'\x60'
    streams=[];occupied=set();cases=0;helper_invocations=0;obj_total=0
    for idx,ptr in enumerate(PTRS):
        header=b(14,ptr,4); assert len(header)==4
        n=next(i for i in range(26) if b(14,ptr+4+5*i,1)==b'\xff')
        assert 0<n<=22,(idx,n)
        stop=ptr+4+5*n
        record=b(14,ptr,stop-ptr+1)
        assert len(record)==4+5*n+1
        assert all(record[4+5*i]!=0xFF for i in range(n))
        assert record[-1]==255
        starts=list(range(ptr,stop+1))
        assert occupied.isdisjoint(starts),(idx,ptr)
        occupied.update(starts);obj_total+=n
        obj=[tuple(record[4+5*i:9+5*i]) for i in range(n)]
        for seed in range(256):
            cpu=CPU(p,idx,seed).run();cases+=1
            assert cpu.ram[8:10]==ptr.to_bytes(2,'little')
            assert (cpu.ram[0x34],cpu.ram[0x35],cpu.ram[0x36],cpu.ram[0x54],cpu.ram[0x72])==(
                header[0]>>4,header[0]&15,header[1]>>4,header[1]&15,header[1]&1)
            assert cpu.ram[0x7A1]==header[2] and cpu.ram[0x54E]==header[3]
            assert cpu.ram[0x7A0]==idx and cpu.ram[0x7A6]==0 and cpu.ram[0x10]==0
            assert cpu.x==(n+1)&255
            for j,o in enumerate(obj,1):
                assert (cpu.ram[0x48C+j],cpu.ram[0x400+j],cpu.ram[0x438+j],
                        cpu.ram[0x41C+j],cpu.ram[0x4A8+j],cpu.ram[0x54E+j])==(*o,1)
            assert len(cpu.mapper_writes)==2*len(cpu.read_0e)
            assert all(cpu.mapper_writes[k:k+2]==[(0xE2D2,14),(0xE2D2,10)]
                       for k in range(0,len(cpu.mapper_writes),2))
            assert len(cpu.read_0e)==(7+5*n)  # header byte0 twice, byte1 twice, 2,3, each object(5), FF
            assert cpu.read_0e[0][1]==ptr and cpu.read_0e[-1][1]==stop
            assert all(b(14,a,1)==bytes([value]) for site,a,y,value in cpu.read_0e)
            assert all(pc==0xFB9B for pc,a,y,v in cpu.read_0e)
            assert cpu.c and cpu.z and not cpu.n # CMP #FF at sentinel, then RTS: carry set/zero set
            helper_invocations+=len(cpu.read_0e)
        streams.append({'index':idx,'start_cpu':f'{ptr:04X}',
            'end_cpu_inclusive':f'{stop:04X}', 'bytes':len(record),
            'objects':n,'header':header.hex().upper(),
            'sha256':hashlib.sha256(record).hexdigest(),
            'physical_8k_prg':29})
    assert obj_total==30
    assert len(occupied)==175 and min(occupied)==0xBE8B and max(occupied)==0xBF39
    assert occupied==set(range(0xBE8B,0xBF3A))
    total=b(14,0xBE8B,175)
    return {'status':'PROVISIONAL_LOCAL_CONDITIONAL_ONLY','jp_rom_sha256':ROM_SHA,
        'executed_code_path':'raw0A:B7F7-B872 -> fixed FB96/FBA4, fixed E2D0/E2D5',
        'source_data_mapping':'raw VRC6 0E physical PRG29 CPU BE8B-BF39',
        'streams':streams,'distinct_stream_source_bytes':175,'contiguous_source_sha256':hashlib.sha256(total).hexdigest(),
        'unique_objects':obj_total,'complete_loader_cases':cases,
        'mapped_indirect_rom_reads':helper_invocations,'mapper_register_writes':2*helper_invocations,
        'all_helper_calls_returned_to_bank_0A':True,
        'exceptions':'Only 07A0=0..4, no IRQs, CPU/PPU side effects beyond documented mapped reads/writes unmodeled',
        'global_07A0_reachability':'UNPROVED','strict_new_prg_bytes':0,'strict_cumulative_prg_bytes':49404,'vpp':24}
if __name__=='__main__':
    assert len(sys.argv) in (2,3)
    r=audit(sys.argv[1]);
    if len(sys.argv)==3:Path(sys.argv[2]).write_text(json.dumps(r,indent=2)+'\n')
    print('0508 phase5 ROM-backed mapped-bus loader PASS')
    print('5 streams / 30 objects / 175 source bytes; cases',r['complete_loader_cases'])
    print('helper reads',r['mapped_indirect_rom_reads'],'mapper writes',r['mapper_register_writes'])
    print('strict coverage remains',r['strict_cumulative_prg_bytes'])