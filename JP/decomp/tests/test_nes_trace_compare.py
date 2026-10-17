#!/usr/bin/env python3
"""ROM-free parser/diff regressions for preinstruction CPU trace formats."""
import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from nes_trace_compare import parse_nestest,parse_json_line,compare
EX='C000  4C F5 C5  JMP $C5F5  A:00 X:00 Y:00 P:24 SP:FD PPU:  0, 21 CYC:7'

def cpu_row(pc='C000',a='00',p='24',bank=None,cycles=7):
    row={'pc':pc,'a':a,'x':'00','y':'00','p':p,'sp':'FD','cycles':cycles}
    if bank is not None:row['prg_bank']=bank
    return row

class TestTrace(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.r=Path(self.tmp.name)/'reference.log';self.c=Path(self.tmp.name)/'candidate.jsonl'
    def write(self,reference=EX,rows=None):
        self.r.write_text(reference+'\n')
        self.c.write_text(''.join(json.dumps(r)+'\n' for r in (rows if rows is not None else [cpu_row()])))
    def test_nestest_preinstruction(self):
        r=parse_nestest(EX)
        self.assertEqual((r['pc'],r['a'],r['sp'],r['cycles']),(0xc000,0,0xfd,7))
    def test_nestest_line_numbered(self):
        self.assertEqual(parse_nestest('3348: '+EX)['pc'],0xc000)
    def test_nestest_missing(self):
        with self.assertRaisesRegex(ValueError,'missing p'):
            parse_nestest(EX.replace('P:24','P2:24'))
    def test_json_hex_strings(self):
        self.assertEqual(parse_json_line(json.dumps(cpu_row()))['sp'],253)
    def test_json_int_numbers_are_decimal(self):
        d={k:0 for k in ('pc','a','x','y','p','sp')};d['pc']=49152
        self.assertEqual(parse_json_line(json.dumps(d))['pc'],49152)
    def test_json_reject_invalid(self):
        r=cpu_row();r['a']=300
        with self.assertRaisesRegex(ValueError,'out of range'):parse_json_line(json.dumps(r))
    def test_exact_match(self):
        self.write();x=compare(str(self.r),str(self.c))
        self.assertTrue(x['matched']);self.assertEqual(x['instruction_pairs_compared'],1)
        self.assertNotIn('4C F5',str(x))
    def test_reg_difference(self):
        self.write(rows=[cpu_row(a='01')]);x=compare(str(self.r),str(self.c))
        self.assertEqual(x['first_mismatch_instruction'],1)
        self.assertEqual(x['mismatches'][0]['fields'],['a'])
    def test_pc_difference(self):
        self.write(rows=[cpu_row(pc='C001')]);x=compare(str(self.r),str(self.c))
        self.assertEqual(x['mismatches'][0]['fields'],['pc'])
    def test_optional_cycle_check(self):
        self.write(rows=[cpu_row(cycles=8)])
        self.assertTrue(compare(str(self.r),str(self.c))['matched'])
        self.assertFalse(compare(str(self.r),str(self.c),compare_cycles=True)['matched'])
    def test_virtual_flags(self):
        self.write(rows=[cpu_row(p='34')])
        self.assertFalse(compare(str(self.r),str(self.c))['matched'])
        self.assertTrue(compare(str(self.r),str(self.c),ignore_virtual_p=True)['matched'])
    def test_length_mismatch(self):
        self.write(reference=EX+'\n'+EX)
        x=compare(str(self.r),str(self.c))
        self.assertEqual(x['disagreeing_or_unpaired_rows'],1)
    def test_bank_optional_only_both(self):
        self.write(rows=[cpu_row(bank=20)])
        self.assertTrue(compare(str(self.r),str(self.c))['matched'])
    def test_bank_checked_if_both(self):
        self.write(reference=json.dumps(cpu_row(bank=10)),rows=[cpu_row(bank=11)])
        x=compare(str(self.r),str(self.c),'jsonl','jsonl')
        self.assertFalse(x['matched']);self.assertIn('prg_bank',x['mismatches'][0]['fields'])
    def test_empty(self):
        self.write(reference='',rows=[])
        self.assertFalse(compare(str(self.r),str(self.c))['matched'])
    def test_bounded_examples(self):
        self.write(reference='\n'.join([EX]*20),rows=[cpu_row(a='ff')]*20)
        x=compare(str(self.r),str(self.c),limit_examples=4)
        self.assertEqual((len(x['mismatches']),x['disagreeing_or_unpaired_rows']),(4,20))
if __name__=='__main__':unittest.main(verbosity=2)
