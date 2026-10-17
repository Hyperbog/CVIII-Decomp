#!/usr/bin/env python3
"""JP0668 ROM-free Mesen(original 1-based) / NESRecomp(native 0-based) replay.

The button schedule follows existing mesen_windows_state13_0551.lua.
It is input intent, not independently witnessed CPU sampling.
"""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path
START=((90,92),(180,182),(300,302),(530,531),(745,746))
RIGHT=((370,520),(645,730),(830,1065))
A=((460,469),(1010,1012))
B=((470,475),(650,652),(870,872))
COUNT=1100
BUTTONS=((1,'A'),(2,'B'),(4,'SELECT'),(8,'START'),(16,'UP'),(32,'DOWN'),(64,'LEFT'),(128,'RIGHT'))

def mask_at(frame_one_based:int)->int:
    if not 1<=frame_one_based<=COUNT:raise ValueError('frame outside historical replay')
    result=0
    for windows,bit in ((START,8),(RIGHT,128),(A,1),(B,2)):
        if any(lo<=frame_one_based<=hi for lo,hi in windows):result|=bit
    return result

def generate()->str:
    lines=['# JP0668 original JP0551 inputs: native NESRecomp ZERO-based frames',
           '# Original Mesen inputPolled uses frame+1.',
           '# Port 1 only; port 2 is silent.']
    old=None
    for frame in range(COUNT):
        mask=mask_at(frame+1)
        if mask==old:continue
        buttons='+'.join(name for bit,name in BUTTONS if mask&bit) or '-'
        lines.append(f'{frame} {buttons}')
        old=mask
    return '\n'.join(lines)+'\n'

def validate(source:str)->list[int]:
    edits=[]
    last=-1
    values={name:bit for bit,name in BUTTONS}
    for line in source.splitlines():
        line=line.split('#',1)[0].strip()
        if not line:continue
        parts=line.split()
        if len(parts)!=2:raise ValueError('wrong NESRecomp --window-input schema')
        try:frame=int(parts[0])
        except ValueError as exc:raise ValueError('noninteger replay frame') from exc
        if not last<frame<COUNT:raise ValueError('unordered/invalid frame')
        last=frame
        bits=0
        if parts[1]!='-':
            named=parts[1].split('+')
            if len(set(named))!=len(named):raise ValueError('duplicate button')
            for name in named:
                if name not in values:raise ValueError('invalid NES button')
                bits|=values[name]
        edits.append((frame,bits))
    if not edits or edits[0]!=(0,0):raise ValueError('missing initial zero-buttons epoch')
    actual=[];i=0;held=0
    for frame in range(COUNT):
        if i<len(edits) and edits[i][0]==frame:
            held=edits[i][1];i+=1
        actual.append(held)
    if actual!=[mask_at(f+1) for f in range(COUNT)]:
        raise ValueError('native replay does not match original JP0551 schedule')
    return actual

def sequence_sha256(source:str)->str:
    return hashlib.sha256(bytes(validate(source))).hexdigest()

def smoke():
    source=generate();masks=validate(source)
    assert len(masks)==1100 and masks[89]==8 and masks[92]==0
    assert masks[369]==128 and masks[459]==129 and masks[469]==130
    for modified in (source.replace('89 START','89 WRONG'),
                     source.replace('89 START','89 -'),
                     source.replace('92 -','92 RIGHT'),
                     source+'1100 -\n'):
        try:validate(modified)
        except ValueError:pass
        else:raise AssertionError('corrupt fixture accepted')
    print('PASS JP0668 1100-frame matched-input intent, 4 negative fixtures (NOT gameplay)')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--smoke',action='store_true')
    p.add_argument('--out',type=Path)
    a=p.parse_args()
    if a.smoke:smoke()
    if a.out:
        data=generate()
        a.out.write_text(data,encoding='utf-8')
        print('JP0668 replay SHA256',hashlib.sha256(data.encode()).hexdigest())
        print('JP0668 input-mask SHA256',sequence_sha256(data))
    elif not a.smoke:p.error('--smoke or --out required')

if __name__=='__main__':main()
