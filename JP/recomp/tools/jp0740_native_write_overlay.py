#!/usr/bin/env python3
"""JP0740: fail-closed opt-in overlays for the pinned NESRecomp CPU bus.

Only an output-directory copy is changed; external NESRecomp is untouched.
These hooks expose real bus writes (incl. unchanged writes), CPU $4016/$4017
reads, and the dispatching PC / physically mapped bank at instruction entry.
"""
from __future__ import annotations
import argparse
from pathlib import Path

HEADER = '#include "cviii_jp0740_native_trace.h"'
MACHINE_START = '''void hw_bus_write(uint16_t addr, uint8_t value)
{
    if (cyc_trace_enabled) cyc_trace_access(addr, value, true);'''
MACHINE_NEW = '''void hw_bus_write(uint16_t addr, uint8_t value)
{
    /* JP0740 - observe actual bus writes before original hardware handling. */
    if (addr < 0x2000u)
        cviii_jp0740_write(addr, hw.ram[addr & 0x7FFu], value, hw.cycles);
    else if (addr == 0x4016u)
        cviii_jp0740_write(addr, 0xFFu, value, hw.cycles);
    if (cyc_trace_enabled) cyc_trace_access(addr, value, true);'''
READ_START = '''uint8_t hw_read(uint16_t addr)
{
    return hw_bus_read(addr);
}'''
READ_NEW = '''uint8_t hw_read(uint16_t addr)
{
    uint8_t value = hw_bus_read(addr);
    if (addr == 0x4016u || addr == 0x4017u)
        cviii_jp0740_read(addr, value, hw.cycles);
    return value;
}'''
RUN_START = '''static void dispatch(void) {
    int view;
    {'''
RUN_NEW = '''static void dispatch(void) {
    int view;
    /* JP0740: record opcode-entry PC and the original 4 KiB PRG bank
     * BEFORE any bus writes. The CPU PC may advance inside callbacks. */
    cviii_jp0740_instruction(cpu.pc,
        hw_prg_is_rom(cpu.pc) ?
        ((hw_prg_bank4(cpu.pc) << 12u) | (cpu.pc & 0x0FFFu)) : 0xFFFFFu);
    {'''

def replace_once(s: str, a: str, b: str) -> str:
    if s.count(a) != 1:
        raise ValueError('pinned upstream NESRecomp anchor absent/repeated: ' + a[:70])
    return s.replace(a, b, 1)

def patch(s: str, kind: str) -> str:
    if HEADER in s: raise ValueError('JP0740 duplicate patch')
    if kind == 'machine':
        s=replace_once(s, '#include "hw_internal.h"',
                       '#include "hw_internal.h"\n'+HEADER)
        # hw_machine.c lives in runner/cyc upstream; its quoted relative
        # common header must become an explicit include from the copied build dir.
        s=replace_once(s, '#include "../../common/nes_fds.h"',
                       '#include "nes_fds.h"')
        s=replace_once(s, MACHINE_START, MACHINE_NEW)
        s=replace_once(s, READ_START, READ_NEW)
    elif kind == 'run':
        s=replace_once(s, '#include "cyc_run.h"',
                       '#include "cyc_run.h"\n'+HEADER)
        s=replace_once(s, RUN_START, RUN_NEW)
    else: raise ValueError('invalid source kind')
    return s

def smoke() -> None:
    machine='#include "hw_internal.h"\n#include "../../common/nes_fds.h"\n'+READ_START+'\n'+MACHINE_START+'\n}'
    run='#include "cyc_run.h"\n'+RUN_START+'\n}'
    m=patch(machine,'machine')
    r=patch(run,'run')
    assert m.count('cviii_jp0740_write(addr')==2
    assert m.count('cviii_jp0740_read(addr, value, hw.cycles)')==1
    assert r.count('cviii_jp0740_instruction(cpu.pc')==1
    assert 'hw_prg_bank4(cpu.pc)' in r
    for text,kind in ((m,'machine'),(r,'run'),
                      (machine.replace(READ_START,'broken'),'machine')):
        try:patch(text,kind)
        except ValueError:pass
        else:raise AssertionError('damaged/duplicate source accepted')
    print('PASS JP0740 ROM-free pinned-source CPU bus/dispatch overlay smoke')

def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--smoke',action='store_true')
    p.add_argument('--machine',type=Path)
    p.add_argument('--run',type=Path)
    p.add_argument('--output-directory',type=Path)
    a=p.parse_args()
    if a.smoke:smoke();return
    if not(a.machine and a.run and a.output_directory):
        p.error('--machine --run --output-directory required')
    if a.machine.name!='hw_machine.c' or a.run.name!='cyc_run.c' or a.machine.parent!=a.run.parent:
        raise ValueError('input files must be same pinned NESRecomp CYC directory')
    out=a.output_directory.resolve()
    if out==a.machine.parent.resolve():
        raise ValueError('upstream source overwrite rejected')
    out.mkdir(parents=True,exist_ok=True)
    for path,kind,dest in ((a.machine,'machine','cviii_jp0740_hw_machine.c'),
                           (a.run,'run','cviii_jp0740_cyc_run.c')):
        (out/dest).write_text(patch(path.read_text(encoding='utf8'),kind),
                              encoding='utf8')
    print('JP0740 private source overlays generated; external NESRecomp untouched')

if __name__=='__main__':main()
