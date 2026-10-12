#!/usr/bin/env python3
"""Original 6502 reset/NMI trace with EXPLICITLY scripted I/O, not gameplay proof.

No ROM bytes are embedded or distributed. CPU instructions are decoded from the
user's authenticated Japanese ROM. The PPU/APU/mapper adapters only supply
minimal deterministic input for bounded reset-initialization observations.
Unknown I/O is logged, NOT assumed accurate to Mesen/real hardware.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from dataclasses import dataclass

# Independently enumerated official NMOS 6502 opcode table by addressing mode.
OPCODES='''
00 BRK imp;01 ORA indx;05 ORA zp;06 ASL zp;08 PHP imp;09 ORA imm;0A ASL acc;0D ORA abs;0E ASL abs;10 BPL rel;11 ORA indy;15 ORA zpx;16 ASL zpx;18 CLC imp;19 ORA absy;1D ORA absx;1E ASL absx;20 JSR abs;21 AND indx;24 BIT zp;25 AND zp;26 ROL zp;28 PLP imp;29 AND imm;2A ROL acc;2C BIT abs;2D AND abs;2E ROL abs;30 BMI rel;31 AND indy;35 AND zpx;36 ROL zpx;38 SEC imp;39 AND absy;3D AND absx;3E ROL absx;40 RTI imp;41 EOR indx;45 EOR zp;46 LSR zp;48 PHA imp;49 EOR imm;4A LSR acc;4C JMP abs;4D EOR abs;4E LSR abs;50 BVC rel;51 EOR indy;55 EOR zpx;56 LSR zpx;58 CLI imp;59 EOR absy;5D EOR absx;5E LSR absx;60 RTS imp;61 ADC indx;65 ADC zp;66 ROR zp;68 PLA imp;69 ADC imm;6A ROR acc;6C JMP ind;6D ADC abs;6E ROR abs;70 BVS rel;71 ADC indy;75 ADC zpx;76 ROR zpx;78 SEI imp;79 ADC absy;7D ADC absx;7E ROR absx;81 STA indx;84 STY zp;85 STA zp;86 STX zp;88 DEY imp;8A TXA imp;8C STY abs;8D STA abs;8E STX abs;90 BCC rel;91 STA indy;94 STY zpx;95 STA zpx;96 STX zpy;98 TYA imp;99 STA absy;9A TXS imp;9D STA absx;A0 LDY imm;A1 LDA indx;A2 LDX imm;A4 LDY zp;A5 LDA zp;A6 LDX zp;A8 TAY imp;A9 LDA imm;AA TAX imp;AC LDY abs;AD LDA abs;AE LDX abs;B0 BCS rel;B1 LDA indy;B4 LDY zpx;B5 LDA zpx;B6 LDX zpy;B8 CLV imp;B9 LDA absy;BA TSX imp;BC LDY absx;BD LDA absx;BE LDX absy;C0 CPY imm;C1 CMP indx;C4 CPY zp;C5 CMP zp;C6 DEC zp;C8 INY imp;C9 CMP imm;CA DEX imp;CC CPY abs;CD CMP abs;CE DEC abs;D0 BNE rel;D1 CMP indy;D5 CMP zpx;D6 DEC zpx;D8 CLD imp;D9 CMP absy;DD CMP absx;DE DEC absx;E0 CPX imm;E1 SBC indx;E4 CPX zp;E5 SBC zp;E6 INC zp;E8 INX imp;E9 SBC imm;EA NOP imp;EC CPX abs;ED SBC abs;EE INC abs;F0 BEQ rel;F1 SBC indy;F5 SBC zpx;F6 INC zpx;F8 SED imp;F9 SBC absy;FD SBC absx;FE INC absx
'''
OPS={int(items[0],16):(items[1],items[2]) for part in OPCODES.replace('\n',' ').split(';') if (items:=part.split())}
SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
class ReplayError(RuntimeError):pass

@dataclass
class Bus:
    rom:bytes
    def __post_init__(self):
        if len(self.rom)!=393232 or hashlib.sha256(self.rom).hexdigest()!=SHA: raise ReplayError('Unauthenticated Japanese ROM')
        self.prg=self.rom[16:16+262144]
        self.mem=bytearray(0x10000)
        self.bank=0
        self.mappers=[];self.events=[]
        self.status_polls=0
        self.ppu_data_reads=0
        self.controller_strobe=0
        self.controller_bit=0
        self.unmodeled_reads={}
    def read(self,a):
        a&=0xffff
        if a<0x2000:return self.mem[a&0x7ff]
        if 0x2000<=a<0x4000:
            reg=0x2000+(a&7)
            if reg==0x2002:
                self.status_polls+=1
                value=(0x80 if self.status_polls>=2 else 0)
                self.events.append(['scripted_ppu_status',self.status_polls,value])
                return value
            if reg==0x2007:
                self.ppu_data_reads+=1
                return 0
            self.unmodeled_reads[f'{reg:04X}']=self.unmodeled_reads.get(f'{reg:04X}',0)+1
            return 0
        if a==0x4016:return self.controller_bit
        if a==0x4017:return 0
        if 0x4000<=a<0x8000:
            self.unmodeled_reads[f'{a:04X}']=self.unmodeled_reads.get(f'{a:04X}',0)+1
            return self.mem[a]
        if 0x8000<=a<0xc000:
            if not 0<=self.bank<=15:raise ReplayError('VRC6 mapped non-physical 16K bank')
            return self.prg[self.bank*16384+(a&0x3fff)]
        if a<0xe000:return self.prg[30*8192+(a-0xc000)]
        return self.prg[31*8192+(a-0xe000)]
    def write(self,a,v):
        a&=0xffff;v&=255
        if a<0x2000:self.mem[a&0x7ff]=v;return
        if a==0x8000:
            self.bank=v;self.mappers.append(['PRG16',v]);return
        if a==0x4016:
            self.controller_strobe=v;return
        if 0x2000<=a<0x4000 or 0x4000<=a<0x6000 or 0x8000<=a<0x10000:
            if len(self.events)<10000:self.events.append(['io_write',a,v])
            return
        self.mem[a]=v

class CPU:
    def __init__(self,bus):
        self.b=bus;self.a=self.x=self.y=0;self.p=0x24;self.sp=0xfd
        self.pc=bus.read(0xfffc)|(bus.read(0xfffd)<<8)
        self.count=0;self.hits={};self.first=[]
        self.nmi_count=0;self.nmi_entries=[];self.last_pc=None;self.last_opcode=None
    def flag(self,k):return bool(self.p & k)
    def setflag(self,k,yes):self.p=((self.p|k) if yes else (self.p&~k))&255
    def nz(self,v):self.setflag(2,(v&255)==0);self.setflag(128,v&128)
    def push(self,v):self.b.write(0x100|self.sp,v);self.sp=(self.sp-1)&255
    def pop(self):self.sp=(self.sp+1)&255;return self.b.read(0x100|self.sp)
    def word(self,a):return self.b.read(a)|(self.b.read((a+1)&65535)<<8)
    def address(self,mode):
        fetch=lambda: self._fetch()
        if mode=='imm':return ('value',fetch())
        if mode=='zp':return ('addr',fetch())
        if mode=='zpx':return ('addr',(fetch()+self.x)&255)
        if mode=='zpy':return ('addr',(fetch()+self.y)&255)
        if mode=='abs':v=fetch();return ('addr',v|(fetch()<<8))
        if mode in ('absx','absy'):
            v=fetch()|(fetch()<<8);return ('addr',(v+(self.x if mode=='absx' else self.y))&65535)
        if mode=='ind':
            lo=fetch();hi=fetch();a=lo|(hi<<8);return ('addr',self.b.read(a)|(self.b.read((a&0xff00)|((a+1)&255))<<8))
        if mode=='indx':
            v=(fetch()+self.x)&255;return ('addr',self.b.read(v)|(self.b.read((v+1)&255)<<8))
        if mode=='indy':
            v=fetch();a=self.b.read(v)|(self.b.read((v+1)&255)<<8);return ('addr',(a+self.y)&65535)
        if mode=='rel':
            v=fetch();return ('value',v if v<128 else v-256)
        if mode in ('imp','acc'):return ('none',None)
        raise ReplayError('bad mode '+mode)
    def _fetch(self):v=self.b.read(self.pc);self.pc=(self.pc+1)&65535;return v
    def interrupt(self,nmi=True):
        if nmi:
            self.nmi_count+=1
            self.nmi_entries.append({'pc':self.pc,'bank':self.b.bank,'ram18':self.b.mem[0x18], 'ram1c':self.b.mem[0x1c]})
        self.push(self.pc>>8);self.push(self.pc&255);self.push(self.p&~16|32)
        self.setflag(4,True);vec=0xfffa if nmi else 0xfffe
        self.pc=self.word(vec)
    def step(self):
        pc=self.pc;bank=self.b.bank
        self.count+=1
        self.hits[pc]=self.hits.get(pc,0)+1
        if len(self.first)<120:self.first.append([bank,pc])
        op=self._fetch();self.last_pc=pc;self.last_opcode=op
        if op not in OPS:raise ReplayError(f'unsupported opcode {op:02X} at bank{bank:02X}:${pc:04X} step={self.count}')
        mn,mode=OPS[op]
        kind,loc=self.address(mode)
        get=lambda:self.b.read(loc) if kind=='addr' else loc
        def store(v):self.b.write(loc,v&255)
        if mn in ('LDA','LDX','LDY'):
            v=get();setattr(self,mn[-1].lower(),v);self.nz(v)
        elif mn in ('STA','STX','STY'):store(getattr(self,mn[-1].lower()))
        elif mn in ('AND','ORA','EOR'):
            v=get();self.a= self.a&v if mn=='AND' else self.a|v if mn=='ORA' else self.a^v;self.nz(self.a)
        elif mn=='BIT':
            v=get();self.setflag(2,not self.a&v);self.setflag(64,v&64);self.setflag(128,v&128)
        elif mn in ('ADC','SBC'):
            # NES 2A03 always performs binary arithmetic even with D set.
            v=get();v2=v if mn=='ADC' else v^255
            total=self.a+v2+bool(self.flag(1));new=total&255
            self.setflag(1,total>255);self.setflag(64, bool((~(self.a^v2)&(self.a^new)&0x80)))
            self.a=new;self.nz(new)
        elif mn in ('CMP','CPX','CPY'):
            v=get();r=self.a if mn=='CMP' else self.x if mn=='CPX' else self.y
            self.setflag(1,r>=v);self.nz((r-v)&255)
        elif mn in ('INC','DEC'):
            v=(get()+(1 if mn=='INC' else -1))&255;store(v);self.nz(v)
        elif mn in ('INX','DEX','INY','DEY'):
            reg='x' if mn[-1]=='X' else 'y';v=(getattr(self,reg)+(1 if mn.startswith('IN') else -1))&255
            setattr(self,reg,v);self.nz(v)
        elif mn in ('ASL','LSR','ROL','ROR'):
            v=self.a if mode=='acc' else get();carry=bool(self.flag(1))
            self.setflag(1,bool(v & (1 if mn in ('LSR','ROR') else 128)))
            if mn=='ASL':w=(v<<1)&255
            elif mn=='LSR':w=v>>1
            elif mn=='ROL':w=((v<<1)|carry)&255
            else:w=(v>>1)|(128 if carry else 0)
            if mode=='acc':self.a=w
            else:store(w)
            self.nz(w)
        elif mn in ('TAX','TAY','TXA','TYA','TSX','TXS'):
            left,right={'TAX':('x','a'),'TAY':('y','a'),'TXA':('a','x'),'TYA':('a','y'),'TSX':('x','sp'),'TXS':('sp','x')}[mn]
            v=getattr(self,right);setattr(self,left,v)
            if mn!='TXS':self.nz(v)
        elif mn=='JSR':
            addr=loc;ret=(self.pc-1)&65535;self.push(ret>>8);self.push(ret&255);self.pc=addr
        elif mn=='RTS':self.pc=(self.pop()|(self.pop()<<8))+1&65535
        elif mn=='RTI':self.p=(self.pop()|32)&0xef;self.pc=self.pop()|(self.pop()<<8)
        elif mn=='JMP':self.pc=loc
        elif mn=='PHA':self.push(self.a)
        elif mn=='PLA':self.a=self.pop();self.nz(self.a)
        elif mn=='PHP':self.push(self.p|0x30)
        elif mn=='PLP':self.p=self.pop()|32
        elif mn in ('CLC','SEC','CLI','SEI','CLV','CLD','SED'):
            mask={'CLC':1,'SEC':1,'CLI':4,'SEI':4,'CLV':64,'CLD':8,'SED':8}[mn];self.setflag(mask,mn in ('SEC','SEI','SED'))
        elif mn in ('BPL','BMI','BVC','BVS','BCC','BCS','BNE','BEQ'):
            bit={'BPL':128,'BMI':128,'BVC':64,'BVS':64,'BCC':1,'BCS':1,'BNE':2,'BEQ':2}[mn]
            cond=self.flag(bit)
            take=(not cond if mn in ('BPL','BVC','BCC','BNE') else cond)
            if take:self.pc=(self.pc+loc)&65535
        elif mn=='NOP':pass
        else:raise ReplayError(f'{mn} at {pc:04X}')

def boot(rom:bytes,limit:int=600000, inject_nmi:bool=True, continue_through_nmi:bool=False):
    bus=Bus(rom);cpu=CPU(bus)
    if cpu.pc!=0xe00b:raise ReplayError('Reset vector does not target $E00B')
    boot_at=None;failure=None;first_nmi_call=None;first_nmi_return=None
    for _ in range(limit):
        if cpu.pc==0xE04B and boot_at is None:
            boot_at=cpu.count
            if inject_nmi:cpu.interrupt()
            else:break
        if cpu.nmi_count and cpu.pc==0xE0BF and first_nmi_call is None:
            first_nmi_call={'step':cpu.count,'ram18':bus.mem[0x18],'ram1c':bus.mem[0x1c], 'mapper_bank':bus.bank,'nmi_entry':cpu.nmi_entries[0], 'state13':bus.mem[0x18]==13}
            if not continue_through_nmi:break
        if continue_through_nmi and cpu.nmi_count and cpu.pc==0xE04B and first_nmi_call is not None:
            if cpu.last_opcode!=0x40:raise ReplayError('NMI boundary not reached through original RTI')
            first_nmi_return={'step':cpu.count,'ram18':bus.mem[0x18], 'ram1c':bus.mem[0x1c], 'bank':bus.bank, 'returned_by_rti_at':cpu.last_pc}
            break
        try:cpu.step()
        except ReplayError as e:
            failure=str(e);break
    return {'original_sha256':SHA,'reset_vector':0xE00B,'nmi_vector':cpu.word(0xfffa),
      'cpu_instructions':cpu.count,'boot_loop_reached':boot_at is not None,
      'boot_instruction_count':boot_at,'nmi_injected':inject_nmi and boot_at is not None,
      'nmi_callsite_reached':first_nmi_call is not None,
      'scheduler_call':first_nmi_call,'first_nmi_return':first_nmi_return,'first_failure':failure,
      'original_state0_dispatch_entry_seen':(0xE383 in cpu.hits),
      'original_scheduler_entry_seen':(0xE35C in cpu.hits),
      'initial_trace':cpu.first,'ppu_status_scripted_reads':bus.status_polls,
      'ppu_data_zero_stub_reads':bus.ppu_data_reads,
      'unmodeled_io_reads':bus.unmodeled_reads,'mapper_writes_first_20':bus.mappers[:20],
      'mapping_after':bus.bank,
      'fidelity':'BOUNDED_CPU_REAL_BYTES__SCRIPTED_PPU_STATUS_AND_UNMODELED_IO__NOT_CYCLE_FRAME_OR_GAMEPLAY_PROOF'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--steps',type=int,default=600000);p.add_argument('--through-first-nmi',action='store_true');p.add_argument('--synthetic-frames',type=int,default=0)
    a=p.parse_args();r=boot(a.rom.read_bytes(),a.steps,continue_through_nmi=a.through_first_nmi) if not a.synthetic_frames else scripted_frames(a.rom.read_bytes(),a.synthetic_frames);a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k not in ('initial_trace','unmodeled_io_reads','mapper_writes_first_20')}))

# Phase two utility is intentionally separate from boot(): a periodic synthetic
# interrupt source is not an NES PPU clock and cannot establish real reachability.
def scripted_frames(rom:bytes,frames:int=20,step_limit:int=2000000,idle_instructions:int=120):
    if not 1<=frames<=256 or not 1<=idle_instructions<=3000:raise ValueError('invalid bounded synthetic frame request')
    b=Bus(rom);c=CPU(b);frame_events=[]
    for _ in range(step_limit):
        if c.pc==0xe04b:break
        c.step()
    else:raise ReplayError('scripted reset never reached E04B')
    for i in range(frames):
        # The first and later interrupts are supplied by the harness. The
        # number of main-loop instructions between them is likewise synthetic.
        for j in range(idle_instructions if i else 0):c.step()
        prior=c.pc
        c.interrupt()
        dispatch=None
        for _ in range(step_limit):
            if c.pc==0xe0bf and dispatch is None:
                dispatch={'state':b.mem[0x18],'substate':b.mem[0x19], 'guard':b.mem[0x1c], 'bank':b.bank}
            # RTI returns to the interrupted main-loop PC, but only after
            # instruction execution of the original NMI handler.
            if c.nmi_count>0 and c.pc==prior and c.last_opcode==0x40 and dispatch is not None and b.mem[0x1c]==0:break
            c.step()
        else:raise ReplayError(f'scripted frame {i} did not finish')
        frame_events.append({'scripted_frame':i+1,'scheduler':dispatch,'post_nmi_state':b.mem[0x18],
                             'post_nmi_substate':b.mem[0x19], 'post_nmi_bank':b.bank,
                             'cumulative_instructions':c.count})
    return {'frames':frame_events,'reached_state13':any(f['scheduler'] and f['scheduler']['state']==13 for f in frame_events),
            'frame_clock':'synthetic_user-scripted NMI / NOT authentic PPU scheduling'}

if __name__=='__main__':main()
