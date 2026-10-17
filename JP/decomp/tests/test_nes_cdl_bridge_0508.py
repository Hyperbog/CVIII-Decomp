#!/usr/bin/env python3
"""ROM-free synthetic regression; cannot certify execution or gameplay."""
from __future__ import annotations
import hashlib,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from nes_cdl_bridge_0508 import (CODE,DATA,INDIRECT_CODE,INDIRECT_DATA,PCM,
    MESEN_SUB_ENTRY,sha,require_hex32,decode_cdl,validated_manifest,top_runs,summarize,audit)

def make_rom():
    header=bytearray(b'NES\x1a'+bytes(12));header[4]=1;header[5]=1
    prg=bytes((i*13+17)%256 for i in range(16384))
    chr_=bytes((i*7+3)%256 for i in range(8192))
    return bytes(header)+prg+chr_

class TestCDL(unittest.TestCase):
    def setUp(self):
        self.rom=make_rom();self.prg=self.rom[16:16+16384]
        self.flags=bytearray(16384)
        self.flags[100:105]=bytes([CODE,CODE|DATA,DATA,INDIRECT_CODE,PCM])
        self.flags[110]=MESEN_SUB_ENTRY
        self.man={'schema':'nes-semantic-origin-regions/v1',
            'source_rom_sha256':sha(self.rom),'target_rom_sha256':'unrelated',
            'source_verified_checkpoint':'TEST','source_evidence':'synthetic only',
            'regions':[{'source_prg_offset':100,'size':5,'sha256':sha(self.prg[100:105])}],
            'total_certified_source_bytes':5}
    def meta(self,fmt='fceux',payload=None,**k):
        return decode_cdl(payload if payload is not None else bytes(self.flags),len(self.flags),8192,
                          codec=fmt,**k)
    def test_raw_prg_only(self):
        m=self.meta()[1];self.assertEqual(m['prg_flag_count'],16384)
        self.assertEqual(m['chr_flag_count'],0)
    def test_raw_prg_chr(self):
        flags,meta=self.meta(payload=bytes(self.flags)+bytes(8192))
        self.assertEqual((len(flags),meta['chr_flag_count']),(16384,8192))
    def test_mesen2_header_crc(self):
        payload=b'CDLv2'+(0x1234_5678).to_bytes(4,'little')+bytes(self.flags)
        flags,meta=self.meta(fmt='auto',payload=payload,expected_mesen_rom_crc32=0x12345678)
        self.assertEqual(flags,bytes(self.flags))
        self.assertEqual(meta['format'],'mesen2')
        self.assertTrue(meta['mesen2_rom_crc_verified_against_external_expected'])
    def test_mesen2_no_external_crc_is_unverified(self):
        payload=b'CDLv2'+(4).to_bytes(4,'little')+bytes(self.flags)
        _,meta=self.meta(fmt='auto',payload=payload)
        self.assertIn('UNVERIFIED',meta['log_image_identity_binding'])
    def test_mesen2_wrong_crc_rejected(self):
        payload=b'CDLv2'+(4).to_bytes(4,'little')+bytes(self.flags)
        with self.assertRaisesRegex(ValueError,'CRC does not match'):
            self.meta(fmt="auto",payload=payload,expected_mesen_rom_crc32=3)
    def test_mesen2_legacy_mismatch(self):
        with self.assertRaisesRegex(ValueError,'expected Mesen2'):
            self.meta(fmt='mesen2')
    def test_cd_lv2_not_read_as_raw(self):
        with self.assertRaisesRegex(ValueError,'cannot be read as raw'):
            self.meta(fmt='fceux',payload=b'CDLv2'+bytes(4)+bytes(self.flags))
    def test_truncated_header(self):
        with self.assertRaisesRegex(ValueError,'truncated'):
            self.meta(fmt="auto",payload=b'CDLv2'+bytes(2))
    def test_geometry_rejects_trainer_or_header(self):
        with self.assertRaisesRegex(ValueError,'payload length'):
            self.meta(payload=b'NES\x1a'+bytes(self.flags))
    def test_reject_extra_mesen_suffix(self):
        with self.assertRaisesRegex(ValueError,'payload length'):
            self.meta(fmt="auto",payload=b'CDLv2'+bytes(4)+bytes(self.flags)+bytes(4))
    def test_crc_hex_range(self):
        self.assertEqual(require_hex32('0xFF'),255)
        self.assertEqual(require_hex32('DEADBEEF'),0xDEADBEEF)
        with self.assertRaises(ValueError):require_hex32('100000000')
    def test_manifest_hash_and_overlap(self):
        m,meta=validated_manifest(self.man,self.prg,sha(self.rom))
        self.assertEqual(sum(m),5)
        self.assertEqual(meta['pinned_source_region_bytes'],5)
        bad={**self.man,'regions':[dict(self.man['regions'][0],sha256='0'*64)]}
        with self.assertRaisesRegex(ValueError,'SHA-256'):
            validated_manifest(bad,self.prg,sha(self.rom))
        bad={**self.man,'regions':self.man['regions']*2,'total_certified_source_bytes':10}
        with self.assertRaisesRegex(ValueError,'overlap'):
            validated_manifest(bad,self.prg,sha(self.rom))
    def test_manifest_wrong_image_and_bools(self):
        with self.assertRaisesRegex(ValueError,'identity'):
            validated_manifest(self.man,self.prg,'wrong')
        region=dict(self.man['regions'][0],size=True)
        with self.assertRaisesRegex(ValueError,'outside'):
            validated_manifest({**self.man,'regions':[region]},self.prg,sha(self.rom))
    def test_statistics_exact_counts(self):
        marked,meta=validated_manifest(self.man,self.prg,sha(self.rom))
        result=summarize(bytes(self.flags),marked,rom_sha=sha(self.rom),cdl_sha=sha(self.flags),
                         meta=self.meta()[1],manifest_info=meta)
        c=result['counts'];self.assertEqual(c['code_observed'],2)
        self.assertEqual(c['data_observed'],2)
        self.assertEqual(c['both_code_and_data'],1)
        self.assertEqual(c['manifest_bytes_also_logged_as_code'],2)
        self.assertEqual(c['manifest_bytes_logged_data_only'],1)
        self.assertEqual(c['manifest_bytes_not_observed'],2)
        self.assertEqual(c.get('code_bit_outside_pinned_manifest',0),0)
        self.assertEqual(c['bit7_tag_format_dependent'],1)
        self.assertEqual(result['policy']['strict_verified_prg_bytes_added'],0)
    def test_unknown_unobserved_not_unreachable(self):
        m=bytearray(len(self.flags))
        r=summarize(bytes(self.flags),m,rom_sha='a',cdl_sha='b',meta=self.meta()[1])
        self.assertTrue(r['policy']['unmarked_bytes_are_not_proven_unreachable'])
    def test_top_runs_physical_boundaries(self):
        flags=bytearray(16384)
        flags[8178:8207]=bytes([CODE])*29
        result=top_runs(flags,bytearray(len(flags)),cap=4,minimum=8)
        self.assertEqual([(x['physical_prg_offset'],x['byte_length']) for x in result],[(8192,15),(8178,14)])
    def test_runs_certified_excluded(self):
        flags=bytearray(16384);flags[100:125]=bytes([CODE])*25
        cert=bytearray(len(flags));cert[110:115]=bytes([1])*5
        runs=top_runs(flags,cert,minimum=5)
        self.assertEqual([x['byte_length'] for x in runs],[10,10])
    def test_real_io_synthetic_rom(self):
        with tempfile.TemporaryDirectory() as d:
            rom=Path(d)/'rom.nes';cdl=Path(d)/'log.cdl';mani=Path(d)/'manifest.json'
            rom.write_bytes(self.rom);cdl.write_bytes(bytes(self.flags));mani.write_text(json.dumps(self.man))
            r=audit(str(rom),str(cdl),manifest_path=str(mani),provenance='synthetic unittest')
            self.assertEqual(r['rom_mapper_id'],0)
            self.assertEqual(r['counts']['manifest_pinned_bytes'],5)
            self.assertEqual(r['imported_format']['format'],'fceux-or-mesen-legacy')
            self.assertNotIn('NES\x1a',json.dumps(r))
    def test_mesen_tag_format_specific(self):
        self.assertEqual(self.meta(fmt='mesen-legacy')[1]['flag7_interpretation'],
                         'Mesen subroutine entry marker')
        self.assertIn('reserved',self.meta(fmt='fceux')[1]['flag7_interpretation'])

if __name__=='__main__':unittest.main(verbosity=2)
