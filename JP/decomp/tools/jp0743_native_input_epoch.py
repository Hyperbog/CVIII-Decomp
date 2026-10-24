#!/usr/bin/env python3
"""JP0743: map original Mesen absolute input-poll frames to native LOCAL frames.

The original owner capture records (absolute, local) and header origin=1.
NESRecomp --input ticks zero-based native frame numbers. Use the recorded
local-frame column, never unadjusted Mesen PPU absolute frameCount.
No private game data in this source file or ROM-free smoke test.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

SHA1='a0f3b31d4e3b0d2ca2e8a34f91f14ad99a5ad11f'
KEYS=((128,'A'),(64,'B'),(32,'SELECT'),(16,'START'),
      (8,'UP'),(4,'DOWN'),(2,'LEFT'),(1,'RIGHT'))


def buttons(mask):
    return '+'.join(name for bit,name in KEYS if mask&bit) or '-'


def read_source(path:Path):
    if path.suffix.lower()=='.zip':
        with zipfile.ZipFile(path) as archive:
            corrupt=archive.testzip()
            if corrupt is not None:raise ValueError('source ZIP CRC mismatch: '+corrupt)
            hits=[n for n in archive.namelist() if n.endswith('-input.tsv')]
            if len(hits)!=1:raise ValueError('expected one owner Mesen -input.tsv')
            return archive.read(hits[0]).decode('ascii'),hits[0]
    return path.read_text(encoding='ascii'),path.name


def convert(raw:str):
    lines=raw.splitlines()
    if len(lines)<3:raise ValueError('truncated owner input stream')
    h=lines[0].split('\t')
    if (len(h)!=5 or h[:3]!=['JP0718INPUT','1',SHA1]
        or re.fullmatch(r'\d{8}-\d{6}',h[3]) is None
        or not h[4].isdigit()):
        raise ValueError('original Mesen input header/ROM identity invalid')
    origin=int(h[4])
    previous_abs=origin
    previous_local=0
    previous_masks=(0,0)
    count=0
    out=['# JP0743 original Mesen input polls -> native zero-based local frames',
         '# Absolute PPU frame count is not the native input frame index',
         '0 1:-','0 2:-']
    for line in lines[1:-1]:
        r=line.split('\t')
        if len(r)!=7 or r[0]!='P':raise ValueError('corrupt original poll')
        if not all(x.isdigit() for x in r[1:4]+r[6:7]):
            raise ValueError('invalid poll numeric fields')
        if any(re.fullmatch(r'[0-9A-F]{2}',x) is None for x in r[4:6]):
            raise ValueError('invalid hex mask')
        af,lf,seq=map(int,r[1:4])
        a,b=(int(r[4],16),int(r[5],16))
        count+=1
        if (seq!=count or af<=previous_abs or lf<=previous_local
            or lf!=af-origin):
            raise ValueError('input chronology or absolute/local epoch mismatch')
        if a!=previous_masks[0]:out.append(f'{lf} 1:{buttons(a)}')
        if b!=previous_masks[1]:out.append(f'{lf} 2:{buttons(b)}')
        previous_abs,previous_local,previous_masks=af,lf,(a,b)
    if lines[-1].split('\t')!=['END','USER_STOP',str(count)] or count!=17562:
        raise ValueError('owner-input footer/count mismatch')
    encoded='\n'.join(out)+'\n'
    first_start=next((int(line.split()[0]) for line in out
                      if line.endswith('1:START')),None)
    if origin!=1 or first_start!=393:
        raise ValueError('source original START/epoch witness did not verify')
    return encoded,{
        'schema':'JP0743-original-local-frame-controller-input/v1',
        'rom_sha1':SHA1,'owner_input_polls':count,
        'original_absolute_frame_origin':origin,
        'first_start_native_frame':first_start,
        'conversion':'native_frame = original_local_frame = original_absolute_frame - header_origin',
        'owner_input_sha256':hashlib.sha256(raw.encode('ascii')).hexdigest(),
        'native_input_sha256':hashlib.sha256(encoded.encode('ascii')).hexdigest(),
        'runtime_parity_certified':False}


def smoke():
    assert buttons(16)=='START'
    assert buttons(129)=='A+RIGHT'
    assert 394-1==393
    text='JP0718INPUT\t1\t'+SHA1+'\t20261023-213546\t1\n'
    text+='P\t2\t1\t1\t00\t00\t27392\nEND\tUSER_STOP\t1\n'
    try:convert(text)
    except ValueError:pass
    else:raise AssertionError('truncated owner capture was accepted')
    print('PASS JP0743 ROM-free source input frame epoch and mask guards')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--smoke',action='store_true')
    ap.add_argument('--original-input',type=Path)
    ap.add_argument('--output',type=Path)
    ap.add_argument('--report',type=Path)
    a=ap.parse_args()
    if a.smoke:smoke();return
    if not(a.original_input and a.output and a.report):
        ap.error('--original-input --output --report required')
    if a.output.exists() or a.report.exists():
        ap.error('refuse to overwrite existing private replay outputs')
    source,name=read_source(a.original_input)
    result,report=convert(source)
    report['source_member']=name
    a.output.write_text(result,encoding='ascii')
    a.report.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print('PASS JP0743: 17,562 owner input polls -> local native frames; START local frame 393')


if __name__=='__main__':
    main()
