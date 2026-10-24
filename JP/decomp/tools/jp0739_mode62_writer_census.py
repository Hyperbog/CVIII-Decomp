#!/usr/bin/env python3
"""JP0739 bounded, ROM-locked candidate $62 direct-writer inventory.

NOT a runtime write trace. Byte hits may be data/operands; indirect,
indexed or aliased writes may be missed. Zero new source-credit claim.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

JP_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
PRG_SIZE=262144
# Writer opcode physical PRG offset, mapped 16K bank, constant if proven,
# immediately preceding original CPU opcode sequence and bounded role.
SITES=(
 (0x386E2,0x0E,1,'A9 01 85 62','edge-mode candidate'),
 (0x386F8,0x0E,0,'A9 00 85 62','room-position candidate'),
 (0x38748,0x0E,1,'A9 01 85 62','player-edge candidate'),
 (0x3877D,0x0E,0,'A9 00 85 62','left-boundary candidate'),
 (0x3936E,0x0E,2,'A9 02 85 62','action-dispatch candidate'),
 (0x39C11,0x0E,2,'A9 02 85 62','action-dispatch candidate'),
 (0x39C54,0x0E,2,'A9 02 85 62','action-dispatch candidate'),
 (0x3A58D,0x0E,2,'A9 02 85 62','action-dispatch candidate'),
 (0x3C997,0x0F,None,'B9 32 CA 85 62','table mode candidate'),
 (0x3C99C,0x0F,2,'A9 02 85 62','fixed mode 2 candidate'),
 (0x3CA08,0x0F,0,'A2 00 A9 F8 86 62','fixed X=0 candidate'),
)
STORE={'85 62':'STA $62','86 62':'STX $62','84 62':'STY $62'}

def cpu(offset):
    base=0xC000 if offset//0x4000==15 else 0x8000
    return f'{base+(offset%0x4000):04X}'

def analyze(prg):
    if len(prg)!=PRG_SIZE:raise ValueError('need 256KiB PRG')
    hits=[]
    for text,op in STORE.items():
        pattern=bytes.fromhex(text)
        start=0
        while (n:=prg.find(pattern,start))>=0:
            hits.append({'physical_prg_offset':f'{n:05X}',
                         'bank16':f'{n//0x4000:02X}',
                         'cpu_address_candidate':cpu(n),
                         'opcode_candidate':op})
            start=n+1
    hits.sort(key=lambda r:int(r['physical_prg_offset'],16))
    contexts=[]
    for loc,bank,value,hexcode,role in SITES:
        begin=loc-(3 if hexcode.startswith('B9 ') else
                   4 if hexcode.startswith('A2 ') else 2)
        code=bytes.fromhex(hexcode)
        if prg[begin:begin+len(code)]!=code or loc//0x4000!=bank:
            raise ValueError(f'original source candidate guard failed at {loc:05X}')
        if prg[loc:loc+2] not in (b'\x85\x62',b'\x86\x62'):
            raise ValueError('wrong store opcode')
        contexts.append({'physical_prg_offset':f'{loc:05X}',
                         'cpu_address_candidate':cpu(loc),
                         'bank16':f'{bank:02X}',
                         'constant_if_statically_known':value,
                         'candidate_role':role,
                         'local_sha256':hashlib.sha256(code).hexdigest()})
    return {
        'schema':'JP0739-original-ROM-$62-static-writer-inventory/v1',
        'verified_candidate_neighborhoods':contexts,
        'raw_direct_byte_hit_counts':dict(Counter(x['opcode_candidate'] for x in hits)),
        'raw_direct_byte_hits':hits,
        'first_incorrect_runtime_write_identified':False,
        'reason':'JP0718 original events omit $62/action/vertical RAM writes; JP0719 native has periodic RAM, not mapped-CPU write events',
        'possible_unobserved_writes':'indexed, aliased, indirect, opcode operand/data matches',
        'source_credit':{'vpp':31,'strict_prg_bytes':49504,
                         'strict_prg_total':262144,'new_credit':0},
    }

def smoke():
    data=bytearray(PRG_SIZE)
    for loc,_,_,hexcode,_ in SITES:
        code=bytes.fromhex(hexcode)
        start=loc-(3 if hexcode.startswith('B9 ') else
                   4 if hexcode.startswith('A2 ') else 2)
        data[start:start+len(code)]=code
    assert len(analyze(bytes(data))['verified_candidate_neighborhoods'])==11
    bad=bytearray(data);bad[0x386E2]=0
    try:analyze(bytes(bad))
    except ValueError:pass
    else:raise AssertionError('bad original source gate accepted')
    print('PASS JP0739 synthetic ROM opcode context and fail-closed gate (not live writes)')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--smoke',action='store_true')
    parser.add_argument('--rom',type=Path)
    a=parser.parse_args()
    if a.smoke:smoke();return
    if not a.rom:parser.error('--rom required')
    rom=a.rom.read_bytes()
    if (len(rom)!=393232 or hashlib.sha256(rom).hexdigest()!=JP_SHA
            or rom[:4]!=b'NES\x1a' or ((rom[6]>>4)|(rom[7]&0xf0))!=24):
        raise ValueError('original Japanese Mapper24 ROM fingerprint mismatch')
    result=analyze(rom[16:16+PRG_SIZE])
    result['original_rom_authenticated']=True
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=='__main__':main()
