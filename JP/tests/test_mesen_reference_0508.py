#!/usr/bin/env python3
"""ROM-free regression tests for independent Mesen CDLv2 reference importer."""
from __future__ import annotations
import hashlib,json,sys,unittest
from pathlib import Path
sys.path.insert(0,str((Path(__file__).resolve().parents[1]/'tools') if Path(__file__).resolve().parent.name=='tests' else Path(__file__).resolve().parent))
from audit_mesen_reference_0508 import (PRG_SIZE,CHR_SIZE,CHECKPOINT_0501_REGIONS,
    decode_cdl,decode_log,counts,known_overlap,bank_rows,sha)

class TestMesenReference(unittest.TestCase):
    def test_shape_pinned(self):
        self.assertEqual((PRG_SIZE,CHR_SIZE),(262144,131072))
        self.assertEqual((len(CHECKPOINT_0501_REGIONS),sum(n for _,n in CHECKPOINT_0501_REGIONS)),(31,4364))
    def test_cdl_header_and_crc(self):
        mask=bytes(PRG_SIZE)
        got,crc=decode_cdl(b'CDLv2'+bytes.fromhex('12345678')+mask+bytes(CHR_SIZE))
        self.assertEqual((got,crc),(mask,'12345678'))
    def test_reject_old_or_truncated_cdl(self):
        for invalid in (b'CDLv1'+bytes(4+PRG_SIZE+CHR_SIZE), b'CDLv2'+bytes(PRG_SIZE), b'CDLv2'+bytes(4+PRG_SIZE+CHR_SIZE-1)):
            with self.assertRaises(ValueError):decode_cdl(invalid)
    def test_code_data_flags(self):
        mask=bytearray(PRG_SIZE);mask[0]=1;mask[1]=2;mask[2]=3;mask[3]=5
        self.assertEqual(counts(mask),{'code':3,'data':2,'either':4,'both':1})
    def test_unknown_flags_no_auto_code(self):
        mask=bytes([0x80])*PRG_SIZE
        self.assertEqual(counts(mask),{'code':0,'data':0,'either':0,'both':0})
    def test_known_overlap(self):
        mask=bytearray(PRG_SIZE)
        for offset,length in CHECKPOINT_0501_REGIONS:
            for i in range(length):mask[offset+i]|=1
        self.assertEqual(known_overlap(mask)['code_0501_overlap'],4364)
    def test_known_overlap_rejects_wrong_len(self):
        with self.assertRaises(AssertionError):known_overlap(b'')
    def test_bank_counts(self):
        mask=bytearray(PRG_SIZE);mask[31*8192]=1;mask[0]=2
        b=bank_rows(mask)
        self.assertEqual([x['physical_PRG_bank'] for x in b],[0,31])
        self.assertEqual(b[1]['observed_code_bytes'],1)
    def test_log_parse_state_and_summary(self):
        text='\n'.join(json.dumps(x) for x in [
          {'event':'loaded','mesen_version':'2.1.1','console':'Nes'},
          {'event':'cdl_saved','type':'NesPrgRom'},
          {'event':'lua_log','error_count':0,'text':'STATE frame=3 s=04 00 00 03 00 00\n'},
          {'event':'summary','ok':True,'reason':'frame_limit','start_frame':500,'final_frame':510,'frames_executed':10}])
        summ,states=decode_log(text)
        self.assertEqual(summ['frames_executed'],10)
        self.assertEqual(states,[{'frame_in_segment':3,'18':4,'19':0,'68':0,'2C':3,'07A0':0,'07A6':0}])
    def test_log_fails_errors(self):
        text='\n'.join(json.dumps(x) for x in [
          {'event':'loaded','mesen_version':'2.1.1','console':'Nes'},
          {'event':'cdl_saved'},
          {'event':'lua_log','error_count':1,'text':'STATE frame=3 s=04 00 00 03 00 00\n'},
          {'event':'summary','ok':True,'reason':'frame_limit','start_frame':0,'final_frame':1,'frames_executed':1}])
        with self.assertRaises(ValueError):decode_log(text)
    def test_log_fails_wrong_source_version(self):
        text='\n'.join(json.dumps(x) for x in [
          {'event':'loaded','mesen_version':'0.0.0','console':'Nes'},
          {'event':'cdl_saved'},
          {'event':'lua_log','error_count':0,'text':'STATE frame=3 s=04 00 00 03 00 00\n'},
          {'event':'summary','ok':True,'reason':'frame_limit','start_frame':0,'final_frame':1,'frames_executed':1}])
        with self.assertRaises(ValueError):decode_log(text)
    def test_hash_data_is_copyright_safe(self):
        data=b'example original-data payload'
        self.assertEqual(sha(data),hashlib.sha256(data).hexdigest())
        self.assertNotIn('example',sha(data))

if __name__=='__main__':unittest.main(verbosity=2)
