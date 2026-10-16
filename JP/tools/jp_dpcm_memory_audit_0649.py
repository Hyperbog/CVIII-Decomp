#!/usr/bin/env python3
"""JP0649 original private DMC byte ranges and mapper24 bank ambiguity.

Source geometry proof ONLY. The cartridge and any raw sample bytes remain
private. This is not live DMA, mapper-register, waveform or input trace parity.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

JP_SHA = '958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
PRG0C = 16 + 12 * 16384
TABLE_CPU = 0xA957
TABLE_SHA = '02d705700fcb42b0b1fa7c5520e54734f8180458265f1286aa132613b4fc6b45'
NTSC=(428,380,340,320,286,254,226,214,190,160,142,128,106,84,72,54)
PAL=(398,354,316,298,276,236,210,198,176,148,132,118,98,78,66,50)

def sha(data:bytes)->str: return hashlib.sha256(data).hexdigest()

def describe(table:bytes)->list[dict]:
    if len(table)!=60:raise ValueError('15 original descriptors require 60 bytes')
    entries=[]
    for i in range(15):
        rate,initial,address,length=table[i*4:i*4+4]
        start=0xC000+address*64
        count=length*16+1
        end=start+count-1
        if start<0xC000 or end>=0xE000:
            raise ValueError(f'entry {i:02X}: DMC reader leaves observed mapper24 $C000 window')
        if count>4081:raise ValueError('unbounded DMC sample size')
        entries.append(dict(command=f'{0x6F+i:02X}',index=i,
            cpu_start=f'{start:04X}',cpu_end=f'{end:04X}',
            byte_count=count,bit_count=count*8,
            rate_index=rate&15,loop=bool(rate&64),irq=bool(rate&128),
            bit_period_ntsc=NTSC[rate&15],bit_period_pal=PAL[rate&15],
            per_pass_cycles_ntsc=count*8*NTSC[rate&15],
            per_pass_cycles_pal=count*8*PAL[rate&15],
            physical_bank8_required=True))
    return entries

def smoke()->None:
    fixture=bytearray(60)
    for i in range(15):
        fixture[i*4] = i
        fixture[i*4+1] = 33
        fixture[i*4+2] = i*8
        fixture[i*4+3] = 1
    cases=describe(bytes(fixture))
    assert len(cases)==15 and cases[0]['cpu_start']=='C000'
    assert cases[-1]['cpu_start']=='DC00' and cases[-1]['cpu_end']=='DC10'
    for offset,val in ((2,0xFF),(3,0xFF)):
        mutated=bytearray(fixture);mutated[offset]=val
        if offset==3:mutated[2]=0x7F
        try: describe(bytes(mutated))
        except ValueError:pass
        else:raise AssertionError('sample crossing $E000 accepted')
    for invalid in (b'',bytes(fixture[:-1]),bytes(fixture+b'\0')):
        try:describe(invalid)
        except ValueError:pass
        else:raise AssertionError('wrong table size accepted')
    assert len(set(NTSC))==16 and len(set(PAL))==16
    print('PASS JP0649 synthetic ROM-free DMC mapping: 15 bounded descriptors, NTSC/PAL and crossing negatives')

def verify_rom(path:Path)->dict:
    data=path.read_bytes()
    if len(data)!=393232 or sha(data)!=JP_SHA:
        raise ValueError('ROM does not match original Japanese Akumajou Densetsu')
    if data[:4]!=b'NES\x1a' or data[4:6]!=bytes((16,16)) or ((data[6]>>4)|(data[7]&0xF0))!=24:
        raise ValueError('mapper24 iNES geometry mismatch')
    # Delegate original ROM opcode/metadata/source integrity, including
    # 15 pointer-chain checks and negative mutations, to existing JP0648.
    from jp_dmc_original_source_0648 import verify_bank
    bank=data[PRG0C:PRG0C+16384]
    table=verify_bank(bank)
    if sha(table)!=TABLE_SHA:raise ValueError('JP0648 canonical DMC source changed')
    rows=describe(table)
    unique={(x['cpu_start'],x['cpu_end']) for x in rows}
    if len(unique)!=8 or sum(x['loop'] for x in rows)!=2 or any(x['irq'] for x in rows):
        raise ValueError('original JP DMC sample grouping/flags unexpectedly changed')
    if min(int(x['cpu_start'],16) for x in rows)!=0xC000 or max(int(x['cpu_end'],16) for x in rows)!=0xDFC0:
        raise ValueError('original JP $C000-$DFC0 DMC span drift')
    return dict(schema='CVIII-JP0649-dpcm-map-v1',rom_sha256=JP_SHA,
                dmc_source_sha256=TABLE_SHA,commands=rows,
                program_count=15,distinct_cpu_spans=len(unique),
                mapper_window='VRC6 $C000-$DFFF: bank8 selected by $C000 register',
                physical_bank_identity_verified=False,
                original_apu_dma_timing_verified=False,
                original_gameplay_audio_verified=False)

def main()->None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--smoke',action='store_true')
    parser.add_argument('--rom',type=Path)
    parser.add_argument('--json',type=Path,help='Owner-private metadata only; never includes sample bytes')
    a=parser.parse_args()
    if not a.smoke and a.rom is None:parser.error('supply --smoke or --rom')
    if a.json and a.rom is None:parser.error('--json requires an authenticated --rom')
    if a.smoke:smoke()
    if a.rom:
        report=verify_rom(a.rom)
        if a.json:a.json.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n',encoding='utf-8')
        print('PASS JP0649 original-JP 15 authentic DMC geometries in 8 unique bounded $C000-$DFFF spans; bank8 intentionally unresolved')
if __name__=='__main__': main()
