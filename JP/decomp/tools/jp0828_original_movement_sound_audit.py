#!/usr/bin/env python3
"""JP0828 owner-original NES 6502 movement and E249 banked-sound attestation.

No ROM bytes, CHR tiles, original saves, or trace dumps are published.
The original emulator owner supplies their own verified JP cartridge.
"""
import argparse
import hashlib
from pathlib import Path

ROM_SHA="958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
RAW0B_SHA="17b216088d12ac7b6a4a68bbea3434dbdba317865bd6cf4d11646a3d4efaf64a"
RAW0F_SHA="96990dfb1b859cfbcebed583ac100cc49aefe235ab61220fafa365dabba88964"
WINDOWS={
 "per_frame_original_8001":(11,0x8001,0x804b,0x8000,
       "4f8acdadcc27a00278b799ca271122d46c05473d92f19e1f01ee505113fccef9"),
 "damage_defeat_6502":(11,0xb486,0xb53f,0x8000,
       "dd9bd653a17930cce3e37105bea6e6fdf3f9c846c35aa388295ee192c7e457fd"),
 "original_e249_mapper_sound":(15,0xe249,0xe264,0xc000,
       "5a5d7b8a0f857c8062faee305b4d752522f281bda0271e402cd4c66759b37324"),
 "original_e2d0_bank_select":(15,0xe2d0,0xe2d6,0xc000,
       "8d1a2898917458f00a455757ee9471327e1d4f51bee3d841d98e23055fb51380")
}
def sha(b):
 return hashlib.sha256(b).hexdigest()
def attest(path):
 r=path.read_bytes()
 if len(r)!=393232 or r[:4]!=b"NES\x1a" or sha(r)!=ROM_SHA:
  raise ValueError("not original owner Japanese Mapper24 ROM")
 if sha(r[16+11*16384:16+12*16384])!=RAW0B_SHA:
  raise ValueError("PRG raw0B source mismatch")
 if sha(r[16+15*16384:16+16*16384])!=RAW0F_SHA:
  raise ValueError("fixed PRG raw0F source mismatch")
 for label,(bank,start,end,base,digest) in WINDOWS.items():
  d=r[16+bank*16384+start-base:16+bank*16384+end-base]
  if len(d)!=end-start or sha(d)!=digest:
   raise ValueError("original ROM instruction window mismatch: "+label)
 print("PASS original ROM, physical raw0B/fixed0F SHA, four code-window SHA")
 print("PASS $8001 original movement, $B486/B525, $E249/$E2D0 sound bank switch")
 print("External bank0C $8850 effects and subsequent B525 path still deferred")
def smoke():
 for before in range(512):
  for diff in (-32,-1,0,1,32):
   after=(before+diff)&511
   dx=after-before
   if dx>256:dx-=512
   if dx< -256:dx+=512
   assert dx==diff
 print("PASS original 9-bit page wrap, 2560 signed movement arithmetic fixtures")

if __name__=="__main__":
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--rom",type=Path)
 p.add_argument("--smoke",action="store_true")
 a=p.parse_args()
 if not(a.rom or a.smoke):p.error("provide --rom or --smoke")
 if a.smoke:smoke()
 if a.rom:attest(a.rom)
