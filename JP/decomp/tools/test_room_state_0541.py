#!/usr/bin/env python3
"""ROM-free CI guard and authenticated JP state-chain versus C++ replay."""
from __future__ import annotations
import argparse, json, subprocess, tempfile
from pathlib import Path
from replay_room_state_0541 import compare, StateCPU, fixture, FIELDS
from replay_room_loader_0540 import JP_SHA
import hashlib

ROOT=Path(__file__).resolve().parents[3]
SRC=ROOT/'JP/recomp/native/room0a/room_loader_native.cpp'

def synthetic_banks():
    a=bytearray(0x4000); e=bytearray(0x4000)
    # fixed E7FB inline dispatch selects state2 / substate0.
    a[0xB4D1+4-0x8000:0xB4D1+6-0x8000]=(0xB597).to_bytes(2,'little')
    a[0xB68E-0x8000:0xB690-0x8000]=(0xB6A4).to_bytes(2,'little')
    a[0xB8C1-0x8000]=0xFF  # B873 07A6=9 sentinel
    for i in range(5):
        ptr=0xA000+i*0x40
        a[0xB8C2+2*i-0x8000:0xB8C4+2*i-0x8000]=ptr.to_bytes(2,'little')
        e[ptr-0x8000:ptr-0x8000+10]=bytes([0x41,0x23,i,0x10+i,0x20+i,
                                            0x30+i,0x40+i,0x50+i,0x60+i,0xFF])
    return a,e

def _run(exe,a,e,flag=True):
    with tempfile.TemporaryDirectory(prefix='0541-smoke-') as tmp:
        pa=Path(tmp)/'a.bin';pe=Path(tmp)/'e.bin'
        pa.write_bytes(a);pe.write_bytes(e)
        command=[str(exe),str(pa),str(pe)]
        if flag:command.append('--state-bridge')
        return subprocess.run(command,capture_output=True,text=True)

def smoke(compiler='g++'):
    with tempfile.TemporaryDirectory(prefix='0541-bld-') as tmp:
        exe=Path(tmp)/'model'
        subprocess.run([compiler,'-std=c++17','-O2','-Wall','-Wextra','-Werror','-pedantic',str(SRC),'-o',str(exe)],check=True)
        a,e=synthetic_banks()
        result=_run(exe,a,e)
        assert result.returncode==0,result.stderr
        lines=[json.loads(l) for l in result.stdout.splitlines()]
        assert len(lines)==1280
        for i in range(5):
            sample=lines[i*256]
            assert sample['state_19']==2 and sample['substate_68']==0
            assert sample['room_stream_state_7a6']==9, 'native loader must preserve 07A6'
            assert sample['state_dispatch_targets']==[0xB597,0xB6A4]
            assert sample['state_gate']=='B8A4_07A6_9_sentinel'
            assert sample['pc_after_loader']==0xB6B4 and sample['sp_after_loader']==0xF9
            assert sample['object_count']==1 and sample['mapped_reads']==12
            assert sample['mapped_accesses'][0]==[0xA000+i*0x40,0x41]
            assert sample['mapped_accesses'][-1]==[0xA000+i*0x40+9,0xFF]
            assert sample['slot_fields'][1:]==[[0]*8]*21
            assert sample['slot_fields'][0][0]==0x30+i
            assert sample['slot_fields'][0][5]==0x20+i
        # Independent corrupted source records must fail closed.
        tests=((0xB4D5,0),(0xB68E,0),(0xB8C1,0))
        for pc,value in tests:
            altered=bytearray(a);altered[pc-0x8000]=value
            bad=_run(exe,altered,e)
            assert bad.returncode!=0,(hex(pc),bad.stdout[:100])
        wrong_bank=_run(exe,a,bytes(e[:-1]))
        assert wrong_bank.returncode!=0
        wrong_cli=_run(exe,a,e,flag=False)
        assert wrong_cli.returncode==0 and len(wrong_cli.stdout.splitlines())==1280
        # Reject unsupported switch at CLI, too.
        with tempfile.TemporaryDirectory() as t:
            pa=Path(t)/'a';pe=Path(t)/'e';pa.write_bytes(a);pe.write_bytes(e)
            wrong=subprocess.run([str(exe),str(pa),str(pe),'--unsupported'],capture_output=True)
            assert wrong.returncode!=0
        print(f'PASS {compiler} ROM-free 1280-case native state-chain smoke, 5 negative fixtures')

def authenticated(rom:Path,out:Path,compiler='g++'):
    raw=rom.read_bytes()
    assert len(raw)==393232 and hashlib.sha256(raw).hexdigest()==JP_SHA
    prg=raw[16:16+262144]
    for idx in range(5):
        cpu=StateCPU(prg,idx,73).run()
        assert cpu.ram[0x7A6]==9 and cpu.pc==0xB6B4
        assert cpu.ram[0x19]==2 and cpu.ram[0x68]==0
        assert cpu.sp==0xF9 and cpu.bank==10
        assert all(0xE785 in cpu.state_visits for _ in [0])
        assert any(cpu.ram[base+22]==0 for base in FIELDS)
    report=compare(rom,out,compiler)
    assert report['matched_steps']==1280
    altered=bytearray(raw);altered[16+10*16384+0xB4D5-0x8000]^=1
    with tempfile.TemporaryDirectory(prefix='0541-negative-rom-') as temp:
        f=Path(temp)/'changed.nes';f.write_bytes(altered)
        try:compare(f,Path(temp)/'reports',compiler)
        except ValueError:pass
        else:raise AssertionError('mutated retail ROM accepted')
    print(f'PASS authenticated {compiler} original E526..B6B4 state-chain 1280-case parity, tamper rejected')

def main():
    p=argparse.ArgumentParser();p.add_argument('--smoke',action='store_true')
    p.add_argument('--rom',type=Path);p.add_argument('--out',type=Path);p.add_argument('--cxx',default='g++')
    args=p.parse_args()
    smoke(args.cxx)
    if args.rom:authenticated(args.rom,args.out or Path('build/room0a_state_0541'),args.cxx)
if __name__=='__main__':main()
