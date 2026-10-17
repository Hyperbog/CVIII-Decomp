#!/usr/bin/env python3
"""Experimental JP 2A03 + NTSC vblank + Mapper-24 IRQ source / IRQ-vector runner.

IRQ source semantics mirror already-tested JP/decomp/src/vrc6_irq.cpp exactly. The
instruction-boundary IRQ sampling, PPU event timing, DMA/IRQ latency and lack of
reference emulator parity are explicit approximations. No score/coverage credit.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from trace_cycle_vblank_0508 import CycleBus, CycleCPU, PULSE_MODELS, ROM_SHA
from trace_6502_vrc6_0508 import I


class Vrc6Irq:
    def __init__(self):
        self.latch=0; self.counter=0; self.cycle_mode=False
        self.enabled=False; self.enable_after_ack=False
        self.pending=False; self.prescaler=341
        self.counter_clocks=0; self.assertions=0
        self.ctrl_writes=0; self.ack_writes=0; self.latch_writes=0

    def write(self,addr:int,v:int):
        v&=255
        address=addr&0xF003
        if address==0xF000:
            self.latch=v;self.latch_writes+=1
        elif address==0xF001:
            self.ctrl_writes+=1
            self.pending=False
            self.cycle_mode=bool(v&4)
            self.enabled=bool(v&2)
            self.enable_after_ack=bool(v&1)
            self.prescaler=341
            if self.enabled:self.counter=self.latch
        elif address==0xF002:
            self.ack_writes+=1
            self.pending=False
            self.enabled=self.enable_after_ack

    def clock_counter(self):
        self.counter_clocks+=1
        if self.counter==255:
            self.counter=self.latch
            self.pending=True
            self.assertions+=1
        else:self.counter+=1

    def advance(self,cycles:int):
        if not self.enabled:return
        if self.cycle_mode:
            for _ in range(cycles):self.clock_counter()
            return
        remaining=cycles
        while remaining:
            until=(self.prescaler+2)//3
            if remaining<until:
                self.prescaler-=3*remaining
                return
            remaining-=until
            self.prescaler-=3*until
            assert self.prescaler<=0
            self.prescaler+=341
            self.clock_counter()


class IrqBus(CycleBus):
    def __init__(self,rom):
        super().__init__(rom)
        self.irq=Vrc6Irq()
        self.irq_reg_writes=[]
    def wb(self,addr,val):
        super().wb(addr,val)
        if (addr&0xF003) in (0xF000,0xF001,0xF002):
            self.irq.write(addr,val)
            if len(self.irq_reg_writes)<256:
                self.irq_reg_writes.append([self.cpu_cycles,addr&0xFFFF,val&255])
    def advance(self,cycles):
        super().advance(cycles)
        self.irq.advance(cycles)


class IrqCPU(CycleCPU):
    def __init__(self,bus):
        super().__init__(bus)
        self.irq_entries=0
        self.irq_returns=0
        self.irq_entry_log=[]
        self._interrupt_stack=[]
        self.irq_masked_steps=0
    def step(self):
        b=self.bus
        if b.nmi_pending:
            self._interrupt_stack.append('NMI')
        elif b.irq.pending and not self.flag(I):
            assert b.irq.pending
            self.interrupt(0xFFFE)
            b.advance(7)  # CPU vector/prologue timing approximate
            self.irq_entries+=1
            self._interrupt_stack.append('IRQ')
            if len(self.irq_entry_log)<128:
                self.irq_entry_log.append({
                    'entry':self.irq_entries,'cycle':b.cpu_cycles,
                    'frame':b.ppu_frames,'state6A':b.ram[0x6A],
                    'irq_counter':b.irq.counter,'irq_latch':b.irq.latch,
                    'bank_saved23':b.ram[0x23],'raw_bank':b.raw_bank,
                    'vector':self.pc,
                })
        elif b.irq.pending:self.irq_masked_steps+=1
        result=super().step()
        if result[2]=='RTI' and self._interrupt_stack:
            kind=self._interrupt_stack.pop()
            if kind=='IRQ':
                self.irq_returns+=1
                self.NMI_returns-=1  # base counts all RTI as NMI; disambiguate
        return result


def exercise(path,frames,policy,max_steps):
    rom=Path(path).read_bytes()
    assert len(rom)==393232 and hashlib.sha256(rom).hexdigest()==ROM_SHA
    b=IrqBus(rom); c=IrqCPU(b)
    controller=PULSE_MODELS[policy]
    transitions=[]; last=None
    irq_witness_states=set()
    while b.ppu_frames<frames and c.steps<max_steps:
        b.controller1_bits=controller(b.ppu_frames+1)
        c.step()
        st=(b.ram[0x18],b.ram[0x19],b.ram[0x68],b.ram[0x6A],b.ram[0x7A0],b.ram[0x7A6])
        if st != last:
            if len(transitions)<300:
                transitions.append({'frame':b.ppu_frames,'cpu_step':c.steps,'18':st[0],'19':st[1],'68':st[2],'6A':st[3],'07A0':st[4],'07A6':st[5]})
            last=st
        if c.irq_entries:
            irq_witness_states.add(st[3])
    return {
        'status':'EXPERIMENTAL_MAPPER24_IRQ_CPU_VECTOR_NOT_REFERENCE_PARITY',
        'rom_sha256':ROM_SHA,'input_policy':policy,
        'frames_target':frames,'frames_completed':b.ppu_frames,
        'cpu_steps':c.steps,'cpu_cycles':b.cpu_cycles,
        'nmi_entries':c.NMI_count,'nmi_returns':c.NMI_returns,
        'irq_entries':c.irq_entries,'irq_returns':c.irq_returns,
        'mapper_irq_assertions':b.irq.assertions,
        'mapper_irq_counter_clocks':b.irq.counter_clocks,
        'irq_masked_instruction_boundaries':c.irq_masked_steps,
        'irq_latch_writes':b.irq.latch_writes,
        'irq_control_writes':b.irq.ctrl_writes,
        'irq_ack_writes':b.irq.ack_writes,
        'irq_register_writes':b.irq_reg_writes,
        'irq_entry_log':c.irq_entry_log,
        'observed_irq_state_values':sorted(irq_witness_states),
        'observed_state_transitions':transitions,
        'end':{'pc':f'{c.pc:04X}','bank':b.raw_bank,'18':b.ram[0x18],'19':b.ram[0x19],'68':b.ram[0x68],'07A0':b.ram[0x7A0],'07A6':b.ram[0x7A6]},
        'limits':['Instruction-boundary timing only (no per-bus-cycle writes)',
                  'PPU vblank proxy, no accurate video/CHR/raster behavior',
                  'Approximate DMA and CPU interrupt-vector latency',
                  'No APU waveform/DMC scheduling; no reference NES execution trace',
                  'IRQ counter mirrors repository native source model but no independent PPU parity'],
        'new_strict_prg_bytes':0,'strict_prg_total':49404,'vpp':24,
    }

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('rom');p.add_argument('report')
    p.add_argument('--frames',type=int,default=120)
    p.add_argument('--policy',choices=sorted(PULSE_MODELS),default='start30')
    p.add_argument('--max-steps',type=int,default=3000000)
    a=p.parse_args()
    x=exercise(a.rom,a.frames,a.policy,a.max_steps)
    Path(a.report).write_text(json.dumps(x,indent=2)+'\n')
    print(f"IRQ trace {x['frames_completed']}/{x['frames_target']} frames, {x['cpu_steps']} instructions, {x['irq_entries']} IRQ, {x['nmi_entries']} NMI")
