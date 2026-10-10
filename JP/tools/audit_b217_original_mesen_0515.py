#!/usr/bin/env python3
"""Original-Japanese-ROM Mesen2 vs native collision admission B217 differential.

Natural actor entry is derived by stepping a SHA-pinned controller-only original
Mesen frame-2604 save. Synthetic cases edit selected emulator RAM to explore
branch precedence; these are not independent game-playback observations.
Never commit ROM, Mesen savestates, code traces, or RAM dumps.
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
NATURAL_B1F8_SHA='0fd7256466e3e952402858ecaa3034eda6774ab2acbf16ad4e2d00c99e1b442c'
NATURAL_B217_RAM_SHA='07b0cbc2d94013a219276945e568bcd5b06c661da61f36cafeae1b7f1d8ec6b0'
B217_ORIGINAL_SOURCE_SHA='07704dd27ecdf3bdc4b0780dd5c0a00acf1bf3dc396fa0e7c93b28a790623587'
B1F8_TO_B232_SHA='1a3b482dca0425a679df117a9330247c727042eb6d4b71fae32092b837956356'

def sha(blob: bytes)->str: return hashlib.sha256(blob).hexdigest()
def readhash(path: Path)->str: return sha(path.read_bytes())

def mesen(agent:Path,rom:Path,folder:Path,tag:str,state:Path,steps:int,mods:dict[int,int]):
    destination=folder/tag
    destination.mkdir()
    mem=destination/'internal-ram.bin'
    cpu=destination/'cpu.json'
    trace=destination/'trace.txt'
    cmd=[str(agent),str(rom),'--home',str(destination/'home'),
         '--load-state',str(state),'--frames','0', '--step',str(steps),'--timeout','12']
    for address,value in mods.items():
        cmd+=['--write-memory',f'NesInternalRam:0x{address:04X}:{value:02X}']
    cmd+=['--dump-memory',f'NesInternalRam={mem}', '--state-json',str(cpu)]
    if steps:cmd+=['--trace',str(trace)]
    done=subprocess.run(cmd,capture_output=True,text=True,timeout=18)
    lines=[json.loads(line) for line in done.stdout.splitlines() if line.startswith('{')]
    summary=[line for line in lines if line.get('event')=='summary']
    if done.returncode or len(summary)!=1 or not summary[0]['ok']:
        raise AssertionError(f'Mesen failure {tag}: {done.returncode}, {done.stderr[-600:]} {summary}')
    registers=json.loads(cpu.read_text())
    ram=mem.read_bytes()
    if len(ram)!=0x800 or (steps and len(trace.read_text().splitlines())!=steps):
        raise AssertionError(f'Mesen RAM/trace mismatch {tag}')
    return ram,registers,mem

def compare(native:Path,folder:Path,tag:str,mode:str,before:bytes,
            after_mem:Path,x:int,initial_y:int,initial_p:int,after_cpu:dict):
    before_file=folder/f'pre-{tag}.bin'
    before_file.write_bytes(before)
    args=[str(native),mode,str(before_file),str(after_mem),str(x),str(initial_y),str(initial_p),
          str(after_cpu['cpu.pc']),str(after_cpu['cpu.a']),str(after_cpu['cpu.x']),
          str(after_cpu['cpu.y']),str(after_cpu['cpu.ps'])]
    done=subprocess.run(args,capture_output=True,text=True,timeout=10)
    if done.returncode or '1792/1792' not in done.stdout:
        raise AssertionError(f'Native mismatch {tag}: {done.stdout} {done.stderr}')

def expected_route(r:bytearray,x:int):
    if r[0x7e]&0xf0:return 0xb258,3,'global-high-mask'
    if r[0x054e+x]>=0x69:return 0xb162,7,'actor-type'
    if r[0x0470+x]&2:return 0xb1d8,9,'actor-bit2'
    if r[0x7d]:return 0xb258,11,'global-7d'
    return 0xb232,11,'enter-collision-b339'

def audit(rom:Path,agent:Path,native:Path,source_state:Path):
    raw=rom.read_bytes()
    if len(raw)!=393232 or sha(raw)!=ROM_SHA:raise ValueError('Unexpected original JP ROM')
    if readhash(agent)!=AGENT_SHA or readhash(agent.parent/'MesenCore.so')!=CORE_SHA:
        raise ValueError('Unqualified original Mesen agent/core')
    if readhash(source_state)!=NATURAL_B1F8_SHA:
        raise ValueError('Natural source input state changed')
    prg=raw[16:16+262144]
    part=lambda a,b:prg[11*16384+a-0x8000:11*16384+b-0x8000]
    if sha(part(0xb217,0xb232))!=B217_ORIGINAL_SOURCE_SHA or sha(part(0xb1f8,0xb232))!=B1F8_TO_B232_SHA:
        raise ValueError('Original physical source code hashes changed')
    with tempfile.TemporaryDirectory(prefix='jp0515_orig_b217_') as td:
        root=Path(td);base=root/'natural_b217.mss'
        cmd=[str(agent),str(rom),'--home',str(root/'anchor-home'),
             '--load-state',str(source_state),'--frames','0','--step','12',
             '--timeout','12','--save-state',str(base),'--state-json',str(root/'anchor.json'),
             '--dump-memory',f'NesInternalRam={root}/anchor.bin',
             '--disassemble','0xB217:1']
        p=subprocess.run(cmd,text=True,capture_output=True,timeout=18)
        ev=[json.loads(x) for x in p.stdout.splitlines() if x.startswith('{')]
        mapped=[x for x in ev if x.get('event')=='disassembly']
        if p.returncode or sha((root/'anchor.bin').read_bytes())!=NATURAL_B217_RAM_SHA or not any(x['address']==0xb217 and x['absolute_type']=='NesPrgRom' and x['absolute_address']==0x2f217 for x in mapped):
            raise AssertionError('Cannot reproduce independently mapped natural $B217 input')
        state=json.loads((root/'anchor.json').read_text())
        anchor=(root/'anchor.bin').read_bytes()
        x=state['cpu.x']
        if (state['cpu.pc'],x,state['cpu.y'],state['cpu.ps'],state['cpu.cycleCount'])!=(0xb217,1,0,0x80,77522038):
            raise AssertionError('Original CPU entry changed')
        rows=[]
        # Genuine 11-instruction path from B217 and composed 23 instructions from B1F8.
        for mode,st,step,name,registers in (
            ('217',base,11,'natural-b217',state),
            ('1f8',source_state,23,'natural-b1f8',{'cpu.x':1,'cpu.y':0,'cpu.ps':1}),
        ):
            after,cpu,after_file=mesen(agent,rom,root,name,st,step,{})
            original_before=anchor if mode=='217' else read_memory_on_state(agent,rom,root,source_state)
            if cpu['cpu.pc']!=0xb232:raise AssertionError('Original normal path no longer entered B339')
            compare(native,root,name,mode,original_before,after_file,1,0,registers['cpu.ps'],cpu)
            rows.append({'kind':'natural','mode':mode,'destination':f'{cpu["cpu.pc"]:04X}',
                         'instructions':step,'matched_ram':1792,
                         'final_A_X_Y_P':[cpu['cpu.a'],cpu['cpu.x'],cpu['cpu.y'],cpu['cpu.ps']]})
        # Every type threshold and all three independent block bits; ensure
        # branch precedence and flags on a SOURCE-CPU-generated oracle.
        for typ in (0x00,0x3d,0x68,0x69,0x7f,0x80,0xff):
            for mask in range(8):
                changed={0x054f:typ,0x7e:0x10 if mask&1 else 0,
                         0x471:0x46 if mask&2 else 0x44,
                         0x7d:0x81 if mask&4 else 0}
                before=bytearray(anchor)
                for address,value in changed.items():before[address]=value
                dest,steps,branch=expected_route(before,1)
                key=f'synthetic-{typ:02X}-{mask}'
                after,cpu,after_file=mesen(agent,rom,root,key,base,steps,changed)
                if cpu['cpu.pc']!=dest:
                    raise AssertionError(f'Original branch destination changed {key}: {cpu["cpu.pc"]:04X} vs {dest:04X}')
                compare(native,root,key,'217',before,after_file,1,0,0x80,cpu)
                rows.append({'kind':'synthetic RAM override, NOT game-live','actor_type':f'{typ:02X}',
                             'mask':mask,'branch':branch,'destination':f'{dest:04X}',
                             'instructions':steps,'matched_ram':1792,
                             'final_A_X_Y_P':[cpu['cpu.a'],cpu['cpu.x'],cpu['cpu.y'],cpu['cpu.ps']]})
        return {
            'schema':'JP-0515-original-B217-collision-admission-differential/v1',
            'rom_sha256':ROM_SHA,'mesen_agent_sha256':AGENT_SHA,'mesen_core_sha256':CORE_SHA,
            'natural_B1F8_state_sha256':NATURAL_B1F8_SHA,
            'derived_natural_B217_ram_sha256':NATURAL_B217_RAM_SHA,
            'note_on_state_hash':'Mesen save-state serialization bytes can vary between equivalent CPU/RAM states; witness qualified by RAM SHA, mapped PC, registers and cycle count',
            'physical_bank0B_B217_B231_sha256':B217_ORIGINAL_SOURCE_SHA,
            'physical_bank0B_B1F8_B231_sha256':B1F8_TO_B232_SHA,
            'physical_prg_entry':'02F217', 'native_exact_nonstack_bytes':1792*len(rows),
            'cases':len(rows),'natural_cases':2,'synthetic_cases':len(rows)-2,
            'branch_histogram':dict(__import__('collections').Counter(r['branch'] for r in rows if 'branch' in r)),
            'result_digest':sha(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()),
            'examples':rows[:3]+rows[-3:],
            'scope':'B217 source collision eligibility only, stopping before JSR B339; no collision solve or frame parity',
            'strict_PRG_bytes_added':0,'VPP_added':0}

def read_memory_on_state(agent:Path,rom:Path,root:Path,source_state:Path)->bytes:
    ram,_,_=mesen(agent,rom,root,'source-B1F8',source_state,0,{})
    return ram

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('rom',type=Path)
    p.add_argument('--mesen',type=Path,required=True)
    p.add_argument('--native-replay',type=Path,required=True)
    p.add_argument('--natural-B1F8-state',type=Path,required=True)
    p.add_argument('--report',type=Path)
    a=p.parse_args()
    r=audit(a.rom.resolve(),a.mesen.resolve(),a.native_replay.resolve(),a.natural_B1F8_state.resolve())
    if a.report:a.report.write_text(json.dumps(r,indent=2)+'\n')
    print('PASS original-Mesen B217 admission: '+str(r['cases'])+' comparisons, '+str(r['native_exact_nonstack_bytes'])+' matched RAM bytes')
if __name__=='__main__':main()
