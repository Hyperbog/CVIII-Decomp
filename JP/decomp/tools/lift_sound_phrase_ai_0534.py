#!/usr/bin/env python3
"""0534 bounded original JP PRG sources: bank0C phrase table & 0504 AI graph.

This is a source transformation, not an increase in strict semantic PRG credit.
The 148-entry phrase table is a structurally evidenced *candidate*: original
bank0C interpreter has two actual LDA indexed consumers ($8B32/$8D0C), and
all 140 distinct targets refer to terminated within-bank streams. Exact
runtime index domains are NOT yet proved, so no strict new credit is claimed.
0504 AI opcode/data ranges are separately authenticated by original 0504
code/operand graph and per-physical-region SHA256 evidence.
"""
from __future__ import annotations
from collections import Counter, deque, defaultdict
import hashlib

JP_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
TABLE_START=0xA304
TABLE_SPLIT=0xA404
TABLE_END=0xA42C
STREAM_BEGIN=0xA42C
STREAM_END=0xA957
PHRASE_POINTER_COUNT=148
PHRASE_UNIQUE_ROOTS=140
SHA_TABLE='2c2b1d4a4f59c39c8ad46ad4b2c103055cf61911fdd3e68e104b1a5d2cfd8945'
SHA_STREAM='a35de62be83954e53e65ef149ee74d5e1f95e3d1999009bcf90221bd47e7e7b5'
SHA_ALL='1ebdf2d0e4a254644b3589aa0ace55789e597c6c2490b2e284284f54a73041b1'
# Authentic original 0504 fixed & bank0B code/operand and bounded ROM-table evidence.
# Source: JP/decomp/tools/audit_ai_script_seed_0504.py (original Git checkpoint 0504).
AI_RANGES='''fixed31 code FBF6 FC17 aef72125489106f46e5126d06c70468a12b2e5d3217bf5601856be437fa98ca6
fixed31 code FC1F FD4D a87fac16f29f6f4ff4d80238545a35cd78446118a02110784835f075d8809c90
fixed31 data FD4D FD59 19f7481bdd32ba4244331a4948e09d1e541eef9702976d4d46b62fab475225b4
raw0B code 807F 808F 872747bd9c7ae5b22d140e73f3b84d0eabf6907b4aed0edb9153ffdc5df3a78a
raw0B code 82C7 82CD 01d6ddd14ddb51aa5e3256683173fc2e4ce8f5d5d556b095a6fc649397908db7
raw0B code 8357 8363 3e3f9a6e7d3e43ad9c8b874723ac32a52f30cfafe5ab6aef218391b1b18dbf02
raw0B code 8519 8529 a9522c36a2015d6ca882339bda770889688cc98b93ea40692e99ffdaf6e60096
raw0B code 85E6 85FE 5fc395b6ecebef6e9de4ed33213afda0dd4959efd720b1730097d2a46e63fe9f
raw0B code 8EF7 8F16 4ce1f0d6ebc209b7fd6aa554315b502767dd36c81305849d860cd23dc22a0ecc
raw0B code 965D 968C cae6fc5dec7311f65c17145809a7aa15d401ec7f99e8fcc12ad2457593eefd19
raw0B code 96B4 96C5 2185fb411ee0675bb8113fe3da781a9a31bf4e420b5008d60c81a7538bbfb1d1
raw0B data 968C 96B4 ecee5e26c7787f38575a7c1b282135c9d53a91bd9bd15273cb3db3c9dbe02336
raw0B data B03A B046 86d624fa134201d5a290ea8668029dbab95f41a2e7717999144e12a70a1754d4
raw0B data BD7D BD7F 6193628a00b751aeaf2e188b4d29405346f1ec74da4528a6b110ddbfaf216de9
raw0B data BDF1 BDF5 d336e3b392df397fdb0cedfe097889a4e6b54d83a39efd7f6523c6c6809066a5
raw0B data BED9 BEDB c89c6b9852ba7db757b98b48dd2bf9d2ca9762247ec1aff4bf903aa5cb733435
'''


def sha(x):return hashlib.sha256(x).hexdigest()


def smoke():
    spans=[(tag,kind,int(a,16),int(e,16)) for tag,kind,a,e,_ in
           (line.split() for line in AI_RANGES.splitlines())]
    if (sum(e-a for tag,kind,a,e in spans),
        sum(e-a for tag,kind,a,e in spans if kind=='code'),
        sum(e-a for tag,kind,a,e in spans if kind=='data'))!=(576,504,72):
        raise ValueError('0504 original source byte accounting drift')
    if (TABLE_END-TABLE_START,STREAM_END-STREAM_BEGIN,STREAM_END-TABLE_START)!=(296,1323,1619):
        raise ValueError('0534 sound phrase table footprint drift')
    print('PASS 0534 ROM-free: 576 original 0504 source bytes and 1619 structured sound candidate bytes')


def source(prg):
    from audit_nmi_fixed_scheduler_banked import OPS,BR,TERM
    from lift_bank04_parser_0532 import fmt
    if len(prg)!=262144:raise ValueError('Original JP PRG requires 256KiB')
    b0b=prg[11*16384:12*16384]
    b0c=prg[12*16384:13*16384]
    fixed=prg[31*8192:32*8192]
    def read(bank,address,size=1):
        data={'raw0B':b0b,'raw0C':b0c,'fixed31':fixed}[bank]
        base=0xe000 if bank=='fixed31' else 0x8000
        if not base<=address<address+size<=base+len(data):
            raise ValueError('Bounded original source read escaped its physical mapper bank')
        return data[address-base:address-base+size]

    # A304 and A404 are real bank0C 6502 LDA abs,Y producer operands.
    # The selector domains are not bounded here: verified table structure is
    # deliberately NOT misreported as proven full runtime reachability.
    if read('raw0C',0x8b2c,13)!=bytes.fromhex('bd b7 01 0a a8 b9 04 a3 85 e2 b9 05 a3'):
        raise ValueError('Original bank0C first indexed phrase producer changed')
    if read('raw0C',0x8d06,13)!=bytes.fromhex('bd a5 06 0a a8 b9 04 a4 85 e2 b9 05 a4'):
        raise ValueError('Original bank0C second indexed phrase producer changed')
    if sha(read('raw0C',TABLE_START,TABLE_END-TABLE_START))!=SHA_TABLE or \
       sha(read('raw0C',STREAM_BEGIN,STREAM_END-STREAM_BEGIN))!=SHA_STREAM or \
       sha(read('raw0C',TABLE_START,STREAM_END-TABLE_START))!=SHA_ALL:
        raise ValueError('Original bank0C table/stream fingerprints changed')
    pointers=[int.from_bytes(read('raw0C',TABLE_START+i*2,2),'little')
              for i in range(PHRASE_POINTER_COUNT)]
    roots=sorted(set(pointers))
    if (len(pointers),len(roots),min(roots),max(roots))!=(148,140,0xa42c,0xa945):
        raise ValueError('Original phrase pointer population drift')
    if pointers!=sorted(pointers):raise ValueError('Original indexed sound pointers not monotone')
    if pointers[127]!=0xa865 or pointers[128]!=0xa865 or pointers[-1]!=0xa945:
        raise ValueError('Sound selector subtable transition changed')
    for i,p in enumerate(roots):
        e=roots[i+1] if i+1<len(roots) else STREAM_END
        if not STREAM_BEGIN<=p<e<=STREAM_END or read('raw0C',e-1)!=b'\xff':
            raise ValueError('Producer-addressed sound phrase not FF-delimited')
    lines=['; Original JP bank0C two indexed sound phrase pointer tables.',
           '; Pointer consumers: $8B32=>A304 and $8D0C=>A404.',
           '; 148 table entries/140 rooted FF-terminated phrases; bounds of',
           '; runtime index-producers are not certified by this structural audit.',
           'Bank0C_PhrasePointers_A304:']
    for a in range(TABLE_START,TABLE_SPLIT,16):
        i=(a-TABLE_START)//2
        lines.append('    .word '+','.join(f'Bank0C_Phrase_{p:04X}' for p in pointers[i:i+8]))
    lines.append('Bank0C_PhrasePointers_A404:')
    for a in range(TABLE_SPLIT,TABLE_END,16):
        i=(a-TABLE_START)//2
        lines.append('    .word '+','.join(f'Bank0C_Phrase_{p:04X}' for p in pointers[i:min(i+8,148)]))
    at=defaultdict(list)
    for i,p in enumerate(pointers):at[p].append(i)
    for i,p in enumerate(roots):
        e=roots[i+1] if i+1<len(roots) else STREAM_END
        lines.append(f'Bank0C_Phrase_{p:04X}: ; entry indices '+','.join(f'${n:02X}' for n in at[p]))
        for k in range(p,e,16):
            lines.append('    .byte '+','.join(f'${x:02X}' for x in read('raw0C',k,min(16,e-k))))
    parts={'raw0C':[{'a':TABLE_START,'b':STREAM_END,
                       'src':'0534 original bank0C 148-entry/140-phrase sound structure (unbounded selectors)',
                       'lines':lines}]}

    # Independently recover precisely the 0504 576-byte admitted opcode/data
    # graph, never linear-disassemble unrelated bank0B or fixed ROM bytes.
    from audit_ai_script_seed_0504 import graph as audited_graph
    b_code,b_covered,b_edges=audited_graph(b0b,0x8000,(0x8519,0x965d,0x96b4))
    f_code,f_covered,f_edges=audited_graph(fixed,0xe000,(0xfc1f,))
    if (len(b_code),len(b_covered),b_edges)!=(71,169,[(0x85f2,0xfc1f)]):
        raise ValueError('Original bank0B 0504 AI control flow changed')
    if (len(f_code),len(f_covered),f_edges)!=(185,335,[]):
        raise ValueError('Original fixed31 0504 AI control flow changed')
    byte_spans={'raw0B':{},'fixed31':{}}
    for line in AI_RANGES.splitlines():
        bank,kind,start,end,digest=line.split()
        a,e=int(start,16),int(end,16)
        if sha(read(bank,a,e-a))!=digest:
            raise ValueError(f'Original 0504 source {bank}:${a:04X} physical certificate mismatch')
        for x in range(a,e):
            if x in byte_spans[bank]:raise ValueError('Duplicate 0504 recovered byte')
            byte_spans[bank][x]=kind
    for bank,ins,covered in (('raw0B',b_code,b_covered),('fixed31',f_code,f_covered)):
        claimed_code={x for x,k in byte_spans[bank].items() if k=='code'}
        if claimed_code!=covered:raise ValueError('0504 strict code graph not exactly source-certified')
        labels={pc:f'Bank{bank[-2:]}_AI_{pc:04X}' for pc in ins
                if pc in ((0x8519,0x965d,0x96b4) if bank=='raw0B' else (0xfc1f,)) or
                any(k[3]==pc and k[0] in BR|{'JSR','JMP'} and k[1]!='ind'
                    for k in ins.values())}
        # Split into contiguous code / bounded data runs with zero gaps.
        regions=[];cur=None
        for address in sorted(byte_spans[bank]):
            kind=byte_spans[bank][address]
            if cur is None or cur['b']!=address or cur['kind']!=kind:
                cur={'a':address,'b':address,'kind':kind,'lines':[]}
                regions.append(cur)
            cur['b']=address+1
        for region in regions:
            a,e=region['a'],region['b']
            if region['kind']=='code':
                pc=a
                while pc<e:
                    if pc not in ins:raise ValueError('Fragment splits original 6502 instruction')
                    mn,mode,n,arg,_blob=ins[pc]
                    if pc in labels:region['lines'].append(labels[pc]+':')
                    # fmt produces NMOS mnemonic operand and target, local symbolic where proven.
                    region['lines'].append('    '+fmt(mn.lower(),mode,arg,labels))
                    pc+=n
                if pc!=e:raise ValueError('Instruction crosses authenticated interval')
            else:
                if bank=='raw0B' and a in (0xbd7d,0xbdf1):
                    for pc in range(a,e,2):
                        region['lines'].append('    .word '+
                            (labels.get(int.from_bytes(read(bank,pc,2),'little'),
                                        f'${int.from_bytes(read(bank,pc,2),"little"):04X}')))
                else:
                    for pc in range(a,e,16):
                        region['lines'].append('    .byte '+','.join(
                            f'${x:02X}' for x in read(bank,pc,min(16,e-pc))))
            region['src']='0504 original-JP certified bank0B AI opcode graph or bounded AI tables'
            del region['kind']
            parts.setdefault(bank,[]).append(region)
    mapped_0504=sum(r['b']-r['a'] for k,rs in parts.items() for r in rs if k!='raw0C')
    if mapped_0504!=576:raise ValueError('Expected exact 576-byte original AI lift')
    return parts,{
        'new_0504_verified_AI_instruction_count':256,
        'new_0504_6502_instruction_operand_bytes':504,
        'new_0504_typed_table_bytes':72,
        'new_0504_classified_source_bytes':576,
        'new_0534_sound_table_structural_candidate_bytes':1619,
        'sound_table_entries':148,'sound_phrase_distinct_roots':140,
        'sound_phrase_data_bytes':1323,'sound_pointer_table_bytes':296,
        'new_classified_total_including_structural_candidates':2195,
        'verified_code_or_bounded_data':576,
        'original_rom_fingerprints':{'sound_table':SHA_TABLE,'sound_stream':SHA_STREAM},
        'semantic_restriction':'Sound phrase index-domain bounds unproven; structural candidate only, no new strict coverage'}

