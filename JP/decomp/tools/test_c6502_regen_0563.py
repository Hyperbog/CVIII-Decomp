#!/usr/bin/env python3
"""JP 0563: private original JP ROM -> regenerated C11 -> 135 original 6502 replays.

The C executable and ROM-derived generated translation are temporary local
artifacts. No licensed game ROM or generated game-code artifact enters Git.
"""
from __future__ import annotations
import argparse,hashlib,json,subprocess,tempfile,shutil,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
TOOLS=ROOT/'JP/decomp/tools'
C=ROOT/'JP/recomp/native/c6502'

def smoke(compiler):
    from static_recompile_c_0562 import generate
    sample=[
       dict(pc=0x801e,category='audited',opcode=0xa5,arg=0x0034,next=0x8020),
       dict(pc=0x8020,category='candidate',opcode=0x0a,arg=0,next=0x8021)
    ]
    with tempfile.TemporaryDirectory(prefix='jp-c6502-regen-') as tmp:
        tmp=Path(tmp)
        gen=tmp/'generated.c'
        gen.write_text(generate(sample))
        subprocess.run([compiler,'-std=c11','-O1','-Wall','-Wextra','-Werror','-pedantic',
          '-I'+str(C),'-c',str(gen),'-o',str(tmp/'generated.o')],check=True)
        for invalid in ([sample[1],sample[0]], [dict(sample[0],category='unknown')]):
            try:generate(invalid)
            except ValueError:pass
            else:raise AssertionError('untrusted generator rows accepted')
        print('PASS ROM-free C11 static generation builds; unknown and unsorted rows rejected')

def original(rom,compiler):
    from static_recompile_c_0562 import main as _unused  # same source contract
    from static_recompile_c_0562 import generate
    from static_recompile_bank0a import source_cases,JP_SHA,BANK_SHA
    from build_fullbank_0a_source import build
    from build_whole_cart_recomp_0529 import assemble
    from test_static_bank0a_0552 import bounded_cases
    from test_raw0a_lookup_cpu import run as cpu_reference
    raw=rom.read_bytes()
    if len(raw)!=393232 or hashlib.sha256(raw).hexdigest()!=JP_SHA:
        raise ValueError('user supplied wrong Japanese original ROM')
    bank=raw[16+10*16384:16+11*16384]
    if hashlib.sha256(bank).hexdigest()!=BANK_SHA:raise ValueError('bank0A identity')
    with tempfile.TemporaryDirectory(prefix='jp-c6502-original-') as work:
        work=Path(work)
        out=work/'source'
        build(raw,out)
        source=(out/'banked/prg_raw0a.asm').read_text()
        if assemble(source,0x8000,0x4000)!=bank:
            raise ValueError('original raw0A source reconstruction failed')
        rows,counts=source_cases(source,bank)
        if len(rows)!=2357 or counts['audited_instructions']!=992:
            raise ValueError('native C source census drift')
        translated=work/'bank0a_compiled.c'
        translated.write_text(generate(rows))
        exe=work/'native-c6502'
        subprocess.run([compiler,'-std=c11','-O1','-Wall','-Wextra','-Werror',
            '-pedantic','-I'+str(C),str(C/'cpu.c'),
            str(C/'opcode_table.c'),str(C/'raw0a_driver_0563.c'),
            str(translated),'-o',str(exe)],check=True)
        cases=bounded_cases(bank)
        if len(cases)!=135:raise ValueError('selector inventory not exactly 135')
        csv=work/'cases.csv'
        csv.write_text(''.join(f'{x},{y},{z}\n' for x,y,z,*_ in cases))
        result=subprocess.run([str(exe),str(rom),str(csv)],capture_output=True,
                              text=True,check=True)
        actual=[tuple(int(v) for v in row.split(',')) for row in result.stdout.splitlines()]
        if len(actual)!=135:raise ValueError('native C generated code ran wrong case count')
        for i,(entry,result_row) in enumerate(zip(cases,actual)):
            x,y,z,p1,p2,p3=entry
            if result_row!=(x,y,z,p1,p2,p3):
                raise ValueError(f'Case {i}: native C {result_row} vs original table {entry}')
            origin1,origin2,origin3,_=cpu_reference(bank,x,y,z)
            if (origin1,origin2,origin3)!=(p1,p2,p3):
                raise ValueError(f'Case {i}: original 6502 disobeys source table')
        print('PASS authenticated original JP: 135/135 original 6502 vs C11 statically compiled bank0A selector, zero fallback calls')
        print(json.dumps({'original_sha256':JP_SHA,'compiled_sites':len(rows),
                          'independently_compared_selector_cases':135,
                          'fallback_instruction_count':0,'new_strict_prg_bytes':0,
                          'native_frame_parity':False},sort_keys=True))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--smoke',action='store_true')
    p.add_argument('--rom',type=Path)
    p.add_argument('--cc',default='cc')
    a=p.parse_args()
    if not shutil.which(a.cc):raise ValueError('C11 compiler not installed: '+a.cc)
    if a.smoke:smoke(a.cc)
    elif a.rom:original(a.rom.resolve(),a.cc)
    else:p.error('choose --smoke or --rom')
if __name__=='__main__':main()
