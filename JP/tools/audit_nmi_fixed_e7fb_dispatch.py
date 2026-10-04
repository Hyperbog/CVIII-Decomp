#!/usr/bin/env python3
from __future__ import annotations
import hashlib, sys
from collections import deque
from pathlib import Path

ROM_SHA="958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
FIRST_TABLE_START=0xE363
FIRST_TARGETS=[0xE383,0xE436,0xE437,0xE449,0xF390,0xE459,0xE49B,0xE539,0xE50E,0xE516,0xE541,0xE549,0xE51E,0xE526,0xE52E,0xE531]
NESTED_TABLE_START=0xF39D
NESTED_TARGETS=[0xF3FC,0xF402,0xF48D,0xF531,0xF5A8,0xF5D2,0xF61D,0xF62C,0xF965,0xF638,0xF511,0xF831,0xF839,0xF841,0xF841,0xF4E7,0xF849,0xF65B,0xF652,0xF713,0xF739,0xF792,0xF7CF,0xF653,0xF6EC,0xF3F4,0xF6E4,0xF4FA,0xF6F4,0xF6FE,0xF3EC,0xF3DD]
EXPECTED_EXTERNAL={
("jmp_ext",0xE53E,0x8974),("jmp_ext",0xE513,0xA38D),("jmp_ext",0xE51B,0xA513),("jmp_ext",0xE546,0xB195),("jmp_ext",0xE54E,0xB7D2),("jmp_ext",0xE523,0xAFA4),("jmp_ext",0xE52B,0xB4CC),("jmp_ext",0xE536,0xBBEA),("jsr_ext",0xE4DA,0x8A81),("jsr_ext",0xE505,0x8EA0),("jsr_ext",0xE7AC,0x8FFC),("jsr_ext",0xE39C,0xA9D5),("jmp_ext",0xE715,0x8F1E),("jsr_ext",0xE4A9,0x8ED0),("jsr_ext",0xE642,0xB69D),("jsr_ext",0xE258,0x8850),("jsr_ext",0xE479,0x8957),("jsr_ext",0xE3EF,0x8A8A),("jsr_ext",0xF6D6,0x84A0),("jsr_ext",0xE21E,0x87AE),("jsr_ext",0xEC5B,0x966F),
}
NEW_RANGES=[
(0xE366,0xE434,"b1bb37d98f9d0c9992ec2c9bc0c8a99cb3a1a2db8eb9359ecdc686ed1a7d6f46"),
(0xE436,0xE577,"faa4c0e4033694f4e0bbadc1ac18fb500d3b746c8c1c1c46bb9523124c9ba3f9"),
(0xE62D,0xE632,"40038e39a56b11e71412ead62b2574002c961973fe122d0aaca3b89f0ac0d52c"),
(0xE63D,0xE648,"0b6bd8d5b060c86180149316236f21750165b786917ccf3dcd636db5071a8d34"),
(0xE710,0xE718,"42e14ed3d9e6686c8e5b7b2f9c4639ddeafdc43a2156d6776c3ca07754096dd5"),
(0xE7A7,0xE814,"77fdf616b9dcf810b95d87fbad15f22842b277c8a28e7bc6b0911084e493bdb2"),
(0xE827,0xE831,"fe9dab3a7ce1bb29399af19923cf2e12165f9d17a0ed4bd6bebce71da6410060"),
(0xEB44,0xEB6B,"7a534ebcac80d8c2e919184621381e3b944ae0ee161d474705cfe5cb199760c6"),
(0xEB82,0xEBF7,"e69aaaa7f343f00621a23d78aab2b018057a6ba29ac50d07aa1c34bc8ed287e8"),
(0xF390,0xF3DD,"534f1b3ff2e7b25348a1a4c66479018ec9153d63b3e9f9b964f9e07483905b15"),
(0xF6AE,0xF6E4,"d79b617b7e27190b6556464a37cc024a1837e949ebe9446d12815da908233dfb"),
]
MANIFEST_SHA="a672f908a238bea20902fc40c5417622bdb9af675cda3b982a6f0ce494ebad32"

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
    fixed=prg[31*0x2000:32*0x2000]
    def rd(a,n=1):
        assert 0xE000<=a and a+n<=0x10000
        return fixed[a-0xE000:a-0xE000+n]

    raw05=prg[10*0x2000:12*0x2000]
    overlap=raw05[0xBEC6-0x8000:0xBF06-0x8000]
    assert hashlib.sha256(overlap).hexdigest()=="147db970967ce1d07c60a098be16c2e45ab99c491a0ade38fd01b6ea8d87fbf6"
    assert hashlib.sha256(rd(0xE7FB,32)).hexdigest()=="1ca470cc478911cb3c75c9dc716b23714e2b816b674d716a2ec33e5cbedd6d58"

    assert rd(0xE7FB,0x19)==bytes.fromhex("0a8403a8c8688500688501b1008502c8b100a40385036c0200")
    assert hashlib.sha256(rd(0xE7FB,0x19)).hexdigest()=="d2adbf45aa9746eb53ba2e8ec8513cb338f8fd30f4bc3627074f186c14439091"
    assert rd(0xE35C,7)==bytes.fromhex("e61ba51820fbe7")

    first=[]
    for i in range(16):
        b=rd(FIRST_TABLE_START+2*i,2); first.append(b[0]|b[1]<<8)
    assert first==FIRST_TARGETS
    assert hashlib.sha256(rd(0xE363,32)).hexdigest()=="def43bbd8730858236b66f0cbfebec9d050c05a29ab90db176a3a4b3da186089"
    assert rd(0xE365,2)==bytes.fromhex("36e4")

    def dec(pc):
        op=rd(pc)[0]; assert op in OPS, f"unknown official opcode ${op:02X} at ${pc:04X}"
        mn,mode,n=OPS[op]; raw=rd(pc,n); operand=None
        if n==2:
            operand=raw[1]
            if mode=="rel":
                off=operand if operand<0x80 else operand-0x100
                operand=(pc+2+off)&0xFFFF
        elif n==3:
            operand=raw[1]|raw[2]<<8
        return op,mn,mode,n,operand

    q=deque(FIRST_TARGETS); seen=set(); ext=set(); inline=[]; writes=[]
    while q:
        pc=q.popleft()
        if pc in seen: continue
        assert 0xE000<=pc<=0xFFFF
        op,mn,mode,n,operand=dec(pc); seen.add(pc)
        if mn in WRITE and mode!="acc": writes.append((pc,op,mn,mode,operand))
        nxt=pc+n
        if mn in TERM: continue
        if mn in BR:
            q.extend([nxt,operand]); continue
        if mn=="JMP":
            if mode=="ind": raise AssertionError(f"unexpected indirect JMP at ${pc:04X}")
            if 0xE000<=operand<=0xFFFF: q.append(operand)
            else: ext.add(("jmp_ext",pc,operand))
            continue
        if mn=="JSR":
            if operand==0xE7FB:
                inline.append(pc)
                continue
            q.append(nxt)
            if 0xE000<=operand<=0xFFFF: q.append(operand)
            else: ext.add(("jsr_ext",pc,operand))
            continue
        q.append(nxt)

    assert len(seen)==435
    assert inline==[0xF39A]
    assert ext==EXPECTED_EXTERNAL
    assert not [(pc,mn,mode,opnd) for pc,op,mn,mode,opnd in writes if mode in ("zp","abs") and opnd==0x10]
    idx=sorted((pc,mn,mode,opnd) for pc,op,mn,mode,opnd in writes if mode in ("zpx","zpy","indx","indy"))
    assert idx==[(0xE7BA,"STA","zpx",0x00),(0xE7F3,"STA","zpx",0xF0),(0xE82A,"STA","zpx",0x00),(0xE82E,"INC","zpx",0x01)]
    assert rd(0xE7B2,0x0F)==bytes.fromhex("a228d002a24da9009500e8e0e0d0f9")
    assert rd(0xE7F0,0x0B)==bytes.fromhex("a900aa95f0e8e00890f960")
    assert rd(0xEBA7,7)==bytes.fromhex("a200a9022027e8")
    assert rd(0xE827,0x0A)==bytes.fromhex("18750095009002f60160")
    assert {pc for pc in seen if pc in (0xEBAB,0xEBD4,0xEBEE)}=={0xEBAB,0xEBD4,0xEBEE}

    assert rd(0xF390,0x0D)==bytes.fromhex("20aef6a52df00160a52c20fbe7")
    nested=[]
    for i in range(32):
        b=rd(NESTED_TABLE_START+2*i,2); nested.append(b[0]|b[1]<<8)
    assert nested==NESTED_TARGETS
    assert hashlib.sha256(rd(0xF39D,64)).hexdigest()=="81d06cd79d64c3d4cfe14bbefa851e74e748536f723636abaf82870ec065d22f"
    assert rd(0xF3DD,2)==bytes.fromhex("a902")

    blob=b""; total=0
    for start,end,sha in NEW_RANGES:
        b=rd(start,end-start); total+=len(b); blob+=b
        assert hashlib.sha256(b).hexdigest()==sha
    assert total==957
    assert hashlib.sha256(blob).hexdigest()==MANIFEST_SHA
    assert hashlib.sha256(rd(0xF3DD,32)).hexdigest()=="65d47f163ffad5ca20903cece8606c76416ceb5cb8edba99780be720730f08aa"

    print("ROM identity: OK",ROM_SHA)
    print("04FD->04FE fixed-PRG recovery handoff: OK")
    print("E7FB dispatcher body: exact; writes only $00-$03 and tail-jumps through inline pointer")
    print("E35C first-level inline table: 16 encoded pointers at $E363-$E382")
    print("first-level fixed graph: 435 instruction starts; unknown opcodes 0")
    print("direct/indexed ZP $10 writes in fixed graph: 0 after caller-X reconciliation")
    print("external banked edges deferred:",len(ext))
    print("nested dispatcher: $F39A uses A=$2C; 32 encoded pointers at $F39D-$F3DC")
    print("selector producer domains for $18 and $2C remain open; no inferred host bounds")
    print("04FE exact new fixed bytes:",total,"manifest SHA-256",MANIFEST_SHA)
    print("next semantic frontier: fixed PRG31 $F3DD nested-handler code")

if __name__=="__main__":
    if len(sys.argv)!=2: raise SystemExit("usage: audit_nmi_fixed_e7fb_dispatch.py ROM.nes")
    main(sys.argv[1])
