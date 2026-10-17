#!/usr/bin/env python3
"""ROM-free C++ room descriptor gate fixtures and authenticated original replay.

The first nine descriptors are evaluated as structural indexed candidates;
not all possible live gameplay selections. This test does not claim a native
frame, original game reachability, or any new strict PRG byte credit.
"""
from __future__ import annotations
import argparse, hashlib, json, subprocess, tempfile
from pathlib import Path
from replay_room_gate_0542 import compare, validate_authentic, GateCPU
from replay_room_state_0541 import ROOT

SRC=ROOT/'JP/recomp/native/room0a/room_loader_native.cpp'

def synthetic_banks():
    a=bytearray(16384);e=bytearray(16384)
    a[0xB4D5-0x8000:0xB4D7-0x8000]=(0xB597).to_bytes(2,'little')
    a[0xB68E-0x8000:0xB690-0x8000]=(0xB6A4).to_bytes(2,'little')
    for i in range(9):
        off=0xB8A6-0x8000+3*i
        a[off:off+3]=bytes([0x24+i,0x20+i,0x40])
    a[0xB8C1-0x8000]=0xFF
    return a,e

def run_native(exe:Path,a:bytes,e:bytes,flag='--state-gate'):
    with tempfile.TemporaryDirectory(prefix='0542-gate-fixture-') as d:
        pa=Path(d)/'a';pe=Path(d)/'e';pa.write_bytes(a);pe.write_bytes(e)
        return subprocess.run([str(exe),str(pa),str(pe),flag],capture_output=True,text=True)

def smoke(compiler='g++'):
    with tempfile.TemporaryDirectory(prefix='0542-gate-build-') as d:
        exe=Path(d)/'model'
        subprocess.run([compiler,'-std=c++17','-O2','-Wall','-Wextra','-Werror','-pedantic',str(SRC),'-o',str(exe)],check=True)
        a,e=synthetic_banks()
        proc=run_native(exe,a,e)
        assert proc.returncode==0,proc.stderr
        rows=[json.loads(l) for l in proc.stdout.splitlines()]
        assert len(rows)==2304
        for i in range(9):
            for seed in (0,1,31,127,255):
                row=rows[i*256+seed]
                cursor=seed&31
                buf=row['buffer_0300_037f']
                assert len(buf)==128
                assert buf[cursor:cursor+3]==[1,0x20+i,0x24+i]
                assert buf[cursor+3:cursor+67]==[0]*64
                assert buf[cursor+67]==0xFF
                assert row['ram_1e']==cursor+68 and row['x']==cursor+68
                assert row['stream_state_7a6']==i+1
                assert row['ram_1d']==2 and row['ram_10']==0
                assert row['ram_5e']==0x20+i and row['ram_5f']==0x24+i
                assert row['pc_after_gate']==0x9000 and row['sp_after_gate']==0xFD
                assert row['mapper']==10 and row['mapper_writes']==1 and row['mapped_reads']==0
        assert rows[0]['buffer_0300_037f'][68:]==[(0*13+j*7)&255 for j in range(0x300+68,0x380)]
        bad=[]
        for addr,val in [(0xB4D5,0),(0xB68E,0),(0xB8A6,0xFF),(0xB8A8,0),(0xB8A8,65)]:
            altered=bytearray(a);altered[addr-0x8000]=val
            bad.append((addr,run_native(exe,altered,e)))
        for addr,got in bad:
            assert got.returncode!=0,(hex(addr),got.stdout[:50])
        assert run_native(exe,a,e[:-1]).returncode!=0
        assert run_native(exe,a,e,'--nonsense').returncode!=0
    print('PASS',compiler,'2304 synthetic C++ gate cases, 7 negative fixtures')

def authenticated(rom:Path,out:Path,compiler='g++'):
    prg=validate_authentic(rom)
    for i in range(9):
        cpu=GateCPU(prg,i,73).run()
        assert cpu.pc==0x9000 and cpu.ram[0x7A6]==i+1
        assert 0xEC70 in cpu.state_visits and 0xE785 not in cpu.state_visits
    r=compare(rom,out,compiler)
    assert r['status']=='PASS' and r['matched_steps']==2304
    content=bytearray(rom.read_bytes());content[16+10*16384+0xB8A6-0x8000]^=1
    with tempfile.TemporaryDirectory(prefix='0542-gate-reject-') as tmp:
        changed=Path(tmp)/'changed.nes';changed.write_bytes(content)
        try:validate_authentic(changed)
        except ValueError:pass
        else:raise AssertionError('altered original iNES accepted')
    print('PASS',compiler,'original 6502->C++ state gate 2304/2304 + ROM SHA rejection')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--smoke',action='store_true')
    parser.add_argument('--rom',type=Path);parser.add_argument('--out',type=Path)
    parser.add_argument('--cxx',default='g++')
    args=parser.parse_args()
    smoke(args.cxx)
    if args.rom:authenticated(args.rom,args.out or Path('build/room_gate_0542'),args.cxx)
if __name__=='__main__':main()
