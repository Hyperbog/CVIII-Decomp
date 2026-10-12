#!/usr/bin/env python3
"""ROM-free adversarial tests for passive-Mesen original-state13 evidence gate."""
from __future__ import annotations
import json
import tempfile
from pathlib import Path
from audit_mesen_state13_0549 import AuditError,scan,field_map


def fixture(*,hits=True, state13=False, tamper=None,frames=2,start=0):
    events=['CV0549 kind=ready schema=jp-state13-provenance-v2 passive=1']
    if hits:
        events.append('CV0549 kind=write18 frame=0 addr=0018 old=00 value=0D pc=E387 shadow=0C phys=03E35C' if state13 else
                      'CV0549 kind=write18 frame=0 addr=0018 old=00 value=02 pc=E387 shadow=0C')
        events.append('CV0549 kind=exec frame=0 pc=E35C state=0D sub=02 guard=01 shadow=0C phys=03E35C' if state13 else
                      'CV0549 kind=exec frame=0 pc=E35C state=02 sub=02 guard=01 shadow=0C phys=03E35C')
        if state13:events.append('CV0549 kind=exec frame=0 pc=E526 state=0D sub=02 guard=01 shadow=0C phys=03E526')
    for i in range(frames):
        s='0D' if state13 else '02'
        events.append(f'CV0549 kind=frame frame={i+1} state={s} sub=02 guard=00 room=00 slot=00 shadow=0C')
    if tamper=='truncated':events.append('CV0549 kind=truncated limit=25000')
    if tamper=='bad_entry':events.append('CV0549 kind=exec frame=0 pc=E777 state=0D sub=02 guard=01 shadow=0C phys=03E526')
    if tamper=='extra_frame':events.append('CV0549 kind=frame frame=3 state=02 sub=02 guard=00 room=00 slot=00 shadow=0C')
    records=[{'event':'rom_loaded','title':'authenticated fixture; fixture not original-ROM evidence'},
             {'event':'lua_log','text':'\n'.join(events),'error_count':0},
             {'event':'summary','ok':True,'reason':'frame_limit','frames_executed':frames,
              'start_frame':start,'final_frame':start+frames}]
    if tamper=='lua_error':records[1]['error_count']=1
    if tamper=='abort':records[2]['ok']=False
    if tamper=='gap':events[-1]='CV0549 kind=frame frame=5 state=02 sub=02 guard=00 room=00 slot=00 shadow=0C';records[1]['text']='\n'.join(events)
    return '\n'.join(json.dumps(r) for r in records)+'\n'

def test():
    assert field_map('CV0549 kind=exec pc=E526 state=0D')['pc']=='E526'
    assert field_map('XYZ kind=frame') is None
    with tempfile.TemporaryDirectory() as t:
        p=Path(t)/'log.jsonl'
        p.write_text(fixture(state13=True));r=scan(p)
        assert r['frames']==2 and r['state13_frame_sampled'] and r['state13_dispatch_observed']
        assert r['e526_execution_in_state13'] and r['e526_hits']==1 and r['strict_prg_credit']==0
        p.write_text(fixture());r=scan(p)
        assert not r['e526_execution_in_state13'] and r['state_values']==[2] and r['state_write_count']==1
        cases=['truncated','bad_entry','extra_frame','lua_error','abort','gap']
        for failure in cases:
            p.write_text(fixture(tamper=failure))
            try:scan(p)
            except AuditError:pass
            else:raise AssertionError(f'accepted corrupted {failure} transcript')
        p.write_text(fixture().replace('"event": "rom_loaded"','"event": "unexpected"'))
        try:scan(p)
        except AuditError:pass
        else:raise AssertionError('accepted missing rom_loaded')
        p.write_text(fixture().replace('value=02','value=BAD_HEX'))
        try:scan(p)
        except AuditError:pass
        else:raise AssertionError('accepted malformed write-byte')
        p.write_text(fixture(state13=True).replace('phys=03E526','phys=00B7F7'))
        r=scan(p)
        assert not r['e526_execution_in_state13'] and r['unqualified_execution_count']==1
        p.write_text(fixture(state13=True).replace('phys=03E526','phys=UNKNOWN'))
        r=scan(p)
        assert not r['e526_execution_in_state13'] and r['unqualified_execution_count']==1
        p.write_text(fixture().replace('kind=ready','kind=notready'))
        try:scan(p)
        except AuditError:pass
        else:raise AssertionError('accepted missing observer installation')
    print('PASS 0549 ROM-free observer parser: 2 positive states and 9 adversarial fixtures')

if __name__=='__main__':test()
