#!/usr/bin/env python3
"""Reusable JP 2A03 instruction stepping and VRC6 PRG-window trace harness.

No cycle scheduling, PPU-rendering, APU waveform or IRQ timing. The 6502
instruction-semantics subset is the full documented official NMOS opcode set;
2A03 ADC/SBC stay binary even if the decimal flag is set. Illegal opcodes
intentionally halt. A tested *mapped bus* is not a complete console emulator.
"""
from __future__ import annotations
import hashlib
from dataclasses import dataclass
from pathlib import Path

try:
    from audit_irq_zp10 import OPS
except ImportError:  # standalone JP project research directory
    from dis6502_0508 import D as OPS

ROM_SHA = '958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
C,Z,I,D,B,U,V,N = (1,2,4,8,16,32,64,128)

class Bus:
    def __init__(self,rom:bytes,raw_bank:int=0,ppu_status:int=0):
        assert len(rom)==393232 and hashlib.sha256(rom).hexdigest()==ROM_SHA
        self.prg=rom[16:16+262144]
        self.ram=bytearray(2048)
        self.sram=bytearray(8192)
        self.raw_bank=raw_bank
        self.upper_bank=30
        self.ppu_status=ppu_status & 255
        self.ppu_ctrl=0
        self.ppu_addr=0
        self.ppu_hi=0
        self.ppu_latch=False
        self.ppu_writes=[]  # [(cpu_address, value)]
        self.vram_writes=[] # [(PPU address, value)]
        self.apu_writes=[]  # [(cpu_address, value)]
        self.mapper_writes=[] # [(cpu_address,value)]
        self.unknown_io_reads=[]
        self.unknown_io_writes=[]
        self.trace_reads=False
        self.read_log=[]
    def rb(self,addr:int)->int:
        addr &= 0xFFFF
        if addr<0x2000:
            out=self.ram[addr&0x7FF]
        elif addr<0x4000:
            reg=0x2000+(addr&7)
            if reg==0x2002:
                self.ppu_latch=False;out=self.ppu_status
            else:
                out=0
                self.unknown_io_reads.append(reg)
        elif addr<0x6000:
            out=0
            self.unknown_io_reads.append(addr)
        elif addr<0x8000:
            out=self.sram[addr-0x6000]
        elif addr<0xC000:
            assert 0<=self.raw_bank<16,('invalid 16KiB PRG bank',self.raw_bank)
            out=self.prg[self.raw_bank*0x4000+addr-0x8000]
        elif addr<0xE000:
            assert 0<=self.upper_bank<32
            out=self.prg[self.upper_bank*0x2000+addr-0xC000]
        else:
            out=self.prg[31*0x2000+addr-0xE000]
        if self.trace_reads:self.read_log.append((addr,out))
        return out
    def wb(self,addr:int,val:int):
        addr &= 0xFFFF;val &= 255
        if addr<0x2000:self.ram[addr&0x7FF]=val;return
        if addr<0x4000:
            reg=0x2000+(addr&7);self.ppu_writes.append((reg,val))
            if reg==0x2000:self.ppu_ctrl=val
            elif reg==0x2006:
                if not self.ppu_latch:self.ppu_hi=val&0x3F;self.ppu_latch=True
                else:
                    self.ppu_addr=((self.ppu_hi<<8)|val)&0x3FFF
                    self.ppu_latch=False
            elif reg==0x2007:
                self.vram_writes.append((self.ppu_addr,val))
                self.ppu_addr=(self.ppu_addr+(32 if self.ppu_ctrl&4 else 1))&0x3FFF
            return
        if addr<0x6000:
            self.apu_writes.append((addr,val));return
        if addr<0x8000:self.sram[addr-0x6000]=val;return
        if addr in (0x9000,0x9001,0x9002,0x9003,0xA000,0xA001,0xA002,0xB000,0xB001,0xB002,0xB003):
            self.apu_writes.append((addr,val));return
        if addr==0x8000:
            assert val<16
            self.raw_bank=val
            self.mapper_writes.append((addr,val));return
        if addr==0xC000:
            self.upper_bank=val&31
            self.mapper_writes.append((addr,val));return
        if addr>=0x8000:
            # Expansion-audio / CHR / IRQ mapper controls are observed, but
            # without simulating their timing, audio or PPU bank side effects.
            self.mapper_writes.append((addr,val))
            return
        raise AssertionError('bad write')
    def rw(self,addr:int)->int:
        return self.rb(addr)|(self.rb((addr+1)&0xFFFF)<<8)
    def rzw(self,zp:int)->int:
        return self.rb(zp&255)|(self.rb((zp+1)&255)<<8)

class CPU:
    def __init__(self,bus:Bus,pc:int=0xE00B):
        self.bus=bus
        self.pc=pc&0xFFFF
        self.a=self.x=self.y=0
        self.sp=0xFD
        self.p=U|I
        self.steps=0
        self.last_instruction=None
        self.halted=False
    def flag(self,bit:int)->bool:return bool(self.p&bit)
    def setflag(self,bit:int,yes:bool):
        self.p=(self.p|bit) if yes else (self.p&~bit)
    def nz(self,v:int)->int:
        v &=255
        self.setflag(Z,v==0);self.setflag(N,bool(v&128));return v
    def push(self,v:int):
        self.bus.wb(0x100+self.sp,v&255)
        self.sp=(self.sp-1)&255
    def pop(self)->int:
        self.sp=(self.sp+1)&255
        return self.bus.rb(0x100+self.sp)
    def interrupt(self,vector:int,brk:bool=False):
        pc=self.pc+(1 if brk else 0)
        self.push((pc>>8)&255);self.push(pc&255)
        self.push((self.p|U|B) if brk else ((self.p|U)&~B))
        self.setflag(I,True)
        self.pc=self.bus.rw(vector)
    def step(self):
        assert not self.halted
        pc=self.pc
        op=self.bus.rb(pc)
        assert op in OPS,(f'Unsupported (unofficial) 2A03 opcode ${op:02X}',f'PC ${pc:04X}',self.bus.raw_bank)
        mnemonic,mode,size=OPS[op]
        mode={'indx':'inx','indy':'iny','absx':'abx','absy':'aby'}.get(mode,mode)
        assert size in (1,2,3)
        arg=self.bus.rb((pc+1)&0xFFFF) if size>=2 else 0
        word=(arg | self.bus.rb((pc+2)&0xFFFF)<<8) if size==3 else 0
        self.pc=(pc+size)&0xFFFF
        self.steps+=1
        self.last_instruction=(pc,self.bus.raw_bank,mnemonic,mode,arg if size==2 else word if size==3 else None)
        b=self.bus
        eff=None
        if mode=='imm':val=arg
        elif mode=='zp':eff=arg
        elif mode=='zpx':eff=(arg+self.x)&255
        elif mode=='zpy':eff=(arg+self.y)&255
        elif mode=='abs':eff=word
        elif mode=='abx':eff=(word+self.x)&0xFFFF
        elif mode=='aby':eff=(word+self.y)&0xFFFF
        elif mode=='inx':eff=b.rzw((arg+self.x)&255)
        elif mode=='iny':eff=(b.rzw(arg)+self.y)&0xFFFF
        elif mode=='ind':
            # Real NMOS 6502 indirect JMP high-byte page wrap.
            eff=b.rb(word)|(b.rb((word&0xFF00)|((word+1)&255))<<8)
        elif mode=='rel':val=arg if arg<128 else arg-256
        if mode not in ('imm','rel','imp','acc'):val=b.rb(eff) if mnemonic not in ('STA','STX','STY','JMP','JSR') else 0
        def store(v:int):
            assert eff is not None
            b.wb(eff,v&255)
        if mnemonic in ('LDA','LDX','LDY'):
            setattr(self,{'LDA':'a','LDX':'x','LDY':'y'}[mnemonic],self.nz(val))
        elif mnemonic in ('STA','STX','STY'):
            store({'STA':self.a,'STX':self.x,'STY':self.y}[mnemonic])
        elif mnemonic in ('TAX','TAY','TXA','TYA','TSX','TXS'):
            src,dst={'TAX':('a','x'),'TAY':('a','y'),'TXA':('x','a'),
              'TYA':('y','a'),'TSX':('sp','x'),'TXS':('x','sp')}[mnemonic]
            value=getattr(self,src)
            setattr(self,dst,(value if dst=='sp' else self.nz(value)))
        elif mnemonic in ('INX','INY','DEX','DEY'):
            reg={'INX':'x','INY':'y','DEX':'x','DEY':'y'}[mnemonic]
            setattr(self,reg,self.nz(getattr(self,reg)+(1 if mnemonic.startswith('IN') else -1)))
        elif mnemonic in ('INC','DEC'):
            # NMOS RMW writes back old value before modified value.
            store(val)
            out=self.nz(val+(1 if mnemonic=='INC' else -1));store(out)
        elif mnemonic in ('ORA','AND','EOR'):
            new={'ORA':lambda:self.a|val,'AND':lambda:self.a&val,
                'EOR':lambda:self.a^val}[mnemonic]()
            self.a=self.nz(new)
        elif mnemonic in ('ADC','SBC'):
            # NES 2A03 ignores decimal arithmetic even when D=1.
            carry=int(self.flag(C));v=val if mnemonic=='ADC' else (val^255)
            out=self.a+v+carry;res=out&255
            self.setflag(C,out>255)
            self.setflag(V,bool((~(self.a^v)&(self.a^res)&0x80)))
            self.a=self.nz(res)
        elif mnemonic in ('CMP','CPX','CPY'):
            lhs={'CMP':self.a,'CPX':self.x,'CPY':self.y}[mnemonic]
            self.setflag(C,lhs>=val);self.nz(lhs-val)
        elif mnemonic=='BIT':
            self.setflag(Z,(self.a&val)==0)
            self.setflag(V,bool(val&0x40));self.setflag(N,bool(val&0x80))
        elif mnemonic in ('ASL','LSR','ROL','ROR'):
            orig=self.a if mode=='acc' else val
            oldcarry=int(self.flag(C))
            if mnemonic in ('ASL','ROL'):
                self.setflag(C,bool(orig&128))
                out=(orig<<1)|(oldcarry if mnemonic=='ROL' else 0)
            else:
                self.setflag(C,bool(orig&1))
                out=(orig>>1)|((oldcarry<<7) if mnemonic=='ROR' else 0)
            out=self.nz(out)
            if mode=='acc':self.a=out
            else:store(orig);store(out)
        elif mnemonic in ('BCC','BCS','BEQ','BNE','BMI','BPL','BVC','BVS'):
            taken={'BCC':not self.flag(C),'BCS':self.flag(C),'BEQ':self.flag(Z),
               'BNE':not self.flag(Z),'BMI':self.flag(N),'BPL':not self.flag(N),
               'BVC':not self.flag(V),'BVS':self.flag(V)}[mnemonic]
            if taken:self.pc=(self.pc+val)&0xFFFF
        elif mnemonic=='JSR':
            assert mode=='abs'
            ret=(self.pc-1)&0xFFFF
            self.push(ret>>8);self.push(ret&255)
            self.pc=word
        elif mnemonic=='RTS':
            self.pc=((self.pop()|(self.pop()<<8))+1)&0xFFFF
        elif mnemonic=='RTI':
            self.p=(self.pop()|U)&~B
            self.pc=self.pop()|(self.pop()<<8)
        elif mnemonic=='JMP':self.pc=eff if mode=='ind' else word
        elif mnemonic=='BRK':
            self.pc=(pc+1)&0xFFFF
            self.interrupt(0xFFFE,brk=True)
        elif mnemonic=='PHA':self.push(self.a)
        elif mnemonic=='PHP':self.push(self.p|B|U)
        elif mnemonic=='PLA':self.a=self.nz(self.pop())
        elif mnemonic=='PLP':self.p=(self.pop()|U)&~B
        elif mnemonic in ('CLC','SEC','CLI','SEI','CLD','SED','CLV'):
            bit={'CLC':C,'SEC':C,'CLI':I,'SEI':I,'CLD':D,'SED':D,'CLV':V}[mnemonic]
            self.setflag(bit,mnemonic in ('SEC','SEI','SED'))
        elif mnemonic=='NOP':pass
        else:raise AssertionError(('missing 2A03 semantics',mnemonic,hex(pc)))
        self.p|=U
        assert self.sp in range(256)
        return self.last_instruction
    def run_until(self,target:int,max_steps:int=50000):
        while self.pc!=target:
            assert self.steps<max_steps, ('instruction limit',f'{self.pc:04X}',self.steps)
            self.step()
        return self

if __name__=='__main__':
    import sys
    if len(sys.argv)!=2:raise SystemExit('usage: trace_6502_vrc6_0508.py JP_ROM.nes')
    r=Path(sys.argv[1]).read_bytes()
    bus=Bus(r,10);cpu=CPU(bus,0xB570)
    cpu.push(0x8F);cpu.push(0xFF)
    cpu.run_until(0xEB82)
    print('Reached EB82 after',cpu.steps,'original instruction steps')
