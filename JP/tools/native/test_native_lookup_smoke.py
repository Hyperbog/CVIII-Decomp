#!/usr/bin/env python3
"""ROM-free compilation and synthetic-input oracle for native room lookup."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import os

HERE=Path(__file__).resolve().parent

class NativeCompileSmoke(unittest.TestCase):
    def test_host_cpp_compiles_and_uses_three_pointer_levels(self):
        compiler=os.environ.get('CXX','g++')
        if shutil.which(compiler) is None:
            self.skipTest('C++ compiler unavailable; native build must run on enabled platform')
        with tempfile.TemporaryDirectory() as t:
            td=Path(t)
            binary=td/'lookup'
            subprocess.run([compiler,'-std=c++17','-O2','-Wall','-Wextra','-Werror','-pedantic',
                            str(HERE/'raw0a_lookup_native.cpp'),'-o',str(binary)],check=True)
            bank=bytearray(0x4000)
            def wr(cpu,val):
                bank[cpu-0x8000:cpu-0x8000+2]=val.to_bytes(2,'little')
            wr(0x92AE,0x9400)   # first level selector0
            wr(0x92B0,0x9402)   # first level selector1
            wr(0x9400,0x9500)   # second level selector0
            wr(0x9402,0x9502)
            wr(0x9500,0x9600)   # leaf selector0
            wr(0x9502,0x9604)
            image=td/'synthetic_bank.bin';image.write_bytes(bank)
            cases=td/'synthetic_cases.tsv';cases.write_text('0 0 0\n1 0 0\n')
            result=subprocess.run([str(binary),str(image),str(cases)],capture_output=True,text=True,check=True)
            rows=[json.loads(x) for x in result.stdout.splitlines()]
            self.assertEqual([x['leaf_ptr'] for x in rows],['9600','9604'])
            self.assertEqual([x['stage_ptr'] for x in rows],['9400','9402'])
            self.assertEqual([x['second_ptr'] for x in rows],['9500','9502'])
            self.assertEqual([x['physical_bank'] for x in rows],['NES:JP:VRC6:raw0A']*2)

    def test_reject_short_bank(self):
        compiler=os.environ.get('CXX','g++')
        if shutil.which(compiler) is None:self.skipTest('C++ compiler unavailable')
        with tempfile.TemporaryDirectory() as t:
            td=Path(t);exe=td/'lookup'
            subprocess.run([compiler,'-std=c++17','-O2','-Wall','-Wextra','-Werror','-pedantic',
                            str(HERE/'raw0a_lookup_native.cpp'),'-o',str(exe)],check=True)
            bad=td/'bad.bin';bad.write_bytes(b'\x00'*40)
            case=td/'case.tsv';case.write_text('0 0 0\n')
            result=subprocess.run([str(exe),str(bad),str(case)],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)

if __name__=='__main__':unittest.main()
