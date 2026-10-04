#!/usr/bin/env python3
from __future__ import annotations
import hashlib, sys
from collections import Counter, deque
from pathlib import Path
from audit_nmi_fixed_2c_head import OPS, BR, TERM, WRITE

ROM_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
WINDOW=(0xF800,0xFC00,'f3090b53f174f15eeacad0d9e042efd95ff93ed6b4bfd706ba233ee5f588c86a')
GAPS=[(0xF706,0xF713),(0xF724,0xF739),(0xF782,0xF792),(0xF7B7,0xF7CF)]
NEW=[WINDOW[:2],*GAPS]
PRIOR=[(0xF3DD,0xF706),(0xF713,0xF724),(0xF739,0xF782),(0xF792,0xF7B7),(0xF7CF,0xF800)]
T1=(0xF84E,0xF86E,[0xF86E,0xF883,0xF88F,0xF899,0xF8B1,0xF8E9,0xF919,0xF95A,0xF86E,0xF877,0xF88F,0xF899,0xF706,0xF724,0xF782,0xF7B7],'88065baa658136181547132c1ee61481724cba01f76f0f5aed837a91aa06e549')
T2=(0xF96A,0xF97E,[0xF97E,0xF9C2,0xF9D7,0xF9FF,0xFAAA,0xFACA,0xFAF2,0xF9C2,0xF9D7,0xFB37],'9db34975a37e416e832cc543ae63858c0fa17e5a7b0b5f6f6070a96974838aea')
RANGES=[
(0xF706,0xF713,'8745c6e3d3acdd90bf3b1cafaf32f9e981a606070ba5d2b365cace8f56fa3025'),
(0xF724,0xF739,'41cad7c7b722c299f4111083f871fd996a0cfa517bd990d3b37ddce6ac30072e'),
(0xF782,0xF792,'17bbb4663de8e617686c27ab5ad5554a69c0062d9c8bff1d353fd6487028546b'),
(0xF7B7,0xF7CF,'0d93fcf865fdae96f01a0640e3769924b558f1cb0aaa0dbe7d2fedfdf17462be'),
(0xF831,0xFAA0,'eb0859ea4906556aa18192c14d446c9968b56eda1d0d27ad70138f292d9cd9fe'),
(0xFAAA,0xFB96,'5d32479e3af38c5477b4a3c076b3c3d0a0bd07f4c572a35a115bd6e347720402')]
MANIFEST='a4ae2796d32ef639940c58f0160af79b8eab8cf80347a998af0ae9c4bab3e44a'
EDGES=Counter({('fallthrough','new'):359,('jsr','fixed_out'):45,('jsr','banked'):32,('branch','new'):29,('jmp','banked'):5,('jmp','fixed_out'):3,('dispatch','fixed_out'):2,('jsr','prior'):2,('jmp','prior'):2,('jsr','new'):2,('jmp','new'):2,('branch','prior'):1})
W2C=[0xF736,0xF78F,0xF7CC,0xF962,0xFB77]
W68=[0xF706,0xF72F,0xF78D,0xF874,0xF896,0xF8AE,0xF8E6,0xF916,0xF957,0xF9B4,0xF9D0,0xF9FC,0xF9FF,0xFAB7,0xFAD7,0xFB04]

def inside(a,rs): return any(s<=a<e for s,e in rs)

def main(path):
    rom=Path(path).read_bytes(); assert hashlib.sha256(rom).hexdigest()==ROM_SHA
    prg=rom[16:16+0x40000]; p31=prg[31*0x2000:32*0x2000]
    def rd(a,n=1): assert 0xE000<=a and a+n<=0x10000; return p31[a-0xE000:a-0xE000+n]
    assert hashlib.sha256(rd(WINDOW[0],0x400)).hexdigest()==WINDOW[2]
    assert hashlib.sha256(rd(0xF7E0,32)).hexdigest()=='6966c228f397fb1a390562bc871d382f624397bd65f06bb301774b085e7759d1'
    assert hashlib.sha256(rd(0xF800,32)).hexdigest()=='322b459da91a43e13712821aba143184801a6b9e6c91e0047f9826846a957f24'
    tables=[]
    for s,e,want,h in (T1,T2):
        b=rd(s,e-s); got=[b[i]|b[i+1]<<8 for i in range(0,len(b),2)]
        assert got==want and hashlib.sha256(b).hexdigest()==h; tables+=want
    assert rd(0xFB20,14)==bytes.fromhex('a000b931fb9d0003e8c8c006d0f4')
    assert hashlib.sha256(rd(0xFB31,6)).hexdigest()=='92e4f972206296cbd33f41e211a71edf949a5c4fd5c5f03e9d530f7cd3f78165'
    def dec(pc):
        op=rd(pc)[0]; assert op in OPS, f'unknown ${op:02X} at ${pc:04X}'
        mn,mode,n=OPS[op]; assert all(inside(x,NEW) for x in range(pc,pc+n)), f'operand escape ${pc:04X}'
        b=rd(pc,n); o=None
        if n==2:
            o=b[1]
            if mode=='rel': o=(pc+2+(o if o<0x80 else o-0x100))&0xFFFF
        elif n==3: o=b[1]|b[2]<<8
        return mn,mode,n,o
    q=deque([0xF831,0xF839,0xF841,0xF849,0xF965]+sorted(set(tables)))
    seen=set(); code=set(); edges=[]; writes=[]
    while q:
        pc=q.popleft()
        if pc in seen or not inside(pc,NEW): continue
        mn,mode,n,o=dec(pc); seen.add(pc); code.update(range(pc,pc+n))
        if mn in WRITE and mode!='acc': writes.append((pc,mn,mode,o))
        if mn=='JSR' and o==0xE7FB: edges.append(('dispatch',pc,o,'fixed_out')); continue
        nxt=pc+n
        def put(k,t):
            c='new' if inside(t,NEW) else ('prior' if inside(t,PRIOR) else ('fixed_out' if t>=0xE000 else 'banked'))
            edges.append((k,pc,t,c)); q.append(t) if c=='new' else None
        if mn in TERM: continue
        if mn in BR: put('fallthrough',nxt); put('branch',o)
        elif mn=='JMP': put('jmp',o) if mode!='ind' else edges.append(('jmp_ind',pc,o,'indirect'))
        elif mn=='JSR': put('fallthrough',nxt); put('jsr',o)
        else: put('fallthrough',nxt)
    assert len(seen)==395 and len(code)==875
    data=set(range(T1[0],T1[1]))|set(range(T2[0],T2[1]))|set(range(0xFB31,0xFB37))
    assert len(data)==58 and not code&data
    cov=code|data; assert len(cov)==933
    a=sorted(cov); rr=[]; s=p=a[0]
    for x in a[1:]:
        if x==p+1:p=x
        else:rr.append((s,p+1));s=p=x
    rr.append((s,p+1)); assert [(s,e) for s,e in rr]==[(s,e) for s,e,_ in RANGES]
    blob=b''
    for s,e,h in RANGES:
        b=rd(s,e-s); assert hashlib.sha256(b).hexdigest()==h; blob+=b
    assert hashlib.sha256(blob).hexdigest()==MANIFEST and len(blob)==933
    assert Counter((k,c) for k,pc,t,c in edges if k!='jmp_ind')==EDGES
    assert not [w for w in writes if w[2] in ('zp','abs') and w[3]==0x10]
    assert not [w for w in writes if w[2] in ('zpx','zpy','indx','indy')]
    assert all(0x0300<=w[3]<=0x057C for w in writes if w[2] in ('absx','absy'))
    assert sorted(pc for pc,m,mode,o in writes if mode=='zp' and o==0x2C)==W2C
    w68=[(pc,m) for pc,m,mode,o in writes if mode=='zp' and o==0x68]
    assert sorted(pc for pc,m in w68)==W68 and all(m=='INC' for pc,m in w68)
    print('ROM identity: OK')
    print('secondary $68 tables: 16 + 10 encoded pointers; producer bounds NOT inferred')
    print('04FF gaps admitted by table #1: $F706 $F724 $F782 $F7B7')
    print('instruction starts 395; code bytes 875; explicit data bytes 58')
    print('0500 genuinely new semantic bytes 933; manifest',MANIFEST)
    print('ZP $10 aliasing writes: 0')
    print('$2C mutations:', ' '.join(f'${x:04X}' for x in W2C))
    print('$68 mutations:', ' '.join(f'${x:04X}' for x in W68), '(all INC)')

if __name__=='__main__':
    if len(sys.argv)!=2: raise SystemExit('usage: audit_nmi_fixed_68_dispatch.py ROM.nes')
    main(sys.argv[1])
