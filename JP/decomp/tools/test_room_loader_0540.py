#!/usr/bin/env python3
"""ROM-free synthetic room-loader tests and optional original JP 6502 parity gate."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

from replay_room_loader_0540 import compare, CPU, original_frame

ROOT=Path(__file__).resolve().parents[3]
SRC=ROOT/'JP/recomp/native/room0a/room_loader_native.cpp'

def fixture():
    a=bytearray(16384);e=bytearray(16384)
    for idx in range(5):
        ptr=0x9000+idx*0x100
        a[0xB8C2-0x8000+2*idx:0xB8C2-0x8000+2*idx+2]=ptr.to_bytes(2,'little')
        n=idx+1
        stream=[0x41+idx,0x21+idx,idx,idx+7]
        for i in range(n):stream.extend([i+1,0x40+i,0x50+i,0x60+i,idx])
        stream.append(0xFF)
        e[ptr-0x8000:ptr-0x8000+len(stream)]=bytes(stream)
    return a,e

def smoke(cxx='g++'):
    with tempfile.TemporaryDirectory(prefix='jp-room-loader-smoke-') as d:
        d=Path(d);a,e=fixture();afile=d/'raw0a.bin';efile=d/'raw0e.bin'
        afile.write_bytes(a);efile.write_bytes(e)
        exe=d/'loader'
        subprocess.run([cxx,'-std=c++17','-O2','-Wall','-Wextra','-Werror','-pedantic',str(SRC),'-o',str(exe)],check=True)
        out=subprocess.run([str(exe),str(afile),str(efile)],capture_output=True,text=True,check=True)
        rows=[json.loads(line) for line in out.stdout.splitlines()]
        assert len(rows)==1280
        for idx in range(5):
            frame=rows[256*idx]
            assert frame['room_index']==idx and frame['seed']==0
            assert frame['object_count']==idx+1
            assert frame['pointer']==0x9000+idx*0x100
            assert frame['mapper']==10 and frame['ram_23']==10
            assert frame['mapped_reads']==7+5*(idx+1)
            assert frame['mapper_writes']==2*frame['mapped_reads']
            assert len(frame['mapped_accesses'])==frame['mapped_reads']
            assert frame['mapped_accesses'][0]==[frame['pointer'],0x41+idx]
            assert frame['mapped_accesses'][-1][1]==0xFF
            assert frame['objects'][0]==[1,0x40,0x50,0x60,idx,1]
            assert rows[256*idx+255]['objects']==frame['objects']
        # Explicit negative tests: malformed physical bank, unbounded selector,
        # missing FF sentinel, and a stream pointer outside its mapper window.
        bad_small=d/'small.bin';bad_small.write_bytes(bytes(a[:-1]))
        bad_big=d/'large.bin';bad_big.write_bytes(bytes(a)+b'\0')
        for source in (bad_small,bad_big):
            assert subprocess.run([str(exe),str(source),str(efile)],capture_output=True).returncode!=0
        tampered=bytearray(e)
        tampered[0x9000-0x8000+4+5]=0 # remove single-record sentinel for idx 0
        modified=d/'bad_stream.bin';modified.write_bytes(tampered)
        assert subprocess.run([str(exe),str(afile),str(modified)],capture_output=True).returncode!=0
        bad_ptr=bytearray(a);bad_ptr[0xB8C2-0x8000:0xB8C4-0x8000]=b'\x00\x40'
        bad_addr=d/'bad_addr.bin';bad_addr.write_bytes(bad_ptr)
        assert subprocess.run([str(exe),str(bad_addr),str(efile)],capture_output=True).returncode!=0
    print('PASS ROM-free native C++ room loader: 5 indexed streams, 1280 input cases, 4 tamper tests')

def authenticated(rom:Path,cxx:str):
    with tempfile.TemporaryDirectory(prefix='jp-room-loader-auth-') as d:
        d=Path(d)
        report=compare(rom,d,cxx)
        assert report['matched_steps']==1280
        frames=[json.loads(s) for s in (d/'native_cpp_room_loader.jsonl').read_text().splitlines()]
        assert sum(frames[idx*256]['object_count'] for idx in range(5))==30
        assert all(x['mapped_reads']>0 for x in frames)
        # Trace tamper proves bad memory and mapper outputs fail comparison.
        from workflow import trace_diff
        baseline=d/'original_6502_room_loader.jsonl'
        for field,value in (('mapper_writes',0),('object_count',0),('mapped_accesses',[])):
            corrupted=[dict(x) for x in frames]
            corrupted[314][field]=value
            mutated=d/'corrupted.jsonl';mutated.write_text(''.join(json.dumps(x)+'\n' for x in corrupted))
            diff=trace_diff(baseline,mutated)
            assert diff['status']=='FAIL' and diff['first_divergence_step']==314
            assert diff['field']==field
        # Authentic original identity rejects otherwise plausible data modifications.
        altered=bytearray(rom.read_bytes());altered[16+14*16384+0xBEA4-0x8000]^=1
        new=d/'wrong_rom.nes';new.write_bytes(altered)
        try:compare(new,d/'invalid',cxx)
        except ValueError:pass
        else:raise AssertionError('modified original ROM accepted')
    print('PASS original-JP 6502/native replay 1280/1280, 30 objects, 4 original-ROM/trace negatives')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--smoke',action='store_true')
    p.add_argument('--rom',type=Path);p.add_argument('--cxx',default='g++')
    a=p.parse_args()
    smoke(a.cxx)
    if a.rom:authenticated(a.rom,a.cxx)
