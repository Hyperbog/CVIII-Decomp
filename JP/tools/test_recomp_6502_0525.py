#!/usr/bin/env python3
"""Two-pass 6502 symbolic source assembler and JP original-ROM parity gate.

Reassemble known original routines at their CPU addresses and verify exact
physical PRG bytes. This is real opcode/operand recompilation, not .byte copying,
not a full NES/mapper emulator, and not a novel strict PRG-byte claim.
"""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ROM_SHA="958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
OP={
 ("lda","imm"):0xa9,("lda","absx"):0xbd,("cmp","imm"):0xc9,
 ("beq","rel"):0xf0,("sta","absx"):0x9d,("sta","zp"):0x85,
 ("sta","abs"):0x8d,("rts","imp"):0x60,("tax","imp"):0xaa,
 ("and","imm"):0x29,("jsr","abs"):0x20,("ldx","zp"):0xa6,
 ("inx","imp"):0xe8,("cpx","imm"):0xe0,("bcs","rel"):0xb0,
 ("jmp","abs"):0x4c,
}
SIZE={"imp":1,"imm":2,"zp":2,"rel":2,"abs":3,"absx":3}
# All source hashes are authenticated against the exact original JP cartridge.
TARGETS={
 "actor_tail_0525.asm":[
  (0x8193,22,0x02c193,"0b9f9559ee19ffcdb30d51a70bb887aa7f5430b648f886eb5a261987e3989ed2"),
  (0x81b2,26,0x02c1b2,"d84f72f11fe42f867816b7503d55d8bbd0d0796f93b8ba1a8360894a1b8080d4"),
  (0xb56b,15,0x02f56b,"15da8668d001967910311e8f390ba85e07b73a2236a39e338f8aff9a6645f3dc")],
 "fixed_tail_0525.asm":[
  (0xe2d0,6,0x03e2d0,"8d1a2898917458f00a455757ee9471327e1d4f51bee3d841d98e23055fb51380"),
  (0xfe63,19,0x03fe63,"bfe287c26149b305403019d54a537ab15137c4a46933803ddc82e8e6f291631e")]
}
def parse(path):
    instructions=[];labels={};pc=None
    for lineno,raw in enumerate(path.read_text(encoding="ascii").splitlines(),1):
        line=raw.split(";",1)[0].strip()
        if not line:continue
        if line.endswith(":"):
            label=line[:-1].lower()
            if label in labels or pc is None:
                raise ValueError("Duplicate or unlocated label at line "+str(lineno))
            labels[label]=pc
            continue
        if line.lower().startswith(".org "):
            pc=int(line.split(None,1)[1].replace("$","0x"),16)
            continue
        if pc is None:raise ValueError("Instruction before origin")
        op,*tail=line.lower().split(None,1)
        operand=tail[0].strip() if tail else ""
        if not operand:mode="imp"
        elif op in ("beq","bcs"):mode="rel"
        elif operand.startswith("#"):mode="imm"
        elif operand.endswith(",x"):mode="absx"
        elif operand.startswith("$") and int(operand[1:],16)<256:mode="zp"
        else:mode="abs"
        if (op,mode) not in OP:raise ValueError("Unsupported instruction "+line)
        instructions.append((pc,op,mode,operand,lineno))
        pc+=SIZE[mode]
    return instructions,labels
def compile_source(path):
    instructions,labels=parse(path)
    compiled={}
    for pc,op,mode,operand,lineno in instructions:
        raw=[OP[(op,mode)]]
        if mode!="imp":
            item=operand[1:] if mode=="imm" else operand[:-2] if mode=="absx" else operand
            value=int(item[1:],16) if item.startswith("$") else labels.get(item)
            if value is None:raise ValueError("Unresolved source label at "+str(lineno))
            if mode=="rel":
                value-=pc+2
                if not -128<=value<=127:raise ValueError("Relative branch cannot reach label")
                value &= 255
            if mode in ("imm","zp","rel"):
                if not 0<=value<=255:raise ValueError("8-bit operand out of range")
                raw.append(value)
            else:
                if not 0<=value<=65535:raise ValueError("16-bit operand out of range")
                raw.extend((value&255,value>>8))
        for i,b in enumerate(raw):
            if pc+i in compiled:raise ValueError("Overlapping code at CPU address")
            compiled[pc+i]=b
    return compiled
def audit(rom_path=None):
    if rom_path:
        rom=Path(rom_path).read_bytes()
        if len(rom)!=393232 or hashlib.sha256(rom).hexdigest()!=ROM_SHA:
            raise ValueError("Wrong original JP retail ROM")
        prg=rom[16:16+262144]
    else:prg=None
    total=0
    for source,regions in TARGETS.items():
        code=compile_source(ROOT/"recomp"/source)
        for cpu,size,offset,digest in regions:
            try:result=bytes(code[pos] for pos in range(cpu,cpu+size))
            except KeyError as error:raise ValueError("Missing recompiled source byte") from error
            if hashlib.sha256(result).hexdigest()!=digest:
                raise ValueError("6502 opcode recompilation mismatch at "+hex(cpu))
            if prg is not None and result!=prg[offset:offset+size]:
                raise ValueError("Original JP ROM disagrees with assembled 6502 source")
            total+=size
            print("PASS 6502 source",source,hex(cpu),size,"bytes")
        if len(code)!=sum(r[1] for r in regions):
            raise ValueError("Unverified instructions outside authenticated source ranges")
    if total!=88:raise ValueError("Original source coverage unexpectedly changed")
    print("PASS original JP symbolic 6502 recompilation 88/88 bytes, ROM verified:",bool(prg))
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rom",type=Path)
    a=p.parse_args()
    audit(a.rom)
if __name__=="__main__":main()
