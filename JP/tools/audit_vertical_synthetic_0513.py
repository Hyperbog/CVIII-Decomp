#!/usr/bin/env python3
"""Independent Mesen source-instruction differential for selected SYNTHETIC
vertical branch RAM entries. This is not a natural gameplay reachability test.

The emulator state is authentic natural gameplay at bank0B $80E3, but CPU PC
and five selected RAM bytes are intentionally forced per test. This isolates
previously unobserved branches; no false claims of natural live execution.
"""
import argparse
import hashlib
import json
from pathlib import Path
import random
import re
import subprocess
import tempfile

JP_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
MESEN_SHA='95bcda9d4ff6428937183093386d993649c2d740273871ced78217d3d8f234d0'
CORE_SHA='d2831c26d42aba675ed5d2cf392b2e12a67cb25274d981ef2c7741e552b72040'
BASE_SHA='9250a09c03b5ea2d56157ddfa5a857a8fddab305dd17aad74490e0d8eac797aa'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def call(args,timeout=15):
    p=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
    ev=[json.loads(line) for line in p.stdout.splitlines() if line.startswith('{')]
    summary=[x for x in ev if x.get('event')=='summary']
    if p.returncode or len(summary)!=1 or not summary[0].get('ok'):
        raise AssertionError(f'Mesen command failed {p.returncode}: {p.stderr[-400:]} {summary}')
    return summary[0],ev

def grid():
    # Fixed user-independent generated grid; every entry is an explicitly
    # INJECTED Mesen test, not a game-produced RAM assignment.
    from itertools import product
    cases=[]
    # Coverage for all control-transfer classes with deterministic coordinates.
    for axis,delta,y,high,typ in product((0,1), (0,1,0x7f,0x80,0xff),
                                        (0x00,0x2f,0x30,0x50,0xff), (0,1),
                                        (0x3d,0x68,0x80)):
        signed=delta if delta<128 else delta-256
        new_y=(y+signed)&0xff
        new_high=((high*256+y+signed)&511)>>8
        transfer=(new_y>=0x30) if axis else (new_high==0)
        key=('odd' if axis else 'even','transfer' if transfer else
             ('clear' if (typ>=0x80 or typ<0x68) else 'retain'),
             'negative' if delta>=128 else 'positive')
        cases.append((key,(axis,delta,y,high,typ)))
    keys=sorted({k for k,_ in cases})
    chosen=[]
    for key in keys:
        bucket=[v for k,v in cases if k==key]
        for i in (0,len(bucket)//2,len(bucket)-1):
            chosen.append(bucket[i])
    # Uncommon status/preserve flag cases on large negative velocity.
    chosen+= [(1,0xff,0x30,0,0x7f),(0,0x80,0x50,1,0x68),
              (0,0xff,0x00,0,0x80),(1,0x7f,0xff,1,0x3d),
              (0,0x7f,0xfe,1,0x67),(1,0,0x2f,1,0x68)]
    # Additional type-$3B cases exercise the $8843 arithmetic continuation,
    # including both vertical movement directions and source guard bypass.
    chosen += [(0,0x01,0x50,0,0x3b),(0,0xff,0x50,0,0x3b),
               (0,0x7f,0x10,0,0x3b),(0,0x00,0x50,0,0x3b),
               (1,0x01,0x50,0,0x3b),(1,0xff,0x50,0,0x3b),
               (1,0x80,0xf0,1,0x3b),(1,0,0x50,1,0x3b),
               (0,0x80,0x00,1,0x3b),(0,0x01,0xff,1,0x3b),
               (1,0x7f,0xff,1,0x3b),(1,0xff,0x2f,0,0x3b)]
    # Unique cases, stable ordering.
    return list(dict.fromkeys(chosen))

def run(rom,mesen,original,native,max_cases=None,complete=False):
    for path,hashval in ((rom,JP_SHA),(mesen,MESEN_SHA),
                         (mesen.parent/'MesenCore.so',CORE_SHA),(original,BASE_SHA)):
        if sha(path)!=hashval:raise ValueError(f'Unexpected ROM/emulator/original natural state: {path}')
    data=rom.read_bytes()[16:16+262144]
    seg=data[11*16384+0xe3:11*16384+0x15f]
    source_sha=hashlib.sha256(seg).hexdigest()
    with tempfile.TemporaryDirectory(prefix='original0513_vertical_') as d:
        root=Path(d)
        pre=root/'natural.bin';initial_json=root/'natural.json'
        call([str(mesen),str(rom),'--home',str(root/'baselinehome'),'--load-state',str(original),
              '--frames','0','--timeout','8',
              '--dump-memory',f'NesInternalRam={pre}','--state-json',str(initial_json)])
        natural=bytearray(pre.read_bytes())
        cpu0=json.loads(initial_json.read_text())
        if len(natural)!=2048 or cpu0['cpu.x']!=1 or cpu0['cpu.ps']!=0:
            raise AssertionError('Original natural entry base drift')
        counts={};samples=[]
        fixtures=grid() if max_cases is None else grid()[:max_cases]
        for i,(axis,delta,y,high,typ) in enumerate(fixtures):
            overrides=((0x65,0x80|axis),(0x6b,delta),(0x041d,y),
                       (0x0471,0x44|high),(0x054f,typ),(0x0401,0x43))
            before=bytearray(natural)
            for address,value in overrides:before[address]=value
            before_path=root/f'pre{i}.bin';before_path.write_bytes(before)
            after_path=root/f'post{i}.bin';cpu_path=root/f'post{i}.json'
            args=[str(mesen),str(rom),'--home',str(root/f'home{i}'),
                  '--load-state',str(original)]
            for addr,value in overrides:
                args+=['--write-memory',f'NesInternalRam:0x{addr:X}:{value:02X}']
            args+=['--set-pc','0x80E3','--frames','1','--timeout','8']
            if not complete: args+=['--breakpoint','NesMemory:0x8843:x:[$23]==$0B']
            args+=['--breakpoint','NesMemory:0xFDFB:x',
                   '--dump-memory',f'NesInternalRam={after_path}',
                   '--state-json',str(cpu_path)]
            summary,_=call(args,timeout=12)
            emu=json.loads(cpu_path.read_text())
            pc=emu['cpu.pc']
            if summary['reason']!='debugger_break' or pc not in ((0xfdfb,) if complete else (0x8843,0xfdfb)) or emu['cpu.x']!=1:
                raise AssertionError(f'Synthetic vertical branch did not stop at declared boundary: {i}: {summary} {pc:X}')
            actual=subprocess.run([str(native),str(before_path),str(after_path),
                '1','0',str(pc),str(emu['cpu.a']),str(emu['cpu.y']),str(emu['cpu.ps'])]+(['complete'] if complete else []),
                capture_output=True,text=True,timeout=5)
            if actual.returncode or '1792' not in actual.stdout:
                raise AssertionError(f'Original-Mesen source vs native synthetic case {i} {fixtures[i]}: {actual.stdout} {actual.stderr}')
            signed=delta if delta<128 else delta-256
            logical=((high<<8)+y+signed)&511
            moved_y=logical&255
            moved_high=logical>>8
            transferred=(moved_y>=0x30) if axis else (moved_high==0)
            status=('transfer' if transferred else
                    ('cleared' if after_path.read_bytes()[0x54f]==0 else 'retained'))
            k=f'{"odd" if axis else "even"}:{status}:{"negative" if delta>=128 else "positive"}'
            counts[k]=counts.get(k,0)+1
            samples.append({'axis_flag_65':f'{0x80|axis:02X}','delta_6B':f'{delta:02X}',
               'initial_y':f'{y:02X}','initial_high_coordinate_bit':high,
               'type':f'{typ:02X}','terminal_pc':f'{pc:04X}',
               'a_y_p':[emu['cpu.a'],emu['cpu.y'],emu['cpu.ps']],
               'full_nonstack_ram_match':True})
            if (i+1)%12==0:print('PASS Mesen synthetic vertical',i+1,'/',len(fixtures),flush=True)
    return {'schema':'JP-0513-original-mesen-synthetic-vertical-ram-v1',
            'provenance':'Original bank0B mapped source, real Mesen CPU instructions, but RAM and PC INJECTED per test; NOT natural gameplay reachability.',
            'rom_sha256':JP_SHA,'mesen_version':'2.1.1',
            'mesen_sha256':MESEN_SHA,'core_sha256':CORE_SHA,
            'natural_state_sha256':BASE_SHA,'source_bank0b_80e3_815e_sha256':source_sha,
            'continuation_8843_886b_sha256':hashlib.sha256(data[11*16384+0x843:11*16384+0x86c]).hexdigest(),
            'cases':len(samples),'nonstack_ram_compared':1792*len(samples),
            'branch_counts':counts,'outcome_digest_sha256':hashlib.sha256(json.dumps(samples,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            'first_cases':samples[:6],
            'scope':'C++ vertical original $80E3 path '+('through $8843 to fixed $FDFB' if complete else 'to RTS or pre-JMP $8843; no $8843 implementation'),
            'source_8843_886b_included':complete,
            'strict_new_prg_bytes':0,'new_vpp':0}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('rom',type=Path)
    ap.add_argument('--mesen',type=Path,required=True)
    ap.add_argument('--natural-original-state',type=Path,required=True)
    ap.add_argument('--native-replay',type=Path,required=True)
    ap.add_argument('--report',type=Path)
    ap.add_argument('--limit',type=int)
    ap.add_argument('--complete',action='store_true')
    x=ap.parse_args()
    result=run(x.rom.resolve(),x.mesen.resolve(),x.natural_original_state.resolve(),x.native_replay.resolve(),x.limit,x.complete)
    if x.report:x.report.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS original Mesen synthetic injected vertical cases=',result['cases'],'RAM bytes=',result['nonstack_ram_compared'])
if __name__=='__main__':main()
