#!/usr/bin/env python3
"""Independent Nintendulator nestest golden CPU trace check (no commercial ROM).

Assets fetched from a PINNED public test-ROM repository, never stored in game repo.
Official-opcode/NROM CPU check, not NES VRC6/PPU/IRQ/gameplay parity.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from trace_6502_vrc6_0508 import CPU, OPS
from trace_cycle_vblank_0508 import base_cycles, _BR, _PAGE_READ
from nes_trace_compare import parse_nestest

PINNED_UPSTREAM_COMMIT = '95d8f621ae55cee0d09b91519a8989ae0e64753b'
FIELDS = ('pc', 'a', 'x', 'y', 'p', 'sp', 'cycles')

class NromBus:
    def __init__(self, image: bytes):
        assert image[:4] == b'NES\x1a' and len(image) >=16
        assert image[6] & 4 == 0 and image[6] >> 4 == 0 and image[7] & 0xF0 == 0, 'mapper/trainer must be NROM'
        banks=image[4]
        assert banks in (1,2),'NROM must have 1/2 16-KiB PRG banks'
        size=banks*16384
        assert len(image) >= 16+size
        self.prg=image[16:16+size]
        self.ram=bytearray(2048)
        self.sram=bytearray(8192)
        self.io={}
        self.raw_bank=0
        self.cpu_cycles=7
    def rb(self, addr:int)->int:
        addr&=0xffff
        if addr<0x2000:return self.ram[addr&0x7ff]
        if addr<0x4000:return self.io.get(0x2000+(addr&7),0)
        if addr<0x6000:return self.io.get(addr,0)
        if addr<0x8000:return self.sram[addr-0x6000]
        return self.prg[(addr-0x8000) % len(self.prg)]
    def wb(self,addr:int,val:int):
        addr&=0xffff;val&=255
        if addr<0x2000:self.ram[addr&0x7ff]=val
        elif addr<0x4000:self.io[0x2000+(addr&7)]=val
        elif addr<0x6000:self.io[addr]=val
        elif addr<0x8000:self.sram[addr-0x6000]=val
    def rw(self,addr:int)->int:return self.rb(addr)|(self.rb((addr+1)&65535)<<8)
    def rzw(self,addr:int)->int:return self.rb(addr&255)|(self.rb((addr+1)&255)<<8)

class NromCPU(CPU):
    def __init__(self,bus):super().__init__(bus,pc=0xC000)
    def step(self):
        b=self.bus;pc=self.pc
        op=b.rb(pc)
        if op not in OPS:raise ValueError(f'unsupported opcode {op:02X} at {pc:04X}')
        m,mode,size=OPS[op]
        mode={'indx':'inx','indy':'iny','absx':'abx','absy':'aby'}.get(mode,mode)
        arg=b.rb((pc+1)&65535) if size>=2 else 0
        word=arg|(b.rb((pc+2)&65535)<<8) if size==3 else 0
        crossing=False
        if m in _PAGE_READ and mode in ('abx','aby','iny'):
            if mode in ('abx','aby'):
                crossing=(word&255)+(self.x if mode=='abx' else self.y)>255
            else:
                crossing=(b.rzw(arg)&255)+self.y>255
        super().step()
        cycles=base_cycles(m,mode)
        if m in _BR and self.pc!=((pc+size)&65535):
            cycles+=1
            if (self.pc&0xff00)!=((pc+size)&0xff00):cycles+=1
        if crossing:cycles+=1
        b.cpu_cycles+=cycles

def run(rom_path:str, log_path:str, *, cap:int=10000, max_differences:int=12)->dict:
    image=Path(rom_path).read_bytes()
    original=Path(log_path).read_bytes()
    image_hash=hashlib.sha256(image).hexdigest()
    log_hash=hashlib.sha256(original).hexdigest()
    bus=NromBus(image);cpu=NromCPU(bus)
    matching=0;total=0;disagreements=[]
    for row in original.decode('utf-8').splitlines():
        if not row.strip():continue
        if total>=cap:break
        expected=parse_nestest(row)
        actual={'pc':cpu.pc,'a':cpu.a,'x':cpu.x,'y':cpu.y,'p':cpu.p,'sp':cpu.sp,'cycles':bus.cpu_cycles}
        bad=[name for name in FIELDS if actual[name] != expected[name]]
        total+=1
        if bad:
            if len(disagreements)<max_differences:
                disagreements.append({'instruction_index_1based':total,'fields':bad,
                    'expected':{name:expected[name] for name in bad},
                    'actual':{name:actual[name] for name in bad},
                    'opcode_at_pc':f'{bus.rb(cpu.pc):02X}'})
            break
        matching+=1
        try:cpu.step()
        except (AssertionError,ValueError) as exc:
            disagreements.append({'instruction_index_1based':total,'error':str(exc), 'next_pc':f'{cpu.pc:04X}'})
            break
    return {'status':'INDEPENDENT_NESTEST_CPU_TRACE_NOT_VRC6_GAMEPLAY_PARITY',
        'upstream_repo_commit':PINNED_UPSTREAM_COMMIT,
        'test_rom_sha256':image_hash,'golden_log_sha256':log_hash,
        'NROM_format_checked':True,'golden_instructions':len([x for x in original.splitlines() if x.strip()]),
        'instruction_states_compared':total,'matching_instruction_states':matching,
        'all_compared_states_match':not disagreements and matching==total,
        'differences':disagreements,
        'reference_fields':FIELDS,'rom_image_exported':False,
        'reference_source':'Kevin Horton nestest.nes / Nintendulator nestest.log, retrieved from christopherpow/nes-test-roms pinned commit',
        'limitations':['NROM CPU only; no VRC6 or MMC5 mapping','No PPU/IRQ raster timing or Castlevania III input/playthrough proof',
            'Unimplemented official/unofficial opcode if execution reaches one is a failure, not a pass'],
        'new_strict_game_PRG_bytes':0,'project_vpp':25}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('test_rom');p.add_argument('golden_log');p.add_argument('--out');p.add_argument('--max-instructions',type=int,default=10000)
    a=p.parse_args();r=run(a.test_rom,a.golden_log,cap=a.max_instructions)
    if a.out:Path(a.out).write_text(json.dumps(r,indent=2)+'\n')
    print(f"NESTEST external reference: {r['matching_instruction_states']}/{r['golden_instructions']} matched states")
    if r['differences']:print(json.dumps(r['differences'],indent=2))
    raise SystemExit(0 if r['all_compared_states_match'] and r['matching_instruction_states']==r['golden_instructions'] else 1)
