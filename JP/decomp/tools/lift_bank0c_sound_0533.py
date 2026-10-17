#!/usr/bin/env python3
"""0533 original JP bank0C: metadata records, referenced sound streams, NMOS code.

Proof boundaries:
- 04F5 source-authenticated bank0C $8000-$91FF and its 1488-instruction CFG;
- 04F6 source-authenticated $9200-$9FFF (fingerprinted below);
- 125 bank0C $8F60 index pointers and 125 structurally bounded records;
- 125 producer-addressed bank0C local sound roots, $9541-$A303;
- 148-entry INTERNAL structural pointer-table candidate, kept OUT of strict
  semantic/verified classification, pending a live producer proof.
All emitted bytes are checked against the independent original ROM and the
whole-cartridge assembler; no strict-PRG or original-Mesen parity promotion.
"""
from __future__ import annotations
from collections import Counter, deque, defaultdict
import hashlib

ORIGINAL_JP_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
ROM0C_04F5_SPAN='2bd1badec12d9f68bf829c272105d85097966d6fb0419c206566eb54c7011734'
ROM0C_04F6_SPAN='d7387b04a03289ebb1a0567ef49240d90b0bb177a0c128c8b06dbccabdb0776f'
META_SHA='ff50c2a4cd6273ca001535a5e319a68526b7e0b7a1ab173b2ced00f5a32f7154'
STREAM_SHA='0df689b5769e50d65d736abe77cbe5752c2b6980de172164991ef32f78d38721'
META_TABLE_START=0x8f60
META_DESC_START=0x905a
META_VARIANT00_START=0x9505
LOCAL_SCRIPT_START=0x9541
LAST_SOUND_ROOT=0xa303
LOCAL_SOUND_END=0xa304  # $A303 is a producer-targeted $FF byte
INDIRECT_SITES={0x802e,0x83e1,0x842d,0x8641,0x8b10,0x8e1d}
ROOTS={
    0x833d,0x837e,0x83b7,0x85b3,0x83f8,0x840f,0x8456,0x845a,
    0x848c,0x849f,0x84ed,0x851d,0x852a,0x8444,0x86a9,0x86b4,
    0x86bf,0x8644,0x8668,0x869e,0x8b2c,0x8c16,0x8c2a,0x8c83,
    0x8e20,0x8e2a,0x8e34,0x8e3d,0x8e45,0x8e4b,
}
STAGE_REFS={4:102,5:84,12:139}


def sha(x):return hashlib.sha256(x).hexdigest()


def smoke():
    assert len(ROOTS)==30
    assert LOCAL_SOUND_END-LOCAL_SCRIPT_START==3523
    assert META_DESC_START-META_TABLE_START==250
    assert LOCAL_SCRIPT_START-META_TABLE_START==1505
    print('PASS 0533 bank0C static contract: 125 records, 1505 metadata bytes, 3523 source-addressed pool bytes')


def classify(prg):
    from lift_bank04_parser_0532 import fmt, BR, TERMINATE, PARSER_BEGIN, PARSER_END
    import audit_nmi_fixed_scheduler_banked as original_cfg
    if len(prg)!=262144:raise ValueError('JP cartridge must contain 256KiB PRG')
    b=prg[12*16384:13*16384]
    def read(a,n=1):
        if not (0x8000<=a<0xc000 and a+n<=0xc000):raise ValueError('PRG bank0C out-of-bounds read')
        return b[a-0x8000:a-0x8000+n]
    if sha(read(0x8000,0x1200))!=ROM0C_04F5_SPAN:
        raise ValueError('04F5 original-JP bank0C code/data checksum changed')
    if sha(read(0x9200,0xe00))!=ROM0C_04F6_SPAN:
        raise ValueError('04F6 original-JP bank0C source span checksum changed')
    if sha(read(META_TABLE_START,LOCAL_SCRIPT_START-META_TABLE_START))!=META_SHA:
        raise ValueError('Bank0C sound metadata source region fingerprint mismatch')
    if sha(read(LOCAL_SCRIPT_START,LOCAL_SOUND_END-LOCAL_SCRIPT_START))!=STREAM_SHA:
        raise ValueError('Bank0C producer-addressed sound stream fingerprint mismatch')
    if read(LAST_SOUND_ROOT)!=b'\xff':
        raise ValueError('Bank0C terminal producer root no longer $FF')

    # The original 04F5/04F6 auditors used the actual 30 proven indirect
    # dispatcher targets and start $89E2. Do not linearly disassemble beyond
    # the accepted original NMOS graph, and reject any code/data collision.
    starts={};queue=deque([0x89e2,*sorted(ROOTS)])
    while queue:
        pc=queue.popleft()
        if pc in starts or not 0x8000<=pc<0x9200:continue
        while pc not in starts and 0x8000<=pc<0x9200:
            op=read(pc)[0]
            if op not in original_cfg.OPS:raise ValueError(f'Unproved NMOS opcode bank0C ${pc:04X}')
            mn,mode,n=original_cfg.OPS[op];mn=mn.lower()
            if pc+n>0x9200:raise ValueError('Instruction operand outside 04F5 certified window')
            raw=read(pc,n)
            operand=None if n==1 else raw[1] if n==2 else raw[1]|raw[2]<<8
            if mode=='rel':operand=(pc+2+(operand if operand<128 else operand-256))&0xffff
            starts[pc]=(mn,mode,n,operand)
            next_pc=pc+n
            if mn=='jsr':
                if 0x8000<=operand<0x9200:queue.append(operand)
                pc=next_pc;continue
            if mn=='jmp':
                if mode=='ind':
                    if pc not in INDIRECT_SITES:raise ValueError('Unproved indirect dispatch site')
                elif 0x8000<=operand<0x9200:queue.append(operand)
                break
            if mn in TERMINATE:break
            if mn in BR:
                if 0x8000<=operand<0x9200:queue.append(operand)
                pc=next_pc;continue
            pc=next_pc
    if len(starts)!=1488 or {p for p,(m,mode,n,o) in starts.items() if m=='jmp' and mode=='ind'}!=INDIRECT_SITES:
        raise ValueError('04F5 authenticated interpreter CFG changed')
    # 0532 already assembles the matched shared parser from $8001-$87AD.
    # Only classify the novel instruction footprints after that boundary.
    code={}
    for pc,(mn,mode,n,arg) in starts.items():
        if pc<PARSER_END:continue
        for x in range(pc,pc+n):
            if x in code or x>=META_TABLE_START:raise ValueError('Unbounded or overlapping bank0C interpreter instruction')
            code[x]=pc
    new_instructions={pc:v for pc,v in starts.items() if pc>=PARSER_END}
    # External entry points, calls and branches within this owned graph have
    # symbolic labels. Other destinations remain numeric, never invented.
    entry=set(new_instructions)
    labels={pc:f'Bank0C_SoundEngine_{pc:04X}' for pc in new_instructions
            if pc==0x89e2 or pc in ROOTS or any(
                v[3]==pc and v[0] in ('jsr','jmp',*BR) and v[1]!='ind'
                for v in starts.values())}
    regions=[];region=None
    for pc,(mn,mode,n,arg) in sorted(new_instructions.items()):
        if region is None or region['b']!=pc:
            region={'a':pc,'b':pc,'src':'04F5 original source verified bank0C interpreter (NMOS 6502 CFG)', 'lines':[]}
            regions.append(region)
        if pc in labels:region['lines'].append(labels[pc]+':')
        region['lines'].append('    '+fmt(mn,mode,arg,labels))
        region['b']=pc+n
    if len(code)!=sum(len(range(r['a'],r['b'])) for r in regions):
        raise ValueError('CFG source fragment graph byte count changed')

    # Metadata pointer table is explicitly addressed by original parser code.
    ptrs=[int.from_bytes(read(META_TABLE_START+2*i,2),'little') for i in range(125)]
    if not (ptrs[0]==META_DESC_START and ptrs[-1]==0x953d and len(set(ptrs))==125):
        raise ValueError('Original bank0C sound metadata index changed')
    descriptors=[];references=[];entry_map={}
    for i,p in enumerate(ptrs):
        variant=read(p)[0]
        if i<110:
            if variant not in (4,5,12):raise ValueError('Original sound bank selector mismatch')
            count=read(p+1)[0]+1
            if not 1<=count<=6:raise ValueError('Unbounded sound record triplets')
            size=2+3*count
            payload=read(p,size)
            info=[]
            for j in range(count):
                mode=payload[2+3*j];dest=int.from_bytes(payload[3+3*j:5+3*j],'little')
                if not 0x8000<=dest<0xc000:raise ValueError('Original sound stream pointer escaped VRC6')
                if variant==12 and not LOCAL_SCRIPT_START<=dest<=LAST_SOUND_ROOT:
                    raise ValueError('Local sound root outside bounded stream pool')
                if variant in (4,5) and not 0x87ae<=dest<0xbf06:
                    raise ValueError('External script root outside audited bank04/05 ranges')
                references.append((i+1,variant,mode,dest));info.append((mode,dest))
        else:
            if variant!=0 or read(p+1)[0]!=9:raise ValueError('Special bank00 record variant changed')
            size=4;info=[]
        descriptors.append((i+1,p,size,variant,info))
        entry_map[p]=(i+1,variant)
    if [x[3] for x in descriptors].count(12)!=79 or [x[3] for x in descriptors].count(4)!=17 or [x[3] for x in descriptors].count(5)!=14:
        raise ValueError('Bank0C sound metadata bank distribution drift')
    if Counter(b for _,b,m,a in references)!=Counter(STAGE_REFS):
        raise ValueError('Metadata producer reference distribution changed')
    # Physical metadata descriptors must occupy the entire $905A-$9540
    # range exactly once; special bank00 records are four-byte variants.
    covered=bytearray(LOCAL_SCRIPT_START-META_DESC_START)
    for sid,p,size,variant,info in descriptors:
        for at in range(p,p+size):
            off=at-META_DESC_START
            if off<0 or off>=len(covered) or covered[off]:raise ValueError('Descriptor span overlap')
            covered[off]=1
    if not all(covered):raise ValueError('Unknown gaps inside original metadata records')
    descriptors.sort(key=lambda x:x[1])
    meta=['; Original bank0C source indexed sound record table: 125 producer-pointer entries.',
          '; $8F60-$9059: 125 .word metadata headers, $905A-$9540: bounded descriptors.',
          '; Sound bank04/05 CPU pointer targets refer to OTHER physical PRG banks.']
    for i in range(0,125,8):
        meta.append('    .word '+','.join(f'Bank0C_Record_{p:04X}' for p in ptrs[i:i+8]))
    for sid,p,size,variant,info in descriptors:
        meta.append(f'Bank0C_Record_{p:04X}: ; original sound ID ${sid:02X}; bank ${variant:02X}')
        if variant==0:
            meta.append('    .byte $00,$09')
            meta.append('    .word $%04X'%int.from_bytes(read(p+2,2),'little'))
        else:
            meta.append(f'    .byte ${variant:02X},${len(info)-1:02X}')
            for mode,dest in info:
                meta.append(f'    .byte ${mode:02X}')
                meta.append(('    .word Bank0C_Stream_%04X'%dest) if variant==12
                            else ('    .word $%04X ; bank%02X rooted stream'%(dest,variant)))
    regions.append({'a':META_TABLE_START,'b':LOCAL_SCRIPT_START,
                    'src':'original $8F60 125 sound-record pointer table + 125 bounded indexed headers',
                    'lines':meta})
    roots=sorted({dest for _,bank,mode,dest in references if bank==12})
    if len(roots)!=125 or roots[0]!=LOCAL_SCRIPT_START or roots[-1]!=LAST_SOUND_ROOT:
        raise ValueError('Bank0C original producer-root inventory changed')
    at_addr=defaultdict(list)
    for sid,bank,mode,dest in references:
        if bank==12:at_addr[dest].append((sid,mode))
    lines=['; Original bank0C producer-addressed sound stream pool, NOT 6502 code.',
           '; 139 source header references resolve to 125 roots; command decoding remains open.',
           '; Ending $A303 is itself a referenced $FF byte.']
    for i,a in enumerate(roots):
        end=roots[i+1] if i+1<len(roots) else LOCAL_SOUND_END
        lines.append('; ID/mode: '+', '.join(f'${sid:02X}/${mode:02X}' for sid,mode in at_addr[a]))
        lines.append(f'Bank0C_Stream_{a:04X}:')
        for k in range(a,end,16):
            lines.append('    .byte '+','.join(f'${x:02X}' for x in read(k,min(16,end-k))))
    regions.append({'a':LOCAL_SCRIPT_START,'b':LOCAL_SOUND_END,
                    'src':'producer-linked bank0C sound byte streams (payload not fully parsed)',
                    'lines':lines})
    stats={'source_interpreter_instructions':len(new_instructions),
           'source_interpreter_6502_opcode_operand_bytes':len(code),
           'source_metadata_index_bytes':250,
           'source_metadata_descriptor_bytes':LOCAL_SCRIPT_START-META_DESC_START,
           'source_metadata_total_bytes':LOCAL_SCRIPT_START-META_TABLE_START,
           'source_producer_addressed_local_sound_pool_bytes':LOCAL_SOUND_END-LOCAL_SCRIPT_START,
           'original_sound_header_count':125,
           'triplet_sound_records':110,
           'special_bank00_record_count':15,
           'original_sound_producer_ref_count':len(references),
           'original_sound_source_roots':len(roots),
           'cross_bank_reference_histogram':dict(sorted(Counter(b for _,b,_,_ in references).items())),
           'source_04F5_sha256':ROM0C_04F5_SPAN,
           'source_04F6_sha256':ROM0C_04F6_SPAN,
           'fully_decoded_6502_only':len(code),
           'new_classified_bytes':len(code)+LOCAL_SOUND_END-META_TABLE_START,
           'classification_note':'Metadata structure and pointed-to script byte pool; command-by-command script semantics not asserted; no new strict credit.'}
    return regions,stats
