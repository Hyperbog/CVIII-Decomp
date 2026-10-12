#!/usr/bin/env python3
"""Original JP bank-$0A post-loader *contract* replay against translated C++.

The six original B49A/FBBB calls traverse the actual 6502 trampoline, mapped
bank zero, real fixed-bank return shim, then B6E7->B597 return. The called
routines for IDs 0,2,3,4 are **deliberate zero-effect RTS stubs**, not claims
of reproduced behavior. IDs 1 and 6 execute their *original* 6502 bytes.
This isolates and tests the caller's complete state/mapping control flow.
"""
from __future__ import annotations
import argparse, hashlib, json, subprocess, tempfile
from pathlib import Path
from replay_room_state_0541 import StateCPU, ROOT, JP_SHA, BANK0A_SHA, BANK0E_SHA
from replay_room_loader_0540 import EvidenceError
import sys
sys.path.insert(0,str(ROOT/'SharedDecomp'))
from workflow import trace_diff, atomic_json

TARGET_IDS=(0,1,2,6,3,4)
TABLE={0:(0x84A0,0),1:(0x8001,0),2:(0x8013,0),3:(0xD03C,0),4:(0xD0CD,0),5:(0xCDA8,0),6:(0x8F3E,0),7:(0xFBA5,0),8:(0xFBB0,0)}
LEAVES_PROVEN=(1,6)

class PostCPU(StateCPU):
    def __init__(self,prg:bytes,index:int,seed:int):
        super().__init__(prg,index,seed)
        self.post_events=[];self.post_writes=[];self.post_visits=[]
        self.post_calls=[]
    def read(self,addr:int)->int:
        addr&=0xFFFF
        if 0xC000<=addr<0xE000:
            return self.prg[30*8192+addr-0xC000]
        return super().read(addr)
    def write(self,addr:int,val:int):
        addr&=0xffff;val&=255
        if addr==0x8000:
            if val not in (0,10,14):raise EvidenceError('post-dispatch illegal mapper bank')
            self.bank=val;self.mapper_writes.append((self.pc,val))
            self.post_writes.append([self.pc,val]);return
        return super().write(addr,val)
    def complete(self):
        self.run()  # independently execute all actual pre-loader original opcodes
        if self.pc!=0xB6B4 or self.bank!=10 or self.sp!=0xF9:
            raise EvidenceError('post-loader prefix did not reach proven boundary')
        self.post_writes=[]  # exclude the preceding authenticated E526 and 0E reads
        local_steps=0
        while self.pc!=0x9000:
            local_steps+=1
            if local_steps>800:raise EvidenceError(f'postloader did not return: {self.bank:02X}:{self.pc:04X}')
            pc=self.pc;self.post_visits.append(pc)
            if pc in (0x84A0,0x8013,0xD03C,0xD0CD):
                call_id=self.ram[0]
                if (call_id not in TABLE or TABLE[call_id][0]!=pc or self.bank!=0
                    or call_id in LEAVES_PROVEN):
                    raise EvidenceError('unapproved opaque foreign-call boundary')
                self.post_events.append({'id':call_id,'target':pc,'mapped_bank':self.bank,
                                         'target_region':'PRG30' if pc>=0xC000 else 'raw00',
                                         'ram16':self.ram[0x16], 'ram17':self.ram[0x17],
                                         'ram23':self.ram[0x23], 'ram3f_at_entry':self.ram[0x3f], 'stack_pointer':self.sp,
                                         'stubbed':True})
                # Script's actual behavior is **not simulated**: return the
                # neutral test callback via original 6502 RTS stack semantics.
                self.pc=((self.pop()|(self.pop()<<8))+1)&0xffff
                continue
            if pc in (0x8001,0x8F3E):
                call_id=self.ram[0]
                if TABLE.get(call_id,(None,None))[0]!=pc or self.bank!=0:
                    raise EvidenceError('wrong bank at executable leaf')
                self.post_events.append({'id':call_id,'target':pc,'mapped_bank':self.bank,
                                         'target_region':'raw00','ram16':self.ram[0x16],
                                         'ram17':self.ram[0x17], 'ram23':self.ram[0x23],
                                         'ram3f_at_entry':self.ram[0x3f], 'stack_pointer':self.sp,'stubbed':False})
            op=self.read(pc);v=self.read((pc+1)&0xffff)
            def word():return v|(self.read((pc+2)&0xffff)<<8)
            p=pc+1
            if op==0xA9:self.a=v;self.nz(self.a);p=pc+2
            elif op==0xA5:self.a=self.read(v);self.nz(self.a);p=pc+2
            elif op==0xAC:self.y=self.read(word());self.nz(self.y);p=pc+3
            elif op==0xAD:self.a=self.read(word());self.nz(self.a);p=pc+3
            elif op==0xB9:self.a=self.read((word()+self.y)&0xffff);self.nz(self.a);p=pc+3
            elif op==0x85:self.write(v,self.a);p=pc+2
            elif op==0x8D:self.write(word(),self.a);p=pc+3
            elif op==0xE6:
                t=(self.read(v)+1)&255;self.write(v,t);self.nz(t);p=pc+2
            elif op==0x0A:self.c=bool(self.a&128);self.a=(self.a<<1)&255;self.nz(self.a)
            elif op==0x18:self.c=False
            elif op==0x65:
                w=self.a+self.read(v)+int(self.c);self.a=w&255;self.c=w>255;self.nz(self.a);p=pc+2
            elif op==0x69:
                w=self.a+v+int(self.c);self.a=w&255;self.c=w>255;self.nz(self.a);p=pc+2
            elif op==0xA8:self.y=self.a;self.nz(self.y)
            elif op==0x48:self.push(self.a)
            elif op==0x68:self.a=self.pop();self.nz(self.a)
            elif op==0x20:
                target=word()
                if target not in (0xB49A,0xB4EE,0xE2D0):
                    raise EvidenceError(f'unexpected JSR {target:04X} from {pc:04X}')
                self.push((pc+2)>>8);self.push((pc+2)&255);p=target
            elif op==0x60:p=(self.pop()|(self.pop()<<8))+1
            elif op==0x4C:p=word()
            elif op==0x6C:
                ptr=word();p=self.read(ptr)|(self.read((ptr&0xff00)|((ptr+1)&255))<<8)
                if pc!=0xFBC6 or p not in [t for t,_ in TABLE.values()]:
                    raise EvidenceError('FBBB dispatch target unrecognized')
            elif op==0xC9:self.c=self.a>=v;self.nz((self.a-v)&255);p=pc+2
            elif op==0xD0:
                p=pc+2
                if not self.z:p=(p+(v if v<128 else v-256))&0xffff
            else:raise EvidenceError(f'unsupported original post-dispatch {op:02X}@{pc:04X} bank{self.bank:02X}')
            self.pc=p&0xffff
        if [e['id'] for e in self.post_events]!=list(TARGET_IDS):
            raise EvidenceError('wrong original six-script order')
        if self.sp!=0xFD or self.bank!=10 or self.ram[0x23]!=10:
            raise EvidenceError('post-loader mapper/stack restoration failed')
        if self.ram[0x68]!=1 or self.ram[0x19]!=2 or self.ram[0x7A6]!=9:
            raise EvidenceError('wrong terminal state')
        expected_sites=(0xB6B4,0xB49A,0xFBBB,0xFBC6,0xFBC9,0xE2D0,0xB4EE,0xB6E5,0xB6E7,0xB59A,0xB5A2)
        if not set(expected_sites).issubset(self.post_visits):
            raise EvidenceError('missing authentic original CPU transition sites')
        if self.post_writes!=[[0xE2D2,val] for val in (0,10)*6]:
            raise EvidenceError('original trampoline mapper not restored six times')
        return self

def snapshot(cpu:PostCPU,idx:int,seed:int,step:int)->dict:
    r=cpu.ram
    return {'step':step,'room_index':idx,'seed':seed,
            'scope':'conditional_6502_post_B6B4_native_host_with_four_stub_callbacks',
            'callbacks':cpu.post_events,'mapper_changes':cpu.post_writes,
            'ram_00':r[0],'ram_16':r[0x16],'ram_17':r[0x17],
            'ram_23':r[0x23],'ram_ff':r[0xff],'ram_fc':r[0xfc],'ram_fd':r[0xfd],
            'ram_3f':r[0x3f],'ram_3c':r[0x3c],
            'ram_38':r[0x38],'ram_39':r[0x39],
            'ram_57':r[0x57],'ram_61':r[0x61], 'state_19':r[0x19],
            'substate_68':r[0x68],'stream_state_7a6':r[0x7a6],
            'mapper':cpu.bank,'pc_after_state':cpu.pc,'sp_after_state':cpu.sp,
            'a':cpu.a,'x':cpu.x,'y':cpu.y,
            'carry':bool(cpu.c),'zero':bool(cpu.z),'negative':bool(cpu.n)}

def check_rom(rom:Path):
    data=rom.read_bytes()
    if len(data)!=393232 or hashlib.sha256(data).hexdigest()!=JP_SHA:
        raise EvidenceError('original JP ROM SHA mismatch')
    prg=data[16:16+262144]
    if (hashlib.sha256(prg[10*16384:11*16384]).hexdigest()!=BANK0A_SHA
        or hashlib.sha256(prg[14*16384:15*16384]).hexdigest()!=BANK0E_SHA):
        raise EvidenceError('wrong PRG bank identity')
    return prg

def compare(rom:Path,out:Path,compiler:str='g++',case_limit:int=1280):
    prg=check_rom(rom);out.mkdir(parents=True,exist_ok=True)
    original=[]
    for idx in range(5):
        for seed in range(256):
            if len(original)>=case_limit:break
            cpu=PostCPU(prg,idx,seed).complete()
            original.append(snapshot(cpu,idx,seed,len(original)))
        if len(original)>=case_limit:break
    ref=out/'original_postdispatch_6502.jsonl';native=out/'native_postdispatch_cpp.jsonl'
    ref.write_text(''.join(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n' for x in original))
    with tempfile.TemporaryDirectory(prefix='jp0543-') as t:
        tmp=Path(t);a=tmp/'a';b=tmp/'b';c=tmp/'c';a.write_bytes(prg[10*16384:11*16384]);b.write_bytes(prg[14*16384:15*16384]);c.write_bytes(prg[:16384]);exe=tmp/'host'
        source=ROOT/'JP/native/room0a/room_loader_native.cpp'
        subprocess.run([compiler,'-std=c++17','-O2','-Wall','-Wextra','-Werror','-pedantic',str(source),'-o',str(exe)],check=True)
        result=subprocess.run([str(exe),str(a),str(b),'--post-dispatch',str(c)],capture_output=True,text=True,check=True)
        native.write_text(result.stdout)
    report=trace_diff(ref,native)
    report.update({'scope':'B6B4_to_B5A2_six_original_mapper_trampolines',
                   'cases':len(original),'real_original_script_bodies':[1,6],
                   'opaque_mocked_script_bodies':[0,2,3,4],
                   'real_gameplay_liveness':False,'whole_subsystem_parity':False,
                   'original_rom_sha256':JP_SHA})
    atomic_json(out/'postdispatch_0543_report.json',report)
    if report['status']!='PASS':raise EvidenceError(json.dumps(report))
    print(json.dumps(report,sort_keys=True))
    return report

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--rom',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--cxx',default='g++')
    ap.add_argument('--cases',type=int,default=1280)
    args=ap.parse_args();compare(args.rom,args.out,args.cxx,args.cases)
