#!/usr/bin/env python3
"""ROM-locked cross-edition fixed-bank E7FB 6502 stack-dispatch fingerprint.

Identical instruction bytes are C1 structural evidence of a common local
algorithm, NOT proof of shared caller contexts, mapper state or live gameplay.
"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
from nes_reuse import OPCODES,MODES,anchored_compare,normalized_instructions
JP_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
US_SHA='1c7b2ed2c1fb5839a6764006aa476f5c9d48f99465b6141980f3a5af1dfec0d6'
CODE_SHA='d2adbf45aa9746eb53ba2e8ec8513cb338f8fd30f4bc3627074f186c14439091'
NEIGHBOR_SHA='49a31b22a09167c55a54fc9697817e67adde600d1fe8051ff3c8adc594d1c481'
JP_OFF=0x3e7fb;US_OFF=0x3e86d

def raw(path, expected):
    r=Path(path).read_bytes()
    assert len(r)==393232 and hashlib.sha256(r).hexdigest()==expected
    return r[16:16+262144]

def audit(jp,us):
    j=raw(jp,JP_SHA);u=raw(us,US_SHA)
    a=j[JP_OFF:JP_OFF+25];b=u[US_OFF:US_OFF+25]
    assert a==b and hashlib.sha256(a).hexdigest()==CODE_SHA
    decoded=[];p=0
    while p<len(a):
        op=a[p];name,mode=OPCODES[op];decoded.append((name,mode))
        p+=MODES[mode]
    assert p==25 and len(decoded)==15
    assert decoded==[
        ('ASL','a'),('STY','z'),('TAY','i'),('INY','i'),('PLA','i'),
        ('STA','z'),('PLA','i'),('STA','z'),('LDA','y'),('STA','z'),
        ('INY','i'),('LDA','y'),('LDY','z'),('STA','z'),('JMP','d')]
    assert a[-3]==0x6c  # jmp indirect through ZP $02
    assert normalized_instructions(a)[1]==15
    assert u.count(a)==1
    jp_start=0x3e7b8;us_start=0x3e82a;size=134
    x=j[jp_start:jp_start+size];y=u[us_start:us_start+size]
    assert x==y and hashlib.sha256(x).hexdigest()==NEIGHBOR_SHA
    assert j[jp_start-1]!=u[us_start-1] and j[jp_start+size]!=u[us_start+size]
    manifest={'name':'fixed_6502_inline_stack_dispatch_25','kind':'code',
        'code_boundaries_verified':True,
        'left':{'prg_offset':JP_OFF,'size':25,'sha256':CODE_SHA},
        'right':{'prg_offset':US_OFF,'size':25,'sha256':CODE_SHA}}
    anchor=anchored_compare(j,u,manifest)
    assert anchor['exact_equal'] and anchor['decoded_instruction_count']==15
    assert anchor['promoted_semantic_bytes']==0
    return {
        'evidence':'original-ROM-matched 15 official-opcode instruction/operand bytes; target runtime mapping/callers not proved',
        'jp_rom_sha256':JP_SHA,'us_rom_sha256':US_SHA,
        'routine':{'jp_prg_offset':JP_OFF,'jp_known_cpu_entry':'E7FB',
                   'us_prg_offset':US_OFF,'us_candidate_cpu_entry':'E86D',
                   'length':25,'instructions':15,'sha256':CODE_SHA,
                   'unique_occurrences_in_us_prg':1,'identical_bytes':True},
        'neighbor_exact_span':{'jp_prg_offset':jp_start,'us_prg_offset':us_start,
                   'length':size,'sha256':NEIGHBOR_SHA,
                   'code_data_semantics':'unclassified outside 25-byte anchored routine'},
        'candidate_function_transfer':'only local algorithm semantics with same register/stack/memory inputs',
        'remaining':['US MMC5 mapper state and whether PRG31 maps at CPU E86D',
                     'US original callers and pointer-table producer domains',
                     'gameplay liveness in either target/whole-frame parity',
                     'full code/data classification of neighboring 134-byte span'],
        'new_strict_prg_bytes':0,'vpp_delta':0
    }
if __name__=='__main__':
    x=audit(sys.argv[1],sys.argv[2]);Path(sys.argv[3]).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
    print('PASS: shared fixed dispatch 25 bytes, 15 official 6502 instructions, 134-neighbor candidate')
