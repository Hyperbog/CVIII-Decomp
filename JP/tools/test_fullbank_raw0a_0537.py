#!/usr/bin/env python3
"""0537 original-JP full physical raw0A integrity and structure regression."""
import argparse, tempfile
from pathlib import Path
from recover_raw0a_bank_0537 import (
    audit,smoke,read_baseline,candidate_source,structure_data,
    digest,BANK_SHA,LO,
)
from build_whole_cart_recomp_0529 import assemble,generate_sources


def run(rom_path:Path):
    rom=rom_path.read_bytes()
    with tempfile.TemporaryDirectory(prefix='jp-0537-') as temp:
        root=Path(temp);original=root/'original'
        generate_sources(rom,original)
        baseline=(original/'prg_raw0a.asm').read_text()
        output=root/'wholebank'
        report=audit(rom,baseline,output)
        cls=report['classification']
        expected=('audited_6502_opcode_operand_bytes',2162),('audited_pointer_and_data_bytes',168),('new_static_6502_candidate_bytes_NOT_CERTIFIED',2910),('structural_pointer_bytes_NOT_LIVE',966),('structural_fixed_record_bytes_NOT_LIVE',2057),('unresolved_bytes',8121)
        for key,value in expected:
            assert cls[key]==value,(key,cls[key],value)
        bank=rom[16+10*16384:16+11*16384]
        assert digest(bank)==BANK_SHA
        assert assemble((output/'raw0a_fullbank_0537.asm').read_text(),0x8000,0x4000)==bank
        classes,known,nodes,labels=read_baseline(bank,baseline)
        candidates,roots,rejected,_=candidate_source(bank,classes,known)
        assert len(roots)==82
        for pc,row in candidates.items():
            for i in range(row[2]):classes[pc+i-LO]=3
        source_nodes,original_tables=structure_data(bank,classes,candidates)
        assert sum(x['pointer_count'] for x in original_tables)==483
        assert sum(x['unique_records'] or 0 for x in original_tables)==460
        tests=0
        # Semantic integrity negatives without relying only on a whole-ROM SHA:
        for addr,value in ((0x92ae,0), (0x9f6e,0), (0xa56b,0)):
            corrupt=bytearray(bank);corrupt[addr-LO]=value
            mask,_known,_nodes,_labels=read_baseline(bank,baseline)
            for pc,row in candidates.items():
                for i in range(row[2]):mask[pc+i-LO]=3
            try:structure_data(bytes(corrupt),mask,candidates)
            except ValueError:tests+=1
            else:raise AssertionError(f'Mutated pointer structure not rejected ${addr:04X}')
        # Source assembly differs from ROM if a pointer value is corrupted.
        generated_source=(output/'raw0a_fullbank_0537.asm').read_text()
        damaged=generated_source.replace('.word $92CC','.word $92CD',1)
        assert damaged!=generated_source
        assert assemble(damaged,0x8000,0x4000)!=bank;tests+=1
        altered=bytearray(rom);altered[16+10*16384+(0x8047-LO)]^=1
        try:audit(bytes(altered),baseline,root/'bad-ROM')
        except ValueError:tests+=1
        else:raise AssertionError('Altered retail bank content accepted')
        assert tests==5
        print('PASS bank0A 16KiB complete exact reassembly; 5 substantive corruption negatives; 483 structure pointers / 460 distinct records')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path);p.add_argument('--smoke',action='store_true');a=p.parse_args()
    smoke()
    if a.rom:run(a.rom)
