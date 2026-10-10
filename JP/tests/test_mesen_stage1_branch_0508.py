#!/usr/bin/env python3
"""ROM-free tests for original-Mesen Stage1 fork reporting and exact matching."""
import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from audit_mesen_stage1_branch_0508 import RUNS,C0501,PRG,read_mask,read_log,filebase,bits
from audit_mesen_stage1_crossedition_0508 import code_runs,cross,WINDOW

class TestOriginalMesenForks(unittest.TestCase):
    def log(self,frames=10,start=1101,version="2.1.1",lua_error=0):
        rows=[{"event":"loaded","mesen_version":version,"console":"Nes"},
          {"event":"cdl_saved","type":"NesPrgRom"},
          {"event":"lua_log","error_count":lua_error,
           "text":"STATE frame=1 s=04 00 09 03 00 00\nSTATE frame=10 s=04 03 08 03 00 00\n"},
          {"event":"summary","ok":True,"reason":"frame_limit",
           "frames_executed":frames,"start_frame":start,"final_frame":start+frames}]
        return "\n".join(json.dumps(x) for x in rows)+"\n"
    def test_total_forks(self):
        self.assertEqual((len(RUNS),sum(x[1] for x in RUNS)),(10,9500))
        self.assertEqual(sum(x[3]=="stage360" for x in RUNS),4)
        self.assertEqual(sum(x[3]=="right_jump" for x in RUNS),3)
    def test_manifest(self):
        self.assertEqual((len(C0501),sum(n for _,n in C0501)),(31,4364))
        a=set()
        for start,n in C0501:
            for p in range(start,start+n):
                self.assertNotIn(p,a);a.add(p)
    def test_frame_log(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"log";p.write_text(self.log())
            r=read_log(p,10,1101)
            self.assertEqual(r["firstlevel_18"],[4])
            self.assertEqual(r["room_19"],[3])
            self.assertEqual(r["secondary_68"],[8])
            with self.assertRaises(ValueError):read_log(p,11,1101)
            with self.assertRaises(ValueError):read_log(p,10,1111)
    def test_reject_bad_emulator_or_lua(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"log"
            for content in [self.log(version="0.0.0"),self.log(lua_error=1)]:
                p.write_text(content)
                with self.assertRaises(ValueError):read_log(p,10,1101)
    def test_cdl_length_crc(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"flags.cdl"
            a=bytearray(PRG);a[0]=3
            p.write_bytes(b"CDLv2"+bytes.fromhex("11223344")+a+bytes(131072))
            v,crc,h=read_mask(p)
            self.assertEqual((bits(v,1),bits(v,2),crc),(1,1,bytes.fromhex("11223344")))
            self.assertEqual(len(h),64)
            with self.assertRaises(ValueError):read_mask(p,bytes.fromhex("55667788"))
            p.write_bytes(b"CDLv2"+bytes(4))
            with self.assertRaises(ValueError):read_mask(p)
    def test_bank_aligned_code_runs(self):
        m=bytearray(PRG);m[8190:8210]=bytes([1])*20
        self.assertEqual(list(code_runs(m)),[(8192,8210)])
        with self.assertRaises(ValueError):list(code_runs(b""))
    def test_exact_unique_candidate(self):
        j=bytearray(PRG);u=bytearray(PRG);m=bytearray(PRG)
        tok=bytes(range(1,17));j[100:116]=tok;u[10000:10016]=tok;m[100:116]=bytes([1])*16
        r=cross(j,u,m)
        self.assertEqual((r["unique_exact_source_bytes"],r["exact_whole_code_bit_runs"]),(16,1))
    def test_exact_ambiguous_candidate(self):
        j=bytearray(PRG);u=bytearray(PRG);m=bytearray(PRG)
        tok=bytes(range(1,17));j[100:116]=tok
        u[10000:10016]=tok;u[30000:30016]=tok;m[100:116]=bytes([1])*16
        r=cross(j,u,m)
        self.assertEqual(r["unique_exact_source_bytes"],0)
        self.assertEqual(r["ambiguous_only_source_bytes"],16)
    def test_bad_prg_len(self):
        with self.assertRaises(ValueError):cross(b"",b"",bytes(PRG))
    def test_filebases(self):
        self.assertEqual(filebase("play520",None),"play520")
        self.assertEqual(filebase("right_jump","stage360"),"right_jump_1200")
if __name__=="__main__":unittest.main(verbosity=2)
