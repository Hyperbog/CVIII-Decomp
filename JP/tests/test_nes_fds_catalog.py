#!/usr/bin/env python3
"""Synthetic ROM-free fixtures only; no commercial disk material."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import unittest
from nes_fds_catalog import catalog,FdsFormatError,FDS_SIDE,QD_SIDE

def sample(*,files=2,crc=False,hidden=False):
    out=bytearray()
    def b(payload):
        out.extend(payload)
        if crc:out.extend(b'\x00\x00') # words carried, NOT CRC-certified
    x=bytearray(56);x[0]=1;x[1:15]=b'*NINTENDO-HVC*';x[15]=0x7f;x[16:19]=b'TST';x[0x19]=2
    b(x);b(bytes((2,files)))
    for i in range(files+(1 if hidden else 0)):
        hdr=bytearray(16);hdr[0]=3;hdr[1]=i;hdr[2]=i;hdr[3:11]=f'FILE{i:04d}'.encode()
        hdr[11:13]=(0x6000+i).to_bytes(2,'little')
        data=(f'DATA{i}').encode();hdr[13:15]=len(data).to_bytes(2,'little')
        b(hdr);b(b'\x04'+data)
    size=QD_SIDE if crc else FDS_SIDE
    assert len(out)<size
    out+=bytes(size-len(out))
    return bytes(out)

class TestDisk(unittest.TestCase):
    def test_unheadered(self):
        s=catalog(sample())
        self.assertEqual(s['format'],'FDS-unheadered')
        self.assertEqual(s['sides'][0]['visible_file_count'],2)
        self.assertEqual(s['sides'][0]['files'][1]['load_address'],0x6001)
        self.assertEqual(s['sides'][0]['files'][1]['name'],'FILE0001')
        self.assertEqual(s['strict_verified_game_code_bytes'],0)
        self.assertTrue(s['no_payload_or_bios_exported'])
    def test_headered_multiside(self):
        s=catalog(b'FDS\x1a'+bytes((2,))+bytes(11)+sample()+sample(files=0))
        self.assertEqual(s['side_count'],2)
        self.assertEqual(s['sides'][1]['declared_file_count'],0)
    def test_header_count_zero_allowed(self):
        self.assertEqual(catalog(b'FDS\x1a'+bytes(12)+sample())['side_count'],1)
    def test_bad_count(self):
        with self.assertRaisesRegex(FdsFormatError,'side count'):
            catalog(b'FDS\x1a'+bytes((3,))+bytes(11)+sample())
    def test_invalid_signature(self):
        a=bytearray(sample());a[1]=0
        with self.assertRaisesRegex(FdsFormatError,'signature'):catalog(a)
    def test_wrong_block_2(self):
        a=bytearray(sample());a[56]=5
        with self.assertRaisesRegex(FdsFormatError,'block 2'):catalog(a)
    def test_wrong_data_marker(self):
        a=bytearray(sample());a[58+16]=0
        with self.assertRaisesRegex(FdsFormatError,'block 4'):catalog(a)
    def test_hidden_file(self):
        s=catalog(sample(hidden=True))['sides'][0]
        self.assertEqual(s['visible_file_count'],2)
        self.assertEqual(s['possible_hidden_file_count'],1)
        self.assertTrue(s['files'][2]['hidden_after_declared_count'])
    def test_qd_crc_word_space(self):
        s=catalog(sample(crc=True))
        self.assertEqual(s['format'],'QD-candidate')
        self.assertEqual(s['side_geometry_bytes'],QD_SIDE)
        self.assertTrue(s['sides'][0]['crc_word_bytes_present'])
        self.assertFalse(s['sides'][0]['crc_verified'])
    def test_huge_file_truncation(self):
        a=bytearray(sample());a[58+13:58+15]=b'\xff\xff'
        with self.assertRaisesRegex(FdsFormatError,'truncated'):catalog(a)
    def test_side_tail_nonz(self):
        a=bytearray(sample());a[-1]=7
        self.assertEqual(catalog(a)['sides'][0]['trailing_nonzero_bytes'],1)
    def test_raw_geometry_not_identity(self):
        with self.assertRaises(FdsFormatError):catalog(bytes(FDS_SIDE))
    def test_qd_invalid_signature(self):
        with self.assertRaisesRegex(FdsFormatError,'block 1'):catalog(bytes(QD_SIDE))
    def test_nonescaping_file_name(self):
        a=bytearray(sample());a[58+3]=1
        result=catalog(a)
        self.assertIn('\\x01',result['sides'][0]['files'][0]['name'])
        self.assertNotIn('DATA0',str(result))

if __name__=='__main__':unittest.main(verbosity=2)
