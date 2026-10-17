#!/usr/bin/env python3
"""Original JP 6502 symbol/branch assembler for 0526 scheduler+raw0B callbacks.

Outputs exactly the original opcodes and operands at original CPU/PRG addresses;
source is bank qualified, no ROM is stored in the repository. This does NOT
claim CPU execution/PPU parity or new strict PRG credit for already certified
regions. ROM-backed mode compares independently against retail PRG bytes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM_SHA = '958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
# Bounded official-NMOS-6502 opcode subset actually used by the two files.
OP = {
 ('inc','zp'):0xe6, ('lda','imm'):0xa9, ('lda','zp'):0xa5,
 ('lda','absx'):0xbd, ('sta','zp'):0x85, ('sta','absx'):0x9d, ('sta','abs'):0x8d,
 ('ldx','imm'):0xa2, ('ldx','zp'):0xa6, ('stx','zp'):0x86,
 ('beq','rel'):0xf0, ('bne','rel'):0xd0, ('bmi','rel'):0x30,
 ('bcc','rel'):0x90, ('bcs','rel'):0xb0,
 ('cmp','imm'):0xc9, ('cpx','imm'):0xe0,
 ('jsr','abs'):0x20, ('jmp','abs'):0x4c,
 ('and','imm'):0x29, ('ora','imm'):0x09,
 ('rts','imp'):0x60, ('dec','zp'):0xc6, ('dec','absx'):0xde,
 ('bpl','rel'):0x10, ('lsr','acc'):0x4a, ('eor','imm'):0x49,
}
SIZE={'imp':1,'acc':1,'imm':2,'zp':2,'rel':2,'abs':3,'absx':3,'word':2}
BRANCHES={'beq','bne','bmi','bcc','bcs','bpl'}
TARGETS={
 'fixed_scheduler_0526.asm':[(0xfde4,127,0x03fde4,
    'f3e0fd7af2b46b3625b2c7205cdfda7d1d3bf569672091b3ec129ad93448c3d6'),
    (0xfe76,116,0x03fe76,'e78b1a3e6459cc126302a1c1a92352d7f7b4eb1896cbb27aa0d8905b2a4a9caa')],
 'raw0b_callbacks_0526.asm':[(0x8161,50,0x02c161,
    '76de1d9e67c5a5ea5e388c2601527b8e4c60aa80ccc6a0e57fabe07c6268bc3e'),
   (0x826c,22,0x02c26c,
    '210667cf666f4bec07e356c74ee535bdb1303568600aadf9c4bcad7d215511e2')],
}

def decode_operand(mnemonic,arg):
    if not arg:return 'imp'
    if mnemonic=='.word':return 'word'
    if arg=='a':return 'acc'
    if mnemonic in BRANCHES:return 'rel'
    if arg.startswith('#'):return 'imm'
    if arg.endswith(',x'):return 'absx'
    if arg.startswith('$') and int(arg[1:],16)<256:return 'zp'
    return 'abs'

def parse_source(path):
    labels={};instructions=[];pc=None
    for line_no,raw in enumerate(path.read_text(encoding='ascii').splitlines(),1):
        line=raw.partition(';')[0].strip().lower()
        if not line:continue
        if line.startswith('.org '):
            pc=int(line.split()[1].replace('$','0x'),16)
            if pc>=65536:raise ValueError('CPU origin invalid')
            continue
        if line.endswith(':'):
            name=line[:-1].strip()
            if pc is None or name in labels or not re.fullmatch(r'[a-z_][a-z0-9_]*',name):
                raise ValueError('Illegal or duplicate label '+name)
            labels[name]=pc
            continue
        if pc is None:raise ValueError('Unlocated instruction')
        name,*tail=line.split(None,1)
        arg=tail[0].strip() if tail else ''
        mode=decode_operand(name,arg)
        if (name,mode) not in OP and mode!='word':raise ValueError('Unsupported original opcode '+line)
        instructions.append((pc,name,mode,arg,line_no))
        pc+=2*len(arg.split(',')) if mode=='word' else SIZE[mode]
    return instructions,labels

def assemble(path):
    ins,labels=parse_source(path)
    machine={}
    for pc,name,mode,arg,line in ins:
        code=[] if mode=='word' else [OP[name,mode]]
        if mode not in ('imp','acc'):
            if mode=='word':
                terms=[x.strip() for x in arg.split(',')]
                if not terms:raise ValueError('Empty .word')
                for term in terms:
                    operand=int(term[1:],16) if term.startswith('$') else labels.get(term)
                    if operand is None or not 0<=operand<=65535:
                        raise ValueError(f'Unresolved or invalid table pointer {term} line {line}')
                    code.extend((operand&255,operand>>8))
                for idx,byte in enumerate(code):
                    address=pc+idx
                    if address in machine:raise ValueError('Overlapping source table')
                    machine[address]=byte
                continue
            term=arg[1:] if mode=='imm' else arg[:-2] if mode=='absx' else arg
            if term.startswith('$'):
                operand=int(term[1:],16)
            else:
                if term not in labels:raise ValueError(f'Unresolved label {term} line {line}')
                operand=labels[term]
            if mode=='rel':
                operand-=pc+2
                if not -128<=operand<=127:raise ValueError(f'Branch overflow line {line}')
                operand&=255
            if mode in ('imm','zp','rel'):
                if not 0<=operand<=255:raise ValueError('8-bit operand overflow')
                code.append(operand)
            else:
                if not 0<=operand<=65535:raise ValueError('16-bit operand overflow')
                code.extend((operand&255,operand>>8))
        for idx,byte in enumerate(code):
            address=pc+idx
            if address in machine or address>65535:
                raise ValueError('Conflicting original 6502 code address')
            machine[address]=byte
    return machine

def audit(rom=None):
    prg=None
    if rom:
        raw=Path(rom).read_bytes()
        if len(raw)!=393232 or hashlib.sha256(raw).hexdigest()!=ROM_SHA:
            raise ValueError('Wrong original JP retail iNES ROM')
        prg=raw[16:16+262144]
    total=0
    for source,regions in TARGETS.items():
        code=assemble(ROOT/'decomp'/'asm'/source)
        for cpu,size,offset,digest in regions:
            try:actual=bytes(code[x] for x in range(cpu,cpu+size))
            except KeyError as e:raise ValueError('Missing original code bytes '+str(e)) from e
            if hashlib.sha256(actual).hexdigest()!=digest:
                raise ValueError(f'Original 6502 reassembly SHA mismatch at ${cpu:04X}')
            if prg is not None and actual!=prg[offset:offset+size]:
                raise ValueError(f'Original PRG comparison failed at ${offset:05X}')
            total+=size
            print(f'PASS 6502 original {source}: ${cpu:04X}, {size} bytes')
        if len(code)!=sum(region[1] for region in regions):
            raise ValueError('Unexpected opcode bytes outside original source spans')
    if total!=315:raise ValueError('Missing exact 315-byte new 6502 source')
    # Existing 0525 reassembly checks the five adjacent companion routines.
    print('PASS 0526 independent original JP 6502 source: 315/315 bytes; cumulative 0525+0526: 403')
    return {'new_6502_reassembled_bytes':total,'cumulative_byte_exact_6502_source':403,
            'original_rom_checked':prg is not None,
            'strict_prg_new_credit':0,'vpp_new_credit':0}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path)
    p.add_argument('--report',type=Path)
    a=p.parse_args()
    result=audit(a.rom)
    if a.report:a.report.write_text(json.dumps(result,indent=2)+'\n')
