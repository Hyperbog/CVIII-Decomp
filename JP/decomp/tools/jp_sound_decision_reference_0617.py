#!/usr/bin/env python3
"""JP0617: verify original Mesen $8852 command -> exact terminal outcome.

A Mesen reference must be executed independently on the SHA-pinned original
Japanese ROM before a gameplay-liveness claim. --smoke is synthetic ONLY.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import re

import jp_mesen_sound_requests_0615 as reference_pin
import jp_sound_priority_paths_0616 as original
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'recomp'/'tools'))
import jp_audio_session_verify_0614 as session

ENTRY = re.compile(r'^JP0617_ENTRY ([0-9]+) 8852 ((?:[0-9A-F]{2} ){3}[0-9A-F]{2})$')
EXIT = re.compile(r'^JP0617_EXIT ([0-9]+) (low_return|low_install|meta_install|dmc_return|dmc_program) (884F|885D|8860|8922|8928) ((?:[0-9A-F]{2} ){3}[0-9A-F]{2})$')
META = re.compile(r'^JP0617_META ([0-9]+) 885D$')
BOUNDARY = re.compile(r'^JP0617_BOUNDARY (reset|state_loaded) ([0-9]+)$')
PC = {'low_return':'884F','low_install':'8860','meta_install':'8860',
      'dmc_return':'8922','dmc_program':'8928'}
LIMIT = 40000

def records(stdout: str) -> list[str]:
    messages=[]; loaded=[]; finished=[]
    for line in stdout.splitlines():
        if not line.strip(): continue
        row=json.loads(line)
        if not isinstance(row,dict):raise ValueError('Nonobject Mesen JSONL row')
        if row.get('event')=='loaded':loaded.append(row)
        elif row.get('event')=='summary':finished.append(row)
        elif row.get('event')=='lua_log':
            if row.get('error_count',0):raise ValueError('Mesen Lua callback error')
            value=row.get('text','')
            if not isinstance(value,str):raise ValueError('Malformed Lua log')
            messages.extend(value.splitlines())
    if (len(loaded)!=1 or len(finished)!=1 or
        loaded[0].get('console')!='Nes' or loaded[0].get('mesen_version')!='2.1.1' or
        finished[0].get('ok') is not True or finished[0].get('reason')!='frame_limit'):
        raise ValueError('Independent Mesen run not positively completed')
    return messages


def expected(command: int, low: int, priority: int) -> str:
    if command < 0x50:
        return 'low_return' if low==0x50 and command>=6 else 'low_install'
    if command < 0x6F:return 'meta_install'
    index=command-0x6F
    return 'dmc_return' if priority>=5 and index<priority else 'dmc_program'


def analyze(text: str) -> dict:
    msgs=records(text)
    if not msgs or len(msgs)>LIMIT:
        raise ValueError('Missing or oversized original observation')
    next_id=0
    pending=None
    complete=[]
    boundaries=[]
    decisions=Counter()
    for message in msgs:
        if message.startswith(('JP0617_TRUNCATED','JP0617_INVALID')):
            raise ValueError('Mesen original observer reported incomplete or invalid capture')
        if message.startswith('JP0617_ENTRY'):
            m=ENTRY.fullmatch(message)
            if not m or pending is not None or int(m[1])!=next_id:
                raise ValueError('Unmatched/duplicate sound-driver entry')
            command,low,priority,counter=(int(x,16) for x in m[2].split())
            pending=(next_id,command,low,priority,counter,False)
            next_id+=1
        elif message.startswith('JP0617_META'):
            m=META.fullmatch(message)
            if (not m or pending is None or int(m[1])!=pending[0] or
                pending[5] or not 0x50<=pending[1]<0x6F):
                raise ValueError('Unexpected original metadata-reset entry')
            pending=(*pending[:5],True)
        elif message.startswith('JP0617_EXIT'):
            m=EXIT.fullmatch(message)
            if not m or pending is None or int(m[1])!=pending[0]:
                raise ValueError('Unmatched sound-driver terminal')
            kind,pc=m[2],m[3]
            if PC[kind]!=pc:raise ValueError('Terminal label and PC disagree')
            command,low,priority,counter=pending[1:5]
            observed_cmd,observed_low,after_priority,after_counter=(int(x,16) for x in m[4].split())
            if kind!=expected(command,low,priority):
                raise ValueError('Terminal decision disagrees with original driver branch')
            if (kind=='meta_install')!=pending[5]:
                raise ValueError('Missing/extra original metadata reset phase')
            if command>=0x6F:
                if observed_low!=low:raise ValueError('DMC guard unexpectedly changed low state')
                index=command-0x6F
                expect_priority=priority if kind=='dmc_return' else index
                expect_counter=(counter+int(index>=13))&0xFF
                if observed_cmd!=index or after_priority!=expect_priority or after_counter!=expect_counter:
                    raise ValueError('Original DMC index/priority/counter differs')
            elif kind=='low_install' or kind=='low_return':
                if (observed_cmd!=command or observed_low!=low or
                    after_priority!=priority or after_counter!=counter):
                    raise ValueError('Low guard modified unrelated original state')
            elif observed_cmd!=command:
                raise ValueError('Metadata record pointer command modified across reset')
            decisions[kind]+=1
            complete.append({'id':pending[0],'command':f'{command:02X}','decision':kind})
            pending=None
        elif message.startswith('JP0617_BOUNDARY'):
            m=BOUNDARY.fullmatch(message)
            if not m or int(m[2])!=next_id or pending is not None:
                raise ValueError('Ambiguous original save-load/reset boundary')
            boundaries.append({'event':m[1],'after_request_id':next_id})
        elif message.startswith('JP0617_'):
            raise ValueError('Unknown original sound event marker')
    if pending is not None or not complete:
        raise ValueError('Missing completed original sound decision pairs')
    return {'schema':'CVIII-JP-mesen-sound-decisions/v1',
            'original_sound_driver_entries':len(complete),
            'completed_decisions':len(complete),
            'branch_counts':dict(sorted(decisions.items())),
            'observed_boundaries':boundaries,
            'event_commands':[row['command'] for row in complete],
            'all_events_have_one_terminal':True,
            'original_execution_verified':False,
            'native_request_command_sequence_matches':None,
            'music_SFX_ownership_proven':False,
            'hardware_write_or_PCM_parity_proven':False,
            'new_strict_PRG_bytes':0}


def native_commands(folder: Path) -> list[str]:
    proof=session.verify(folder)
    if len(proof['epochs'])!=1 or proof['epochs'][0]['event']!='power_on':
        raise ValueError('A single native reset epoch is required for comparison')
    rows=session.rows((folder/'CVIII-Sound-Requests.csv').read_bytes(),session.REQUESTS)
    return [r['command'].upper() for r in rows]


def fixture(events: list[str],version: str='2.1.1') -> str:
    return '\n'.join(json.dumps(row) for row in (
        {'event':'loaded','mesen_version':version,'console':'Nes'},
        {'event':'lua_log','error_count':0,'text':'\n'.join(events)},
        {'event':'summary','ok':True,'reason':'frame_limit'}))


def smoke() -> None:
    events=[
        'JP0617_BOUNDARY reset 0',
        'JP0617_ENTRY 0 8852 06 50 04 00',
        'JP0617_EXIT 0 low_return 884F 06 50 04 00',
        'JP0617_ENTRY 1 8852 6B 00 05 FE',
        'JP0617_META 1 885D',
        'JP0617_EXIT 1 meta_install 8860 6B 50 00 FE',
        'JP0617_BOUNDARY state_loaded 2',
        'JP0617_ENTRY 2 8852 7C 00 FF FF',
        'JP0617_EXIT 2 dmc_return 8922 0D 00 FF 00',
        'JP0617_ENTRY 3 8852 6F 00 04 00',
        'JP0617_EXIT 3 dmc_program 8928 00 00 00 00',
        'JP0617_ENTRY 4 8852 05 50 00 00',
        'JP0617_EXIT 4 low_install 8860 05 50 00 00',
    ]
    good=analyze(fixture(events))
    assert good['completed_decisions']==5 and sum(good['branch_counts'].values())==5
    assert good['observed_boundaries'][1]['after_request_id']==2
    corrupt=[
        events[:-1],
        [events[1], *events[1:]],  # nested entry
        [*events[:4], *events[5:]],  # metadata decision without phase
        [*events[:4], 'JP0617_META 99 885D', *events[5:]],
        [*events[:8], 'JP0617_EXIT 2 dmc_return 8922 0D 00 FF FF', *events[9:]],
        [*events[:7], 'JP0617_BOUNDARY state_loaded 99', *events[8:]],
        [*events[:3], 'JP0617_INVALID orphan_terminal', *events[3:]],
        [*events[:3], 'JP0617_TRUNCATED', *events[3:]],
        [*events[:1], 'JP0617_EXIT 0 low_return 884F 06 50 04 00', *events[1:]],
        [*events[:5], 'JP0617_EXIT 1 meta_install 884F 6B 50 00 FE', *events[6:]],
    ]
    for rows in corrupt:
        try:analyze(fixture(rows))
        except ValueError:continue
        raise AssertionError('Malformed original sound decision capture passed')
    try:analyze(fixture(events,version='2.0.0'))
    except ValueError:pass
    else:raise AssertionError('Incorrect independent emulator version passed')
    print('PASS JP0617 original request/decision pairing: 5 paths, 2 boundaries, 11 rejected cases')


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--smoke',action='store_true')
    p.add_argument('--rom',type=Path)
    p.add_argument('--emulator',type=Path)
    p.add_argument('--mesen-stdout',type=Path)
    p.add_argument('--native-dir',type=Path)
    p.add_argument('--json',type=Path)
    args=p.parse_args()
    if args.smoke:smoke();return
    if not (args.rom and args.emulator and args.mesen_stdout):
        p.error('--rom, --emulator, --mesen-stdout are required')
    reference_pin.check_binaries(args.rom,args.emulator)
    bank=original.validated(args.rom.read_bytes())
    if bank[0x8850-0x8000:0x8855-0x8000]!=bytes.fromhex('85 EF C9 6F 90'):
        raise ValueError('JP original sound entry $8852 byte boundary changed')
    results=analyze(args.mesen_stdout.read_text(encoding='utf-8'))
    results['original_execution_verified']=True
    if args.native_dir:
        results['native_request_command_sequence_matches']=(
            native_commands(args.native_dir)==results['event_commands'])
    # Do not write the per-event command sequence to the portable report.
    del results['event_commands']
    results['original_rom_sha256_verified']=True
    results['mesen_agent_and_core_sha256_verified']=True
    if args.json:args.json.write_text(json.dumps(results,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(results,indent=2,sort_keys=True))

if __name__=='__main__':main()
