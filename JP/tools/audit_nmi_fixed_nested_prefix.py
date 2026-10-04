#!/usr/bin/env python3
from __future__ import annotations
import hashlib, sys
from collections import deque, defaultdict, Counter
from pathlib import Path

ROM_SHA="958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
LO,HI=0xF3DD,0xF800
SPAN_SHA="72918e40813310fe3f967790d9b77e344a0f2ede92d12942d95c23849084b1b6"
OVERLAP_LO,OVERLAP_HI=0xF6AE,0xF6E4
OVERLAP_SHA="d79b617b7e27190b6556464a37cc024a1837e949ebe9446d12815da908233dfb"
NEW_RANGES=[
    (0xF3DD,0xF6AE,"371c27c08f71624463d2c63097938a30fa57253bd073d2554d454111708f6852"),
    (0xF6E4,0xF800,"6f3c519ae6a1965fc20722535001e4c08a84dfde4245cfa79b78a463c8df0ce6"),
]
NEW_MANIFEST_SHA="257dfb57d710e3eb4ea9e4ff1d4d168901e65dc3afc7c1c6054c1c5d2548e51a"
TABLE_LO,TABLE_HI=0xF39D,0xF3DD
TABLE_SHA="81d06cd79d64c3d4cfe14bbefa851e74e748536f723636abaf82870ec065d22f"
TARGETS=[0xF3FC,0xF402,0xF48D,0xF531,0xF5A8,0xF5D2,0xF61D,0xF62C,0xF965,0xF638,0xF511,0xF831,0xF839,0xF841,0xF841,0xF4E7,0xF849,0xF65B,0xF652,0xF713,0xF739,0xF792,0xF7CF,0xF653,0xF6EC,0xF3F4,0xF6E4,0xF4FA,0xF6F4,0xF6FE,0xF3EC,0xF3DD]
EXPECTED_WRITER_ROOTS={0xF3FF:(0x00,),0xF443:(0x01,),0xF486:(0x01,),0xF4BF:(0x01,0x02),0xF4CF:(0x01,0x02),0xF4DC:(0x01,0x02),0xF4F3:(0x0F,),0xF5CF:(0x04,),0xF629:(0x06,),0xF635:(0x07,),0xF64F:(0x09,),0xF6FB:(0x1C,),0xF716:(0x13,),0xF775:(0x14,),0xF7B4:(0x15,),0xF7DB:(0x16,)}
EXPECTED_STA_VALUES={0xF486:{0x09,0x13},0xF4CF:{0x0F},0xF4DC:{0x0A},0xF4F3:{0x10},0xF629:{0x07},0xF635:{0x01},0xF64F:{0x02},0xF7DB:{0x10}}
EXPECTED_INC_TRANSITIONS={0xF3FF:{0x01},0xF443:{0x02},0xF4BF:{0x02,0x03},0xF5CF:{0x05},0xF6FB:{0x1D},0xF716:{0x14},0xF775:{0x15},0xF7B4:{0x16}}

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
    prg=rom[16:16+0x40000]; assert len(prg)==0x40000
    p31=prg[31*0x2000:32*0x2000]
    def rd(a,n=1):
        assert 0xE000<=a and a+n<=0x10000
        return p31[a-0xE000:a-0xE000+n]
    assert len(rd(LO,HI-LO))==1059 and hashlib.sha256(rd(LO,HI-LO)).hexdigest()==SPAN_SHA
    assert hashlib.sha256(rd(TABLE_LO,TABLE_HI-TABLE_LO)).hexdigest()==TABLE_SHA
    assert hashlib.sha256(rd(OVERLAP_LO,OVERLAP_HI-OVERLAP_LO)).hexdigest()==OVERLAP_SHA
    new=b""
    for a,b,h in NEW_RANGES:
        z=rd(a,b-a); assert hashlib.sha256(z).hexdigest()==h; new+=z
    assert len(new)==1005 and hashlib.sha256(new).hexdigest()==NEW_MANIFEST_SHA
    table=rd(TABLE_LO,TABLE_HI-TABLE_LO)
    targets=[table[i]|table[i+1]<<8 for i in range(0,len(table),2)]
    assert targets==TARGETS
    roots=[r for r in dict.fromkeys(targets) if LO<=r<HI]; assert len(roots)==26
    def dec(pc):
        op=rd(pc)[0]; assert op in OPS, f"unknown official opcode ${op:02X} at ${pc:04X}"
        mn,mode,n=OPS[op]; raw=rd(pc,n); operand=None
        if n==2:
            operand=raw[1]
            if mode=="rel":
                off=operand if operand<0x80 else operand-0x100; operand=(pc+2+off)&0xFFFF
        elif n==3: operand=raw[1]|raw[2]<<8
        return op,mn,mode,n,operand
    def walk(root):
        q=deque([root]); seen=set(); exits=set(); writes=[]
        while q:
            pc=q.popleft()
            if pc in seen: continue
            if not (LO<=pc<HI): exits.add(("entry",None,pc)); continue
            op,mn,mode,n,operand=dec(pc); assert pc+n<=HI, f"operand escape at ${pc:04X}"
            seen.add(pc)
            if mn in WRITE and mode!="acc": writes.append((pc,mn,mode,operand))
            nxt=pc+n
            if mn in TERM: continue
            if mn in BR:
                if LO<=nxt<HI: q.append(nxt)
                else: exits.add(("fall",pc,nxt))
                if LO<=operand<HI: q.append(operand)
                else: exits.add(("branch",pc,operand))
                continue
            if mn=="JMP":
                if mode=="ind": exits.add(("jmpind",pc,operand))
                elif LO<=operand<HI: q.append(operand)
                else: exits.add(("jmp",pc,operand))
                continue
            if mn=="JSR":
                if operand in (0xE7FB,0xE814): exits.add(("dispatcher",pc,operand)); continue
                if LO<=nxt<HI: q.append(nxt)
                else: exits.add(("fall",pc,nxt))
                if LO<=operand<HI: q.append(operand)
                else: exits.add(("jsr",pc,operand))
                continue
            if LO<=nxt<HI: q.append(nxt)
            else: exits.add(("fall",pc,nxt))
        return seen,exits,writes
    all_seen=set(); all_exits=set(); all_writes=[]; writer_roots=defaultdict(list)
    for idx,root in enumerate(targets):
        if not (LO<=root<HI): continue
        s,e,w=walk(root); all_seen|=s; all_exits|=e; all_writes+=w
        for pc,mn,mode,operand in w:
            if mode=="zp" and operand==0x2C: writer_roots[pc].append(idx)
    assert len(all_seen)==401
    assert not [w for w in all_writes if w[2] in ("zpx","zpy","indx","indy")]
    w2c=sorted({(pc,mn,mode,opnd) for pc,mn,mode,opnd in all_writes if mode=="zp" and opnd==0x2C}); assert len(w2c)==16
    assert {pc:tuple(v) for pc,v in sorted(writer_roots.items())}==EXPECTED_WRITER_ROOTS
    assert rd(0xF480,0x0D)==bytes.fromhex("a9008561a909852c60a913d0f9")
    for pc,vals in EXPECTED_STA_VALUES.items():
        if pc==0xF486: continue
        assert rd(pc-2,4)[0]==0xA9 and rd(pc-2,4)[2:]==bytes([0x85,0x2C]) and {rd(pc-1)[0]}==vals
    for pc,vals in EXPECTED_INC_TRANSITIONS.items():
        assert rd(pc,2)==bytes([0xE6,0x2C]); roots_for=EXPECTED_WRITER_ROOTS[pc]
        assert {((r+1)&0xFF) for r in roots_for}==vals
    local_values=set()
    for vals in EXPECTED_STA_VALUES.values(): local_values|=vals
    for vals in EXPECTED_INC_TRANSITIONS.values(): local_values|=vals
    assert max(local_values)<=0x1F and local_values=={1,2,3,5,7,9,10,15,16,19,20,21,22,29}
    counts=Counter(k for k,_,_ in all_exits); assert counts==Counter({"jsr":124,"jmp":9,"branch":2,"fall":1})
    print("ROM identity: OK")
    print("04FF fixed prefix: $F3DD-$F7FF, 1059 dependency bytes, SHA-256",SPAN_SHA)
    print("prior 04FE overlap: $F6AE-$F6E3 = 54 bytes")
    print("04FF genuinely new bytes: 1005; ordered new-manifest SHA-256",NEW_MANIFEST_SHA)
    print("nested table roots physically inside prefix: 26 unique / 32 encoded entries")
    print("conservative in-prefix instruction starts:",len(all_seen),"unknown opcodes: 0")
    print("reachable direct $2C writers:",len(w2c))
    print("indexed/indirect zero-page writes in local graph: 0")
    print("nominal local-only $2C values (constant stores plus root-associated INC):",",".join(f"${v:02X}" for v in sorted(local_values)))
    print("all nominal local-only values are <= $1F: OK; this is NOT a transitive producer bound")
    print("deferred prefix exits:",dict(sorted(counts.items())))
    print("IMPORTANT: external callees are not assumed to preserve $2C or $10; complete producer/transitive closure remains open")
    print("04FF result: fixed-prefix local $2C producer transitions bounded; next byte frontier $F800")

if __name__=="__main__":
    if len(sys.argv)!=2: raise SystemExit("usage: audit_nmi_fixed_nested_prefix.py ROM.nes")
    main(sys.argv[1])
