#!/usr/bin/env python3
"""StarFox-style local regeneration of original-JP game C11 code.
No copyrighted ROM or locally generated .c file is committed.
"""
from __future__ import annotations
import argparse,hashlib,subprocess,sys
from pathlib import Path
from build_fullbank_0a_source import build
from static_recompile_c_0562 import generate as generate_bank,source_cases,JP_SHA,BANK_SHA
from static_recompile_fixed_0553 import make
from static_recompile_boot_c_0564 import extract,generate as generate_fixed

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--rom',type=Path,required=True)
 p.add_argument('--out',type=Path,required=True,
                help='local ignored build directory, NOT a tracked source tree')
 a=p.parse_args()
 data=a.rom.read_bytes()
 if len(data)!=393232 or hashlib.sha256(data).hexdigest()!=JP_SHA:
  raise ValueError('Japanese ROM must match exact authenticated retail SHA')
 bank=data[16+10*16384:16+11*16384]
 if hashlib.sha256(bank).hexdigest()!=BANK_SHA:raise ValueError('VRC6 raw0A identity')
 out=a.out.resolve()
 repo=Path(__file__).resolve().parents[2]
 if out==repo or out==repo/'JP':
  raise ValueError('output must be a dedicated build directory')
 out.mkdir(parents=True,exist_ok=True)
 src=out/'original_source'
 build(data,src)
 asm=(src/'banked/prg_raw0a.asm').read_text()
 from build_whole_cart_recomp_0529 import assemble
 if assemble(asm,0x8000,0x4000)!=bank:raise ValueError('raw0A source drift')
 rows,count=source_cases(asm,bank)
 if len(rows)!=2357:raise ValueError('raw0A static site count drift')
 cpp,meta=make(data,(src/'banked/prg_fixed31.asm').read_text())
 fixed=extract(cpp)
 if len(fixed)!=1904:raise ValueError('fixed31/boot site count drift')
 gen=out/'gen';gen.mkdir(parents=True,exist_ok=True)
 (gen/'bank0a_compiled.c').write_text(generate_bank(rows))
 (gen/'boot_compiled.c').write_text(generate_fixed(fixed))
 import json
 summary=dict(schema='JP-0564-C11-local-generated-all-existing-sites/v1',
              original_rom_sha256=JP_SHA,raw0a_sites=len(rows),
              fixed_and_scripted_sites=len(fixed),
              total_existing_sites=len(rows)+len(fixed),
              candidate_code_certified=False,native_frame_parity=False,
              new_strict_prg_bytes=0,new_vpp_points=0)
 (gen/'manifest.json').write_text(json.dumps(summary,sort_keys=True,indent=2)+'\n')
 print(json.dumps(summary,sort_keys=True))
if __name__=='__main__':main()
