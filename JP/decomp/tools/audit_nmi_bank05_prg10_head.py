#!/usr/bin/env python3
from __future__ import annotations
import hashlib, sys
from collections import Counter, deque
from pathlib import Path

ROM_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
SPAN_START,SPAN_END=0x87AE,0x9A6B
SPAN_SHA='58f4a24e41ba95766529e1eaa531c63fc666ca51abc668ec4eb3ba3f4e50eb6b'
COMMON_START,COMMON_END=0x8001,0x87AE
COMMON_SHA='e2c3ff3d7e9f96b598610a8028f5b92a606fac7f9acb2977811146fa145fdb67'
META_TABLE,META_COUNT=0x8F60,0x7D
EXPECTED_REFS=[
(0x50,0,0x87F9),(0x50,1,0x8811),(0x50,2,0x882A),(0x50,3,0x87AE),(0x50,4,0x87C8),(0x50,7,0x87E1),
(0x51,0,0x8E17),(0x51,1,0x8FE0),(0x51,2,0x91B9),(0x51,3,0x8842),(0x51,4,0x8ACD),(0x51,7,0x8CCB),
(0x52,0,0x9644),(0x52,1,0x9773),(0x52,2,0x97FC),(0x52,3,0x9387),(0x52,4,0x94B1),(0x52,7,0x95E6),
(0x53,3,0x995F),
]
EXPECTED_E7={(0x8A39,0x50),(0x8BDC,0x50),(0x8E2C,0x58),(0x8EFE,0x50),(0x911F,0x50),(0x9126,0x55),(0x924A,0x80),(0x9260,0x80),(0x928C,0x02)}

def main(path):
    rom=Path(path).read_bytes(); assert hashlib.sha256(rom).hexdigest()==ROM_SHA
    prg=rom[16:16+0x40000]
    def rb(n): return prg[(n*2)*0x2000:(n*2+2)*0x2000]
    r04,r05,r0c=rb(4),rb(5),rb(0x0c)
    def read(bank,a,n=1):
        assert 0x8000<=a<0xC000 and a+n<=0xC000
        return bank[a-0x8000:a-0x8000+n]
    common=read(r05,COMMON_START,COMMON_END-COMMON_START)
    assert common==read(r04,COMMON_START,COMMON_END-COMMON_START)
    assert len(common)==1965 and hashlib.sha256(common).hexdigest()==COMMON_SHA
    assert read(r05,0x8430,0x14)==bytes.fromhex('4484'*10)
    span=read(r05,SPAN_START,SPAN_END-SPAN_START)
    assert len(span)==4797 and hashlib.sha256(span).hexdigest()==SPAN_SHA

    ptrs=[]
    for sid in range(1,META_COUNT+1):
        b=read(r0c,META_TABLE+(sid-1)*2,2); ptrs.append(b[0]|b[1]<<8)
    refs=[]
    for sid,ptr in enumerate(ptrs,1):
        if read(r0c,ptr)[0]!=0x05: continue
        nminus=read(r0c,ptr+1)[0]; rec=read(r0c,ptr,2+3*(nminus+1))
        for j in range(nminus+1):
            inst=rec[2+3*j]; a=rec[3+3*j]|rec[4+3*j]<<8
            refs.append((sid,inst,a,read(r05,a)[0]))
    roots=sorted({a for _,_,a,_ in refs})
    assert len(refs)==84 and len(roots)==72 and roots[0]==0x87AE and roots[-1]==0xBEE8
    assert all(first>=0x10 and inst not in (5,6) for _,inst,_,first in refs)
    current=[(sid,inst,a) for sid,inst,a,_ in refs if SPAN_START<=a<SPAN_END]
    assert current==EXPECTED_REFS
    current_roots=sorted({a for _,_,a in current})
    assert len(current_roots)==19 and current_roots[-1]==0x995F
    rem=[a for a in roots if a>=SPAN_END]
    assert len(rem)==53 and rem[0]==0x9A6B

    def decode(root,inst,hi):
        q=deque([(root,None,None)]); seen=set(); commands=set(); edges=set(); e7=[]; outside=[]; missing=[]; max_read=SPAN_START
        def need_at(pc,n):
            nonlocal max_read
            assert SPAN_START<=pc<hi and pc+n<=hi, f'operand escape pc=${pc:04X} n={n} hi=${hi:04X}'
            max_read=max(max_read,pc+n)
        while q:
            pc,ret,anchor=q.popleft(); state=(pc,ret,anchor)
            if state in seen: continue
            seen.add(state)
            if not (SPAN_START<=pc<hi): outside.append(state); continue
            need_at(pc,1); cmd=read(r05,pc)[0]; commands.add(pc); top,sub=cmd>>4,cmd&0xF; nxt=[]
            if inst==7 and top!=0xF: nxt=[(pc+1,ret,anchor)]
            elif inst!=7 and top!=0xF:
                if top<=0xC: nxt=[(pc+1,ret,anchor)]
                elif top==0xD: need_at(pc,4); nxt=[(pc+4,ret,anchor)]
                elif top==0xE:
                    if sub<=5: nxt=[(pc+1,ret,anchor)]
                    elif sub in (6,7,8,9,10,12,13,14,15):
                        need_at(pc,2)
                        if sub==7: e7.append((pc,read(r05,pc+1)[0]))
                        nxt=[(pc+2,ret,anchor)]
                    elif sub==11:
                        need_at(pc,2); p=read(r05,pc+1)[0]
                        if p==0: nxt=[(pc+2,ret,anchor)]
                        else: need_at(pc,3); nxt=[(pc+3,ret,anchor)]
            if top==0xF:
                if sub<=0xA or sub==0xC: nxt=[(pc+1,ret,anchor)]
                elif sub==0xB: nxt=[(pc+1,ret,pc+1)]
                elif sub==0xD:
                    if ret is None:
                        need_at(pc,3); target=read(r05,pc+1)[0]|read(r05,pc+2)[0]<<8
                        edges.add((pc,'FD-call',target)); nxt=[(target,pc+3,anchor)]
                    else:
                        edges.add((pc,'FD-ret',ret)); nxt=[(ret,None,anchor)]
                elif sub==0xE:
                    need_at(pc,2); p=read(r05,pc+1)[0]
                    if p==0xFF:
                        need_at(pc,4); target=read(r05,pc+2)[0]|read(r05,pc+3)[0]<<8
                        edges.add((pc,'FE-jmp',target)); nxt=[(target,ret,anchor)]
                    else:
                        nxt=[(pc+2,ret,anchor)]
                        if anchor is None: missing.append(pc)
                        else: edges.add((pc,'FE-loop',anchor)); nxt.append((anchor,ret,anchor))
                elif sub==0xF: nxt=[]
            q.extend(nxt)
        return seen,commands,edges,e7,outside,missing,max_read

    states=0; commands=set(); edges=set(); e7=[]; max_read=SPAN_START
    for sid,inst,root in current:
        s,c,ed,ev,o,m,mr=decode(root,inst,SPAN_END)
        assert not o and not m
        states+=len(s); commands|=c; edges|=ed; e7+=ev; max_read=max(max_read,mr)
    assert states==6437 and len(commands)==3992
    assert min(commands)==0x87AE and max(commands)==0x9A67 and max_read==SPAN_END
    counts=Counter(k for _,k,_ in edges)
    assert counts==Counter({'FE-loop':38,'FD-call':26,'FD-ret':26,'FE-jmp':13})
    assert all(SPAN_START<=t<SPAN_END for _,_,t in edges)
    assert set(e7)==EXPECTED_E7
    highs={p>>4 for _,p in e7}; assert highs=={0,5,8} and max(highs)<=9
    for pc,p in set(e7):
        x=(p&0xF0)>>3
        ptr=read(r05,0x8430+x)[0]|read(r05,0x8431+x)[0]<<8
        assert ptr==0x8444

    next_refs=[(sid,inst,a) for sid,inst,a,_ in refs if a==0x9A6B]
    assert next_refs==[(0x53,4,0x9A6B)]
    s,c,ed,ev,o,m,mr=decode(0x9A6B,4,0xC000)
    assert not o and not m and mr==0x9B6A
    assert mr-SPAN_START==5052

    print('ROM identity: OK')
    print('bank $05 parser core identity with audited bank $04: OK; 1965 bytes SHA-256',COMMON_SHA)
    print('bank $05 metadata: 84 references / 72 roots; all alternate-parser mode')
    print('04FB dependency span: $87AE-$9A6A (4797 new bytes), SHA-256',SPAN_SHA)
    print('closed refs/roots: 19/19; sounds: $50 $51 $52 $53')
    print('abstract parser states:',states,'unique commands:',len(commands))
    print('pointer edges:',dict(sorted(counts.items())))
    print('decoded E7 command sites:',len(EXPECTED_E7),'high-nibble domain:',sorted(highs))
    print('all live E7 parameters index in-range $8430-$8443 entries and dispatch to audited $8444')
    print('operand/path/pointer escapes: 0')
    print('remaining bank $05 roots: 53; next root $9A6B')
    print('including next root requires 5052 new bytes through $9B69, so it is deferred')
    print('04FB result: first 19 bank-$05 roots preserve shared ZP $10')

if __name__=='__main__':
    if len(sys.argv)!=2: raise SystemExit('usage: audit_nmi_bank05_prg10_head.py ROM.nes')
    main(sys.argv[1])
