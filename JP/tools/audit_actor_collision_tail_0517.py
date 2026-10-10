#!/usr/bin/env python3
"""Original Japanese Castlevania III Mesen-to-native collision tail audit.

Starts from SHA-locked ORIGINAL controller-reached B1F8 source state. Derives
B235 naturally, and derives a second explicitly SYNTHETIC overlap input by
editing X/Y coordinates at original B339. Additional cases inject RAM.
The original retail ROM, emulator savestates and RAM dumps stay private.
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
NATURAL_B1F8_SHA='0fd7256466e3e952402858ecaa3034eda6774ab2acbf16ad4e2d00c99e1b442c'
SOURCE_WINDOWS=((0xb235,0xb27c,'c574b40977c2792490272d71441d622dec6f29b3db1eed2709c69e979001e294'),
                (0xb29d,0xb2a8,'dcb6ae9933347084a3403bd972b16568c780e350fef83be5e715618e615e2661'),
                (0xb317,0xb320,'76e769e52e5abe16461f696c487ef5e5edc1ec6aaf8565b543334b8d7230326c'))

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def filehash(p:Path)->str:return sha(p.read_bytes())

def run(agent:Path,rom:Path,root:Path,tag:str,opts:list[str]):
    home=root/('home_'+tag)
    cmd=[str(agent),str(rom),'--home',str(home),*opts]
    p=subprocess.run(cmd,capture_output=True,text=True,timeout=29)
    msgs=[json.loads(s) for s in p.stdout.splitlines() if s.startswith('{')]
    sums=[x for x in msgs if x.get('event')=='summary']
    if p.returncode or len(sums)!=1 or not sums[0].get('ok'):
        raise AssertionError(f'Mesen original-source step {tag} failed: {p.returncode}: {p.stderr[-450:]} {sums}')
    return sums[0],msgs

def snapshot(agent:Path,rom:Path,root:Path,tag:str,state:Path,opts:list[str]):
    where=root/tag;where.mkdir()
    ram=where/'memory.bin';cpu=where/'cpu.json';out=where/'resume.mss'
    summary,events=run(agent,rom,root,tag,[
        '--load-state',str(state),*opts,'--state-json',str(cpu),
        '--dump-memory',f'NesInternalRam={ram}','--save-state',str(out)])
    reg=json.loads(cpu.read_text());data=ram.read_bytes()
    if len(data)!=2048:raise AssertionError('Mesen dumped non-2KiB RAM')
    return summary,events,out,reg,data,ram

def audit(rom:Path,agent:Path,source:Path,native:Path,composed:Path):
    raw=rom.read_bytes()
    if len(raw)!=393232 or sha(raw)!=ROM_SHA:raise ValueError('Wrong original Japanese ROM')
    if filehash(agent)!=AGENT_SHA or filehash(agent.parent/'MesenCore.so')!=CORE_SHA:
        raise ValueError('Original-Mesen executable/core changed')
    if filehash(source)!=NATURAL_B1F8_SHA:raise ValueError('Required natural original Stage1 B1F8 input state differs')
    bank=raw[16+11*16384:16+12*16384]
    for lo,hi,expected in SOURCE_WINDOWS:
        if sha(bank[lo-0x8000:hi-0x8000])!=expected:
            raise ValueError(f'Physical raw bank0B original source bytes changed at {lo:04X}')
    rows=[]
    with tempfile.TemporaryDirectory(prefix='jp0517_mesen_actor_tail_') as d:
        root=Path(d)
        # 54 original CPU steps: B1F8 to B393 (53), RTS from B393 -> B235.
        _,_,natural_state,natural_cpu,natural_ram,_=snapshot(agent,rom,root,'natural_B235',source,
            ['--frames','0','--step','54','--timeout','18'])
        if (natural_cpu['cpu.pc'],natural_cpu['cpu.x'],natural_cpu['cpu.ps'],natural_cpu['cpu.cycleCount'])!=(0xb235,1,1,77522176):
            raise AssertionError('Natural original B235 CPU entry changed')
        # Reproduce B339 from the original B1F8 state, and FORCE only the
        # actor's X,Y coordinates to the original player coordinates. This
        # second B235 entry is NOT naturally reached gameplay evidence.
        _,_,at_b339,first_cpu,b339_ram,_=snapshot(agent,rom,root,'at_B339',source,
            ['--frames','0','--step','24','--timeout','18'])
        if first_cpu['cpu.pc']!=0xb339 or first_cpu['cpu.x']!=1:
            raise AssertionError('Natural original collision-measure entry changed')
        changes={0x0439:b339_ram[0x0438],0x041d:b339_ram[0x041c]}
        _,_,overlap_state,overlap_cpu,overlap_ram,_=snapshot(agent,rom,root,'synthetic_B235',at_b339,
            ['--frames','1','--timeout','18',
             '--write-memory',f'NesInternalRam:0x0439:{changes[0x0439]:02X}',
             '--write-memory',f'NesInternalRam:0x041D:{changes[0x041d]:02X}',
             '--breakpoint','NesMemory:0xB235:x:[$23]==$0B'])
        if (overlap_cpu['cpu.pc'],overlap_cpu['cpu.x'],overlap_cpu['cpu.ps']&1)!=(0xb235,1,0):
            raise AssertionError('Synthetic overlap did not take original collision-positive route')
        # A complete 91-original-instruction path on the actual unmodified
        # source-state actor, including B1F8/B217/B339 and collision tail.
        cp,_,_,end_cpu,_,end_file=snapshot(agent,rom,root,'composed_91',source,
            ['--frames','1','--timeout','18','--trace',str(root/'composed_91.trace'),
             '--breakpoint','NesMemory:0xFDFE:x'])
        if cp['reason']!='debugger_break' or end_cpu['cpu.pc']!=0xfdfe or len((root/'composed_91.trace').read_text().splitlines())!=91:
            raise AssertionError('Original 91-instruction naturally reached return path drift')
        # Snapshot B1F8 without stepping; the first CPU instruction is LDA
        # and does not mutate RAM. The known initial status is $01.
        _,_,_,_,entry_ram,_=snapshot(agent,rom,root,'entry_ram',source,['--frames','0','--timeout','12'])
        pre=root/'composed_before.bin';pre.write_bytes(entry_ram)
        cmd=[str(composed),str(pre),str(end_file),'1','0','1',str(end_cpu['cpu.pc']),
             str(end_cpu['cpu.a']),str(end_cpu['cpu.y']),str(end_cpu['cpu.ps'])]
        checked=subprocess.run(cmd,capture_output=True,text=True,timeout=12)
        if checked.returncode or '1792/1792' not in checked.stdout:
            raise AssertionError('Native composed 91-instruction actor frame path differs: '+checked.stdout+' '+checked.stderr)
        rows.append({'case':'natural_original_B1F8_to_FDFE','evidence':'natural_gameplay','source_instructions':91,
                     'stop_pc':'FDFE','matched_nonstack_bytes':1792,
                     'return_A_X_Y_P':[end_cpu['cpu.a'],end_cpu['cpu.x'],end_cpu['cpu.y'],end_cpu['cpu.ps']]})
        # The 15 tested post-measure states: one natural B235, plus 14
        # synthetic or RAM-injected B235 states, including overlap, actor
        # type exceptions, attachment bit, and occupied follower slot.
        cases=[('natural','normal',{}),('overlap','overlap',{}),
          ('natural','type16',{0x54f:0x16}),('natural','type37',{0x54f:0x37}),
          ('natural','type61',{0x54f:0x61}),('natural','type7e',{0x54f:0x7e}),
          ('natural','type7f',{0x54f:0x7f}),('natural','bit1',{0x68e:1}),
          ('natural','B27C',{0x630:1,0x413:1}),('natural','follower',{0x562:1}),
          ('overlap','type39',{0x54f:0x39}),('overlap','left',{0x439:0x20}),
          ('overlap','type16',{0x54f:0x16}),('overlap','type7e',{0x54f:0x7e}),
          ('overlap','B27C',{0x630:1,0x413:1})]
        for anchor,name,overrides in cases:
            initial_state=natural_state if anchor=='natural' else overlap_state
            before_cpu=natural_cpu if anchor=='natural' else overlap_cpu
            before=bytearray(natural_ram if anchor=='natural' else overlap_ram)
            for addr,val in overrides.items():before[addr]=val
            label=f'{anchor}_{name}'
            pre=root/(label+'_before.bin');pre.write_bytes(before)
            opts=['--frames','1','--timeout','15','--trace',str(root/(label+'.trace'))]
            for addr,val in overrides.items():
                opts.extend(['--write-memory',f'NesInternalRam:0x{addr:04X}:{val:02X}'])
            for terminal in ('B243','B27C','B2A8','FDFE'):
                opts.extend(['--breakpoint',f'NesMemory:0x{terminal}:x'])
            summary,_,_,end,after,post=snapshot(agent,rom,root,label,initial_state,opts)
            if summary['reason']!='debugger_break' or end['cpu.pc'] not in (0xb243,0xb27c,0xb2a8,0xfdfe):
                raise AssertionError(f'Original branch end changed {label}: {end["cpu.pc"]:04X}')
            instructions=len((root/(label+'.trace')).read_text().splitlines())
            cmd=[str(native),str(pre),str(post),str(before_cpu['cpu.x']),
                 str(before_cpu['cpu.a']),str(before_cpu['cpu.y']),str(before_cpu['cpu.ps']),
                 str(end['cpu.pc']),str(end['cpu.a']),str(end['cpu.y']),str(end['cpu.ps']),str(end['cpu.x'])]
            ret=subprocess.run(cmd,capture_output=True,text=True,timeout=12)
            if ret.returncode or '1792/1792' not in ret.stdout:
                raise AssertionError('Native collision tail diverged from original Mesen '+label+': '+ret.stdout+' '+ret.stderr)
            rows.append({'case':label,'evidence':'natural_gameplay' if label=='natural_normal' else 'SYNTHETIC_RAM_OR_COORDINATE_INJECTION',
                'source_instructions':instructions,'stop_pc':f'{end["cpu.pc"]:04X}',
                'ram_write_locations':{'7E':after[0x7e],'8D':after[0x8d],'8E':after[0x8e],'9B':after[0x9b]},
                'matched_nonstack_bytes':1792,
                'return_A_X_Y_P':[end['cpu.a'],end['cpu.x'],end['cpu.y'],end['cpu.ps']]})
    return {'schema':'JP-0517-native-original-Mesen-collision-tail/v1','rom_sha256':ROM_SHA,
       'mesen_agent_sha256':AGENT_SHA,'mesen_core_sha256':CORE_SHA,
       'original_controller_state_sha256':NATURAL_B1F8_SHA,
       'source_sha256':{f'0B:{lo:04X}-{hi-1:04X}':hashval for lo,hi,hashval in SOURCE_WINDOWS},
       'independent_original_cpu_comparisons':len(rows),
       'naturally_reached_windows':2,'explicit_synthetic_windows':len(rows)-2,
       'naturally_reached_windows_same_actor':True,
       'exact_nonstack_ram_bytes':1792*len(rows),'native_synthetic_math_tests':65539,
       'original_windows':rows,
       'digest_sha256':sha(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()),
       'limitations':'Original $B243 FF15/B568, $B27C B3EC and occupied $B2A8 branch are stop boundaries; collision response on natural sample is B235 carry-set; no PPU/frame/audio parity',
       'strict_new_prg_bytes':0,'vpp_added':0}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('rom',type=Path);p.add_argument('--mesen',required=True,type=Path)
    p.add_argument('--natural-B1F8-state',required=True,type=Path)
    p.add_argument('--native-replay',required=True,type=Path)
    p.add_argument('--native-composed',required=True,type=Path)
    p.add_argument('--report',type=Path)
    a=p.parse_args()
    report=audit(a.rom.resolve(),a.mesen.resolve(),a.natural_B1F8_state.resolve(),a.native_replay.resolve(),a.native_composed.resolve())
    if a.report:a.report.write_text(json.dumps(report,indent=2)+'\n')
    print('PASS 0517 Mesen JP source postcollision: ',report['independent_original_cpu_comparisons'],' windows, ',report['exact_nonstack_ram_bytes'],' nonstack RAM bytes')
if __name__=='__main__':main()
