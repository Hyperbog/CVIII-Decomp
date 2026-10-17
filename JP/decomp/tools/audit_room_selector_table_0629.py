#!/usr/bin/env python3
"""JP0629: authenticated Japanese ROM nine-entry raw01 producer table census.

Conditional table arithmetic, NOT a runtime predecessor chain, verified
gameplay selector-domain bound or additional strict decompilation credit.
"""
from __future__ import annotations
import argparse,hashlib,json
from collections import Counter
from pathlib import Path

JP='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
TABLE='5dc2cd33cc3315a52720f845da6d9ad4af1b4f18fef32d6bf8629390e1cd6944'
KNOWN={0xBEA4,0xBEDB,0xBF03,0xBE8B,0xBF1C}

def audit(rom:bytes)->dict:
    if len(rom)!=393232 or hashlib.sha256(rom).hexdigest()!=JP:
        raise ValueError('not authenticated JP retail cartridge')
    p=rom[16:16+262144]
    b1=p[0x4000:0x8000]
    ba=p[0x28000:0x2C000]
    at=lambda cpu,length:b1[cpu-0x8000:cpu-0x8000+length]
    if at(0xBB57,11)!=bytes.fromhex('a5 30 4a a8 b9 62 bb 8d a0 07 60'):
        raise ValueError('producer instructions changed')
    cells=at(0xBB62,9)
    if hashlib.sha256(cells).hexdigest()!=TABLE:
        raise ValueError('nine source table bytes changed')
    if at(0xBB6B,6)!=bytes.fromhex('a9 00 85 00 a2 05'):
        raise ValueError('code-like suffix changed')
    if at(0xB877,3)!=bytes.fromhex('4c 6b bb'):
        raise ValueError('alternate JMP $BB6B bytes changed')
    counts=Counter()
    rows=[]
    for value in range(18):
        y=value>>1
        selector=cells[y]
        index=(2*selector)&255
        addr=0xB8C2-0x8000+index
        target=int.from_bytes(ba[addr:addr+2],'little')
        kind=('documented_stream_root' if target in KNOWN
              else 'other_unvalidated_bank_address' if 0x8000<=target<=0xBFFF
              else 'outside_expected_switchable_window')
        counts[kind]+=1
        rows.append({'ram30':f'{value:02X}', 'index':y,
                     'written_07a0':f'{selector:02X}',
                     'conditional_target':f'{target:04X}',
                     'category':kind})
    expected={'documented_stream_root':6,
              'other_unvalidated_bank_address':4,
              'outside_expected_switchable_window':8}
    if dict(counts)!=expected or rows[6]['written_07a0']!='35' or rows[6]['conditional_target']!='FF63':
        raise ValueError('source table classification drift')
    return {
       'schema':1,'kind':'ROM-authenticated conditional nine-entry table study',
       'rom_sha256':JP,'producer_table':'raw01:$BB62-$BB6A',
       'table_sha256':TABLE,'following_candidate_code':'raw01:$BB6B',
       'candidate_JMP_to_after_table':'raw01:$B877 JMP $BB6B',
       'conditional_input_ram30_range':'00-11',
       'conditional_input_classifications':dict(sorted(counts.items())),
       'unvalidated_ram30_range':'12-FF (reads beyond nine identified entries)',
       'rows':rows,
       'runtime_ram30_domain_proved':False,
       'producer_to_room_consumer_path_proved':False,
       'strict_new_prg_bytes':0,
    }

def main()->None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom',required=True,type=Path)
    parser.add_argument('--out',type=Path)
    args=parser.parse_args()
    result=audit(args.rom.read_bytes())
    output=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.out:args.out.write_text(output,encoding='utf-8')
    print(output,end='')

if __name__=='__main__':main()
