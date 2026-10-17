#!/usr/bin/env python3
"""ROM-locked 0508 P7: two conditional NMI dispatch entries and exact E7FB stack ABI.

This deliberately does not run RESET/NMI scheduler or claim gameplay liveness. An
IRQ-only intervening window is handled by the separate verified Phase 6 audit.
"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

ROM_SHA = '958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'

class CPU:
    def __init__(self, prg: bytes, saved_y: int, room_field: int):
        self.prg=prg; self.mem=bytearray(0x800); self.bank=0x00
        self.a=0; self.x=0x51; self.y=saved_y; self.sp=0xFD
        self.c=False; self.z=False; self.n=False; self.pc=0
        self.mem[0x18]=0x0C; self.mem[0x19]=0x13
        self.mem[0x789]=room_field; self.mem[0x23]=0x00
        self.mapper=[];self.visits=[];self.writes=[];self.dispatch_reads=[]
    def read(self,a):
        a &= 0xFFFF
        if a<0x2000:return self.mem[a & 0x7FF]
        if 0x8000<=a<0xC000:
            return self.prg[self.bank*0x4000+a-0x8000]
        if a>=0xE000:
            return self.prg[31*0x2000+a-0xE000]
        raise AssertionError(f'unmapped read ${a:04X}')
    def wr(self,a,v):
        a&=0xFFFF;v&=0xFF
        if a<0x2000:
            self.mem[a&0x7FF]=v;self.writes.append((self.pc,a&0x7FF,v));return
        if a==0x8000:
            assert v==0x0A,(self.pc,v)
            self.bank=v;self.mapper.append((self.pc,v));return
        raise AssertionError(f'unmapped write ${a:04X}')
    def push(self,v):
        self.mem[0x100+self.sp]=v&255;self.sp=(self.sp-1)&255
    def pop(self):
        self.sp=(self.sp+1)&255;return self.mem[0x100+self.sp]
    def nz(self,v):
        self.z=(v&255)==0;self.n=bool(v&0x80)
    def run(self,entry,stop):
        assert self.sp==0xFD
        # Parent of E35C: synthetic return address. The E7FB call must consume
        # ONLY its own inline-dispatch JSR return, leaving this parent on stack.
        self.push(0x8F);self.push(0xFF)
        self.pc=entry;steps=0;visited=[]
        while self.pc!=stop:
            assert steps<80,(hex(self.pc),steps)
            steps+=1;at=self.pc;visited.append(at);self.visits.append(at)
            op=self.read(at);v=self.read(at+1)
            w=v|(self.read(at+2)<<8)
            next_pc=(at+1)&0xFFFF
            if op==0xA9: # LDA #imm
                self.a=v;self.nz(self.a);next_pc=at+2
            elif op==0xA5: # LDA zp
                self.a=self.read(v);self.nz(self.a);next_pc=at+2
            elif op==0xAD: # LDA abs
                self.a=self.read(w);self.nz(self.a);next_pc=at+3
            elif op==0x85: # STA zp
                self.wr(v,self.a);next_pc=at+2
            elif op==0x84: # STY zp
                self.wr(v,self.y);next_pc=at+2
            elif op==0x8D: # STA abs
                self.wr(w,self.a);next_pc=at+3
            elif op==0x0A: # ASL accumulator, 8-bit
                self.c=bool(self.a&128);self.a=(self.a*2)&255;self.nz(self.a)
            elif op==0xA8: # TAY
                self.y=self.a;self.nz(self.y)
            elif op==0xC8: # INY
                self.y=(self.y+1)&255;self.nz(self.y)
            elif op==0xA4: # LDY zp
                self.y=self.read(v);self.nz(self.y);next_pc=at+2
            elif op==0x68: # PLA
                self.a=self.pop();self.nz(self.a)
            elif op==0xB1: # LDA (zp),Y (zero-page wrap)
                ptr=self.read(v)|(self.read((v+1)&255)<<8)
                addr=(ptr+self.y)&0xFFFF
                self.a=self.read(addr);self.nz(self.a);next_pc=at+2
                if at in (0xE806,0xE80B):self.dispatch_reads.append((at,addr,self.a))
            elif op==0x20: # JSR absolute
                self.push((at+2)>>8);self.push((at+2)&255);next_pc=w
            elif op==0x60: # RTS
                next_pc=((self.pop()|(self.pop()<<8))+1)&0xFFFF
            elif op==0x4C: # JMP absolute
                next_pc=w
            elif op==0x6C: # JMP (ind), hardware page wrap
                hi=(w&0xFF00)|((w+1)&255)
                next_pc=self.read(w)|(self.read(hi)<<8)
            else:raise AssertionError(f'op {op:02X} at {at:04X}')
            self.pc=next_pc&0xFFFF
        assert self.sp==(0xFD if stop==0x9000 else 0xFB),(self.sp,steps)
        return visited

def audit(path):
    rom=Path(path).read_bytes()
    assert len(rom)==393232 and hashlib.sha256(rom).hexdigest()==ROM_SHA
    prg=rom[16:16+0x40000]
    b=lambda a,n:prg[0x0A*0x4000+a-0x8000:0x0A*0x4000+a-0x8000+n]
    f=lambda a,n:prg[31*0x2000+a-0xE000:31*0x2000+a-0xE000+n]
    assert f(0xE51E,8)==bytes.fromhex('a9 0a 20 d0 e2 4c a4 af')
    assert f(0xE526,8)==bytes.fromhex('a9 0a 20 d0 e2 4c cc b4')
    assert f(0xE2D0,6)==bytes.fromhex('85 23 8d 00 80 60')
    assert f(0xE7FB,25)==bytes.fromhex('0a 84 03 a8 c8 68 85 00 68 85 01 b1 00 85 02 c8 b1 00 a4 03 85 03 6c 02 00')
    assert b(0xAFA4,5)==bytes.fromhex('a5 19 20 fb e7')
    assert b(0xB4CC,5)==bytes.fromhex('a5 19 20 fb e7')
    assert int.from_bytes(b(0xAFA9+2*0x13,2),'little')==0xB36B
    assert int.from_bytes(b(0xB4D1,2),'little')==0xB570
    assert b(0xB36B,15)==bytes.fromhex('ad 89 07 8d 81 07 a9 0d 85 18 a9 00 85 19 60')
    assert f(0xE363+2*0x0C,2)==bytes.fromhex('1e e5')
    assert f(0xE363+2*0x0D,2)==bytes.fromhex('26 e5')
    cases=0;first_steps=None;second_steps=None
    for field in range(256):
      for saved_y in range(256):
        cpu=CPU(prg,saved_y,field)
        first=cpu.run(0xE51E,0x9000)
        assert first[0]==0xE51E and first[-1]==0xB379
        assert cpu.mapper==[(0xE2D2,0x0A)]
        assert (cpu.mem[0x18],cpu.mem[0x19],cpu.mem[0x781],cpu.mem[0x789])==(0x0D,0,field,field)
        assert cpu.y==saved_y and cpu.x==0x51 and cpu.bank==0x0A and cpu.mem[0x23]==0x0A
        assert cpu.dispatch_reads==[(0xE806,0xAFCF,0x6B),(0xE80B,0xAFD0,0xB3)]
        assert cpu.mem[0:4]==bytes((0xA8,0xAF,0x6B,0xB3))
        assert cpu.c==False # selector 13 < 80, E7FB sets carry clear
        # Between these frame-local calls, assume no other game writer to $18/$19.
        # Separate Phase 6 establishes ordinary IRQ graph preserves both.
        cpu.dispatch_reads.clear();cpu.mapper.clear();cpu.visits.clear()
        second=cpu.run(0xE526,0xB570) # Stop at next state's handler entry
        assert second[0]==0xE526 and second[-1]==0xE811
        assert cpu.mapper==[(0xE2D2,0x0A)]
        assert cpu.dispatch_reads==[(0xE806,0xB4D1,0x70),(0xE80B,0xB4D2,0xB5)]
        assert cpu.mem[0:4]==bytes((0xD0,0xB4,0x70,0xB5))
        assert cpu.y==saved_y and cpu.x==0x51
        assert (cpu.c,cpu.z,cpu.n)==(False,saved_y==0,saved_y>=128)
        assert (cpu.mem[0x18],cpu.mem[0x19],cpu.mem[0x781])==(0x0D,0,field)
        assert cpu.sp==0xFB # parent RTS address still on stack at handler entry
        assert cpu.read(0x1FC)==0xFF and cpu.read(0x1FD)==0x8F
        if first_steps is None:first_steps=len(first);second_steps=len(second)
        else:assert (len(first),len(second))==(first_steps,second_steps)
        cases+=1
    assert cases==65536
    return dict(status='PROVISIONAL_CONDITIONAL_TWO_NMI_ENTRY_WITNESS',rom_sha256=ROM_SHA,
        executed_cases=cases,first_nmi_entry='fixed E51E -> mapper 0A -> raw0A AFA4 -> E7FB -> B36B -> RTS',
        second_nmi_entry='fixed E526 -> mapper 0A -> raw0A B4CC -> E7FB -> B570 entry',
        incoming_saved_y_domain='00-FF',incoming_0789_domain='00-FF',
        initial_ram_18='0C',initial_ram_19='13',after_first_ram_18='0D',after_first_ram_19='00',
        second_target_cpu='B570',first_instructions=first_steps,second_instructions=second_steps,
        first_pointer_reads=['AFCF','AFD0'],second_pointer_reads=['B4D1','B4D2'],
        caveat='synthetic parent stack; first selector precondition NOT proven live, no full NMI or external callees; no unmodeled intervening writers',
        strict_new_prg_bytes=0,strict_cumulative_prg_bytes=49404,vpp=24)

if __name__=='__main__':
    if len(sys.argv) not in (2,3):raise SystemExit('usage: script JP-ROM.nes [report.json]')
    r=audit(sys.argv[1])
    if len(sys.argv)==3:Path(sys.argv[2]).write_text(json.dumps(r,indent=2)+'\n')
    print('P7 conditional two-NMI E7FB/JMP/JSR/RTS machine witness: PASS')
    print('cases',r['executed_cases'],'first/second steps',r['first_instructions'],r['second_instructions'])
    print('strict new bytes',r['strict_new_prg_bytes'])
