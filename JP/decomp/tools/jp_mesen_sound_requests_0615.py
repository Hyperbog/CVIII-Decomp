#!/usr/bin/env python3
"""JP0615: compare original Mesen2 E249 execution with owner native requests.

Only a single power-on epoch and matching scripted inputs are comparable.
Identical command registers != audio, game, or CPU-cycle parity.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import tempfile
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"recomp"/"tools"))
import jp_audio_session_verify_0614 as session

JP='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
AGENT='95bcda9d4ff6428937183093386d993649c2d740273871ced78217d3d8f234d0'
CORE='fa0e7af858dce0171f5857837f8cad92090078c354631ce74f8279185df97bd1'
FIELDS=('cycle','pc','command','x','y','s','p','tracked_prg_bank','stack_next_lo','stack_next_hi')
REGEX=re.compile(r'^JP0615_REQ ([0-9]+) E249 ((?:[A-F0-9]{2} ){7}[A-F0-9]{2})$')
MAX_EVENTS=20000

def digest(data:bytes)->str:return hashlib.sha256(data).hexdigest()

def check_binaries(rom:Path, emulator:Path)->None:
    source=rom.read_bytes()
    if len(source)!=393232 or digest(source)!=JP:
        raise ValueError('wrong original Japanese ROM')
    # Explicit original raw-$0A / PRG21 caller signatures. Physical bytes,
    # not a proof these callers are live in the reference route.
    prg=source[16:16+262144]
    for pc,command in ((0xB0C8,0x06),(0xB1CE,0x6A),(0xB58C,0x6B)):
        at=21*8192+pc-0xA000
        if prg[at:at+5]!=bytes((0xA9,command,0x20,0x49,0xE2)):
            raise ValueError('Original raw-$0A sound caller changed')
    for name,want in (('mesen-agent',AGENT),('MesenCore.so',CORE)):
        if digest((emulator/name).read_bytes())!=want:
            raise ValueError('unrecognized independent Mesen2 binary: '+name)

def reference(stdout:str)->list[dict[str,str]]:
    events=[];all_rows=[]
    for line in stdout.splitlines():
        if not line.strip():continue
        obj=json.loads(line)
        if not isinstance(obj,dict):raise ValueError('not a Mesen-agent JSONL record')
        all_rows.append(obj)
    load=[r for r in all_rows if r.get('event')=='loaded']
    finish=[r for r in all_rows if r.get('event')=='summary']
    if (len(load)!=1 or len(finish)!=1 or
        load[0].get('mesen_version')!='2.1.1' or load[0].get('console')!='Nes' or
        not finish[0].get('ok') or finish[0].get('reason')!='frame_limit'):
        raise ValueError('Mesen original-ROM execution not positively completed')
    prev=-1
    for item in all_rows:
        if item.get('event')!='lua_log':continue
        if item.get('error_count',0):raise ValueError('Mesen Lua callback failure')
        for line in item.get('text','').splitlines():
            if line.startswith('JP0615_TRUNCATED'):
                raise ValueError('Mesen E249 capture truncated')
            if not line.startswith('JP0615_REQ'):continue
            m=REGEX.fullmatch(line)
            if m is None or len(events)>=MAX_EVENTS:
                raise ValueError('Malformed/excessive Mesen E249 request line')
            cyc=int(m.group(1));parts=m.group(2).split()
            if cyc<prev or cyc>2**64-1:
                raise ValueError('Mesen request cycles nonmonotonic')
            prev=cyc
            row=dict(zip(FIELDS,(str(cyc),'E249',*parts)))
            events.append(row)
    if not events:raise ValueError('Mesen never executed JP fixed E249')
    return events

def native(folder:Path)->list[dict[str,str]]:
    verified=session.verify(folder)
    if len(verified['epochs'])!=1 or verified['epochs'][0]['event']!='power_on':
        raise ValueError('Original reference gate needs one native power-on epoch')
    data=(folder/'CVIII-Sound-Requests.csv').read_bytes()
    rows=session.rows(data,FIELDS)
    if not rows or len(rows)>MAX_EVENTS:
        raise ValueError('Empty/excessive native sound request sequence')
    return rows

def compare(ref:list[dict[str,str]], cand:list[dict[str,str]])->dict:
    # Source clocks need not share the same power-on offset. No absolute
    # cycle equality is inferred; compare successive deltas descriptively.
    names=('pc','command','x','y','s','tracked_prg_bank','stack_next_lo','stack_next_hi')
    mismatches=[]
    for i in range(max(len(ref),len(cand))):
        if i>=len(ref) or i>=len(cand):
            if len(mismatches)<12:mismatches.append({'index':i,'kind':'missing_event'})
            continue
        bad=[k for k in names if ref[i][k].upper()!=cand[i][k].upper()]
        # Ignore virtual P bits 4 and 5 (6502 B and constant-1 flags).
        if int(ref[i]['p'],16)&0xCF != int(cand[i]['p'],16)&0xCF:bad.append('p_mask_CF')
        if bad and len(mismatches)<12:mismatches.append({'index':i,'fields':bad})
    actual_mismatch=(len(ref)!=len(cand) or bool(mismatches))
    deltas_same=(len(ref)==len(cand) and all(
        int(ref[i]['cycle'])-int(ref[i-1]['cycle'])==
        int(cand[i]['cycle'])-int(cand[i-1]['cycle'])
        for i in range(1,len(ref))))
    return {'schema':'CVIII-JP-independent-E249-compare/v1',
            'reference_requests':len(ref),'native_requests':len(cand),
            'request_register_sequence_matches':not actual_mismatch,
            'request_interval_cycle_deltas_match':deltas_same,
            'first_mismatches':mismatches,
            'source':'Mesen2 Mesen-agent Lua exec callback and JP0614 native session',
            'whole_CPU_PPU_audio_parity_proven':False,
            'sound_SFX_ownership_proven':False,'new_strict_PRG_bytes':0}

def smoke()->None:
    rows=[dict(zip(FIELDS,('10','E249','6B','00','01','FD','24','0A','90','B5'))),
          dict(zip(FIELDS,('30','E249','10','02','01','FE','20','0C','00','00')))]
    capture={'event':'lua_log','error_count':0,'text':'\n'.join(
        'JP0615_REQ '+ ' '.join((r['cycle'],'E249',*(r[f] for f in FIELDS[2:])))
        for r in rows)}
    text='\n'.join(json.dumps(r) for r in (
        {'event':'loaded','mesen_version':'2.1.1','console':'Nes'},
        capture,{'event':'summary','ok':True,'reason':'frame_limit'}))
    ref=reference(text)
    assert compare(ref,rows)['request_register_sequence_matches']
    assert compare(ref,rows)['request_interval_cycle_deltas_match']
    broken=[dict(v) for v in rows];broken[1]['command']='11'
    assert not compare(ref,broken)['request_register_sequence_matches']
    variants=(text.replace('2.1.1','2.0.0'),text.replace('JP0615_REQ','JP0615_TRUNCATED'),
              text.replace('"ok": true','"ok": false'))
    for v in variants:
        try:reference(v)
        except ValueError:continue
        raise AssertionError('Accepted untrusted original reference')
    print('PASS JP0615 Mesen exec-callback request comparison and 4 failure paths')

def main()->None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--smoke',action='store_true')
    p.add_argument('--rom',type=Path)
    p.add_argument('--emulator',type=Path)
    p.add_argument('--native-dir',type=Path)
    p.add_argument('--mesen-stdout',type=Path)
    p.add_argument('--json',type=Path)
    a=p.parse_args()
    if a.smoke:smoke();return
    if not all((a.rom,a.emulator,a.native_dir,a.mesen_stdout)):
        p.error('--rom, --emulator, --native-dir, --mesen-stdout required')
    check_binaries(a.rom,a.emulator)
    result=compare(reference(a.mesen_stdout.read_text(encoding='utf-8')),
                   native(a.native_dir))
    result['rom_sha256_verified']=True
    result['mesen_binaries_sha256_verified']=True
    result['mesen_stdout_sha256']=digest(a.mesen_stdout.read_bytes())
    if a.json:a.json.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2,sort_keys=True))
    if not result['request_register_sequence_matches']:
        raise SystemExit(1)

if __name__=='__main__':main()
