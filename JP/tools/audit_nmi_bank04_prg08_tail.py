#!/usr/bin/env python3
"""Checkpoint 04F8 repair: enforce operand-in-span bounds for bank $04 streams."""
from __future__ import annotations
import hashlib, sys
from collections import deque
from pathlib import Path

ROM_SHA = '958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
SPAN_START, SPAN_END = 0x920A, 0xA014  # exclusive; includes $A010 FE FF operands through $A013
SPAN_SHA = '728c86cd808e178821f7f72d1f0371eb16a5bde3a1dda495543338391a5e7b3c'
META_TABLE, META_COUNT = 0x8F60, 0x7D
PREV_ROOT_CUTOFF = 0x920A
PREV_SEMANTIC_END = 0x920C  # includes operands $920A-$920B for command at $9208

EXPECTED_ROOTS = [0x920C,0x92DB,0x93FA,0x95E3,0x967E,0x974D,0x9900,0x99E9,0x9BAF,0x9D21,0x9E85]
EXPECTED_REFS = [
    (0x5D,7,0x920C),(0x5E,0,0x967E),(0x5E,1,0x974D),(0x5E,2,0x9900),
    (0x5E,3,0x92DB),(0x5E,4,0x93FA),(0x5E,7,0x95E3),(0x60,0,0x9E85),
    (0x60,3,0x99E9),(0x60,4,0x9BAF),(0x60,7,0x9D21),
]
PREV_ROOTS = [
    0x87AE,0x87CD,0x87E9,0x87FE,0x880C,0x8818,0x8865,0x887F,0x88A5,0x88C5,0x88DF,
    0x8904,0x8997,0x8A60,0x8B16,0x8B5D,0x8C8B,0x8D53,0x8E05,0x8ED0,0x8F9F,0x9040,0x9133,
]

def main(path: str) -> None:
    rom=Path(path).read_bytes()
    assert hashlib.sha256(rom).hexdigest()==ROM_SHA
    prg=rom[16:16+0x40000]
    raw04=prg[8*0x2000:10*0x2000]
    raw0c=prg[24*0x2000:26*0x2000]

    def r04(a:int,n:int=1)->bytes:
        assert 0x8000<=a<0xC000 and a+n<=0xC000
        return raw04[a-0x8000:a-0x8000+n]
    def r0c(a:int,n:int=1)->bytes:
        assert 0x8000<=a<0xC000 and a+n<=0xC000
        return raw0c[a-0x8000:a-0x8000+n]

    span=r04(SPAN_START,SPAN_END-SPAN_START)
    assert len(span)==3594
    assert hashlib.sha256(span).hexdigest()==SPAN_SHA
    assert r04(0x9208,4)==bytes.fromhex('feff3391')
    assert r04(0xA010,4)==bytes.fromhex('feff859e')

    assert r04(0x8001,0x87AE-0x8001)==r0c(0x8001,0x87AE-0x8001)

    ptrs=[]
    for sid in range(1,META_COUNT+1):
        b=r0c(META_TABLE+(sid-1)*2,2)
        ptrs.append(b[0]|(b[1]<<8))
    refs=[]
    for sid,ptr in enumerate(ptrs,1):
        if r0c(ptr)[0]!=0x04: continue
        nminus=r0c(ptr+1)[0]
        rec=r0c(ptr,2+3*(nminus+1))
        for j in range(nminus+1):
            inst=rec[2+3*j]
            addr=rec[3+3*j]|(rec[4+3*j]<<8)
            refs.append((sid,inst,addr,r04(addr)[0]))

    roots=sorted({a for _,_,a,_ in refs})
    assert len(refs)==102 and len(roots)==96
    assert all(first>=0x10 and inst not in (5,6) for _,inst,_,first in refs)

    current=[(sid,inst,a) for sid,inst,a,_ in refs if 0x920A<=a<0xA000]
    assert current==EXPECTED_REFS
    assert sorted({a for _,_,a in current})==EXPECTED_ROOTS
    overlap={a for _,_,a in current}
    assert len(overlap)==11
    assert len(span)-len(overlap)==3583
    remaining=[r for r in roots if r>=SPAN_END]
    assert len(remaining)==62 and remaining[0]==0xA014

    def decode(root:int,inst:int,lo:int,hi:int):
        q=deque([(root,None,None)])
        seen=set(); commands=set(); edges=set(); e7=[]; outside=[]; missing_anchor=[]

        def need(pc:int,n:int)->None:
            assert lo<=pc<hi and pc+n<=hi, (
                f'command/operand escapes accounted span: pc=${pc:04X} len={n} span=${lo:04X}-${hi-1:04X}'
            )

        while q:
            pc,ret,anchor=q.popleft()
            state=(pc,ret,anchor)
            if state in seen: continue
            seen.add(state)
            if not (lo<=pc<hi):
                outside.append(state); continue

            need(pc,1)
            cmd=r04(pc)[0]
            commands.add(pc)
            top=cmd>>4; sub=cmd&0x0F
            nxt=[]

            if inst==7 and top!=0xF:
                nxt=[(pc+1,ret,anchor)]
            elif inst!=7 and top!=0xF:
                if top<=0xC:
                    nxt=[(pc+1,ret,anchor)]
                elif top==0xD:
                    need(pc,4)
                    nxt=[(pc+4,ret,anchor)]
                elif top==0xE:
                    if sub<=5:
                        nxt=[(pc+1,ret,anchor)]
                    elif sub in (6,7,8,9,10,12,13,14,15):
                        need(pc,2)
                        if sub==7: e7.append(pc)
                        nxt=[(pc+2,ret,anchor)]
                    elif sub==11:
                        need(pc,2)
                        p=r04(pc+1)[0]
                        if p==0:
                            nxt=[(pc+2,ret,anchor)]
                        else:
                            need(pc,3)
                            nxt=[(pc+3,ret,anchor)]

            if top==0xF:
                if sub<=0xA or sub==0xC:
                    nxt=[(pc+1,ret,anchor)]
                elif sub==0xB:
                    nxt=[(pc+1,ret,pc+1)]
                elif sub==0xD:
                    if ret is None:
                        need(pc,3)
                        target=r04(pc+1)[0]|(r04(pc+2)[0]<<8)
                        edges.add((pc,'FD-call',target))
                        nxt=[(target,pc+3,anchor)]
                    else:
                        edges.add((pc,'FD-ret',ret))
                        nxt=[(ret,None,anchor)]
                elif sub==0xE:
                    need(pc,2)
                    p=r04(pc+1)[0]
                    if p==0xFF:
                        need(pc,4)
                        target=r04(pc+2)[0]|(r04(pc+3)[0]<<8)
                        edges.add((pc,'FE-jmp',target))
                        nxt=[(target,ret,anchor)]
                    else:
                        nxt=[(pc+2,ret,anchor)]
                        if anchor is None:
                            missing_anchor.append(pc)
                        else:
                            edges.add((pc,'FE-loop',anchor))
                            nxt.append((anchor,ret,anchor))
                elif sub==0xF:
                    nxt=[]

            q.extend(nxt)
        return seen,commands,edges,e7,outside,missing_anchor

    prev_refs=[(sid,inst,a) for sid,inst,a,_ in refs if a<PREV_ROOT_CUTOFF]
    assert sorted({a for _,_,a in prev_refs})==PREV_ROOTS
    prev_commands=set(); prev_edges=set(); prev_states=0
    for _,inst,root in prev_refs:
        seen,cmds,edges,e7,out,missing=decode(root,inst,0x87AE,PREV_SEMANTIC_END)
        assert not e7 and not out and not missing
        prev_states+=len(seen); prev_commands|=cmds; prev_edges|=edges
    assert prev_states==2819 and len(prev_commands)==2169
    assert max(prev_commands)==0x9208
    assert (0x9208,'FE-jmp',0x9133) in prev_edges
    assert all(0x87AE<=target<PREV_SEMANTIC_END for _,_,target in prev_edges)

    all_commands=set(); all_edges=set(); total_states=0
    for _,inst,root in current:
        seen,cmds,edges,e7,out,missing=decode(root,inst,SPAN_START,SPAN_END)
        assert not e7 and not out and not missing
        total_states+=len(seen); all_commands|=cmds; all_edges|=edges
    assert min(all_commands)==0x920C and max(all_commands)==0xA010
    assert len(all_commands)==3025 and total_states==3312
    assert (0xA010,'FE-jmp',0x9E85) in all_edges
    assert all(SPAN_START<=target<SPAN_END for _,_,target in all_edges)
    assert not [a for a in range(SPAN_START,SPAN_END) if r04(a)[0]==0xE7]

    print('ROM identity: OK')
    print('strict operand-in-span checks: OK')
    print('04F7 affected cycle: $9208 FE FF 33 91 -> $9133, operands through $920B accounted')
    print('04F7 prior roots:',len(PREV_ROOTS),'states:',prev_states,'commands:',len(prev_commands),'decoded E7: 0')
    print('corrected 04F8 dependency span: $920A-$A013 (3594 bytes), SHA-256',SPAN_SHA)
    print('11 bytes overlap 04F7 root probes; corrected exact new-byte footprint: 3583')
    print('04F8 affected cycle: $A010 FE FF 85 9E -> $9E85, operands through $A013 accounted')
    print('04F8 roots:',len(EXPECTED_ROOTS),'states:',total_states,'commands:',len(all_commands),'decoded E7: 0')
    print('all FD/FE pointer targets stay inside their accounted semantic spans')
    print('corrected next unresolved root/frontier: $A014')
    print('04F8 repair result: 34/96 bank-$04 roots remain closed and ZP $10-safe; forward work may resume at $A014')

if __name__=='__main__':
    if len(sys.argv)!=2:
        raise SystemExit(f'usage: {Path(sys.argv[0]).name} ROM.nes')
    main(sys.argv[1])
