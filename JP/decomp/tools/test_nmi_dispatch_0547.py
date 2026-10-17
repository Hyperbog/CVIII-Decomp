#!/usr/bin/env python3
"""ROM-free fixed NMI dispatch smoke and optional original-ROM integrated parity.

This does NOT claim boot/frame reachability; executes the $E35C callsite under
an injected $18 selector and preserves correct original 6502 instructions.
"""
from __future__ import annotations
import argparse
from pathlib import Path
from replay_nmi_dispatch_0547 import NmiPostCPU, compare, ENTRY, TARGET, TABLE_BASE
from replay_room_loader_0540 import EvidenceError
from replay_postdispatch_0543 import check_rom


def smoke_prg():
    p=bytearray(262144)
    def put(addr, values):
        offset=31*8192+addr-0xE000
        p[offset:offset+len(values)]=values
    put(0xE0BF,bytes.fromhex('20 5C E3'))
    put(0xFFFA,bytes.fromhex('57 E0'))
    put(0xE35C,bytes.fromhex('E6 1B A5 18 20 FB E7'))
    put(0xE7FB,bytes.fromhex('0A 84 03 A8 C8 68 85 00 68 85 01 B1 00 85 02 C8 B1 00 A4 03 85 03 6C 02 00'))
    targets=[0xE383+i*7 for i in range(16)]
    targets[13]=TARGET
    for idx,t in enumerate(targets):put(TABLE_BASE+2*idx,t.to_bytes(2,'little'))
    return bytes(p),targets


def smoke():
    p,targets=smoke_prg()
    for stage,target in enumerate(targets):
        c=NmiPostCPU(p,0,stage)
        c.ram[0x18]=stage
        c.ram[0x1B]=255
        c.dispatch_prefix(expected=target)
        assert c.pc==target and c.nmi_table_target==target
        assert c.sp==0xFB and c.ram[0x1B]==0
        assert c.nmi_prefix_visits[0]==ENTRY and c.nmi_prefix_visits[-1]==0xE811
        assert len(c.nmi_prefix_visits)==18
    # Fail closed when the vector, callsite, instruction opcode or selected
    # original target is modified. These are independent failure modes.
    for at,value in ((0xFFFA,0),(0xE0BF,0),(0xE7FB,0),(TABLE_BASE+13*2,0)):
        q=bytearray(p);q[31*8192+at-0xE000]=value
        try:NmiPostCPU(bytes(q),0,1).dispatch_prefix()
        except EvidenceError:pass
        else:raise AssertionError(f'corrupt fixed-ROM input at ${at:04X} accepted')
    print('PASS 16 state selections through authentic NMI inline-dispatch instructions')
    print('PASS 4 ROM-free negative NMI-vector/callsite/opcode/table tests')


def original(rom:Path,out:Path,compiler:str):
    prg=check_rom(rom)
    expected=(0xE383,0xE436,0xE437,0xE449,0xF390,0xE459,0xE49B,0xE539,
              0xE50E,0xE516,0xE541,0xE549,0xE51E,0xE526,0xE52E,0xE531)
    for idx,target in enumerate(expected):
        c=NmiPostCPU(prg,0,idx)
        c.ram[0x18]=idx
        c.dispatch_prefix(expected=target)
        assert c.nmi_table_target==target
    return compare(rom,out,compiler)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--smoke',action='store_true')
    parser.add_argument('--rom',type=Path);parser.add_argument('--out',type=Path)
    parser.add_argument('--cxx',default='g++');args=parser.parse_args()
    smoke()
    if args.rom:
        if not args.out:parser.error('--out needed with --rom')
        original(args.rom,args.out,args.cxx)
