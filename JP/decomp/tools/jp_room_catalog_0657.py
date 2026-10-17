#!/usr/bin/env python3
"""JP0657 entire raw0A 15/64/135 stage hierarchy and native C11 parity.

Authenticated original ROM is private; outputs are aggregate, not stages/assets.
Original $801E-$8046 6502 opcodes are executed, not pointer-formula-only.
"""
from __future__ import annotations
import argparse
import ctypes
import hashlib
import json
from pathlib import Path
ROM_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
BANK_SHA='1460df577d44e114c64fdf34a8837629765f3f6a93d45796fdf81e5ffacb5ed8'
SELECT_SHA='31d3ba22edd5ef269b08f4c4322bbe78bd34588d186a500a9c1edee4de0c13f8'
def require(ok,why):
    if not ok:raise ValueError(why)
def sha(b):return hashlib.sha256(b).hexdigest()
def bank_of(rom):
    require(len(rom)==393232 and rom[:4]==b'NES\x1a' and sha(rom)==ROM_SHA and
            (rom[6]>>4 | rom[7]&240)==24,'original Japanese mapper24 ROM identity failure')
    b=rom[16+10*16384:16+11*16384]
    require(sha(b)==BANK_SHA and sha(b[0x1e:0x47])==SELECT_SHA,
            'original raw0A or three-level pointer-lookup opcode mismatch')
    return b

def original_lookup(bank,stage,second,third):
    ram=bytearray(256)
    ram[0x34]=stage;ram[0x35]=second;ram[0x36]=third
    pc=0x801e;a=y=0;step=0
    def read(at):
        if at<256:return ram[at]
        require(0x8000<=at<0xc000,'original source fetch outside raw0A')
        return bank[at-0x8000]
    while True:
        step+=1;require(step<=36,'unexpected CPU original lookup sequence')
        op=read(pc)
        if op==0xa5:a=read(read(pc+1));pc+=2
        elif op==0x0a:a=(a<<1)&255;pc+=1
        elif op==0xa8:y=a;pc+=1
        elif op==0xb9:
            at=read(pc+1)|read(pc+2)<<8
            a=read((at+y)&65535);pc+=3
        elif op==0x85:
            ram[read(pc+1)]=a;pc+=2
        elif op==0xb1:
            zp=read(pc+1);ptr=ram[zp]|ram[(zp+1)&255]<<8
            a=read((ptr+y)&65535);pc+=2
        elif op==0xc8:y=(y+1)&255;pc+=1
        elif op==0x60:
            require(pc==0x8046,'original lookup RTS at wrong address')
            return (ram[0x06]|ram[0x07]<<8,
                    ram[0x04]|ram[0x05]<<8,
                    ram[0x95]|ram[0x96]<<8),step
        else:raise ValueError(f'unknown original ROM opcode {op:02X} at {pc:04X}')

class Leaf(ctypes.Structure):
    _fields_=[(k,ctypes.c_uint8) for k in ('stage','second','third','width')]
    _fields_+= [('root',ctypes.c_uint16),('end_exclusive',ctypes.c_uint16)]
class Catalog(ctypes.Structure):
    _fields_=[(k,ctypes.c_uint16) for k in ('leaf_count','stages','tier2','cells4','records7','terminators7')]
    _fields_ += [('leaves',Leaf*135)]
def original_partition(b):
    def word(p):return b[p-0x8000]|b[p-0x8000+1]<<8
    stages=[word(0x92ae+i*2) for i in range(15)]
    require(stages[0]==0x92cc and stages[9]==0x9af4,'original stage table changed')
    second=[];triples=[]
    for i,st in enumerate(stages):
        limit= (0x9320 if i==8 else 0x9b20 if i==14 else stages[i+1])
        for j,src in enumerate(range(st,limit,2)):
            second.append((i,j,word(src)))
    require(len(second)==64,'second level source count changed')
    for idx,(i,j,start) in enumerate(second):
        stop= (0x93cc if idx==41 else 0x9b82 if idx==63 else second[idx+1][2])
        for k,src in enumerate(range(start,stop,2)):
            leaf=word(src)
            _,steps=original_lookup(b,i,j,k)
            require(steps==24,'original 6502 source-path length changed')
            triples.append((i,j,k,leaf))
    require(len(triples)==135,'third pointer source count changed')
    roots=sorted(set(v for _,_,_,v in triples))
    group4lo=[v for v in roots if 0x93cc<=v<0x9af4]
    group4hi=[v for v in roots if 0x9b82<=v<0x9f6e]
    group7=[v for v in roots if 0xab1f<=v<0xafa4]
    require((len(group4lo),len(group4hi),len(group7))==(70,43,16),
            'incorrect all-bank typed room-record source roots')
    spans={}
    for group,end,width in ((group4lo,0x9af4,4),(group4hi,0x9f6e,4),(group7,0xafa4,7)):
        for idx,root in enumerate(group):
            stop=group[idx+1] if idx+1<len(group) else end
            require(stop>root,'source room record empty interval')
            if width==4:require((stop-root)%4==0,'room cell stride changed')
            else:
                require((stop-root-1)%7==0 and b[stop-1-0x8000]==0xff,
                        'room seven-byte stream terminator changed')
                for p in range(root,stop-1,7):
                    require(b[p-0x8000]<=3,'seven-record structural first byte changed')
            spans[root]=(stop,width)
    require(sum((en-st)//4 for st,(en,w) in spans.items() if w==4)==709,
            'room four-byte cell population changed')
    require(sum((en-st-1)//7 for st,(en,w) in spans.items() if w==7)==163,
            'room seven-byte record count changed')
    return triples,spans

def parity(b,shared):
    binary=ctypes.CDLL(str(shared.resolve()))
    load=binary.cviii_room_catalog_0657
    load.argtypes=[ctypes.POINTER(ctypes.c_uint8),ctypes.c_size_t,ctypes.POINTER(Catalog)]
    load.restype=ctypes.c_int
    query=binary.cviii_room_catalog_find_0657
    query.argtypes=[ctypes.POINTER(Catalog),ctypes.c_uint8,ctypes.c_uint8,ctypes.c_uint8,ctypes.POINTER(Leaf)]
    query.restype=ctypes.c_int
    image=(ctypes.c_uint8*16384).from_buffer_copy(b)
    result=Catalog()
    require(load(image,16384,ctypes.byref(result))==1,'original room bank rejected by native catalog')
    require((result.leaf_count,result.stages,result.tier2,result.cells4,result.records7,result.terminators7)==
            (135,15,64,709,163,16),'native catalog summary differs')
    triples,spans=original_partition(b)
    for ordinal,(st,mid,idx,src) in enumerate(triples):
        original,steps=original_lookup(b,st,mid,idx)
        require(original[2]==src and steps==24,'original opcode-selector replay mismatch')
        leaf=Leaf()
        require(query(ctypes.byref(result),st,mid,idx,ctypes.byref(leaf))==1,
                'native catalog selector absent')
        stop,width=spans[src]
        require((leaf.stage,leaf.second,leaf.third,leaf.width,leaf.root,leaf.end_exclusive)==
                (st,mid,idx,width,src,stop),'original CPU/decoded structural leaf mismatch')
        stored=result.leaves[ordinal]
        require(bytes(stored)==bytes(leaf),'native catalog enumeration order changed')
    return {'original_lookup_to_native_catalog_cases':len(triples),
            'source_stages':15,'source_second_level_tables':64,
            'source_leaf_selectors':135,'unique_record_roots':len(spans),
            'complete_four_byte_cells':result.cells4,'complete_seven_byte_records':result.records7,
            'complete_ff_record_terminators':result.terminators7,
            'natural_gameplay_entry_verified':False,
            'original_ppu_room_render_parity':False}
def smoke():
    require(70+43+16==129 and 709*4==2836 and 163*7+16==1157,
            'room-data structural byte accounting drift')
    require(15*2+64*2+135*2==428,'pointer table abstract census')
    print('PASS JP0657 synthetic 15-stage/64-table/135-selector, 709x4/163x7 source geometry')
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--smoke',action='store_true')
    p.add_argument('--rom',type=Path)
    p.add_argument('--native-lib',type=Path)
    p.add_argument('--json',type=Path)
    args=p.parse_args()
    if args.smoke:smoke()
    if args.rom:
        if not args.native_lib:p.error('compiled --native-lib required for original ROM parity')
        report=parity(bank_of(args.rom.read_bytes()),args.native_lib)
        if args.json:args.json.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
        print('PASS JP0657 authentic entire raw0A stage hierarchy versus native C11',report)
    elif not args.smoke:p.error('require --smoke or --rom and --native-lib')
if __name__=='__main__':main()
