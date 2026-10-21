#!/usr/bin/env python3
"""JP0666: actual owner-ROM 6502 opcode execution vs detached C11 reg events.

Start PC=$811F (original raw05) and stop at $86DA, with deliberately
synthetic sound RAM. Confirms byte-exact *bounded branch writes only*;
it does not prove prior setup, original game/NMI execution or chip timing.
Owner-ROM bytes, notes, and event dumps never leave this machine.
"""
from __future__ import annotations
import argparse
import ctypes
from hashlib import sha256
import json
from pathlib import Path

EXPECTED_SHA = '958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
CORE_SHA = 'e2c3ff3d7e9f96b598610a8028f5b92a606fac7f9acb2977811146fa145fdb67'

class Write(ctypes.Structure):
    _fields_ = [('address',ctypes.c_uint16),('value',ctypes.c_uint8)]
class Input(ctypes.Structure):
    _fields_=[(x,ctypes.c_uint8) for x in ('slot','note','octave','transpose','detune','apu_gate','high_cache','flag_011b','flag_017e','flag_018e','flag_06b4')]
class Plan(ctypes.Structure):
    _fields_=[('period_before_detune',ctypes.c_uint16),('period_after_detune',ctypes.c_uint16),('high_cache_after',ctypes.c_uint8),('stored_period_low',ctypes.c_uint8),('write_count',ctypes.c_size_t),('writes',Write*2)]

class CPU:
    def __init__(self,bank:bytes,i:Input):
        assert len(bank)==16384
        self.mem=bytearray(65536)
        self.mem[0x8000:0xc000]=bank
        self.mem[0x0200]=i.note
        self.mem[0xe0:0xe2]=b'\x00\x02'
        slot=i.slot
        self.mem[0xee]=slot
        self.mem[0x01a8+slot]=i.transpose
        self.mem[0x01a3+slot]=i.octave
        self.mem[0x0195+slot]=i.detune
        self.mem[0x0163+slot]=i.high_cache
        self.mem[0x011b+slot]=i.flag_011b
        self.mem[0x017e+slot]=i.flag_017e
        self.mem[0x018e+slot]=i.flag_018e
        self.mem[0x06b4+slot]=i.flag_06b4
        self.mem[0x010e+(slot==4)]=i.apu_gate
        self.pc=0x811f
        self.sp=0xfd
        self.a=0
        self.x=slot
        self.y=0
        self.c=self.z=self.n=self.v=0
        self.writes=[]
        self.nsteps=0
    def read(self,a):return self.mem[a&65535]
    def write(self,a,v):
        a&=65535;v&=255;self.mem[a]=v
        if (0x4000<=a<=0x4017) or (a in (0x9000,0x9001,0x9002,0xa000,0xa001,0xa002,0xb000,0xb001,0xb002)):
            self.writes.append((a,v))
    def next(self):
        v=self.read(self.pc);self.pc=(self.pc+1)&65535;return v
    def next16(self):return self.next()|self.next()<<8
    def push(self,v):self.write(0x100+self.sp,v);self.sp=(self.sp-1)&255
    def pop(self):self.sp=(self.sp+1)&255;return self.read(0x100+self.sp)
    def nz(self,v):v&=255;self.n=int(bool(v&128));self.z=int(v==0);return v
    def add(self,other):
        res=self.a+other+self.c; self.v=int(bool((~(self.a^other)&(self.a^res))&128));self.c=int(res>255);self.a=self.nz(res)
    def sub(self,other):
        self.add(other^255)
    def cmp(self,a,b):d=(a-b)&255;self.c=int(a>=b);self.nz(d)
    def branch(self,cond):
        d=self.next();
        if cond:self.pc=(self.pc+(d if d<128 else d-256))&65535
    def run(self):
        while self.pc!=0x86da:
            self.nsteps+=1
            if self.nsteps>350:raise ValueError('opcode step budget exceeded')
            pc=self.pc;op=self.next()
            if op==0xb1: # LDA (zp),Y
                z=self.next();a=self.read(z)|(self.read((z+1)&255)<<8);self.a=self.nz(self.read(a+self.y))
            elif op==0x29:self.a=self.nz(self.a&self.next())
            elif op==0x09:self.a=self.nz(self.a|self.next())
            elif op==0x4a:self.c=self.a&1;self.a=self.nz(self.a>>1)
            elif op==0x46:
                at=self.next();v=self.read(at);self.c=v&1;self.write(at,self.nz(v>>1))
            elif op==0x66:
                at=self.next();v=self.read(at);new=((self.c<<7)|(v>>1))&255;self.c=v&1;self.write(at,self.nz(new))
            elif op==0xaa:self.x=self.nz(self.a)
            elif op==0x8a:self.a=self.nz(self.x)
            elif op==0xa8:self.y=self.nz(self.a)
            elif op==0x84:self.write(self.next(),self.y)
            elif op==0x85:self.write(self.next(),self.a)
            elif op==0xa4:self.y=self.nz(self.read(self.next()))
            elif op==0xa5:self.a=self.nz(self.read(self.next()))
            elif op==0xa6:self.x=self.nz(self.read(self.next()))
            elif op==0xa9:self.a=self.nz(self.next())
            elif op==0xbd:self.a=self.nz(self.read(self.next16()+self.x))
            elif op==0xb9:self.a=self.nz(self.read(self.next16()+self.y))
            elif op==0xad:self.a=self.nz(self.read(self.next16()))
            elif op==0x9d:self.write(self.next16()+self.x,self.a)
            elif op==0x99:self.write(self.next16()+self.y,self.a)
            elif op==0x8d:self.write(self.next16(),self.a)
            elif op==0x20:
                dest=self.next16();ret=(self.pc-1)&65535;self.push(ret>>8);self.push(ret&255);self.pc=dest
            elif op==0x60:self.pc=((self.pop()|(self.pop()<<8))+1)&65535
            elif op==0x4c:self.pc=self.next16()
            elif op==0x18:self.c=0
            elif op==0x38:self.c=1
            elif op==0x79:self.add(self.read(self.next16()+self.y))
            elif op==0x65:self.add(self.read(self.next()))
            elif op==0xe5:self.sub(self.read(self.next()))
            elif op==0xe9:self.sub(self.next())
            elif op==0xc0:self.cmp(self.y,self.next())
            elif op==0xe0:self.cmp(self.x,self.next())
            elif op==0xc9:self.cmp(self.a,self.next())
            elif op==0xdd:self.cmp(self.a,self.read(self.next16()+self.x))
            elif op==0xd0:self.branch(not self.z)
            elif op==0xf0:self.branch(bool(self.z))
            elif op==0xb0:self.branch(bool(self.c))
            elif op==0x90:self.branch(not self.c)
            elif op==0x30:self.branch(bool(self.n))
            elif op==0x10:self.branch(not self.n)
            elif op==0xc6:
                at=self.next();self.write(at,self.nz(self.read(at)-1))
            elif op==0xe6:
                at=self.next();self.write(at,self.nz(self.read(at)+1))
            elif op==0x48:self.push(self.a)
            elif op==0x68:self.a=self.nz(self.pop())
            elif op==0xe8:self.x=self.nz(self.x+1)
            elif op==0xea:pass
            else:raise ValueError(f'unhandled original opcode ${op:02X} at ${pc:04X} ({self.nsteps} steps)')
        return self

def authenticated_bank(path:Path)->bytes:
    rom=path.read_bytes()
    if len(rom)!=393232 or sha256(rom).hexdigest()!=EXPECTED_SHA:
        raise ValueError('ROM differs from authenticated original JP cartridge')
    bank=rom[16+5*16384:16+6*16384]
    if sha256(bank[1:0x87ae-0x8000]).hexdigest()!=CORE_SHA:
        raise ValueError('JP 04FB original interpreter opcode span differs')
    return bank

def compare(lib,bank):
    dll=ctypes.CDLL(str(lib))
    fn=dll.cviii_jp0666_note_plan
    fn.argtypes=[ctypes.POINTER(ctypes.c_uint8),ctypes.c_size_t,ctypes.POINTER(Input),ctypes.POINTER(Plan)]
    fn.restype=ctypes.c_bool
    original=(ctypes.c_uint8*len(bank)).from_buffer_copy(bank)
    n=0
    counts=[0]*5
    for slot in range(5):
      for note in range(0,0xc0,0x10):
       for octave in range(6):
        for transpose in (0,2,4,0x82,0x84,0x90):
         for detune in (0,1,3,0x7f,0x80,0x81,0x87,0xff):
          for gate,cache,flags,flag17 in ((0,0,0,0),(0,0xff,0x81,0x10),(1,0,0,0x10),(1,0xff,0x81,0)):
           inp=Input(slot,note,octave,transpose,detune,gate,cache,flags,flag17,0,0x80)
           out=Plan()
           if not fn(original,len(bank),ctypes.byref(inp),ctypes.byref(out)):
               continue
           cpu=CPU(bank,inp).run()
           writes=[(out.writes[i].address,out.writes[i].value) for i in range(out.write_count)]
           scratch=cpu.read(0xec)|(cpu.read(0xed)<<8)
           pre=cpu.read(0x01ad+slot)|(cpu.read(0x01b2+slot)<<8)
           errors=[]
           if writes!=cpu.writes:errors.append('writes')
           if scratch!=out.period_after_detune:errors.append('period')
           if pre!=out.period_before_detune:errors.append('original-unscaled-cache')
           if slot>=3:
               if cpu.read(0x0163+slot)!=out.high_cache_after:errors.append('APU-high-cache')
               if cpu.read(0x019c+slot)!=out.stored_period_low:errors.append('APU-low-cache')
           if errors:
               raise AssertionError(f'original 6502 != C11 on {errors} case '+repr((slot,note,octave,detune,gate,cache,flags,flag17))+
                                    f': oracle={cpu.writes}, c11={writes}, scratch={scratch:04x}/{out.period_after_detune:04x}, pre={pre:04x}/{out.period_before_detune:04x}, pc={cpu.pc:04x}')
           n+=1;counts[slot]+=1
    return dict(source='authenticated_original_6502_instruction_fetch', cases=n,cases_by_slot=counts,
                tested_entry_pc='811F',stop_pc='86DA',time_cycle_parity='not_exercised',
                original_runtime_liveness='not_exercised',
                limitations='hypothetical branch RAM; bounded positive/negative transpose, $06B4 negative, no E1 timing/envelope, no DMC/noise')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--lib',type=Path,required=True)
    p.add_argument('--json',type=Path)
    a=p.parse_args()
    result=compare(a.lib,authenticated_bank(a.rom))
    if a.json:a.json.write_text(json.dumps(result,indent=2)+'\n')
    print(f'PASS JP0666 genuine original-6502 vs C11: {result["cases"]} bounded note cases; hardware timing NOT VERIFIED')
if __name__=='__main__':main()
