#!/usr/bin/env python3
"""Original Mesen2 physical-ROM differential for JP actor preflight 0514.

Two calls are genuinely reached from natural gameplay. All rows with explicit
RAM mutations are synthetic, source-instruction verification only. ROM,
savestates, RAM dumps and raw step traces remain PRIVATE and uncommitted.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROM_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
AGENT_SHA='95bcda9d4ff6428937183093386d993649c2d740273871ced78217d3d8f234d0'
CORE_SHA='d2831c26d42aba675ed5d2cf392b2e12a67cb25274d981ef2c7741e552b72040'
def sha(b):return hashlib.sha256(b).hexdigest()
def filehash(p):return sha(p.read_bytes())

def mesen(exe,rom,tmp,tag,state,steps,changes):
    here=tmp/tag;here.mkdir()
    cmd=[str(exe),str(rom),'--home',str(here/'home'),'--load-state',str(state),
         '--frames','0','--step',str(steps),'--timeout','12']
    for a,v in changes.items():cmd.extend(['--write-memory',f'NesInternalRam:0x{a:X}:{v:02X}'])
    cmd.extend(['--state-json',str(here/'cpu.json'), '--dump-memory',f'NesInternalRam={here}/ram.bin',
                '--trace',str(here/'trace.txt')])
    p=subprocess.run(cmd,capture_output=True,text=True,timeout=19)
    summaries=[json.loads(line) for line in p.stdout.splitlines() if '"event":"summary"' in line]
    if p.returncode or len(summaries)!=1 or not summaries[0]['ok']:
        raise AssertionError(f'Original Mesen step {tag}: exit {p.returncode} {p.stderr[-200:]} {summaries}')
    cpu=json.loads((here/'cpu.json').read_text())
    ram=(here/'ram.bin').read_bytes()
    if len(ram)!=0x800 or len((here/'trace.txt').read_text().splitlines()) not in ((0,1) if steps==0 else (steps,)):
        raise AssertionError(f'Mesen trace/RAM shape {tag}')
    return here,cpu,ram

def native(native_binary,kind,input_bytes,after,entry,final,where):
    pre=where/'native_input.bin';pre.write_bytes(input_bytes)
    cmd=[str(native_binary),kind,str(pre),str(after),
         str(entry['x']),str(entry['a']),str(entry['y']),str(entry['p']),
         str(final['pc'] if kind=='gate' else 0),str(final['a']),str(final['x']),
         str(final['y']),str(final['p'])]
    p=subprocess.run(cmd,capture_output=True,text=True,timeout=6)
    if p.returncode or '1792/1792' not in p.stdout:
        raise AssertionError(f'Native != original Mesen {kind}: {p.stdout} {p.stderr}')

def do_audit(rom,mesen_binary,native_binary,producer_state,post_state):
    if filehash(rom)!=ROM_SHA or rom.stat().st_size!=393232:raise ValueError('Original-JP ROM changed')
    if filehash(mesen_binary)!=AGENT_SHA or filehash(mesen_binary.parent/'MesenCore.so')!=CORE_SHA:
        raise ValueError('Independent Mesen2 binary changed')
    source=rom.read_bytes()[16:16+262144]
    ranges={'producer30_D2FE_D30C':source[30*8192+0x12fe:30*8192+0x130d],
            'gate0B_B1F8_B216':source[11*16384+0x31f8:11*16384+0x3217],
            'roomflag30_D062_D068':source[30*8192+0x1062:30*8192+0x1069]}
    source_hashes={k:sha(v) for k,v in ranges.items()}
    # Both savestates are from unmodified, controller-only original Mesen:
    # D2FE on Stage 1 frame 2605, B1F8 actor X=1 at frame 2604.
    with tempfile.TemporaryDirectory(prefix='jp0514_preflight_') as t:
        tmp=Path(t);all_rows=[]
        from_state={}
        for kind,state in [('delta',producer_state),('gate',post_state)]:
            here,cpu,ram=mesen(mesen_binary,rom,tmp,f'{kind}_initial',state,0,{})
            # --step=0 is a CLI inspection with possible one instruction PC
            # advance; original RAM unaffected in these LDA/LDY entries.
            at={'x':cpu['cpu.x'],'a':cpu['cpu.a'],'y':cpu['cpu.y'],'p':cpu['cpu.ps']}
            if kind=='delta':
                # Natural stop event recorded separately before any --step run.
                at.update(x=16,a=0,y=0,p=3)
                assert ram[0x62]==2 and ram[0x53]==0 and ram[0x08]==0
            else:
                at.update(x=1,a=68,y=0,p=1)
                assert ram[0x0471]==0x44 and ram[0x0401]==0x92 and ram[0x054f]==0x3d
            from_state[kind]=(ram,at)
        deltas=[(0,0,2),(0,1,2),(1,0,2),(0,255,2),(255,0,2),
                (127,255,2),(128,1,2),(127,128,2),(128,127,2),
                (255,255,2),(16,240,2),(240,16,2),(0,0,3),
                (255,1,3),(1,255,3),(127,128,255),(128,127,255),
                (200,199,255),(199,200,255),(0,0,255)]
        gates=[(0x44,0x92,0x3d,12),(0x45,0x92,0x3d,3),
               (0x54,0x92,0x3d,3),(0x44,0,0x3d,5),
               (0x44,0x92,0,12),(0x44,0x92,0x57,12),
               (0x44,0x92,0x58,14),(0x44,0x92,0x60,14),
               (0x44,0x92,0x61,14),(0x44,0x92,0x7f,14),
               (0x44,0x92,0x80,10),(0x44,0x92,0x82,10),
               (0x44,0x92,0x83,8),(0x44,0x92,0xff,8),
               (0x40,0x92,0x3d,12),(0x50,0x92,0xff,3),
               (0x44,0xff,0x80,10),(0x44,1,0x38,12)]
        for i,(aa,bb,mode) in enumerate(deltas):
            changes={0x53:aa,0x08:bb,0x62:mode}
            here,cpu,after=mesen(mesen_binary,rom,tmp,f'delta{i}',producer_state,9,changes)
            first,entry=from_state['delta'];arr=bytearray(first)
            for k,v in changes.items():arr[k]=v
            final={k:cpu['cpu.'+k] for k in ['pc','a','x','y','ps']}
            final['p']=final.pop('ps')
            if cpu['cpu.pc']!=0xd15b or cpu['cpu.x']!=16:raise AssertionError('Producer return drift')
            native(native_binary,'delta',arr,here/'ram.bin',entry,final,here)
            all_rows.append({'branch':'delta','source':'synthetic_RAM' if changes!={0x53:0,0x08:0,0x62:2} else 'natural_Ram_same_as_original',
                    'params':[aa,bb,mode], 'end_pc':f'{cpu["cpu.pc"]:04X}',
                    'A_X_Y_P':[cpu['cpu.a'],cpu['cpu.x'],cpu['cpu.y'],cpu['cpu.ps']],
                    'original_nonstack_sha256':sha(after[:256]+after[512:])})
        for i,(mask,alive,typ,steps) in enumerate(gates):
            changes={0x0471:mask,0x0401:alive,0x054f:typ}
            here,cpu,after=mesen(mesen_binary,rom,tmp,f'gate{i}',post_state,steps,changes)
            first,entry=from_state['gate'];arr=bytearray(first)
            for k,v in changes.items():arr[k]=v
            final={k:cpu['cpu.'+k] for k in ['pc','a','x','y','ps']}
            final['p']=final.pop('ps')
            if cpu['cpu.pc'] not in (0xb1f7,0xb217,0xb258):
                raise AssertionError(f'Gate final PC not original branch boundary {cpu["cpu.pc"]:04X}')
            native(native_binary,'gate',arr,here/'ram.bin',entry,final,here)
            all_rows.append({'branch':'gate','source':'synthetic_RAM' if i else 'natural_same_as_original',
                    'params':[mask,alive,typ], 'end_pc':f'{cpu["cpu.pc"]:04X}',
                    'A_X_Y_P':[cpu['cpu.a'],cpu['cpu.x'],cpu['cpu.y'],cpu['cpu.ps']],
                    'original_nonstack_sha256':sha(after[:256]+after[512:])})
    return {'schema':'JP-0514-original-native-actor-preflight-differential/v1',
            'rom_sha256':ROM_SHA,'mesen_agent_sha256':AGENT_SHA,'mesen_core_sha256':CORE_SHA,
            'private_natural_state_sha256':{'delta':filehash(producer_state),'gate':filehash(post_state)},
            'physical_original_source_hashes':source_hashes,
            'cases':len(all_rows),'native_exact_nonstack_ram_bytes':1792*len(all_rows),
            'delta_cases':len(deltas),'postprocess_gate_cases':len(gates),
            'outcome_digest_sha256':sha(json.dumps(all_rows,sort_keys=True,separators=(',',':')).encode()),
            'examples':all_rows[:3]+all_rows[-3:],
            'evidence':'original unmodified ROM instructions with natural input-state anchors; synthetic test RAM edits explicitly flagged; not new original gameplay liveness',
            'certified_PRG_addition':0,'VPP_addition':0}

def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('original_jp_rom',type=Path)
    a.add_argument('--mesen',type=Path,required=True)
    a.add_argument('--native-replay',type=Path,required=True)
    a.add_argument('--producer-state',type=Path,required=True)
    a.add_argument('--postprocess-state',type=Path,required=True)
    a.add_argument('--report',type=Path)
    args=a.parse_args()
    out=do_audit(args.original_jp_rom.resolve(),args.mesen.resolve(),args.native_replay.resolve(),args.producer_state.resolve(),args.postprocess_state.resolve())
    if args.report:args.report.write_text(json.dumps(out,indent=2)+'\n')
    print('PASS original Japanese Mesen native preflight',out['cases'],'cases',out['native_exact_nonstack_ram_bytes'],'RAM comparisons')
if __name__=='__main__':main()
