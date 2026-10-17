#!/usr/bin/env python3
"""Reusable *physical* VRC6 PRG/address adapter, not a stateful emulator.

NESdev VRC6 a/b hardware: mapper 24 and mapper 26 differ in A0/A1
subregister routing. Report physical PRG offsets only after explicit
caller-supplied bank state, NEVER from header/bytes alone.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

VRC6_VARIANTS={24:'VRC6a',26:'VRC6b'}

@dataclass(frozen=True)
class BankContext:
    mapper:int
    prg_size:int
    raw16_bank:int
    upper8_bank:int
    provenance:str  # required, e.g. observed mapper-write trace/event SHA
    def validate(self):
        if self.mapper not in VRC6_VARIANTS:raise ValueError('only Mapper 24/26 VRC6 family supported')
        if self.prg_size<32768 or self.prg_size%8192:
            raise ValueError('PRG must consist of >=4 physical 8 KiB banks')
        if not (0<=self.raw16_bank<=15 and (self.raw16_bank+1)*16384<=self.prg_size):
            raise ValueError('raw16 bank outside actual PRG')
        if not (0<=self.upper8_bank<self.prg_size//8192):
            raise ValueError('upper8 bank outside actual PRG')
        if not self.provenance.strip():raise ValueError('explicit bank-state provenance required')

def vrc6_canonical_write(mapper:int,cpu_address:int)->int:
    """Normalize physical register decode of A0/A1 for VRC6a/VRC6b.

    CPU $9001 -> chip register $9002 on VRC6b, but $9001 on VRC6a.
    Normalized address is NOT necessarily a valid *game* I/O write.
    """
    if mapper not in VRC6_VARIANTS:raise ValueError('not a VRC6 mapper')
    if not (0x8000<=cpu_address<=0xFFFF):raise ValueError('address is not mapped VRC6 register space')
    sub=cpu_address&3
    if mapper==26:sub=((sub&1)<<1)|((sub&2)>>1)
    return (cpu_address&0xF000)|sub

def prg_physical_location(context:BankContext,cpu_address:int)->dict[str,Any]:
    context.validate()
    if not(0x8000<=cpu_address<=0xFFFF):raise ValueError('not a switchable/fixed PRG-ROM address')
    if cpu_address<0xC000:
        file_offset=context.raw16_bank*16384+(cpu_address-0x8000)
        window='16KiB-switchable'
    elif cpu_address<0xE000:
        file_offset=context.upper8_bank*8192+(cpu_address-0xC000)
        window='8KiB-switchable'
    else:
        file_offset=context.prg_size-8192+(cpu_address-0xE000)
        window='8KiB-fixed-last'
    assert 0<=file_offset<context.prg_size
    return {'mapped_cpu_address':f'{cpu_address:04X}',
            'physical_prg_file_offset':file_offset,
            'physical_8k_bank':file_offset//8192,
            'physical_bank_offset':file_offset%8192,
            'window':window,
            'mapper':context.mapper,
            'mapper_family':VRC6_VARIANTS[context.mapper],
            'explicit_mapping_provenance':context.provenance,
            'semantic_verified':False}
