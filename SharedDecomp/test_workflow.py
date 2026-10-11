"""ROM-free cross-project CI: positive fixtures and deliberate corruption."""
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from workflow import (EvidenceError, attempt_update, context_packet,
                      trace_diff, validate_bank, validate_cfg, sha)

SAMPLE = bytes.fromhex('a9 01 85 10 60 ff ff ff')


def sample_map():
    return {"schema_version":1,
        "bank":{"physical_id":"NES:raw0A", "cpu_base":"8000", "size":8,"sha256":sha(SAMPLE)},
        "segments":[
          {"start":"8000", "end_exclusive":"8005", "type":"code", "evidence":"STATIC_PROVED",
           "source":"audit-mocked-fixture","sha256":sha(SAMPLE[:5])},
          {"start":"8005", "end_exclusive":"8008", "type":"unknown", "evidence":"RAW_FALLBACK"} ]}


class BankTests(unittest.TestCase):
    def test_exact_bank(self):
        r=validate_bank(sample_map(),SAMPLE)
        self.assertEqual((r['verified_instruction_bytes'],r['raw_fallback_bytes'],r['proven_semantic_bytes']),(5,3,5))
        self.assertFalse(r['parity_proved'])

    def test_unverified_not_promoted(self):
        d=sample_map();d['segments'][0].update(evidence='STRUCTURAL_CANDIDATE',source='')
        r=validate_bank(d,SAMPLE)
        self.assertEqual(r['verified_instruction_bytes'],0)
        self.assertEqual(r['structural_or_unverified_bytes'],5)

    def test_gap(self):
        d=sample_map();d['segments'][1]['start']='8006'
        with self.assertRaisesRegex(EvidenceError,'gap/overlap'):validate_bank(d,SAMPLE)

    def test_overlap(self):
        d=sample_map();d['segments'][1]['start']='8004'
        with self.assertRaisesRegex(EvidenceError,'gap/overlap'):validate_bank(d,SAMPLE)

    def test_missing_tail(self):
        d=sample_map();d['segments'].pop()
        with self.assertRaisesRegex(EvidenceError,'incomplete'):validate_bank(d,SAMPLE)

    def test_sha_original_mismatch(self):
        with self.assertRaisesRegex(EvidenceError,'SHA256 mismatch'):validate_bank(sample_map(),SAMPLE[:-1]+b'\x00')

    def test_segment_sha_mismatch(self):
        d=sample_map();d['segments'][0]['sha256']='0'*64
        with self.assertRaisesRegex(EvidenceError,'segment 0: hash mismatch'):validate_bank(d,SAMPLE)

    def test_missing_original_provenance(self):
        d=sample_map();d['segments'][0]['source']=''
        with self.assertRaisesRegex(EvidenceError,'source reference'):validate_bank(d)

    def test_trace_needs_scenario(self):
        d=sample_map();d['segments'][0]['evidence']='TRACE_EXECUTED'
        with self.assertRaisesRegex(EvidenceError,'scenario'):validate_bank(d)
        d['segments'][0]['scenario']='testrun-001'
        self.assertEqual(validate_bank(d)['verified_instruction_bytes'],5)

    def test_raw_fallback_not_code(self):
        d=sample_map();d['segments'][1].update(type='code')
        with self.assertRaisesRegex(EvidenceError,'raw fallback'):validate_bank(d)

    def test_full_window(self):
        d=sample_map();d['bank']['cpu_base']='FFFE'
        with self.assertRaisesRegex(EvidenceError,'CPU mapped window'):validate_bank(d)


class CFGTests(unittest.TestCase):
    def setUp(self):
        self.graph={"schema_version":1,"roots":["raw0A:8000"],
          "nodes":[{"id":"raw0A:8000","physical_bank":"NES:raw0A","start":"8000","end_exclusive":"8003"},
                   {"id":"raw0A:8003","physical_bank":"NES:raw0A","start":"8003","end_exclusive":"8005"}],
          "edges":[{"source":"raw0A:8000","target":"raw0A:8003","status":"resolved"},
                   {"source":"raw0A:8003","target":None,"status":"unresolved","reason":"indirect jump producer unknown"}]}

    def test_open_not_fully_closed(self):
        r=validate_cfg(self.graph,sample_map())
        self.assertEqual(r['open_edges'],1)
        self.assertFalse(r['fully_closed'])

    def test_bad_edge(self):
        self.graph['edges'][0]['target']='raw0A:DEAD'
        with self.assertRaisesRegex(EvidenceError,'target not mapped'):validate_cfg(self.graph)

    def test_missing_reason(self):
        self.graph['edges'][1]['reason']=''
        with self.assertRaisesRegex(EvidenceError,'needs reason'):validate_cfg(self.graph)

    def test_same_bank_overlap(self):
        self.graph['nodes'][1]['start']='8002'
        with self.assertRaisesRegex(EvidenceError,'overlapping'):validate_cfg(self.graph)

    def test_alias_in_other_bank_ok(self):
        self.graph['nodes'][1]['physical_bank']='NES:raw0B'
        self.assertEqual(validate_cfg(self.graph)['nodes'],2)

    def test_malformed_root(self):
        self.graph['roots']=['unknown']
        with self.assertRaisesRegex(EvidenceError,'root unknown'):validate_cfg(self.graph)


class TraceTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.ref=Path(self.t.name)/'ref.jsonl'
        self.nat=Path(self.t.name)/'native.jsonl'
        self.frames=[{"step":0,"physical_bank":"raw0A","pc":"801E","regs":{"A":1},"mapper":{"prg":"0A"},"ram_writes":[]},
                     {"step":1,"physical_bank":"raw0A","pc":"8021","regs":{"A":2},"mapper":{"prg":"0A"},"ram_writes":[{"addr":"0004","value":"A0"}]}]
        self.put(self.ref,self.frames)
        self.put(self.nat,self.frames)

    def put(self,path,rows):
        path.write_text(''.join(json.dumps(x)+'\n' for x in rows),encoding='utf-8')

    def test_matched(self):
        self.assertEqual(trace_diff(self.ref,self.nat)['matched_steps'],2)

    def test_first_divergence(self):
        mutated=copy.deepcopy(self.frames);mutated[1]['regs']['A']=99
        self.put(self.nat,mutated)
        r=trace_diff(self.ref,self.nat)
        self.assertEqual((r['status'],r['matched_steps'],r['field'],r['first_divergence_step']),('FAIL',1,'regs',1))

    def test_mapper_mismatch_caught(self):
        mutated=copy.deepcopy(self.frames);mutated[0]['mapper']['prg']='0B'
        self.put(self.nat,mutated)
        self.assertEqual(trace_diff(self.ref,self.nat)['field'],'mapper')

    def test_truncated(self):
        self.put(self.nat,self.frames[:1]);self.assertEqual(trace_diff(self.ref,self.nat)['field'],'trace_length')

    def test_empty_rejected(self):
        self.put(self.ref,[]);self.put(self.nat,[])
        with self.assertRaisesRegex(EvidenceError,'empty traces'):trace_diff(self.ref,self.nat)

    def test_nondeterministic_time_ignored(self):
        mutated=copy.deepcopy(self.frames);mutated[0]['wall_time']='sometimes'
        self.put(self.nat,mutated)
        self.assertEqual(trace_diff(self.ref,self.nat)['status'],'PASS')


class AgentTests(unittest.TestCase):
    def test_three_strikes_per_hypothesis(self):
        x=None
        for value in (0.5,0.4,0.5,0.3):
            x=attempt_update(x,value,hypothesis='bank0a-room-native')
        self.assertEqual((x['action'],x['best_score'],x['no_improvement']),('STOP_AND_DIAGNOSE',0.5,3))
        x=attempt_update(x,0.55,hypothesis='bank0a-room-native')
        self.assertEqual(x['action'],'CONTINUE')
        self.assertEqual(x['no_improvement'],0)

    def test_other_hypothesis_requires_ledger(self):
        x=attempt_update(None,0.1,hypothesis='one')
        with self.assertRaisesRegex(EvidenceError,'hypothesis changed'):attempt_update(x,.2,hypothesis='two')

    def test_context_small_and_identified(self):
        packet=context_packet(sample_map(),cpu=0x8004,radius=3,max_segments=1)
        self.assertTrue(packet['truncated'])
        self.assertEqual(packet['physical_bank'],'NES:raw0A')
        self.assertEqual(len(packet['segments']),1)

    def test_cli_no_false_parity(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'map.json';path.write_text(json.dumps(sample_map()))
            proc=subprocess.run([sys.executable,str(Path(__file__).with_name('workflow.py')),'bank',str(path)],capture_output=True,text=True)
            self.assertEqual(proc.returncode,0,proc.stderr)
            self.assertFalse(json.loads(proc.stdout)['parity_proved'])

if __name__=='__main__':unittest.main()
