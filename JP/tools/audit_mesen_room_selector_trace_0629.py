#!/usr/bin/env python3
"""JP0629: validate owner-only Mesen2 RAM $07A0 producer/consumer event logs.

An observed session remains scenario-specific. Synthetic smoke proves ONLY
the parser's safety contract. No automatic byte certification or R-002 closure.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from collections import Counter
from pathlib import Path

JP='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
ROOTS={0xBEA4,0xBEDB,0xBF03,0xBE8B,0xBF1C}
FORMAT=re.compile(r'^JP0629_EVT (\d+) ([PWC]) ([0-9A-F]{4}) ([0-9A-F]{5}) ([0-9A-F]{2}) ([0-9A-F]{2}) ([0-9A-F]{4}) (\d+)$')
SOURCE={'P':(0xBB57,0x07B57,1),'C':(0xB7F7,0x2B7F7,10)}

def rom_prg(data:bytes)->bytes:
    if len(data)!=393232 or hashlib.sha256(data).hexdigest()!=JP or data[:4]!=b'NES\x1a':
        raise ValueError('must use authenticated original JP ROM')
    return data[16:16+262144]

def source_pointer(prg:bytes,value:int)->int:
    address=0x28000+0xB8C2-0x8000+((2*value)&255)
    return int.from_bytes(prg[address:address+2],'little')

def parse(log:str,prg:bytes)->dict:
    lines=[s[s.index('JP0629_'):].strip() for s in log.splitlines() if 'JP0629_' in s]
    if len(lines)<2 or lines[0]!='JP0629_BEGIN 1':
        raise ValueError('missing single Mesen session header')
    if not lines[-1].startswith('JP0629_END '):
        raise ValueError('missing complete script-ended footer')
    if any(s.startswith(('JP0629_TRUNCATED','JP0629_STATE_LOADED',
                         'JP0629_MAPPING_ERROR')) for s in lines):
        raise ValueError('truncated, interrupted or invalid physical mapping')
    if lines.count('JP0629_BEGIN 1')!=1 or sum(s.startswith('JP0629_END ') for s in lines)!=1:
        raise ValueError('multiple sessions')
    records=[]
    last_cycle=-1
    for ordinal,line in enumerate(lines[1:-1],1):
        m=FORMAT.fullmatch(line)
        if not m:raise ValueError('invalid event format')
        seq,kind,pc,physical,bank,value,aux,cycle=m.groups()
        row=dict(seq=int(seq),kind=kind,pc=int(pc,16),physical=int(physical,16),
                 bank=int(bank,16),value=int(value,16),aux=int(aux,16),cycle=int(cycle))
        if row['seq']!=ordinal or row['cycle']<last_cycle or row['aux']>65535:
            raise ValueError('event sequence/cycle order violated')
        last_cycle=row['cycle']
        if kind in SOURCE:
            if (row['pc'],row['physical'],row['bank'])!=SOURCE[kind]:
                raise ValueError('execution is NOT in the required original physical ROM bank')
        if kind=='C' and row['aux']!=source_pointer(prg,row['value']):
            raise ValueError('Mesen pointer does not match authenticated JP ROM')
        if kind!='C' and row['aux']>255:
            raise ValueError('invalid prior RAM byte')
        records.append(row)
    try:n=int(lines[-1][len('JP0629_END '):])
    except ValueError as exc:raise ValueError('invalid footer count') from exc
    if n!=len(records):raise ValueError('missing events or incorrect footer')
    counts=Counter(r['kind'] for r in records)
    last_write=None
    recent_entry=None
    links=[]
    for row in records:
        if row['kind']=='P':
            recent_entry=row
        elif row['kind']=='W':
            last_write=row
        else:
            candidate=last_write is not None and last_write['value']==row['value']
            links.append({
                'consumer_seq':row['seq'],
                'selector':f"{row['value']:02X}",
                'pointer':f"{row['aux']:04X}",
                'last_matching_write_seq':last_write['seq'] if candidate else None,
                'raw01_store_physical_hint':bool(candidate and last_write['physical']==0x07B5E and last_write['bank']==1),
                'raw01_entry_precedes_write':bool(candidate and recent_entry and recent_entry['seq']<last_write['seq']),
                'complete_runtime_predecessor_proved':False,
            })
    return {
        'schema':1,'rom_sha256':JP,
        'status':'MESEN_LOG_FORMAT_VALIDATED_NOT_AUTOMATIC_GAMEPLAY_CERTIFICATION',
        'event_counts':{k:counts[k] for k in ('P','W','C')},
        'consumer_selectors':sorted({f"{e['value']:02X}" for e in records if e['kind']=='C'}),
        'known_stream_roots_at_consumer':sum(e['aux'] in ROOTS for e in records if e['kind']=='C'),
        'outside_expected_bank_window':sum(not 0x8000<=e['aux']<=0xBFFF for e in records if e['kind']=='C'),
        'chronological_predecessor_candidates':links[:100],
        'candidates_omitted':max(0,len(links)-100),
        'trace_record_count':len(records),
        'script_callback_write_pc_may_be_post_operand':True,
        'observed_gameplay_independent_emulator_verified':False,
        'r002_closed':False,'strict_new_prg_bytes':0,
    }

def smoke()->None:
    prg=bytearray(262144)
    offset=0x28000+0xB8C2-0x8000+0x35*2
    prg[offset:offset+2]=(0xFF63).to_bytes(2,'little')
    orig='\n'.join((
        'JP0629_BEGIN 1',
        'JP0629_EVT 1 P BB57 07B57 01 06 0000 100',
        'JP0629_EVT 2 W BB5E 07B5E 01 35 0000 120',
        'JP0629_EVT 3 C B7F7 2B7F7 0A 35 FF63 140',
        'JP0629_END 3',''))
    res=parse(orig,bytes(prg))
    assert res['event_counts']=={'P':1,'W':1,'C':1}
    assert res['outside_expected_bank_window']==1
    assert res['r002_closed'] is False and res['strict_new_prg_bytes']==0
    broken=(orig.replace('07B57','09B57'),
            orig.replace('2B7F7 0A','2B7F7 01'),
            orig.replace('35 FF63','35 0000'),
            orig.replace('JP0629_END 3','JP0629_END 4'),
            orig.replace('JP0629_END 3','JP0629_TRUNCATED\nJP0629_END 3'),
            orig.replace('JP0629_END 3','JP0629_STATE_LOADED\nJP0629_END 3'),
            orig.replace('JP0629_END 3','JP0629_MAPPING_ERROR\nJP0629_END 3'),
            orig.replace('JP0629_EVT 2 W','JP0629_EVT 4 W'),
            orig.replace('0000 120','0000 90'),orig[:-13])
    for sample in broken:
        try:parse(sample,bytes(prg))
        except ValueError:pass
        else:raise AssertionError('bad Mesen trace accepted')
    empty=parse('JP0629_BEGIN 1\nJP0629_END 0\n',bytes(prg))
    assert empty['event_counts']['C']==0
    print('PASS JP0629 ROM-free Mesen event log source/mapping/ordering regression')

def main()->None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--smoke',action='store_true')
    p.add_argument('--rom',type=Path)
    p.add_argument('--trace',type=Path)
    p.add_argument('--out',type=Path)
    a=p.parse_args()
    if a.smoke:smoke();return
    if not a.rom or not a.trace:p.error('--rom and --trace required')
    result=parse(a.trace.read_text(encoding='utf-8'),rom_prg(a.rom.read_bytes()))
    output=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if a.out:a.out.write_text(output,encoding='utf-8')
    print(output,end='')

if __name__=='__main__':main()
