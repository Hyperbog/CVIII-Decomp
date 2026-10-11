#!/usr/bin/env python3
"""Original Japanese JP 0524 physical source verification, not Mesen parity."""
import argparse
import hashlib
from pathlib import Path
ROM_SHA="958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
SOURCE={
 "raw0B_81B2_81CB":(0x02C1B2,bytes.fromhex(
 "BD 1D 06 AA BD 70 04 29 81 F0 06 20 6B B5 9D 4E 05"
 " A6 69 20 6B B5 9D 4E 05 60"),
 "d84f72f11fe42f867816b7503d55d8bbd0d0796f93b8ba1a8360894a1b8080d4"),
 "raw0B_B56B_B579":(0x02F56B,bytes.fromhex(
 "A9 00 9D 57 06 9D 70 04 9D C1 05 9D 00 04 60"),
 "15da8668d001967910311e8f390ba85e07b73a2236a39e338f8aff9a6645f3dc"),
 "fixed_FE6E_FE75":(0x03FE6E,bytes.fromhex(
 "E8 E0 13 B0 03 4C EC FD"),
 "409c848d417a2e8fefcf0bce493b8676699a3cbc707dd6d8bc443b60308c6b05")
}
def audit(path:Path)->None:
 rom=path.read_bytes()
 assert len(rom)==393232 and hashlib.sha256(rom).hexdigest()==ROM_SHA,"Wrong JP ROM"
 assert rom[:4]==b"NES\x1a" and rom[4:6]==bytes((16,16)),"Wrong header"
 assert ((rom[6]>>4)|(rom[7]&0xf0))==24,"Not VRC6 Mapper 24"
 prg=rom[16:16+0x40000]
 for name,(offset,source,expected_sha) in SOURCE.items():
  actual=prg[offset:offset+len(source)]
  assert actual==source and hashlib.sha256(actual).hexdigest()==expected_sha,name
  print("PASS",name,hex(offset),len(source),"bytes")
 src=SOURCE["raw0B_81B2_81CB"][1]
 assert src[9]==0xf0 and 0x81bd+src[10]==0x81c3
 assert src[11:14]==bytes.fromhex("20 6B B5")
 assert src[19:22]==bytes.fromhex("20 6B B5")
 print("PASS 0524 physical source; no original Mesen differential claimed")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("rom",type=Path)
 audit(p.parse_args().rom)
