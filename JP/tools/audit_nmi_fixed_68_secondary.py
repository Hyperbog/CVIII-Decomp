#!/usr/bin/env python3
from __future__ import annotations
import hashlib, sys
from collections import Counter, deque
from pathlib import Path

ROM_SHA="958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
WINDOW_SHA="f3090b53f174f15eeacad0d9e042efd95ff93ed6b4bfd706ba233ee5f588c86a"
OVERLAP_SHA="6966c228f397fb1a390562bc871d382f624397bd65f06bb301774b085e7759d1"
FINGERPRINT_SHA="322b459da91a43e13712821aba143184801a6b9e6c91e0047f9826846a957f24"

T1_START,T1_COUNT=0xF84E,16
T1_SHA="88065baa658136181547132c1ee61481724cba01f76f0f5aed837a91aa06e549"
T1_TARGETS=[0xF86E,0xF883,0xF88F,0xF899,0xF8B1,0xF8E9,0xF919,0xF95A,
            0xF86E,0xF877,0xF88F,0xF899,0xF706,0xF724,0xF782,0xF7B7]
T2_START,T2_COUNT=0xF96A,10
T2_SHA="9db34975a37e416e832cc543ae63858c0fa17e5a7b0b5f6f6070a96974838aea"
T2_TARGETS=[0xF97E,0xF9C2,0xF9D7,0xF9FF,0xFAAA,0xFACA,0xFAF2,0xF9C2,0xF9D7,0xFB37]

EXPECTED_RANGES=[
 (0xF706,0xF713,"8745c6e3d3acdd90bf3b1cafaf32f9e981a606070ba5d2b365cace8f56fa3025"),
 (0xF724,0xF739,"41cad7c7b722c299f4111083f871fd996a0cfa517bd990d3b37ddce6ac30072e"),
 (0xF782,0xF792,"17bbb4663de8e617686c27ab5ad5554a69c0062d9c8bff1d353fd6487028546b"),
 (0xF7B7,0xF7CF,"0d93fcf865fdae96f01a0640e3769924b558f1cb0aaa0dbe7d2fedfdf17462be"),
 (0xF800,0xFAA0,"6dea651f93c64d59355c4180907677d367bb705ed84cbfa6ec59da79009028a8"),
 (0xFAAA,0xFB96,"5d32479e3af38c5477b4a3c076b3c3d0a0bd07f4c572a35a115bd6e347720402"),
]
MANIFEST_SHA="fdc1a53db0ee18ca5e70188d2c8b31d1b350c91d011f72fddb4b6fcb7434984e"
EXPECTED_EDGES=Counter({
 "jsr_fixed_out":50,"jsr_banked":38,"jmp_banked":5,
 "jsr_prior":3,"jmp_fixed_out":3,"jmp_prior":2,"branch_prior":1})
EXPECTED_2C=[0xF736,0xF78F,0xF7CC,0xF962,0xFB77]
EXPECTED_68=[0xF706,0xF72F,0xF78D,0xF874,0xF896,0xF8AE,0xF8E6,0xF916,
             0xF957,0xF9B4,0xF9D0,0xF9FC,0xF9FF,0xFAB7,0xFAD7,0xFB04]

OPS={}
def add(o,m,mode,n): OPS[int(o,16)]=(m,mode,n)
TABLE="""00 BRK imp 1
01 ORA indx 2
05 ORA zp 2
06 ASL zp 2
08 PHP imp 1
09 ORA imm 2
0A ASL acc 1
0D ORA abs 3
0E ASL abs 3
10 BPL rel 2
11 ORA indy 2
15 ORA zpx 2
16 ASL zpx 2
18 CLC imp 1
19 ORA absy 3
1D ORA absx 3
1E ASL absx 3
20 JSR abs 3
21 AND indx 2
24 BIT zp 2
25 AND zp 2
26 ROL zp 2
28 PLP imp 1
29 AND imm 2
2A ROL acc 1
2C BIT abs 3
2D AND abs 3
2E ROL abs 3
30 BMI rel 2
31 AND indy 2
35 AND zpx 2
36 ROL zpx 2
38 SEC imp 1
39 AND absy 3
3D AND absx 3
3E ROL absx 3
40 RTI imp 1
41 EOR indx 2
45 EOR zp 2
46 LSR zp 2
48 PHA imp 1
49 EOR imm 2
4A LSR acc 1
4C JMP abs 3
4D EOR abs 3
4E LSR abs 3
50 BVC rel 2
51 EOR indy 2
55 EOR zpx 2
56 LSR zpx 2
58 CLI imp 1
59 EOR absy 3
5D EOR absx 3
5E LSR absx 3
60 RTS imp 1
61 ADC indx 2
65 ADC zp 2
66 ROR zp 2
68 PLA imp 1
69 ADC imm 2
6A ROR acc 1
6C JMP ind 3
6D ADC abs 3
6E ROR abs 3
70 BVS rel 2
71 ADC indy 2
75 ADC zpx 2
76 ROR zpx 2
78 SEI imp 1
79 ADC absy 3
7D ADC absx 3
7E ROR absx 3
81 STA indx 2
84 STY zp 2
85 STA zp 2
86 STX zp 2
88 DEY imp 1
8A TXA imp 1
8C STY abs 3
8D STA abs 3
8E STX abs 3
90 BCC rel 2
91 STA indy 2
94 STY zpx 2
95 STA zpx 2
96 STX zpy 2
98 TYA imp 1
99 STA absy 3
9A TXS imp 1
9D STA absx 3
A0 LDY imm 2
A1 LDA indx 2
A2 LDX imm 2
A4 LDY zp 2
A5 LDA zp 2
A6 LDX zp 2
A8 TAY imp 1
A9 LDA imm 2
AA TAX imp 1
AC LDY abs 3
AD LDA abs 3
AE LDX abs 3
B0 BCS rel 2
B1 LDA indy 2
B4 LDY zpx 2
B5 LDA zpx 2
B6 LDX zpy 2
B8 CLV imp 1
B9 LDA absy 3
BA TSX imp 1
BC LDY absx 3
BD LDA absx 3
BE LDX absy 3
C0 CPY imm 2
C1 CMP indx 2
C4 CPY zp 2
C5 CMP zp 2
C6 DEC zp 2
C8 INY imp 1
C9 CMP imm 2
CA DEX imp 1
CC CPY abs 3
CD CMP abs 3
CE DEC abs 3
D0 BNE rel 2
D1 CMP indy 2
D5 CMP zpx 2
D6 DEC zpx 2
D8 CLD imp 1
D9 CMP absy 3
DD CMP absx 3
DE DEC absx 3
E0 CPX imm 2
E1 SBC indx 2
E4 CPX zp 2
E5 SBC zp 2
E6 INC zp 2
E8 INX imp 1
E9 SBC imm 2
EA NOP imp 1
EC CPX abs 3
ED SBC abs 3
EE INC abs 3
F0 BEQ rel 2
F1 SBC indy 2
F5 SBC zpx 2
F6 INC zpx 2
F8 SED imp 1
F9 SBC absy 3
FD SBC absx 3
FE INC absx 3"""
for line in TABLE.splitlines():
    o,m,mode,n=line.split(); add(o,m,mode,int(n))
BR={"BPL","BMI","BVC","BVS","BCC","BCS","BNE","BEQ"}
TERM={"RTS","RTI","BRK"}
WRITE={"STA","STX","STY","INC","DEC","ASL","LSR","ROL","ROR"}

PRIOR_RANGES=[
 (0xE366,0xE434),(0xE436,0xE577),(0xE62D,0xE632),(0xE63D,0xE648),
 (0xE710,0xE718),(0xE7A7,0xE814),(0xE827,0xE831),(0xEB44,0xEB6B),
 (0xEB82,0xEBF7),(0xF390,0xF3DD),(0xF6AE,0xF6E4),
 (0xF3DD,0xF6AE),(0xF6E4,0xF706),(0xF713,0xF724),(0xF739,0xF782),
 (0xF792,0xF7B7),(0xF7CF,0xF800),
]
NEW_WINDOWS=[(0xF706,0xF713),(0xF724,0xF739),(0xF782,0xF792),(0xF7B7,0xF7CF),(0xF800,0xFC00)]

def main(path:str)->None:
    rom=Path(path).read_bytes()
    assert hashlib.sha256(rom).hexdigest()==ROM_SHA
    prg=rom[16:16+0x40000]
    assert len(prg)==0x40000
    fixed=prg[31*0x2000:32*0x2000]
    def rd(a,n=1):
        assert 0xE000<=a and a+n<=0x10000
        return fixed[a-0xE000:a-0xE000+n]
    assert hashlib.sha256(rd(0xF800,0x400)).hexdigest()==WINDOW_SHA
    assert hashlib.sha256(rd(0xF7E0,32)).hexdigest()==OVERLAP_SHA
    assert hashlib.sha256(rd(0xF800,32)).hexdigest()==FINGERPRINT_SHA

    def getptrs(s,count):
        b=rd(s,2*count)
        return [b[i]|b[i+1]<<8 for i in range(0,len(b),2)]
    assert hashlib.sha256(rd(T1_START,32)).hexdigest()==T1_SHA
    assert getptrs(T1_START,T1_COUNT)==T1_TARGETS
    assert hashlib.sha256(rd(T2_START,20)).hexdigest()==T2_SHA
    assert getptrs(T2_START,T2_COUNT)==T2_TARGETS

    prior=set()
    for s,e in PRIOR_RANGES: prior.update(range(s,e))
    allowed=set()
    for s,e in NEW_WINDOWS: allowed.update(range(s,e))
    table_bytes=set(range(T1_START,T1_START+32))|set(range(T2_START,T2_START+20))
    table_targets={0xF84B:T1_TARGETS,0xF967:T2_TARGETS}

    def dec(pc):
        op=rd(pc)[0]
        assert op in OPS, f"unknown opcode ${op:02X} at ${pc:04X}"
        mn,mode,n=OPS[op]
        raw=rd(pc,n); operand=None
        if n==2:
            operand=raw[1]
            if mode=="rel":
                off=operand if operand<0x80 else operand-0x100
                operand=(pc+2+off)&0xFFFF
        elif n==3:
            operand=raw[1]|raw[2]<<8
        return mn,mode,n,operand

    roots=[0xF800,0xF831,0xF839,0xF841,0xF849,0xF965]
    q=deque(roots); seen=set(); inst={}; edges=[]
    while q:
        pc=q.popleft()
        if pc in prior:
            edges.append(("prior",None,pc)); continue
        if pc not in allowed:
            edges.append(("banked" if pc<0xE000 else "fixed_out",None,pc)); continue
        assert pc not in table_bytes, f"table data decoded as code at ${pc:04X}"
        if pc in seen: continue
        mn,mode,n,operand=dec(pc)
        assert not any(b in table_bytes for b in range(pc,pc+n))
        seen.add(pc); inst[pc]=(mn,mode,n,operand)
        nxt=pc+n
        def put(kind,t):
            if t in prior: edges.append((kind+"_prior",pc,t))
            elif t in allowed: q.append(t)
            else: edges.append((kind+("_banked" if t<0xE000 else "_fixed_out"),pc,t))
        if pc in table_targets:
            assert mn=="JSR" and operand==0xE7FB
            for t in table_targets[pc]: put("dispatch",t)
            continue
        if mn in TERM: continue
        if mn in BR:
            put("branch_ft",nxt); put("branch",operand)
        elif mn=="JMP":
            assert mode!="ind"
            put("jmp",operand)
        elif mn=="JSR":
            put("jsr",operand); put("fallthrough",nxt)
        else:
            put("fallthrough",nxt)

    assert len(seen)==414
    ec=Counter(k for k,_,_ in edges)
    assert ec==EXPECTED_EDGES, ec

    covered=set(table_bytes)
    for pc,(mn,mode,n,operand) in inst.items():
        covered.update(range(pc,pc+n))

    # FB31-FB36 is a six-byte ROM data record read by the bounded Y=0..5 loop at FB20-FB2C.
    assert rd(0xFB20,14)==bytes.fromhex("a000b931fb9d0003e8c8c006d0f4")
    data_record=set(range(0xFB31,0xFB37))
    covered |= data_record

    new=covered-prior
    assert len(new)==982

    arr=sorted(new); ranges=[]; s=p=arr[0]
    for a in arr[1:]:
        if a==p+1: p=a
        else: ranges.append((s,p+1)); s=p=a
    ranges.append((s,p+1))
    assert [(s,e) for s,e in ranges]==[(s,e) for s,e,_ in EXPECTED_RANGES]
    manifest=b""
    for s,e,h in EXPECTED_RANGES:
        b=rd(s,e-s)
        assert hashlib.sha256(b).hexdigest()==h
        manifest+=b
    assert hashlib.sha256(manifest).hexdigest()==MANIFEST_SHA

    writes=[]
    for pc,(mn,mode,n,o) in inst.items():
        if mn in WRITE and mode!="acc": writes.append((pc,mn,mode,o))
    assert len(writes)==82
    assert not [(pc,mn,mode,o) for pc,mn,mode,o in writes if mode in ("zp","abs") and o==0x10]
    indexed=[(pc,mn,mode,o) for pc,mn,mode,o in writes if mode in ("zpx","zpy","indx","indy","absx","absy")]
    assert len(indexed)==9
    assert all(mode in ("absx","absy") and o>=0x0300 for pc,mn,mode,o in indexed)

    w2c=sorted(pc for pc,mn,mode,o in writes if mode=="zp" and o==0x2C)
    w68=sorted(pc for pc,mn,mode,o in writes if mode=="zp" and o==0x68)
    assert w2c==EXPECTED_2C
    assert w68==EXPECTED_68

    print("ROM identity: OK")
    print("0500 window/fingerprint/overlap: OK")
    print("secondary table F84E-F86D: 16 pointers, SHA-256",T1_SHA)
    print("secondary table F96A-F97D: 10 pointers, SHA-256",T2_SHA)
    print("strict fixed graph: 414 official instruction starts; unknown opcodes 0")
    print("reachable store/RMW instructions: 82; indexed writes: 9 absolute-indexed only")
    print("direct/indexed ZP $10 aliases: 0")
    print("$2C mutation sites:", " ".join(f"${x:04X}" for x in w2c))
    print("$68 mutation sites:", " ".join(f"${x:04X}" for x in w68))
    print("04FF pending gaps admitted by F84E table: $F706,$F724,$F782,$F7B7")
    print("semantic data: $FB31-$FB36 six-byte record included")
    print("exact genuinely new bytes: 982")
    print("ordered manifest SHA-256",MANIFEST_SHA)
    print("boundary edges:", dict(sorted(EXPECTED_EDGES.items())))
    print("IMPORTANT: encoded target closure is not yet a complete live $68/$2C producer-domain proof")

if __name__=="__main__":
    if len(sys.argv)!=2: raise SystemExit("usage: audit_nmi_fixed_68_secondary.py ROM.nes")
    main(sys.argv[1])
