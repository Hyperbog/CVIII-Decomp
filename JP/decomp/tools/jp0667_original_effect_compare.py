#!/usr/bin/env python3
"""JP0667 actual owner-ROM 6502 D/E handler opcode oracle versus C11 RAM.

Only reaches $8001 from particular D/E local handlers. No live NMI, IRQ,
cycle claims, game sound or original waveform parity. No source bytes output.
"""
from __future__ import annotations
import argparse
import ctypes
from hashlib import sha256
from pathlib import Path
from collections import Counter
import json
from jp0666_original_cpu_compare import CPU, Input, authenticated_bank

ROM_SHA = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
RAM_BYTES = 2048

class Effect(ctypes.Structure):
    _fields_ = [("mode",ctypes.c_uint8),("opcode",ctypes.c_uint8),
                ("arguments",ctypes.c_uint8*3),("argument_count",ctypes.c_uint8)]

class EffectCPU(CPU):
    def run(self, stop=0x8001):
        while (self.pc not in stop if isinstance(stop, (set,frozenset,tuple)) else self.pc!=stop):
            self.nsteps+=1
            if self.nsteps>1600:raise ValueError('opcode step budget exceeded')
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
            elif op==0x0a:self.c=(self.a>>7)&1;self.a=self.nz(self.a<<1)
            elif op==0x69:self.add(self.next())
            elif op==0x7d:self.add(self.read(self.next16()+self.x))
            elif op==0xc8:self.y=self.nz(self.y+1)
            elif op==0x88:self.y=self.nz(self.y-1)
            elif op==0xfe:
                at=self.next16()+self.x;self.write(at,self.nz(self.read(at)+1))
            elif op==0xde:
                at=self.next16()+self.x;self.write(at,self.nz(self.read(at)-1))
            elif op==0x1d:self.a=self.nz(self.a|self.read(self.next16()+self.x))
            elif op==0xa0:self.y=self.nz(self.next())
            elif op==0x9e:raise ValueError('unsupported unofficial 6502')
            elif op==0x6c:
                ptr=self.next16()
                self.pc=self.read(ptr)|(self.read((ptr&0xff00)|((ptr+1)&0xff))<<8)
            elif op==0xea:pass
            else:raise ValueError(f'unhandled original opcode ${op:02X} at ${pc:04X} ({self.nsteps} steps)')
        return self

ENTRY = {
    "D": 0x837e,
    **{f"E{i:X}":0x83b7 for i in range(6)},
    "E6":0x83f8, "E7":0x840f, "E8":0x8456,
    "E9":0x845a, "EA":0x848c, "EB":0x849f,
    "EC":0x84ed, "EE":0x852a,
}
MONITORED = tuple(sorted(set(
    [0x01be] + [a+x for a in (0x0112,0x0175,0x017e,0x0187,0x018e,
                  0x01a3,0x01a8,0x01b7,0x03d9,0x03de,0x03e8,0x03ed,
                  0x03f7,0x06a5,0x06b4,0x06b9) for x in range(5)]
)))

def owner_compare(rom:Path, lib:Path)->dict:
    bank=authenticated_bank(rom)
    dll=ctypes.CDLL(str(lib.resolve()))
    fun=dll.cviii_jp0667_effect
    buf=ctypes.POINTER(ctypes.c_uint8)
    fun.argtypes=(buf,ctypes.c_size_t,ctypes.POINTER(Effect),buf,
                  ctypes.c_size_t,ctypes.POINTER(ctypes.c_uint8))
    fun.restype=ctypes.c_bool
    stats=Counter();n=0
    # Includes edge values for widths, nibble packing and state gates.
    values=[0,1,3,4,0x10,0x11,0x20,0x40,0x50,0x7f,0x80,0x85,0xf0,0xff]
    operations=[*range(0xd0,0xe0),*range(0xe0,0xed),0xee]
    for slot in range(5):
      for op in operations:
       if op in (0xed,):continue
       if op==0xeb:cases=[(0,0),(1,0),(0x51,0x31),(0xff,0xe8)]
       elif op>>4==0xd:cases=[(p,q,r) for p,q,r in ((0,0,0),(0xff,0x80,0xff),(0x91,0x40,0xf0),(0x03,0x7f,0x10))]
       elif op>=0xe6:cases=[(p,) for p in values]
       else:cases=[()]
       for k,args in enumerate(cases):
        # EB explicitly has 2 arguments when its first is nonzero, one when zero.
        if op==0xeb: args=(args[0],) if args[0]==0 else args
        # E7's table is only valid for upper nibbles 0..9.
        if op==0xe7 and args[0]>>4>9:continue
        w=len(args)+1
        before=bytearray(((i*11+slot*43+op*3+k*17)&255)
                         for i in range(RAM_BYTES))
        before[0xe0:0xe2]=bytes((0,2))
        before[0xee]=slot
        before[0x0200:0x0200+w]=bytes([op,*args])
        # E7 with $018E negative enters a separate unverified parser path.
        if op==0xe7:before[0x018e+slot]&=0x7f
        inp=Effect(slot,op,(ctypes.c_uint8*3)(*(list(args)+[0]*(3-len(args)))),len(args))
        a=(ctypes.c_uint8*RAM_BYTES).from_buffer_copy(before)
        b=(ctypes.c_uint8*RAM_BYTES)(*([0xa5]*RAM_BYTES))
        consumed=ctypes.c_uint8(0)
        if not fun(a,RAM_BYTES,ctypes.byref(inp),b,RAM_BYTES,ctypes.byref(consumed)):
            raise AssertionError(f"refused test candidate {slot} {op:02x} {args}")
        cpu=EffectCPU(bank,Input(slot,0,0,0,0,0,0,0,0,0,0))
        cpu.mem[:RAM_BYTES]=before
        cpu.pc=ENTRY["D" if op>>4==0xd else f"E{op&15:X}"]
        cpu.x=slot;cpu.a=op&15;cpu.y=0
        cpu.run(stop=0x8001)
        if consumed.value!=w or cpu.y!=w:
            raise AssertionError(f"opcode width mismatch {op:02X} {args}: C {consumed.value} CPU {cpu.y}")
        for where in MONITORED:
            if cpu.read(where)!=b[where]:
                raise AssertionError(f"CPU/C state mismatch {slot} {op:02X} {args} at {where:04X}: oracle {cpu.read(where)} native {b[where]}")
        n+=1;stats[f"{op&0xf0:02X}" if op<0xe0 else f"{op:02X}"]+=1
    # Unknown external-handling paths must NOT be treated as verified.
    for op in (0xed,0xef,0xf0):
        e=Effect(0,op,(ctypes.c_uint8*3)(0,0,0),0)
        a=(ctypes.c_uint8*RAM_BYTES)()
        sentinel=bytes([0x55])*RAM_BYTES
        b=(ctypes.c_uint8*RAM_BYTES).from_buffer_copy(sentinel)
        consumed=ctypes.c_uint8(0x5a)
        if fun(a,RAM_BYTES,ctypes.byref(e),b,RAM_BYTES,ctypes.byref(consumed)) or bytes(b)!=sentinel or consumed.value!=0x5a:
            raise AssertionError('unsupported original handler silently accepted or mutated result')
    return dict(status='bounded_original_rom_6502_equals_detached_C11_effect_RAM',
                cases=n,per_kind=dict(sorted(stats.items())),
                local_source_opcode_authentication=True,
                original_game_liveness=False,absolute_cpu_cycle_parity=False,
                complete_envelope_parity=False,exact_song_pcm_parity=False)

def main()->None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True);p.add_argument('--lib',type=Path,required=True)
    p.add_argument('--json',type=Path)
    a=p.parse_args();data=owner_compare(a.rom,a.lib)
    if a.json:a.json.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    print(f'PASS JP0667 {data["cases"]} original-CPU vs C11 bounded effects; runtime/cycles NOT VERIFIED')
if __name__=='__main__':main()
