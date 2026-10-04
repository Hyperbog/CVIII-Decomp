#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os
from pathlib import Path
from collections import Counter, defaultdict

ROM_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
PRG_SIZE=0x40000
BANK_SIZE=0x2000

OPS={}
def add(o,m,mode,n): OPS[int(o,16)] = (m,mode,int(n))
TABLE='''00 BRK imp 1
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
FE INC absx 3'''
for line in TABLE.splitlines():
    add(*line.split())

BR={'BPL','BMI','BVC','BVS','BCC','BCS','BNE','BEQ'}
CTRL=BR|{'JSR','JMP','RTS','RTI','BRK'}
WRITE={'STA','STX','STY'}
RMW={'INC','DEC','ASL','LSR','ROL','ROR'}
READ={'ORA','AND','EOR','ADC','SBC','BIT','LDA','LDX','LDY','CMP','CPX','CPY'}
MEMMODES={'zp','zpx','zpy','abs','absx','absy','indx','indy','ind'}

def sha(b): return hashlib.sha256(b).hexdigest()

def cpu_views(bank, off):
    out=[]
    if bank == 31:
        out.append(('fixed', 0xE000+off))
    else:
        if bank < 30:
            out.append((f'raw{bank//2:02X}', 0x8000+(bank&1)*0x2000+off))
        out.append(('c000_candidate',0xC000+off))
    return out

def decode_at(bank_bytes, off):
    op=bank_bytes[off]
    if op not in OPS: return None
    mn,mode,n=OPS[op]
    if off+n>len(bank_bytes): return None
    raw=bank_bytes[off:off+n]
    operand=None
    if n==2: operand=raw[1]
    elif n==3: operand=raw[1]|raw[2]<<8
    return mn,mode,n,raw,operand

def fmt_operand(mn,mode,operand,pc=None):
    if mode=='imp': return ''
    if mode=='acc': return 'A'
    if mode=='imm': return f'#$%02X'%operand
    if mode=='zp': return f'$%02X'%operand
    if mode=='zpx': return f'$%02X,X'%operand
    if mode=='zpy': return f'$%02X,Y'%operand
    if mode=='abs': return f'$%04X'%operand
    if mode=='absx': return f'$%04X,X'%operand
    if mode=='absy': return f'$%04X,Y'%operand
    if mode=='indx': return f'($%02X,X)'%operand
    if mode=='indy': return f'($%02X),Y'%operand
    if mode=='ind': return f'($%04X)'%operand
    if mode=='rel':
        if pc is None: return f'rel ${operand:02X}'
        d=operand if operand<0x80 else operand-0x100
        return f'$%04X'%((pc+2+d)&0xFFFF)
    return f'${operand:X}' if operand is not None else ''

def region_for_addr(a):
    if a is None: return ''
    if a < 0x100: return 'zp'
    if a < 0x200: return 'stack'
    if a < 0x2000: return 'cpu_ram_mirror'
    if a < 0x4000: return 'ppu_regs'
    if a < 0x4020: return 'apu_io'
    if a < 0x6000: return 'expansion'
    if a < 0x8000: return 'prg_ram'
    return 'prg_space'

def access_kind(mn):
    if mn in WRITE: return 'write'
    if mn in RMW: return 'readwrite'
    if mn in READ: return 'read'
    return ''

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('rom')
    ap.add_argument('outdir')
    args=ap.parse_args()
    rom=Path(args.rom).read_bytes()
    assert sha(rom)==ROM_SHA, (sha(rom),ROM_SHA)
    assert rom[:4]==b'NES\x1a'
    trainer=512 if rom[6]&4 else 0
    p0=16+trainer
    prg=rom[p0:p0+PRG_SIZE]
    assert len(prg)==PRG_SIZE
    out=Path(args.outdir); out.mkdir(parents=True,exist_ok=True)
    banks_dir=out/'banks'; banks_dir.mkdir(exist_ok=True)

    summary={'schema_version':1,'rom_sha256':ROM_SHA,'prg_size':len(prg),'bank_size':BANK_SIZE,
             'warning':'Candidate decode/xrefs are aggressive whole-ROM scans and are not verified code/data classification.',
             'banks':[], 'global':{}}
    global_counts=Counter(); all_ctrl=[]; all_mem=[]; all_e7=[]; all_zpw=[]

    for bank in range(32):
        b=prg[bank*BANK_SIZE:(bank+1)*BANK_SIZE]
        cand=0; ctrl=[]; mem=[]; e7=[]; zpw=[]
        for off in range(BANK_SIZE):
            d=decode_at(b,off)
            if not d: continue
            cand+=1
            mn,mode,n,raw,operand=d
            views=cpu_views(bank,off)
            view_s=';'.join(f'{k}:${pc:04X}' for k,pc in views)
            if mn in CTRL:
                for vk,pc in views:
                    target=''
                    if mn in BR:
                        rel=operand if operand<0x80 else operand-0x100
                        target=f'{(pc+2+rel)&0xFFFF:04X}'
                    elif mn in {'JSR','JMP'} and mode in {'abs','ind'}:
                        target=f'{operand:04X}'
                    ctrl.append((bank,off,vk,pc,mn,mode,raw.hex().upper(),target))
            ak=access_kind(mn)
            if ak and mode in MEMMODES:
                base=operand
                reg=region_for_addr(base)
                mem.append((bank,off,view_s,mn,mode,raw.hex().upper(),ak,base,reg))
                if ak in {'write','readwrite'} and mode in {'zp','zpx','zpy','indx','indy'}:
                    zpw.append((bank,off,view_s,mn,mode,raw.hex().upper(),base,ak))
            if off+3<=BANK_SIZE and b[off:off+3]==bytes.fromhex('20FBE7'):
                e7.append((bank,off,view_s))
        lines=[]
        lines.append(f'; AUTO-GENERATED LOSSLESS PRG BANK REFERENCE — PRG{bank:02d}')
        lines.append('; Every ROM byte is represented exactly once. This file does NOT classify code vs data.')
        lines.append(f'; ROM SHA-256 {ROM_SHA}')
        lines.append(f'; bank SHA-256 {sha(b)}')
        if bank==31:
            lines.append('; fixed mapping: PRG31:$E000-$FFFF')
        else:
            if bank<30:
                lines.append(f'; canonical raw16 view: raw bank ${bank//2:02X}, CPU ${0x8000+(bank&1)*0x2000:04X}-${0x9FFF+(bank&1)*0x2000:04X}')
            lines.append('; possible $C000-$DFFF mapping is mapper-state dependent and is NOT asserted here.')
        lines.append('')
        for off in range(0,BANK_SIZE,16):
            chunk=b[off:off+16]
            views=cpu_views(bank,off)
            tags=' / '.join(f'{k}:${pc:04X}' for k,pc in views)
            bs=', '.join(f'${x:02X}' for x in chunk)
            lines.append(f'PRG{bank:02d}_{off:04X}: .byte {bs} ; {tags}')
        lines.append('')
        lines.append('; Candidate-control summary (aggressive byte-offset scan; false positives expected)')
        for r in ctrl:
            _,off,vk,pc,mn,mode,rawhex,target=r
            optext=fmt_operand(mn,mode, int(rawhex[2:4],16) if len(rawhex)==4 else (int(rawhex[2:4],16)|(int(rawhex[4:6],16)<<8) if len(rawhex)==6 else None), pc)
            lines.append(f'; +{off:04X} {vk}:${pc:04X} {rawhex:<6} {mn} {optext}' + (f' -> ${target}' if target else ''))
        if e7:
            lines.append('')
            lines.append('; Exact byte-pattern candidates for JSR $E7FB (semantic validity requires code proof)')
            for _,off,views in e7: lines.append(f'; +{off:04X} {views}')
        (banks_dir/f'prg{bank:02d}.asm').write_text('\n'.join(lines)+'\n',encoding='utf-8')

        bankinfo={'bank':bank,'sha256':sha(b),'official_opcode_candidates':cand,
                  'control_candidates':len(ctrl),'memory_candidates':len(mem),
                  'zp_write_candidates':len(zpw),'e7fb_bytepattern_candidates':len(e7),
                  'reference_file':f'banks/prg{bank:02d}.asm'}
        summary['banks'].append(bankinfo)
        global_counts.update({'official_opcode_candidates':cand,'control_candidates':len(ctrl),'memory_candidates':len(mem),'zp_write_candidates':len(zpw),'e7fb_bytepattern_candidates':len(e7)})
        all_ctrl.extend(ctrl); all_mem.extend(mem); all_e7.extend(e7); all_zpw.extend(zpw)

    summary['global']=dict(global_counts)
    fixed=prg[31*BANK_SIZE:]
    summary['vectors']={name: fixed[o]|(fixed[o+1]<<8) for name,o in [('NMI',0x1FFA),('RESET',0x1FFC),('IRQ',0x1FFE)]}

    with (out/'control_flow_candidates.tsv').open('w',encoding='utf-8') as f:
        f.write('bank\toffset\tview\tcpu\tmnemonic\tmode\tbytes\ttarget\n')
        for r in all_ctrl: f.write('\t'.join(str(x) if not isinstance(x,int) else (f'{x:04X}' if x>31 else str(x)) for x in r)+'\n')
    with (out/'memory_access_candidates.tsv').open('w',encoding='utf-8') as f:
        f.write('bank\toffset\tviews\tmnemonic\tmode\tbytes\taccess\tbase\tregion\n')
        for bank,off,views,mn,mode,raw,ak,base,reg in all_mem:
            f.write(f'{bank}\t{off:04X}\t{views}\t{mn}\t{mode}\t{raw}\t{ak}\t{base:04X}\t{reg}\n')
    with (out/'zp_write_candidates.tsv').open('w',encoding='utf-8') as f:
        f.write('bank\toffset\tviews\tmnemonic\tmode\tbytes\tbase\taccess\n')
        for bank,off,views,mn,mode,raw,base,ak in all_zpw:
            f.write(f'{bank}\t{off:04X}\t{views}\t{mn}\t{mode}\t{raw}\t{base:02X}\t{ak}\n')
    with (out/'e7fb_call_candidates.tsv').open('w',encoding='utf-8') as f:
        f.write('bank\toffset\tviews\n')
        for bank,off,views in all_e7: f.write(f'{bank}\t{off:04X}\t{views}\n')

    focus={0x10:'zp10',0x18:'zp18',0x2C:'zp2c',0x68:'zp68'}
    focus_rows=defaultdict(list)
    for row in all_mem:
        bank,off,views,mn,mode,raw,ak,base,reg=row
        if mode in {'zp','zpx','zpy','indx','indy'} and base in focus:
            focus_rows[base].append(row)
    summary['focus_candidate_counts']={f'{a:02X}':len(rows) for a,rows in focus_rows.items()}
    for a,name in focus.items():
        with (out/f'{name}_candidates.tsv').open('w',encoding='utf-8') as f:
            f.write('bank\toffset\tviews\tmnemonic\tmode\tbytes\taccess\tbase\n')
            for bank,off,views,mn,mode,raw,ak,base,reg in focus_rows[a]:
                f.write(f'{bank}\t{off:04X}\t{views}\t{mn}\t{mode}\t{raw}\t{ak}\t{base:02X}\n')

    (out/'manifest.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')

    quick=[]
    quick += ['WHOLE-PRG QUICK REFERENCE — Akumajou Densetsu JP','',
              f'ROM SHA-256 {ROM_SHA}',
              'WARNING: candidate scans are aggressive and are not verified code/data classification.','',
              'BANK HASHES']
    for bi in summary['banks']:
        quick.append(f"PRG{bi['bank']:02d} {bi['sha256']} control={bi['control_candidates']} mem={bi['memory_candidates']} zpwrite={bi['zp_write_candidates']} e7fb={bi['e7fb_bytepattern_candidates']}")
    for fn,title in [('e7fb_call_candidates.tsv','E7FB BYTE-PATTERN CANDIDATES'),
                     ('zp10_candidates.tsv','ZP $10 CANDIDATE REFERENCES'),
                     ('zp18_candidates.tsv','ZP $18 CANDIDATE REFERENCES'),
                     ('zp2c_candidates.tsv','ZP $2C CANDIDATE REFERENCES'),
                     ('zp68_candidates.tsv','ZP $68 CANDIDATE REFERENCES')]:
        quick += ['',title]
        quick += (out/fn).read_text(encoding='utf-8').splitlines()
    (out/'MASTER_REFERENCE.txt').write_text('\n'.join(quick)+'\n',encoding='utf-8')

    md=['# Whole-PRG static atlas','',
        'Generated from the authoritative JP ROM. **Candidate scans are intentionally aggressive and may decode data as instructions.** ROM bytes and later semantic audits remain authoritative.','',
        f'- ROM SHA-256: `{ROM_SHA}`',f'- PRG bytes: `{len(prg)}`',f'- physical banks: `32 x 8 KiB`',
        f"- vectors: NMI `${summary['vectors']['NMI']:04X}`, RESET `${summary['vectors']['RESET']:04X}`, IRQ `${summary['vectors']['IRQ']:04X}`",'',
        '## Generated indexes','',
        '- `control_flow_candidates.tsv` — candidate branches/JSR/JMP/returns from every byte offset.','- `memory_access_candidates.tsv` — candidate memory reads/writes/RMW.','- `zp_write_candidates.tsv` — zero-page write/RMW candidates, including indexed forms.','- `e7fb_call_candidates.tsv` — exact `20 FB E7` byte-pattern locations.','- `zp10_candidates.tsv`, `zp18_candidates.tsv`, `zp2c_candidates.tsv`, `zp68_candidates.tsv` — focused candidate references for current high-value state bytes.','- `banks/prgXX.asm` — lossless `.byte` listing for every physical 8 KiB PRG bank plus candidate-control comments.','',
        '## Bank summary','', '| PRG | SHA-256 | opcode candidates | control | memory | ZP writes | E7FB patterns |','|---:|---|---:|---:|---:|---:|---:|']
    for bi in summary['banks']:
        md.append(f"| {bi['bank']:02d} | `{bi['sha256'][:16]}…` | {bi['official_opcode_candidates']} | {bi['control_candidates']} | {bi['memory_candidates']} | {bi['zp_write_candidates']} | {bi['e7fb_bytepattern_candidates']} |")
    md += ['', '## Interpretation rule','', 'These files accelerate search and hypothesis generation. An entry is **not verified code** merely because an official opcode can be decoded at that byte offset. Promotion to verified decompilation still requires control-flow / producer-domain / mapper-context evidence from the JP ROM.','']
    (out/'README.md').write_text('\n'.join(md),encoding='utf-8')

    paths=sorted(p for p in out.rglob('*') if p.is_file())
    h=hashlib.sha256()
    for p in paths:
        rel=p.relative_to(out).as_posix().encode(); data=p.read_bytes(); h.update(rel+b'\0'+hashlib.sha256(data).digest())
    print('ROM',ROM_SHA)
    print('banks',32)
    print('generated files',len(paths))
    print('aggregate candidate counts',dict(global_counts))
    print('focus counts',summary['focus_candidate_counts'])
    print('generated-set digest',h.hexdigest())

if __name__=='__main__': main()
