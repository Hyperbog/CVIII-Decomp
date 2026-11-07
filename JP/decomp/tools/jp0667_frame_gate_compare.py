#!/usr/bin/env python3
"""Owner ROM 6502 opcode oracle for bounded raw0C $8A7C frame decision.

Frame cadence and absolute original CPU cycles remain OUTSIDE this proof.
"""
from __future__ import annotations
import argparse
import ctypes
import json
from pathlib import Path
from jp0667_original_effect_compare import EffectCPU
from jp0666_original_cpu_compare import Input
from hashlib import sha256
ROM_SHA="958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"

class FrameIn(ctypes.Structure):
    _fields_=[(x,ctypes.c_uint8) for x in ('slot','sound_id','flags_011b','global_01bf','countdown_0100')]
class FrameOut(ctypes.Structure):
    _fields_=[('decision',ctypes.c_int),('countdown_after',ctypes.c_uint8),('parser_mode_main',ctypes.c_uint8)]

def compare(path:Path,lib:Path)->dict:
    rom=path.read_bytes()
    if len(rom)!=393232 or sha256(rom).hexdigest()!=ROM_SHA:
        raise ValueError('wrong original Japanese ROM')
    bank=rom[16+12*16384:16+13*16384]
    # Source witness for the EXACT branch from $8A7C through $8AA0.
    witness=sha256(bank[0x8a7c-0x8000:0x8aa1-0x8000]).hexdigest()
    fn=ctypes.CDLL(str(lib.resolve())).cviii_jp_frame_gate_0667
    fn.argtypes=(ctypes.POINTER(FrameIn),ctypes.POINTER(FrameOut))
    fn.restype=ctypes.c_bool
    counts=[0,0,0]
    for slot in range(9):
     for sid in (1,5,6,0x4f,0x51,0x7d):
      for flags in (0,1,2,0x80,0xff):
       for global_gate in (0,1,0xff):
        for count in (0,1,2,255):
         inp=FrameIn(slot,sid,flags,global_gate,count)
         result=FrameOut(-1,0xa5,0xa5)
         if not fn(ctypes.byref(inp),ctypes.byref(result)):
             raise AssertionError('valid input refused')
         cpu=EffectCPU(bank,Input(0,0,0,0,0,0,0,0,0,0))
         cpu.x=slot;cpu.pc=0x8a7c;cpu.mem[0x0109+slot]=sid
         cpu.mem[0x011b+slot]=flags;cpu.mem[0x01bf]=global_gate
         cpu.mem[0x0100+slot]=count
         cpu.run(stop={0x8a8b,0x8aac,0x8dcd})
         expected={0x8a8b:0,0x8aac:1,0x8dcd:2}[cpu.pc]
         if (result.decision!=expected or
             result.countdown_after!=cpu.mem[0x0100+slot] or
             result.parser_mode_main!=(flags&1)):
             raise AssertionError(f'frame gate mismatch slot={slot},sound={sid:02X},flags={flags:02X},global={global_gate},count={count}, oracle={cpu.pc:04X}/{cpu.mem[0x0100+slot]}, c={result.decision}/{result.countdown_after}')
         counts[expected]+=1
    return {'authentic_source_span':'raw0C:$8A7C-$8AA0',
            'original_source_span_sha256':witness,
            'bounded_original_6502_vs_C11_cases':sum(counts),
            'suspended_counting_due_counts':counts,
            'real_gameplay_liveness':False,'absolute_cpu_cycles_verified':False,
            'frame_entry_cadence_verified':False}

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--rom',type=Path,required=True);p.add_argument('--lib',type=Path,required=True)
 p.add_argument('--json',type=Path);a=p.parse_args()
 out=compare(a.rom,a.lib)
 if a.json:a.json.write_text(json.dumps(out,indent=2)+'\n')
 print('PASS JP0667 authentic frame gate',out['bounded_original_6502_vs_C11_cases'],'cases; full frame/cycle timing NOT VERIFIED')
if __name__=='__main__':main()
