#!/usr/bin/env python3
"""Run 2357-site *compiled* bank0A output against independent original CPU.

--smoke: no original commercial ROM required (compile native output when present).
--rom: 1280 complete 2KiB-RAM room cases plus 135 bounded selector triples.
"""
from __future__ import annotations
import argparse,hashlib,json,subprocess,tempfile,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
SRC=ROOT/'JP/recomp/native/bank0a'
GEN=SRC/'generated/bank0a_compiled.cpp'
BANK_SHA='1460df577d44e114c64fdf34a8837629765f3f6a93d45796fdf81e5ffacb5ed8'
ROM_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'

def compile_native(compiler:str,out:Path)->None:
    subprocess.run([compiler,'-std=c++20','-O1','-Wall','-Wextra','-Werror','-pedantic',
                    '-I'+str(SRC),str(GEN),str(SRC/'static_bank0a_driver.cpp'),'-o',str(out)],check=True)

def bounded_cases(bank:bytes):
    def word(addr):return bank[addr-0x8000]|bank[addr-0x8000+1]<<8
    stage=[word(addr) for addr in range(0x92ae,0x92cc,2)]
    if len(stage)!=15:raise ValueError('expected 15 top-level pointers')
    sec=[];cases=[]
    for x,a in enumerate(stage):
        stop=stage[x+1] if x not in (8,14) else (0x9320 if x==8 else 0x9b20)
        for y,pos in enumerate(range(a,stop,2)):
            sec.append((x,y,word(pos)))
    if len(sec)!=64:raise ValueError('expected 64 second-level pointers')
    for n,(x,y,ptr) in enumerate(sec):
        limit=sec[n+1][2] if n not in (41,63) else (0x93cc if n==41 else 0x9b82)
        for z,addr in enumerate(range(ptr,limit,2)):
            cases.append((x,y,z,stage[x],ptr,word(addr)))
    if len(cases)!=135:raise ValueError('expected 135 leaf selectors')
    return cases

def main():
    p=argparse.ArgumentParser();p.add_argument('--smoke',action='store_true');p.add_argument('--rom',type=Path)
    p.add_argument('--source',type=Path);p.add_argument('--compiler',default='g++')
    a=p.parse_args()
    manifest=json.loads((SRC/'generated/bank0a_native_manifest.json').read_text())
    assert (manifest['audited_bytes'],manifest['candidate_bytes'],manifest['instruction_sites'])==(2162,2910,2357)
    assert manifest['candidate_code_certified'] is False and not manifest['native_frame_parity']
    assert GEN.is_file()
    with tempfile.TemporaryDirectory(prefix='jp-statically-compiled0a-') as d:
        d=Path(d);exe=d/'native';compile_native(a.compiler,exe)
        selftest=subprocess.run([str(exe),'--self-test'],capture_output=True,text=True,check=True)
        assert 'PASS fail-closed' in selftest.stdout
        # ROM-free negative: a missing physical bank image must never become a pass.
        assert subprocess.run([str(exe),str(d/'absent'),str(d/'absent')],capture_output=True).returncode!=0
        if a.rom is None:
            print('PASS 2357-site ROM-free compiled bank0A static lift; unresolved map remains fail-closed')
            return
        raw=a.rom.read_bytes()
        if len(raw)!=393232 or hashlib.sha256(raw).hexdigest()!=ROM_SHA:
            raise ValueError('original Japanese ROM fingerprint mismatch')
        bank0a=raw[16+10*16384:16+11*16384]
        bank0e=raw[16+14*16384:16+15*16384]
        if hashlib.sha256(bank0a).hexdigest()!=BANK_SHA:raise ValueError('bank0A sha mismatch')
        if a.source:
            from static_recompile_bank0a import source_cases,generate
            rows,counts=source_cases(a.source.read_text(),bank0a)
            assert len(rows)==2357
            if generate(rows)!=GEN.read_text(encoding="utf-8"):raise ValueError("committed source differs from original-bank static recompilation")
        f0=d/'raw0a.bin';f0.write_bytes(bank0a);f1=d/'raw0e.bin';f1.write_bytes(bank0e)
        result=subprocess.run([str(exe),str(f0),str(f1)],check=True,capture_output=True,text=True)
        output=[json.loads(v) for v in result.stdout.splitlines()]
        if len(output)!=1280:raise ValueError('native executable did not emit 1280 cases')
        # Existing independent original opcode interpreter, not a copy of the
        # C++ static lift. Its original JSRS and stack writes are byte-executed.
        from replay_room_loader_0540 import CPU
        src_prg=raw[16:16+262144]
        checked=0
        for idx in range(5):
            for seed in range(256):
                row=output[idx*256+seed];original=CPU(src_prg,idx,seed).run()
                if (row['room'],row['seed'])!=(idx,seed):raise ValueError('output case misordered')
                for field,expected in [('a',original.a),('x',original.x),('y',original.y),
                                       ('sp',original.sp),('mapper',original.bank),
                                       ('mapper_writes',len(original.mapper_writes))]:
                    if row[field]!=expected:raise ValueError(f'{idx}:{seed} {field} {row[field]} != {expected}')
                for flag,mask,expected in [('carry',1,original.c),('zero',2,original.z),('negative',128,original.n)]:
                    if bool(row['p']&mask)!=expected:raise ValueError(f'{idx}:{seed} flag {flag}')
                expected_reads=[[addr,v] for _,addr,_,v in original.read_0e]
                if row['mapped_reads']!=expected_reads:raise ValueError(f'{idx}:{seed} mapper read trace mismatch')
                if bytes(row['ram'])!=bytes(original.ram):
                    index=next(i for i,(left,right) in enumerate(zip(row['ram'],original.ram)) if left!=right)
                    raise ValueError(f'{idx}:{seed} RAM mismatch at ${index:04X}')
                checked+=1
        assert checked==1280
        # Candidate code opt-in is restricted to the 135 independently bounded
        # original $801E paths. Other candidate bytes remain uncertified.
        triples=bounded_cases(bank0a)
        case_file=d/'cases.csv';case_file.write_text(''.join(f'{x},{y},{z}\n' for x,y,z,_,_,_ in triples))
        result=subprocess.run([str(exe),str(f0),str(f1),str(case_file)],check=True,capture_output=True,text=True)
        actual=[[int(c) for c in row.split(',')] for row in result.stdout.splitlines()]
        if len(actual)!=135:raise ValueError('selector test missing paths')
        from test_raw0a_lookup_cpu import run as original_lookup
        for expected,got in zip(triples,actual):
            x,y,z,st,mid,end=expected
            if got!=list(expected):raise ValueError(f'compiled selector differs from independent table decoder at {expected}')
            original_st,original_mid,original_end,_=original_lookup(bank0a,x,y,z)
            if (original_st,original_mid,original_end)!=(st,mid,end):
                raise ValueError('original 6502 selector discrepancy')
        # Invalid/modified bank data are not treated as authenticated inputs.
        tampered=d/'damaged_bank.bin';tampered.write_bytes(bank0a[:-1]);assert subprocess.run(
            [str(exe),str(tampered),str(f1)],capture_output=True).returncode!=0
        print(f'PASS independent original-vs-statically-compiled bank0A: {checked}/1280 full RAM, registers, mapper traces; 135/135 pointer triples')

if __name__=='__main__':main()
