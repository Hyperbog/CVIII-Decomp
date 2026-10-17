#!/usr/bin/env python3
"""JP0640: static physical raw01 direct-call bridge, not gameplay liveness.

No inference that fixed helpers preserve mapper state, or that a candidate
password/selector route ever joins raw0A B7F7 during retail play.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROM_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
RAW01_SHA='8199a7b3cb99e175b7554fc2d8e4ccd593b953aea82b9d636aa881c919391f6d'
CALLER_SHA='159459f13cb3b5ce1d27c0fee8d636b7ccbead3b6e9507f8d86cc744f361e806'
TABLE_SHA='5dc2cd33cc3315a52720f845da6d9ad4af1b4f18fef32d6bf8629390e1cd6944'
OPWIDTH={0xC0:2,0xA9:2,0x20:3,0xE6:2,0x85:2,0x4C:3}
CALLS={0xB7F3:0xE249,0xB7F8:0xB3F7,0xB7FB:0xB855,0xB7FE:0xB8A0,
       0xB801:0xB87A,0xB804:0xB4BB,0xB807:0xB877,0xB80A:0xB296}

def decoded(code:bytes,start:int)->list[tuple[int,int,bytes]]:
    rows=[]
    offset=0
    while offset<len(code):
        pc=start+offset
        op=code[offset]
        width=OPWIDTH.get(op)
        if width is None or offset+width>len(code):
            raise ValueError('unknown/truncated source opcode at $%04X' % pc)
        rows.append((pc,op,code[offset:offset+width]))
        offset+=width
    return rows

def audit(bank:bytes)->dict:
    if len(bank)!=0x4000 or hashlib.sha256(bank).hexdigest()!=RAW01_SHA:
        raise ValueError('physical raw01 bank identity mismatch')
    def read(pc:int,count:int)->bytes:
        if pc<0x8000 or pc+count>0xC000:
            raise ValueError('CPU window outside raw01 physical mapping')
        return bank[pc-0x8000:pc-0x8000+count]
    code=read(0xB7EF,0xB814-0xB7EF)
    if hashlib.sha256(code).hexdigest()!=CALLER_SHA:
        raise ValueError('parent direct-caller source hash changed')
    rows=decoded(code,0xB7EF)
    if len(rows)!=14 or rows[-1][0]!=0xB811:
        raise ValueError('caller instruction boundary drift')
    calls={pc:raw[1]|(raw[2]<<8) for pc,op,raw in rows if op==0x20}
    if calls!=CALLS:
        raise ValueError('direct JSR targets in physical raw01 changed')
    if [(pc,raw) for pc,op,raw in rows if op==0x4C]!=[
            (0xB811,bytes.fromhex('4c 2b b6'))]:
        raise ValueError('caller tail JMP changed')
    if read(0xB877,3)!=bytes.fromhex('4c 6b bb'):
        raise ValueError('B877 JMP after nine-cell table changed')
    if read(0xBB6B,6)!=bytes.fromhex('a9 00 85 00 a2 05'):
        raise ValueError('BB6B candidate code prefix changed')
    if hashlib.sha256(read(0xBB62,9)).hexdigest()!=TABLE_SHA:
        raise ValueError('nine-cell producer table changed')
    for target,actual in ((0xB87A,0xB801),(0xB877,0xB807)):
        sig=bytes((0x20,target&255,target>>8))
        seen=[0x8000+i for i in range(len(bank)-2) if bank[i:i+3]==sig]
        if seen!=[actual]:
            raise ValueError('literal callsite census changed')
    return dict(schema=1,physical='JP:Mapper24:raw01',
        bound='raw01 B7EF-B813 original instruction boundaries',
        direct_jsr_count=len(CALLS),
        direct_B87A_callsite='raw01:$B801',
        B87A_next_instruction='raw01:$B804',
        direct_B877_callsite='raw01:$B807',
        candidate_entry='raw01:$B877 JMP $BB6B',
        distinct_nine_cell_boundary='raw01:$BB62-$BB6A',
        code_like_suffix='raw01:$BB6B',
        raw01_bank_sha256=RAW01_SHA,
        direct_callsite_census_limited_to_literal_JSR=True,
        entry_executed_by_original_game=False,
        callee_mapper_restoration_proved=False,
        alternative_indirect_callers_excluded=False,
        raw0A_producer_consumer_link_proved=False,
        new_strict_prg_bytes=0)

def smoke()->None:
    source=bytes.fromhex('a9 00 20 7a b8 e6 19 4c 2b b6')
    rows=decoded(source,0xB7F1)
    assert [r[0] for r in rows]==[0xB7F1,0xB7F3,0xB7F6,0xB7F8]
    for bad in (source[:-1],source[:2]+bytes((0x02,))+source[3:]):
        try:decoded(bad,0xB7F1)
        except ValueError:continue
        raise AssertionError('source boundary corruption accepted')
    print('PASS JP0640 ROM-free 6502 caller opcode boundaries and truncation rejection')

def main()->None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path)
    p.add_argument('--out',type=Path)
    p.add_argument('--smoke',action='store_true')
    a=p.parse_args()
    if a.smoke:smoke();return
    if a.rom is None:p.error('--rom required to authenticate original retail source')
    rom=a.rom.read_bytes()
    if len(rom)!=393232 or rom[:4]!=b'NES\x1a' or hashlib.sha256(rom).hexdigest()!=ROM_SHA:
        raise ValueError('original Japanese cartridge mismatch')
    report=audit(rom[16+0x4000:16+0x8000])
    result=json.dumps(report,indent=2,sort_keys=True)+'\n'
    if a.out:a.out.write_text(result,encoding='utf-8')
    print(result,end='')

if __name__=='__main__':main()
