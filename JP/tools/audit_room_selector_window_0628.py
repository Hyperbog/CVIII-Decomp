#!/usr/bin/env python3
"""JP0628: instruction-stepped original-ROM room-selector producer/consumer bounds.

This is a CONSIDERED STATIC/CONDITIONAL study, not gameplay liveness proof.
Never promote bytes, infer mapper register history or dereference unsafe targets.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

JP_SHA = '958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
RAW0A_SHA = '1460df577d44e114c64fdf34a8837629765f3f6a93d45796fdf81e5ffacb5ed8'
PTRS = (0xBEA4, 0xBEDB, 0xBF03, 0xBE8B, 0xBF1C)
PRODUCER = bytes.fromhex('a5 30 4a a8 b9 62 bb 8d a0 07 60')
CONSUMER = bytes.fromhex('ad a0 07 0a a8 b9 c2 b8 85 08 b9 c3 b8 85 09')


def mapped(bank: bytes, address: int) -> int:
    if not 0x8000 <= address < 0xC000:
        raise ValueError(f'Bank-switched address outside $8000-$BFFF: ${address:04X}')
    return bank[address-0x8000]


def execute_prefix(bank: bytes, entry: int, ram: bytearray) -> tuple[int,int,int]:
    """Execute exact 6502 source ops up to RTS or B806; no made-up branch paths."""
    pc = entry
    a = y = 0
    steps = 0
    while True:
        if pc == 0xB806 or (entry == 0xBB57 and mapped(bank,pc) == 0x60):
            return pc, a, y
        steps += 1
        if steps > 12:
            raise ValueError('Unexpected producer/consumer control-flow depth')
        op = mapped(bank,pc)
        arg = mapped(bank,pc+1)
        if op == 0xA5:        # LDA zp
            a=ram[arg]; pc+=2
        elif op == 0xAD:      # LDA abs
            addr=arg | (mapped(bank,pc+2)<<8)
            if addr>=len(ram):raise ValueError('Unexpected non-RAM consumer input')
            a=ram[addr];pc+=3
        elif op == 0x4A:      # LSR A
            a>>=1;pc+=1
        elif op == 0x0A:      # ASL A
            a=(a<<1)&255;pc+=1
        elif op == 0xA8:      # TAY
            y=a;pc+=1
        elif op == 0xB9:      # LDA abs,Y
            base=arg | (mapped(bank,pc+2)<<8)
            a=mapped(bank,(base+y)&65535);pc+=3
        elif op == 0x85:      # STA zp
            ram[arg]=a;pc+=2
        elif op == 0x8D:      # STA abs
            addr=arg | (mapped(bank,pc+2)<<8)
            if addr>=len(ram):raise ValueError('Unexpected non-RAM producer write')
            ram[addr]=a;pc+=3
        else:
            raise ValueError(f'Unsupported instruction ${op:02X} at ${pc:04X}')


def authenticate(rom: bytes) -> tuple[bytes,bytes]:
    if len(rom)!=393232 or hashlib.sha256(rom).hexdigest()!=JP_SHA:
        raise ValueError('Not the authenticated retail JP cartridge')
    if rom[:4]!=b'NES\x1a' or rom[4]!=16 or rom[5]!=16:
        raise ValueError('Unexpected original iNES header')
    prg=rom[16:16+262144]
    b01=prg[0x4000:0x8000]
    b0a=prg[0x28000:0x2C000]
    if hashlib.sha256(b0a).hexdigest()!=RAW0A_SHA:
        raise ValueError('Physical raw0A fingerprint changed')
    return b01,b0a


def audit(b01: bytes,b0a: bytes, *, lock_retail: bool) -> dict:
    if len(b01)!=0x4000 or len(b0a)!=0x4000:
        raise ValueError('Both original physical 16 KiB banks required')
    if b01[0xBB57-0x8000:0xBB62-0x8000]!=PRODUCER:
        raise ValueError('raw01:$BB57 original producer instruction bytes differ')
    if b0a[0xB7F7-0x8000:0xB806-0x8000]!=CONSUMER:
        raise ValueError('raw0A:$B7F7 original consumer instruction bytes differ')
    if lock_retail:
        words=tuple(int.from_bytes(b0a[0xB8C2-0x8000+2*i:0xB8C4-0x8000+2*i], 'little') for i in range(5))
        if words!=PTRS:raise ValueError('Known five stream roots changed')
    results=[]
    counts=Counter()
    for selector in range(256):
        ram=bytearray(0x800)
        ram[0x7A0]=selector
        pc,_,y=execute_prefix(b0a,0xB7F7,ram)
        if pc!=0xB806 or y!=((selector<<1)&255):
            raise AssertionError('Original 6502 consumer index differs from 8-bit ASL')
        pointer=ram[8] | (ram[9]<<8)
        independent=(mapped(b0a,0xB8C2+y) | (mapped(b0a,0xB8C3+y)<<8))
        if pointer!=independent:raise AssertionError('Independent table decoder mismatch')
        if pointer in PTRS:
            kind='five_known_stream_roots'
        elif 0x8000<=pointer<=0xBFFF:
            kind='other_in_bank_window_not_validated'
        else:
            kind='outside_bank_window'
        counts[kind]+=1
        results.append((selector,pointer,kind))
    for s,p,k in results[:128]:
        if results[s+128][1:]!=(p,k):raise AssertionError('ASL high-bit mirror broken')
    writers=[]
    for value in range(256):
        ram=bytearray(0x800);ram[0x30]=value
        pc,_,y=execute_prefix(b01,0xBB57,ram)
        if pc!=0xBB61 or y!=value>>1:
            raise AssertionError('Original 6502 producer shift/dispatch differs')
        if ram[0x7A0]!=mapped(b01,0xBB62+(value>>1)):
            raise AssertionError('Independent producer table mismatch')
        writers.append(ram[0x7A0])
    if lock_retail:
        assert dict(counts)=={
            'five_known_stream_roots':10,
            'other_in_bank_window_not_validated':26,
            'outside_bank_window':220}
        assert writers[6]==0x35
        assert results[0x35][1]==0xFF63
        assert [results[i][1] for i in range(5)]==list(PTRS)
    return {
        'schema':1,
        'kind':'original-ROM-bounded-producer-consumer-risk; not gameplay trace',
        'original_rom_sha256':JP_SHA if lock_retail else 'synthetic',
        'producer':'physical raw01:$BB57-$BB61 reads $BB62+(RAM[$30]>>1)',
        'consumer':'physical raw0A:$B7F7-$B805 reads word at $B8C2+((2*$07A0)&$FF)',
        'target':'raw0E $8000-$BFFF requires independent mapper/liveness proof',
        'all_256_selectors':dict(sorted(counts.items())),
        'high_bit_mirror_period':128,
        'conditional_risk_example':{
            'producer_input_ram30':6,
            'producer_output_ram07a0':f'{writers[6]:02X}',
            'consumer_word':f'{results[writers[6]][1]:04X}',
            'pointer_outside_bank_window':not 0x8000<=results[writers[6]][1]<=0xBFFF,
            'independent_live_call_chain_proved':False},
        'five_stream_selector_values':[0,1,2,3,4],
        'additional_selector_values_are_proved_safe':False,
        'new_semantically_certified_prg_bytes':0,
        'runtime_liveness_proved':False}


def smoke() -> None:
    b01=bytearray(b'\xFF'*0x4000)
    b0a=bytearray(b'\xFF'*0x4000)
    b01[0xBB57-0x8000:0xBB62-0x8000]=PRODUCER
    b0a[0xB7F7-0x8000:0xB806-0x8000]=CONSUMER
    b01[0xBB62-0x8000:0xBB62-0x8000+9]=bytes((1,0x1b,2,0x35,0x19,3,0x37,0x1a,0x36))
    for i,p in enumerate(PTRS):
        start=0xB8C2-0x8000+2*i
        b0a[start:start+2]=p.to_bytes(2,'little')
    report=audit(bytes(b01),bytes(b0a),lock_retail=False)
    assert sum(report['all_256_selectors'].values())==256
    assert report['conditional_risk_example']['pointer_outside_bank_window']
    assert report['new_semantically_certified_prg_bytes']==0
    b0a[0xB7F7-0x8000]=0x00
    try:audit(bytes(b01),bytes(b0a),lock_retail=False)
    except ValueError:pass
    else:raise AssertionError('Tampered 6502 consumer was accepted')
    print('PASS JP0628 synthetic instruction-stepped producer/consumer selectors')


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path)
    p.add_argument('--out',type=Path)
    p.add_argument('--smoke',action='store_true')
    args=p.parse_args()
    if args.smoke:smoke();return
    if not args.rom:p.error('--rom is required for authentic ROM findings')
    report=audit(*authenticate(args.rom.read_bytes()),lock_retail=True)
    data=json.dumps(report,indent=2,sort_keys=True)+'\n'
    if args.out:args.out.write_text(data,encoding='utf-8')
    print(data,end='')
    print('PASS JP0628 all 256 selector paths + all 256 conditional producer inputs')


if __name__=='__main__':main()
