#!/usr/bin/env python3
from __future__ import annotations
import hashlib, sys
from collections import Counter, deque
from pathlib import Path
from audit_nmi_fixed_2c_head import OPS, BR, TERM, WRITE

ROM_SHA="958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
WINDOW_SHA="f3090b53f174f15eeacad0d9e042efd95ff93ed6b4bfd706ba233ee5f588c86a"
OVERLAP_SHA="6966c228f397fb1a390562bc871d382f624397bd65f06bb301774b085e7759d1"
FINGERPRINT_SHA="322b459da91a43e13712821aba143184801a6b9e6c91e0047f9826846a957f24"
T1=(0xF84E,0xF86E,[0xF86E,0xF883,0xF88F,0xF899,0xF8B1,0xF8E9,0xF919,0xF95A,0xF86E,0xF877,0xF88F,0xF899,0xF706,0xF724,0xF782,0xF7B7],"88065baa658136181547132c1ee61481724cba01f76f0f5aed837a91aa06e549")
T2=(0xF96A,0xF97E,[0xF97E,0xF9C2,0xF9D7,0xF9FF,0xFAAA,0xFACA,0xFAF2,0xF9C2,0xF9D7,0xFB37],"9db34975a37e416e832cc543ae63858c0fa17e5a7b0b5f6f6070a96974838aea")
RANGES=[
(0xF706,0xF713,"8745c6e3d3acdd90bf3b1cafaf32f9e981a606070ba5d2b365cace8f56fa3025"),
(0xF724,0xF739,"41cad7c7b722c299f4111083f871fd996a0cfa517bd990d3b37ddce6ac30072e"),
(0xF782,0xF792,"17bbb4663de8e617686c27ab5ad5554a69c0062d9c8bff1d353fd6487028546b"),
(0xF7B7,0xF7CF,"0d93fcf865fdae96f01a0640e3769924b558f1cb0aaa0dbe7d2fedfdf17462be"),
(0xF800,0xFAA0,"6dea651f93c64d59355c4180907677d367bb705ed84cbfa6ec59da79009028a8"),
(0xFAAA,0xFB96,"5d32479e3af38c5477b4a3c076b3c3d0a0bd07f4c572a35a115bd6e347720402")]
MANIFEST="fdc1a53db0ee18ca5e70188d2c8b31d1b350c91d011f72fddb4b6fcb7434984e"
EXPECTED_EDGES=Counter({"jsr_fixed_out":50,"jsr_banked":38,"jmp_banked":5,"jsr_prior":3,"jmp_fixed_out":3,"jmp_prior":2,"branch_prior":1})
W2C=[0xF736,0xF78F,0xF7CC,0xF962,0xFB77]
W68=[0xF706,0xF72F,0xF78D,0xF874,0xF896,0xF8AE,0xF8E6,0xF916,0xF957,0xF9B4,0xF9D0,0xF9FC,0xF9FF,0xFAB7,0xFAD7,0xFB04]
PRIOR=[(0xE366,0xE434),(0xE436,0xE577),(0xE62D,0xE632),(0xE63D,0xE648),(0xE710,0xE718),(0xE7A7,0xE814),(0xE827,0xE831),(0xEB44,0xEB6B),(0xEB82,0xEBF7),(0xF390,0xF3DD),(0xF6AE,0xF6E4),(0xF3DD,0xF6AE),(0xF6E4,0xF706),(0xF713,0xF724),(0xF739,0xF782),(0xF792,0xF7B7),(0xF7CF,0xF800)]
NEW=[(0xF706,0xF713),(0xF724,0xF739),(0xF782,0xF792),(0xF7B7,0xF7CF),(0xF800,0xFC00)]

def inside(a,rs): return any(s<=a<e for s,e in rs)

def main(path):
    rom=Path(path).read_bytes(); assert hashlib.sha256(rom).hexdigest()==ROM_SHA
    prg=rom[16:16+0x40000]; p31=prg[31*0x2000:32*0x2000]
    def rd(a,n=1): assert 0xE000<=a and a+n<=0x10000; return p31[a-0xE000:a-0xE000+n]
    assert hashlib.sha256(rd(0xF800,0x400)).hexdigest()==WINDOW_SHA
    assert hashlib.sha256(rd(0xF7E0,32)).hexdigest()==OVERLAP_SHA
    assert hashlib.sha256(rd(0xF800,32)).hexdigest()==FINGERPRINT_SHA
    tables=[]; table_bytes=set()
    for s,e,want,h in (T1,T2):
        b=rd(s,e-s); got=[b[i]|b[i+1]<<8 for i in range(0,len(b),2)]
        assert got==want and hashlib.sha256(b).hexdigest()==h
        tables+=want; table_bytes.update(range(s,e))
    prior=set(); allowed=set()
    for s,e in PRIOR: prior.update(range(s,e))
    for s,e in NEW: allowed.update(range(s,e))
    dispatch={0xF84B:T1[2],0xF967:T2[2]}
    def dec(pc):
        op=rd(pc)[0]; assert op in OPS, f"unknown ${op:02X} at ${pc:04X}"
        mn,mode,n=OPS[op]; b=rd(pc,n); o=None
        if n==2:
            o=b[1]
            if mode=='rel': o=(pc+2+(o if o<0x80 else o-0x100))&0xFFFF
        elif n==3: o=b[1]|b[2]<<8
        return mn,mode,n,o
    q=deque([0xF800,0xF831,0xF839,0xF841,0xF849,0xF965])
    seen=set(); code=set(); edges=[]; writes=[]
    while q:
        pc=q.popleft()
        if pc in prior: edges.append(("prior",None,pc)); continue
        if pc not in allowed: edges.append(("banked" if pc<0xE000 else "fixed_out",None,pc)); continue
        assert pc not in table_bytes, f"table data decoded as code at ${pc:04X}"
        if pc in seen: continue
        mn,mode,n,o=dec(pc); assert not any(x in table_bytes for x in range(pc,pc+n))
        seen.add(pc); code.update(range(pc,pc+n))
        if mn in WRITE and mode!='acc': writes.append((pc,mn,mode,o))
        nxt=pc+n
        def put(kind,t):
            if t in prior: edges.append((kind+"_prior",pc,t))
            elif t in allowed: q.append(t)
            else: edges.append((kind+("_banked" if t<0xE000 else "_fixed_out"),pc,t))
        if pc in dispatch:
            assert mn=='JSR' and o==0xE7FB
            for t in dispatch[pc]: put('dispatch',t)
            continue
        if mn in TERM: continue
        if mn in BR: put('branch_ft',nxt); put('branch',o)
        elif mn=='JMP': assert mode!='ind'; put('jmp',o)
        elif mn=='JSR': put('jsr',o); put('fallthrough',nxt)
        else: put('fallthrough',nxt)
    assert len(seen)==414
    assert Counter(k for k,_,_ in edges)==EXPECTED_EDGES
    data=set(table_bytes)
    assert rd(0xFB20,14)==bytes.fromhex('a000b931fb9d0003e8c8c006d0f4')
    data.update(range(0xFB31,0xFB37))
    covered=code|data; new=covered-prior
    assert len(new)==982
    a=sorted(new); rr=[]; s=p=a[0]
    for x in a[1:]:
        if x==p+1:p=x
        else:rr.append((s,p+1));s=p=x
    rr.append((s,p+1)); assert [(s,e) for s,e in rr]==[(s,e) for s,e,_ in RANGES]
    blob=b''
    for s,e,h in RANGES:
        b=rd(s,e-s); assert hashlib.sha256(b).hexdigest()==h; blob+=b
    assert len(blob)==982 and hashlib.sha256(blob).hexdigest()==MANIFEST
    assert len(writes)==82
    assert not [w for w in writes if w[2] in ('zp','abs') and w[3]==0x10]
    indexed=[w for w in writes if w[2] in ('zpx','zpy','indx','indy','absx','absy')]
    assert len(indexed)==9 and all(w[2] in ('absx','absy') and w[3]>=0x0300 for w in indexed)
    assert sorted(pc for pc,m,mode,o in writes if mode=='zp' and o==0x2C)==W2C
    w68=sorted((pc,m) for pc,m,mode,o in writes if mode=='zp' and o==0x68)
    assert [pc for pc,m in w68]==W68 and all(m=='INC' for pc,m in w68)
    print('ROM identity: OK')
    print('0500 recovery window/fingerprint: OK')
    print('secondary $68 tables: 16 + 10 encoded pointers; producer bounds NOT inferred')
    print('04FF gaps admitted by table #1: $F706 $F724 $F782 $F7B7')
    print('required 04FF fallthrough root $F800: included')
    print('instruction starts 414; exact genuinely new semantic bytes 982')
    print('manifest',MANIFEST)
    print('ZP $10 aliasing writes: 0')
    print('$2C mutations:', ' '.join(f'${x:04X}' for x in W2C))
    print('$68 mutations:', ' '.join(f'${x:04X}' for x in W68), '(all INC)')
    print('IMPORTANT: complete live $68/$2C producer domains remain open')

if __name__=='__main__':
    if len(sys.argv)!=2: raise SystemExit('usage: audit_nmi_fixed_68_dispatch.py ROM.nes')
    main(sys.argv[1])
