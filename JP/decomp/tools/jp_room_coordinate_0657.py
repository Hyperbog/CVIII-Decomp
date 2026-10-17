#!/usr/bin/env python3
"""JP0657 original PRG0A $80D1-$8107 ROM-fetched CPU vs native C11.

Conditional room calculation; not a live original-Mesen gameplay trace.
No commercial game bytes or owner-local per-case outputs emitted.
"""
import argparse
import ctypes
import hashlib
import json
from pathlib import Path
ROM_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
BANK_SHA='1460df577d44e114c64fdf34a8837629765f3f6a93d45796fdf81e5ffacb5ed8'
CODE1_SHA='a5bfb0b51b7d7e50ec5dbc1fd882490136b49e0d91f9245aa06dea86aa19a6bb'
CODE2_SHA='73e0e407e4a2151a9af018b41f000e7ab4fd4d6693fccd594cef6cc29b7ac014'
def sha(b):return hashlib.sha256(b).hexdigest()
def check(x,msg):
    if not x:raise ValueError(msg)
def authenticate(rom):
    check(len(rom)==393232 and sha(rom)==ROM_SHA and rom[:4]==b'NES\x1a' and
          (rom[6]>>4|rom[7]&0xf0)==24,'wrong Japanese Mapper24 image')
    b=rom[16+10*16384:16+11*16384]
    check(sha(b)==BANK_SHA,'raw0A physical bank SHA mismatch')
    check(sha(b[1:0x1e])==CODE1_SHA,'stage 16-bit coordinate helper changed')
    check(sha(b[0xd1:0x108])==CODE2_SHA,'stage coordinate caller changed')
    return b

def original_cpu(bank,low,high,mode):
    ram=bytearray(2048)
    ram[0x53]=low;ram[0x54]=high;ram[0x62]=255 if mode else 0
    a=x=y=c=z=n=v=0
    sp=255;pc=0x80D1
    step=0
    def flags(t):
        nonlocal z,n
        z=int(t==0);n=int(bool(t&128))
    def fetch():
        nonlocal pc
        check((0x8001<=pc<0x801e) or (0x80d1<=pc<0x8108),'left audited PC intervals')
        val=bank[pc-0x8000];pc+=1;return val
    def push(t):
        nonlocal sp
        ram[0x100+sp]=t&255;sp=(sp-1)&255
    def pop():
        nonlocal sp
        sp=(sp+1)&255;return ram[0x100+sp]
    def adc(q):
        nonlocal a,c,v
        old=a;total=a+q+c;r=total&255
        c=int(total>255);v=int(bool((~(old^q)&(old^r)&128)))
        a=r;flags(a)
    while pc!=0x8108:
        step+=1
        check(step<80,'unexpected CPU control loop')
        op=fetch()
        if op==0x20:
            lo=fetch();hi=fetch();ret=pc-1
            push(ret>>8);push(ret&255);pc=lo|hi<<8
        elif op==0x60:
            pc= (pop() | (pop()<<8))+1
        elif op==0x48:push(a)
        elif op==0x68:a=pop();flags(a)
        elif op==0x18:c=0
        elif op==0xa5:a=ram[fetch()];flags(a)
        elif op==0xa6:x=ram[fetch()];flags(x)
        elif op==0xa9:a=fetch();flags(a)
        elif op==0xa0:y=fetch();flags(y)
        elif op==0x69:adc(fetch())
        elif op==0x65:adc(ram[fetch()])
        elif op==0x85:ram[fetch()]=a
        elif op==0x84:ram[fetch()]=y
        elif op==0x0a:c=(a>>7)&1;a=(a<<1)&255;flags(a)
        elif op==0x26:
            addr=fetch();temp=ram[addr];carry=(temp>>7)&1
            ram[addr]=((temp<<1)|c)&255;c=carry;flags(ram[addr])
        elif op==0x4c:pc=fetch()|(fetch()<<8)
        elif op==0xf0 or op==0xd0:
            raw=fetch();taken=(op==0xf0 and z==1) or (op==0xd0 and z==0)
            if taken:pc=(pc+raw-(256 if raw>=128 else 0))&65535
        elif op==0x29:a&=fetch();flags(a)
        elif op==0x09:a|=fetch();flags(a)
        elif op==0xa4:y=ram[fetch()];flags(y)
        else:raise ValueError(f'Unsupported ROM 6502 op {op:02X} at {pc-1:04X}')
    check(sp==255,'unexpected saved return stack state')
    return (a,x,y,c,z,n,v,ram[0x73],ram[8],ram[9],ram[0xe],ram[0xa]),step
class Result(ctypes.Structure):
    _fields_=[(k,ctypes.c_uint8) for k in ('a','x','y','carry','zero','negative','overflow',
       'room_hi_73','room_sub_08','room_offset_09','masked_0e','room_phase_0a')]
def parity(bank,path):
    fn=ctypes.CDLL(str(path.resolve())).cviii_room_coordinate_0657
    fn.argtypes=[ctypes.POINTER(ctypes.c_uint8),ctypes.c_size_t,ctypes.POINTER(ctypes.c_uint8),ctypes.c_size_t,ctypes.POINTER(Result)]
    fn.restype=ctypes.c_int
    image=(ctypes.c_uint8*16384).from_buffer_copy(bank)
    ram=(ctypes.c_uint8*2048)();output=Result()
    tested=0;maxstep=0
    for low in range(256):
        for high in range(256):
            for mode in range(2):
                reference,steps=original_cpu(bank,low,high,mode)
                ram[0x53]=low;ram[0x54]=high;ram[0x62]=255 if mode else 0
                status=fn(image,16384,ram,2048,ctypes.byref(output))
                actual=tuple(getattr(output,k) for k,_ in output._fields_)
                check(status==1 and actual==reference,
                      f'original CPU/native room-coordinate divergence input={low,high,mode}: {reference} != {actual}')
                tested+=1;maxstep=max(maxstep,steps)
    check(tested==131072,'room coordinate cross product changed')
    return {'original_rom_to_compiled_c11_cases':tested,'maximum_original_6502_instructions':maxstep,
            'physical_prg_bank':'raw0A','original_mapper_liveness_proven':False,
            'full_gameplay_frame_parity':False}
def smoke():
    # Independent 8-bit carry table and sign/wrap boundary tests; no ROM data.
    count=0
    for lo in range(256):
        for hi in (0,127,128,255):
            base=((hi<<8)|lo)
            shifted=((base+2)<<2)&0xffff
            high=((hi+int(lo>=254))&255)
            expected=((high<<2)|(((lo+2)&255)>>6))&255
            check((shifted>>8)==expected,'16-bit coordinate wrap mismatch')
            count+=1
    check(count==1024,'smoke census drift')
    print('PASS JP0657 1024 synthetic original coordinate wrap cases')
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path)
    p.add_argument('--native-lib',type=Path)
    p.add_argument('--json',type=Path)
    p.add_argument('--smoke',action='store_true')
    args=p.parse_args()
    if args.smoke:smoke()
    if args.rom:
        if not args.native_lib:p.error('--native-lib required with original ROM')
        r=parity(authenticate(args.rom.read_bytes()),args.native_lib)
        if args.json:args.json.write_text(json.dumps(r,sort_keys=True,indent=2)+'\n')
        print('PASS JP0657',r)
    elif not args.smoke:p.error('specify --smoke or --rom with --native-lib')
if __name__=='__main__':main()
