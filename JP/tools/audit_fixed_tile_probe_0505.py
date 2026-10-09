#!/usr/bin/env python3
"""0505 JP fixed-tile-probe audit; static candidates are not live paths."""
import hashlib,json,sys
from pathlib import Path
ROM_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
WANTED=(0xFB96,0xFBA5,0xFC17,0xFC1F,0xFCDE)
EXPECTED={0xFB96:11,0xFBA5:4,0xFC17:6,0xFC1F:43,0xFCDE:92}
SCRIPT_INIT_COUNTS={2:4,3:9,9:5,10:6,11:12,12:1}
CODE={
 'FD03':'a5 53 18 65 10 85 13 a5 54 69 00 85 14 a8',
 'FD11':'a5 13 4a 4a 4a 4a 4a 19 62 fd',
 'FD1B':'c9 0c 90 05 e9 0c 4c 1b fd a8 b9 4d fd 18 65 11 a8',
 'FC6F':'a5 53 18 65 10 85 13 a5 54 65 14 4c 0e fd',
 'FC17':'84 10 a8 a5 10 4c ee fc',
 'FD4D':'00 0c 18 24 30 3c 48 54 60 6c 78 84',
}
def main(path,out=None):
 rom=Path(path).read_bytes()
 assert len(rom)==0x60010 and hashlib.sha256(rom).hexdigest()==ROM_SHA
 prg=rom[16:16+0x40000];fixed=prg[31*0x2000:32*0x2000]
 for addr,pattern in CODE.items():
  pc=int(addr,16);data=bytes.fromhex(pattern)
  assert fixed[pc-0xE000:pc-0xE000+len(data)]==data,addr
 assert fixed[0xFD18-0xE000:0xFD1B-0xE000]==bytes.fromhex('19 62 fd')
 assert fixed[0xFD25-0xE000:0xFD28-0xE000]==bytes.fromhex('b9 4d fd')
 result={'jp_rom_sha256':ROM_SHA,'checkpoint':'0505','strict_new_rom_bytes':0,
   'native_helper':'src/fixed_tile_probe.hpp',
   'high_index_producer_paths':[
       'FD0A-FD10: Y=(RAM[$54]+carry_from_low_position)&$FF',
       'FC76-FC7A -> FD0E: Y=(RAM[$54]+RAM[$14]+carry)&$FF'],
   'unbounded_rom_lookup':'$FD62,Y; conservative 256 possible bytes FD62-FE61 until producer proof',
   'bounded_tile_table':'$FD4D-$FD58 (12 bytes, counted in 0504)',
   'static_candidate_calls':{},
   'classifications':'Raw byte-pattern JSR and immediate stores are provisional, not executable-site proof'}
 for target in WANTED:
  needle=bytes((0x20,target&255,target>>8))
  locations=[]
  for bank in range(16):
   block=prg[bank*0x4000:(bank+1)*0x4000]
   p=0
   while (i:=block.find(needle,p))!=-1:
    locations.append({'raw_bank':f'{bank:02X}','cpu':f'{0x8000+i:04X}'})
    p=i+1
  assert len(locations)==EXPECTED[target],(hex(target),len(locations))
  result['static_candidate_calls'][f'{target:04X}']=locations
 immediate=[]
 for bank in range(16):
  block=prg[bank*0x4000:(bank+1)*0x4000]
  for i in range(len(block)-4):
   if block[i]==0xA9 and block[i+2:i+5]==bytes.fromhex('9d ef 05'):
    immediate.append({'raw_bank':f'{bank:02X}',
      'lda_cpu':f'{0x8000+i:04X}',
      'candidate_script_id':f'{block[i+1]:02X}'})
 by_bank={i:sum(1 for x in immediate if int(x['raw_bank'],16)==i) for i in range(16)}
 assert {k:v for k,v in by_bank.items() if v}==SCRIPT_INIT_COUNTS
 assert len(immediate)==37
 assert {'raw_bank':'0B','lda_cpu':'B503','candidate_script_id':'1B'} in immediate
 result['raw_immediate_script_init_candidates']=immediate
 result['raw_immediate_script_init_total']=37
 if out:Path(out).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 print('JP ROM: PASS',ROM_SHA)
 print('FD62,Y: up to 256 possible high-index addresses FD62-FE61; live domain open')
 print('FD4D,Y: 12 modulo-reduced data bytes, already 0504-covered')
 print('candidate JSR counts:',{k:len(v) for k,v in result['static_candidate_calls'].items()})
 print('raw LDA #id / STA $05EF,X patterns: 37, not live')
 print('new strict PRG bytes: 0')
if __name__=='__main__':
 if len(sys.argv) not in (2,3):sys.exit('usage: audit_fixed_tile_probe_0505.py JP.nes [report.json]')
 main(Path(sys.argv[1]),Path(sys.argv[2]) if len(sys.argv)==3 else None)
