#!/usr/bin/env python3
"""ROM-free deterministic JP0672 audit tests; do not depend on private traces."""
import csv
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from jp0672_audio_cycle_audit import audit,mask_at,parse_native,parse_original,verify_session,M_CSV


def sample_native(rows):
    buf=io.StringIO();writer=csv.writer(buf,lineterminator='\n');writer.writerow(M_CSV)
    for cyc,reg,val in rows:
        writer.writerow([cyc,'2a03' if reg<0x9000 else 'vrc6','test',f'{reg:04X}',f'{val:02X}','00',0,0])
    return buf.getvalue()


def sample_mesen():
    return '\n'.join(['JP0668_READY v2','JP0668_BEGIN 7',
                      'JP0668_FRAME 1 27278','JP0668_POLL 1 2 27392 00',
                      'JP0668_WRITE 1 57234 4015 0F','JP0668_WRITE 2 57240 4017 C0',
                      'JP0668_FRAME 2 60000',
                      'JP0668_END 2 2 1 60000'])+'\n'


class AuditTests(unittest.TestCase):
    A=[(100,0x4015,0x0f),(106,0x4017,0xC0),(206,0x9000,0x55)]
    N=[(99,0x4015,0x0f),(105,0x4017,0xC0),(207,0x9000,0x55)]

    def test_equal_values_not_equal_cycles(self):
        s=audit(self.A,self.N)
        self.assertTrue(s['ordered_audio_register_and_value_match'])
        self.assertFalse(s['strict_unadjusted_cycle_timestamp_parity'])
        self.assertEqual(s['strict_exact_cycle_count'],0)
        self.assertEqual(s['adjacent_native_and_mesen_write_intervals_exact'],1)
        self.assertEqual(s['hypothetical_native_plus_one_phase_exact_count_UNCERTIFIED'],2)

    def test_exact_cycles_still_not_full_phase_proof(self):
        s=audit(self.A,self.A)
        self.assertTrue(s['strict_unadjusted_cycle_timestamp_parity'])
        self.assertFalse(s['cycle_phase_equivalence_proven'])
        self.assertFalse(s['cycle_exact_parity_certified'])

    def test_address_or_value_tamper_fails_closed(self):
        for k in [1,2]:
            data=list(self.N); t=list(data[k]);t[k%2+1]^=1;data[k]=tuple(t)
            with self.assertRaisesRegex(ValueError,'address/value mismatch'):
                audit(self.A,data)

    def test_count_mismatch_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'count unequal'):
            audit(self.A,self.N[:-1])

    def test_mask_windows(self):
        self.assertEqual([mask_at(i) for i in (89,90,92,93,370,460,470,475,476)],
                         [0,8,8,0,128,129,130,130,128])

    def test_original_parser(self):
        events,stats=parse_original(sample_mesen(),full=False)
        self.assertEqual(len(events),2)
        self.assertEqual((stats['frames'],stats['polls']),(2,1))

    def test_mesen_duplicate_write_or_cycle_raises(self):
        for corrupted in [sample_mesen().replace('WRITE 2','WRITE 1'),
                          sample_mesen().replace('57240','57230')]:
            with self.assertRaises(ValueError):parse_original(corrupted,full=False)

    def test_missing_pad_gate_fails_full_session(self):
        with self.assertRaises(ValueError):parse_original(sample_mesen(),full=True)

    def test_mesen_protocol_invalid_marker_raises(self):
        s=sample_mesen().replace('JP0668_END','JP0668_INVALID no_clock\nJP0668_END')
        with self.assertRaisesRegex(ValueError,'invalid or truncated'):
            parse_original(s,full=False)

    def test_native_csv_and_tamper(self):
        raw=sample_native(self.A)
        self.assertEqual(parse_native(raw),self.A)
        for edited in [raw.replace('2a03','vrc6',1),raw.replace('4015','4016',1),
                       raw.replace('100,','-1,',1),raw.replace(',00,0,0\n',',00,-2,0\n',1)]:
            with self.assertRaises(ValueError):parse_native(edited)

    def test_manifest_sha_and_epoch_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            d=Path(temp);sid='a'*32
            objects={'CVIII-Audio-Registers.csv':sample_native(self.A),
                     'CVIII-Sound-Requests.csv':'session_id,epoch\n',
                     'CVIII-Audio-Epochs.csv':'session_id,epoch,event,cycle,request_rows,register_rows\n'+sid+',0,power_on,0,0,0\n'}
            files={}
            for key,name in [('registers','CVIII-Audio-Registers.csv'),('requests','CVIII-Sound-Requests.csv'),('epochs','CVIII-Audio-Epochs.csv')]:
                v=objects[name].encode();(d/name).write_bytes(v)
                files[key]={'name':name,'sha256':hashlib.sha256(v).hexdigest()}
            (d/'CVIII-Audio-Session.json').write_text(json.dumps({'schema':'CVIII-JP-audio-session/v1','session_id':sid,'files':files}))
            self.assertTrue(verify_session(d)['native_epoch_verified'])
            (d/'CVIII-Sound-Requests.csv').write_text('tampered\n')
            with self.assertRaisesRegex(ValueError,'integrity'):verify_session(d)

if __name__=='__main__':unittest.main()