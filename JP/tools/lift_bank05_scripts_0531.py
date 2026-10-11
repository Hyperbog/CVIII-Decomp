#!/usr/bin/env python3
"""Typed, original-metadata-rooted JP raw bank05 script source (14,168 bytes).

Unlike NMOS 6502 instructions, these are original parser commands/operands.
The original 04FB/04FC/04FD audits proved control/operand span closure.
Emit meaningful ROM-metadata-indexed symbol addresses for all 72 roots;
never imply the bytes are CPU instructions or new strict verification credit.
"""
from __future__ import annotations
from collections import defaultdict
import hashlib

ROM_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
WINDOWS=[
 ('04FB',0x87AE,0x9A6B,'58f4a24e41ba95766529e1eaa531c63fc666ca51abc668ec4eb3ba3f4e50eb6b'),
 ('04FC',0x9A6B,0xAD97,'3d34329fd18b7c713f1fe35206868f1b6c0bdfb6127f664410a60fd54a8c46f0'),
 ('04FD',0xAD97,0xBF06,'30f4e1640f97c342886a4d5f1a652cbfda41102abbd4760501bcd2915b474a72'),
]
ROOT_SHA='70bdd50aaae10a4806c2d6bd537ecb37b5a1229d74bc8941e6c4a37af12000a7'
REFS_SHA='74b04a7df06cc803c86b57de74243346c1a0885c6db6336d1f5e155f5e9e42b0'

def digest(x):return hashlib.sha256(x).hexdigest()

def lift(prg):
    if len(prg)!=262144:raise ValueError('JP PRG 256KiB required')
    b5=prg[5*0x4000:6*0x4000]
    meta=prg[12*0x4000:13*0x4000]
    def r05(addr,n=1):
        if not 0x8000<=addr<0xc000 or addr+n>0xc000:raise ValueError('bank05 script exceeds mapper window')
        return b5[addr-0x8000:addr-0x8000+n]
    def r0c(addr,n=1):
        if not 0x8000<=addr<0xc000 or addr+n>0xc000:raise ValueError('raw0C original metadata pointer out of range')
        return meta[addr-0x8000:addr-0x8000+n]
    for stage,start,end,expected in WINDOWS:
        if digest(r05(start,end-start))!=expected:raise ValueError(stage+' original ROM source differs')
    ptrs=[int.from_bytes(r0c(0x8f60+2*i,2),'little') for i in range(0x7d)]
    refs=[]
    for sid,ptr in enumerate(ptrs,1):
        if r0c(ptr)[0]!=5:continue
        count=r0c(ptr+1)[0]+1
        record=r0c(ptr,2+count*3)
        for j in range(count):
            mode=record[2+3*j]
            address=int.from_bytes(record[3+3*j:5+3*j],'little')
            if not 0x87ae<=address<0xbf06:raise ValueError('Original bank05 reference escaped admitted script span')
            if r05(address)[0]<0x10 or mode in (5,6):raise ValueError('Script metadata incompatible with original parser proof')
            refs.append((sid,mode,address))
    roots=sorted(set(a for _,_,a in refs))
    if len(refs)!=84 or len(roots)!=72 or roots[0]!=0x87ae or roots[-1]!=0xbee8:
        raise ValueError('Historical bank05 root counts changed')
    if digest(('\n'.join(f'{a:04X}' for a in roots)).encode())!=ROOT_SHA:
        raise ValueError('Original bank05 root identity changed')
    if digest(('\n'.join(f'{sid:02X},{mode:02X},{a:04X}' for sid,mode,a in refs)).encode())!=REFS_SHA:
        raise ValueError('Original metadata reference order changed')
    by_addr=defaultdict(list)
    for sid,mode,a in refs:by_addr[a].append((sid,mode))
    lines=['; Original JP raw bank05 script commands and operand bytes, provenance 04FB-04FD.',
           '; Source typed as parser script stream, NOT NMOS 6502 code.',
           '; 84 producer-certified raw0C metadata references map to 72 roots.']
    for idx,a in enumerate(roots):
        end=roots[idx+1] if idx+1<len(roots) else 0xbf06
        refs_text=', '.join(f'stage ${sid:02X} mode ${mode:02X}' for sid,mode in by_addr[a])
        lines.append(f'; ${a:04X}-${end-1:04X}; original metadata: {refs_text}')
        lines.append(f'Bank05_Script_{a:04X}:')
        for offset in range(a,end,16):
            lines.append('    .byte '+','.join(f'${v:02X}' for v in r05(offset,min(16,end-offset))))
    fragment={'a':0x87ae,'b':0xbf06,'src':'04FB-04FD producer-bound bank05 scripts','lines':lines}
    return fragment,{'authenticated_script_data_bytes':14168,'script_roots':72,
                     'metadata_refs':84,'original_script_metadata_sha256':REFS_SHA,
                     'kind':'original JP alternate parser command/operand stream, not 6502 code'}
