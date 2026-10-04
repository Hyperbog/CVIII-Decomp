#!/usr/bin/env python3
from __future__ import annotations
import hashlib, sys
from collections import Counter, deque
from pathlib import Path

ROM_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
SPAN_START,SPAN_END=0x9A6B,0xAD97
SPAN_SHA='3d34329fd18b7c713f1fe35206868f1b6c0bdfb6127f664410a60fd54a8c46f0'
COMMON_START,COMMON_END=0x8001,0x87AE
COMMON_SHA='e2c3ff3d7e9f96b598610a8028f5b92a606fac7f9acb2977811146fa145fdb67'
META_TABLE,META_COUNT=0x8F60,0x7D
EXPECTED_REFS=[
(0x53,0,0x9BD8),(0x53,1,0x9CF4),(0x53,2,0x9D21),(0x53,4,0x9A6B),(0x53,7,0x9B6A),
(0x54,0,0x9F46),(0x54,1,0xA01E),(0x54,2,0xA05B),(0x54,3,0x9D99),(0x54,4,0x9E36),(0x54,7,0xA118),
(0x55,0,0xA3BA),(0x55,1,0xA506),(0x55,2,0xA658),(0x55,3,0xA119),(0x55,4,0xA252),(0x55,7,0xA6FB),
(0x56,0,0xA918),(0x56,1,0xA9D6),(0x56,2,0xAA90),(0x56,3,0xA6FC),(0x56,4,0xA7B3),(0x56,7,0xA86D),
(0x57,3,0xAB65),(0x57,4,0xAC55),
(0x5C,0,0xA918),(0x5C,1,0xA9D6),(0x5C,2,0xAA90),(0x5C,3,0xA6FC),(0x5C,4,0xA7B3),(0x5C,7,0xA86D),
]
EXPECTED_E7={(0x9F5C,0x09),(0xA950,0x0E),(0xAA13,0x0D)}

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
    assert len(span)==4908 and hashlib.sha256(span).hexdigest()==SPAN_SHA

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
    assert len(current)==31 and len(current_roots)==25
    assert current_roots[0]==0x9A6B and current_roots[-1]==0xAC55
    rem=[a for a in roots if a>=SPAN_END]
    assert len(rem)==28 and rem[0]==0xAD97

    def decode(root,inst,lo,hi):
        q=deque([(root,None,None)]); seen=set(); commands=set(); edges=set(); e7=[]; outside=[]; missing=[]; max_read=lo
        def need_at(pc,n):
            nonlocal max_read
            assert lo<=pc<hi and pc+n<=hi, f'operand escape pc=${pc:04X} n={n} span=${lo:04X}-${hi-1:04X}'
            max_read=max(max_read,pc+n)
        while q:
            pc,ret,anchor=q.popleft(); state=(pc,ret,anchor)
            if state in seen: continue
            seen.add(state)
            if not (lo<=pc<hi): outside.append(state); continue
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
        s,c,ed,ev,o,m,mr=decode(root,inst,SPAN_START,SPAN_END)
        assert not o and not m
        states+=len(s); commands|=c; edges|=ed; e7+=ev; max_read=max(max_read,mr)
    assert states==7105 and len(commands)==4221
    assert min(commands)==0x9A6B and max(commands)==0xAD96 and max_read==SPAN_END
    counts=Counter(k for _,k,_ in edges)
    assert counts==Counter({'FE-loop':56,'FE-jmp':23,'FD-call':22,'FD-ret':22})
    assert all(SPAN_START<=t<SPAN_END for _,_,t in edges)
    assert set(e7)==EXPECTED_E7
    assert [a for a in range(SPAN_START,SPAN_END) if read(r05,a)[0]==0xE7]==[0x9F5C,0xA950,0xAA13]
    highs={p>>4 for _,p in e7}; assert highs=={0}
    for pc,p in set(e7):
        x=(p&0xF0)>>3
        ptr=read(r05,0x8430+x)[0]|read(r05,0x8431+x)[0]<<8
        assert ptr==0x8444

    next_refs=[(sid,inst,a) for sid,inst,a,_ in refs if a==0xAD97]
    assert next_refs==[(0x57,7,0xAD97)]
    s,c,ed,ev,o,m,mr=decode(0xAD97,7,0xAD97,0xC000)
    assert not o and not m and mr==0xAE2E
    assert mr-SPAN_START==5059

    print('ROM identity: OK')
    print('bank $05 common parser core identity: OK; 1965 bytes SHA-256',COMMON_SHA)
    print('bank $05 metadata: 84 references / 72 roots; all alternate-parser mode')
    print('04FC dependency span: $9A6B-$AD96 (4908 new bytes), SHA-256',SPAN_SHA)
    print('closed refs/roots: 31/25; sounds: $53 $54 $55 $56 $57 $5C')
    print('abstract parser states:',states,'unique commands:',len(commands))
    print('pointer edges:',dict(sorted(counts.items())))
    print('unique decoded E7 sites:',[(f'${pc:04X}',f'${p:02X}') for pc,p in sorted(set(e7))])
    print('live E7 high-nibble domain: $0; all dispatch through in-range table entry to audited $8444')
    print('operand/path/pointer escapes: 0')
    print('cumulative bank $05 roots closed: 44/72; remaining 28; next root $AD97')
    print('including next root requires 5059 new bytes through $AE2D, so it is deferred')
    print('04FC result: next 25 bank-$05 roots preserve shared ZP $10')

if __name__=='__main__':
    if len(sys.argv)!=2: raise SystemExit('usage: audit_nmi_bank05_prg10_mid.py ROM.nes')
    main(sys.argv[1])
