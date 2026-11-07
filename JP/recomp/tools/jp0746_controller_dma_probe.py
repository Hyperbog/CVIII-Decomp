#!/usr/bin/env python3
"""Opt-in pinned upstream DMC/controller collision experiment.

Mode 1: suppress held-controller extra shift on DMC halt cycles.
Mode 2: retain CPU's pre-DMC controller upper bus bits.
Mode 3: both. Experimental and OFF by default; no gameplay/source credit.
"""
from __future__ import annotations
import argparse
from pathlib import Path

MACHINE_CYCLE='''    hw.cpu_addr = addr;
    hw.cpu_reading = kind == HW_READ || kind == HW_FETCH;'''
MACHINE_READ='''uint8_t value = (uint8_t)(apu_read_controller((int)reg - 0x16) | (hw.data_bus & 0xE0));'''
APU_HALT='''    if (cyc_trace_enabled) cyc_trace_dma(true);
    hw_bus_read(hw.cpu_addr);
}'''

def once(s,needle,replacement):
    if s.count(needle)!=1:raise ValueError('pinned NESRecomp anchor missing/repeated: '+needle[:80])
    return s.replace(needle,replacement,1)

def patch_machine(s):
    s=once(s,'void hw_cycle_start(uint16_t addr, HwCycleKind kind)\n{',
'''#if (JP0746_CONTROLLER_DMA_POLICY & 2)
/* Experimental: track CPU controller bus upper bits independently of
   intervening DMC sample fetch. Do not enable for production by default. */
static uint8_t jp0746_controller_cpu_upper;
#endif
void hw_cycle_start(uint16_t addr, HwCycleKind kind)
{''')
    s=once(s,MACHINE_CYCLE,
'''    hw.cpu_addr = addr;
#if (JP0746_CONTROLLER_DMA_POLICY & 2)
    if (addr == 0x4016u || addr == 0x4017u)
        jp0746_controller_cpu_upper = (uint8_t)(hw.data_bus & 0xE0u);
#endif
    hw.cpu_reading = kind == HW_READ || kind == HW_FETCH;''')
    s=once(s,MACHINE_READ,
'''#if (JP0746_CONTROLLER_DMA_POLICY & 2)
            uint8_t upper = (addr == hw.cpu_addr && hw_dma_stalls)
                ? jp0746_controller_cpu_upper : hw.data_bus;
#else
            uint8_t upper = hw.data_bus;
#endif
            uint8_t value = (uint8_t)(apu_read_controller((int)reg - 0x16) | (upper & 0xE0u));''')
    return s

def patch_apu(s):
    return once(s,APU_HALT,
'''    if (cyc_trace_enabled) cyc_trace_dma(true);
#if (JP0746_CONTROLLER_DMA_POLICY & 1)
    /* Experimental: a DMC halt holds the controller bus without
       consuming another serial input bit. */
    if (hw.cpu_addr == 0x4016u || hw.cpu_addr == 0x4017u)
        return;
#endif
    hw_bus_read(hw.cpu_addr);
}''')

def smoke():
    m='void hw_cycle_start(uint16_t addr, HwCycleKind kind)\n{\n'+MACHINE_CYCLE+'\n}\n'+MACHINE_READ
    a='static void dma_halt(void)\n{\n'+APU_HALT
    x=patch_machine(m);y=patch_apu(a)
    assert 'jp0746_controller_cpu_upper' in x and 'JP0746_CONTROLLER_DMA_POLICY & 1' in y
    for fn,src in ((patch_machine,x),(patch_apu,y)):
        try:fn(src)
        except ValueError:pass
        else:raise AssertionError('duplicate patch accepted')
    print('PASS JP0746 pinned-source ROM-free DMA/controller policy smoke')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--smoke',action='store_true')
    p.add_argument('--machine',type=Path)
    p.add_argument('--apu',type=Path)
    p.add_argument('--output-directory',type=Path)
    args=p.parse_args()
    if args.smoke:smoke();return
    if not(args.machine and args.apu and args.output_directory):
        p.error('--machine --apu --output-directory required')
    if args.output_directory.resolve()==args.apu.parent.resolve():
        raise ValueError('refuse upstream overwrite')
    args.output_directory.mkdir(parents=True,exist_ok=True)
    (args.output_directory/'cviii_jp0746_hw_machine.c').write_text(
        patch_machine(args.machine.read_text(encoding='utf8')),encoding='utf8')
    (args.output_directory/'cviii_jp0746_hw_apu.c').write_text(
        patch_apu(args.apu.read_text(encoding='utf8')),encoding='utf8')
    print('JP0746 opt-in overlays created without rewriting upstream')

if __name__=='__main__':main()
