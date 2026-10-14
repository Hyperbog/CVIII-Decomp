#!/usr/bin/env python3
"""JP0616: audit independently executed Mesen2 sound gate entry/exit pairs.

No event, liveness or priority proof without original ROM + pinned emulator.
ROM-free --smoke exercises strict state-pairing with synthetic JSONL.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import jp_mesen_sound_requests_0615 as witness

PATTERN=re.compile(r'^JP0616_GATE (low_enter|low_return|low_install|dmc_enter|dmc_return|dmc_install) ([A-F0-9]{4}) ([A-F0-9]{2}) ([A-F0-9]{2}) ([A-F0-9]{2})$')
PC={'low_enter':0x8842,'low_return':0x884F,'low_install':0x8860,
    'dmc_enter':0x8908,'dmc_return':0x8922,'dmc_install':0x8928}
MAX_ROWS=20000

def analyze(stdout: str) -> dict:
    frames=[]
    for line in stdout.splitlines():
        if line.strip():
            item=json.loads(line)
            if not isinstance(item,dict):raise ValueError('Bad Mesen JSONL record')
            frames.append(item)
    loaded=[x for x in frames if x.get('event')=='loaded']
    finished=[x for x in frames if x.get('event')=='summary']
    if (len(loaded)!=1 or len(finished)!=1 or
        loaded[0].get('mesen_version')!='2.1.1' or
        loaded[0].get('console')!='Nes' or
        not finished[0].get('ok') or
        finished[0].get('reason')!='frame_limit'):
        raise ValueError('Reference emulator run not positively completed')
    pending=None
    counts=Counter()
    rows=0
    for item in frames:
        if item.get('event')!='lua_log':continue
        if item.get('error_count',0):raise ValueError('Mesen Lua error')
        text=item.get('text','')
        if not isinstance(text,str):raise ValueError('Invalid Lua output')
        for line in text.splitlines():
            if line.startswith('JP0616_TRUNCATED'):
                raise ValueError('Bounded reference capture truncated')
            if not line.startswith('JP0616_GATE'):continue
            m=PATTERN.fullmatch(line)
            if not m or rows>=MAX_ROWS:raise ValueError('Malformed gate record')
            kind,pc,command,prior,state=m.groups()
            pc=int(pc,16);command=int(command,16)
            prior=int(prior,16);state=int(state,16)
            if pc!=PC[kind]:raise ValueError('Unexpected original gate PC')
            rows+=1
            if kind.endswith('_enter'):
                if pending is not None:raise ValueError('Nested sound gate')
                if kind=='low_enter' and command>=0x50:
                    raise ValueError('Low gate has high command')
                if kind=='dmc_enter' and command<0x6F:
                    raise ValueError('DMC gate has low command')
                pending=(kind,command,prior,state)
                continue
            if pending is None:raise ValueError('Exit without gate entry')
            enter,cmd_in,old,old_state=pending
            if enter=='low_enter':
                if (kind not in ('low_return','low_install') or
                    command!=cmd_in or state!=old_state):
                    raise ValueError('Low gate pair mismatch')
                return_expected=old_state==0x50 and command>=0x06
                if (kind=='low_return')!=return_expected:
                    raise ValueError('Original low state branch disagrees')
            else:
                if kind not in ('dmc_return','dmc_install'):
                    raise ValueError('DMC gate pair mismatch')
                idx=cmd_in-0x6F
                suppressed=old>=5 and idx<old
                if command!=idx or (kind=='dmc_return')!=suppressed:
                    raise ValueError('Original DMC priority branch disagrees')
                priority=old if suppressed else idx
                if prior!=priority or state!=(old_state+int(idx>=13))%256:
                    raise ValueError('DMC counter/priority side effect mismatch')
            counts[kind]+=1
            pending=None
    if pending is not None or not counts:
        raise ValueError('Missing or incomplete original gate pairs')
    return {'schema':'CVIII-JP-original-Mesen-sound-gates/v1',
            'completed_gate_pairs':sum(counts.values()),
            'gate_counts':dict(sorted(counts.items())),
            'records_including_entry_and_exit':rows,
            'original_execution_proven_only_if_binary_pins_verified':True,
            'source_ownership_proven':False,
            'audio_register_or_PCM_parity_proven':False,
            'new_strict_prg_bytes':0}

def fixture(events:list[str])->str:
    records=({'event':'loaded','mesen_version':'2.1.1','console':'Nes'},
             {'event':'lua_log','error_count':0,'text':'\n'.join(events)},
             {'event':'summary','ok':True,'reason':'frame_limit'})
    return '\n'.join(json.dumps(rec) for rec in records)

def smoke()->None:
    events=['JP0616_GATE low_enter 8842 06 00 50',
            'JP0616_GATE low_return 884F 06 00 50',
            'JP0616_GATE low_enter 8842 05 00 50',
            'JP0616_GATE low_install 8860 05 00 50',
            'JP0616_GATE dmc_enter 8908 7C FF 01',
            'JP0616_GATE dmc_return 8922 0D FF 02',
            'JP0616_GATE dmc_enter 8908 6F 04 00',
            'JP0616_GATE dmc_install 8928 00 00 00']
    report=analyze(fixture(events))
    assert report['completed_gate_pairs']==4 and report['records_including_entry_and_exit']==8
    corrupt=(events[:1],
             events[:2]+['JP0616_TRUNCATED'],
             [*events[:5],'JP0616_GATE dmc_install 8928 0D FF 02',*events[6:]],
             [*events[:5],'JP0616_GATE dmc_return 8922 0D FF 01',*events[6:]],
             [*events[:3],'JP0616_GATE low_return 884F 05 00 50',*events[4:]],
             [*events[:5],'JP0616_GATE dmc_return 8928 0D FF 02',*events[6:]])
    for seq in corrupt:
        try:analyze(fixture(list(seq)))
        except ValueError:continue
        raise AssertionError('Corrupt Mesen sound decision accepted')
    try:analyze(fixture(events).replace('2.1.1','2.0.0'))
    except ValueError:pass
    else:raise AssertionError('Wrong independent emulator version accepted')
    print('PASS JP0616 Mesen gate-pair parser: 4 synthetic pairs, 7 failures rejected')

def main()->None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--smoke',action='store_true')
    p.add_argument('--rom',type=Path)
    p.add_argument('--emulator',type=Path)
    p.add_argument('--mesen-stdout',type=Path)
    p.add_argument('--json',type=Path)
    a=p.parse_args()
    if a.smoke:smoke();return
    if not (a.rom and a.emulator and a.mesen_stdout):
        p.error('--rom, --emulator and --mesen-stdout required')
    witness.check_binaries(a.rom,a.emulator)
    buf=a.mesen_stdout.read_bytes()
    result=analyze(buf.decode('utf-8'))
    result['original_jp_rom_sha256_verified']=True
    result['reference_executable_sha256_verified']=True
    result['mesen_stdout_sha256']=witness.digest(buf)
    if a.json:
        a.json.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=='__main__':main()
