#!/usr/bin/env python3
"""ROM-free CPU/reset-gate checks; optional authenticated JP original replay.

This is not an NES emulator conformance or PPU/frame fidelity certification.
"""
from __future__ import annotations
import argparse, json, tempfile
from pathlib import Path
from replay_reset_0548 import CPU, OPS, ReplayError, boot, scripted_frames

class MiniBus:
    def __init__(self,program,entry=0x8000):
        self.data=bytearray(65536);self.mem=self.data;self.bank=0
        self.data[entry:entry+len(program)]=bytes(program)
        self.data[0xfffc]=entry&255;self.data[0xfffd]=entry>>8
    def read(self,a):return self.data[a&65535]
    def write(self,a,v):self.data[a&65535]=v&255

def cpu_program(program, steps):
    b=MiniBus(program);c=CPU(b)
    for i in range(steps):c.step()
    return c,b

def smoke():
    assert len(OPS)==151, 'official NMOS 6502 opcode table incomplete'
    # Reset vector, immediate/zp addressing, branching, arithmetic, and stack.
    c,b=cpu_program([0xA9,0x05,0x85,0x34,0xA2,0x03,0xA5,0x34,0x18,0x69,0x07,
                     0x48,0xA9,0x00,0x68,0xE8,0xE0,0x04,0xD0,0x02,0xEA],10)
    assert (c.a,c.x,b.read(0x34),c.sp)==(12,4,5,0xfd)
    c,b=cpu_program([0xA9,0xFE,0x18,0x69,0x03,0xE9,0x01],3)
    assert c.a==1 and c.flag(1)
    # The synthetic instruction above stops before SBC; exercise borrow separately.
    c,b=cpu_program([0x38,0xA9,0x00,0xE9,0x01],3)
    assert c.a==255 and not c.flag(1) and c.flag(128)
    # Original 6502 JSR/RTS stack semantics.
    c,b=cpu_program([0x20,0x09,0x80,0xA9,0x42,0x4C,0x0C,0x80,0xEA,0xA9,0x41,0x60,0xEA],4)
    assert c.a==0x42 and c.pc==0x8005 and c.sp==0xfd
    # NMOS JMP ($XXFF) wraps high-byte fetch to $XX00.
    b=MiniBus([0x6C,0xFF,0x12]);b.write(0x12ff,0x34);b.write(0x1200,0x56);b.write(0x1300,0xee)
    c=CPU(b);c.step();assert c.pc==0x5634
    # RTI restores status and the interrupted PC after NMI.
    b=MiniBus([0xea,0xea]);b.write(0xfffa,0x00);b.write(0xfffb,0x90);b.write(0x9000,0x40)
    c=CPU(b);c.a=0x72;c.interrupt();c.step();assert c.pc==0x8000 and c.a==0x72 and c.sp==0xfd
    # A deliberately unsupported unofficial byte must fail closed.
    c,b=cpu_program([0xea],1)
    b.write(0x8001,0x02)
    try:c.step()
    except ReplayError:pass
    else:raise AssertionError('unknown opcode accepted')
    # Invalid requests never run an unbounded number of synthetic frames.
    try:scripted_frames(b'',0)
    except ValueError:pass
    else:raise AssertionError('invalid synthetic frame count accepted')
    # Failed source identities must not be silently accepted.
    try:boot(b'not a ROM')
    except ReplayError:pass
    else:raise AssertionError('non-authenticated original ROM accepted')
    print('PASS ROM-free 151-opcode table, 6502 semantics, stack/interrupt, fail-closed input checks')

def authenticated(rom):
    payload=rom.read_bytes()
    reset=boot(payload,limit=200000,inject_nmi=False)
    assert reset['boot_loop_reached'] and reset['boot_instruction_count']==6419
    assert reset['nmi_callsite_reached'] is False and not reset['first_failure']
    nmi=boot(payload,limit=200000,continue_through_nmi=True)
    assert nmi['boot_loop_reached'] and nmi['nmi_callsite_reached'] and not nmi['first_failure']
    assert nmi['nmi_vector']==0xE057 and nmi['scheduler_call']['ram18']==0
    assert nmi['scheduler_call']['state13'] is False
    assert nmi['first_nmi_return']['ram18']==0
    assert nmi['first_nmi_return']['returned_by_rti_at']==0xE0D6
    assert nmi['cpu_instructions']==11740
    result=scripted_frames(payload,80)
    assert len(result['frames'])==80 and not result['reached_state13']
    assert result['frames'][0]['scheduler']['state']==0
    assert all(x['scheduler']['state']==0 for x in result['frames'])
    return {'reset':reset,'first_complete_nmi':nmi,'scripted_frames':result,
            'authority':'Original 6502 instructions + scripted synthetic I/O. Does not prove VBlank/NMI timing, state13 gameplay reachability, or native full-frame parity.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path);p.add_argument('--out',type=Path)
    args=p.parse_args()
    smoke()
    if args.rom:
        report=authenticated(args.rom)
        if args.out:
            args.out.parent.mkdir(parents=True,exist_ok=True)
            args.out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        print('PASS authenticated JP reset 6419 instructions; complete first NMI 11740; 80 scripted NMI entries state0 only')
if __name__=='__main__':main()
