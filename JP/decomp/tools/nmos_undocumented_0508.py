#!/usr/bin/env python3
"""Stable unofficial NMOS-6502 opcodes for independent CPU validation only.

Opcode support is opt-in via NromCPU; not silently promoted into the JP
Castlevania trace core, mapper, or verified gameplay code. 6502 decimal
flag is ignored by the NES 2A03 ALU in this implementation.
"""
from __future__ import annotations
from trace_6502_vrc6_0508 import C,Z,V,N

# Each opcode resolves to (operation, addressing mode, baseline CPU cycles).
M = {}
def _add(op, names, modes, cycles):
    for n,mode,t in zip(names,modes,cycles):
        opcode=int(n,16)
        assert opcode not in M
        M[opcode]=(op,mode,t)

_add('NOP', ['1A','3A','5A','7A','DA','FA'],['imp']*6,[2]*6)
_add('NOP', ['80','82','89','C2','E2'],['imm']*5,[2]*5)
_add('NOP', ['04','44','64'],['zp']*3,[3]*3)
_add('NOP', ['14','34','54','74','D4','F4'],['zpx']*6,[4]*6)
_add('NOP', ['0C'],['abs'],[4])
_add('NOP', ['1C','3C','5C','7C','DC','FC'],['abx']*6,[4]*6)
_add('SBC', ['EB'],['imm'],[2])
_add('ANC', ['0B','2B'],['imm']*2,[2]*2)
_add('ALR', ['4B'],['imm'],[2])
_add('ARR', ['6B'],['imm'],[2])
_add('AXS', ['CB'],['imm'],[2])
_add('LAX', ['A3','A7','AF','B3','B7','BF'],['inx','zp','abs','iny','zpy','aby'],[6,3,4,5,4,4])
_add('SAX', ['83','87','8F','97'],['inx','zp','abs','zpy'],[6,3,4,4])
_add('LAS', ['BB'],['aby'],[4])
# Composite undocumented read/modify/write instructions.
MODES=['inx','zp','abs','iny','zpx','aby','abx']
CYCLES=[8,5,6,8,6,7,7]
for operation, codes in {
    'SLO':['03','07','0F','13','17','1B','1F'],
    'RLA':['23','27','2F','33','37','3B','3F'],
    'SRE':['43','47','4F','53','57','5B','5F'],
    'RRA':['63','67','6F','73','77','7B','7F'],
    'DCP':['C3','C7','CF','D3','D7','DB','DF'],
    'ISC':['E3','E7','EF','F3','F7','FB','FF'],
}.items():_add(operation,codes,MODES,CYCLES)

# Unstable store/high-byte and XAA opcodes are NOT implemented without
# separate hardware tests. KIL/JAM halts remain unsupported by design.

def step(cpu, opcode: int)->bool:
    record=M.get(opcode)
    if record is None:return False
    operation,mode,cycles=record
    bus=cpu.bus
    pc=cpu.pc
    arg=bus.rb((pc+1)&0xffff) if mode not in ('imp',) else 0
    word=arg | (bus.rb((pc+2)&0xffff)<<8) if mode in ('abs','abx','aby') else 0
    size=1 if mode=='imp' else 3 if mode in ('abs','abx','aby') else 2
    crossed=False
    if mode=='zp':addr=arg
    elif mode=='zpx':addr=(arg+cpu.x)&0xff
    elif mode=='zpy':addr=(arg+cpu.y)&0xff
    elif mode=='abs':addr=word
    elif mode=='abx':
        addr=(word+cpu.x)&0xffff;crossed=(word&255)+cpu.x>255
    elif mode=='aby':
        addr=(word+cpu.y)&0xffff;crossed=(word&255)+cpu.y>255
    elif mode=='inx':addr=bus.rzw((arg+cpu.x)&255)
    elif mode=='iny':
        base=bus.rzw(arg);addr=(base+cpu.y)&0xffff
        crossed=(base&255)+cpu.y>255
    else:addr=None
    cpu.pc=(pc+size)&0xffff
    cpu.steps+=1
    cpu.last_instruction=(pc,bus.raw_bank,'*'+operation,mode,arg if size==2 else word if size==3 else None)
    val=arg if mode=='imm' else bus.rb(addr) if addr is not None else 0
    if operation=='NOP':
        if mode=='abx' and crossed:cycles+=1
    elif operation=='LAX':
        cpu.a=cpu.x=cpu.nz(val)
        if mode in ('aby','iny') and crossed:cycles+=1
    elif operation=='LAS':
        cpu.a=cpu.x=cpu.sp=cpu.nz(val&cpu.sp)
        if crossed:cycles+=1
    elif operation=='SAX':bus.wb(addr,cpu.a&cpu.x)
    elif operation in ('ANC','ALR','ARR'):
        a=cpu.a&val
        if operation=='ANC':
            cpu.a=cpu.nz(a);cpu.setflag(C, bool(cpu.a&128))
        elif operation=='ALR':
            cpu.setflag(C,bool(a&1));cpu.a=cpu.nz(a>>1)
        else:
            out=(a>>1)|(128 if cpu.flag(C) else 0)
            cpu.a=cpu.nz(out)
            cpu.setflag(C,bool(out&64))
            cpu.setflag(V,bool(((out>>6)^(out>>5))&1))
    elif operation=='AXS':
        old=cpu.a&cpu.x
        cpu.setflag(C,old>=val)
        cpu.x=cpu.nz(old-val)
    else:
        if operation in ('SLO','RLA','SRE','RRA','DCP','ISC'):
            assert addr is not None
            oldcarry=int(cpu.flag(C))
            bus.wb(addr,val)  # NMOS RMW dummy write (not cycle-interleaved)
            if operation=='SLO':
                cpu.setflag(C,bool(val&128));out=(val<<1)&255
            elif operation=='RLA':
                cpu.setflag(C,bool(val&128));out=((val<<1)|oldcarry)&255
            elif operation=='SRE':
                cpu.setflag(C,bool(val&1));out=val>>1
            elif operation=='RRA':
                cpu.setflag(C,bool(val&1));out=(val>>1)|(oldcarry<<7)
            elif operation=='DCP':out=(val-1)&255
            else:out=(val+1)&255
            bus.wb(addr,out)
            if operation=='SLO':cpu.a=cpu.nz(cpu.a|out)
            elif operation=='RLA':cpu.a=cpu.nz(cpu.a&out)
            elif operation=='SRE':cpu.a=cpu.nz(cpu.a^out)
            elif operation=='DCP':
                cpu.setflag(C,cpu.a>=out);cpu.nz(cpu.a-out)
            else:val=out  # RRA/ISC share ALU implementation below
        if operation in ('SBC','ISC','RRA'):
            carry=int(cpu.flag(C))
            v=val if operation=='RRA' else val^255
            result=cpu.a+v+carry
            output=result&255
            cpu.setflag(C,result>255)
            cpu.setflag(V,bool((~(cpu.a^v)&(cpu.a^output)&128)))
            cpu.a=cpu.nz(output)
    cpu.p|=32
    bus.cpu_cycles+=cycles
    return True
