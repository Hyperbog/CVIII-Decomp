#!/usr/bin/env python3
from __future__ import annotations
import hashlib, sys
from collections import Counter, deque
from pathlib import Path

ROM_SHA="958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
LO,HI=0xF3DD,0xF800
WINDOW_SHA="72918e40813310fe3f967790d9b77e344a0f2ede92d12942d95c23849084b1b6"
OVERLAP_START,OVERLAP_END=0xF39D,0xF3DD
OVERLAP_SHA="81d06cd79d64c3d4cfe14bbefa851e74e748536f723636abaf82870ec065d22f"
FINGERPRINT_SHA="65d47f163ffad5ca20903cece8606c76416ceb5cb8edba99780be720730f08aa"
PRIOR_HELPER=(0xF6AE,0xF6E4,"d79b617b7e27190b6556464a37cc024a1837e949ebe9446d12815da908233dfb")
TABLE_START=0xF39D
TARGETS=[
0xF3FC,0xF402,0xF48D,0xF531,0xF5A8,0xF5D2,0xF61D,0xF62C,
0xF965,0xF638,0xF511,0xF831,0xF839,0xF841,0xF841,0xF4E7,
0xF849,0xF65B,0xF652,0xF713,0xF739,0xF792,0xF7CF,0xF653,
0xF6EC,0xF3F4,0xF6E4,0xF4FA,0xF6F4,0xF6FE,0xF3EC,0xF3DD]
IN_ENTRIES=[(i,t) for i,t in enumerate(TARGETS) if LO<=t<HI]
OUT_ENTRIES=[(i,t) for i,t in enumerate(TARGETS) if not (LO<=t<HI)]
EXPECTED_OUT=[(0x08,0xF965),(0x0B,0xF831),(0x0C,0xF839),(0x0D,0xF841),(0x0E,0xF841),(0x10,0xF849)]
EXPECTED_RANGES=[
(0xF3DD,0xF6AE,"371c27c08f71624463d2c63097938a30fa57253bd073d2554d454111708f6852"),
(0xF6E4,0xF706,"cd2f26e03fcfab69f12aec4fbe3ff9571f8a2633b3c84eb4365a0d8e777378c5"),
(0xF713,0xF724,"4bc45df46fbab59efc9b70eb7d577001b8474818f921b86e618b43c4653c8300"),
(0xF739,0xF782,"b8cc2cdf6b04eb86ff7693b53c006afb6710098252d7a921e199c22355d462ac"),
(0xF792,0xF7B7,"b564a74ff4c6ba3a55b76472c1462ff1b915f0c333c8dc54ccae3b9a76d1e5e1"),
(0xF7CF,0xF800,"13b6de6ba1671ce00afec40ee8b7886d6ed9126a6261b5a090a15f0cc73b1574")]
MANIFEST_SHA="2e8b703b970ca2f1eae61f5fd1a4850da6b8e5d4af1a894fb8075657299ae0d4"
EXPECTED_MUT=[
(0xF3FF,"INC"),(0xF443,"INC"),(0xF486,"STA"),(0xF4BF,"INC"),
(0xF4CF,"STA"),(0xF4DC,"STA"),(0xF4F3,"STA"),(0xF5CF,"INC"),
(0xF629,"STA"),(0xF635,"STA"),(0xF64F,"STA"),(0xF6FB,"INC"),
(0xF716,"INC"),(0xF775,"INC"),(0xF7B4,"INC"),(0xF7DB,"STA")]
INC_ROOTS={
0xF3FF:{0x00},0xF443:{0x01},0xF4BF:{0x01,0x02},0xF5CF:{0x04},
0xF6FB:{0x1C},0xF716:{0x13},0xF775:{0x14},0xF7B4:{0x15}}
EXPECTED_EDGE_COUNTS=Counter({
("jsr","banked"):64,("jmp","banked"):8,("jsr","fixed_out"):60,
("jmp","fixed_out"):1,("branch","fixed_out"):2,("fallthrough","fixed_out"):1})

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

def main(path):
    rom=Path(path).read_bytes(); assert hashlib.sha256(rom).hexdigest()==ROM_SHA
    prg=rom[16:16+0x40000]; fixed=prg[31*0x2000:32*0x2000]
    def rd(a,n=1):
        assert 0xE000<=a and a+n<=0x10000
        return fixed[a-0xE000:a-0xE000+n]

    assert hashlib.sha256(rd(OVERLAP_START,OVERLAP_END-OVERLAP_START)).hexdigest()==OVERLAP_SHA
    assert hashlib.sha256(rd(LO,32)).hexdigest()==FINGERPRINT_SHA
    assert len(rd(LO,HI-LO))==1059 and hashlib.sha256(rd(LO,HI-LO)).hexdigest()==WINDOW_SHA
    ps,pe,ph=PRIOR_HELPER; assert hashlib.sha256(rd(ps,pe-ps)).hexdigest()==ph

    tb=rd(TABLE_START,64); targets=[tb[i]|tb[i+1]<<8 for i in range(0,64,2)]
    assert targets==TARGETS and len(IN_ENTRIES)==26 and len({t for _,t in IN_ENTRIES})==26
    assert OUT_ENTRIES==EXPECTED_OUT

    def dec(pc):
        op=rd(pc)[0]; assert op in OPS, f"unknown official opcode ${op:02X} at ${pc:04X}"
        mn,mode,n=OPS[op]; assert pc+n<=HI, f"operand escape at ${pc:04X}"
        raw=rd(pc,n); operand=None
        if n==2:
            operand=raw[1]
            if mode=="rel":
                off=operand if operand<0x80 else operand-0x100
                operand=(pc+2+off)&0xFFFF
        elif n==3: operand=raw[1]|raw[2]<<8
        return op,mn,mode,n,operand

    def walk(root):
        q=deque([root]); seen=set(); edges=set()
        while q:
            pc=q.popleft()
            if pc in seen or not (LO<=pc<HI): continue
            op,mn,mode,n,operand=dec(pc); seen.add(pc); nxt=pc+n
            def put(kind,t):
                if LO<=t<HI: q.append(t)
                else:
                    cat="banked" if t<0xE000 else "fixed_out"
                    edges.add((kind,cat,pc,t))
            if mn in TERM: continue
            if mn in BR:
                put("fallthrough" if nxt>=HI else "branch",nxt); put("branch",operand)
            elif mn=="JMP":
                assert mode!="ind"; put("jmp",operand)
            elif mn=="JSR":
                put("fallthrough",nxt); put("jsr",operand)
            else: put("fallthrough",nxt)
        return seen,edges

    all_seen=set(); all_edges=set(); per_root={}
    for idx,root in IN_ENTRIES:
        s,e=walk(root); per_root[idx]=s; all_seen|=s; all_edges|=e
    assert len(all_seen)==401

    covered=set(); writes=[]
    for pc in all_seen:
        op,mn,mode,n,operand=dec(pc); covered.update(range(pc,pc+n))
        if mn in WRITE and mode!="acc": writes.append((pc,mn,mode,operand))
    assert len(covered)==931

    arr=sorted(covered); ranges=[]; s=p=arr[0]
    for a in arr[1:]:
        if a==p+1: p=a
        else: ranges.append((s,p+1)); s=p=a
    ranges.append((s,p+1))
    assert [(s,e) for s,e in ranges]==[(s,e) for s,e,_ in EXPECTED_RANGES]
    manifest=b""
    for s,e,h in EXPECTED_RANGES:
        b=rd(s,e-s); assert hashlib.sha256(b).hexdigest()==h; manifest+=b
    assert len(manifest)==931 and hashlib.sha256(manifest).hexdigest()==MANIFEST_SHA
    assert not (set(range(ps,pe)) & covered)

    assert not [(pc,mn,mode,o) for pc,mn,mode,o in writes if mode in ("zp","abs") and o==0x10]
    assert not [(pc,mn,mode,o) for pc,mn,mode,o in writes if mode in ("zpx","zpy","indx","indy")]
    mut=sorted((pc,mn) for pc,mn,mode,o in writes if mode=="zp" and o==0x2C)
    assert mut==EXPECTED_MUT

    assert rd(0xF450,4)==bytes.fromhex("a904d032")
    assert rd(0xF480,9)==bytes.fromhex("a9008561a909852c60")
    assert rd(0xF489,4)==bytes.fromhex("a913d0f9")
    for pc,val in [(0xF4CF,0x0F),(0xF4DC,0x0A),(0xF4F3,0x10),(0xF629,0x07),(0xF635,0x01),(0xF64F,0x02),(0xF7DB,0x10)]:
        assert rd(pc-2,4)==bytes([0xA9,val,0x85,0x2C])

    for site,expected in INC_ROOTS.items():
        assert {idx for idx,s in per_root.items() if site in s}==expected
    assert max(max(v) for v in INC_ROOTS.values())==0x1C

    ec=Counter((kind,cat) for kind,cat,pc,t in all_edges); assert ec==EXPECTED_EDGE_COUNTS
    print("ROM identity: OK")
    print("04FE nested-table overlap/fingerprint: OK")
    print("04FF initial window: $F3DD-$F7FF, 1059 raw bytes, SHA-256",WINDOW_SHA)
    print("encoded primary entries in window: 26/32; deferred:"," ".join(f"${i:02X}->${t:04X}" for i,t in OUT_ENTRIES))
    print("strict in-window graph: 401 official instruction starts; unknown opcodes 0")
    print("exact genuinely new decoded bytes: 931; ordered manifest SHA-256",MANIFEST_SHA)
    print("prior 04FE helper $F6AE-$F6E3 overlap with decoded graph: 0 bytes")
    print("dependency edges:",dict(sorted(ec.items())))
    print("reachable writes capable of aliasing ZP $10: 0")
    print("fixed-side $2C mutations:"," ".join(f"${pc:04X}:{mn}" for pc,mn in mut))
    print("fixed-side constants are <= $16; conservative INC-entry max is $1C -> at most $1D")
    print("NOT CLOSED: out-of-window fixed/banked callees may still mutate $2C; six primary table entries remain beyond $F7FF")
    print("04FF partial result: in-window fixed graph preserves $10 and sharpens, but does not close, the live $2C producer domain")

if __name__=="__main__":
    if len(sys.argv)!=2: raise SystemExit("usage: audit_nmi_fixed_2c_head.py ROM.nes")
    main(sys.argv[1])
