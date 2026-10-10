#!/usr/bin/env python3
"""ROM-free checks of golden-log NROM CPU harness plumbing."""
import sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from test_nestest_external_0508 import NromBus, NromCPU, run

def cart(opcodes: bytes):
    prg=bytearray(16384)
    prg[0x0000:0x0000+len(opcodes)]=opcodes
    prg[0x3ffc:0x3ffe]=b'\x00\xc0'
    return b'NES\x1a'+bytes((1,0,0,0))+bytes(8)+prg

class TestNestestRunner(unittest.TestCase):
    def test_mapper_nrom_mirror(self):
        b=NromBus(cart(b'\xa9\x42'))
        self.assertEqual(b.rb(0xc000),0xa9)
        self.assertEqual(b.rb(0x8001),0x42)
        self.assertEqual(b.rw(0xfffc),0xc000)
    def test_ram_mirrors(self):
        b=NromBus(cart(b'\xea'));b.wb(0x17ff,0x5a)
        self.assertEqual(b.rb(0x7ff),0x5a)
        self.assertEqual(b.rb(0x0fff),0x5a)
    def test_preinstruction_and_cycle_golden(self):
        im=cart(bytes.fromhex('a9 42 18 69 01 85 00 4c 04 c0'))
        line=lambda pc,a,p,cyc: f'{pc:04X}  EA NOP     A:{a:02X} X:00 Y:00 P:{p:02X} SP:FD PPU:  0, 21 CYC:{cyc}'
        with tempfile.TemporaryDirectory() as td:
            rom=Path(td)/'test.nes';rom.write_bytes(im)
            log=Path(td)/'nestest.log';log.write_text('\n'.join([
                line(0xc000,0x00,0x24,7),
                line(0xc002,0x42,0x24,9),
                line(0xc003,0x42,0x24,11),
                line(0xc005,0x43,0x24,13),
                line(0xc007,0x43,0x24,16)])+'\n')
            result=run(str(rom),str(log))
            self.assertEqual((result['matching_instruction_states'],result['golden_instructions']),(5,5),result['differences'])
    def test_bad_mapper(self):
        r=bytearray(cart(b'\xea'));r[6]=0x10
        with self.assertRaises(AssertionError):NromBus(bytes(r))
    def test_golden_first_mismatch_is_bounded(self):
        im=cart(b'\xea')
        with tempfile.TemporaryDirectory() as td:
            rom=Path(td)/'test.nes';rom.write_bytes(im)
            log=Path(td)/'log';log.write_text('C001  EA NOP     A:00 X:00 Y:00 P:24 SP:FD CYC:7\n')
            result=run(str(rom),str(log))
            self.assertEqual(result['matching_instruction_states'],0)
            self.assertIn('pc',result['differences'][0]['fields'])

if __name__=='__main__':unittest.main(verbosity=2)
