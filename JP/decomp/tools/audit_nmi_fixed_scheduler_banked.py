#!/usr/bin/env python3
from __future__ import annotations
import hashlib, sys
from collections import deque, Counter
from pathlib import Path

ROM_SHA="958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"

OPS={}
def add(o,m,mode,n): OPS[int(o,16)]=(m,mode,n)
TABLE='00 BRK imp 1\n01 ORA indx 2\n05 ORA zp 2\n06 ASL zp 2\n08 PHP imp 1\n09 ORA imm 2\n0A ASL acc 1\n0D ORA abs 3\n0E ASL abs 3\n10 BPL rel 2\n11 ORA indy 2\n15 ORA zpx 2\n16 ASL zpx 2\n18 CLC imp 1\n19 ORA absy 3\n1D ORA absx 3\n1E ASL absx 3\n20 JSR abs 3\n21 AND indx 2\n24 BIT zp 2\n25 AND zp 2\n26 ROL zp 2\n28 PLP imp 1\n29 AND imm 2\n2A ROL acc 1\n2C BIT abs 3\n2D AND abs 3\n2E ROL abs 3\n30 BMI rel 2\n31 AND indy 2\n35 AND zpx 2\n36 ROL zpx 2\n38 SEC imp 1\n39 AND absy 3\n3D AND absx 3\n3E ROL absx 3\n40 RTI imp 1\n41 EOR indx 2\n45 EOR zp 2\n46 LSR zp 2\n48 PHA imp 1\n49 EOR imm 2\n4A LSR acc 1\n4C JMP abs 3\n4D EOR abs 3\n4E LSR abs 3\n50 BVC rel 2\n51 EOR indy 2\n55 EOR zpx 2\n56 LSR zpx 2\n58 CLI imp 1\n59 EOR absy 3\n5D EOR absx 3\n5E LSR absx 3\n60 RTS imp 1\n61 ADC indx 2\n65 ADC zp 2\n66 ROR zp 2\n68 PLA imp 1\n69 ADC imm 2\n6A ROR acc 1\n6C JMP ind 3\n6D ADC abs 3\n6E ROR abs 3\n70 BVS rel 2\n71 ADC indy 2\n75 ADC zpx 2\n76 ROR zpx 2\n78 SEI imp 1\n79 ADC absy 3\n7D ADC absx 3\n7E ROR absx 3\n81 STA indx 2\n84 STY zp 2\n85 STA zp 2\n86 STX zp 2\n88 DEY imp 1\n8A TXA imp 1\n8C STY abs 3\n8D STA abs 3\n8E STX abs 3\n90 BCC rel 2\n91 STA indy 2\n94 STY zpx 2\n95 STA zpx 2\n96 STX zpy 2\n98 TYA imp 1\n99 STA absy 3\n9A TXS imp 1\n9D STA absx 3\nA0 LDY imm 2\nA1 LDA indx 2\nA2 LDX imm 2\nA4 LDY zp 2\nA5 LDA zp 2\nA6 LDX zp 2\nA8 TAY imp 1\nA9 LDA imm 2\nAA TAX imp 1\nAC LDY abs 3\nAD LDA abs 3\nAE LDX abs 3\nB0 BCS rel 2\nB1 LDA indy 2\nB4 LDY zpx 2\nB5 LDA zpx 2\nB6 LDX zpy 2\nB8 CLV imp 1\nB9 LDA absy 3\nBA TSX imp 1\nBC LDY absx 3\nBD LDA absx 3\nBE LDX absy 3\nC0 CPY imm 2\nC1 CMP indx 2\nC4 CPY zp 2\nC5 CMP zp 2\nC6 DEC zp 2\nC8 INY imp 1\nC9 CMP imm 2\nCA DEX imp 1\nCC CPY abs 3\nCD CMP abs 3\nCE DEC abs 3\nD0 BNE rel 2\nD1 CMP indy 2\nD5 CMP zpx 2\nD6 DEC zpx 2\nD8 CLD imp 1\nD9 CMP absy 3\nDD CMP absx 3\nDE DEC absx 3\nE0 CPX imm 2\nE1 SBC indx 2\nE4 CPX zp 2\nE5 SBC zp 2\nE6 INC zp 2\nE8 INX imp 1\nE9 SBC imm 2\nEA NOP imp 1\nEC CPX abs 3\nED SBC abs 3\nEE INC abs 3\nF0 BEQ rel 2\nF1 SBC indy 2\nF5 SBC zpx 2\nF6 INC zpx 2\nF8 SED imp 1\nF9 SBC absy 3\nFD SBC absx 3\nFE INC absx 3'
for line in TABLE.splitlines():
    o,m,mode,n=line.split(); add(o,m,mode,int(n))
BR={"BPL","BMI","BVC","BVS","BCC","BCS","BNE","BEQ"}
TERM={"RTS","RTI","BRK"}
WRITE={"STA","STX","STY","INC","DEC","ASL","LSR","ROL","ROR"}

FIXED_NEW=[
(0xFDE4,0xFEEA,"87cb2d7b62449573311d9a9aae13cdb072d3058d42faf82b9c7b81c5b6e3a3c1"),
(0xFF56,0xFF7A,"3bc8a1cf86ea269287fe1133f416880d9c552654d537ab02676a968c4737124d"),
]
BANK09=[
(0x8001,0x8150,"2dd7d61df700b59351a3233b09df098f97f6c338828e74a54b349a0136006bc7"),
(0x8152,0x8163,"52202e6406418453ccc7e56bf3eb725fd468e4f59b0cef10017baa06c1159b47"),
(0x8250,0x831F,"9d1b0adbc05522dcbf64c234e41a96db047d86f35eec0f3bd35c5537705fdf7b"),
(0x8357,0x841A,"6e4880f156a25ec9cc3629d85b02345b115a2f0899f6d92f1b062d7b474d3560"),
(0x843C,0x84E5,"18b0aeae2ef5979d33e052059c6dc827bd086f7588d6dc80e888e9e6d8eb9281"),
(0x8692,0x86BE,"23f97b589e7577cb68385e24c313f013774a71c74df7339ef207b0def906155c"),
(0x8810,0x8863,"9cb9e1a5b221e5de3749feb2c2a45d9a141cd31bfcd6bba2d9b03bdf2d1d8b38"),
]
BANK0A=[
(0x83D1,0x8410,"f302ac2b3ac985520f5d7780d6583a5cbed3f9164b33136484b157b2c99f4a90"),
(0x84EA,0x8523,"5190ad255e8121db4a4c4143c7965f0a5391391465e46618a39e9644fa992bfb"),
]
BANK0B=[
(0x8001,0x804B,"4f8acdadcc27a00278b799ca271122d46c05473d92f19e1f01ee505113fccef9"),
(0x80B3,0x821B,"8808b66fc5d79e67731f93e6b1fa6554d72262b9e5b29a1e4867ae2758c32ca7"),
(0x8253,0x8291,"970aa4064d4764e045bf51afb40cb64e7dcafa6fc65778db3e3bbc24555c3930"),
(0x82CD,0x82EF,"1222fb43b483c3a0f3e1e2ad973cec228fc29f60a550d50bd0141d789fe92a75"),
(0x8309,0x8312,"ac7aded349ec49398a679d2da45eecb298b89b4581671c895599bd61768dd6ae"),
(0x8315,0x831E,"25de7e8be3bee10543ef719c350ff4317d161faf3cc3e1709eb0c10716ae0be3"),
(0x8843,0x886C,"c79cb2d2295368c2034f93615d0acf4aca20a24c3a338c9f3be0f7d54854d8eb"),
(0xA154,0xA15D,"b2bac4515e62017992e1cd8ff89a0a307871a8b8503a68f3d74625e5ac769cae"),
(0xA2C9,0xA2CF,"f79e1d0981d284dfb551be33010685836f73901c76db0e97145bf45fa42feca1"),
(0xA329,0xA366,"6825e459291b646417e7f1d918677e7f76453379a1560ae24fc933fd79485c2a"),
(0xA3A6,0xA3AC,"b0098751a43af502824e9ac33341c0384a53559d6fcef54360b23682f2107adc"),
(0xB106,0xB320,"ffbbafe28471a79bdb0f4b7b08b11a27ce8ce47ced545dbed205560658dc8f48"),
(0xB323,0xB394,"ada777e3c5d6cff781f04cd8c1afdc4afedc27aa589d4ece91060189f8a618a5"),
(0xB396,0xB4D5,"0356b104267a70383b750c09187209c282e7dd252fb518f11b56f65341c6b167"),
(0xB4D7,0xB629,"d6ca1dcb716862996f99c2253f005b202eab7224e8dd6666c8cbbf1d2dae3e03"),
(0xB632,0xB673,"efee106fa7f7651f999d6110514425dc8615da42f47de108b57a056224a807e0"),
(0xB6CE,0xB782,"cb72dbf7c191a568d7fc61498a7b3a0038a16594fdc1767d8f56d6b9710927fd"),
(0xB7E5,0xB974,"ef24909ade0b6e170c013403a7ba513f84d8109496bbcd17ddb47b70872cb896"),
(0xB986,0xBA40,"8a4c0047b50f6b7b7c8b843928334e6dd8197baff8ec7669c5939ce12b281559"),
(0xBD10,0xBD67,"d4336919aa9623d6a468541ba5f578dc8127d494a781af95811994bec2eb04b9"),
]
COMBINED_SHA="639e20f7e96e816a40ef4ef7d8585c809ce670ac5384f3c2fabc9a77d275737e"
ZP10_0B=[0xB3B6,0xB3D2,0xB40E,0xB460,0xB65F,0xB740,0xB76C]

PRIOR_FIXED=[
(0xE057,0xE366),(0xEC00,0xF000),
(0xE366,0xE434),(0xE436,0xE577),(0xE62D,0xE632),(0xE63D,0xE648),
(0xE710,0xE718),(0xE7A7,0xE814),(0xE827,0xE831),(0xEB44,0xEB6B),
(0xEB82,0xEBF7),(0xF390,0xF3DD),(0xF6AE,0xF6E4),
(0xF3DD,0xF6AE),(0xF6E4,0xF706),(0xF713,0xF724),(0xF739,0xF782),
(0xF792,0xF7B7),(0xF7CF,0xF800),
(0xF706,0xF713),(0xF724,0xF739),(0xF782,0xF792),(0xF7B7,0xF7CF),
(0xF800,0xFAA0),(0xFAAA,0xFB96),
]

def ranges_from_set(ss):
    a=sorted(ss)
    if not a:return []
    out=[];s=p=a[0]
    for x in a[1:]:
        if x==p+1:p=x
        else:out.append((s,p+1));s=p=x
    out.append((s,p+1));return out

def main(path):
    rom=Path(path).read_bytes()
    assert hashlib.sha256(rom).hexdigest()==ROM_SHA
    prg=rom[16:16+0x40000]; assert len(prg)==0x40000
    fixed=prg[31*0x2000:32*0x2000]
    def f_rd(a,n=1):
        assert 0xE000<=a and a+n<=0x10000
        return fixed[a-0xE000:a-0xE000+n]
    def bank(raw):
        b=prg[raw*0x4000:(raw+1)*0x4000]; assert len(b)==0x4000
        return b
    def r_rd(raw,a,n=1):
        assert 0x8000<=a and a+n<=0xC000
        return bank(raw)[a-0x8000:a-0x8000+n]
    def dec(reader,pc):
        op=reader(pc)[0]; assert op in OPS, f"unknown ${op:02X} at ${pc:04X}"
        mn,mode,n=OPS[op]; b=reader(pc,n); o=None
        if n==2:
            o=b[1]
            if mode=="rel":
                off=o if o<0x80 else o-0x100; o=(pc+2+off)&0xFFFF
        elif n==3:o=b[1]|b[2]<<8
        return mn,mode,n,o

    assert f_rd(0xFDE4,2)==bytes.fromhex("e6a0")
    assert f_rd(0xFE8C,12)==bytes.fromhex("bd65054a4a4a4a4a4a20fbe7")
    tb=f_rd(0xFE98,6)
    assert [tb[i]|tb[i+1]<<8 for i in range(0,6,2)]==[0xFE9E,0xFEB1,0xFEC6]
    assert f_rd(0xFE9E,2)==bytes.fromhex("a980")

    q=deque([0xFDE4]); fseen=set(); fedges=[]; fw=[]
    while q:
        pc=q.popleft()
        if pc in fseen:continue
        mn,mode,n,o=dec(f_rd,pc); fseen.add(pc)
        if mn in WRITE and mode!="acc":fw.append((pc,mn,mode,o))
        nxt=pc+n
        def put(k,t):
            c="fixed" if t>=0xE000 else "banked"; fedges.append((k,pc,t,c))
            if c=="fixed":q.append(t)
        if pc==0xFE95:
            assert mn=="JSR" and o==0xE7FB
            for t in (0xFE9E,0xFEB1,0xFEC6):put("dispatch",t)
            continue
        if mn in TERM:continue
        if mn in BR:put("fallthrough",nxt);put("branch",o)
        elif mn=="JMP":
            assert mode!="ind";put("jmp",o)
        elif mn=="JSR":put("jsr",o);put("fallthrough",nxt)
        else:put("fallthrough",nxt)
    assert len(fseen)==161
    fcode=set()
    for pc in fseen:
        mn,mode,n,o=dec(f_rd,pc); fcode.update(range(pc,pc+n))
    fsemantic=fcode|set(range(0xFE98,0xFE9E))
    prior=set()
    for s,e in PRIOR_FIXED:prior.update(range(s,e))
    fnew=fsemantic-prior
    assert len(fnew)==298 and ranges_from_set(fnew)==[(s,e) for s,e,h in FIXED_NEW]
    assert not [w for w in fw if w[2] in ("zp","abs") and w[3]==0x10]
    assert not [w for w in fw if w[2] in ("zpx","zpy","indx","indy")]

    assert f_rd(0xFDF3,11)==bytes.fromhex("a90b20d0e220e38020f8b1")
    assert f_rd(0xFE09,8)==bytes.fromhex("a90920d0e2200180")
    assert f_rd(0xFE4C,8)==bytes.fromhex("a90b20d0e2200180")
    assert f_rd(0xFE63,11)==bytes.fromhex("a90b20d0e2206181206c82")
    assert f_rd(0xFE76,8)==bytes.fromhex("a90a20d0e220ea84")
    assert f_rd(0xFE31,3)==bytes.fromhex("2011bd")

    def walk_raw(raw,roots,blocked=frozenset()):
        reader=lambda a,n=1:r_rd(raw,a,n)
        q=deque(roots);seen=set();edges=[];writes=[];dispatch=[]
        while q:
            pc=q.popleft()
            if pc in seen or pc in blocked:continue
            mn,mode,n,o=dec(reader,pc);seen.add(pc)
            if mn in WRITE and mode!="acc":writes.append((pc,mn,mode,o))
            nxt=pc+n
            def put(k,t):
                if 0x8000<=t<0xC000:
                    edges.append((k,pc,t,"same"));q.append(t)
                elif t>=0xE000:edges.append((k,pc,t,"fixed"))
                else:edges.append((k,pc,t,"other"))
            if mn in TERM:continue
            if mn in BR:put("fallthrough",nxt);put("branch",o)
            elif mn=="JMP":
                if mode=="ind":edges.append(("jmp_ind",pc,o,"indirect"))
                else:put("jmp",o)
            elif mn=="JSR":
                if o==0xE7FB:
                    dispatch.append(pc);edges.append(("e7fb_dispatch",pc,o,"fixed"));continue
                put("jsr",o);put("fallthrough",nxt)
            else:put("fallthrough",nxt)
        return seen,edges,writes,dispatch

    assert r_rd(0x0B,0xB96E,8)==bytes.fromhex("c910b0fb90e91010")
    s09,e09,w09,d09=walk_raw(0x09,[0x8001])
    s0a,e0a,w0a,d0a=walk_raw(0x0A,[0x84EA])
    s0b,e0b,w0b,d0b=walk_raw(0x0B,[0x80E3,0xB1F8,0xBD11,0x8001,0x8161,0x826C],{0xB974})
    assert (len(s09),len(s0a),len(s0b))==(479,57,1338)
    assert d09==[] and d0a==[] and sorted(d0b)==[0xA15A,0xA2CC,0xA3A9]
    def code_bytes(raw,seen):
        out=set(); reader=lambda a,n=1:r_rd(raw,a,n)
        for pc in seen:
            mn,mode,n,o=dec(reader,pc);out.update(range(pc,pc+n))
        return out
    c09=code_bytes(0x09,s09);c0a=code_bytes(0x0A,s0a);c0b=code_bytes(0x0B,s0b)
    assert (len(c09),len(c0a),len(c0b))==(1050,120,2896)
    assert ranges_from_set(c09)==[(s,e) for s,e,h in BANK09]
    assert ranges_from_set(c0a)==[(s,e) for s,e,h in BANK0A]
    assert ranges_from_set(c0b)==[(s,e) for s,e,h in BANK0B]
    for raw,ranges in ((0x09,BANK09),(0x0A,BANK0A),(0x0B,BANK0B)):
        for s,e,h in ranges:
            assert hashlib.sha256(r_rd(raw,s,e-s)).hexdigest()==h

    def d10(w):return sorted(pc for pc,mn,mode,o in w if mode in ("zp","abs") and o==0x10)
    assert d10(w09)==[] and d10(w0a)==[] and d10(w0b)==ZP10_0B
    for ww in (w09,w0a,w0b):
        assert not [w for w in ww if w[2] in ("zpx","zpy","indx","indy")]

    m0b=sorted((pc,o) for pc in s0b for mn,mode,n,o in [dec(lambda a,n=1:r_rd(0x0B,a,n),pc)] if mn in ("JSR","JMP") and o in (0xE2D0,0xE2CA,0xE249,0xE5DA))
    assert m0b==[(0xA331,0xE249),(0xB4BE,0xE249),(0xB4DC,0xE249),(0xB53C,0xE249)]
    assert f_rd(0xE249,0x1B)==bytes.fromhex("48a9ff8526a5238525a90c20d0e268205088a9008526a5254cd0e2")

    for s,e,h in FIXED_NEW:
        assert hashlib.sha256(f_rd(s,e-s)).hexdigest()==h
    hh=hashlib.sha256(); total=0
    for tag,ranges,reader in (
        (0x09,BANK09,lambda s,n:r_rd(0x09,s,n)),
        (0x0A,BANK0A,lambda s,n:r_rd(0x0A,s,n)),
        (0x0B,BANK0B,lambda s,n:r_rd(0x0B,s,n)),
        (0x1F,FIXED_NEW,lambda s,n:f_rd(s,n)),
    ):
        for s,e,h in ranges:
            b=reader(s,e-s);total+=len(b)
            hh.update(bytes([tag]));hh.update(s.to_bytes(2,"little"));hh.update((e-1).to_bytes(2,"little"));hh.update(b)
    assert total==4364 and hh.hexdigest()==COMBINED_SHA

    print("ROM identity: OK")
    print("0501 fixed root: PRG31:$FDE4; 161 instruction starts; 298 genuinely new fixed bytes")
    print("FE95 inline dispatch: 3 encoded fixed pointers ($FE9E,$FEB1,$FEC6); selector value 3 remains unproven")
    print("raw bank $09 root $8001: 479 starts / 1050 bytes; direct ZP $10 writes 0")
    print("raw bank $0A root $84EA: 57 starts / 120 bytes; direct ZP $10 writes 0")
    print("raw bank $0B scheduler roots: 1338 starts / 2896 bytes")
    print("raw bank $0B direct ZP $10 writes:", " ".join(f"${x:04X}" for x in ZP10_0B))
    print("0501 exact new tracked PRG bytes: 4364")
    print("combined tagged-manifest SHA-256",COMBINED_SHA)
    print("OPEN: raw09 indirect/E5DA callees, raw0B E7FB/indirect exits, FE95 selector=3 producer proof")

if __name__=="__main__":
    if len(sys.argv)!=2: raise SystemExit("usage: audit_nmi_fixed_scheduler_banked.py ROM.nes")
    main(sys.argv[1])
