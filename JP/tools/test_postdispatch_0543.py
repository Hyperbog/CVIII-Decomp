#!/usr/bin/env python3
"""ROM-free native six-dispatch contract fixtures + authenticated original replay.

Three callbacks (0,3,4) are neutral test doubles; scripts 1,2,6 are native.
Do not interpret this test as fully reproduced room initialization.
"""
from __future__ import annotations
import argparse, json, subprocess, tempfile
from pathlib import Path
from replay_postdispatch_0543 import compare,check_rom,TARGET_IDS,LEAVES_PROVEN
from test_room_state_0541 import synthetic_banks
from replay_room_state_0541 import ROOT

SRC=ROOT/'JP/native/room0a/room_loader_native.cpp'
TARGETS=(0x84A0,0x8001,0x8013,0xD03C,0xD0CD,0xCDA8,0x8F3E,0xFBA5,0xFBB0)

def fixtures():
    a,e=synthetic_banks();z=bytearray(16384)
    for i,target in enumerate(TARGETS):
        off=0xB4B1-0x8000+3*i
        a[off:off+3]=target.to_bytes(2,'little')+b'\x00'
    for idx in range(5):
        ptr=0xA000+idx*0x40
        e[ptr-0x8000+3]=idx%4
    z[0x800F-0x8000:0x8013-0x8000]=bytes([0x00,0x04,0x02,0x06])
    # Synthetic first header nibbles $34=4,$35=1,$36=2 select:
    # word[$805F+8]=$9000; word[$9000+4]=$9100,
    # word[$9000+6]=$9200; their third ($36=2) words become
    # authentic $3D/$3E and $3A/$3B video register values.
    def word(at,value):z[at-0x8000:at-0x8000+2]=value.to_bytes(2,'little')
    word(0x805F+8,0x9000)
    word(0x9004,0x9100);word(0x9006,0x9200)
    word(0x9104,0xABCD);word(0x9204,0x1234)
    return a,e,z

def runner(exe:Path,a:bytes,e:bytes,z:bytes,flag='--post-dispatch'):
    with tempfile.TemporaryDirectory(prefix='0543-synthetic-') as t:
        d=Path(t);pa=d/'a';pe=d/'e';pz=d/'z';pa.write_bytes(a);pe.write_bytes(e);pz.write_bytes(z)
        return subprocess.run([str(exe),str(pa),str(pe),flag,str(pz)],capture_output=True,text=True)

def smoke(compiler='g++'):
    with tempfile.TemporaryDirectory(prefix='0543-native-smoke-') as t:
        exe=Path(t)/'native'
        subprocess.run([compiler,'-std=c++17','-O2','-Wall','-Wextra','-Werror','-pedantic',str(SRC),'-o',str(exe)],check=True)
        a,e,z=fixtures();r=runner(exe,a,e,z)
        assert r.returncode==0,r.stderr
        frames=[json.loads(line) for line in r.stdout.splitlines()]
        assert len(frames)==1280
        expected_maps=[[0xE2D2,v] for v in (0,10)*6]
        for row in frames:
            idx=row['room_index'];seed=row['seed']
            assert row['step']==idx*256+seed
            assert [x['id'] for x in row['callbacks']]==list(TARGET_IDS)
            assert [x['target'] for x in row['callbacks']]==[TARGETS[k] for k in TARGET_IDS]
            assert [x['stubbed'] for x in row['callbacks']]==[k not in LEAVES_PROVEN for k in TARGET_IDS]
            assert [x['stack_pointer'] for x in row['callbacks']]==[0xF5]*6
            assert all(x['ram23']==0 and x['mapped_bank']==0 for x in row['callbacks'])
            assert row['mapper_changes']==expected_maps
            assert (row['mapper'],row['pc_after_state'],row['sp_after_state'])==(10,0x9000,0xFD)
            assert (row['state_19'],row['substate_68'],row['stream_state_7a6'])==(2,1,9)
            assert (row['ram_3f'],row['ram_3c'],row['ram_61'])==(0x37,0x40,8)
            assert row['ram_3a']==0x34 and row['ram_3b']==0x12
            assert row['ram_3d']==0xCD and row['ram_3e']==0xAB
            assert row['video_register_writes']==[
                [0xE333,0xD002,0x34],[0xE338,0xD003,0x12],
                [0xE33E,0xD000,z[0x800F-0x8000+(idx%4)]],
                [0xE343,0xD001,z[0x800F-0x8000+(idx%4)]+1],
                [0xE349,0xE000,0],[0xE34E,0xE003,0],
                [0xE353,0xE001,0xCD],[0xE358,0xE002,0xAB]]
            expected=z[0x800F-0x8000+(idx%4)]
            assert (row['ram_38'],row['ram_39'])==(expected,expected+1)
            assert (row['ram_ff'],row['ram_fc'],row['ram_fd'])==(0xB0,0x10,0)
        negative=[('first pointer',0xB4B1-0x8000,0),
                  ('unused pointer',0xB4B1-0x8000+3*8,0),
                  ('script bank',0xB4B1-0x8000+3*1+2,1),
                  ('late return',0xB4B1-0x8000+3*4,0)]
        for name,addr,value in negative:
            bad=bytearray(a);bad[addr]=value
            q=runner(exe,bad,e,z)
            assert q.returncode!=0,(name,q.stdout[:100])
        wrong_pointer=bytearray(z);wrong_pointer[0x805F-0x8000+9]=0
        assert runner(exe,a,e,wrong_pointer).returncode!=0
        bad_e=bytearray(e);bad_e[0xA000-0x8000+3]=5
        assert runner(exe,a,bad_e,z).returncode!=0
        assert runner(exe,a,e,z[:-1]).returncode!=0
        assert runner(exe,a,e,z,'--unsupported').returncode!=0
        print('PASS',compiler,'1280 synthetic postloader with ID2 video-register implementation, 8 negative fixtures')

def main():
    p=argparse.ArgumentParser();p.add_argument('--smoke',action='store_true')
    p.add_argument('--rom',type=Path);p.add_argument('--out',type=Path)
    p.add_argument('--cxx',default='g++');a=p.parse_args()
    smoke(a.cxx)
    if a.rom:
        compare(a.rom,a.out or Path('build/postdispatch_0543'),a.cxx)
        raw=bytearray(a.rom.read_bytes());raw[16+10*16384+0xB4B1-0x8000]^=1
        with tempfile.TemporaryDirectory(prefix='0543-identity-') as t:
            bad=Path(t)/'altered.nes';bad.write_bytes(raw)
            try:check_rom(bad)
            except ValueError:pass
            else:raise AssertionError('original ROM identity tampering accepted')
        print('PASS original Japanese ROM identity mutation rejected')
if __name__=='__main__':main()
