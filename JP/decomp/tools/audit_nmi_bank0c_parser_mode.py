#!/usr/bin/env python3
from __future__ import annotations
import hashlib, sys
from pathlib import Path

EXPECTED_SHA256='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
EXPECTED_NEW_SPAN_SHA256='d7387b04a03289ebb1a0567ef49240d90b0bb177a0c128c8b06dbccabdb0776f'
META_TABLE=0x8F60
META_COUNT=0x7D
CONTROL_FIELD_STORE_SITES=[0x8098,0x8114,0x8358,0x858E,0x85AD,0x85E3,0x860B,0x8620,0x8682,0x88F2,0x8C47,0x8C6B,0x8E2F,0x8E50,0x8E6C,0x8E95,0x8EB7]
ALT_REFS_EXPECTED=[(0x0C,8,0x9D8F),(0x0D,8,0x9F73),(0x22,8,0xA303),(0x3A,8,0xA303),(0x3B,8,0xA303)]

CONTROL_CONTEXTS={
0x8098: bytes.fromhex('bd1b0129bb0902'),
0x8114: bytes.fromhex('bd1b0129b9'),
0x8358: bytes.fromhex('bd1b010940'),
0x858E: bytes.fromhex('bd1b0129f7'),
0x85AD: bytes.fromhex('bd1b0129fb'),
0x85E3: bytes.fromhex('bd1b010908'),
0x860B: bytes.fromhex('bd1b010920'),
0x8620: bytes.fromhex('bd1b0129df'),
0x8682: bytes.fromhex('bd1b0129f9'),
0x8C47: bytes.fromhex('bd1b010906'),
0x8C6B: bytes.fromhex('bd1b01090429fd'),
0x8E2F: bytes.fromhex('bd1b010902'),
0x8E50: bytes.fromhex('bd1b0129f9'),
0x8E6C: bytes.fromhex('bd1b0129f9'),
0x8E95: bytes.fromhex('bd1b010980'),
0x8EB7: bytes.fromhex('bd1b01297f'),
}

def main(path:str)->None:
    rom=Path(path).read_bytes()
    assert hashlib.sha256(rom).hexdigest()==EXPECTED_SHA256
    prg=rom[16:16+0x40000]
    raw=prg[24*0x2000:26*0x2000]
    def rd(cpu:int,n:int=1)->bytes:
        assert 0x8000<=cpu<0xC000 and cpu+n<=0xC000
        return raw[cpu-0x8000:cpu-0x8000+n]

    new_span=rd(0x9200,0xE00)
    assert len(new_span)==3584
    assert hashlib.sha256(new_span).hexdigest()==EXPECTED_NEW_SPAN_SHA256

    fixed=prg[31*0x2000:32*0x2000]
    def rf(cpu:int,n:int)->bytes:
        return fixed[cpu-0xE000:cpu-0xE000+n]
    assert rf(0xE1AF,9)==bytes.fromhex('bdd30620d0e24c0180')
    assert rd(0x8DCD,9)==bytes.fromhex('4a90034cea8d4cafe1')
    assert rd(0x88E0,0x15)==bytes.fromhex('209fe1c8c9109009e005f005e006f00188989d1b01')

    all_sites=[]; p=0; needle=bytes.fromhex('9d1b01')
    while True:
        i=raw.find(needle,p)
        if i<0: break
        all_sites.append(0x8000+i); p=i+1
    assert all_sites==CONTROL_FIELD_STORE_SITES, [hex(x) for x in all_sites]
    for site,ctx in CONTROL_CONTEXTS.items():
        assert rd(site-len(ctx),len(ctx))==ctx
    assert rd(0x88F1,4)==bytes.fromhex('989d1b01')
    for pat in ('8d1b01','991b01','8c1b01','8e1b01','ee1b01','ce1b01','fe1b01','de1b01'):
        assert bytes.fromhex(pat) not in raw

    ptrs=[]
    for sid in range(1,META_COUNT+1):
        b=rd(META_TABLE+(sid-1)*2,2)
        ptrs.append(b[0]|(b[1]<<8))
    assert ptrs[0]==0x905A and ptrs[-1]==0x953D
    assert min(ptrs)==0x905A and max(ptrs)==0x953D

    refs=[]
    for sid,ptr in enumerate(ptrs,1):
        bank=rd(ptr,1)[0]
        if bank==0:
            continue
        nminus=rd(ptr+1,1)[0]
        rec=rd(ptr,2+3*(nminus+1))
        for j in range(nminus+1):
            inst=rec[2+3*j]
            addr=rec[3+3*j] | (rec[4+3*j]<<8)
            if bank==0x0C:
                refs.append((sid,inst,addr,rd(addr,1)[0]))

    assert len(refs)==139
    assert len({a for _,_,a,_ in refs})==125
    alt=[(sid,inst,addr) for sid,inst,addr,first in refs if not (first<0x10 or inst in (5,6))]
    assert alt==ALT_REFS_EXPECTED, [(hex(s),i,hex(a)) for s,i,a in alt]
    for _,_,addr in alt:
        assert rd(addr,1)==b'\xff'

    roots=sorted({a for _,_,a,_ in refs})
    e7=[]
    for a in range(min(roots), min(max(roots)+1,0xA000)):
        if rd(a,1)==b'\xe7':
            root=max(r for r in roots if r<=a)
            root_refs=[r for r in refs if r[2]==root]
            assert root_refs
            assert all((first<0x10 or inst in (5,6)) for _,inst,_,first in root_refs)
            e7.append(a)
    assert e7==[0x9695,0x97BB,0x97C7,0x9D73], [hex(x) for x in e7]

    print('ROM identity: OK')
    print('new PRG24 span $9200-$9FFF: 3584 bytes, SHA-256',EXPECTED_NEW_SPAN_SHA256)
    print('bank-$0C metadata refs:',len(refs),'distinct roots:',len({a for _,_,a,_ in refs}))
    print('alternate-parser refs:',[(f'${s:02X}',i,f'${a:04X}') for s,i,a in alt])
    print('all alternate-parser roots begin with $FF')
    print('all raw E7 bytes in referenced PRG24 stream data belong to main-mode roots')
    print('control-byte bit 0 has one initializer and all later direct writers preserve it')
    print('04F6 result: PRG24 $842D is not a live bank-$0C stream dispatch; prior static edge was state/bank over-approximation')

if __name__=='__main__':
    if len(sys.argv)!=2: raise SystemExit(f'usage: {Path(sys.argv[0]).name} ROM.nes')
    main(sys.argv[1])
