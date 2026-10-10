#!/usr/bin/env python3
"""Exhaustive opcode-set smoke plus selected NMOS unofficial arithmetic edges."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[0]))
from nmos_undocumented_0508 import M
from test_nestest_external_0508 import NromBus,NromCPU

def cart(code):
    p=bytearray(16384);p[:len(code)]=code
    return b'NES\x1a'+bytes((1,0,0,0))+bytes(8)+p

def new_cpu(op,arg=0x10,hi=0x06):
    code=bytes([op,arg,hi])
    b=NromBus(cart(code));cpu=NromCPU(b)
    cpu.a=0x55;cpu.x=1;cpu.y=2;cpu.p=0x25
    b.wb(0x10,0xfe);b.wb(0x11,0x05)
    b.wb(0x12,0x06)
    b.wb(0x0600,0x80);b.wb(0x0610,0x80)
    b.wb(0x11,0x80)
    return cpu,b

class TestUnofficial(unittest.TestCase):
    def test_every_supported_opcode_consumes_correct_width_and_is_accounted(self):
        self.assertGreater(len(M),70)
        for opcode,(name,mode,cycles) in sorted(M.items()):
            with self.subTest(opcode=f'{opcode:02X}',name=name):
                c,b=new_cpu(opcode)
                if mode=='inx':
                    b.wb(0x11,0x00);b.wb(0x12,0x06)
                if mode=='iny':
                    b.wb(0x10,0xfe);b.wb(0x11,0x05)
                before=b.cpu_cycles
                c.step()
                width=1 if mode=='imp' else 3 if mode in ('abs','abx','aby') else 2
                self.assertEqual(c.pc,0xc000+width)
                self.assertEqual(c.steps,1)
                self.assertIn(b.cpu_cycles-before,(cycles,cycles+1))
    def test_shift_or(self):
        c,b=new_cpu(0x07);b.wb(0x10,0x80);c.a=1
        c.step()
        self.assertEqual((b.rb(0x10),c.a,bool(c.p&1)),(0,1,True))
    def test_dcp_compare(self):
        c,b=new_cpu(0xC7);b.wb(0x10,1);c.a=0
        c.step()
        self.assertEqual((b.rb(0x10),c.a,c.p&3),(0,0,3))
    def test_isc_sbc(self):
        c,b=new_cpu(0xE7);b.wb(0x10,0);c.a=5
        c.step()
        self.assertEqual((b.rb(0x10),c.a,c.p&1),(1,4,1))
    def test_anc(self):
        c,b=new_cpu(0x0B,arg=0xff);c.a=0x80
        c.step()
        self.assertEqual((c.a,c.p&0x81),(0x80,0x81))
    def test_lax(self):
        c,b=new_cpu(0xA7);b.wb(0x10,0xff)
        c.step()
        self.assertEqual((c.a,c.x,c.p&0x80),(0xff,0xff,0x80))

if __name__=='__main__':unittest.main(verbosity=2)
