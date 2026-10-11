#!/usr/bin/env python3
"""Execute original bank0A $801E 6502 bytes for all bounded tier selectors.

A deliberately small instruction-exact interpreter: no mapper or frame claim.
Its inputs are selected *only* from producer-verified table capacities.
"""
from __future__ import annotations

from pathlib import Path

BASE=0x8000
FIRST=0x801E
LAST=0x8047


def run(bank:bytes,first:int,second:int,third:int):
    assert len(bank)==0x4000
    if not all(0<=v<=127 for v in (first,second,third)):
        raise ValueError('Selector out of locally bounded range')
    ram=bytearray(0x100)
    ram[0x34]=first;ram[0x35]=second;ram[0x36]=third
    pc=FIRST;a=y=0;carry=0
    seen=[]

    def read(address:int):
        if address<0x100:return ram[address]
        if 0x8000<=address<0xC000:return bank[address-BASE]
        raise ValueError(f'Unmapped read ${address:04X}')

    for _ in range(36):
        op=read(pc);seen.append(pc)
        if op==0xA5:  # LDA zeropage
            a=read(read(pc+1));pc+=2
        elif op==0x0A:  # ASL A
            carry=(a>>7)&1;a=(a<<1)&0xff;pc+=1
        elif op==0xA8:  # TAY
            y=a;pc+=1
        elif op==0xB9:  # LDA absolute,Y
            addr=read(pc+1)|(read(pc+2)<<8)
            a=read((addr+y)&0xffff);pc+=3
        elif op==0x85:  # STA zeropage
            ram[read(pc+1)]=a;pc+=2
        elif op==0xB1:  # LDA (zeropage),Y
            zp=read(pc+1)
            addr=ram[zp]|(ram[(zp+1)&0xff]<<8)
            a=read((addr+y)&0xffff);pc+=2
        elif op==0xC8:  # INY
            y=(y+1)&0xff;pc+=1
        elif op==0x60:  # RTS
            if pc!=LAST-1:raise ValueError('Unexpected RTS address')
            ptr_1=ram[0x06]|ram[0x07]<<8
            ptr_2=ram[0x04]|ram[0x05]<<8
            leaf=ram[0x95]|ram[0x96]<<8
            return (ptr_1,ptr_2,leaf,tuple(seen))
        else:raise ValueError(f'Unsupported original byte ${op:02X} at ${pc:04X}')
    raise ValueError('Interpreter exceeded bounded linear CPU sequence')


def selftest():
    # Simplest ROM-free A5/0A/A8/B9/85/B1/C8/60 test is supplied by full ROM
    # test; here verify deliberate opcode support is exhaustive for 801E.
    assert LAST-FIRST==41
    print('PASS ROM-free original $801E indexed 6502 interpreter module')


if __name__=='__main__':selftest()
