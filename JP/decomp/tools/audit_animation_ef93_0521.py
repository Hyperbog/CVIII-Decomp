#!/usr/bin/env python3
"""Original JP Mesen EF93 original-source differential: 2 natural, 36 RAM-injected."""
import argparse,hashlib,json,subprocess,tempfile
from pathlib import Path
ROM='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
AGENT='95bcda9d4ff6428937183093386d993649c2d740273871ced78217d3d8f234d0'
CORE='d2831c26d42aba675ed5d2cf392b2e12a67cb25274d981ef2c7741e552b72040'
STATE='403e0819d38124abbc5156aae63f86566873c64719536eef9721d2fb40dc3a47'
def H(data):return hashlib.sha256(data).hexdigest()
def call(exe,rom,root,name,state,steps,mods):
 d=root/name;d.mkdir();cp=d/'cpu.json';ram=d/'ram.bin';save=d/'state.mss';trace=d/'trace.txt'
 args=[str(exe),str(rom),'--home',str(d/'home'),'--load-state',str(state),'--frames','0','--step',str(steps),'--timeout','12']
 for k,v in mods.items():args+=['--write-memory',f'NesInternalRam:0x{k:04X}:{v:02X}']
 args+=['--state-json',str(cp),'--dump-memory',f'NesInternalRam={ram}','--trace',str(trace),'--save-state',str(save)]
 p=subprocess.run(args,capture_output=True,text=True,timeout=20)
 summaries=[json.loads(t) for t in p.stdout.splitlines() if t.startswith('{') and '"event":"summary"' in t]
 if p.returncode or len(summaries)!=1 or not summaries[0]['ok']:raise AssertionError('original Mesen failure '+name+p.stderr[-200:])
 r=ram.read_bytes()
 if len(r)!=2048 or len(trace.read_text().splitlines())!=steps:raise AssertionError('Mesen trace/RAM drift '+name)
 return json.loads(cp.read_text()),r,ram,save,d
def check(native,folder,initial,afterfile,entry,exit,composed=False):
 pre=folder/'pre.bin';pre.write_bytes(initial)
 args=[str(native),str(pre),str(afterfile),str(entry['cpu.x']),str(entry['cpu.a']),str(entry['cpu.y']),str(entry['cpu.ps']),str(exit['cpu.pc']),str(exit['cpu.a']),str(exit['cpu.y']),str(exit['cpu.ps']),str(exit['cpu.x'])]
 if composed:args+=['composed']
 p=subprocess.run(args,capture_output=True,text=True,timeout=8)
 if p.returncode or (('1792' if composed else '2048')+' RAM bytes') not in p.stdout:raise AssertionError('native mismatch '+folder.name+p.stdout+p.stderr)
def audit(rom,exe,state,native):
 data=rom.read_bytes()
 if len(data)!=393232 or H(data)!=ROM or H(exe.read_bytes())!=AGENT or H((exe.parent/'MesenCore.so').read_bytes())!=CORE or H(state.read_bytes())!=STATE:raise ValueError('original ROM, emulator or natural state identity drift')
 bank=data[16+31*8192:16+32*8192]
 blocks={'EF93_EFD1':bank[0xf93:0xfd2],'EFE0_EFE1':bank[0xfe0:0xfe2],'F359_F388':bank[0x1359:0x1389]}
 if blocks['EFE0_EFE1']!=bytes.fromhex('59 f3') or len(blocks['F359_F388'])!=48:raise ValueError('original indexed animation data drift')
 frames=blocks['F359_F388'];rows=[]
 with tempfile.TemporaryDirectory(prefix='jp0521_') as work:
  root=Path(work)
  entry,input_ram,_,at_ef93,_=call(exe,rom,root,'natural_derive',state,29,{})
  if (entry['cpu.pc'],entry['cpu.x'],entry['cpu.a'],entry['cpu.y'],entry['cpu.ps'])!=(0xef93,15,0,0,3):raise AssertionError('natural EF93 entry drift')
  def record(name,mods,steps,natural):
   final,ram,post,_,folder=call(exe,rom,root,name,at_ef93,steps,mods)
   if (final['cpu.pc'],final['cpu.x'])!=(0xfe63,15):raise AssertionError('unexpected original return '+name)
   pre=bytearray(input_ram)
   for k,v in mods.items():pre[k]=v
   check(native,folder,pre,post,entry,final)
   rows.append({'case':name,'natural':natural,'steps':steps,'bytes':2048,'regs':[final['cpu.a'],final['cpu.x'],final['cpu.y'],final['cpu.ps']],'ram_sha256':H(ram)})
  record('natural_ef93',{},28,True)
  for f in range(16):
   t=frames[f*3+2]
   for suffix,delta,steps in (('below',3,26),('equal',2,28)):
    record(f'synthetic_{f:02d}_{suffix}',{0x58b:1,0x5b9:f,0x5a2:(t-delta)&255,0x49b:14},steps,False)
  for timer in (0,2,127,255):record(f'synthetic_timer_{timer}',{0x58b:timer,0x5b9:255,0x49b:255},3,False)
  final,ram,post,_,folder=call(exe,rom,root,'natural_57_step_composed',state,57,{})
  if (final['cpu.pc'],final['cpu.x'])!=(0xfe63,15):raise AssertionError('connected FDFE source drift')
  check(native,folder,input_ram,post,{'cpu.x':15,'cpu.a':1,'cpu.y':0,'cpu.ps':1},final,True)
  rows.append({'case':'natural_57_step_composed','natural':True,'overlaps_same_actor':True,'steps':57,'bytes':1792,'regs':[final['cpu.a'],final['cpu.x'],final['cpu.y'],final['cpu.ps']],'nonstack_sha256':H(ram[:256]+ram[512:])})
 return {'schema':'JP-0521-original-EF93-source/v1','rom_sha256':ROM,'private_natural_FDFE_state_sha256':STATE,'source_hashes':{k:H(v) for k,v in blocks.items()},'comparisons':len(rows),'natural_windows':2,'synthetic_windows':36,'independent_natural_events':1,'total_exact_ram_bytes':sum(r['bytes'] for r in rows),'native_unit_cases':65547,'outcome_digest_sha256':H(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()),'samples':rows[:2]+rows[-2:],'strict_new_prg_bytes':0,'vpp_added':0}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('rom',type=Path);p.add_argument('--mesen',required=True,type=Path);p.add_argument('--natural-FDFE-state',required=True,type=Path);p.add_argument('--native-replay',required=True,type=Path);p.add_argument('--report',type=Path)
 a=p.parse_args();report=audit(a.rom.resolve(),a.mesen.resolve(),a.natural_FDFE_state.resolve(),a.native_replay.resolve())
 if a.report:a.report.write_text(json.dumps(report,indent=2)+'\n')
 print('PASS 0521 original Mesen',report['comparisons'],'windows',report['total_exact_ram_bytes'],'RAM comparisons')
