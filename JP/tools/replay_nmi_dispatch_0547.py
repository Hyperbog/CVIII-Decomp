#!/usr/bin/env python3
"""Original fixed-bank NMI scheduler dispatch into integrated JP room initialization.

The reference CPU executes original $E35C-$E362 and $E7FB-$E813 bytes,
then the complete previously verified E526/B4CC/B7F7/foreign-script path.
$E0BF JSR $E35C exists in the original NMI handler; earlier NMI instructions
and reset-to-gameplay liveness are *not executed* by this conditional fixture.
"""
from __future__ import annotations
import argparse, hashlib, json, subprocess, tempfile
from pathlib import Path
from replay_postdispatch_0543 import PostCPU, snapshot, check_rom, JP_SHA, ROOT
from replay_room_state_0541 import StateCPU
from replay_room_loader_0540 import EvidenceError
import sys
sys.path.insert(0,str(ROOT/'SharedDecomp'))
from workflow import trace_diff,atomic_json

ENTRY=0xE35C
TARGET=0xE526
STATE=13
TABLE_BASE=0xE363

class NmiPostCPU(PostCPU):
    def __init__(self,prg:bytes,idx:int,seed:int):
        super().__init__(prg,idx,seed)
        self.ram[0x18]=STATE
        self.ram[0x1B]=(seed*19+idx*31)&255
        self.nmi_prefix_visits=[]
        self.nmi_table_target=0

    def dispatch_prefix(self,expected=TARGET):
        # Prove the entry is reachable as a static, authentic NMI JSR callsite.
        if [self.read(a) for a in (0xE0BF,0xE0C0,0xE0C1)]!=[0x20,0x5C,0xE3]:
            raise EvidenceError('authentic NMI callsite to E35C mutated')
        if [self.read(a) for a in (0xFFFA,0xFFFB)]!=[0x57,0xE0]:
            raise EvidenceError('original NMI vector mutated')
        self.pc=ENTRY
        # Stack already has the original synthetic caller return ($8FFF)
        # as required by previous bounded E526 replay. E7FB consumes the
        # inline-table JSR return, leaving the synthetic caller untouched.
        for _ in range(23):
            pc=self.pc
            if pc==expected:break
            self.nmi_prefix_visits.append(pc)
            op=self.read(pc);v=self.read((pc+1)&0xffff)
            word=lambda:v|(self.read((pc+2)&0xffff)<<8)
            nxt=pc+1
            if op==0xE6:  # INC zp
                value=(self.read(v)+1)&255;self.write(v,value);self.nz(value);nxt=pc+2
            elif op==0xA5: self.a=self.read(v);self.nz(self.a);nxt=pc+2
            elif op==0x20:
                if pc!=0xE360 or word()!=0xE7FB:raise EvidenceError('unexpected NMI JSR')
                self.push((pc+2)>>8);self.push((pc+2)&255);nxt=0xE7FB
            elif op==0x0A: self.c=bool(self.a&128);self.a=(self.a<<1)&255;self.nz(self.a)
            elif op==0x84: self.write(v,self.y);nxt=pc+2
            elif op==0xA8: self.y=self.a;self.nz(self.y)
            elif op==0xC8: self.y=(self.y+1)&255;self.nz(self.y)
            elif op==0x68: self.a=self.pop();self.nz(self.a)
            elif op==0x85: self.write(v,self.a);nxt=pc+2
            elif op==0xB1:
                pointer=self.read(v)|(self.read((v+1)&255)<<8)
                addr=(pointer+self.y)&0xffff
                if not(TABLE_BASE <= addr <= TABLE_BASE+31):
                    raise EvidenceError(f'inline NMI pointer outside 16-word table ${addr:04X}')
                self.a=self.read(addr);self.nz(self.a);nxt=pc+2
            elif op==0xA4:self.y=self.read(v);self.nz(self.y);nxt=pc+2
            elif op==0x6C:
                if pc!=0xE811 or word()!=2:raise EvidenceError('unexpected original indirect jump')
                ptr=word();nxt=self.read(ptr)|(self.read((ptr+1)&255)<<8)
                self.nmi_table_target=nxt
                if expected is not None and nxt!=expected:raise EvidenceError(f'state {self.ram[0x18]} dispatched to ${nxt:04X}, not ${expected:04X}')
            else:raise EvidenceError(f'unsupported original scheduler opcode {op:02X} at {pc:04X}')
            self.pc=nxt&0xffff
        else:raise EvidenceError('original NMI dispatch did not reach E526')
        required=(0xE35C,0xE35E,0xE360,0xE7FB,0xE7FC,0xE800,0xE806,0xE811)
        if not set(required).issubset(self.nmi_prefix_visits):
            raise EvidenceError('original dispatcher path incomplete')
        if self.sp!=0xFB or (expected is not None and self.pc!=expected):
            raise EvidenceError('original dispatcher stack/state incorrect')
        return self

    def run(self):
        self.dispatch_prefix()
        # Continue through E526, both bank0A inline dispatchers, the real
        # loader, all six original foreign scripts and return to $9000.
        return StateCPU.run(self)


def nmi_frame(cpu:NmiPostCPU,index:int,seed:int,step:int)->dict:
    frame=snapshot(cpu,index,seed,step)
    frame['nmi_dispatch']={'entry':ENTRY,'state_index':STATE,'target':cpu.nmi_table_target,
                           'tick_1b':cpu.ram[0x1B],
                           'callsite':0xE0BF, 'conditional':True,
                           'original_instruction_starts':cpu.nmi_prefix_visits}
    return frame


def compare(rom:Path,out:Path,compiler='g++',limit=1280):
    if not 0<limit<=1280:raise ValueError('cases must be in [1,1280]')
    prg=check_rom(rom);out.mkdir(parents=True,exist_ok=True)
    cases=[]
    for index in range(5):
        for seed in range(256):
            if len(cases)==limit:break
            cpu=NmiPostCPU(prg,index,seed).complete()
            cases.append(nmi_frame(cpu,index,seed,len(cases)))
        if len(cases)==limit:break
    original=out/'original_nmi_dispatch_6502.jsonl';native=out/'native_nmi_dispatch_cpp.jsonl'
    original.write_text(''.join(json.dumps(c,sort_keys=True,separators=(',',':'))+'\n' for c in cases),encoding='utf-8')
    with tempfile.TemporaryDirectory(prefix='jp0547-') as d:
        tmp=Path(d)
        for name,data in [('a',prg[10*16384:11*16384]),('e',prg[14*16384:15*16384]),('zero',prg[:16384]),('full',prg)]:
            (tmp/name).write_bytes(data)
        exe=tmp/'native';source=ROOT/'JP/native/room0a/room_loader_native.cpp'
        subprocess.run([compiler,'-std=c++17','-O2','-Wall','-Wextra','-Werror','-pedantic',str(source),'-o',str(exe)],check=True)
        p=subprocess.run([str(exe),str(tmp/'a'),str(tmp/'e'),'--post-dispatch',str(tmp/'zero'),str(tmp/'full'),'--nmi-stage'],capture_output=True,text=True,check=True)
        native.write_text(''.join(p.stdout.splitlines(keepends=True)[:limit]),encoding='utf-8')
    report=trace_diff(original,native)
    report.update({'scope':'conditional_fixed_NMI_E0BF_callsite_E35C_to_E526_then_all_six_room_scripts',
                   'cases':limit,'original_rom_sha256':JP_SHA,
                   'complete_NMI_handler_executed':False,'reset_to_gameplay_reachability':False,
                   'PPU_APU_frame_parity':False})
    atomic_json(out/'nmi_dispatch_0547_report.json',report)
    if report.get('status')!='PASS':raise EvidenceError(json.dumps(report))
    print(json.dumps(report,sort_keys=True))
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--cxx',default='g++')
    p.add_argument('--cases',type=int,default=1280)
    a=p.parse_args();compare(a.rom,a.out,a.cxx,a.cases)
