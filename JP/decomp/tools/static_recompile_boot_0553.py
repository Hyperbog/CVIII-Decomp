#!/usr/bin/env python3
"""Native static recompilation from a *scripted hardware* original 6502 boot execution.

Unlike an assembly round-trip, the emitted C++ contains real compile-time
6502 semantic calls for each trace-executed physical instruction site. The
source ROM remains private: emit only opcodes/mnemonics/operands and metadata.
This proves only reset -> ONE injected NMI under the exact replay_reset_0548
PPU and controller assumptions; it is not an independently timed gameplay run.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from collections import Counter
from replay_reset_0548 import Bus, CPU, SHA
from audit_nmi_fixed_scheduler_banked import OPS

def physical(pc:int,bank:int)->int:
    if 0x8000<=pc<0xc000:
        if not 0<=bank<=15:raise ValueError('unmapped VRC6 physical bank')
        return 16384*bank+(pc-0x8000)
    if 0xc000<=pc<0xe000:return 30*8192+(pc-0xc000)
    if 0xe000<=pc<=0xffff:return 31*8192+(pc-0xe000)
    raise ValueError('execution in unsupported non-ROM address')

def executed(rom:bytes):
    if len(rom)!=393232 or hashlib.sha256(rom).hexdigest()!=SHA:raise ValueError('not the exact JP ROM')
    bus=Bus(rom); cpu=CPU(bus)
    sites={}; records=[]; injected=False; returned=False; crossbank=Counter()
    for step in range(100000):
        if cpu.pc==0xe04b and not injected:
            cpu.interrupt();injected=True
        if cpu.pc==0xe04b and injected and cpu.last_opcode==0x40:
            returned=True;break
        pc=cpu.pc;bank=bus.bank;phys=physical(pc,bank)
        opcode=bus.read(pc)
        if opcode not in OPS:raise ValueError(f'unsupported opcode at ${pc:04X}')
        mnemonic,mode,size=OPS[opcode]
        if pc+size>65536:raise ValueError('wrapped instruction')
        args=bytes(bus.read((pc+j)&65535) for j in range(1,size))
        arg=int.from_bytes(args,'little')
        if mode=='rel':arg=(pc+2+(arg if arg<128 else arg-256))&65535
        current=(phys,pc,opcode,mnemonic,mode,arg,pc+size)
        if phys in sites and sites[phys]!=current:raise ValueError(f'inconsistent bank alias {phys:05X}')
        sites[phys]=current
        crossbank[phys//8192]+=1
        if step==0 or step%64==0 or step>11695:
            records.append({'step':step,'pc':pc,'bank':bank,'a':cpu.a,'x':cpu.x,'y':cpu.y,'s':cpu.sp,'p':cpu.p,
                            'ram_sha256':hashlib.sha256(bus.mem[:2048]).hexdigest(),
                            'mapper_writes':len(bus.mappers),'status_polls':bus.status_polls,
                            'nmi':int(injected)})
        cpu.step()
    if not injected or not returned:raise ValueError('scripted original reset-NMI did not return')
    # Physical code must not overlap any another observed instruction's operand.
    occupied={}
    for phys,pc,opcode,mn,mode,arg,nxt in sites.values():
        for j in range(nxt-pc):
            key=phys+j
            if key in occupied and occupied[key]!=phys:raise ValueError('intersecting instruction boundaries')
            occupied[key]=phys
    summary={'schema':'JP0553-original-scripted-boot-static-native/v1','authenticated_rom_sha256':SHA,
             'trace_executed_physical_instruction_sites':len(sites),
             'physical_instruction_bytes':len(occupied),
             'original_cpu_instructions':cpu.count,'unique_physical_8k_banks':sorted(crossbank),
             'dynamic_per_8k_bank':dict(sorted((str(k),v) for k,v in crossbank.items())),
             'first_nmi_return_pc':cpu.pc,'final_mapper_bank':bus.bank,'final_ram_sha256':hashlib.sha256(bus.mem[:2048]).hexdigest(),
             'ppu_status_scripted':True,'nmi_injected_at_e04b':True,
             'gameplay_frame_parity':False,'candidate_bytes_promoted_to_strict':0}
    return sites,summary,records,bus,cpu

def source(sites)->str:
    out=['// GENERATED from original Japanese 6502 *scripted* reset+NMI execution.',
         '// Executable native code, not a copied binary ROM. Fails closed for unobserved sites.',
         '#include "static_6502.hpp"','namespace jpstatic {',
         'StepResult compiled_boot_step(Cpu& cpu) {',' unsigned offset;',
         ' if(cpu.pc>=0xE000)offset=31u*8192u+unsigned(cpu.pc-0xE000);',
         ' else if(cpu.pc>=0xC000)offset=30u*8192u+unsigned(cpu.pc-0xC000);',
         ' else if(cpu.pc>=0x8000 && cpu.pc<0xC000 && cpu.bus.bank<=15)',
         '   offset=unsigned(cpu.bus.bank)*16384u+unsigned(cpu.pc-0x8000);',
         ' else return StepResult::unresolved;',
         ' switch(offset) {']
    for phys,pc,opcode,mn,mode,arg,nxt in sorted(sites.values()):
        out.extend([f'  case 0x{phys:05X}: // CPU ${pc:04X}, actual opcode ${opcode:02X}',
                    f'   cpu.exec<Op::{mn},Mode::{mode}>(0x{arg:04X},0x{nxt:04X});return StepResult::executed;'])
    out.extend([' default:return StepResult::unresolved;',' }','}','}'])
    return '\n'.join(out)+'\n'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--rom',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();sites,report,records,_,_=executed(a.rom.read_bytes());a.out.mkdir(parents=True,exist_ok=True)
    (a.out/'boot_compiled.cpp').write_text(source(sites))
    (a.out/'boot_native_manifest.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report,sort_keys=True))
if __name__=='__main__':main()
