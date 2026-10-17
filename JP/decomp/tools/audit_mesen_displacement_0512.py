#!/usr/bin/env python3
"""Reproduce original Japanese $0B:$80E3 horizontal displacement vs native C++.

The required private state was produced by natural controller-only Mesen play.
No RAM/PC manipulation is performed in this comparison. Its 2-KiB RAM
snapshots and Mesen savestates stay in a temporary directory, never in Git.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

ROM_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
AGENT_SHA='95bcda9d4ff6428937183093386d993649c2d740273871ced78217d3d8f234d0'
CORE_SHA='d2831c26d42aba675ed5d2cf392b2e12a67cb25274d981ef2c7741e552b72040'
STATE_SHA='c54060fc64196d750c79f222c22325d8ae1829a32f6da96c0fe93d808907a872'
SRC_SHA='7cb6c954c56b9288f621afd4c03fdf7ccd3658c2597920fd3311cc7330d7cff3'
FIXED_SHA='49893822450a81ebc7347ffb15342a12320d7bf1802834b44a3a01e75b0a74c8'

def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()

def execute(mesen:Path,rom:Path,root:Path,name:str,opts:list[str]):
    call=[str(mesen),str(rom),'--home',str(root/('home-'+name))]+opts
    p=subprocess.run(call,capture_output=True,text=True,timeout=30)
    events=[json.loads(x) for x in p.stdout.splitlines() if x.startswith('{')]
    summaries=[e for e in events if e.get('event')=='summary']
    if p.returncode or len(summaries)!=1 or not summaries[0].get('ok'):
        raise AssertionError(f'Mesen source step {name} failed: {p.stderr[-400:]} {summaries}')
    return events,summaries[0]

def audit(rom:Path,mesen:Path,native:Path,state:Path):
    raw=rom.read_bytes()
    if len(raw)!=393232 or sha(raw)!=ROM_SHA:raise ValueError('Wrong original Japanese ROM')
    if sha(mesen.read_bytes())!=AGENT_SHA or sha((mesen.parent/'MesenCore.so').read_bytes())!=CORE_SHA:
        raise ValueError('Mesen binary differs from independently verified 2.1.1')
    if sha(state.read_bytes())!=STATE_SHA:
        raise ValueError('Natural frame-2603 two-spawn state differs; do not inject game RAM')
    prg=raw[16:16+262144]
    code=prg[11*16384+0xe3:11*16384+0x10f]
    fixed=prg[31*8192+0x1df2:31*8192+0x1dfe]
    if sha(code)!=SRC_SHA or sha(fixed)!=FIXED_SHA:
        raise ValueError('Physical original $0B:$80E3 or fixed $FDF2 caller bytes changed')
    records=[]
    with tempfile.TemporaryDirectory(prefix='JP0512_independent_Mesen_') as directory:
        root=Path(directory)
        for x in (1,2):
            at=root/f'hit{x}.mss'; before=root/f'pre{x}.bin'; after=root/f'post{x}.bin'
            cpu0=root/f'cpu{x}-in.json';cpu1=root/f'cpu{x}-out.json'
            ev,hit=execute(mesen,rom,root,f'hit{x}',[
              '--load-state',str(state),'--frames','2','--timeout','20',
              '--breakpoint','NesMemory:0x80E3:x:[$23]==$0B',
              '--disassemble','0x80E3:1','--state-json',str(cpu0),'--save-state',str(at)])
            regs=json.loads(cpu0.read_text())
            mapping=[e for e in ev if e.get('event')=='disassembly' and e.get('address')==0x80e3]
            if (hit['reason']!='debugger_break' or hit['final_frame']!=2604 or
                regs['cpu.pc']!=0x80e3 or regs['cpu.x']!=x or
                not any(e.get('absolute_address')==0x2c0e3 and e.get('absolute_type')=='NesPrgRom' for e in mapping)):
                raise AssertionError(f'Original physical $0B:$80E3 actor entry mismatch X={x}')
            # The --frames 0 load reads source entry LDA once before returning,
            # which cannot change RAM. Flags are taken from actual hit cpu0.
            _,pr=execute(mesen,rom,root,f'pre{x}',[
              '--load-state',str(at),'--frames','0','--timeout','12',
              '--dump-memory',f'NesInternalRam={before}'])
            trace=root/f'trace{x}.txt';done=root/f'done{x}.mss'
            _,end=execute(mesen,rom,root,f'step{x}',[
              '--load-state',str(at),'--frames','0','--step','20','--timeout','12',
              '--trace',str(trace),'--state-json',str(cpu1),
              '--dump-memory',f'NesInternalRam={after}','--save-state',str(done)])
            last=json.loads(cpu1.read_text())
            instructions=trace.read_text().splitlines()
            if (len(instructions)!=20 or not instructions[0].startswith('80E3 ') or
                not instructions[-1].startswith('810E ') or
                last['cpu.pc']!=0xfdfb or last['cpu.x']!=x or
                end['final_frame']!=2604):
                raise AssertionError(f'Original 20 instruction horizontal branch drift X={x}')
            a=before.read_bytes();b=after.read_bytes()
            if len(a)!=2048 or len(b)!=2048 or a[0x54e+x]!=0x3d or a[0x65]&0x80:
                raise AssertionError('Original Mesen RAM or actor identity drift')
            run=subprocess.run([str(native),str(before),str(after),str(x),
                str(regs['cpu.ps']),str(last['cpu.a']),str(last['cpu.y']),
                str(last['cpu.ps'])],capture_output=True,text=True,timeout=12)
            if run.returncode or '1792/1792' not in run.stdout:
                raise AssertionError(f'C++ native movement != original Mesen: {run.stdout} {run.stderr}')
            records.append({'actor_slot':x,'original_frame':2604,
                'physical_prg_entry':'02C0E3','fixed_caller':'FDF8',
                'original_source_instructions':20,'original_cpu_return':'FDFB',
                'original_delta_6B':a[0x6b],'original_axis_65':a[0x65],
                'returned_registers_A_X_Y_P':[last['cpu.a'],x,last['cpu.y'],last['cpu.ps']],
                'original_cycles':last['cpu.cycleCount'],'matched_nonstack_ram_bytes':1792,
                'before_nonstack_sha256':sha(a[:256]+a[512:]),
                'after_nonstack_sha256':sha(b[:256]+b[512:])})
            state=done  # original gameplay resumes naturally at $FDFB for X=2
    return {'schema':'JP-0512-live-native-prg0b-80E3-horizontal/v1',
      'rom_sha256':ROM_SHA,'source_block_sha256':SRC_SHA,'fixed_caller_sha256':FIXED_SHA,
      'private_original_state_sha256':STATE_SHA,
      'original_Mesen_version':'2.1.1','cases':records,
      'verified_nonstack_ram_bytes':3584,'native_math_test_cases':73742,
      'claim':'two naturally reached horizontal zero-delta calls; signed/higher-bit cases are native math tests only',
      'vertical_810F_status':'not implemented or live certified',
      'new_strict_prg_bytes':0,'new_vpp_points':0}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('rom',type=Path)
    p.add_argument('--mesen',type=Path,required=True)
    p.add_argument('--private-state',type=Path,required=True)
    p.add_argument('--native-replay',type=Path,required=True)
    p.add_argument('--report',type=Path)
    a=p.parse_args()
    result=audit(a.rom.resolve(),a.mesen.resolve(),a.native_replay.resolve(),a.private_state.resolve())
    if a.report:a.report.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS JP0512 independent original Mesen horizontal displacement:',result['verified_nonstack_ram_bytes'],'native RAM bytes')
if __name__=='__main__':main()
