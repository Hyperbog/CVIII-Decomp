#!/usr/bin/env python3
"""Fail-closed audit of Mesen2 native Windows --testRunner stdout.

Native GUI/test-runner output is NOT mesen-agent JSONL. Require a ROM SHA,
Windows EXE SHA and the dedicated CV0551 Lua marker scheme. Only a real
Windows run is evidence; fixtures never certify state 13 gameplay reachability.
"""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path

ROM_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
WINDOWS_EXE_SHA='8ef403d6b9af32075416193914d7993ce8480b347fe1f20a0cfd9815374933e7'
KIND={'ready','frame','exec','write18','complete','truncated'}
PHYSICAL={0xE35C:0x3E35C,0xE526:0x3E526,0xB873:0x2B873,0xB7F7:0x2B7F7}
LINE=re.compile(r'CV0551 (kind=[a-z0-9]+(?: [A-Za-z0-9_]+=[A-Za-z0-9_-]+)*)\s*$')
class InvalidCapture(ValueError): pass

def sha(path:Path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def parse_lines(raw:str):
    events=[]
    for line in raw.splitlines():
        if 'CV0551' not in line:continue
        m=LINE.search(line)
        if not m:raise InvalidCapture('Malformed CV0551 output')
        d={}
        for word in m[1].split(' '):
            k,eq,v=word.partition('=')
            if not eq or k in d:raise InvalidCapture('Duplicate/missing field')
            d[k]=v
        if d['kind'] not in KIND:raise InvalidCapture('Unknown callback kind')
        events.append(d)
    if not events:raise InvalidCapture('No CV0551 events in stdout')
    if events[0] != {'kind':'ready','schema':'jp-mesen-windows-native-0551','passive':'1','input_only':'1','frames':'1100'}:
        raise InvalidCapture('Missing/modified ready boundary')
    if sum(e['kind']=='ready' for e in events)!=1:raise InvalidCapture('Duplicate script installation')
    if any(e['kind']=='truncated' for e in events):raise InvalidCapture('Incomplete event log')
    if sum(e['kind']=='complete' for e in events)!=1:raise InvalidCapture('Missing/duplicate complete boundary')
    if events[-1]!={'kind':'complete','frames':'1100','truncated':'0'}:
        raise InvalidCapture('Incorrect terminal run condition')
    frames=[e for e in events if e['kind']=='frame']
    if len(frames)!=1100:raise InvalidCapture('Incomplete frame series')
    if [e['frame'] for e in frames]!=[str(i) for i in range(1,1101)]:
        raise InvalidCapture('Nonconsecutive frame indices')
    prior=0
    for e in events[1:-1]:
        if e['kind'] not in {'write18','exec','frame'}:raise InvalidCapture('Unexpected internal event')
        if not re.fullmatch(r'[0-9]+',e.get('frame','')):raise InvalidCapture('Missing frame')
        f=int(e['frame'])
        if f<prior or f>1100:raise InvalidCapture('Out-of-order event')
        prior=f
        for field in ('state','sub','guard','room','slot','old','value','shadow'):
            if field in e and not re.fullmatch(r'[0-9A-F]{2}',e[field]):
                raise InvalidCapture(f'Invalid byte: {field}')
        if e['kind']=='exec':
            if not re.fullmatch(r'[0-9A-F]{4}',e.get('pc','')):raise InvalidCapture('Invalid CPU PC')
            if int(e['pc'],16) not in PHYSICAL:raise InvalidCapture('Unexpected watched code')
            if not (re.fullmatch(r'[0-9A-F]{6}',e.get('phys','')) or e.get('phys')=='UNKNOWN'):
                raise InvalidCapture('Invalid physical mapping')
        if e['kind']=='write18':
            if e.get('addr')!='0018' or not re.fullmatch(r'[0-9A-F]{4}',e.get('pc','')):
                raise InvalidCapture('Invalid state-write event')
    if events[-2]['kind']!='frame' or events[-2]['frame']!='1100':
        raise InvalidCapture('Incomplete final frame')
    vals=sorted({int(e['state'],16) for e in frames})
    hits=[];unknown=[];scheduler=[]
    for e in events:
        if e['kind']!='exec':continue
        pc=int(e['pc'],16)
        qualified=(e['phys']==f'{PHYSICAL[pc]:06X}')
        d={'frame':int(e['frame']),'pc':e['pc'],'state':int(e['state'],16),
           'physical_prg':e['phys'],'mapped_correctly':qualified}
        if not qualified:unknown.append(d)
        if qualified and pc==0xE35C:scheduler.append(d)
        if qualified and pc==0xE526 and int(e['state'],16)==13:hits.append(d)
    writes=[{'frame':int(e['frame']),'old':int(e['old'],16),'new':int(e['value'],16),'pc':e['pc']}
            for e in events if e['kind']=='write18']
    return {'schema':'JP-0551-Mesen2-Windows-original-state13/v1','frames_completed':1100,
            'states_at_frame_end':vals,'state13_frame_observed':13 in vals,
            'qualified_scheduler_entries':len(scheduler),'verified_e526_state13_hits':hits[:30],
            'verified_e526_state13_hit_count':len(hits),
            'unqualified_code_hits':unknown[:30],'unqualified_code_hit_count':len(unknown),
            'write18_count':len(writes),'write18_samples':writes[:100],
            'strict_prg_coverage_change':0,
            'native_frame_parity':'NOT TESTED',
            'note':'Mesen original-console emulation; source-only detector is not execution evidence'}

def audit(log:Path,rom:Path,exe:Path)->dict:
    if sha(rom)!=ROM_SHA:raise InvalidCapture('Wrong Japanese source ROM')
    if sha(exe)!=WINDOWS_EXE_SHA:raise InvalidCapture('Wrong Mesen 2.2.1 EXE')
    report=parse_lines(log.read_text(encoding='utf-8',errors='replace'))
    report['rom_sha256']=ROM_SHA
    report['mesen_windows_exe_sha256']=WINDOWS_EXE_SHA
    report['stdout_sha256']=sha(log)
    report['capture_authentication']='ROM_AND_EMULATOR_HASH_MATCHED'
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--stdout',required=True,type=Path);p.add_argument('--rom',required=True,type=Path)
    p.add_argument('--mesen-exe',required=True,type=Path);p.add_argument('--out',required=True,type=Path)
    a=p.parse_args()
    data=audit(a.stdout,a.rom,a.mesen_exe)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(data,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print('PASS 1100 native Mesen Windows frames, authenticated ROM and emulator; state13 hits:', data['verified_e526_state13_hit_count'])
if __name__=='__main__':main()
