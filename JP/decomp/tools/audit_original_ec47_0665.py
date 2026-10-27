#!/usr/bin/env python3
"""JP $EC47 authenticated message formatter, ROM-private input only.

Verify independently pinned real opcodes without checking ROM-derived data into
Git. --smoke is source-free and runs in public CI; --rom verifies the owner's
original Japanese cartridge image at instruction level.
"""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path
HASH = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"

def readcpu(data:bytes,bank:int,addr:int,n:int)->bytes:
    if bank == 15:
        assert 0xC000 <= addr and addr+n <= 0x10000
        start=16+15*16384+addr-0xC000
    else:
        assert 0 <= bank < 15 and 0x8000 <= addr and addr+n <= 0xC000
        start=16+bank*16384+addr-0x8000
    return data[start:start+n]

# Original source address, expected instruction bytes. No original ROM stored.
SITES=(
 (10,0xB8F4,"aca507"),   # LDY $07A5
 (10,0xB8F7,"b10ac9ff"), # LDA ($0A),Y; CMP #$FF
 (10,0xB8FF,"2047ec"),   # JSR $EC47
 (15,0xEC47,"48a90020cae268"), # bank-save prologue
 (15,0xEC4E,"206a96"),   # formatter in bank zero
 (15,0xEC51,"4c2de6"),   # bank restoration
 (15,0xE2CA,"48a5238524688523"),
 (15,0xE62D,"a5244cd0e2"),
 (0,0x966A,"86ae4c7596"),
 (0,0x9675,"0aa8b9b9968500b9"),
 (0,0x9689,"a9012072ec2061ec2074ec"),
 (15,0xEC72,"a61e9d0003e8"),
)

def stack_matches(ram:bytes,sp:int,token:int)->bool:
    return tuple(ram[0x100|((sp+i)&255)] for i in (2,3,4,5,6)) == (
        0x4C,0xEC,token,0x01,0xB9)

def smoke()->None:
    ram=bytearray(2048)
    for i,value in zip((2,3,4,5,6),(0x4C,0xEC,0x32,0x01,0xB9)):
        ram[0x100|((0xF7+i)&255)]=value
    assert stack_matches(ram,0xF7,0x32)
    assert not stack_matches(ram,0xF7,0x33)
    ram[0x1FC]=0
    assert not stack_matches(ram,0xF7,0x32)
    assert len({(bank,addr) for bank,addr,_ in SITES})==len(SITES)
    print("PASS JP original EC47 stack and source signature smoke")

def verify(rom:Path)->None:
    data=rom.read_bytes()
    if len(data)!=393232 or data[:4]!=b"NES\\x1a":
        raise ValueError("original Japanese iNES geometry is required")
    digest=hashlib.sha256(data).hexdigest()
    if digest!=HASH:raise ValueError("original Japanese ROM SHA-256 differs")
    for bank,addr,expected in SITES:
        if readcpu(data,bank,addr,len(expected)//2)!=bytes.fromhex(expected):
            raise ValueError(f"original CPU opcode provenance mismatch at bank {bank:02X} CPU ${addr:04X}")
    print(f"PASS {len(SITES)} private ROM original EC47 instruction windows")
    print("EC47 queues $0300 commands via bank00 formatter; PPU writes are later/uncertain")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--smoke",action="store_true")
    p.add_argument("--rom",type=Path)
    args=p.parse_args()
    smoke()
    if args.rom:verify(args.rom)
    elif not args.smoke:p.error("provide --smoke or --rom <original JP NES image>")
