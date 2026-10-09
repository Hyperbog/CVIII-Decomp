#!/usr/bin/env python3
"""Mapped JP $E7FB ABI and CPU ALU/stack/indirect JMP byte tests.

The ALU/stack programs execute from volatile cartridge PRG-RAM at $6000;
E7FB dispatch instead executes only original JP ROM instructions.
No full NES PPU/APU/IRQ timing or real recorded console CPU trace.
"""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
from trace_6502_vrc6_0508 import Bus,CPU,C,Z,D,V,N,ROM_SHA

Y_VALUES=(0,1,2,0x40,0x7F,0x80,0xFE,0xFF)


def test(rom):
    b=Bus(rom,10)
    prg=b.prg
    count=0
    instructions=0
    for selector in range(256):
        offset=(selector*2)&255
        lo_cpu=0xB4D0+((offset+1)&255)
        hi_cpu=0xB4D0+((offset+2)&255)
        low=prg[10*16384+lo_cpu-0x8000]
        high=prg[10*16384+hi_cpu-0x8000]
        target=low|(high<<8)
        for y in Y_VALUES:
            b.ram[:]=bytes(2048)
            b.raw_bank=10
            b.ram[0x19]=selector
            cpu=CPU(b,0xB4CC)
            cpu.y=y
            cpu.push(0x8F);cpu.push(0xFF)
            initial=cpu.steps
            for _ in range(17):cpu.step()
            assert cpu.pc==target,(selector,y,hex(target),hex(cpu.pc),cpu.steps,cpu.last_instruction)
            assert cpu.a==high,(selector,y,hex(target),hex(cpu.a),hex(high),cpu.steps)
            assert cpu.y==y
            assert cpu.sp==0xFB  # E7FB consumes the inline JSR return, not parent
            assert (b.ram[0x02],b.ram[0x03])==(low,high)
            assert cpu.flag(C)==bool(selector&0x80)
            assert cpu.flag(Z)==(y==0)
            assert cpu.flag(N)==bool(y&0x80)
            assert cpu.steps==17,(selector,y,cpu.steps)
            instructions+=cpu.steps-initial
            count+=1
    # 2A03 always performs binary ADC/SBC even with decimal flag set.
    # Compare arithmetic and overflow to independent arithmetic formulas.
    alu=0
    values=tuple(range(0,256,7))+(0x7f,0x80,0xff)
    for opcode in (0x69,0xE9):
        for a in range(256):
            for v in values:
                for carry in (0,1):
                    cpu=CPU(b,0x6000)
                    b.sram[0:2]=bytes((opcode,v))
                    cpu.a=a
                    cpu.setflag(C,bool(carry));cpu.setflag(D,True)
                    cpu.step()
                    q=v if opcode==0x69 else (v^255)
                    t=a+q+carry;out=t&255
                    assert cpu.a==out,(opcode,a,v,carry)
                    assert cpu.flag(C)==(t>255)
                    assert cpu.flag(Z)==(out==0)
                    assert cpu.flag(N)==bool(out&0x80)
                    assert cpu.flag(V)==bool((~(a^q)&(a^out)&0x80))
                    assert cpu.flag(D)  # unchanged but ignored by 2A03 arithmetic
                    alu+=1;instructions+=1
    # NMOS JMP ($60FF) takes its high byte from $6000, not $6100.
    b.sram[0x100]=0xA3
    for lo,hi in ((0x34,0x12),(0x01,0xAB),(0xFF,0x00),(0x00,0xFF)):
        b.sram[0x0100]=0x98
        b.sram[0:3]=bytes((0x6C,0xFF,0x60))
        b.sram[0xFF]=lo
        # $6000 simultaneously holds the JMP opcode, so high should equal
        # the literal $6C, irrespective of what is at $6100.
        cpu=CPU(b,0x6000);cpu.step()
        assert cpu.pc==(lo|0x6C00)
        instructions+=1
    # BRK pushes PC+2 / B=1; IRQ vector is ROM-fixed at E0F5.
    b.sram[0:2]=b'\x00\xEA'
    cpu=CPU(b,0x6000)
    cpu.sp=0xFD
    cpu.step()
    assert cpu.pc==0xE0F5
    assert cpu.sp==0xFA
    assert b.ram[0x1FD]==0x60 and b.ram[0x1FC]==0x02
    assert b.ram[0x1FB] & 0x10
    instructions+=1
    # A hand-triggered NMI uses the actual fixed NMI vector, no frame timing.
    cpu=CPU(b,0x8123)
    cpu.interrupt(0xFFFA)
    assert cpu.pc==0xE057 and cpu.sp==0xFA
    assert b.ram[0x1FD]==0x81 and b.ram[0x1FC]==0x23
    assert not b.ram[0x1FB]&0x10
    assert cpu.flag(4)
    return {'status':'ROM_BACKED_PARTIAL_6502_CPU_CONFORMANCE_NOT_EXTERNAL_EMULATOR_PARITY',
      'rom_sha256':ROM_SHA,
      'e7fb_dispatch_cases':count,'e7fb_y_set':list(Y_VALUES),
      'binary_alu_cases':alu,'indirect_jmp_pagewrap_cases':4,
      'brk_software_interrupt_cases':1,'nmi_manual_entry_cases':1,
      'total_cpu_instructions_executed':instructions,
      'scope':'ROM-fetched E7FB; synthetic RAM ALU cases; NES 2A03 official opcodes',
      'limits':['does not test all 151 instructions exhaustively',
                'no PPU/NMI/IRQ CPU-cycle scheduling or reference traces',
                'no full-game behavior/score promotion'],
      'strict_new_prg_bytes':0,'strict_cumulative_prg_bytes':49404,'vpp':24}

if __name__=='__main__':
    if len(sys.argv) not in (2,3):raise SystemExit('usage: test_trace_6502_micro_0508.py ROM.nes [json]')
    data=Path(sys.argv[1]).read_bytes()
    assert hashlib.sha256(data).hexdigest()==ROM_SHA
    result=test(data)
    if len(sys.argv)==3:Path(sys.argv[2]).write_text(json.dumps(result,indent=2)+'\n')
    print('CPU micro conformance passed',result['e7fb_dispatch_cases'],'mapped E7FB cases',result['binary_alu_cases'],'binary 2A03 ALU cases')
