#!/usr/bin/env python3
"""Bulk, bank-qualified JP decomp/recomp source generator. Requires original ROM.

Uses the original 0501 authenticated 6502 CFG plus human-authored 0525/0526
mnemonic modules. All other PRG bytes remain explicitly UNCLASSIFIED .byte;
CHR is graphical data. Reassembles all 393232 retail-ROM bytes exactly.
Not a new strict-byte certificate, and not playable native recompilation.
"""
from __future__ import annotations
import argparse, hashlib, json
from collections import deque
from pathlib import Path
import audit_nmi_fixed_scheduler_banked as proof
import test_recomp_6502_0525 as p25
import test_recomp_6502_0526 as p26
import lift_fixed_dispatch_0530 as d30
import lift_bank05_scripts_0531 as data31
import lift_bank04_parser_0532 as data32
import lift_bank0c_sound_0533 as data33

ROOT=Path(__file__).resolve().parents[1]
OP={(mn.lower(),mode):byte for byte,(mn,mode,n) in proof.OPS.items()}
BR={x.lower() for x in proof.BR}
ENDS={x.lower() for x in proof.TERM}
SIZES={mode:n for (mn,mode),byte in OP.items() for _m,_mo,n in [proof.OPS[byte]]}
SIZES['rel']=2
BASE={'raw09':0x09*0x4000,'raw0A':0x0a*0x4000,'raw0B':0x0b*0x4000,'fixed31':31*0x2000}
SRC={'actor_tail_0525.asm':('raw0B',p25.compile_source),
     'fixed_tail_0525.asm':('fixed31',p25.compile_source),
     'fixed_scheduler_0526.asm':('fixed31',p26.assemble),
     'raw0b_callbacks_0526.asm':('raw0B',p26.assemble)}
ROOTS={'fixed31':[0xfde4],'raw09':[0x8001],'raw0A':[0x84ea],
       'raw0B':[0x80e3,0xb1f8,0xbd11,0x8001,0x8161,0x826c]}
RANGES={'fixed31':proof.FIXED_NEW,'raw09':proof.BANK09,
        'raw0A':proof.BANK0A,'raw0B':proof.BANK0B}
COUNTS={'fixed31':161,'raw09':479,'raw0A':57,'raw0B':1338}

def digest(b):return hashlib.sha256(b).hexdigest()
def raw_value(s,labels):
    if s.startswith('$'):return int(s[1:],16)
    if s in labels:return labels[s]
    raise ValueError('Unknown 6502 label '+s)
def mode_of(m,a):
    if not a:return 'imp'
    if a=='a':return 'acc'
    if m in BR:return 'rel'
    if a.startswith('#'):return 'imm'
    if a.startswith('(') and a.endswith(',x)'):return 'indx'
    if a.startswith('(') and a.endswith('),y'):return 'indy'
    if a.startswith('(') and a.endswith(')'):return 'ind'
    if a.endswith(',x'):return 'zpx' if len(a[:-2].lstrip('$'))<=2 else 'absx'
    if a.endswith(',y'):return 'zpy' if len(a[:-2].lstrip('$'))<=2 else 'absy'
    return 'zp' if a.startswith('$') and len(a[1:])<=2 else 'abs'
def numeric_token(a,mode):
    if mode=='imm':return a[1:]
    if mode in ('zpx','zpy','absx','absy'):return a[:-2]
    if mode in ('indx','indy'):return a[1:-3]
    if mode=='ind':return a[1:-1]
    return a

def assemble(src,base,length):
    """Two-pass source compiler with real 6502 opcodes and symbolic labels."""
    labels={};nodes=[];pc=None;limit=base+length
    for ln,text in enumerate(src.splitlines(),1):
        s=text.split(';',1)[0].strip().lower()
        if not s:continue
        if s.startswith('.equ '):
            name,value=[x.strip() for x in s[5:].split(',',1)]
            if name in labels:raise ValueError('Duplicate equ '+name)
            labels[name]=int(value[1:],16);continue
        if s.startswith('.org '):
            pc=int(s[5:].replace('$','0x'),16)
            if not base<=pc<=limit:raise ValueError('Bad .org')
            continue
        if s.endswith(':'):
            if pc is None or s[:-1] in labels:raise ValueError('Bad label '+s)
            labels[s[:-1]]=pc;continue
        if pc is None:raise ValueError('Missing .org')
        mn,*rest=s.split(None,1);a=rest[0].strip() if rest else ''
        if mn=='.byte':n=len(a.split(','))
        elif mn=='.word':n=2*len(a.split(','))
        else:
            mode=mode_of(mn,a)
            if (mn,mode) not in OP:raise ValueError('Unknown NMOS opcode/mode '+str((mn,mode,ln)))
            n=SIZES[mode]
        if pc+n>limit:raise ValueError('Cross-bank instruction')
        nodes.append((pc,mn,a));pc+=n
    buf=bytearray(length);occupied=bytearray(length)
    for pc,mn,a in nodes:
        if mn in ('.byte','.word'):
            payload=[]
            for word in a.split(','):
                n=raw_value(word.strip(),labels)
                if mn=='.byte':
                    if not 0<=n<=255:raise ValueError('.byte overflow')
                    payload.append(n)
                else:
                    if not 0<=n<=0xffff:raise ValueError('.word overflow')
                    payload.extend((n&255,n>>8))
        else:
            mode=mode_of(mn,a);payload=[OP[mn,mode]]
            if mode not in ('imp','acc'):
                n=raw_value(numeric_token(a,mode),labels)
                if mode=='rel':
                    n-=pc+2
                    if not -128<=n<=127:raise ValueError('Branch out of range')
                    n&=255
                if SIZES[mode]==2:
                    if not 0<=n<=255:raise ValueError('8-bit operand overflow')
                    payload.append(n)
                else:
                    if not 0<=n<=0xffff:raise ValueError('16-bit operand overflow')
                    payload.extend((n&255,n>>8))
        offset=pc-base
        for j,n in enumerate(payload):
            if occupied[offset+j]:raise ValueError('Duplicated bank byte')
            occupied[offset+j]=1;buf[offset+j]=n
    if not all(occupied):raise ValueError('Generated bank has a byte hole')
    return bytes(buf)

def decode(prg,bank,pc):
    off=BASE[bank]+pc-(0xe000 if bank=='fixed31' else 0x8000)
    opcode=prg[off]
    if opcode not in proof.OPS:raise ValueError(f'0501 unknown opcode {bank}:${pc:04X}')
    mn,mode,n=proof.OPS[opcode];src=prg[off:off+n]
    if len(src)!=n:raise ValueError('End-of-ROM opcode')
    arg=src[1] if n==2 else (src[1]|src[2]<<8) if n==3 else None
    if mode=='rel':arg=(pc+2+(arg if arg<0x80 else arg-256))&0xffff
    return (mn.lower(),mode,n,arg)

def cfg(prg):
    graphs={}
    for bank,roots in ROOTS.items():
        seen={};q=deque(roots)
        lo=0xe000 if bank=='fixed31' else 0x8000
        hi=0x10000 if bank=='fixed31' else 0xc000
        while q:
            pc=q.popleft()
            if bank=='raw0B' and pc==0xb974:continue # flag-proven unreachable
            if pc in seen or not lo<=pc<hi:continue
            mn,mode,n,arg=decode(prg,bank,pc);seen[pc]=(mn,mode,n,arg)
            if bank=='fixed31' and pc==0xfe95:
                if (mn,arg)!=('jsr',0xe7fb):raise ValueError('Changed dispatcher')
                q.extend((0xfe9e,0xfeb1,0xfec6));continue
            if mn in ENDS:continue
            if mn in BR:q.extend((pc+n,arg))
            elif mn=='jmp':
                if mode!='ind':q.append(arg)
            elif mn=='jsr':
                if bank!='fixed31' and arg==0xe7fb:continue # inline dispatch data, unresolved
                q.extend((arg,pc+n))
            else:q.append(pc+n)
        code=set()
        for pc,(_,mode,n,_) in seen.items():
            span=set(range(pc,pc+n))
            if code&span:raise ValueError('Overlapping original 0501 instructions')
            code|=span
        tested=set(x for a,b,_ in RANGES[bank] for x in range(a,b))
        if bank=='fixed31':
            code.update(range(0xfe98,0xfe9e)) # 3 inline pointers, data
            if not tested<=code or len(code-tested)!=69:raise ValueError('Prior fixed-code closure drift')
        elif code!=tested:raise ValueError(f'0501 {bank} graph does not match verified byte spans')
        if len(seen)!=COUNTS[bank]:raise ValueError('0501 instruction starts drift')
        for a,b,h in RANGES[bank]:
            off=BASE[bank]+a-lo
            if digest(prg[off:off+b-a])!=h:raise ValueError('Original 0501 range SHA mismatch')
        graphs[bank]=seen
    return graphs

def mnemonic(mn,mode,arg):
    if mode=='imp':return mn
    if mode=='acc':return mn+' a'
    if mode=='imm':return f'{mn} #${arg:02X}'
    if mode=='rel':return f'{mn} ${arg:04X}'
    if mode in ('zp','zpx','zpy','indx','indy'):
        v=f'${arg:02X}'
    else:v=f'${arg:04X}'
    if mode in ('zpx','absx'):v+=',x'
    if mode in ('zpy','absy'):v+=',y'
    if mode=='indx':v='('+v+',x)'
    if mode=='indy':v='('+v+'),y'
    if mode=='ind':v='('+v+')'
    return mn+' '+v

def handwritten():
    groups={};labels={};count=0
    for name,(bank,compile_source) in SRC.items():
        path=ROOT/'recomp'/name;code=compile_source(path);count+=len(code)
        fragments=[];g=None
        for line in path.read_text(encoding='ascii').splitlines():
            clean=line.split(';',1)[0].strip().lower()
            if clean.startswith('.org '):
                if g is not None:fragments.append(g)
                g={'a':int(clean.split()[1][1:],16),'lines':[],'src':name}
            elif g is not None:g['lines'].append(line)
        if g:fragments.append(g)
        for idx,f in enumerate(fragments):
            end=f['a'];stop=fragments[idx+1]['a'] if idx+1<len(fragments) else 0x10000
            while end<stop and end in code:end+=1
            f['b']=end
            if f['a']==end:
                for x in f['lines']:
                    clean=x.split(';',1)[0].strip()
                    if clean.endswith(':'):labels.setdefault(bank,[]).append((clean[:-1],end))
            else:groups.setdefault(bank,[]).append(f)
    if count!=403:raise ValueError('Handwritten 0525/0526 source drift')
    return groups,labels,count

def generate_sources(rom,out):
    if len(rom)!=393232 or digest(rom)!=proof.ROM_SHA:raise ValueError('Incorrect original JP retail ROM')
    prg=rom[16:16+262144];chrrom=rom[16+262144:]
    graphs=cfg(prg);fragments,labels,manual=handwritten()
    # Extend the 0501-only CFG with historic 04FE/04FF/0500 authenticated
    # fixed-bank dispatch handlers and typed inline pointer data.
    more,dispatch_tables,early_stats=d30.lift(prg)
    for pc,ins in more.items():
        if pc in graphs['fixed31'] and graphs['fixed31'][pc]!=ins:
            raise ValueError('Fixed-bank graph instruction conflict')
        graphs['fixed31'][pc]=ins
    fragments.setdefault('fixed31',[]).extend(dispatch_tables)
    script_fragment,script_stats=data31.lift(prg)
    fragments.setdefault('raw05',[]).append(script_fragment)
    bulk_0532,stats_0532=data32.lift(prg)
    for bank,region_list in bulk_0532.items():
        fragments.setdefault(bank,[]).extend(region_list)
    bank0c_0533,stats_0533=data33.classify(prg)
    fragments.setdefault('raw0C',[]).extend(bank0c_0533)
    by_bank={};newbytes=0;new_instructions=0
    for bank,graph in graphs.items():
        old=set(x for f in fragments.get(bank,[]) for x in range(f['a'],f['b']))
        outstanding=[]
        for pc,(mn,mode,n,arg) in sorted(graph.items()):
            used=set(range(pc,pc+n))
            if used&old:
                if not used<=old:raise ValueError('Partial overlap with handwritten instruction')
                continue
            outstanding.append((pc,mn,mode,n,arg));newbytes+=n;new_instructions+=1
        by_bank[bank]=len(outstanding)
        group=None
        for pc,mn,mode,n,arg in outstanding:
            if group is None or group['b']!=pc:
                group={'a':pc,'b':pc,'src':'0501 mapped code graph','lines':[]}
                fragments.setdefault(bank,[]).append(group)
            group['lines'].append('    '+mnemonic(mn,mode,arg));group['b']=pc+n
    if newbytes!=6749 or manual+newbytes+154!=7306:raise ValueError('0529+0530 lift did not reproduce audited source byte counts')
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    specs=[(f'prg_raw{b:02x}',f'raw{b:02X}',0x8000,0x4000,b*0x4000) for b in range(15)]
    specs += [('prg_fixed30','fixed30',0xc000,0x2000,30*0x2000),
              ('prg_fixed31','fixed31',0xe000,0x2000,31*0x2000)]
    stats=[];claimed=0
    for filename,bank,base,n,offset in specs:
        blob=prg[offset:offset+n];parts=sorted(fragments.get(bank,[]),key=lambda f:f['a'])
        lines=[f'; JP {filename}, physical PRG offset ${offset:06X}',
               '; 6502 source: original verified mapped code only.',
               '; UNCLASSIFIED .byte ranges are not semantic decompilation.']
        for name,address in labels.get(bank,[]):lines.append(f'.equ {name}, ${address:04X}')
        lines.append(f'.org ${base:04X}')
        pc=base;recognized=0
        def fallback(begin,end):
            if begin==end:return
            lines.append(f'; UNCLASSIFIED ${begin:04X}-${end-1:04X}')
            for i in range(begin,end,16):
                lines.append('    .byte '+','.join(f'${x:02X}' for x in blob[i-base:min(i+16,end)-base]))
        for f in parts:
            a,b=f['a'],f['b']
            if not base<=a<b<=base+n or a<pc:raise ValueError('Bank-qualified source group overlap')
            fallback(pc,a)
            lines.extend((f'; VERIFIED {f["src"]}',f'.org ${a:04X}'))
            lines.extend(f['lines']);recognized+=b-a;pc=b
        fallback(pc,base+n)
        source='\n'.join(lines)+'\n'
        if assemble(source,base,n)!=blob:raise ValueError('Wrong reassembled PRG bank '+bank)
        (out/(filename+'.asm')).write_text(source,encoding='ascii')
        stats.append({'bank':filename,'symbolic':recognized,'unclassified':n-recognized,'sha256':digest(blob)})
        claimed+=recognized
    for bank in range(8):
        raw=chrrom[bank*16384:(bank+1)*16384]
        src=f'; JP CHR {bank}, 16KiB graphics not CPU code\n.org $0000\n'
        src+='\n'.join('    .byte '+','.join(f'${x:02X}' for x in raw[i:i+16]) for i in range(0,16384,16))+'\n'
        if assemble(src,0,16384)!=raw:raise ValueError('CHR source roundtrip mismatch')
        (out/f'chr_{bank:02x}.asm').write_text(src,encoding='ascii')
    rebuilt=rom[:16]+b''.join(assemble((out/(filename+'.asm')).read_text(),base,n)
                     for filename,bank,base,n,off in specs)+b''.join(
        assemble((out/f'chr_{bank:02x}.asm').read_text(),0,16384) for bank in range(8))
    if rebuilt!=rom:raise ValueError('Whole cartridge recompilation incorrect')
    if claimed!=48028:raise ValueError('0533 miscounted source classified bytes (expected 41401+6627)')
    manifest={'schema':'jp-0533-whole-cart-metadata-and-interpreter-source/v1','original_sha256':proof.ROM_SHA,
              'source_files':25,'prg_bytes_reassembled':262144,'chr_bytes_reassembled':131072,
              '0530_fixed_dispatch_evidence':early_stats,
              '0531_bank05_script_evidence':script_stats,
              '0532_bank04_and_parser_evidence':stats_0532,
              '0533_bank0c_sound_and_interpreter_evidence':stats_0533,
              '0533_new_interpreter_6502_bytes':1599,
              '0533_sound_metadata_bytes':1505,
              '0533_sound_stream_pool_bytes':3523,
              '0533_new_classified_prg_bytes':6627,
              '0532_new_parser_opcode_operand_bytes':5148,
              '0532_new_parser_local_data_bytes':747,
              '0532_new_script_data_bytes':14032,
              '0532_new_classified_prg_bytes':19927,
              'total_prg_classified_code_table_and_script_bytes':claimed,
              'total_authenticated_script_data_bytes':28200,
              'additional_source_linked_bank0c_stream_pool_bytes':3523,
              'total_sound_script_and_bounded_stream_pool_bytes':31723,
              'symbolic_6502_and_typed_data_bytes':16305,'symbolic_6502_instruction_bytes':13893,
              'total_verified_inline_pointer_bytes':160,
              'additional_parser_lookup_and_local_data_bytes':747,
              'total_dispatch_parser_and_sound_metadata_bytes':2412,
              'new_mnemonic_bytes_since_0529':2719,'new_symbolic_bytes_since_0529':2873,
              'reused_handwritten_bytes':manual,'unclassified_prg_bytes':262144-claimed,
              'total_new_instruction_count':new_instructions,'new_by_bank':by_bank,
              'new_typed_dispatch_table_bytes':154,
              'extra_0530_symbolic_bytes':2873,
              'prg_banks':stats,'new_strict_certified_prg_bytes':0,
              'limit':'Original certified 04FE/04FF/0500/0501 source, not newly proven runtime parity or novel strict coverage.'}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print('PASS original JP whole cartridge 393232/393232 bytes, 25 bank sources')
    print('PASS 0533 original 6502 source 13893; tables/local/metadata 2412; original scripts 28200; sound pool 3523; total classified',claimed)
    return manifest

def smoke():
    sample='.org $8000\nentry:\n    lda #$81\n    sta $05\n    lda $0005,x\n    lda $05,x\n    lda ($02),y\n    bne entry\n'
    code=assemble(sample,0x8000,13)
    assert code==bytes.fromhex('A9 81 85 05 BD 05 00 B5 05 B1 02 D0 F3'),code.hex()
    data32.smoke()
    data33.smoke()
    print('PASS ROM-free 6502 assembler branch/indexing/zero-page smoke')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path);p.add_argument('--out',type=Path)
    p.add_argument('--smoke',action='store_true');a=p.parse_args()
    if a.smoke:smoke()
    else:
        if not a.rom or not a.out:p.error('both --rom and --out required, or --smoke')
        generate_sources(a.rom.read_bytes(),a.out)
