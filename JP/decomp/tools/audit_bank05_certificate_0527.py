#!/usr/bin/env python3
"""Recover exact 04FB-04FD raw-VRC6 bank05 historical strict-PRG spans.

Each region was previously admitted under producer-validated bank-05 script
roots and parser state (not CPU opcode disassembly). This script reconstructs
physical provenance, never adds strict credit before full previous mask parity.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
JP_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
PRG_SIZE=262144
# SHA-locked history: RESUME_STATE.json at git 711c0ee21c27 (04FB),
# 4f35c4789e4c (04FC), 5cfbacc99d01 (04FD).
BANK05=[
    ('04FB',0x87AE,0x9A6B,'58f4a24e41ba95766529e1eaa531c63fc666ca51abc668ec4eb3ba3f4e50eb6b'),
    ('04FC',0x9A6B,0xAD97,'3d34329fd18b7c713f1fe35206868f1b6c0bdfb6127f664410a60fd54a8c46f0'),
    ('04FD',0xAD97,0xBF06,'30f4e1640f97c342886a4d5f1a652cbfda41102abbd4760501bcd2915b474a72'),
]
def bank05_regions():
    rows=[]
    for checkpoint,begin,end,digest in BANK05:
        if not 0x8000 <= begin < end <= 0xC000:raise ValueError('Bank 05 address outside mapper window')
        off=5*16384 + begin-0x8000
        rows.append({'checkpoint':checkpoint,'offset':off,'length':end-begin,
                     'sha256':digest,'kind':'source-verified script data'})
    if [r['length'] for r in rows]!=[4797,4908,4463]:raise ValueError('historical lengths drift')
    if rows[0]['offset']+rows[0]['length']!=rows[1]['offset'] or rows[1]['offset']+rows[1]['length']!=rows[2]['offset']:
        raise ValueError('historical spans not contiguous')
    return rows

def mask(rows):
    m=bytearray(PRG_SIZE)
    for r in rows:
        a,b=r['offset'],r['offset']+r['length']
        if not (0<=a<b<=PRG_SIZE) or any(m[a:b]):raise ValueError('physical overlap or invalid boundary '+str(r))
        m[a:b]=b'\x01'*(b-a)
    return m

def audit(rom=None,only_bank05=False):
    early=bank05_regions()
    if only_bank05:rows=early
    else:
        # Compatible with the committed 0525/0526 public audit APIs.
        import audit_historical_prg_0526 as prior
        import audit_prg_recomp_0525 as first
        rows=early+prior.historical()+first.certified()
    union=mask(rows)
    expected=14168 if only_bank05 else 22085
    expected_n=3 if only_bank05 else 79
    if len(rows)!=expected_n or sum(union)!=expected:
        raise ValueError('04FB-0508 physical union changed')
    source_overlap=None
    if not only_bank05:
        import audit_prg_recomp_0525 as first
        native=mask(first.source_windows())
        known=sum(a and b for a,b in zip(native,union))
        unknown=sum(a and not b for a,b in zip(native,union))
        if (sum(native),known,unknown)!=(1365,626,739):
            raise ValueError('0510-0517 differential source provenance changed')
        source_overlap={'inventory_bytes':1365,'already_in_known_mask':626,
                        'outside_known_mask_unproven_global_novelty':739}
    if rom:
        original=Path(rom).read_bytes()
        if len(original)!=393232 or hashlib.sha256(original).hexdigest()!=JP_SHA:
            raise ValueError('Wrong original Akumajou Densetsu JP ROM')
        prg=original[16:16+PRG_SIZE]
        for r in rows:
            original_bytes=prg[r['offset']:r['offset']+r['length']]
            if hashlib.sha256(original_bytes).hexdigest()!=r['sha256']:
                raise ValueError('Original physical certificate SHA failure '+str(r))
    return {
        'schema':'JP-bank05-historical-certificate/v1','original_rom_sha256':JP_SHA,
        'original_rom_verified':bool(rom),'bank05_04FB_04FD_bytes':14168,
        'bank05_historical_intervals':3,'combined_physical_intervals':expected_n,
        'combined_physically_mapped_historical_bytes':expected,
        'remaining_pre_04FB_historical_floor_without_physical_map':49504-expected,
        'cumulative_strict_prg_floor_unchanged':49504,
        'physical_mask_sha256':hashlib.sha256(union).hexdigest(),
        'native_0510_0517_overlap':source_overlap,
        'new_global_strict_bytes_promoted':0,
        'warning':'Historical byte-location recovery; original script-data proof, not 6502 instruction reassembly; earlier 27419-byte physical mask still missing',
    }

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path)
    p.add_argument('--only-bank05',action='store_true')
    p.add_argument('--report',type=Path)
    args=p.parse_args()
    result=audit(args.rom,args.only_bank05)
    if args.report:args.report.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('PASS 04FB-04FD bank05 recovered:',result['combined_physically_mapped_historical_bytes'],
          'source-certified physical PRG bytes in',result['combined_physical_intervals'],'spans; strict 49504 unchanged')
