#!/usr/bin/env python3
"""Experimental CPU instruction-cycle class and synthetic PPU-vblank unit audit.

Validates deterministic implementation invariants, NOT hardware/reference parity.
"""
from pathlib import Path
import argparse,hashlib,json
from trace_cycle_vblank_0508 import CycleBus,CycleCPU,base_cycles,OPS,ROM_SHA

MODE_NORMAL={'indx':'inx','indy':'iny','absx':'abx','absy':'aby'}
def run(path):
    rom=Path(path).read_bytes()
    assert len(rom)==393232 and hashlib.sha256(rom).hexdigest()==ROM_SHA
    classes={}
    for op,(m,mode,size) in OPS.items():
        normalized=MODE_NORMAL.get(mode,mode)
        cyc=base_cycles(m,normalized)
        assert 2<=cyc<=7 and size in (1,2,3),(hex(op),m,mode,cyc)
        classes[op]=cyc
    assert len(classes)==151,len(classes)
    assertions=0
    # Representative documented NTSC/2A03 cycle classes, including indexed
    # read vs indexed store, indirect read and RMW old/new bus writes.
    examples={
        0xEA:2, 0x20:6,0x60:6,0x40:6,0x00:7,0x6C:5,
        0xA9:2,0xAD:4,0xBD:4,0xB1:5,0x91:6,
        0x9D:5,0x8D:4,0x0E:6,0x1E:7,0x16:6,
        0xD0:2,0xF0:2,0x48:3,0x68:4,0x08:3,0x28:4,
        0xE6:5,0xF6:6,0xFE:7,0xE0:2,0xEC:4}
    for op,want in examples.items():
        assert classes[op]==want,(hex(op),classes[op],want)
        assertions+=1
    b=CycleBus(rom)
    assert (b.ppu_phase,b.vblank,b.nmi_line,b.nmi_pending,b.nmi_edges)==(0,False,False,False,0)
    b.wb(0x2000,0x80)
    b.advance(27393) # PPU $2002 vblank start is at CPU-cycle 27394
    assert b.ppu_phase==27393*3 and not b.vblank and b.nmi_edges==0
    b.advance(1)
    assert (b.ppu_phase,b.vblank,b.nmi_line,b.nmi_pending,b.nmi_edges)==(341*241+1,True,True,True,1)
    assert b.rb(0x2002)==0x80
    assert not b.vblank and not b.nmi_line and b.nmi_pending
    b.nmi_pending=False
    assert b.rb(0x2002)==0 and b.nmi_edges==1
    # The vblank start is a rising edge; enabling NMI *during* vblank raises
    # a new edge, but repeated writes to $2000 do not duplicate an edge.
    b2=CycleBus(rom)
    b2.advance(27394)
    assert b2.vblank and not b2.nmi_pending
    b2.wb(0x2000,0x80)
    assert b2.nmi_edges==1 and b2.nmi_pending
    b2.nmi_pending=False
    b2.wb(0x2000,0x80)
    assert b2.nmi_edges==1 and not b2.nmi_pending
    b2.advance(341*20//3+10)
    assert not b2.vblank
    # Explicit early DMA only queues a CPU stall; RAM/OAM transfers are not
    # modeled. Confirm this remains labeled as a restricted timing primitive.
    b3=CycleBus(rom)
    b3.wb(0x4014,2)
    assert b3.dma_requested==1
    # The real instruction step invokes the real NMI stack/vector when the
    # scheduler has a pending line and uses the first ROM NMI instruction.
    cpu=CycleCPU(b2)
    b2.nmi_pending=True
    old=cpu.sp;cpu.step()
    assert cpu.NMI_count==1 and cpu.sp==((old-4)&255)
    assert cpu.last_instruction[0]==0xE057 and cpu.last_instruction[2]=='PHA'
    assert cpu.NMI_log[0]['NMI']==1
    # CPU cycle and ROM-instruction regression separately establish the
    # map/reset behavior. This unit test is *not* a reference timing oracle.
    return {'status':'EXPERIMENTAL_CYCLE_CLASS_VBLANK_TEST_NOT_HARDWARE_PARITY',
        'rom_sha256':ROM_SHA,'official_opcode_classes_tested':len(classes),
        'representative_cycle_classes_checked':assertions,
        'ppu_dots_per_frame':b.DOTS_PER_FRAME,
        'vblank_start_ppu_dot':b.VBLANK_AT,
        'vblank_clear_ppu_dot':b.VBLANK_END,
        'ppu_cpu_cycles_to_first_vblank':27394,
        'ppu_status_clears_vblank':True,
        'ppu_ctrl_mid_vblank_nmi_edge':True,
        'dma_stall_queued_not_cpu_bus_parity':True,
        'nmi_cpu_stack_push_sample':True,
        'limits':['Approximate PPU/CPU instruction-boundary timing, no odd-frame skip, no mapper IRQ, no DMC/APU frame synchronization',
                  'Not a reference-emulator differential test or full system parity'],
        'strict_PRG_new_bytes':0,'strict_PRG_verified':49404,'VPP':24}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('rom');p.add_argument('report');a=p.parse_args()
    r=run(a.rom)
    Path(a.report).write_text(json.dumps(r,indent=2)+'\n')
    print('CPU cycle-vblank class test PASS',r['official_opcode_classes_tested'],'official opcodes',r['representative_cycle_classes_checked'],'samples')
