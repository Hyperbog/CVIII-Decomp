#!/usr/bin/env python3
"""0569: generate a copyright-free mapper24 integration-test iNES cartridge.

The synthetic cartridge exercises VRC6 16K/8K PRG bank registers, WRAM
enable, OAM DMA, PPU NMI and VRC IRQ while its fixed-bank ROM spins.
It contains NO data copied from Konami's game.
"""
from __future__ import annotations
import argparse,hashlib,sys,tempfile
from pathlib import Path

PRG=262144
CHR=131072
SIZE=16+PRG+CHR
FIXED=31*8192

def create()->bytes:
    header=bytearray(16)
    header[:4]=b'NES\x1a';header[4]=16;header[5]=16
    header[6]=0x80;header[7]=0x10  # NES mapper 24 / VRC6a.
    prg=bytearray([0x02])*PRG  # JAM in unused address space, not game code.
    code=bytes((
        0x78,                         # SEI
        0xd8,                         # CLD
        0xa2,0xff,                    # LDX #$FF
        0x9a,                         # TXS
        0xa9,0x03,0x8d,0x00,0x80,    # PRG 16K bank 3
        0xa9,0x05,0x8d,0x00,0xc0,    # PRG 8K bank 5
        0xa9,0x80,0x8d,0x03,0xb0,    # $B003 WRAM enable
        0xa9,0x02,0x8d,0x14,0x40,    # OAMDMA from CPU RAM $0200
        0xa9,0x80,0x8d,0x00,0x20,    # PPUCTRL NMI enable
        0xa9,0x08,0x8d,0x01,0x20,    # PPUMASK background enable
        0xa9,0xfe,0x8d,0x00,0xf0,    # VRC6 IRQ latch $FE
        0xa9,0x03,0x8d,0x01,0xf0,    # VRC6 scanline IRQ + re-enable on ack
        0x58,                         # CLI
    ))
    start=0xe000
    spin=start+len(code)
    code+=bytes((0x4c,spin&255,spin>>8))
    # IRQ/NMI handlers may not overwrite the main-loop JMP.
    if len(code)>=0x80:
        raise ValueError("synthetic main-code/IRQ overlap")
    prg[FIXED:FIXED+len(code)]=code
    # $E030 IRQ handler: acknowledge IRQ and return.
    prg[FIXED+0x80:FIXED+0x86]=bytes((0xa9,0x00,0x8d,0x02,0xf0,0x40))
    # $E040 NMI handler: RTI, without fake flag/cycle state.
    prg[FIXED+0x90]=0x40
    prg[FIXED+0x1ffa:FIXED+0x2000]=bytes((0x90,0xe0,0x00,0xe0,0x80,0xe0))
    return bytes(header)+bytes(prg)+bytes(CHR)

def verify(data:bytes)->dict:
    if len(data)!=SIZE or data[:4]!=b'NES\x1a' or data[4:8]!=bytes((16,16,0x80,0x10)):
        raise ValueError("synthetic mapper24 image/size drift")
    fixed=data[16+FIXED:16+FIXED+8192]
    if fixed[0:3]!=bytes((0x78,0xd8,0xa2)):
        raise ValueError("CPU entry at $E000 changed")
    spin_offset=fixed[:0x80].find(bytes((0x4c,)))
    if spin_offset<0 or spin_offset+3>=0x80:
        raise ValueError("missing non-overlapping main-loop JMP")
    spin_pc=0xe000+spin_offset
    if fixed[spin_offset:spin_offset+3]!=bytes((0x4c,spin_pc&255,spin_pc>>8)):
        raise ValueError("the main-loop JMP operand is corrupted")
    if fixed[0x90]!=0x40:
        raise ValueError("NMI handler RTI lost")
    if fixed[0x1ffa:0x2000]!=bytes((0x90,0xe0,0x00,0xe0,0x80,0xe0)):
        raise ValueError("NMI/reset/IRQ vectors changed")
    if fixed[0x80:0x86]!=bytes((0xa9,0x00,0x8d,0x02,0xf0,0x40)):
        raise ValueError("IRQ test code changed")
    if hashlib.sha256(data).hexdigest()=="958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28":
        raise ValueError("synthetic test image must never equal the original game")
    return {"size":len(data),"mapper":24,"reset_pc":"E000",
            "irq_pc":"E080","nmi_pc":"E090","sha256":hashlib.sha256(data).hexdigest(),
            "contains_original_game_code":False,"pixel_parity_verified":False}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path)
    p.add_argument("--smoke",action="store_true")
    args=p.parse_args()
    data=create()
    metadata=verify(data)
    if args.smoke:
        damaged=bytearray(data);damaged[16+FIXED+0x1ffe]=0
        broken=bytearray(data)
        spinner=broken.index(bytes((0x4c,)),16+FIXED,16+FIXED+0x80)
        broken[spinner+2]=0xa9
        try:verify(broken)
        except ValueError:pass
        else:raise AssertionError("overwritten main-loop JMP high byte accepted")
        try:verify(damaged)
        except ValueError:pass
        else:raise AssertionError("wrong reset vector accepted")
        print("PASS synthetic VRC6 mapper24 PRG/CHR, reset/NMI/IRQ, no commercial ROM")
    elif args.out is not None:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_bytes(data)
        print("WROTE_SYNTHETIC_MAPPER24 "+str(args.out)+" "+metadata["sha256"])
    else:p.error("choose --smoke or --out")
if __name__=="__main__":
    try:main()
    except (OSError,ValueError) as ex:
        print(str(ex),file=sys.stderr);raise SystemExit(2)
