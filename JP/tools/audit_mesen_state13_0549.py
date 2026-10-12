#!/usr/bin/env python3
"""Fail-closed audit of independently emulated Mesen2 original-JP state provenance.

Never promotes an emulator-observed event to global strict byte certification.
Rejects incomplete, unbounded, unexpected or fabricated-state transcripts.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

ROM_SHA = '958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
MESEN_SHA = '95bcda9d4ff6428937183093386d993649c2d740273871ced78217d3d8f234d0'
CORE_SHA = 'fa0e7af858dce0171f5857837f8cad92090078c354631ce74f8279185df97bd1'
PAT = re.compile(r'^CV0549 (kind=\w+(?: [a-zA-Z0-9_]+=[A-Za-z0-9_-]+)*)$')
VALID = {'ready','frame','write18','exec','truncated'}
# CPU $Bxxx is bank-switched; mapped physical PRG offsets, not CPU PCs, certify identity.
PHYSICAL = {0xE35C:0x3E35C, 0xE526:0x3E526, 0xB873:0x2B873, 0xB7F7:0x2B7F7}
FIXED = {0xE35C,0xE526}
BANKED = {0xB873,0xB7F7}
class AuditError(ValueError):pass

def digest(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def authenticate(rom:Path,emulator:Path|None=None):
    if digest(rom)!=ROM_SHA:raise AuditError('Original Japanese ROM hash mismatch')
    if emulator:
        if digest(emulator/'mesen-agent')!=MESEN_SHA:raise AuditError('Mesen agent binary hash mismatch')
        if digest(emulator/'MesenCore.so')!=CORE_SHA:raise AuditError('Mesen core library hash mismatch')

def field_map(line:str):
    match=PAT.fullmatch(line)
    if not match:return None
    out={}
    for token in match[1].split(' '):
        key,sep,val=token.partition('=')
        if not sep or key in out:raise AuditError('Duplicate/malformed event field')
        out[key]=val
    if out.get('kind') not in VALID:raise AuditError('Unknown event type')
    return out

def scan(path:Path):
    try:lines=[json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
    except (ValueError,UnicodeError) as exc:raise AuditError(f'Invalid JSONL: {exc}') from exc
    loaded=[x for x in lines if x.get('event')=='rom_loaded']
    summaries=[x for x in lines if x.get('event')=='summary']
    if len(loaded)!=1 or len(summaries)!=1:raise AuditError('Missing/duplicated Mesen run boundary')
    summ=summaries[0]
    if summ.get('ok') is not True or summ.get('reason')!='frame_limit':raise AuditError('Mesen did not complete requested bounded frames')
    frames_expected=summ.get('frames_executed')
    if not isinstance(frames_expected,int) or not 1<=frames_expected<=20000:raise AuditError('Unbounded or empty frame count')
    if (not isinstance(summ.get('start_frame'),int) or not isinstance(summ.get('final_frame'),int)
            or summ['final_frame']-summ['start_frame'] != frames_expected):
        raise AuditError('Inconsistent emulator frame timestamps')
    logs=[]
    for rec in lines:
        if rec.get('event')=='lua_log':
            if rec.get('error_count',0):raise AuditError('Lua callback error')
            logs.extend(rec.get('text','').splitlines())
    events=[e for line in logs if (e:=field_map(line)) is not None]
    ready=[e for e in events if e['kind']=='ready']
    if len(ready)!=1 or ready[0].get('schema')!='jp-state13-provenance-v2' or ready[0].get('passive')!='1':
        raise AuditError('Passive observer did not install exactly once with v2 schema')
    if any(e['kind']=='truncated' for e in events):raise AuditError('Observer event cap exceeded: incomplete provenance')
    samples=[e for e in events if e['kind']=='frame']
    if len(samples)!=frames_expected:raise AuditError('Missing frame samples; cannot claim complete run')
    prev=0
    for e in samples:
        try:f=int(e['frame'])
        except (KeyError,ValueError) as exc:raise AuditError('Bad frame index') from exc
        if f!=prev+1:raise AuditError('Frame samples are not consecutive')
        prev=f
        if not re.fullmatch(r'[0-9A-F]{2}',e.get('state','')):raise AuditError('Bad state byte')
    events_by_kind={kind:[x for x in events if x['kind']==kind] for kind in VALID}
    dispatch=[];room=[];writes=[];banked_hits=[];unqualified=[]
    for e in events_by_kind['exec']:
        try:pc=int(e['pc'],16);state=int(e['state'],16);guard=int(e['guard'],16)
        except (KeyError,ValueError) as exc:raise AuditError('Invalid exec fields') from exc
        if pc not in FIXED|BANKED:raise AuditError('Unexpected instrumented entry')
        raw=e.get('phys','UNKNOWN')
        if raw!='UNKNOWN' and not re.fullmatch(r'[0-9A-F]{6}',raw):
            raise AuditError('Invalid physical ROM offset')
        qualified=raw==f'{PHYSICAL[pc]:06X}'
        entry={'frame':int(e['frame']),'pc':f'{pc:04X}','state':state,'guard':guard,'sub':int(e['sub'],16),
               'bank_register_shadow':e['shadow'], 'physical_prg_offset':raw, 'physical_identity_verified':qualified}
        if not qualified:unqualified.append(entry)
        if pc==0xE35C and qualified:dispatch.append(entry)
        if pc==0xE526 and qualified:room.append(entry)
        if pc in BANKED and qualified:banked_hits.append(entry)
    for e in events_by_kind['write18']:
        try:w={'frame':int(e['frame']),'old':int(e['old'],16),'new':int(e['value'],16),'pc_observed':e['pc']}
        except (KeyError,ValueError) as exc:raise AuditError('Invalid write18 fields') from exc
        if e.get('addr')!='0018':raise AuditError('Write18 address mismatch')
        writes.append(w)
    observed13=any(int(x['state'],16)==13 for x in samples)
    # A live state-13 hit requires original execution at E526, not just a RAM sample.
    e526_13=[x for x in room if x['state']==13]
    return {'frames':frames_expected,'start_frame':summ['start_frame'],'final_frame':summ['final_frame'],
            'state_values':sorted({int(x['state'],16) for x in samples}),
            'state13_frame_sampled':observed13,'state13_dispatch_observed':any(x['state']==13 for x in dispatch),
            'e526_execution_in_state13':bool(e526_13),'e526_hits':len(room),
            'scheduler_hits':len(dispatch),'bank0a_live_entry_hits':banked_hits[:60],
            'bank0a_live_entry_count':len(banked_hits),'unqualified_execution_hits':unqualified[:60],
            'unqualified_execution_count':len(unqualified),
            'state_writes':writes[:300], 'state_write_count':len(writes),
            'scheduler_state13_samples':[x for x in dispatch if x['state']==13][:30],
            'e526_state13_samples':e526_13[:30], 'instrumentation':'Mesen2 passive original-ROM Lua callbacks',
            'runtime_evidence':'real_Mesen_frame_event_if_provenance_and_binary_hashes_are_authenticated',
            'strict_prg_credit':0,'native_full_frame_parity':'NOT ESTABLISHED'}

def audit(rom:Path,emulator:Path,legs:list[tuple[str,Path]],prior:Path|None=None):
    authenticate(rom,emulator)
    if not legs:raise AuditError('No emulator runs')
    reports=[];last=None
    for name,path in legs:
        r=scan(path)
        if last is not None and r['start_frame']!=last:raise AuditError('Segments do not connect')
        last=r['final_frame'];reports.append({'name':name,**r,'file_sha256':digest(path)})
    total=sum(x['frames'] for x in reports)
    result={'schema':'JP-0549-mesen-natural-state13-execution/v1','original_rom_sha256':ROM_SHA,
        'emulator_sha256':MESEN_SHA,'core_sha256':CORE_SHA,'total_frames':total,'segments':reports,
        'state13_execution_observed':any(x['e526_execution_in_state13'] for x in reports),
        'state13_scheduler_observed':any(x['state13_dispatch_observed'] for x in reports),
        'limitations':['No cycle-exact native comparison or full-game recomp claim','Control flow only for the supplied real-input route',
          'State-13 not observed is evidence only for this bounded route','CPU PC in write callback is informational; no automatic writer certification',
          'No entry is counted as original ROM execution unless emu.convertAddress maps it to expected physical PRG' ],
        'strict_prg_credit':0}
    if prior:
        old=json.loads(prior.read_text(encoding='utf-8'))
        expected=old.get('total_independently_emulated_frames')
        if expected!=1100:raise AuditError('Unexpected historical original-Mesen reference length')
        result['historical_0508_reference_frames']=expected
        result['historical_0508_state13_not_seen_in_sampled_logs']=True
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--rom',type=Path,required=True);ap.add_argument('--emulator',type=Path,required=True)
    ap.add_argument('--segment',nargs=2,action='append',metavar=('NAME','JSONL'),required=True)
    ap.add_argument('--historical-report',type=Path);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();report=audit(a.rom,a.emulator,[(n,Path(p)) for n,p in a.segment],a.historical_report)
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(report,indent=2)+'\n')
    print(f"PASS {report['total_frames']} original Mesen frames; state13 E526 observed={report['state13_execution_observed']}; strict credit 0")
if __name__=='__main__':main()
