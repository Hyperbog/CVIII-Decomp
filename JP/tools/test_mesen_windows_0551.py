#!/usr/bin/env python3
"""ROM-free native-Windows transcript-contract regression (not emulator output)."""
from __future__ import annotations
import json
from audit_mesen_windows_0551 import parse_lines, InvalidCapture

START='CV0551 kind=ready schema=jp-mesen-windows-native-0551 passive=1 input_only=1 frames=1100'
COMPLETE='CV0551 kind=complete frames=1100 truncated=0'
EXEC='CV0551 kind=exec frame=8 pc=E526 state=0D sub=02 guard=00 shadow=0A phys=03E526'
BAD_BANK='CV0551 kind=exec frame=8 pc=B873 state=0D sub=02 guard=00 shadow=0A phys=029873'
WRITE='CV0551 kind=write18 frame=6 addr=0018 old=04 value=0D pc=F012 shadow=0A'

def fixture(*, hit=True):
    lines=['Mesen2 test console text before Lua logs', START]
    for n in range(1,1101):
        if n==6:lines.append(WRITE)
        if n==8 and hit:
            lines.extend((EXEC,BAD_BANK))
        state='0D' if n>=6 else '04'
        lines.append(f'CV0551 kind=frame frame={n} state={state} sub=02 guard=00 room=01 slot=04 shadow=0A')
    lines.append(COMPLETE)
    return '\n'.join(lines)+'\n'

def fails(source:str,what:str):
    try:parse_lines(source)
    except InvalidCapture:return
    raise AssertionError('Bad '+what+' accepted')

def run():
    raw=fixture()
    r=parse_lines(raw)
    assert r['frames_completed']==1100
    assert r['state13_frame_observed']
    assert r['verified_e526_state13_hit_count']==1
    assert r['unqualified_code_hit_count']==1
    assert r['strict_prg_coverage_change']==0
    assert r['native_frame_parity']=='NOT TESTED'
    assert parse_lines(fixture(hit=False))['verified_e526_state13_hit_count']==0
    fails(raw.replace(START,START+' corrupted=1'),'modified ready')
    fails(raw.replace(START,START+'\n'+START),'duplicate ready')
    fails(raw.replace(COMPLETE,''),'missing end')
    fails(raw.replace(COMPLETE,'CV0551 kind=complete frames=1100 truncated=1'),'truncated')
    fails(raw.replace('kind=frame frame=41 ','kind=frame frame=40 '),'duplicate frame 40')
    fails(raw.replace('kind=frame frame=40 ','kind=frame frame=49 '),'out of sequence')
    fails(raw.replace('kind=frame frame=1100 ','kind=frame frame=1101 '),'out of bounds')
    fails(raw.replace('kind=frame frame=100 ','kind=frame frame=100 state=ZZ '),'bad byte')
    fails(raw.replace(EXEC,EXEC.replace('pc=E526','pc=DEAD')),'unknown address')
    fails(raw.replace(EXEC,EXEC.replace('phys=03E526','phys=NOTHEX')),'bad mapping')
    fails(raw.replace(WRITE,WRITE.replace('addr=0018','addr=0019')),'wrong watched RAM')
    fails(raw.replace('CV0551 kind=frame frame=91','CV0551 kind=wat frame=91'),'unknown event')
    fails(raw+'CV0551 kind=truncated frame=1100\n','truncation event')
    fails(raw.replace(START,'CV0551 kind=ready schema=jp-mesen-windows-native-0551 passive=1 input_only=1 frames=1100\nCV0551 kind=bad\n'),'unknown callback')
    fails(raw.replace(START,'CV0551 ready nonsense'),'garbled event')
    # Frame and exec provenance must not count native gameplay from fixture alone.
    print('PASS 0551 Mesen Windows transcript parser: 1100 frames, 15 rejection tests')
    print('NOTE all 0551 events above are synthetic and provide zero live gameplay evidence')

if __name__=='__main__':run()
