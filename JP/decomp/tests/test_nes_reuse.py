#!/usr/bin/env python3
"""ROM-free source-of-truth tests + optional exact JP and US user-provided ROM."""
import json
from pathlib import Path
import sys
# This test lives under JP/decomp/tests, the standalone implementation under JP/tools.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import tempfile
import unittest
from nes_reuse import (OPCODES,MODES,anchored_compare,compare,fds_info,load,
                       nes2_size,normalized_instructions,sha,sliding_matches)

JP='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
US='1c7b2ed2c1fb5839a6764006aa476f5c9d48f99465b6141980f3a5af1dfec0d6'

def nrom(prg=16384,chr_=8192,trainer=False,nes2=False):
    h=bytearray(16);h[:4]=b'NES\x1a';h[4]=prg//16384;h[5]=chr_//8192
    h[6]=4 if trainer else 0
    h[7]=8 if nes2 else 0
    rom=bytes(h)+(b'\xff'*512 if trainer else b'')+bytes([i&255 for i in range(prg)])+b'\x55'*chr_
    return rom

class TestContainer(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup)
        self.path=Path(self.t.name)/'cart.nes'
    def write(self,data):self.path.write_bytes(data);return self.path
    def test_opcode_domain(self):
        self.assertEqual(len(OPCODES),151)
        self.assertEqual(sum(1 for m,mode in OPCODES.values() if MODES[mode]==3),48)
    def test_nrom16(self):
        info,prg=load(self.write(nrom()));self.assertEqual(info['mapper'],0)
        self.assertEqual(info['prg_bytes'],16384);self.assertEqual(info['chr_bytes'],8192)
        self.assertEqual(info['mirroring_header'],'horizontal')
        self.assertEqual(len(info['prg_8k_banks']),2)
        self.assertEqual(info['fixed_vectors']['reset'],'0xfdfc')
    def test_nrom32(self):
        a=bytearray(nrom(prg=32768));a[16+32768-4:16+32768-2]=b'\x0b\xe0'
        info,_=load(self.write(a));self.assertEqual(info['fixed_vectors']['reset'],'0xe00b')
    def test_mirroring_flag(self):
        b=bytearray(nrom());b[6]|=1
        info,_=load(self.write(b));self.assertEqual(info['mirroring_header'],'vertical')
    def test_trainer(self):
        info,prg=load(self.write(nrom(trainer=True)));self.assertEqual(info['trainer_bytes'],512)
        self.assertEqual(prg[:16],bytes(range(16)))
    def test_nes2_exp(self):
        self.assertEqual(nes2_size(0x19,15,16384),2**6*3)
        self.assertEqual(nes2_size(0x12,2,8192),0x212*8192)
    def test_nes2_mapper(self):
        b=bytearray(nrom(nes2=True));b[6]|=0x80;b[7]|=0x10;b[8]=0xB2
        i,_=load(self.write(b));self.assertEqual(i['format'],'NES2.0')
        self.assertEqual(i['mapper'],0x218);self.assertEqual(i['submapper'],11)
    def test_short_prg(self):
        with self.assertRaisesRegex(ValueError,'truncated'):
            load(self.write(nrom()[:-100]))
    def test_extra_bytes(self):
        x,_=load(self.write(nrom()+b'junk'));self.assertTrue(any('trailing' in s for s in x['warnings']))
    def test_dirty_header(self):
        x=bytearray(nrom());x[12]=ord('x')
        a,_=load(self.write(x));self.assertTrue(any('dirty' in s for s in a['warnings']))
    def test_fds_headered(self):
        a=fds_info(b'FDS\x1a'+bytes([2])+bytes(11)+bytes(65500*2))
        self.assertEqual((a['side_count'],a['format']),(2,'FDS-headered'))
    def test_fds_geometry_only(self):
        a=fds_info(bytes(65500));self.assertEqual(a['format'],'FDS-raw-candidate')
    def test_fds_bad_side_count(self):
        with self.assertRaisesRegex(ValueError,'side count'):
            fds_info(b'FDS\x1a'+bytes([4])+bytes(11)+bytes(65500))
    def test_fds_not_raw_audio(self):
        with self.assertRaisesRegex(ValueError,'unrecognized'):
            fds_info(bytes(66000))
    def test_norm_relocation(self):
        a=bytes.fromhex('a9 01 20 34 12 4c 78 56 d0 fa 85 10 60 ea ea ea')
        b=bytes.fromhex('a9 01 20 88 77 4c 11 a0 d0 fa 85 10 60 ea ea ea')
        x,n=normalized_instructions(a);y,m=normalized_instructions(b)
        self.assertEqual((n,m),(9,9));self.assertEqual(x,y)
        self.assertNotEqual(a,b)
    def test_norm_zp_not_masked(self):
        a=bytes.fromhex('a5 10 60 ea ea ea ea ea ea ea ea ea ea ea ea ea')
        b=bytes.fromhex('a5 11 60 ea ea ea ea ea ea ea ea ea ea ea ea ea')
        self.assertNotEqual(normalized_instructions(a)[0],normalized_instructions(b)[0])
    def test_norm_branch_preserved(self):
        a=bytes.fromhex('d0 fe 60 ea ea ea ea ea ea ea ea ea ea ea ea ea')
        b=bytes.fromhex('d0 fd 60 ea ea ea ea ea ea ea ea ea ea ea ea ea')
        self.assertNotEqual(normalized_instructions(a)[0],normalized_instructions(b)[0])
    def test_norm_invalid(self):
        with self.assertRaisesRegex(ValueError,'unsupported'):
            normalized_instructions(b'\x02'*16)
    def test_norm_truncated(self):
        with self.assertRaisesRegex(ValueError,'midway'):
            normalized_instructions(b'\x20\x55')
    def test_anchor(self):
        a=bytes.fromhex('a9 01 20 34 12 4c 78 56 d0 fa 85 10 60 ea ea ea')
        b=bytes.fromhex('a9 01 20 88 77 4c 11 a0 d0 fa 85 10 60 ea ea ea')
        r=anchored_compare(a,b,{'name':'demo','kind':'code','code_boundaries_verified':True,
            'left':{'prg_offset':0,'size':16,'sha256':sha(a)},
            'right':{'prg_offset':0,'size':16,'sha256':sha(b)}})
        self.assertFalse(r['exact_equal']);self.assertTrue(r['opcode_aligned_normalized_match'])
        self.assertEqual(r['promoted_semantic_bytes'],0)
    def test_anchor_need_proven_boundaries(self):
        a=b'\xea'*16;r=anchored_compare(a,a,{'kind':'code','left':{'prg_offset':0,'size':16},'right':{'prg_offset':0,'size':16}})
        self.assertIsNone(r['decoded_instruction_count'])
    def test_anchor_bad_hash(self):
        a=b'\xea'*16
        with self.assertRaisesRegex(ValueError,'fingerprint'):
            anchored_compare(a,a,{'left':{'prg_offset':0,'size':16,'sha256':'0'*64},'right':{'prg_offset':0,'size':16}})
    def test_low_entropy_rejected(self):
        a=b'\x00'*300
        r=sliding_matches(a,a,window=32,stride=64)
        self.assertEqual(r['candidate_windows_tested'],0)
    def test_window_higher_entropy(self):
        a=bytes(range(256))*2
        r=sliding_matches(a,a,window=32,stride=64)
        self.assertGreater(r['candidate_windows_with_any_match'],0)
        self.assertEqual(r['semantically_promoted_bytes'],0)
    def test_mapper24_vs26(self):
        a=bytearray(nrom(prg=32768));a[6]=0x80;a[7]=0x10
        # mapper 0x18 (24) requires low part 8 and upper high 0x10
        a[6]=0x80;a[7]=0x10
        b=bytearray(a);b[6]=0xA0
        self.assertEqual(load(self.write(a))[0]['mapper'],24)
        self.assertEqual(load(self.write(b))[0]['mapper'],26)

class TestOriginalRoms(unittest.TestCase):
    def test_pair_if_supplied(self):
        jp=Path(__file__).with_name('Akumajou Densetsu (Japan).nes')
        us=Path(__file__).with_name("Castlevania III - Dracula's Curse (USA).nes")
        if not (jp.is_file() and us.is_file()):self.skipTest('retail ROMs not required by CI')
        info,_=load(jp);self.assertEqual(info['file_sha256'],JP)
        self.assertEqual(info['mapper'],24)
        self.assertEqual(info['fixed_vectors'],{'nmi':'0xe057','reset':'0xe00b','irq':'0xe0f5'})
        j=compare(str(jp),str(us))
        self.assertEqual(j['left']['file_sha256'],JP)
        self.assertEqual(j['right']['file_sha256'],US)
        self.assertFalse(j['same_mapper'])
        self.assertGreater(j['exact_window_discovery']['candidate_windows_with_any_match'],100)
        self.assertEqual(j['strict_new_verified_bytes'],0)

if __name__=='__main__':unittest.main(verbosity=2)
