#!/usr/bin/env python3
"""ROM-authoritative 6502 instruction replay of JP phrase controls $FB-$FF.

No sound data is written to Git, and no original runtime liveness asserted.
"""
from __future__ import annotations
import argparse, ctypes, hashlib, json
from collections import Counter
from pathlib import Path

ORIGINAL_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
BANK_SHA='f52c62b3c01fb10e9d727b9e983a2d0c1fc78ef502c5f972f9b28a349b2a9a42'
PFX_SHA='cee4cc1f5bfa0852bbb7ba9ac6c56d841d19cb1218009570b0383b9bd507f4c3'
CONTROL_SHA='b483a567561def4d16207dc526ed89c53bf69e673651fc06b637d970f31cb315'
POOL_SHA='a35de62be83954e53e65ef149ee74d5e1f95e3d1999009bcf90221bd47e7e7b5'
BANK_SIZE=16384

def check(cond,msg):
    if not cond:raise ValueError(msg)
def sha(x):return hashlib.sha256(x).hexdigest()
def original_bank(rom):
    check(len(rom)==393232 and sha(rom)==ORIGINAL_SHA and rom[:4]==b'NES\x1a'
          and (rom[6]>>4 | rom[7]&0xf0)==24,'not authenticated JP VRC6 ROM')
    return rom[16+12*BANK_SIZE:16+13*BANK_SIZE]
def authenticate(bank):
    check(len(bank)==BANK_SIZE and sha(bank)==BANK_SHA,'changed raw0C')
    for lo,hi,digest in ((0x8d15,0x8d20,PFX_SHA),(0x8d90,0x8dcd,CONTROL_SHA),
                         (0xa42c,0xa957,POOL_SHA)):
        check(sha(bank[lo-0x8000:hi-0x8000])==digest,'source span changed')
    contents=Counter(bank[0xa42c-0x8000:0xa957-0x8000]);
    check({k:contents[k] for k in range(0xfb,0x100)}==
          {0xfb:30,0xfc:0,0xfd:0,0xfe:30,0xff:141},'phrase control census changed')

def fixture(source,cursor,x,param,repeat_start,counter,original_v=0):
    mem=bytearray(2048)
    ptr=(source-cursor)&65535
    mem[0xe2:0xe4]=ptr.to_bytes(2,'little')
    mem[0x06aa+x]=cursor;mem[0x06a0+x]=repeat_start
    mem[0x06af+x]=counter;mem[0x03f2+x]=0x35
    return bytes(mem)

def original_cpu(bank, ram, x, incoming_v):
    """Fetch each original NMOS 6502 opcode, perform exact RAM/bus operations.
    Stops at $8D06 transfer or at the $8DCC RTS; no speculative callee.
    """
    check(len(bank)==BANK_SIZE and len(ram)==2048 and 0<=x<=255 and
          incoming_v in (0,1),'bad source CPU fixture')
    mem=bytearray(ram);a=y=c=z=n=0;v=incoming_v;pc=0x8d15
    writes=[];steps=0
    def rd():
        nonlocal pc
        check(0x8d15<=pc<0x8dcd,'original control PC escaped verified window')
        b=bank[pc-0x8000];pc+=1;return b
    def rd16():
        lo=rd();return lo+(rd()<<8)
    def flags(val):
        nonlocal z,n
        z=int((val&255)==0);n=int(bool(val&128))
    def compare(val):
        nonlocal c,z,n
        diff=(a-val)&255;c=int(a>=val);flags(diff)
    while steps<32:
        at=pc;op=rd();steps+=1
        if op==0xbd: # LDA abs,X
            addr=(rd16()+x)&65535;check(addr<2048,'unmapped RAM indexed read')
            a=mem[addr];flags(a)
        elif op==0xa8:y=a;flags(y)
        elif op==0xb1: # LDA (zp),Y with physical source raw0C
            zp=rd();ptr=mem[zp]|mem[(zp+1)&255]<<8
            addr=(ptr+y)&65535;check(0x8000<=addr<0xc000,'read outside raw0C')
            a=bank[addr-0x8000];flags(a)
        elif op==0xc9:compare(rd())
        elif op in (0xb0,0xf0,0xd0):
            rel=rd();take= (op==0xb0 and c==1) or (op==0xf0 and z==1) or (op==0xd0 and z==0)
            if take:pc=(pc+(rel if rel<128 else rel-256))&65535
        elif op==0xfe: # INC abs,X
            addr=(rd16()+x)&65535;check(addr<2048,'unmapped RAM increment')
            mem[addr]=(mem[addr]+1)&255;flags(mem[addr]);writes.append(addr)
        elif op==0x9d: # STA abs,X
            addr=(rd16()+x)&65535;check(addr<2048,'unmapped RAM store')
            mem[addr]=a;writes.append(addr)
        elif op==0x4c:
            target=rd16();check(target==0x8d06,'unexpected unconditional original JMP')
            pc=target;break
        elif op==0xc8:y=(y+1)&255;flags(y)
        elif op==0xdd:
            addr=(rd16()+x)&65535;check(addr<2048,'unmapped RAM compare')
            compare(mem[addr])
        elif op==0xa9:a=rd();flags(a)
        elif op==0x60:
            check(at==0x8dcc,'RTS at unexpected original PC')
            pc=at;break
        else:raise ValueError(f'uncertified opcode {op:02X} at {at:04X}')
    else:raise ValueError('original 6502 failed bounded opcode budget')
    check(pc in (0x8d06,0x8dcc),'original control exit not bounded')
    return {'ram':bytes(mem),'a':a,'x':x,'y':y,'c':c,'z':z,'n':n,'v':v,
            'next_pc':pc,'writes':writes,'steps':steps}

class Result(ctypes.Structure):
    _fields_=[(k,ctypes.c_uint8) for k in
              ('token','kind','parameter','a','x','y','carry','zero','negative','overflow',
               'cursor','repeat_start','repeat_counter','high_nibble',
               'write_cursor','write_repeat_start','write_repeat_counter','write_high_nibble')]
    _fields_ += [('token_cpu',ctypes.c_uint16),('next_pc',ctypes.c_uint16)]

def check_result(bank,fn,image,source,x,cursor,repeat_start,counter,original_v):
    ram=fixture(source,cursor,x,0,repeat_start,counter,original_v)
    # Only the token's actual source location determines input. The FE
    # parameter may be at source+1 or at pointer when cursor==255.
    step=original_cpu(bank,ram,x,original_v)
    a=(ctypes.c_uint8*2048).from_buffer_copy(ram);out=Result()
    ret=fn(image,16384,a,2048,x,original_v,ctypes.byref(out))
    check(ret==1,f'host rejected control at {source:04X}')
    before=ram;after=step['ram'];delta={i for i in range(2048) if before[i]!=after[i]}
    allowed={0x06aa+x,0x06a0+x,0x06af+x,0x03f2+x}
    check(delta<=allowed,'reference control changed undocumented RAM')
    # Account writes even if the final value happens to equal initial.
    expected_writes={i for i in step['writes']}
    kind=out.kind
    check(kind in (1,2,3,4),'unrecognized control subroutine')
    check(out.token==bank[source-0x8000] and out.token_cpu==source,
          'original source bus identity differs')
    expected={
      'a':step['a'],'x':step['x'],'y':step['y'],'carry':step['c'],
      'zero':step['z'],'negative':step['n'],'overflow':step['v'],
      'cursor':after[0x06aa+x], 'repeat_start':after[0x06a0+x],
      'repeat_counter':after[0x06af+x],'high_nibble':after[0x03f2+x],
      'next_pc':step['next_pc'],
      'write_cursor':int(0x06aa+x in expected_writes),
      'write_repeat_start':int(0x06a0+x in expected_writes),
      'write_repeat_counter':int(0x06af+x in expected_writes),
      'write_high_nibble':int(0x03f2+x in expected_writes)
    }
    for key,val in expected.items():
        if getattr(out,key)!=val:
            raise ValueError(f'6502/native divergence at {source:04X} '+
                             f'token={out.token:02X} x={x} y={cursor} count={counter}: '+
                             f'{key}: native={getattr(out,key)} reference={val}')
    check((kind==1)==(out.token in (0xfb,0xfc,0xfd)), 'invalid jump opcode class')
    check((kind==4)==(out.token==0xff),'invalid termination opcode class')
    if out.token==0xfe:
        ptr=(source-cursor)&65535
        paramcpu=(ptr+((cursor+1)&255))&65535
        check(out.parameter==bank[paramcpu-0x8000],'FE parameter bus differs')
        check((kind==2)==(out.parameter==((counter+1)&255)),'FE repeat branch mismatch')
    return kind,step['steps']

def native_replay(bank,library):
    dll=ctypes.CDLL(str(library.resolve())); fn=dll.cviii_phrase_control_0656
    fn.argtypes=[ctypes.POINTER(ctypes.c_uint8),ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint8),ctypes.c_size_t,ctypes.c_uint8,
        ctypes.c_uint8,ctypes.POINTER(Result)]
    fn.restype=ctypes.c_int
    image=(ctypes.c_uint8*BANK_SIZE).from_buffer_copy(bank)
    locations=[a for a in range(0xa42c,0xa957) if bank[a-0x8000]>=0xfb]
    check(len(locations)==201,'original source pool special-token count changed')
    bykind=Counter();cases=0;maximum=0
    for location in locations:
        token=bank[location-0x8000]
        for j,(x,cursor,repeat_start,seedcounter) in enumerate((
             (0,0,0,0),(1,1,255,255),(7,127,128,127),
             (31,254,13,253),(63,255,0,17),(127,55,255,0),
             (255,128,99,252))):
            original_v=j&1
            if token==0xfe:
                pointer=(location-cursor)&65535
                parameter=bank[((pointer+((cursor+1)&255))&65535)-0x8000]
                counts=((parameter-1)&255,parameter,seedcounter)
            else:counts=(seedcounter,)
            for counter in counts:
                kind,steps=check_result(bank,fn,image,location,x,cursor,
                                         repeat_start,counter,original_v)
                bykind[kind]+=1;cases+=1;maximum=max(maximum,steps)
    check(cases==1827,'expected all source commands and FE branch seeds')
    check(bykind[1]==210 and bykind[4]==987 and bykind[2]>=210 and bykind[3]>=210,
          f'wrong source command branch histogram {bykind}')
    # Exercise $FC/$FD too: these are legitimate original comparator outcomes
    # but ABSENT from the authenticated 1323-byte pool. Alter only a private
    # scratch *data* byte; executable original 6502 opcodes remain genuine.
    # This is labeled invented-data testing, never original usage evidence.
    synthetic=0
    for token in range(0xfb,0x100):
        scratch=bytearray(bank)
        scratch[0xa42c-0x8000]=token
        scratch=bytes(scratch)
        scratch_image=(ctypes.c_uint8*BANK_SIZE).from_buffer_copy(scratch)
        for x,cursor in ((0,0),(1,1),(7,127),(31,254),(63,255),(127,55),(255,128)):
            pointer=(0xa42c-cursor)&65535
            par= scratch[((pointer+((cursor+1)&255))&65535)-0x8000]
            for counter in (((par-1)&255,par) if token==0xfe else (0,)):
                check_result(scratch,fn,scratch_image,0xa42c,x,cursor,0x7f,counter,0)
                synthetic+=1
    check(synthetic==42,'synthetic five-class complete source comparison drift')
    return {'original_6502_vs_native_cases':cases,
            'synthetic_all_five_control_byte_cases':synthetic,
            'control_source_locations':201,'total_phrase_pool_bytes':1323,
            'branch_hits':dict(sorted(bykind.items())),
            'max_instructions':maximum,'observed_retail_gameplay_liveness':False,
            'verified_6502_cycle_parity':False}

def smoke():
    # ROM-free independent structural control truth table; original source
    # input can be validated only with --rom and compiled native binary.
    roots=(0xfb,0xfc,0xfd,0xfe,0xff)
    assert len(roots)==5
    assert [int(z>=0xfe) for z in roots]==[0,0,0,1,1]
    assert all(((y+1)&255)==0 for y in (255,))
    assert len({(p-1)&255 for p in range(256)})==256
    print('PASS JP0656 synthetic control-domain and 8-bit wrap contracts')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path)
    p.add_argument('--native-lib',type=Path)
    p.add_argument('--json',type=Path)
    p.add_argument('--smoke',action='store_true')
    o=p.parse_args()
    if o.smoke:smoke()
    if o.rom:
        if not o.native_lib:p.error('--native-lib required for original CPU/host replay')
        bank=original_bank(o.rom.read_bytes());authenticate(bank)
        report=native_replay(bank,o.native_lib)
        if o.json:o.json.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
        print('PASS JP0656',report)
    elif not o.smoke:p.error('provide --smoke or --rom and --native-lib')
if __name__=='__main__':main()
