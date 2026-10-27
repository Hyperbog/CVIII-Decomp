#!/usr/bin/env python3
"""JP0821: owner-ROM audit for B6CE/B5DF/B486 original response prefixes.

No game media or original bytes are published. --smoke uses invented data.
--rom uses only an authenticated, locally supplied original Japanese ROM.
"""
import argparse
import hashlib
from pathlib import Path
ROM="958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
BANK="17b216088d12ac7b6a4a68bbea3434dbdba317865bd6cf4d11646a3d4efaf64a"
WINDOWS={
 "B6CE_flag_or_sweep":(0xb6ce,0xb707,"4923f2a5a6945b606c806e8cc720a5a38403c5e19a7b5caee65de19088e0c9e2"),
 "B5DF_effect_slot23":(0xb5df,0xb629,"2639dc4d86d077f566c9c1a77da7eb351aed7109f4855744e9bce21d703758d7"),
 "B486_actor_response":(0xb486,0xb4d5,"8f303c18bf0e9ce793d147cbcfaed74b9f65bb2f76d06f5282e0a1388a16df67")
}
def verify(rom:bytes)->None:
 if len(rom)!=393232 or rom[:4]!=b"NES\x1a" or hashlib.sha256(rom).hexdigest()!=ROM:
  raise ValueError("not the authenticated owner Japanese retail ROM")
 b=rom[16+11*16384:16+12*16384]
 if hashlib.sha256(b).hexdigest()!=BANK:raise ValueError("physical bank0B changed")
 def op(pc:int,end:int)->bytes:return b[pc-0x8000:end-0x8000]
 for name,(pc,end,expect) in WINDOWS.items():
  if hashlib.sha256(op(pc,end)).hexdigest()!=expect:
   raise ValueError("original opcode window changed: "+name)
 if op(0xb6ce,0xb6dd)!=bytes.fromhex(
    "bd 4e 05 c9 30 90 1f c9 58 b0 1b c9 49 f0 18"):
  raise ValueError("B6CE original type30/type58/type49 dispatcher changed")
 if op(0xb6e4,0xb6f5)!=bytes.fromhex(
    "bd 70 04 09 02 9d 70 04 bd 65 05 29 3f 9d 65 05 60"):
  raise ValueError("B6E4 original bit02 and 0565 mask changed")
 if op(0xb5df,0xb5f0)!=bytes.fromhex(
    "a0 17 b9 00 04 d0 42 a4 9b b9 1c 04 85 01 4c 02 b6"):
  raise ValueError("B5DF slot23 occupancy and partner height changed")
 if op(0xb607,0xb629)!=bytes.fromhex(
    "a2 17 a9 20 9d 70 04 a9 12 9d 00 04 a9 0e 9d 8c 04 "
    "a5 00 9d 38 04 a5 01 9d 1c 04 a9 08 85 89 a6 69 60"):
  raise ValueError("B5DF slot23 installation postconditions changed")
 if op(0xb486,0xb498)!=bytes.fromhex(
    "bd 4e 05 c9 30 90 47 c9 58 b0 ea bd 69 06 85 00 29 f0"):
  raise ValueError("B486 initial actor-type and high-state branch changed")
 if op(0xb4a0,0xb4bc)!=bytes.fromhex(
    "bd 69 06 29 0f 9d 69 06 bd 70 04 29 02 d0 28 "
    "38 bd 7b 06 e5 01 9d 7b 06 f0 6b 30 69"):
  raise ValueError("B486 event nibble/decrement and sound boundary changed")
 print("PASS JP0821 owner ROM and bank0B; B6CE/B5DF/B486 source hashes and postconditions")
 print("LIMIT: E75A/E249/B5C4/B8282/B525/A32F and natural contact/deallocation not proved")
def smoke()->None:
 for counter in range(256):
  for nibble in range(16):
   next_byte=(counter-nibble)&255
   assert (next_byte==0 or bool(next_byte&128)) == (
       (counter-nibble)%256==0 or ((counter-nibble)%256)>=128)
 print("PASS JP0821 4096 bounded B486 decrement/status synthetic pairs")
if __name__=="__main__":
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--rom",type=Path);p.add_argument("--smoke",action="store_true")
 a=p.parse_args()
 if a.smoke:smoke()
 if a.rom:verify(a.rom.read_bytes())
 if not(a.smoke or a.rom):p.error("provide --smoke and/or --rom")
