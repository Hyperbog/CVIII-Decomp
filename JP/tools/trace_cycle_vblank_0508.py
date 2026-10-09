#!/usr/bin/env python3
"""Experimental NES CPU instruction-cycle + PPU vblank/NMI scheduler.

Not a cycle-accurate NES emulator: no CHR/PPU rendering, no mapper IRQ,
CPU interrupt sampling delay, CPU/PPU register-cycle interleave, DMC/real DMA,
odd-frame dot skip, PPU open bus or scanline image parity.
"""
from __future__ import annotations
from trace_6502_vrc6_0508 import Bus,CPU,OPS,ROM_SHA

PULSE_MODELS={
 'none': lambda frame:0,
 'start30': lambda frame:8 if frame%30==1 else 0,
 'start10': lambda frame:8 if frame%10==1 else 0,
 'startheld':lambda frame:8,
 'abstart': lambda frame:(1,2,8,0)[(frame-1)//10%4],
}

# All official MOS 6502 instruction-cycle classes. Page-crossing and taken
# branch penalties are applied separately for the appropriate opcodes.
_READ={'inx':6,'iny':5,'zp':3,'zpx':4,'zpy':4,'abs':4,'abx':4,'aby':4,'imm':2}
_WRITE={'inx':6,'iny':6,'zp':3,'zpx':4,'zpy':4,'abs':4,'abx':5,'aby':5}
_RMW={'zp':5,'zpx':6,'abs':6,'abx':7,'acc':2}
_BR={'BCC','BCS','BEQ','BNE','BMI','BPL','BVC','BVS'}
_PAGE_READ={'ORA','AND','EOR','ADC','LDA','CMP','SBC','LDX','LDY'}

def base_cycles(m:str,mode:str)->int:
    if m in _BR:return 2
    if m in ('LDA','LDX','LDY','ORA','AND','EOR','ADC','CMP','SBC'):
        return _READ[mode]
    if m in ('STA','STX','STY'):return _WRITE[mode]
    if m in ('ASL','LSR','ROL','ROR','INC','DEC'):return _RMW[mode]
    if m in ('CPX','CPY'):return {'imm':2,'zp':3,'abs':4}[mode]
    if m=='BIT':return {'zp':3,'abs':4}[mode]
    if m=='JMP':return 3 if mode=='abs' else 5
    if m=='JSR':return 6
    if m in ('RTS','RTI'):return 6
    if m=='BRK':return 7
    if m in ('PHA','PHP'):return 3
    if m in ('PLA','PLP'):return 4
    if m in ('TAX','TAY','TXA','TYA','TSX','TXS','INX','DEX','INY','DEY',
              'CLC','SEC','CLI','SEI','CLD','SED','CLV','NOP'):return 2
    raise AssertionError((m,mode))

class CycleBus(Bus):
    # NTSC 341 dots per scanline, 262 lines. No odd-frame skip here.
    DOTS_PER_FRAME=341*262
    VBLANK_AT=341*241+1
    VBLANK_END=341*261+1
    def __init__(self,rom):
        super().__init__(rom,ppu_status=0)
        self.ppu_phase=0
        self.vblank=False
        self.nmi_line=False
        self.nmi_pending=False
        self.nmi_edges=0
        self.ppu_frames=0
        self.cpu_cycles=0
        self.dma_requested=0
        self.ppu_status_reads=0
    def set_line(self):
        level=bool(self.vblank and (self.ppu_ctrl&0x80))
        if level and not self.nmi_line:
            self.nmi_pending=True
            self.nmi_edges+=1
        self.nmi_line=level
    def rb(self,addr):
        if 0x2000<= (addr&0xFFFF)<0x4000 and (addr&7)==2:
            self.ppu_status_reads+=1
            self.ppu_latch=False
            status=(0x80 if self.vblank else 0)
            self.vblank=False
            self.set_line()
            if self.trace_reads:self.read_log.append((0x2002,status))
            return status
        return super().rb(addr)
    def wb(self,addr,val):
        super().wb(addr,val)
        if (addr&0xFFFF)==0x2000:
            self.set_line()
        if (addr&0xFFFF)==0x4014:self.dma_requested+=1
    def advance(self,cycles:int):
        self.cpu_cycles+=cycles
        dots=3*cycles
        # At most a few threshold crossings per instruction, including DMA.
        while dots>0:
            next_edge=min([x for x in (self.VBLANK_AT,self.VBLANK_END,self.DOTS_PER_FRAME) if x>self.ppu_phase])
            block=min(dots,next_edge-self.ppu_phase)
            self.ppu_phase+=block;dots-=block
            if self.ppu_phase==self.VBLANK_AT:
                self.vblank=True;self.set_line()
            elif self.ppu_phase==self.VBLANK_END:
                self.vblank=False;self.set_line()
            elif self.ppu_phase==self.DOTS_PER_FRAME:
                self.ppu_phase=0;self.ppu_frames+=1

class CycleCPU(CPU):
    def __init__(self,bus):
        super().__init__(bus,0xE00B)
        self.NMI_count=0
        self.NMI_returns=0
        self.NMI_log=[]
        self.cycle_observations={}
    def step(self):
        b=self.bus
        if b.nmi_pending:
            b.nmi_pending=False
            self.interrupt(0xFFFA)
            b.advance(7) # CPU interrupt entry bus cycles; approximation
            self.NMI_count+=1
            self.NMI_log.append({'NMI':self.NMI_count,'cpu_cycles':b.cpu_cycles,
                'ppu_frame':b.ppu_frames,'18':b.ram[0x18],'19':b.ram[0x19],
                '68':b.ram[0x68],'07A0':b.ram[0x7A0],'07A6':b.ram[0x7A6],
                'ram_F8':b.ram[0xF8],'bank':b.raw_bank})
        pc=self.pc;op=b.rb(pc)
        m,mode,size=OPS[op]
        mode={'indx':'inx','indy':'iny','absx':'abx','absy':'aby'}.get(mode,mode)
        # Only RAM/mapped PRG opcodes reached by these tests are expected.
        # Any official opcode absent from this table fails independently.
        arg=b.rb((pc+1)&65535) if size>=2 else 0
        word=(arg|(b.rb((pc+2)&65535)<<8)) if size==3 else 0
        x,y=self.x,self.y
        readpage=False
        if m in _PAGE_READ and mode in ('abx','aby','iny'):
            if mode in ('abx','aby'):
                plus=x if mode=='abx' else y
                readpage=(word&0xFF)+plus>255
            else:
                ptr=b.rzw(arg)
                readpage=(ptr&255)+y>255
        oldpc=self.pc
        super().step()
        cycles=base_cycles(m,mode)
        if m in _BR and self.pc!=((oldpc+size)&65535):
            cycles+=1
            if (self.pc&0xFF00)!=((oldpc+size)&0xFF00):cycles+=1
        if readpage:cycles+=1
        b.advance(cycles)
        if b.dma_requested:
            cnt=b.dma_requested;b.dma_requested=0
            for _ in range(cnt):b.advance(513+(b.cpu_cycles&1))
        if m=='RTI':self.NMI_returns+=1
        return self.last_instruction

def run(rom,frames:int,policy='none',limit_steps:int=2000000):
    b=CycleBus(rom);cpu=CycleCPU(b)
    cb=PULSE_MODELS[policy]
    seen_changes=[];prior=None
    # State-machine and input cadence is based on natural PPU frame number,
    # NOT on manually injected NMI number.
    while b.ppu_frames<frames and cpu.steps<limit_steps:
        b.controller1_bits=cb(b.ppu_frames+1)
        cpu.step()
        state=(b.ram[0x18],b.ram[0x19],b.ram[0x68],b.ram[0x7A0],b.ram[0x7A6])
        if state!=prior and len(seen_changes)<300:
            seen_changes.append({'frame':b.ppu_frames,'CPU_step':cpu.steps,
                                 '18':state[0],'19':state[1],'68':state[2],
                                 '07A0':state[3],'07A6':state[4]})
            prior=state
    return {
        'status':'EXPERIMENTAL_PPU_VBLANK_NMI_SCHEDULER_NOT_NES_PARITY',
        'frame_target':frames,'frame_reached':b.ppu_frames,
        'CPU_steps':cpu.steps,'CPU_cycles':b.cpu_cycles,
        'natural_NMI_entries':cpu.NMI_count,'RTI_count':cpu.NMI_returns,
        'NMI_edges':b.nmi_edges,'PPUSTATUS_reads':b.ppu_status_reads,
        'final_PC':f'{cpu.pc:04X}','final_PRG_bank':b.raw_bank,
        'initial_controller_policy':policy,
        'NMI_log':cpu.NMI_log[:100],
        'RAM_state_changes':seen_changes,
        'main_limits':['No reference PPU pixel/tile behavior','No mapper IRQ',
            'No odd-frame dot skip','CPU instruction writes modeled at instruction boundary',
            'DMA only as approximate stall','No reference-emulator verified cycle timings',
            'No official hardware/frame parity or VPP point'],
        'new_strict_PRG_bytes':0,'strict_verified_PRG_floor':49404,'VPP':24}

if __name__=='__main__':
    import argparse,json,hashlib
    from pathlib import Path
    p=argparse.ArgumentParser();p.add_argument('rom');p.add_argument('output');p.add_argument('--frames',type=int,default=60);p.add_argument('--policy',choices=sorted(PULSE_MODELS),default='start30');p.add_argument('--max-steps',type=int,default=10000000);a=p.parse_args()
    rom=Path(a.rom).read_bytes();assert len(rom)==393232 and hashlib.sha256(rom).hexdigest()==ROM_SHA
    result=run(rom,a.frames,a.policy,limit_steps=a.max_steps)
    Path(a.output).write_text(json.dumps(result,indent=2)+'\n')
    print('Experimental scheduler',result['frame_reached'],'frames',result['CPU_steps'],'instructions',result['natural_NMI_entries'],'NMI',result['final_PC'])
