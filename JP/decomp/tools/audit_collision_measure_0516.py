#!/usr/bin/env python3
"""Original ROM Mesen source versus structured C++ actor B339 collision measurement.

Only unchanged original-ROM and controller-reached natural B339 source state is
natural gameplay evidence. Each artificial RAM override is clearly synthetic.
Private savestates, Mesen traces, and original ROM bytes stay outside Git.
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
NATURAL_B339_RAM_SHA='938ba9d9775a9544da06f666802f34f4b4ee20096eb396c8480ade73fb7fdc67'

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def sha_file(p:Path)->str:return sha(p.read_bytes())

def scenarios(original:bytes):
    assert len(original)==2048
    # Variants deliberately edit only original Mesen internal RAM, NOT ROM.
    cases=[('natural_actor3D',{})]
    types=(0x00,0x08,0x16,0x3b,0x3d,0x57,0x68)
    rooms=(0,3,4,8)
    for i in range(48):
        typ=types[i%len(types)];room=rooms[(i//len(types))%len(rooms)]
        player_x=(0x20+i*13)&255
        px_mode=i%6
        actor_x=(player_x+[0,1,6,12,128,252][px_mode])&255
        player_y=(0x20+i*17)&255
        actor_y=(player_y+[0,1,5,12,128,252][(i//3)%6])&255
        mod={0x7f:room,0x054f:typ,0x048d:0x08 if i%3==0 else 0,
             0x0401:0x92,0x0438:player_x,0x0439:actor_x,
             0x041c:player_y,0x041d:actor_y}
        cases.append((f'synthetic_{i:02}',mod))
    return cases

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('rom',type=Path)
    p.add_argument('--mesen',type=Path,required=True)
    p.add_argument('--private-state',type=Path,required=True)
    p.add_argument('--native-replay',type=Path,required=True)
    p.add_argument('--report',type=Path)
    a=p.parse_args();rom=a.rom.resolve();agent=a.mesen.resolve();natural=a.private_state.resolve();native=a.native_replay.resolve()
    if sha_file(natural)!=NATURAL_B1F8_SHA:raise ValueError('Expected independently authenticated original controller-reached B1F8 state')
    if sha_file(rom)!=ROM_SHA or rom.stat().st_size!=393232:raise ValueError('Original Japanese ROM changed')
    if sha_file(agent)!=AGENT_SHA or sha_file(agent.parent/'MesenCore.so')!=CORE_SHA:raise ValueError('Original Mesen2 binary changed')
    prg=rom.read_bytes()[16:16+262144];bank=prg[11*16384:12*16384]
    slices=[('B339_B393',0xb339,0xb394),('80B3_80CA',0x80b3,0x80ca),('BB05_9',0xbb05,0xbb0e),('BB0E_9',0xbb0e,0xbb17),('BB80_105',0xbb80,0xbbe9),('BC08_105',0xbc08,0xbc71),('B394_2',0xb394,0xb396)]
    chunks={name:sha(bank[lo-0x8000:hi-0x8000]) for name,lo,hi in slices}
    with tempfile.TemporaryDirectory(prefix='jp0516_original_mesen_') as td:
        root=Path(td)
        # Derive B339 from *natural original B1F8* using 24 CPU steps:
        # 12 actor eligibility, 11 admission, 1 source JSR B339.
        prefix=root/'derive_B339';prefix.mkdir()
        private=prefix/'atB339.mss'
        dcmd=[str(agent),str(rom),'--home',str(prefix/'home'),
              '--load-state',str(natural),'--frames','0','--step','24','--timeout','12',
              '--save-state',str(private),'--state-json',str(prefix/'cpu.json'),
              '--dump-memory',f'NesInternalRam={prefix}/ram.bin', '--trace',str(prefix/'trace.txt')]
        dproc=subprocess.run(dcmd,capture_output=True,text=True,timeout=20)
        derived=json.loads((prefix/'cpu.json').read_text());derived_ram=(prefix/'ram.bin').read_bytes()
        if dproc.returncode or (derived['cpu.pc'],derived['cpu.x'],derived['cpu.cycleCount'])!=(0xb339,1,77522077) or sha(derived_ram)!=NATURAL_B339_RAM_SHA:
            raise AssertionError('Original B1F8->B339 derived state was not produced naturally')
        if len((prefix/'trace.txt').read_text().splitlines())!=24:
            raise AssertionError('Original B1F8 source step count drift')
        def launch(tag,changes):
            dest=root/tag;dest.mkdir()
            cmd=[str(agent),str(rom),'--home',str(dest/'home'),'--load-state',str(private)]
            for addr,val in changes.items():cmd+=['--write-memory',f'NesInternalRam:0x{addr:04X}:{val:02X}']
            cmd+=['--frames','1','--timeout','12',
                 '--breakpoint','NesMemory:0xB393:x:[$23]==$0B',
                 '--state-json',str(dest/'cpu.json'),
                 '--dump-memory',f'NesInternalRam={dest}/ram.bin',
                 '--trace',str(dest/'trace.txt')]
            done=subprocess.run(cmd,capture_output=True,text=True,timeout=20)
            records=[json.loads(line) for line in done.stdout.splitlines() if line.startswith('{')]
            summaries=[entry for entry in records if entry.get('event')=='summary']
            if done.returncode or len(summaries)!=1 or summaries[0]['reason']!='debugger_break':
                raise AssertionError(f'Mesen source execution failed {tag}: {done.returncode} {done.stderr[-400:]} {summaries}')
            cpu=json.loads((dest/'cpu.json').read_text());ram=(dest/'ram.bin').read_bytes()
            trace=(dest/'trace.txt').read_text().splitlines()
            if cpu['cpu.pc']!=0xb393 or cpu['cpu.x']!=1 or len(ram)!=2048 or not trace[0].startswith('B339 '):
                raise AssertionError(f'Original B339 input boundary changed: {tag} {cpu["cpu.pc"]:X}')
            return dest,cpu,ram,trace
        # Verify original natural state by emulator-mapped CPU register state,
        # RAM digest, and cycle, not incidental compressed .mss serialization.
        initial=root/'natural';initial.mkdir()
        c=[str(agent),str(rom),'--home',str(initial/'home'),'--load-state',str(private),
          '--frames','0','--state-json',str(initial/'cpu.json'),
          '--dump-memory',f'NesInternalRam={initial}/ram.bin','--disassemble','0xB339:1']
        res=subprocess.run(c,capture_output=True,text=True,timeout=20)
        vals=[json.loads(x) for x in res.stdout.splitlines() if x.startswith('{')]
        pre_cpu=json.loads((initial/'cpu.json').read_text());before=(initial/'ram.bin').read_bytes()
        mapped=[v for v in vals if v.get('event')=='disassembly']
        if res.returncode or (pre_cpu['cpu.pc'],pre_cpu['cpu.x'],pre_cpu['cpu.cycleCount'])!=(0xb33b,1,77522080):
            raise AssertionError('Not the naturally reached original Stage1 actor B339 entry (Mesen frames=0 executes LDY $7F once)')
        if sha(before)!='938ba9d9775a9544da06f666802f34f4b4ee20096eb396c8480ade73fb7fdc67':
            raise AssertionError('Natural original Stage1 RAM digest mismatch')
        if not any(v.get('address')==0xb339 and v.get('absolute_type')=='NesPrgRom' and v.get('absolute_address')==0x2f339 for v in mapped):
            raise AssertionError('Original B339 mapped bank0B physical ROM mismatch')
        rows=[]
        # A second window of the very SAME actor event, from natural B1F8
        # through B217, JSR B339, horizontal distance, and arrival at B393.
        composed=root/'composed_natural';composed.mkdir()
        composed_args=[str(agent),str(rom),'--home',str(composed/'home'),
                       '--load-state',str(natural),'--frames','1','--timeout','12',
                       '--breakpoint','NesMemory:0xB393:x:[$23]==$0B',
                       '--dump-memory',f'NesInternalRam={composed}/result.bin',
                       '--state-json',str(composed/'result.json'),
                       '--trace',str(composed/'trace.txt')]
        cp=subprocess.run(composed_args,capture_output=True,text=True,timeout=20)
        cjson=json.loads((composed/'result.json').read_text())
        if cp.returncode or cjson['cpu.pc']!=0xb393 or len((composed/'trace.txt').read_text().splitlines())!=53:
            raise AssertionError('Natural original 53-instruction actor collision prefix changed')
        composed_input=root/'composed_before.bin';composed_input.write_bytes(derived_ram)
        composed_command=[str(native),str(composed_input),str(composed/'result.bin'),
                          '1','68','0','1',str(cjson['cpu.pc']),str(cjson['cpu.a']),
                          str(cjson['cpu.y']),str(cjson['cpu.ps']),'composed']
        cr=subprocess.run(composed_command,capture_output=True,text=True,timeout=8)
        if cr.returncode or '1792/1792' not in cr.stdout:
            raise AssertionError('Source original full B1F8->B393 C++ pipeline mismatch: '+cr.stdout+' '+cr.stderr)
        rows.append({'case':'natural_B1F8_to_B393_same_actor','evidence':'natural-original-game, same original actor as shorter window',
                     'axis':'horizontal_early_exit','original_steps':53,'native_equal_original_ram_bytes':1792,
                     'original_A_X_Y_P':[cjson['cpu.a'],cjson['cpu.x'],cjson['cpu.y'],cjson['cpu.ps']],
                     'original_nonstack_ram_sha256':sha((composed/'result.bin').read_bytes()[:256]+(composed/'result.bin').read_bytes()[512:])})
        for index,(tag,mods) in enumerate(scenarios(before)):
            dest,out_cpu,ram,trace=launch(tag,mods)
            edited=bytearray(before)
            for addr,val in mods.items():edited[addr]=val
            infile=root/f'input{index}.bin';infile.write_bytes(edited)
            args=[str(native),str(infile),str(dest/'ram.bin'),
                  '1','0','0','2',
                  str(out_cpu['cpu.pc']),str(out_cpu['cpu.a']),str(out_cpu['cpu.y']),str(out_cpu['cpu.ps'])]
            check=subprocess.run(args,capture_output=True,text=True,timeout=8)
            if check.returncode or '1792/1792' not in check.stdout:
                raise AssertionError(f'Original CPU vs native difference: {tag} {check.stdout} {check.stderr}')
            branch='vertical' if any(x.startswith('80C1 ') for x in trace) else 'horizontal_early_exit'
            rows.append({'case':tag,'evidence':'natural-original-game' if not mods else 'SYNTHETIC_RAM_override',
                         'axis':branch,'original_steps':len(trace),
                         'native_equal_original_ram_bytes':1792,
                         'original_A_X_Y_P':[out_cpu['cpu.a'],out_cpu['cpu.x'],out_cpu['cpu.y'],out_cpu['cpu.ps']],
                         'original_nonstack_ram_sha256':sha(ram[:256]+ram[512:])})
            if (index+1)%12==0:print('PASS 0516 original collision measure',index+1,'/',len(scenarios(before)),flush=True)
    summary={'schema':'JP-0516-original-Mesen-native-B339-collision-measure/v1',
       'rom_sha256':ROM_SHA,'mesen_agent_sha256':AGENT_SHA,'mesen_core_sha256':CORE_SHA,
       'source_ranges_sha256':chunks,'physical_prg_entry':'02F339',
       'natural_pc_B339_cpu_cycle':77522077,
       'natural_B1F8_state_sha256':NATURAL_B1F8_SHA,
       'derived_original_B339_ram_sha256':NATURAL_B339_RAM_SHA,
       'scenarios':len(rows),'natural_scenarios':2,'synthetic_scenarios':len(rows)-2,
       'natural_windows_same_actor':True,
       'horizontal_early_exits':sum(r['axis']=='horizontal_early_exit' for r in rows),
       'vertical_compares':sum(r['axis']=='vertical' for r in rows),
       'original_ram_bytes_matched':1792*len(rows),
       'comparison_digest_sha256':sha(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()),
       'cases_first_and_last':rows[:2]+rows[-2:],
       'bounded_entry':'room $7F<=8; actor type<=68; $B7=0; $048C==8 with $0400>=EE excluded',
       'excluded':'B7 E5BE branch, B396 alternate, actual B235 collision response, integrated full actor frame',
       'certified_new_prg_bytes':0,'vpp_added':0}
    if a.report:a.report.write_text(json.dumps(summary,indent=2)+'\n')
    print('PASS original JP B339 native:',summary['scenarios'],'cases;',summary['original_ram_bytes_matched'],'exact nonstack RAM bytes')
if __name__=='__main__':main()
