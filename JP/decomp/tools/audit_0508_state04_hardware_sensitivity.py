#!/usr/bin/env python3
"""ROM-locked experimental state-$04 fork from a shared synthetic vblank checkpoint.

Tests controller policy and a declared hypothetical PPUSTATUS bit-6 stimulus.
Not an original-reference trace, gameplay liveness proof or byte promotion.
"""
import copy,hashlib,json,sys,types
from pathlib import Path
from trace_cycle_vblank_0508 import CycleBus,CycleCPU,ROM_SHA

def step_to_state(rom):
    b=CycleBus(rom);c=CycleCPU(b)
    while b.ppu_frames<480 and b.ram[0x18]!=4:
        b.controller1_bits=8 if (b.ppu_frames+1)%30==1 else 0
        c.step()
    assert b.ram[0x18]==4 and b.ppu_frames==421,(b.ppu_frames,c.steps,b.ram[0x18])
    return b,c

def apply_hit(bus,y):
    original=bus.rb
    def reader(self,addr):
        value=original(addr)
        if (addr&0x2007)==0x2002 and (addr&7)==2:
            scanline=self.ppu_phase//341
            if y<=scanline<261:return value|0x40
        return value
    bus.rb=types.MethodType(reader,bus)

def run(path):
    rom=Path(path).read_bytes()
    assert len(rom)==393232 and hashlib.sha256(rom).hexdigest()==ROM_SHA
    baseb,basec=step_to_state(rom)
    capture={'frame':baseb.ppu_frames,'instructions':basec.steps,
             'cpu_cycles':baseb.cpu_cycles,'NMI':basec.NMI_count,
             'PC':f'{basec.pc:04X}','RAM18':baseb.ram[0x18],
             'RAM19':baseb.ram[0x19],'RAM2C':baseb.ram[0x2C],
             'bank':baseb.raw_bank}
    result=[]
    scenarios=[('baseline_start30',None,'start30'),
               ('held_start',None,'held'),
               ('frequent_start5',None,'start5'),
               ('all_buttons',None,'all'),
               ('sprite0_bit6_scanline0',0,'start30'),
               ('sprite0_bit6_scanline80',80,'start30'),
               ('sprite0_bit6_scanline180',180,'start30')]
    for name,hit,policy in scenarios:
        b,c=copy.deepcopy((baseb,basec))
        assert c.bus is b
        if hit is not None:apply_hit(b,hit)
        transitions=[];last=(b.ram[0x18],b.ram[0x19],b.ram[0x2C]);status_reads0=b.ppu_status_reads
        fault=None
        while b.ppu_frames<480:
            f=b.ppu_frames+1
            b.controller1_bits=(8 if f%30==1 else 0) if policy=='start30' else (
                8 if policy=='held' else 8 if policy=='start5' and f%5==1 else 255 if policy=='all' else 0)
            try:
                c.step()
            except (AssertionError,KeyError) as err:
                fault={'class':type(err).__name__,'detail':str(err),
                       'pc':f'{c.pc:04X}','raw_bank':b.raw_bank,
                       'PPU_frame':b.ppu_frames,'cpu_steps':c.steps}
                break
            state=(b.ram[0x18],b.ram[0x19],b.ram[0x2C])
            if state!=last:
                if len(transitions)<40:transitions.append({'frame':b.ppu_frames,'18':state[0],'19':state[1],'2C':state[2]})
                last=state
        r={'name':name,'PPUSTATUS_bit6_heuristic_scanline':hit,'frames':b.ppu_frames,
           'additional_instructions':c.steps-basec.steps,'additional_NMI':c.NMI_count-basec.NMI_count,
           'PPUSTATUS_reads':b.ppu_status_reads-status_reads0,'fault':fault,'end18':b.ram[0x18],
           'end19':b.ram[0x19],'end2C':b.ram[0x2C],
           'ever_18_0C':any(x['18']==0x0C for x in transitions),
           'ever_18_0D':any(x['18']==0x0D for x in transitions),
           'last_transitions':transitions[-8:]}
        if hit is None:assert fault is None and b.ppu_frames==480
        result.append(r)
        print(name,r['additional_instructions'],r['end18'],r['end19'],r['end2C'],flush=True)
    return {'status':'SYNTHETIC_STATE04_SENSITIVITY_NOT_GAMEPLAY_PARITY',
            'rom_sha256':ROM_SHA,'fork_from':capture,'results':result,
            'strict_new_PRG_bytes':0,'verified_floor_PRG_bytes':49404,
            'limitations':['The checkpoint is produced under synthetic controller/PPU timing',
              'Sprite 0 hit bit6 injected as an explicit hypothetical stimulus; not modeled sprites',
              'No reference emulator traces or global nonreachability claim']}
if __name__=='__main__':
    out=run(sys.argv[1]);Path(sys.argv[2]).write_text(json.dumps(out,indent=2)+'\n')
