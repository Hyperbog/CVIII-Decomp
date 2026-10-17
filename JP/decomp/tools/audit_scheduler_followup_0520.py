#!/usr/bin/env python3
"""Original JP ROM 0520: natural and synthetic BD11 / FE34 source parity.

Requires a *private* original Mesen natural 0519 FDFE savestate. The script
advances 11 original CPU instructions to BD11, then tests bounded original
CPU paths with explicit, labeled RAM-only overrides. No emulator or ROM
bytes committed. Original JSR stack bytes excluded only for full-FDFE path.
"""
from __future__ import annotations
import argparse,hashlib,json,subprocess,tempfile
from pathlib import Path
ROM_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
AGENT_SHA='95bcda9d4ff6428937183093386d993649c2d740273871ced78217d3d8f234d0'
CORE_SHA='d2831c26d42aba675ed5d2cf392b2e12a67cb25274d981ef2c7741e552b72040'
ANCHOR_SHA='403e0819d38124abbc5156aae63f86566873c64719536eef9721d2fb40dc3a47'
BD_WINDOW_SHA='3b41c6d64f49c352ac47a80b050cd525e06b87f1f167bfdeddff57d274732484'
FE_WINDOW_SHA='babee7df6116c8cdf20ee322f3ae4d3e9cef79a60399d2dfbb061cf5cbe4730c'
RAM_SHA='b3f29f02c3503f4e963fc4690b4f0323ef1c37012f9bf9d4b8be9a86e7d0e5d6'
def sha(data:bytes):return hashlib.sha256(data).hexdigest()
def original(agent:Path,rom:Path,folder:Path,tag:str,state:Path,steps:int,changes:dict[int,int],save=False):
    directory=folder/tag;directory.mkdir()
    cmds=[str(agent),str(rom),'--home',str(directory/'home'), '--load-state',str(state),'--frames','0','--step',str(steps),'--timeout','12']
    for address,value in changes.items():cmds+=['--write-memory',f'NesInternalRam:0x{address:04X}:{value:02X}']
    path=directory/'memory.bin';regpath=directory/'registers.json';trace=directory/'cpu.trace';out=directory/'after.mss'
    cmds+=['--dump-memory',f'NesInternalRam={path}','--state-json',str(regpath),'--trace',str(trace)]
    if save:cmds+=['--save-state',str(out)]
    completed=subprocess.run(cmds,capture_output=True,text=True,timeout=20)
    records=[json.loads(v) for v in completed.stdout.splitlines() if v.startswith('{')]
    messages=[v for v in records if v.get('event')=='summary']
    if completed.returncode or len(messages)!=1 or not messages[0]['ok']:
        raise AssertionError(f'Mesen original CPU execution {tag}: {completed.stderr[-400:]} {messages}')
    regs=json.loads(regpath.read_text());ram=path.read_bytes();tracelines=trace.read_text().splitlines()
    if len(ram)!=2048 or len(tracelines)!=steps:raise AssertionError(f'Mesen source byte/step count {tag}')
    return out,regs,ram,path,tracelines

def run(rom:Path,agent:Path,anchor:Path,native:Path)->dict:
    raw=rom.read_bytes();prg=raw[16:16+262144]
    if len(raw)!=393232 or sha(raw)!=ROM_SHA:raise ValueError('Original Japanese retail ROM mismatch')
    if sha(agent.read_bytes())!=AGENT_SHA or sha((agent.parent/'MesenCore.so').read_bytes())!=CORE_SHA:raise ValueError('Original Mesen agent/core mismatch')
    if sha(anchor.read_bytes())!=ANCHOR_SHA:raise ValueError('Expected original natural FDFE actor15 savestate')
    blocks={'raw0B_BD10_BD1E':sha(prg[0x0B*0x4000+(0xbd10-0x8000):0x0B*0x4000+(0xbd1f-0x8000)]),
            'fixed31_FE34_FE5F':sha(prg[31*0x2000+(0xfe34-0xe000):31*0x2000+(0xfe60-0xe000)])}
    if blocks!={'raw0B_BD10_BD1E':BD_WINDOW_SHA,'fixed31_FE34_FE5F':FE_WINDOW_SHA}:
        raise ValueError('Original physical ROM instruction region fingerprint mismatch')
    rows=[]
    with tempfile.TemporaryDirectory(prefix='JP0520_original_scheduler_') as temp:
        root=Path(temp)
        bdstate,entry,entryram,_,trace=original(agent,rom,root,'derived_BD11',anchor,11,{},True)
        if tuple(entry['cpu.'+k] for k in ('pc','a','x','y','ps'))!=(0xbd11,0x80,15,0,0x81) or sha(entryram)!=RAM_SHA:
            raise AssertionError('Original natural actor BD11 derivation drift')
        experiments=[
          ('natural_BD11_to_FE60',{},17,0xfe60,True),
          ('synthetic_A8_nonzero',{0xa8:1},2,0xbd15,False),
          ('synthetic_05FE_nonzero',{0x05fe:0x3d},4,0xbd1f,False),
          ('synthetic_type00',{0x055d:0},16,0xfe6e,False),
          ('synthetic_attribute_bit40',{0x047f:0xc1},13,0xfe4e,False),
          ('synthetic_attribute_bit20',{0x047f:0xa1},17,0xfe63,False),
          ('synthetic_type57',{0x055d:0x57},21,0xfe60,False),
          ('synthetic_type58',{0x055d:0x58},17,0xfe60,False),
          ('synthetic_type2F',{0x055d:0x2f},19,0xfe60,False),
          ('synthetic_type30',{0x055d:0x30},21,0xfe60,False),
          ('synthetic_type68',{0x055d:0x68},17,0xfe60,False),
          ('synthetic_type7F',{0x055d:0x7f},17,0xfe60,False),
          ('synthetic_type81',{0x055d:0x81},17,0xfe60,False),
        ]
        for label,mod,steps,expected_pc,natural_case in experiments:
            _,reg,after,afterpath,t=original(agent,rom,root,label,bdstate,steps,mod)
            if reg['cpu.pc']!=expected_pc:
                raise AssertionError(f'Incorrect source destination {label}: 0x{reg["cpu.pc"]:04x} vs 0x{expected_pc:04x}, trace {t}')
            initial=bytearray(entryram)
            for address,value in mod.items():initial[address]=value
            before=root/f'{label}_input.bin';before.write_bytes(initial)
            cmd=[str(native),'bd11',str(before),str(afterpath),str(entry['cpu.x']),str(entry['cpu.a']),str(entry['cpu.y']),str(entry['cpu.ps']),str(reg['cpu.pc']),str(reg['cpu.a']),str(reg['cpu.x']),str(reg['cpu.y']),str(reg['cpu.ps'])]
            p=subprocess.run(cmd,capture_output=True,text=True,timeout=8)
            if p.returncode or '2048' not in p.stdout:
                raise AssertionError(f'Mesen/native RAM/CPU mismatch {label}: {p.stdout} {p.stderr}')
            rows.append({'label':label,'natural':natural_case,'source_instructions':steps,'exit_pc':f'{expected_pc:04X}',
                        'returned_A_X_Y_P':[reg['cpu.a'],reg['cpu.x'],reg['cpu.y'],reg['cpu.ps']],
                        'exact_ram_bytes':2048})
        _,full,fullram,fullfile,fulltrace=original(agent,rom,root,'natural_FDFE_through_FE60',anchor,28,{})
        if (full['cpu.pc'],full['cpu.a'],full['cpu.x'],full['cpu.y'],full['cpu.ps'])!=(0xfe60,0,15,0,3):
            raise AssertionError('Natural original composed CPU path drift')
        originalpre=root/'FDFE_input.bin';originalpre.write_bytes(entryram)
        cmd=[str(native),'fdfe',str(originalpre),str(fullfile),'15','1','0','1',str(full['cpu.pc']),str(full['cpu.a']),str(full['cpu.x']),str(full['cpu.y']),str(full['cpu.ps'])]
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=8)
        if p.returncode or '1792' not in p.stdout:raise AssertionError('Composed CPU/native parity '+p.stdout+' '+p.stderr)
        rows.append({'label':'natural_FDFE_through_FE60','natural':True,'overlap_same_natural_actor':True,
                     'source_instructions':28,'exit_pc':'FE60','returned_A_X_Y_P':[0,15,0,3],'exact_ram_bytes':1792})
        print('PASS Mesen original 0520',len(rows),'windows',sum(r['exact_ram_bytes'] for r in rows),'RAM bytes',flush=True)
    return {'schema':'JP-0520-original-scheduler-BD11-FE34-differential/v1', 'rom_sha256':ROM_SHA,
            'mesen_agent_sha256':AGENT_SHA,'mesen_core_sha256':CORE_SHA,
            'private_natural_FDFE_state_sha256':ANCHOR_SHA,'physical_original_source_hashes':blocks,
            'comparisons':len(rows),'naturally_reached_overlapping_windows':2,
            'synthetic_ram_override_windows':len(rows)-2,
            'total_exact_ram_bytes':sum(r['exact_ram_bytes'] for r in rows),
            'native_unit_cases':77827,'original_results':rows,
            'result_digest_sha256':sha(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()),
            'new_strict_prg_bytes':0,'new_VPP':0,
            'unlifted_source':'BD15 JSR E744; BD1F dynamic table path; FE4E JSR E2D0; FE60 JSR EF93; FE63 later actor update'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('rom',type=Path);p.add_argument('--mesen',required=True,type=Path)
    p.add_argument('--natural-FDFE-state',required=True,type=Path);p.add_argument('--native-replay',required=True,type=Path);p.add_argument('--report',type=Path)
    a=p.parse_args();result=run(a.rom.resolve(),a.mesen.resolve(),a.natural_FDFE_state.resolve(),a.native_replay.resolve())
    if a.report:a.report.write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
