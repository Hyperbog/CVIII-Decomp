#!/usr/bin/env python3
"""ROM-locked independent-Mesen vs native $0B:$8001 actor movement.

Requires private, controller-only original-Mesen source state after two live
row-$32 actor spawns. Never embeds ROM, savestate, or a RAM dump in Git.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

ROM_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
AGENT_SHA='95bcda9d4ff6428937183093386d993649c2d740273871ced78217d3d8f234d0'
CORE_SHA='d2831c26d42aba675ed5d2cf392b2e12a67cb25274d981ef2c7741e552b72040'
SOURCE_SHA='4f8acdadcc27a00278b799ca271122d46c05473d92f19e1f01ee505113fccef9'
PRIV_SHA='c54060fc64196d750c79f222c22325d8ae1829a32f6da96c0fe93d808907a872'
PHYS='''for _,pc in ipairs({0x8037,0x803e,0x8047,0x8020,0x8033}) do
 emu.addMemoryCallback(function()
  local p=emu.convertAddress(pc,emu.memType.nesMemory)
  emu.log(string.format('PHYS %04X %06X',pc,p.address))
 end,emu.callbackType.exec,pc)
end
'''

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def mesen(exe,rom,root,label,args):
    cmd=[str(exe),str(rom),'--home',str(root/('home-'+label))]+args
    p=subprocess.run(cmd,text=True,capture_output=True,timeout=30)
    logs=[json.loads(x) for x in p.stdout.splitlines() if x.startswith('{')]
    sums=[x for x in logs if x.get('event')=='summary']
    if p.returncode or len(sums)!=1 or not sums[0].get('ok'):
        raise AssertionError(f'Mesen failed {label}: {sums}, {p.stderr[-300:]}')
    return logs,sums[0]

def audit(rom,exe,native,initial):
    if digest(rom)!=ROM_SHA or rom.stat().st_size!=393232:raise ValueError('Incorrect original JP ROM')
    if digest(exe)!=AGENT_SHA or digest(exe.parent/'MesenCore.so')!=CORE_SHA:
        raise ValueError('Mesen binary/core changed')
    if digest(initial)!=PRIV_SHA:
        raise ValueError('Expected exact private natural two-actor Mesen state; not a fixture')
    source=rom.read_bytes()[16+11*16384+1:16+11*16384+0x4b]
    if hashlib.sha256(source).hexdigest()!=SOURCE_SHA:
        raise ValueError('Original raw bank0B $8001-$804A changed')
    with tempfile.TemporaryDirectory(prefix='jp0511_actor_motion_') as temp:
        root=Path(temp);state=initial;rows=[]
        observer=root/'phys.lua';observer.write_text(PHYS)
        for slot in (1,2):
            pre=root/f'before{slot}.bin';snapshot=root/f'before{slot}.json';halt=root/f'before{slot}.mss'
            _,summary=mesen(exe,rom,root,f'entry{slot}',[
                '--load-state',str(state),'--frames','8','--timeout','20',
                '--breakpoint','NesMemory:0x8001:x:[$23]==$0B',
                '--dump-memory',f'NesInternalRam={pre}',
                '--state-json',str(snapshot),'--save-state',str(halt)])
            before=json.loads(snapshot.read_text())
            if (summary['final_frame']!=2604 or summary['reason']!='debugger_break'
                or before['cpu.pc']!=0x8001 or before['cpu.x']!=slot
                or pre.read_bytes()[0x54e+slot]!=0x3d):
                raise AssertionError('Original actor did not reach its native-lift entry')
            post=root/f'after{slot}.bin';snapshot2=root/f'after{slot}.json';resume=root/f'after{slot}.mss'
            logs,s=mesen(exe,rom,root,f'step{slot}',[
                '--load-state',str(halt),'--frames','0','--step','30','--timeout','20',
                '--lua',str(observer),'--dump-memory',f'NesInternalRam={post}',
                '--state-json',str(snapshot2),'--save-state',str(resume)])
            cpu=json.loads(snapshot2.read_text())
            readings='\n'.join(x['text'] for x in logs if x.get('event')=='lua_log')
            mapped=set(re.findall(r'PHYS ([0-9A-F]{4}) ([0-9A-F]{6})',readings))
            required={(f'{pc:04X}',f'{0x2c000+pc-0x8000:06X}') for pc in (0x8037,0x803e,0x8047,0x8020,0x8033)}
            if (s['final_frame']!=2604 or not required<=mapped or cpu['cpu.pc']!=0xfe54
                    or cpu['cpu.x']!=slot):raise AssertionError('Mesen source/physical path drift')
            test=subprocess.run([str(native),str(pre),str(post),f'{before["cpu.ps"]:x}',str(slot)],
                                capture_output=True,text=True,timeout=15)
            result=re.search(r'1792/1792 .* A=(\d+) Y=(\d+) P=(\d+)',test.stdout)
            if test.returncode or not result or tuple(map(int,result.groups()))!=tuple(cpu['cpu.'+f] for f in ('a','y','ps')):
                raise AssertionError(f'Native vs original Mesen difference: {test.stdout} {test.stderr}')
            old=pre.read_bytes();new=post.read_bytes()
            rows.append({'actor_slot':slot,'frame':2604,'cpu_in':'8001','cpu_out':'FE54',
                         'instructions':30,'matched_nonstack_ram_bytes':1792,
                         'before_nonstack_sha256':hashlib.sha256(old[:256]+old[512:]).hexdigest(),
                         'after_nonstack_sha256':hashlib.sha256(new[:256]+new[512:]).hexdigest(),
                         'registers_A_Y_P':[cpu['cpu.a'],cpu['cpu.y'],cpu['cpu.ps']],
                         'original_cycles_end':cpu['cpu.cycleCount']})
            state=resume
    return {'schema':'JP-0511-mesen-native-actor-motion/v1',
            'rom_sha256':ROM_SHA,'source_sha256':SOURCE_SHA,
            'mesen_agent_sha256':AGENT_SHA,'mesen_core_sha256':CORE_SHA,
            'private_original_state_sha256':PRIV_SHA,
            'case_provenance':'natural ROM/controller-run savestate, bank-qualified 0B:8001 execution; no RAM/PC edits',
            'comparisons':rows,'verified_nonstack_ram_bytes':3584,
            'scope':'two live actor movement calls only, not whole frame or audio/PPU parity',
            'new_strict_prg_bytes':0,'new_vpp_points':0}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('rom',type=Path);p.add_argument('--mesen',type=Path,required=True)
    p.add_argument('--private-state',type=Path,required=True)
    p.add_argument('--native-replay',type=Path,required=True)
    p.add_argument('--report',type=Path)
    x=p.parse_args();v=audit(x.rom.resolve(),x.mesen.resolve(),x.native_replay.resolve(),x.private_state.resolve())
    if x.report:x.report.write_text(json.dumps(v,indent=2)+'\n')
    print('PASS original bank0B native two-axis movement:',v['verified_nonstack_ram_bytes'],'Mesen RAM bytes')
if __name__=='__main__':main()
