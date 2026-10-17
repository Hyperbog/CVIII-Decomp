#!/usr/bin/env python3
"""Original JP bank0A:B7F7-B872 room resource loader vs native C11.

Runs ORIGINAL 6502 opcodes from the authenticated JP retail cartridge,
including 5 original raw0E record streams, fixed31:FB96/E2D0 bank switches,
and source-backed 2 KiB RAM/register/mapper-event state comparison.
Owner ROM is never emitted or checked in. Conditional entry != natural Mesen trace.
"""
from __future__ import annotations
import argparse, ctypes, hashlib, json
from pathlib import Path
ROM_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
BANK0A_SHA='1460df577d44e114c64fdf34a8837629765f3f6a93d45796fdf81e5ffacb5ed8'
BANK0E_SHA='9fc30168f3eca751de893aac2af31b5f4c40b8dcdcde1ad70b9614c607c29bb5'
STREAM_SPAN_SHA='977745b341cfa56056be96e454d2e49e5d91084b798e82b1a1e819dcfcdab479'
EXPECTED_ROOTS=(0xBEA4,0xBEDB,0xBF03,0xBE8B,0xBF1C)
EXPECTED_COUNTS=(10,7,4,4,5)
CPU_START=0xB7F7; CPU_END=0xB873

def sha(v):return hashlib.sha256(v).hexdigest()
def check(cond,msg):
    if not cond:raise ValueError(msg)

def authentic(rom):
    check(len(rom)==393232 and sha(rom)==ROM_SHA and rom[:4]==b'NES\x1a'
        and (rom[6]>>4|(rom[7]&0xf0))==24,'wrong authentic original Japanese VRC6 ROM')
    prg=rom[16:16+262144]
    source=prg[10*16384:11*16384]
    stream=prg[14*16384:15*16384]
    fixed=prg[31*8192:32*8192]
    check(sha(source)==BANK0A_SHA and sha(stream)==BANK0E_SHA,'original raw0A/raw0E physical bank changed')
    check(sha(stream[0xBE8B-0x8000:0xBF3A-0x8000])==STREAM_SPAN_SHA,'original 175-byte source stream window changed')
    roots=tuple(source[0x38c2+2*i]|source[0x38c3+2*i]<<8 for i in range(5))
    check(roots==EXPECTED_ROOTS,'physical raw0A record-root table changed')
    check(fixed[0x1B96:0x1BA5]==bytes.fromhex('a9 0e 20 d0 e2 b1 08 48 a9 0a 20 d0 e2 68 60'),'fixed original bank-qualified reader changed')
    check(fixed[0x02d0:0x02d6]==bytes.fromhex('85 23 8d 00 80 60'),'fixed bank-mapper helper changed')
    # Independent restricted, physical code window fingerprint, not embedded source data.
    check(sha(source[0x37f7:0x3873])==LOADER_SHA,'original bank0A loader code changed')
    for i,root in enumerate(roots):
        o=root-0x8000
        stop=o+4+5*EXPECTED_COUNTS[i]
        check(stop<0x4000 and stream[stop]==0xff,'original room record terminator outside source bound')
        check(0xff not in stream[o+4:stop:5], 'original room count changed')
    return prg,source,stream,fixed

# Exact ROM SHA computed by owner-local utility, not an assumption.
LOADER_SHA='068cd9f225e38a3b2f0b6e19717bfa11b73a68b9419854d684c42cf55d66d15d'

class CPU:
    def __init__(self,prg,ram,overflow):
        self.prg=prg;self.ram=bytearray(ram)
        self.a=0;self.x=0;self.y=0;self.c=0;self.z=0;self.n=0;self.v=overflow
        self.pc=CPU_START;self.sp=0xfd;self.steps=0;self.bank=10
        self.mapper=[];self.stream_reads=[];self.script_calls=0
        self.push(0x8f);self.push(0xff)
    def push(self,v):
        self.ram[0x100+self.sp]=v&255;self.sp=(self.sp-1)&255
    def pop(self):
        self.sp=(self.sp+1)&255;return self.ram[0x100+self.sp]
    def flags(self,v):
        self.z=int((v&255)==0);self.n=int(bool(v&128))
    def read(self,addr):
        addr &=0xffff
        if addr<0x2000:return self.ram[addr&2047]
        if 0x8000<=addr<0xc000:return self.prg[self.bank*16384+addr-0x8000]
        if addr>=0xe000:return self.prg[31*8192+addr-0xe000]
        raise ValueError('unexpected original CPU bus read '+hex(addr))
    def write(self,addr,val):
        addr &=0xffff;val&=255
        if addr<0x2000:self.ram[addr&2047]=val;return
        if addr==0x8000:
            check(val in (10,14) and self.ram[0x23]==val,'unexpected original mapper transition')
            self.bank=val;self.mapper.append(val);return
        raise ValueError('unexpected original CPU hardware write '+hex(addr))
    def byte(self):
        v=self.read(self.pc);self.pc=(self.pc+1)&65535;return v
    def word(self):return self.byte()|(self.byte()<<8)
    def step(self):
        here=self.pc;op=self.byte();self.steps+=1
        check(self.steps<12500,'original CPU failed bounded terminating stream')
        check(0xb7f7<=here<0xb873 or 0xfb96<=here<0xfba5 or
              0xe2d0<=here<0xe2d6,'original 6502 escaped full mapped source graph')
        if op==0xad:self.a=self.read(self.word());self.flags(self.a)
        elif op==0x0a:self.c=self.a>>7;self.a=(self.a<<1)&255;self.flags(self.a)
        elif op==0xa8:self.y=self.a;self.flags(self.y)
        elif op==0xb9:self.a=self.read((self.word()+self.y)&65535);self.flags(self.a)
        elif op==0x85:self.write(self.byte(),self.a)
        elif op==0xa0:self.y=self.byte();self.flags(self.y)
        elif op==0x20:
            target=self.word();ret=(self.pc-1)&65535
            if target==0xfb96:self.script_calls+=1
            self.push(ret>>8);self.push(ret&255);self.pc=target
        elif op==0x4a:self.c=self.a&1;self.a>>=1;self.flags(self.a)
        elif op==0x29:self.a &=self.byte();self.flags(self.a)
        elif op==0xc8:self.y=(self.y+1)&255;self.flags(self.y)
        elif op==0x8d:self.write(self.word(),self.a)
        elif op==0xa2:self.x=self.byte();self.flags(self.x)
        elif op==0xc9:
            v=self.byte();d=(self.a-v)&255;self.c=int(self.a>=v);self.flags(d)
        elif op==0xf0:
            d=self.byte();
            if self.z:self.pc=(self.pc+(d if d<128 else d-256))&65535
        elif op==0x9d:self.write((self.word()+self.x)&65535,self.a)
        elif op==0xe8:self.x=(self.x+1)&255;self.flags(self.x)
        elif op==0x4c:self.pc=self.word()
        elif op==0x60:self.pc=((self.pop()|(self.pop()<<8))+1)&65535
        elif op==0xa9:self.a=self.byte();self.flags(self.a)
        elif op==0xb1:
            zp=self.byte();root=self.read(zp)|(self.read((zp+1)&255)<<8)
            addr=(root+self.y)&65535
            check(self.bank==14,'source stream read with wrong mapper state')
            self.stream_reads.append(addr)
            self.a=self.read(addr);self.flags(self.a)
        elif op==0x48:self.push(self.a)
        elif op==0x68:self.a=self.pop();self.flags(self.a)
        else:raise ValueError(f'original unsupported opcode {op:02X} at {here:04X}')
    def run(self):
        while self.pc!=0x9000:self.step()
        check(self.sp==0xfd and self.bank==10 and self.ram[0x23]==10,'original CPU did not return to mapped parent')

class Result(ctypes.Structure):
    _fields_=[('ram_after',ctypes.c_uint8*2048),('source_root',ctypes.c_uint16)]
    _fields_+= [(k,ctypes.c_uint8) for k in ('record_count','source_y_after','x_after','a_after',
        'carry_after','zero_after','negative_after','overflow_after','bank_after',
        'source_calls','mapper_events')]
    _fields_.append(('mapper_values',ctypes.c_uint8*114))

def matrix(prg,bank0a,bank0e,lib,seeds):
    dll=ctypes.CDLL(str(lib.resolve()));fn=dll.cviii_room_stream_0659
    fn.argtypes=[ctypes.POINTER(ctypes.c_uint8),ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint8),ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint8),ctypes.c_size_t,ctypes.c_uint8,ctypes.POINTER(Result)]
    fn.restype=ctypes.c_int
    bank0=(ctypes.c_uint8*16384).from_buffer_copy(bank0a)
    bank14=(ctypes.c_uint8*16384).from_buffer_copy(bank0e)
    totals={'cases':0,'original_6502_instructions':0,'nonstack_ram_compared':0,'mapper_register_events':0,
            'source_reads':0,'records_installed':0}
    report=[]
    for selector in range(5):
        for seed in range(seeds):
            before=bytearray((i*17+seed*31)&255 for i in range(2048))
            before[0x7a0]=selector;before[0x23]=10
            ov=seed&1
            cpu=CPU(prg,before,ov);cpu.run()
            out=Result()
            ram=(ctypes.c_uint8*2048).from_buffer_copy(before)
            check(fn(bank0,16384,bank14,16384,ram,2048,ov,ctypes.byref(out))==1,
                  'native rejected original room data')
            for addr in (*range(0,256),*range(512,2048)):
                check(cpu.ram[addr]==out.ram_after[addr],
                      f'FIRST original/native RAM divergence selector={selector} seed={seed} addr={addr:04X} '+
                      f'{cpu.ram[addr]:02X}!={out.ram_after[addr]:02X}')
            check((cpu.a,cpu.x,cpu.y,cpu.c,cpu.z,cpu.n,cpu.v,cpu.bank)==
                  (out.a_after,out.x_after,out.source_y_after,out.carry_after,
                   out.zero_after,out.negative_after,out.overflow_after,out.bank_after),
                   f'original/native CPU A/X/Y/P postconditions differ selector={selector} seed={seed}')
            check(tuple(cpu.mapper)==tuple(out.mapper_values[:out.mapper_events]),
                  'original/native exact mapper switch sequence mismatch')
            check(cpu.script_calls==out.source_calls==7+5*out.record_count,
                  'original/native crossbank helper call count mismatch')
            check(len(cpu.stream_reads)==cpu.script_calls,
                  'original 6502 physical stream read count mismatch')
            check(out.record_count==EXPECTED_COUNTS[selector],
                  'original source stream record census changed')
            check(out.source_root==EXPECTED_ROOTS[selector],
                  'original physical source root mismatch')
            totals['cases']+=1;totals['original_6502_instructions']+=cpu.steps
            totals['nonstack_ram_compared']+=1792
            totals['mapper_register_events']+=len(cpu.mapper)
            totals['source_reads']+=len(cpu.stream_reads)
            totals['records_installed']+=out.record_count
        report.append({'selector':selector,'root_cpu':f'{EXPECTED_ROOTS[selector]:04X}',
                       'records':EXPECTED_COUNTS[selector], 'source_reads_per_case':7+5*EXPECTED_COUNTS[selector]})
    totals.update({'conditional_original_6502':True,'natural_Mesen_gameplay_trace':False,
                   'new_strict_prg_bytes':0,'stage_0e_stream_sources':report})
    return totals

def smoke():
    check(tuple(7+5*n for n in EXPECTED_COUNTS)==(57,42,27,27,32),
          'original room source byte count drift')
    check(sum(EXPECTED_COUNTS)==30 and len(EXPECTED_ROOTS)==5,'room five-root census')
    print('PASS JP0659 ROM-free 5 room stream selectors / 30 record installation cases')

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--smoke',action='store_true');ap.add_argument('--rom',type=Path)
    ap.add_argument('--native-lib',type=Path);ap.add_argument('--seeds',type=int,default=256)
    ap.add_argument('--json',type=Path)
    args=ap.parse_args()
    if args.smoke:smoke()
    if args.rom:
        check(args.native_lib is not None and 1<=args.seeds<=256,'compiled library and 1..256 seeds required')
        report=matrix(*authentic(args.rom.read_bytes())[:3],args.native_lib,args.seeds)
        if args.json:args.json.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
        print('PASS JP0659 authentic original 6502 bank0A/bank0E loader parity:',report)
    elif not args.smoke:ap.error('specify --smoke or --rom --native-lib')
if __name__=='__main__':main()
