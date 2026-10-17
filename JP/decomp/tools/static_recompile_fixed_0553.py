#!/usr/bin/env python3
"""Combine *every* previously verified fixed PRG31 instruction with traced boot.

Source-led instructions are only given the evidence grade that the source
actually claims. Traced boot instructions within RAW fallback are tagged
"SCRIPTED_TRACE", never misreported as naturally executed gameplay code.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from static_recompile_boot_0553 import executed,source as boot_source
from audit_nmi_fixed_scheduler_banked import OPS
SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'

def verified_sites(rom,source):
    src=source.splitlines();bank=rom[16+31*8192:16+32*8192]
    pos=None;verified=False;out={};consumed=bytearray(8192)
    for lineno,line in enumerate(src,1):
        if line.startswith('; VERIFIED '):verified=True
        elif line.startswith('; UNCLASSIFIED '):verified=False
        instruction=line.split(';',1)[0].strip().lower()
        if not instruction or instruction.startswith('.equ '):continue
        if instruction.startswith('.org '):pos=int(instruction[5:].lstrip('$'),16);continue
        if instruction.endswith(':'):continue
        if pos is None:raise ValueError(f'missing .org at line {lineno}')
        if not 0xe000<=pos<0x10000:raise ValueError('source outside fixed physical bank31')
        if instruction.startswith('.byte '):size=len(instruction[6:].split(','))
        elif instruction.startswith('.word '):size=2*len(instruction[6:].split(','))
        else:
            op=bank[pos-0xe000]
            if op not in OPS:raise ValueError(f'bad opcode fixed31 {op:02x}@{pos:04x}')
            mnemonic,mode,size=OPS[op]
            src_mn=instruction.split()[0]
            if mnemonic.lower()!=src_mn:raise ValueError(f'asm mnemonic mismatch {pos:04x}: {src_mn} vs {mnemonic}')
            if not verified:raise ValueError(f'asm source instruction in non-verified segment {pos:04x}')
            operands=bank[pos+1-0xe000:pos+size-0xe000]
            arg=int.from_bytes(operands,'little')
            if mode=='rel':arg=(pos+2+(arg if arg<128 else arg-256))&0xffff
            phys=31*8192+(pos-0xe000)
            out[phys]=(phys,pos,op,mnemonic,mode,arg,pos+size)
        if pos+size>0x10000:raise ValueError(f'fixed bank overflow {pos:04x}')
        for j in range(size):
            k=pos+j-0xe000
            if consumed[k]:raise ValueError(f'source overlap fixed bank at {pos:04x}')
            consumed[k]=1
        pos+=size
    if not all(consumed):raise ValueError('not a complete 8K source')
    return out

def make(rom,source):
    trace,summary,records,_,_=executed(rom)
    fixed=verified_sites(rom,source)
    combined=dict(fixed)
    overlap=0
    for phys,desc in trace.items():
        if phys in combined:
            if combined[phys]!=desc:raise ValueError('trace contradicts verified source')
            overlap+=1
        else:combined[phys]=desc
    # Reject any byte used both as one instruction operand and another instruction start.
    occupied={}
    for phys,pc,op,mn,mode,arg,nxt in combined.values():
        for j in range(nxt-pc):
            old=occupied.setdefault(phys+j,phys)
            if old!=phys:raise ValueError(f'overlapping executable sites at physical {phys+j:05X}')
    names={p:('TRACE_EXECUTED' if p in trace else 'HISTORICALLY_VERIFIED') for p in combined}
    lines=['// GENERATED from original fixed bank31 ASM + scripted reset/NMI trace.',
           '// All physical instruction sites compile as native C++, no ROM bytes embedded.',
           '// Unknown offsets fail closed; scripted trace does not prove natural game liveness.',
           '#include "static_6502.hpp"','namespace jpstatic {','StepResult compiled_boot_step(Cpu& cpu) {',
           ' unsigned offset;',
           ' if(cpu.pc>=0xE000)offset=31u*8192u+unsigned(cpu.pc-0xE000);',
           ' else if(cpu.pc>=0xC000)offset=30u*8192u+unsigned(cpu.pc-0xC000);',
           ' else if(cpu.pc>=0x8000 && cpu.pc<0xC000 && cpu.bus.bank<=15)',
           '   offset=unsigned(cpu.bus.bank)*16384u+unsigned(cpu.pc-0x8000);',
           ' else return StepResult::unresolved;',
           ' switch(offset) {']
    for phys,pc,op,mn,mode,arg,nxt in sorted(combined.values()):
        lines.extend([f'  case 0x{phys:05X}: // ${pc:04X} opcode ${op:02X}, {names[phys]}',
                      f'   cpu.exec<Op::{mn},Mode::{mode}>(0x{arg:04X},0x{nxt:04X});return StepResult::executed;'])
    lines+=[' default:return StepResult::unresolved;', ' }','}', '}']
    manifest=dict(summary)
    manifest.update({'schema':'JP0553-audited-fixed31-plus-scripted-boot-native/v2',
       'compiled_physical_instruction_sites':len(combined),
       'historically_verified_fixed31_sites':len(fixed),
       'scripted_boot_sites':len(trace),
       'overlap_verified_and_boot':overlap,
       'scripted_boot_only_sites':len(trace)-overlap,
       'compiled_code_bytes':len(occupied),
       'uncompiled_code_or_data_bytes_prg31':8192-sum(nxt-pc for phys,pc,op,mn,mode,arg,nxt in fixed.values()),
       'strict_prg_new_bytes':0,
       'native_frame_parity':False,'native_gameplay_ready':False})
    return '\n'.join(lines)+'\n',manifest

def main():
    a=argparse.ArgumentParser();a.add_argument('--rom',type=Path,required=True)
    a.add_argument('--asm',type=Path,required=True);a.add_argument('--out',type=Path,required=True)
    t=a.parse_args();rom=t.rom.read_bytes()
    if len(rom)!=393232 or hashlib.sha256(rom).hexdigest()!=SHA:raise ValueError('ROM identity')
    cpp,manifest=make(rom,t.asm.read_text())
    t.out.mkdir(parents=True,exist_ok=True)
    (t.out/'boot_compiled.cpp').write_text(cpp)
    (t.out/'boot_native_manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    print(json.dumps(manifest,sort_keys=True))
if __name__=='__main__':main()
