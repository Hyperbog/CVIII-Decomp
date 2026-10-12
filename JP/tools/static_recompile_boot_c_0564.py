#!/usr/bin/env python3
"""0564 original JP fixed/scripted boot -> generated C11 physical-bank dispatch.

Uses the byte-exact fixed-bank source + historically scripted trace from
static_recompile_fixed_0553.make(). No generated game code is committed.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
from static_recompile_fixed_0553 import make,SHA

CASE=re.compile(
 r'case 0x([0-9A-Fa-f]{5}): // \$([0-9A-Fa-f]{4}) opcode \$([0-9A-Fa-f]{2}), '
 r'(TRACE_EXECUTED|HISTORICALLY_VERIFIED)\n'
 r'\s+cpu\.exec<Op::([A-Z]+),Mode::([a-z]+)>\(0x([0-9A-Fa-f]{4}),0x([0-9A-Fa-f]{4})\);'
 r'return StepResult::executed;'
)

def extract(cpp):
    rows=[]
    for phys,pc,opcode,evidence,op,mode,arg,nxt in CASE.findall(cpp):
        entry=dict(physical=int(phys,16),pc=int(pc,16),opcode=int(opcode,16),
            evidence=evidence,op=op,mode=mode,arg=int(arg,16),next=int(nxt,16))
        if entry['physical']!= (31*8192 + entry['pc']-0xe000 if entry['pc']>=0xe000
          else 30*8192+entry['pc']-0xc000 if entry['pc']>=0xc000 else
          (entry['physical']//16384)*16384+entry['pc']-0x8000):
            raise ValueError('physical mapper / PC alias contradiction')
        rows.append(entry)
    if not rows or sorted(x['physical'] for x in rows)!=[x['physical'] for x in rows]:
        raise ValueError('missing or out-of-order original physical sites')
    if len({x['physical'] for x in rows})!=len(rows):
        raise ValueError('duplicate original physical sites')
    return rows

def generate(rows):
    lines=[
       '/* Original-JP fixed31 and scripted reset/NMI instruction sites -> C11.',
       ' * Generated locally from authenticated original; no game ROM included. */',
       '#include "cpu.h"',
       'JpStep jp_fixed_compiled_step(JpCpu *c) {',
       '  if(!c || !c->bus)return JP_STEP_UNRESOLVED;',
       '  unsigned physical;',
       '  if(c->pc>=0xe000)physical=31u*8192u+c->pc-0xe000u;',
       '  else if(c->pc>=0xc000)physical=30u*8192u+c->pc-0xc000u;',
       '  else if(c->pc>=0x8000 && c->bus->bank<16)',
       '    physical=(unsigned)c->bus->bank*16384u+c->pc-0x8000u;',
       '  else return JP_STEP_UNRESOLVED;',
       '  switch(physical) {'
    ]
    for r in rows:
        if r['evidence'] not in ('TRACE_EXECUTED','HISTORICALLY_VERIFIED'):
            raise ValueError('invalid source code provenance')
        lines.extend([
            f"  case 0x{r['physical']:05x}: /* 6502 PC 0x{r['pc']:04x}, {r['evidence']} */",
            f"    return jp_cpu_exec(c,0x{r['opcode']:02x},0x{r['arg']:04x},0x{r['next']:04x});"
        ])
    return '\n'.join(lines+[
       '  default:return JP_STEP_UNRESOLVED;','  }','}',
       '']) 

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--smoke',action='store_true')
    p.add_argument('--rom',type=Path)
    p.add_argument('--asm',type=Path)
    p.add_argument('--out',type=Path)
    a=p.parse_args()
    if a.smoke:
        fake=('  case 0x3e000: // $E000 opcode $A9, HISTORICALLY_VERIFIED\n'
             '   cpu.exec<Op::LDA,Mode::imm>(0x007f,0xE002);return StepResult::executed;')
        rows=extract(fake)
        assert len(rows)==1 and rows[0]['physical']==31*8192
        generated=generate(rows)
        assert 'physical=31u*8192u' in generated and '0xa9,0x007f' in generated
        print('PASS ROM-free physical mapper qualified fixed31 C11 codegen')
        return
    if not all((a.rom,a.asm,a.out)):p.error('--rom, --asm, --out required')
    rom=a.rom.read_bytes()
    if len(rom)!=393232 or hashlib.sha256(rom).hexdigest()!=SHA:
        raise ValueError('original Japanese ROM identity mismatch')
    cpp,manifest=make(rom,a.asm.read_text())
    rows=extract(cpp)
    if len(rows)!=1904 or manifest['compiled_physical_instruction_sites']!=1904:
        raise ValueError('fixed/scripted boot codegen count changed')
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/'boot_compiled.c').write_text(generate(rows))
    evidence={
       'schema':'JP-C11-fixed-boot-generator/v1',
       'original_rom_sha256':SHA,
       'compiled_existing_physical_sites':len(rows),
       'original_historically_verified_sites':manifest['historically_verified_fixed31_sites'],
       'scripted_boot_only_sites':manifest['scripted_boot_only_sites'],
       'scripted_nmi_injected':True,
       'scripted_ppu_status':True,
       'native_gameplay_parity':False,'new_strict_prg_bytes':0,'new_vpp_points':0
    }
    (a.out/'boot_c_manifest.json').write_text(json.dumps(evidence,indent=2,sort_keys=True)+'\n')
    print(json.dumps(evidence,sort_keys=True))
if __name__=='__main__':main()
