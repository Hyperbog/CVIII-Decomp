#!/usr/bin/env python3
"""0562 StarFox-style original-ROM -> C11 bank0A recompilation backend.

Generated files live outside git (local build only), authenticating the
source and original retail image through the existing Python source_cases.
Candidates NEVER gain strict PRG or liveness credit. ROM is not distributed.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from static_recompile_bank0a import source_cases, JP_SHA, BANK_SHA
from build_whole_cart_recomp_0529 import assemble

def generate(rows):
    lines=[
      '/* Original JP raw0A instruction starts -> host C11 calls.',
      ' * GENERATED LOCALLY FROM PRIVATE ORIGINAL ROM; no ROM copied here. */',
      '#include "cpu.h"',
      'JpStep jp_bank0a_compiled_step(JpCpu *cpu) {',
      '  if(!cpu || !cpu->bus || cpu->bus->bank!=10) return JP_STEP_UNRESOLVED;',
      '  switch(cpu->pc) {'
    ]
    last=-1
    for r in rows:
        pc=r['pc']
        if pc<=last: raise ValueError('instruction starts must be sorted')
        last=pc
        if r['category'] not in ('audited','candidate'):
            raise ValueError('unknown instruction evidence class')
        lines.append(f'  case 0x{pc:04x}:')
        if r['category']=='candidate':
            lines.append('    if(!cpu->allow_candidate_static) return JP_STEP_CANDIDATE;')
        lines.append(f"    return jp_cpu_exec(cpu, 0x{r['opcode']:02x}, 0x{r['arg']:04x}, 0x{r['next']:04x});")
    return '\n'.join(lines+['  default:return JP_STEP_UNRESOLVED;','  }','}'])+'\n'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--smoke',action='store_true')
    p.add_argument('--rom',type=Path)
    p.add_argument('--source',type=Path)
    p.add_argument('--out',type=Path)
    a=p.parse_args()
    if a.smoke:
        fixture=[
          dict(pc=0x801e,category='audited',opcode=0xa5,arg=0x34,next=0x8020),
          dict(pc=0x8020,category='candidate',opcode=0x0a,arg=0,next=0x8021)
        ]
        sample=generate(fixture)
        assert sample.count('case 0x')==2
        assert sample.count('JP_STEP_CANDIDATE')==1
        assert 'jp_cpu_exec(cpu, 0xa5' in sample
        assert 'JP_STEP_UNRESOLVED' in sample
        print('PASS C11 bank0A codegen contract: roots, candidate gate, fallback')
        return
    if not all((a.rom,a.source,a.out)):p.error('--rom, --source and --out required')
    rom=a.rom.read_bytes()
    if len(rom)!=393232 or hashlib.sha256(rom).hexdigest()!=JP_SHA:
        raise ValueError('wrong original Japanese ROM fingerprint')
    bank=rom[16+10*16384:16+11*16384]
    if hashlib.sha256(bank).hexdigest()!=BANK_SHA:
        raise ValueError('physical VRC6 raw0A bank mismatch')
    src=a.source.read_text(encoding='utf-8')
    if assemble(src,0x8000,0x4000)!=bank:
        raise ValueError('source does not roundtrip to original physical bank')
    rows,counts=source_cases(src,bank)
    if len(rows)!=2357 or counts['audited_instructions']!=992:
        raise ValueError('original-source boundary census drift')
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/'bank0a_compiled.c').write_text(generate(rows),encoding='utf-8')
    manifest={
      'schema':'JP-C11-original-bank0A-generator/v1',
      'original_rom_sha256':JP_SHA,'bank_sha256':BANK_SHA,
      'source_roundtrip_exact':True,'generated_instruction_sites':len(rows),
      **counts,'candidate_code_certified':False,
      'interpreted_fallback_enabled_by_default':False,
      'native_gameplay_frame_parity':False,
      'new_strict_prg_bytes':0,'new_vpp_points':0
    }
    (a.out/'bank0a_c_manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    print(json.dumps(manifest,sort_keys=True))
if __name__=='__main__':main()
