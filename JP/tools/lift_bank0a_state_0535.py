#!/usr/bin/env python3
"""0535 original-JP bank0A sound state controller and bounded bank0C helpers.

Bank0A state entries come from the 12-entry table read by the original 0506
bank0A state-chain audit and are followed via 6502 control flow. Original
E7FB dispatcher calls are treated as opaque/inline-selector exits, not as
fall-through instructions. Bank0C helpers are *structural* source candidates:
$A992 has two raw01 JSR encodings, $A9D5 an original fixed31 JSR encoding,
and $A9C4 is their internal call target. Active VRC6 bank mapping at those
cross-bank call sites is NOT verified. No new strict PRG byte credit.
"""
from __future__ import annotations
from collections import deque
import hashlib

STATE_TABLE=0xB4D1
STATE_ENTRIES=(0xB570,0xB58C,0xB597,0xB5A3,0xB5CC,0xB5DA,
               0xB614,0xB622,0xB64E,0xB5CC,0xB5DA,0xB662)
STATE_SEEDS=frozenset((*STATE_ENTRIES,0xB4CC,0xB4E9,0xB689,0xB7F7))
STATE_RUNS=((0xB49A,0xB4B1),(0xB4CC,0xB4D1),
            (0xB4E9,0xB4EE),(0xB4FA,0xB502),
            (0xB570,0xB68E),(0xB7F7,0xB8A6))
HELPER_RUNS=((0xA992,0xA9E1),)
HELPER_TABLE=(0xA9E7,0xA9F9)
ORIGINAL_ROM_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
CODE_FOOTPRINT_SHA='781b127871ae47f933b045e06ced79405b29d72de00ef57f894216576a76e8c6'
TABLE_SHA='380ecdac9478f19215c9a5628e8395dce3a11ba951218f5f01583fa6dabdfa7c'
HELPERS_SHA='70f6e7472df2f6a92645563e2e2983a4a200f6cb16ad5e52ce5a47a602983ba0'
LOOKUP_SHA='bf9000adeaa463c4c5ccfb3455e153521ef53a37d59f1e3ee15d22cd074f2c19'


def sha(b):return hashlib.sha256(b).hexdigest()


def smoke():
    assert len(STATE_ENTRIES)==12 and len(set(STATE_ENTRIES))==10
    assert sum(b-a for a,b in STATE_RUNS)==502
    assert HELPER_RUNS==((0xA992,0xA9E1),)
    print('PASS 0535 ROM-free state roots and physical 6502 footprint contract')


def _walk(bank,roots,lo,hi,opaque=frozenset()):
    from audit_nmi_fixed_scheduler_banked import OPS,BR,TERM
    entries={};occupied={};external=[];q=deque(sorted(roots))
    while q:
        pc=q.popleft()
        if pc in entries:continue
        if not lo<=pc<hi:
            external.append(pc);continue
        op=bank[pc-0x8000]
        if op not in OPS:raise ValueError(f'Unknown NMOS opcode at ${pc:04X}')
        mn,mode,n=OPS[op];
        if pc+n>hi:raise ValueError(f'Instruction escaped bounded CPU window ${pc:04X}')
        raw=bank[pc-0x8000:pc+n-0x8000]
        v=None if n==1 else raw[1] if n==2 else int.from_bytes(raw[1:3],'little')
        if mode=='rel':v=(pc+2+(v if v<128 else v-256))&65535
        if any(x in occupied for x in range(pc,pc+n)):
            raise ValueError(f'6502 instruction/data or alternate-path overlap at ${pc:04X}')
        entries[pc]=(mn.lower(),mode,n,v)
        for x in range(pc,pc+n):occupied[x]=pc
        nxt=pc+n
        if mn in BR:q.extend((nxt,v))
        elif mn=='JSR':
            if v not in opaque:q.extend((nxt,v))
        elif mn=='JMP':
            if mode=='ind':external.append(('indirect',pc,v))
            else:q.append(v)
        elif mn not in TERM:q.append(nxt)
    return entries,occupied,external


def _regions(ins,banktag,src,roots):
    from lift_bank04_parser_0532 import fmt
    labels={p:f'{banktag}_{p:04X}' for p in ins if p in roots or any(
        mn in ('jsr','jmp','bpl','bmi','bvc','bvs','bcc','bcs','bne','beq')
        and mode!='ind' and operand==p for mn,mode,n,operand in ins.values())}
    runs=[];g=None
    for pc,(mn,mode,n,arg) in sorted(ins.items()):
        if g is None or g['b']!=pc:
            g={'a':pc,'b':pc,'src':src,'lines':[]};runs.append(g)
        if pc in labels:g['lines'].append(labels[pc]+':')
        g['lines'].append('    '+fmt(mn,mode,arg,labels));g['b']=pc+n
    return runs


def classify(prg):
    if len(prg)!=262144:raise ValueError('Expected exact original JP 256KiB PRG')
    b0a=prg[10*16384:11*16384]
    b0c=prg[12*16384:13*16384]
    b01=prg[1*16384:2*16384]
    fixed=prg[31*8192:32*8192]
    def read(b,a,n=1):
        if not 0x8000<=a<a+n<=0xC000:raise ValueError('Outside original VRC6 raw bank')
        return b[a-0x8000:a+n-0x8000]
    ptrs=tuple(int.from_bytes(read(b0a,STATE_TABLE+2*i,2),'little') for i in range(12))
    if ptrs!=STATE_ENTRIES or sha(read(b0a,STATE_TABLE,24))!=TABLE_SHA:
        raise ValueError('Original 0506 bank0A state table changed')
    # Authentic 0506 state-chain read and mapped B7F7 loader evidence.
    if read(b0a,0xB4CC,5)!=bytes.fromhex('a51920fbe7'):
        raise ValueError('0506 state table producer changed')
    if read(b0a,0xB689,5)!=bytes.fromhex('a56820fbe7'):
        raise ValueError('0506 state selector producer changed')
    if sha(read(b0a,0xB7F7,0x7C))!='068cd9f225e38a3b2f0b6e19717bfa11b73a68b9419854d684c42cf55d66d15d':
        raise ValueError('0506 original bank0A loader digest changed')
    ins,used,external=_walk(b0a,STATE_SEEDS,0x8000,0xC000,{0xE7FB})
    runs=_regions(ins,'Bank0A_State',
                  '0535 state-table rooted 0506 bank0A 6502 code (runtime bank context not asserted)',STATE_SEEDS)
    if (len(ins),len(used),tuple((x['a'],x['b']) for x in runs))!=\
       (244,502,STATE_RUNS) or sha(b''.join(read(b0a,a,e-a) for a,e in STATE_RUNS))!=CODE_FOOTPRINT_SHA:
        raise ValueError('0506 bank0A state CFG physical source spans changed')
    table_lines=['; Twelve original state-table words; selector bounds not promoted to runtime proof.',
                 'Bank0A_StatePointers_B4D1:',
                 '    .word '+','.join(f'Bank0A_State_{p:04X}' for p in ptrs[:6]),
                 '    .word '+','.join(f'Bank0A_State_{p:04X}' for p in ptrs[6:])]
    fragments={'raw0A':runs+[{'a':STATE_TABLE,'b':STATE_TABLE+24,
               'src':'0506 original state-pointer table (12 explicit .word entries)',
               'lines':table_lines}]}
    # The external sources are encodings, not certified active mapper states.
    if read(b01,0xAB88,3)!=bytes.fromhex('2092a9') or\
       read(b01,0xAB93,3)!=bytes.fromhex('2092a9') or\
       fixed[0xE39C-0xE000:0xE39F-0xE000]!=bytes.fromhex('20d5a9'):
        raise ValueError('Original bank0C helper cross-bank code entry candidate changed')
    rA,seenA,extA=_walk(b0c,{0xA992},0xA992,0xA9C4)
    rB,seenB,extB=_walk(b0c,{0xA9D5},0xA9C4,0xA9E1)
    if (len(rA),len(seenA),len(rB),len(seenB))!=(26,50,16,29):
        raise ValueError('0535 bounded 6502 helper CFG changed')
    if set(seenA)&set(seenB) or sha(read(b0c,0xA992,0x4f))!=HELPERS_SHA:
        raise ValueError('Bank0C helper disassembly overlap/fingerprint drift')
    insC={**rA,**rB}
    helper_regions=_regions(insC,'Bank0C_Helper',
        '0535 conditional bank0C 6502 helper entries from raw01/fixed pointer callers (mapper state unproven)',
        {0xA992,0xA9D5})
    if len(helper_regions)!=1 or (helper_regions[0]['a'],helper_regions[0]['b'])!=(0xA992,0xA9E1):
        raise ValueError('Helper source instruction boundary mismatch')
    # $A9C8 is a decoded bank0C LDA abs,Y addressing $A9E7. The value
    # population looks like pointers but the index domain remains unproved.
    if read(b0c,0xA9C8,3)!=bytes.fromhex('b9e7a9'):
        raise ValueError('Original bank0C lookup table consumer changed')
    table=[int.from_bytes(read(b0c,0xA9E7+2*i,2),'little') for i in range(9)]
    if table!=[0x962f,0x98cf,0x9756,0xb9f7,0xae26,0xbad6,0xba4d,0xbc63,0x87ea] or sha(read(b0c,0xA9E7,18))!=LOOKUP_SHA:
        raise ValueError('Original bank0C nine-word lookup candidate changed')
    helper_regions.append({'a':0xA9E7,'b':0xA9F9,
                           'src':'bank0C 9-word structurally recognized table $A9E7 (selector bounds unproven)',
                           'lines':['Bank0C_Lookup_A9E7:',
                                   '    .word '+','.join(f'${w:04X}' for w in table)]})
    fragments['raw0C']=helper_regions
    return fragments,{
        'bank0A_state_instructions':len(ins),
        'bank0A_state_instruction_bytes':len(used),
        'bank0A_state_table_bytes':24,
        'bank0A_0506_sources':{'root':'$B4CC','state_table':'$B4D1','initial_loaded_bank':'$0A',
                              'B7F7_7C_sha256':'068cd9f225e38a3b2f0b6e19717bfa11b73a68b9419854d684c42cf55d66d15d'},
        'bank0C_structural_helper_instruction_bytes':len(seenA)+len(seenB),
        'bank0C_structural_lookup_table_bytes':18,
        'state_cfg_external_fixed_edges':len(external),
        'classified_additional_bytes':502+24+79+18,
        'unresolved':['VRC6 mapper context at raw01/fixed helper call sites',
                      'bank0C indexed lookup selector bounds',
                      'E7FB state selection and live state domains']}
