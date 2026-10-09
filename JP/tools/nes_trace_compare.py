#!/usr/bin/env python3
"""Compare independent NES CPU register logs without asserting emulator parity.

Supports Nintendulator/nestest preinstruction text and explicit JSONL records.
No PRG bytes or disassembly text are exported; only register/mapping differences.
Reference: https://forums.nesdev.org/viewtopic.php?p=241032
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import re

STATES=('pc','a','x','y','p','sp')
PREFIX=re.compile(r'^\s*(?:\d+:\s*)?([0-9A-Fa-f]{4})\s',re.ASCII)
REGS={k:re.compile(r'\b'+k.upper()+r':([0-9A-Fa-f]{2})\b',re.ASCII) for k in ('a','x','y','p','sp')}
CYC=re.compile(r'\bCYC:\s*(\d+)\b',re.ASCII)

def parse_nestest(text:str)->dict:
    m=PREFIX.search(text)
    if m is None:raise ValueError('cannot parse PC from Nintendulator/nestest line')
    result={'pc':int(m.group(1),16)}
    for k,rx in REGS.items():
        v=rx.search(text)
        if v is None:raise ValueError(f'missing {k} from reference line')
        result[k]=int(v.group(1),16)
    cy=CYC.search(text)
    if cy:result['cycles']=int(cy.group(1))
    return result

def parse_json_line(text:str)->dict:
    item=json.loads(text)
    if not isinstance(item,dict):raise ValueError('trace row must be an object')
    result={}
    for k in STATES:
        if k not in item:raise ValueError(f'missing {k} in JSONL row')
        v=item[k]
        if isinstance(v,int) and not isinstance(v,bool):n=v
        elif isinstance(v,str):
            # Hex strings are explicitly hexadecimal; bare int types are decimal.
            n=int(v,16)
        else:raise ValueError(f'invalid {k} type')
        if not 0<=n<=(65535 if k=='pc' else 255):raise ValueError(f'{k} out of range')
        result[k]=n
    for k in ('cycles','prg_bank'):
        if k in item:
            n=item[k]
            if isinstance(n,bool) or not isinstance(n,int) or n<0:raise ValueError(f'invalid {k}')
            result[k]=n
    return result

def rows(path:str,style:str):
    parser={'nestest':parse_nestest,'jsonl':parse_json_line}[style]
    with open(path,encoding='utf-8') as handle:
        for line_num,line in enumerate(handle,1):
            if not line.strip():continue
            try:yield parser(line.rstrip('\n'))
            except (ValueError,json.JSONDecodeError) as exc:
                raise ValueError(f'{Path(path).name}:{line_num}: {exc}') from exc

def fingerprint(path:str)->str:
    s=hashlib.sha256()
    with open(path,'rb') as h:
        for chunk in iter(lambda:h.read(1<<20),b''):s.update(chunk)
    return s.hexdigest()

def compare(reference:str,candidate:str,ref_format='nestest',candidate_format='jsonl',
            *,compare_cycles=False,ignore_virtual_p=False,limit_examples=16)->dict:
    if not 0<=limit_examples<=1024:raise ValueError('limit_examples out of range')
    keys=list(STATES)
    if compare_cycles:keys.append('cycles')
    count=0;different=0;examples=[];first=None
    for idx,(r,c) in enumerate(itertools.zip_longest(rows(reference,ref_format),rows(candidate,candidate_format)),1):
        if r is None or c is None:
            different+=1
            if first is None:first=idx
            if len(examples)<limit_examples:
                examples.append({'instruction_number':idx,'difference':'trace-length mismatch',
                                 'reference_exists':r is not None,'candidate_exists':c is not None})
            continue
        count+=1
        fields=[]
        for k in keys:
            if k not in r or k not in c:
                raise ValueError(f'cannot compare {k}: not supplied by both traces')
            rv,cv=r[k],c[k]
            if k=='p' and ignore_virtual_p:rv&=0xCF;cv&=0xCF
            if rv!=cv:fields.append(k)
        if 'prg_bank' in r and 'prg_bank' in c and r['prg_bank']!=c['prg_bank']:
            fields.append('prg_bank')
        if fields:
            different+=1
            if first is None:first=idx
            if len(examples)<limit_examples:
                examples.append({'instruction_number':idx,'fields':fields,
                    'reference':{k:r.get(k) for k in fields},
                    'candidate':{k:c.get(k) for k in fields}})
    return {'schema':'shared-nes-cpu-trace-compare/v1',
        'reference_log_sha256':fingerprint(reference),'candidate_log_sha256':fingerprint(candidate),
        'reference_format':ref_format,'candidate_format':candidate_format,
        'matched':different==0 and count>0,
        'instruction_pairs_compared':count,'disagreeing_or_unpaired_rows':different,
        'first_mismatch_instruction':first,'mismatches':examples,
        'fields_compared':keys,'prg_bank_compared_if_present_on_both':True,
        'p_virtual_bits_masked':ignore_virtual_p,
        'scope':'register trace format comparison only; logs not independently validated as genuine hardware/reference output',
        'new_strict_prg_bytes':0}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('reference');p.add_argument('candidate')
    p.add_argument('--reference-format',choices=('nestest','jsonl'),default='nestest')
    p.add_argument('--candidate-format',choices=('nestest','jsonl'),default='jsonl')
    p.add_argument('--compare-cycles',action='store_true')
    p.add_argument('--ignore-virtual-p-bits',action='store_true')
    p.add_argument('--out');a=p.parse_args()
    result=compare(a.reference,a.candidate,a.reference_format,a.candidate_format,
        compare_cycles=a.compare_cycles,ignore_virtual_p=a.ignore_virtual_p)
    txt=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if a.out:Path(a.out).write_text(txt)
    else:print(txt,end='')
    return 0 if result['matched'] else 1
if __name__=='__main__':raise SystemExit(main())
