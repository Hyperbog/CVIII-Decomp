#!/usr/bin/env python3
"""JP0619: original-ROM CHR identity gates for health-bar slider + numerals.

Derived tile IDs/digests only; never exports licensed graphic bytes to Git.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
ROM_HASH='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
SIZE=393232
CHR_START=16+262144
BLOCKS=(
 ('original_numeric_0_to_9',0x1041,10,'2738bea62342332fba08fff03f7d746f7de25dd93b5aac86d1cfac65a0a12a8c'),
 ('original_latin_A_to_Z',0x1050,26,'a80bdb980cdf813ae757a6e354dde1f9b07c28828b09911afd98117f06d66e13'),
 ('health_outline_family',0x1083,3,'e4cf4857bc8e144726c4ef3d8732ea07798d7ed08820f831b06b61b46bcf576f'),
 ('health_filled_family',0x1093,3,'166f548ca0cdacfb9efd94cd6cc360cc995630c22262c073e432f990ed48fb40'),
)
def pixels(tile:bytes)->tuple[tuple[int,...],...]:
 if len(tile)!=16:raise ValueError('Exactly 16 planar tile bytes required')
 return tuple(tuple(((tile[y]>>(7-x))&1)|(((tile[y+8]>>(7-x))&1)<<1)
                    for x in range(8)) for y in range(8))
def audit(rom:bytes)->dict:
 if len(rom)!=SIZE or sha256(rom).hexdigest()!=ROM_HASH:
  raise ValueError('Original 393232-byte Japanese ROM required')
 chr_data=rom[CHR_START:]
 for name,at,count,digest in BLOCKS:
  if sha256(chr_data[at*16:(at+count)*16]).hexdigest()!=digest:
   raise ValueError('Original CHR tile family changed: '+name)
 assert pixels(chr_data[0x1093*16:0x1094*16])[1]==(2,2,2,0,2,2,2,0)
 assert pixels(chr_data[0x1085*16:0x1086*16])[1]==(3,3,3,0,3,3,3,0)
 assert pixels(chr_data[0x1041*16:0x1042*16])[0]==(0,0,0,3,3,3,0,0)
 return {'schema':'CVIII-JP-authentic-health-bar-font/v1','rom_sha256':ROM_HASH,
         'glyph_digits':list(range(0x1041,0x104B)),
         'glyph_letters':list(range(0x1050,0x106A)),
         'health_bar_filled_tile':'1093','health_bar_empty_tile':'1085',
         'pixel_layout_exact_source_rom':True,
         'palette_rgb_authenticity_verified':False,
         'menu_navigation_or_pause_implemented':False,
         'strict_PRG_bytes_credited':0}
def smoke()->None:
 src=bytes.fromhex('00eeeeeeeeeeee000000000000000000')
 assert pixels(src)[1]==(1,1,1,0,1,1,1,0)
 broken=bytearray(src);broken[8]=0xff
 assert pixels(broken)[0]!=(0,)*8
 for wrong in (b'',b'\x00'*SIZE,b'NES\x1a'+b'\x00'*(SIZE-4)):
  try:audit(wrong)
  except ValueError:continue
  raise AssertionError('Unauthenticated ROM accepted')
 print('PASS JP0619 2bpp geometry, original-ROM identity fail-closed fixtures')
def main()->None:
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--smoke',action='store_true')
 p.add_argument('--rom',type=Path)
 p.add_argument('--json',type=Path)
 a=p.parse_args()
 if a.smoke:smoke();return
 if a.rom is None:p.error('Authentic original Japanese --rom required')
 report=audit(a.rom.read_bytes())
 if a.json:a.json.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
 print(json.dumps(report,indent=2,sort_keys=True))
if __name__=='__main__':main()
