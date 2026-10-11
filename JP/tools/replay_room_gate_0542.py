#!/usr/bin/env python3
"""JP raw0A room descriptor gate: original E526/inline dispatch/B873 versus C++.

Exercise all nine *structurally* valid non-sentinel descriptor indices and all
256 initial register/flag seeds. This local conditional execution is not a
claim that a real game frame visits every descriptor or that global selectors
are bounded. This executor runs authentic CPU bytes, including E843/E86B/EC70.
"""
from __future__ import annotations
import argparse, hashlib, json, subprocess, tempfile, sys
from pathlib import Path
from replay_room_state_0541 import StateCPU, JP_SHA, BANK0A_SHA, BANK0E_SHA, ROOT
from replay_room_loader_0540 import CPU
sys.path.insert(0,str(ROOT/'SharedDecomp'))
from workflow import trace_diff, atomic_json, EvidenceError

PATH='E526/B4CC/E7FB/B597/B689/B6A4/B873/E843/E86B/EC70/B6AD/B5A2'
BUFFER_START=0x300
BUFFER_END=0x380

class GateCPU(StateCPU):
    def __init__(self,prg:bytes,index:int,seed:int):
        super().__init__(prg,0,seed)
        if not (0<=index<9):raise EvidenceError('non-sentinel descriptor range must be 0..8')
        self.gate_index=index
        self.ram[0x7A6]=index
        self.ram[0x1E]=seed&31
        for j in range(BUFFER_START,BUFFER_END):
            self.ram[j]=(seed*13+j*7)&255
        self.pc=0xE526
        self.state_visits=[]
        self.mapper_writes=[]
        self.read_0e=[]
        self.steps=0

    def run(self):
        while self.pc!=0x9000:
            self.steps+=1
            if self.steps>10000:raise EvidenceError('non-sentinel gate failed to return')
            pc=self.pc;self.state_visits.append(pc)
            op=self.read(pc);v=self.read((pc+1)&65535)
            def word():return v|(self.read((pc+2)&65535)<<8)
            dest=pc+1
            if op==0xAD:self.a=self.read(word());self.nz(self.a);dest=pc+3
            elif op==0xA9:self.a=v;self.nz(self.a);dest=pc+2
            elif op==0xA5:self.a=self.read(v);self.nz(self.a);dest=pc+2
            elif op==0xA4:self.y=self.read(v);self.nz(self.y);dest=pc+2
            elif op==0xA6:self.x=self.read(v);self.nz(self.x);dest=pc+2
            elif op==0x0A:self.c=bool(self.a&128);self.a=(self.a<<1)&255;self.nz(self.a)
            elif op==0xA8:self.y=self.a;self.nz(self.y)
            elif op==0x85:self.write(v,self.a);dest=pc+2
            elif op==0x84:self.write(v,self.y);dest=pc+2
            elif op==0x86:self.write(v,self.x);dest=pc+2
            elif op==0x8D:self.write(word(),self.a);dest=pc+3
            elif op==0x9D:self.write((word()+self.x)&65535,self.a);dest=pc+3
            elif op==0xB9:self.a=self.read((word()+self.y)&65535);self.nz(self.a);dest=pc+3
            elif op==0xB1:
                ptr=self.read(v)|(self.read((v+1)&255)<<8)
                addr=(ptr+self.y)&65535
                if self.bank!=10 or not (0xB4D1<=addr<0xB6A4):
                    raise EvidenceError(f'non-sentinel indirect read unproven mapping {self.bank}:{addr:04X}')
                self.a=self.read(addr);self.nz(self.a);dest=pc+2
            elif op==0xC9:self.c=self.a>=v;self.nz((self.a-v)&255);dest=pc+2
            elif op==0xE0:self.c=self.x>=v;self.nz((self.x-v)&255);dest=pc+2
            elif op==0x29:self.a&=v;self.nz(self.a);dest=pc+2
            elif op==0xF0:
                dest=pc+2
                if self.z:dest=(dest+(v if v<128 else v-256))&65535
            elif op==0xD0:
                dest=pc+2
                if not self.z:dest=(dest+(v if v<128 else v-256))&65535
            elif op==0x90:
                dest=pc+2
                if not self.c:dest=(dest+(v if v<128 else v-256))&65535
            elif op==0xB0:
                dest=pc+2
                if self.c:dest=(dest+(v if v<128 else v-256))&65535
            elif op==0x18:self.c=False
            elif op==0x38:self.c=True
            elif op==0x6D:
                summ=self.a+self.read(word())+int(self.c)
                self.c=summ>255;self.a=summ&255;self.nz(self.a);dest=pc+3
            elif op==0xE8:self.x=(self.x+1)&255;self.nz(self.x)
            elif op==0xC8:self.y=(self.y+1)&255;self.nz(self.y)
            elif op==0xEE:
                target=word();res=(self.read(target)+1)&255;self.write(target,res);self.nz(res);dest=pc+3
            elif op==0xC6:
                res=(self.read(v)-1)&255;self.write(v,res);self.nz(res);dest=pc+2
            elif op==0x48:self.push(self.a)
            elif op==0x68:self.a=self.pop();self.nz(self.a)
            elif op==0x20:
                target=word()
                if target not in (0xE2D0,0xE7FB,0xB689,0xB873,0xE843,0xE86B):
                    raise EvidenceError(f'unknown 0542 original call {target:04X} at {pc:04X}')
                self.push((pc+2)>>8);self.push((pc+2)&255);dest=target
            elif op==0x60:dest=(self.pop()|(self.pop()<<8))+1
            elif op==0x4C:dest=word()
            elif op==0x6C:
                ptr=word()
                dest=self.read(ptr)|(self.read((ptr&0xff00)|((ptr+1)&255))<<8)
                if pc!=0xE811 or dest not in (0xB597,0xB6A4):
                    raise EvidenceError(f'invalid inline indirect jump {pc:04X}->{dest:04X}')
            else:raise EvidenceError(f'unknown original opcode {op:02X}@{pc:04X} bank{self.bank:02X}')
            self.pc=dest&65535
        must={0xE526,0xB4CC,0xE7FB,0xB597,0xB689,0xB6A4,0xB873,
              0xB883,0xE843,0xE857,0xB894,0xB89C,0xE86B,0xEC70,
              0xB89F,0xB6AD,0xB5A2}
        absent=must-set(self.state_visits)
        if absent:raise EvidenceError('gate missing original CPU locations '+repr(sorted(absent)))
        if any(x in self.state_visits for x in (0xE785,0xB7F7,0xFB96,0xB6B4)):
            raise EvidenceError('normal gate unexpectedly loaded room objects')
        if self.bank!=10 or self.sp!=0xFD or self.ram[0x23]!=10:
            raise EvidenceError('mapper/stack restoration failed')
        if self.mapper_writes!=[(0xE2D2,10)] or self.read_0e:
            raise EvidenceError('non-sentinel branch unexpectedly switched banks')
        if (self.ram[0x19],self.ram[0x68],self.ram[0x7A6])!=(2,0,self.gate_index+1):
            raise EvidenceError('gate state mutation mismatch')
        if self.ram[0x300+self.ram[0x1e]-1]!=0xFF:
            raise EvidenceError('original descriptor sentinel not appended')
        return self


def snapshot(c:GateCPU,index:int,seed:int,step:int):
    r=c.ram
    return {'step':step,'physical_bank':'NES:JP:VRC6:raw0A','cpu_path':PATH,
            'descriptor_index':index,'seed':seed,'state_19':r[0x19],
            'substate_68':r[0x68],'stream_state_7a6':r[0x7A6],
            'ram_1d':r[0x1d],'ram_1e':r[0x1e],'ram_5e':r[0x5e],
            'ram_5f':r[0x5f],'ram_10':r[0x10],
            'pc_after_gate':c.pc,'sp_after_gate':c.sp,
            'mapper':c.bank,'mapper_writes':len(c.mapper_writes),
            'mapped_reads':len(c.read_0e),
            'x':c.x,'y':c.y,'carry':bool(c.c),'zero':bool(c.z),'negative':bool(c.n),
            'buffer_0300_037f':list(r[BUFFER_START:BUFFER_END])}

def validate_authentic(rom:Path):
    game=rom.read_bytes()
    if len(game)!=393232 or hashlib.sha256(game).hexdigest()!=JP_SHA:
        raise EvidenceError('original JP iNES identity mismatch')
    prg=game[16:16+262144]
    if (hashlib.sha256(prg[10*16384:11*16384]).hexdigest()!=BANK0A_SHA or
        hashlib.sha256(prg[14*16384:15*16384]).hexdigest()!=BANK0E_SHA):
        raise EvidenceError('raw physical bank identity mismatch')
    return prg

def compare(rom:Path,out:Path,compiler='g++'):
    prg=validate_authentic(rom)
    out.mkdir(parents=True,exist_ok=True)
    ref=[]
    for i in range(9):
        for seed in range(256):
            c=GateCPU(prg,i,seed).run()
            ref.append(snapshot(c,i,seed,len(ref)))
    p_ref=out/'original_6502_room_gate.jsonl'
    p_host=out/'native_cpp_room_gate.jsonl'
    p_ref.write_text(''.join(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n' for x in ref),encoding='utf-8')
    with tempfile.TemporaryDirectory(prefix='jp-0542-gate-') as t:
        tmp=Path(t);a=tmp/'raw0a.bin';e=tmp/'raw0e.bin'
        a.write_bytes(prg[10*16384:11*16384]);e.write_bytes(prg[14*16384:15*16384])
        exe=tmp/'gate-native';src=ROOT/'JP/native/room0a/room_loader_native.cpp'
        subprocess.run([compiler,'-std=c++17','-O2','-Wall','-Wextra','-Werror','-pedantic',str(src),'-o',str(exe)],check=True)
        run=subprocess.run([str(exe),str(a),str(e),'--state-gate'],check=True,capture_output=True,text=True)
        p_host.write_text(run.stdout,encoding='utf-8')
    report=trace_diff(p_ref,p_host)
    report.update({'scope':'E526_to_state2_B5A2_nine_non_sentinel_descriptor_paths',
                   'cases':len(ref),'descriptor_domain':'structural_indices_0_to_8_only',
                   'actual_gameplay_reachability':False,'frame_ppu_apu_irq_parity':False,
                   'original_rom_sha256':JP_SHA})
    atomic_json(out/'room_gate_0542_report.json',report)
    if report['status']!='PASS':raise EvidenceError('room gate parity divergence: '+json.dumps(report))
    print(json.dumps(report,sort_keys=True))
    return report

def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--cxx',default='g++')
    a=p.parse_args();compare(a.rom,a.out,a.cxx)
if __name__=='__main__':main()
