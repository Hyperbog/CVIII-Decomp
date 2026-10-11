#!/usr/bin/env python3
"""Replay original JP bank0A $B7F7-$B872 CPU vs native C++ room/object loader.

Interpreter actually executes the original 6502 instruction bytes, JSR/RTS
stack frames, and mapper changes in $FB96 -> $E2D0. Native implementation is
independent and translates the same bounded semantics into portable C++.
Not frame, IRQ, PPU, APU, arbitrary selector or complete-game parity.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import sys

JP_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
BANK0A_SHA='1460df577d44e114c64fdf34a8837629765f3f6a93d45796fdf81e5ffacb5ed8'
BANK0E_SHA='9fc30168f3eca751de893aac2af31b5f4c40b8dcdcde1ad70b9614c607c29bb5'
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'SharedDecomp'))
from workflow import trace_diff, atomic_json, EvidenceError

class CPU:
    """Scoped original-opcode interpreter with VRC6 ROM bank switching."""
    def __init__(self,prg:bytes,idx:int,seed:int):
        self.prg=prg;self.bank=10;self.ram=bytearray(2048)
        self.pc=0xB7F7;self.sp=0xFD
        self.a=(seed*13)&255;self.x=(seed*5)&255;self.y=(seed*7)&255
        self.c=bool(seed&1);self.z=bool(seed&2);self.n=bool(seed&4)
        self.ram[0x7A0]=idx;self.ram[0x23]=10
        self.mapper_writes=[];self.read_0e=[];self.steps=0
        self.push(0x8F);self.push(0xFF)  # synthetic JSR caller return to $9000
    def read(self,a:int)->int:
        a &= 0xFFFF
        if a<0x2000:return self.ram[a&2047]
        if 0x8000<=a<0xC000:return self.prg[self.bank*16384+a-0x8000]
        if 0xE000<=a<=0xFFFF:return self.prg[31*8192+a-0xE000]
        raise EvidenceError(f'unmapped CPU read {a:04X}')
    def write(self,a:int,v:int)->None:
        a &= 0xFFFF;v &= 255
        if a<0x2000:self.ram[a&2047]=v;return
        if a==0x8000:
            if v not in (10,14):raise EvidenceError('unapproved mapper bank')
            self.bank=v;self.mapper_writes.append((self.pc,v));return
        raise EvidenceError(f'unexpected CPU write {a:04X} @ {self.pc:04X}')
    def push(self,v:int)->None:
        self.ram[0x100+self.sp]=v&255;self.sp=(self.sp-1)&255
    def pop(self)->int:
        self.sp=(self.sp+1)&255;return self.ram[0x100+self.sp]
    def nz(self,v:int)->None:
        self.z=(v&255)==0;self.n=bool(v&128)
    def run(self):
        while self.pc!=0x9000:
            self.steps+=1
            if self.steps>20000:raise EvidenceError(f'CPU did not return: {self.pc:04X}')
            at=self.pc;op=self.read(at)
            # Read opcode operands lazily: last-bank-window operands may not exist.
            v=self.read((at+1)&0xFFFF)
            def word():return v|(self.read((at+2)&0xFFFF)<<8)
            p=at+1
            if op==0xAD: self.a=self.read(word());self.nz(self.a);p=at+3
            elif op==0xA9:self.a=v;self.nz(self.a);p=at+2
            elif op==0xA0:self.y=v;self.nz(self.y);p=at+2
            elif op==0xA2:self.x=v;self.nz(self.x);p=at+2
            elif op==0x0A:self.c=bool(self.a&128);self.a=(self.a<<1)&255;self.nz(self.a)
            elif op==0x4A:self.c=bool(self.a&1);self.a>>=1;self.nz(self.a)
            elif op==0xA8:self.y=self.a;self.nz(self.y)
            elif op==0xB9:self.a=self.read((word()+self.y)&65535);self.nz(self.a);p=at+3
            elif op==0xB1:
                ptr=self.read(v)|(self.read((v+1)&255)<<8)
                addr=(ptr+self.y)&65535
                if self.bank!=14 or not 0x8000<=addr<0xC000:
                    raise EvidenceError('wrong mapper bank during indirect read')
                self.a=self.read(addr);self.nz(self.a)
                self.read_0e.append((at,addr,self.y,self.a));p=at+2
            elif op==0x85:self.write(v,self.a);p=at+2
            elif op==0x8D:self.write(word(),self.a);p=at+3
            elif op==0x9D:self.write((word()+self.x)&65535,self.a);p=at+3
            elif op==0x29:self.a&=v;self.nz(self.a);p=at+2
            elif op==0xC9:self.c=self.a>=v;self.nz((self.a-v)&255);p=at+2
            elif op==0xF0:
                p=at+2
                if self.z:p=(p+(v if v<128 else v-256))&65535
            elif op==0xE8:self.x=(self.x+1)&255;self.nz(self.x)
            elif op==0xC8:self.y=(self.y+1)&255;self.nz(self.y)
            elif op==0x48:self.push(self.a)
            elif op==0x68:self.a=self.pop();self.nz(self.a)
            elif op==0x20:
                target=word()
                if target not in (0xFB96,0xE2D0):raise EvidenceError(f'unexpected JSR {target:04X}')
                self.push((at+2)>>8);self.push((at+2)&255);p=target
            elif op==0x60:p=(self.pop()|(self.pop()<<8))+1
            elif op==0x4C:p=word()
            else:raise EvidenceError(f'unsupported 6502 opcode {op:02X} @ {at:04X} bank {self.bank:02X}')
            self.pc=p&65535
        if self.sp!=0xFD or self.bank!=10 or self.ram[0x23]!=10:
            raise EvidenceError('mapper/stack restoration failed')
        return self

def original_frame(cpu:CPU,index:int,seed:int,step:int)->dict:
    r=cpu.ram;n=cpu.x-1;ptr=r[8]|(r[9]<<8)
    if not 0<n<=22:raise EvidenceError('invalid original stream object count')
    reads=cpu.read_0e
    if len(reads)!=7+5*n or len(cpu.mapper_writes)!=2*len(reads):
        raise EvidenceError('original mapper read/write count mismatch')
    if not all(cpu.mapper_writes[k:k+2]==[(0xE2D2,14),(0xE2D2,10)]
               for k in range(0,len(cpu.mapper_writes),2)):
        raise EvidenceError('original $E2D0 bank switch was not restored')
    if not all(a==0xFB9B for a,_,_,_ in reads):raise EvidenceError('unexpected mapped read PC')
    return {
        'step':step,'physical_bank':'NES:JP:VRC6:raw0A','cpu_path':'B7F7-B872/FB96/E2D0',
        'room_index':index,'seed':seed,
        'header':[r[0x34],r[0x35],r[0x36],r[0x54],r[0x72],r[0x7A1],r[0x54E]],
        'pointer':ptr,'mapper':cpu.bank,'mapper_writes':len(cpu.mapper_writes),
        'mapped_reads':len(reads),'first_read':reads[0][1],'last_read':reads[-1][1],
        'mapped_accesses':[[addr,value] for _,addr,_,value in reads],
        'object_count':n,'final_x':cpu.x,'ram_10':r[0x10],'ram_53':r[0x53],
        'ram_7a0':r[0x7A0],'ram_7a6':r[0x7A6],'ram_23':r[0x23],
        'carry':bool(cpu.c),'zero':bool(cpu.z),'negative':bool(cpu.n),
        'objects':[[r[0x48C+i],r[0x400+i],r[0x438+i],r[0x41C+i],r[0x4A8+i],r[0x54E+i]]
                   for i in range(1,cpu.x)]
    }

def _jsonl(path:Path,frames:list[dict])->None:
    path.write_text(''.join(json.dumps(f,sort_keys=True,separators=(',',':'))+'\n' for f in frames),encoding='utf-8')

def compare(rom:Path,out:Path,compiler:str='g++')->dict:
    game=rom.read_bytes()
    if len(game)!=393232 or hashlib.sha256(game).hexdigest()!=JP_SHA:
        raise EvidenceError('original Japanese NES SHA256 mismatch')
    prg=game[16:16+262144]
    bank0a=prg[10*16384:11*16384]
    bank0e=prg[14*16384:15*16384]
    if hashlib.sha256(bank0a).hexdigest()!=BANK0A_SHA or hashlib.sha256(bank0e).hexdigest()!=BANK0E_SHA:
        raise EvidenceError('physical bank hash mismatch')
    frames=[]
    for i in range(5):
        for seed in range(256):frames.append(original_frame(CPU(prg,i,seed).run(),i,seed,len(frames)))
    if len(frames)!=1280:raise EvidenceError('incomplete original trace')
    out.mkdir(parents=True,exist_ok=True)
    reference=out/'original_6502_room_loader.jsonl';candidate=out/'native_cpp_room_loader.jsonl'
    _jsonl(reference,frames)
    with tempfile.TemporaryDirectory(prefix='jp-room-loader-') as t:
        tmp=Path(t);a=tmp/'raw0a.bin';e=tmp/'raw0e.bin';a.write_bytes(bank0a);e.write_bytes(bank0e)
        exe=tmp/'room_native';src=ROOT/'JP/native/room0a/room_loader_native.cpp'
        subprocess.run([compiler,'-std=c++17','-O2','-Wall','-Wextra','-Werror','-pedantic',str(src),'-o',str(exe)],check=True)
        result=subprocess.run([str(exe),str(a),str(e)],check=True,capture_output=True,text=True)
        candidate.write_text(result.stdout,encoding='utf-8')
    report=trace_diff(reference,candidate)
    report.update({'scope':'bank0A_B7F7_B872_bounded_5_room_loader_indices',
                   'cases':1280,'objects_in_five_streams':30,
                   'original_rom_sha256':JP_SHA,
                   'full_frame_ppu_apu_irq_parity':False,
                   'actual_gameplay_selector_liveness':False})
    atomic_json(out/'room0a_replay_result.json',report)
    if report['status']!='PASS':raise EvidenceError(f'first semantic divergence: {report}')
    print(json.dumps(report,sort_keys=True))
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--cxx',default='g++');a=p.parse_args()
    compare(a.rom,a.out,a.cxx)

if __name__=='__main__':
    try:main()
    except (ValueError,OSError,subprocess.CalledProcessError) as exc:
        print(f'REPLAY FAIL: {exc}',file=sys.stderr);raise SystemExit(2)
