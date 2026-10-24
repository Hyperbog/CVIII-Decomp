#!/usr/bin/env python3
"""JP0740: extract PRIVATE JP0718 anchors, verify Mesen replay, compare native trace.
Only source/tool code belongs in Git. Never publish the extracted RAM/input logs.
CYC --trace-frame is one frame: mismatches are hypotheses absent CPU alignment.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import tempfile
import zipfile

ROM_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
ROM_SHA1='a0f3b31d4e3b0d2ca2e8a34f91f14ad99a5ad11f'
WATCH=(0x62,0x53,0x54,0x55,0x63,0x6b,0x41c,0x438,
       0x4c4,0x4f2,0x509,0x520,0x565,0x5c1)
ANCHORS=(9376,9440,9504,9576)
CORE=(0x62,0x41c,0x520,0x565)
N_INSN=re.compile(r'^(\d+) INSN PC=([0-9A-F]{4}) ')
N_WRITE=re.compile(r'^(\d+) W ([0-9A-F]{4}) ([0-9A-F]{2}) db=')

def source(rom):
    b=rom.read_bytes()
    if (len(b)!=393232 or b[:4]!=b'NES\x1a'
        or ((b[6]>>4)|(b[7]&0xF0))!=24
        or hashlib.sha256(b).hexdigest()!=ROM_SHA
        or hashlib.sha1(b).hexdigest()!=ROM_SHA1):
        raise ValueError('original JP Mapper24 retail ROM identity mismatch')
    return b

def member(z,suffix):
    matched=[n for n in z.namelist() if n.endswith(suffix)]
    if len(matched)!=1:raise ValueError('missing/ambiguous '+suffix)
    return z.read(matched[0])

def history(archive):
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:raise ValueError('corrupt JP0718 ZIP')
        ir=member(z,'-input.tsv')
        rr=member(z,'-ram.tsv')
    lines=ir.decode('ascii').splitlines()
    header=lines[0].split('\t')
    if (len(header)!=5 or header[:3]!=['JP0718INPUT','1',ROM_SHA1]
        or header[4]!='1' or lines[-1]!='END\tUSER_STOP\t17562'
        or len(lines)!=17564):
        raise ValueError('wrong original input schema/count/epoch')
    for k,line in enumerate(lines[1:-1],1):
        r=line.split('\t')
        if (len(r)!=7 or r[0]!='P'
            or tuple(map(int,r[1:4]))!=(k+1,k,k)
            or len(r[4])!=2 or len(r[5])!=2):
            raise ValueError('original input sequence mismatch')
        int(r[4],16);int(r[5],16)
    rs=rr.decode('ascii').splitlines()
    if rs[0].split('\t')[:3]!=['JP0718RAM','1',ROM_SHA1]:
        raise ValueError('original RAM source mismatch')
    snapshots={};prev=-1
    for line in rs[1:]:
        r=line.split('\t')
        if r[0]!='R':continue
        if len(r)!=6:raise ValueError('invalid original RAM row')
        frame,cyc=int(r[2]),int(r[3])
        b=bytes.fromhex(r[5])
        if cyc<=prev or frame in snapshots or len(b)!=2048:
            raise ValueError('original RAM record ordering/size')
        prev=cyc;snapshots[frame]=(cyc,b)
    if any(f not in snapshots for f in ANCHORS):
        raise ValueError('original capture missing four anchor frames')
    return ir,snapshots

def anchor_file(snapshot):
    lines=['JP0740_ANCHORS\t1']
    for frame in ANCHORS:
        cycle,ram=snapshot[frame]
        lines.append(f'{frame}\t{cycle}\t'+''.join(f'{ram[a]:02X}' for a in WATCH))
    return '\n'.join(lines)+'\n'

def prepare(rom,archive,out):
    source(rom)
    data,snap=history(archive)
    if out.exists() and any(out.iterdir()):
        raise ValueError('private output directory must be empty')
    out.mkdir(parents=True,exist_ok=True)
    (out/'jp0740_private_input.tsv').write_bytes(data)
    (out/'jp0740_private_anchors.tsv').write_text(anchor_file(snap),encoding='ascii')
    return {'historical_absolute_input_epoch':1,
            'historical_local_snapshot_epoch':0,
            'input_polls':17562,'anchor_frames':list(ANCHORS),
            'original_rom_sha256':ROM_SHA,'mesen_replay_executed':False,
            'private_directory':str(out)}

def check_original(trace,anchors,rom):
    rows=trace.read_text(encoding='ascii').splitlines()
    if not rows or rows[0]!=f'JP0740\t1\t{ROM_SHA1}\t17562':
        raise ValueError('JP0740 original trace schema/ROM mismatch')
    if not rows[-1].startswith('END\tCOMPLETE\t'):
        raise ValueError('original Mesen trace not completed')
    end=rows[-1].split('\t')
    if len(end)!=5 or int(end[4])!=4:
        raise ValueError('missing source RAM/cycle anchors')
    events=[];checked=set();prevseq=0;prevcycle=-1
    for line in rows[1:-1]:
        if line.startswith('ANCHOR_OK\t'):
            r=line.split('\t')
            if len(r)!=3:raise ValueError('bad anchor confirmation')
            frame,cycle=int(r[1]),int(r[2])
            if (frame not in ANCHORS or frame in checked
                or cycle!=anchors[frame][0]):
                raise ValueError('original replay anchor failure')
            checked.add(frame)
            continue
        if line.startswith('ANCHOR_FAIL\t'):
            raise ValueError('original Mesen replay deviates from JP0718')
        r=line.split('\t')
        if r[0]=='W' and len(r)==10:
            seq,frame,cycle=map(int,r[1:4])
            a,old,new,bus,pc,phys=[int(v,16) for v in r[4:10]]
            if a not in WATCH or (bus&0x7ff)!=a or not 9350<=frame<=9600:
                raise ValueError('source RAM write address/frame invalid')
            # Byte authentication is necessary but not sufficient for instruction
            # PC attribution; e.g. RMW and aliased stores also write RAM.
            opcode=rom[16+phys] if 0<=phys<262144 else None
            events.append({'seq':seq,'frame':frame,'cycle':cycle,'addr':a,
                           'old':old,'new':new,'pc':pc,'phys':phys,
                           'opcode':opcode,'mapped_prg_pc_confirmed':opcode is not None})
        elif r[0]=='R' and len(r)==8:
            seq,frame,cycle=map(int,r[1:4])
            if int(r[4],16) not in (0x4016,0x4017):
                raise ValueError('unexpected controller bus read')
        else:raise ValueError('unrecognized original trace record')
        if seq!=prevseq+1 or cycle<prevcycle:
            raise ValueError('original write/read event chronology invalid')
        prevseq,prevcycle=seq,cycle
    if set(ANCHORS)!=checked or int(end[2])!=prevseq:
        raise ValueError('source trace completeness failure')
    return events

def native_trace(text):
    pc=None;out=[];prev=-1
    for line in text.splitlines():
        mi=N_INSN.match(line)
        mw=N_WRITE.match(line)
        if not (mi or mw):continue
        cycle=int((mi or mw)[1])
        if cycle<prev:raise ValueError('native bus cycles not ordered')
        prev=cycle
        if mi:pc=int(mi[2],16);continue
        addr=int(mw[2],16)
        if addr<0x2000 and (addr&0x7ff) in WATCH:
            out.append({'cycle':cycle,'addr':addr&0x7ff,
                        'new':int(mw[3],16),'pc':pc,
                        'native_physical_prg_bank_confirmed':False})
    return out

def smoke():
    ram=bytearray(2048);snaps={}
    for n,frame in enumerate(ANCHORS):
        ram[0x62]=n
        snaps[frame]=(1000+12*n,bytes(ram))
    assert len(anchor_file(snaps).splitlines())==5
    nts='100 INSN PC=CA08 A=00 X=00 Y=00 S=FD P=22\n101 W 0062 02 db=02 done\n102 R 4016 01 db=01 done\n'
    assert native_trace(nts)[0]['addr']==0x62
    try:native_trace('200 W 0062 01 db=01 done\n100 W 0062 02 db=02 done')
    except ValueError:pass
    else:raise AssertionError('unordered native trace accepted')
    with tempfile.TemporaryDirectory() as d:
        f=Path(d)/'bad-original.tsv';f.write_text('JP0740 fake data')
        try:check_original(f,snaps,bytes(393232))
        except ValueError:pass
        else:raise AssertionError('unverified Mesen original accepted')
    print('PASS JP0740 synthetic original-anchor/native-bus parser; not retail write parity')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--smoke',action='store_true')
    p.add_argument('--rom',type=Path)
    p.add_argument('--mesen-zip',type=Path)
    p.add_argument('--prepare',type=Path,metavar='PRIVATE_DIRECTORY')
    p.add_argument('--original-trace',type=Path)
    p.add_argument('--native-trace',type=Path)
    p.add_argument('--native-frame',type=int)
    a=p.parse_args()
    if a.smoke:smoke();return
    if not a.rom or not a.mesen_zip:p.error('--rom and --mesen-zip required')
    if a.prepare:
        print(json.dumps(prepare(a.rom,a.mesen_zip,a.prepare),indent=2));return
    if not a.original_trace:p.error('--prepare or --original-trace required')
    rom=source(a.rom);_,snap=history(a.mesen_zip)
    rows=check_original(a.original_trace,snap,rom)
    result={'schema':'JP0740-first-writer-evidence/v1',
            'original_rom_verified':True,'original_mesen_events':len(rows),
            'original_source_writes_by_address':dict(Counter(f'{r["addr"]:04X}' for r in rows)),
            'first_original_write_by_address':{f'{adr:04X}':
                next((r for r in rows if r['addr']==adr),None) for adr in CORE},
            'first_incorrect_cpu_write_proved':False,
            'vpp':31,'strict_prg_bytes':49504,'strict_prg_total':262144}
    if a.native_trace:
        if a.native_frame is None:p.error('--native-frame is required with trace')
        result['native_frame_requested']=a.native_frame
        result['original_writes_in_nominal_frame']=[
            r for r in rows if r['frame']==a.native_frame]
        result['native_writes']=native_trace(a.native_trace.read_text(encoding='ascii'))
        result['native_physical_prg_mapping']='not reported by upstream --trace-out'
        result['comparison_grade']='candidate differences only; require CPU/frame/bank alignment'
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
