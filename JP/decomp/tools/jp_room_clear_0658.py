#!/usr/bin/env python3
"""JP0658 private original 6502 B570→EB82→B58B vs native C11 source parity.

Uses the existing original-opcode CPU from audit_0508_phase9.py, not a
second speculative PPU parser as the reference. ROM/VRAM bytes stay private.
These are conditional 6502 executions, NOT independent Mesen gameplay.
"""
from __future__ import annotations
import argparse, ctypes, hashlib, json
from pathlib import Path

ROM_SHA = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
RAW_SHA = "1460df577d44e114c64fdf34a8837629765f3f6a93d45796fdf81e5ffacb5ed8"
SPAN_SHA = (
 ("raw",0xB570,0xB58C,"93e1bf0880ea31d9c31e161e7d9e965dbbef0b290e48a14da232e5ed8c731708"),
 ("fixed",0xE2C4,0xE2CA,"4a9672995666573a7e4d5a3a02bc4df52437b91e2fdf79a2551d55586236dd4a"),
 ("fixed",0xE616,0xE625,"a1d890373fd26cc5f723317baf8eb678e6f4a21506db5376502de55de30e2131"),
 ("fixed",0xE7B6,0xE7FB,"a0553ee342963dc596ed48638067d5558d87a32b02649b429b18b6ebba5a1966"),
 ("fixed",0xEB82,0xEBF7,"e69aaaa7f343f00621a23d78aab2b018057a6ba29ac50d07aa1c34bc8ed287e8"),
 ("fixed",0xEC1D,0xEC47,"7500a17666fbd773b53c9d784e06ab1b1b12ffaa817c2d1ccae99a6c7a53054f"),
 ("fixed",0xE16C,0xE182,"a0d8fb637f811579a693e598ae89a9db5c81054459ea254e32cb62760aa8aa04"),
 ("fixed",0xE827,0xE831,"fe9dab3a7ce1bb29399af19923cf2e12165f9d17a0ed4bd6bebce71da6410060"),
 ("fixed",0xED89,0xED8F,"411ae3d34e7db4cc16edabd13701b0be0b67839c03cff09dc448693fb9aec613")
)
def check(ok,reason):
    if not ok: raise ValueError(reason)
def sha(data): return hashlib.sha256(data).hexdigest()
def verify(rom):
    check(len(rom)==393232 and sha(rom)==ROM_SHA and rom[:4]==b"NES\x1a",
          "original Japanese Mapper24 cartridge does not match")
    prg=rom[16:16+262144]
    raw=prg[10*16384:11*16384]
    fixed=prg[31*8192:32*8192]
    check(sha(raw)==RAW_SHA,"raw0A bank changed")
    for kind,start,end,digest in SPAN_SHA:
        b,base=(raw,0x8000) if kind=="raw" else (fixed,0xE000)
        check(sha(b[start-base:end-base])==digest,
              f"source ROM span changed at {start:04X}-{end-1:04X}")
    check(fixed[0xBF7:0xBF9]==bytes((0x1d,0xec)),"fixed PPU stream root changed")
    return prg,raw,fixed

class Plan(ctypes.Structure):
    _fields_=[("address",ctypes.c_uint16*2048),("value",ctypes.c_uint8*2048),
    ("count",ctypes.c_uint16),("final_vram_address",ctypes.c_uint16),
    ("final_source_pointer",ctypes.c_uint16),("ctrl_setup",ctypes.c_uint8),
    ("ctrl_final",ctypes.c_uint8),("mask_setup",ctypes.c_uint8),
    ("initial_ppu_address_high",ctypes.c_uint8),("initial_ppu_address_low",ctypes.c_uint8),
    ("second_ppu_address_high",ctypes.c_uint8),("second_ppu_address_low",ctypes.c_uint8),
    ("address_switch_count",ctypes.c_uint8),("original_ppu_status_reads",ctypes.c_uint8),
    ("consumed_stream_bytes",ctypes.c_uint8),("scratch02_final_count",ctypes.c_uint8)]
class State(ctypes.Structure):
    _fields_=[("ram_after",ctypes.c_uint8*2048),("ppu",Plan),
    ("cpu_ram_bank_after",ctypes.c_uint8),("state_after",ctypes.c_uint8),
    ("mapper_reg_address",ctypes.c_uint16),("sound_reg_address",ctypes.c_uint16),
    ("mapper_reg_value",ctypes.c_uint8),("sound_reg_value",ctypes.c_uint8),
    ("distinct_cleared_bytes",ctypes.c_uint16)]

def replay(prg,raw,fixed,native,seeds):
    from audit_0508_phase9 import CPU as OriginalCPU
    dll=ctypes.CDLL(str(native.resolve()))
    fn=dll.cviii_room_state0_0658
    fn.argtypes=[ctypes.POINTER(ctypes.c_uint8),ctypes.c_size_t,
       ctypes.POINTER(ctypes.c_uint8),ctypes.c_size_t,
       ctypes.POINTER(ctypes.c_uint8),ctypes.c_size_t,ctypes.POINTER(State)]
    fn.restype=ctypes.c_int
    raw_image=(ctypes.c_uint8*16384).from_buffer_copy(raw)
    fixed_image=(ctypes.c_uint8*8192).from_buffer_copy(fixed)
    cases=0
    for seed in range(seeds):
        for ctrl in (0x00,0x04):
            reference=OriginalCPU(prg,(seed*37+17)&255,seed,ctrl)
            before=bytes(reference.ram)
            reference.run()
            check(reference.pc==0x9000 and reference.sp==0xfd and
                  reference.reached_b589 and reference.steps==10532,
                  "original CPU source/stack/step boundary changed")
            out=State()
            ram=(ctypes.c_uint8*2048).from_buffer_copy(before)
            check(fn(raw_image,16384,fixed_image,8192,ram,2048,ctypes.byref(out))==1,
                  "native rejected authentic Japanese state-zero input")
            for address in (*range(0,256),*range(512,2048)):
                check(out.ram_after[address]==reference.ram[address],
                      f"original/native RAM first mismatch at {address:04X}, seed={seed}, ctrl={ctrl}")
            check(out.ppu.count==len(reference.vram_writes)==2048,
                  "expected 2048 original room PPUDATA writes")
            for index,(address,value) in enumerate(reference.vram_writes):
                check((out.ppu.address[index],out.ppu.value[index])==(address,value),
                      f"original/native first VRAM event divergence at #{index}, seed={seed}, ctrl={ctrl}")
            check(out.ppu.final_vram_address==reference.ppu_pointer and
                  out.ppu.ctrl_final==reference.ppu_control and
                  out.ppu.mask_setup==(before[0xFE]&0xE7),
                  "original/native final PPU state mismatch")
            control=[(address,value) for _,address,value in reference.ppu_events
                     if address!=0x2007]
            check(control==[(0x2000,ctrl&0x7F),(0x2006,0),(0x2006,0),
                    (0x2001,before[0xFE]&0xE7),(0x2006,0x20),(0x2006,0),
                    (0x2006,0x24),(0x2006,0),(0x2000,ctrl)],
                  "original PPU control/nametable address sequence changed")
            check([(addr,val) for _,addr,val in reference.hw] ==
                  [(0xC000,0x1E),(0xB003,0x20)],
                  "original bank/audio register write order changed")
            check((out.mapper_reg_address,out.mapper_reg_value,
                   out.sound_reg_address,out.sound_reg_value)==
                  (0xC000,0x1E,0xB003,0x20),
                  "native mapper/audio write plan divergence")
            check((out.distinct_cleared_bytes,out.state_after,
                   out.cpu_ram_bank_after)==(1297,1,10),
                  "native room-state/clear result changed")
            cases+=1
    return {"schema":"JP0658-original-6502-native-room-clear/1",
            "cases":cases,"original_cpu_instructions_per_case":10532,
            "source_cpu_instructions_replayed":cases*10532,
            "nonstack_RAM_bytes_compared":cases*1792,
            "ordered_PPUDATA_events_compared":cases*2048,
            "distinct_clear_RAM_bytes_per_case":1297,
            "mapper_and_audio_register_events_per_case":2,
            "original_gameplay_Mesen_liveness_proven":False,
            "ppu_cycle_or_rendering_frame_parity_proven":False}
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--smoke",action="store_true")
    ap.add_argument("--rom",type=Path)
    ap.add_argument("--native-lib",type=Path)
    ap.add_argument("--seeds",type=int,default=256)
    ap.add_argument("--json",type=Path)
    args=ap.parse_args()
    if args.smoke:
        assert 8*120+64==1024 and 2*1024==2048
        assert sum(b-a for a,b in ((0x4d,0xe0),(0xf0,0xf8),(0x300,0x3c0),
             (0x400,0x500),(0x500,0x600),(0x600,0x6a0),
             (0x6e0,0x700),(0x700,0x7f6)))==1297
        print("PASS JP0658 ROM-free original room RAM/PPU transfer size contracts")
    if args.rom:
        if not args.native_lib:ap.error("--native-lib needed with --rom")
        check(1<=args.seeds<=256,"seed count outside independently bounded test domain")
        report=replay(*verify(args.rom.read_bytes()),args.native_lib,args.seeds)
        if args.json:args.json.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
        print("PASS JP0658 authentic original 6502 vs native room-clear state:",report)
    elif not args.smoke:ap.error("--smoke or --rom with --native-lib required")
if __name__=="__main__":main()
