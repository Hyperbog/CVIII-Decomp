#!/usr/bin/env python3
"""0504: auditable JP bank-$0B AI seed and fixed PRG31 $FC1F graph.

Only consumed opcode/operand bytes and producer-bounded table data are
counted. Indirect/indexed ROM accesses with unknown domains stay open.
"""
from __future__ import annotations
import hashlib, json, sys
from collections import Counter, deque
from pathlib import Path
from audit_nmi_fixed_scheduler_banked import OPS, BR, TERM, BANK0B

ROM_SHA="958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
EXPECTED_MANIFEST_SHA="4416db601cba553569d4ccc4aba410a6d843a6da3504dac1d735317ca1106eb4"
# End addresses exclusive, SHA256 hashes over the exact physical ROM bytes.
RANGES="""fixed31 code FBF6 FC17 aef72125489106f46e5126d06c70468a12b2e5d3217bf5601856be437fa98ca6
fixed31 code FC1F FD4D a87fac16f29f6f4ff4d80238545a35cd78446118a02110784835f075d8809c90
fixed31 data FD4D FD59 19f7481bdd32ba4244331a4948e09d1e541eef9702976d4d46b62fab475225b4
raw0b code 807F 808F 872747bd9c7ae5b22d140e73f3b84d0eabf6907b4aed0edb9153ffdc5df3a78a
raw0b code 82C7 82CD 01d6ddd14ddb51aa5e3256683173fc2e4ce8f5d5d556b095a6fc649397908db7
raw0b code 8357 8363 3e3f9a6e7d3e43ad9c8b874723ac32a52f30cfafe5ab6aef218391b1b18dbf02
raw0b code 8519 8529 a9522c36a2015d6ca882339bda770889688cc98b93ea40692e99ffdaf6e60096
raw0b code 85E6 85FE 5fc395b6ecebef6e9de4ed33213afda0dd4959efd720b1730097d2a46e63fe9f
raw0b code 8EF7 8F16 4ce1f0d6ebc209b7fd6aa554315b502767dd36c81305849d860cd23dc22a0ecc
raw0b code 965D 968C cae6fc5dec7311f65c17145809a7aa15d401ec7f99e8fcc12ad2457593eefd19
raw0b code 96B4 96C5 2185fb411ee0675bb8113fe3da781a9a31bf4e420b5008d60c81a7538bbfb1d1
raw0b data 968C 96B4 ecee5e26c7787f38575a7c1b282135c9d53a91bd9bd15273cb3db3c9dbe02336
raw0b data B03A B046 86d624fa134201d5a290ea8668029dbab95f41a2e7717999144e12a70a1754d4
raw0b data BD7D BD7F 6193628a00b751aeaf2e188b4d29405346f1ec74da4528a6b110ddbfaf216de9
raw0b data BDF1 BDF5 d336e3b392df397fdb0cedfe097889a4e6b54d83a39efd7f6523c6c6809066a5
raw0b data BED9 BEDB c89c6b9852ba7db757b98b48dd2bf9d2ca9762247ec1aff4bf903aa5cb733435"""

def graph(blob,base,seeds):
    pending=deque(seeds); seen={}; external=[]
    while pending:
        pc=pending.popleft()
        if pc in seen:continue
        assert base<=pc<base+len(blob),(hex(pc),hex(base))
        op=blob[pc-base];assert op in OPS,(hex(pc),hex(op))
        mnemonic,mode,n=OPS[op]
        ins=blob[pc-base:pc-base+n];assert len(ins)==n
        val=ins[1] if n==2 else (ins[1]|ins[2]<<8) if n==3 else None
        if mode=="rel":val=(pc+n+(val if val<128 else val-256))&65535
        seen[pc]=(mnemonic,mode,n,val,ins)
        if mnemonic in BR:pending.extend((val,pc+n))
        elif mnemonic=="JSR":
            pending.append(pc+n)
            if base<=val<base+len(blob):pending.append(val)
            else:external.append((pc,val))
        elif mnemonic=="JMP":
            if mode=="abs":pending.append(val)
            else:external.append((pc,"indirect"))
        elif mnemonic not in TERM:pending.append(pc+n)
        assert len(seen)<=400
    used={x for pc,(_,_,n,_,_) in seen.items() for x in range(pc,pc+n)}
    assert len(used)==sum(row[2] for row in seen.values())
    return seen,used,external

def main(path, output=None):
    rom=Path(path).read_bytes()
    assert hashlib.sha256(rom).hexdigest()==ROM_SHA
    prg=rom[16:16+0x40000];assert len(prg)==0x40000
    b=prg[11*0x4000:12*0x4000];f=prg[31*0x2000:32*0x2000]
    rb=lambda a,n=1:b[a-0x8000:a+n-0x8000]
    rf=lambda a,n=1:f[a-0xE000:a+n-0xE000]
    # Previously verified object writer $B503 sets ID $1B, then resets subscript.
    assert rb(0xB503,5)==bytes.fromhex("a9 1b 9d ef 05")
    assert rb(0xB50D,3)==bytes.fromhex("20 16 b5")
    assert rb(0xB516,5)==bytes.fromhex("a9 00 9d c1 05")
    assert rb(0xBED9,2)==bytes.fromhex("3a b0")
    assert rb(0xB03A,12)==bytes.fromhex("0b 0e 46 00 45 30 00 00 46 00 00 00")
    entries=(0xBD7D,0xBDF1,0xBDF3)
    targets=tuple(int.from_bytes(rb(a,2),"little") for a in entries)
    assert targets==(0x8519,0x965D,0x96B4)
    assert rb(0x8526,3)==bytes.fromhex("4c 57 83")
    assert rb(0x8357,3)==bytes.fromhex("fe c1 05")
    assert rb(0x9688,3)==bytes.fromhex("fe c1 05")
    assert rb(0x96B4,3)==bytes.fromhex("de 1d 06")
    # Five eight-entry tables are selected via AND #$07.
    assert rb(0x9664,6)==bytes.fromhex("8a 65 1b 29 07 a8")
    assert [int.from_bytes(rb(a+1,2),"little") for a in
        (0x966A,0x9670,0x9676,0x967C,0x9682)]==[
            0x968C,0x9694,0x969C,0x96A4,0x96AC]
    # FD1B modulo-12 reduction bounds FD4D,Y to exactly 12 table bytes.
    assert rf(0xFD1B,9)==bytes.fromhex("c9 0c 90 05 e9 0c 4c 1b fd")
    assert rf(0xFD25,3)==bytes.fromhex("b9 4d fd")
    gb,cb,exb=graph(b,0x8000,targets)
    gf,cf,exf=graph(f,0xE000,(0xFC1F,))
    assert len(gb)==71 and len(cb)==169 and exb==[(0x85F2,0xFC1F)]
    assert len(gf)==185 and len(cf)==335 and not exf
    prior_b={i for a,e,_ in BANK0B for i in range(a,e)}
    prior_b.update((0xB394,0xB395))
    assert not cb&prior_b
    assert min(cf)>=0xFB96 and max(cf)<0xFDE4
    zp10=sorted((pc,mn) for pc,(mn,mode,n,val,ins) in gf.items()
        if mn in ("STA","STX","STY","INC","DEC","ASL","LSR","ROL","ROR")
        and mode=="zp" and val==0x10)
    assert zp10==[(0xFBFC,"STA"),(0xFC1F,"STA"),(0xFC4F,"STA"),
                  (0xFCA0,"STY"),(0xFCF9,"STY")]
    assert not any(mn in ("STA","STX","STY","INC","DEC","ASL","LSR","ROL","ROR")
        and mode.startswith("abs") and val>=0x8000
        for mn,mode,n,val,ins in gf.values())
    # DO NOT read/claim data at FD62+Y without a real producer domain.
    assert rf(0xFD18,3)==bytes.fromhex("19 62 fd")
    db=set(range(0x968C,0x96B4))|set(range(0xB03A,0xB046))|set(range(0xBED9,0xBEDB))
    for a in entries:db.update(range(a,a+2))
    df=set(range(0xFD4D,0xFD59))
    assert (len(db),len(df))==(60,12) and not db&cb and not df&cf
    expected=set();manifest=[]
    for row in RANGES.splitlines():
        tag,kind,left,right,digest=row.split()
        a,e=int(left,16),int(right,16)
        blob=f if tag=="fixed31" else b
        base=0xE000 if tag=="fixed31" else 0x8000
        assert hashlib.sha256(blob[a-base:e-base]).hexdigest()==digest,row
        expected.update((tag,kind,x) for x in range(a,e))
        manifest.append({"region":tag,"kind":kind,"start_cpu":left,
            "end_cpu_inclusive":f"{e-1:04X}","length":e-a,"sha256":digest})
    actual=set()
    for tag,code,data in (("raw0b",cb,db),("fixed31",cf,df)):
        actual.update((tag,"code",x) for x in code)
        actual.update((tag,"data",x) for x in data)
    assert actual==expected and len(actual)==576
    manifest.sort(key=lambda x:(x["region"],x["kind"],x["start_cpu"]))
    manifest_sha=hashlib.sha256(json.dumps(manifest,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    assert manifest_sha==EXPECTED_MANIFEST_SHA
    # Global candidate corpus, not a proven live script/action census.
    pointers=[int.from_bytes(rb(0xBEA3+2*i,2),"little") for i in range(0x6B)]
    starts=sorted({p for p in pointers if 0xA4A6<=p<=0xB0DE})
    hist=Counter(rb(a)[0] for a in range(0xA4A6,0xB106,4))
    assert (len(pointers),len(set(pointers)),len(starts))==(107,72,71)
    assert starts[0]==0xA4A6 and starts[-1]==0xB0DE
    assert all((v-u)%4==0 for u,v in zip(starts,starts[1:]))
    assert (sum(hist.values()),len(hist),
        sum(c for op,c in hist.items() if op>=128))==(792,163,73)
    result={"rom_sha256":ROM_SHA,"checkpoint":"0504","strict_new_bytes":576,
        "strict_cumulative_bytes":49399,"manifest_sha256":manifest_sha,
        "code_instructions":{"raw0b":71,"fixed31":185},
        "new_code_bytes":{"raw0b":169,"fixed31":335},
        "new_bounded_data_bytes":{"raw0b":60,"fixed31":12},
        "script_seed":{"id":"1B","pointer":"B03A","actions":["0B","45","46"],
                       "targets":["8519","965D","96B4"]},
        "fixed_zp10_writes":[{"cpu":f"{a:04X}","opcode":m} for a,m in zp10],
        "structural_only":{"directory_ids":107,"distinct_pointers":72,
                           "candidate_starts":71,"candidate_lattice_cells":792,
                           "first_byte_values":163,"highbit_first_bytes":73},
        "open":["$FD62,Y indexed ROM producer domain","runtime path liveness",
                "full AI-script ID/subscript producer domains","final $10 writer"],
        "manifest":manifest}
    if output:Path(output).write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("0504 ROM: PASS",ROM_SHA)
    print("ID $1B / $0B->$45->$46: PASS")
    print("raw bank $0B: 71 starts / 169 new code bytes")
    print("fixed PRG31: 185 starts / 335 new code bytes")
    print("bounded data: 60 banked + 12 fixed; strict new total 576")
    print("five fixed shared-$10 writes:",zp10)
    print("candidate directory: 107 IDs / 72 pointers / 792 unverified lattice cells")
    print("manifest SHA256:",manifest_sha)
    print("unresolved: FD62,Y indexed ROM domain; do NOT invent a bound")
if __name__=="__main__":
    if len(sys.argv) not in (2,3):
        raise SystemExit("usage: audit_ai_script_seed_0504.py JP.nes [report.json]")
    main(sys.argv[1],sys.argv[2] if len(sys.argv)==3 else None)
