#!/usr/bin/env python3
"""Recover the complete three-level room-data pointer hierarchy in JP raw bank 0A.

Only graph-local, structurally verified data is classified. The 0537 static
instruction candidates remain unproved. The contiguous leaf arrays retain
explicit 4-byte and 7-byte record boundaries, without inventing field names.

This pass covers every original PRG byte in the same 16 KiB bank source and
provides a selectable source replacement for the whole-cartridge assembler.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

from build_whole_cart_recomp_0529 import assemble, mnemonic
import recover_raw0a_bank_0537 as base
from test_raw0a_lookup_cpu import run as run_lookup_cpu

START, END = 0x8000, 0xC000
REGIONS = {
    'level1': ((0x92AE, 0x92CC),),
    'level2': ((0x92CC, 0x9320), (0x9AF4, 0x9B20)),
    'level3': ((0x9320, 0x93CC), (0x9B20, 0x9B82)),
    'cells4': ((0x93CC, 0x9AF4), (0x9B82, 0x9F6E)),
    'records7': ((0xAB1F, 0xAFA4),),
}
CODE_SHA = '1460df577d44e114c64fdf34a8837629765f3f6a93d45796fdf81e5ffacb5ed8'


def rd(bank: bytes, cpu: int, size: int = 1) -> bytes:
    if not START <= cpu or cpu + size > END: raise ValueError('bank-local read outside bank')
    return bank[cpu-START:cpu-START+size]


def word(bank: bytes, cpu: int) -> int:
    return int.from_bytes(rd(bank, cpu, 2), 'little')


def checked_claim(classes: bytearray, nodes: dict, cpu: int, payload: str, length: int, kind: int):
    if not 0 <= cpu - START and cpu + length <= END:
        raise ValueError('node out of bounds')
    if any(classes[x-START] for x in range(cpu,cpu+length)):
        raise ValueError(f'Overlapping source classification at ${cpu:04X}')
    if cpu in nodes: raise ValueError(f'Duplicate record start at ${cpu:04X}')
    nodes[cpu] = (length,payload)
    for x in range(cpu,cpu+length):classes[x-START]=kind


def lookup(bank: bytes, a: int, b: int, limit: int):
    p=[word(bank,x) for x in range(a,b,2)]
    if len(set(p))!=len(p):
        # The two second-level lists have unique pointers. Third-level lists
        # are permitted to share a leaf or 7-byte stream root.
        raise ValueError('Repeated pointer where distinct table root expected')
    if not all(p[i]<p[i+1] for i in range(len(p)-1)):
        raise ValueError('Nested table boundary pointers not increasing')
    if p[0]!=b or p[-1]>=limit:
        raise ValueError('Nested pointer table not adjacent to its payload')
    return p


def classify(bank: bytes, baseline: str, strict_identity: bool = True) -> dict:
    if len(bank)!=0x4000:
        raise ValueError('Raw bank 0A must be exactly 16KiB')
    if strict_identity and hashlib.sha256(bank).hexdigest()!=CODE_SHA:
        raise ValueError('Original JP raw bank 0A SHA mismatch')
    if strict_identity and assemble(baseline, START, 0x4000)!=bank:
        raise ValueError('Input 0536 bank source does not match original bytes')

    # Repeat the 0537 bank-wide static work and preserve its evidence labels.
    classes, known, nodes, labels = base.read_baseline(bank, baseline)
    candidates, accepted, rejected, raw_sources = base.candidate_source(bank, classes, known)
    for pc,row in candidates.items():
        for off in range(row[2]):
            if classes[pc+off-START]: raise ValueError('Candidate overlaps proven source')
            classes[pc+off-START]=3
    table_nodes, table_evidence = base.structure_data(bank, classes, candidates)
    nodes.update(table_nodes)

    # This is the actual bank0A CPU routine selecting three hierarchical
    # indices through $34, $35, $36, and writing leaf pointer $95/$96.
    routine = bytes.fromhex(
        'a5340aa8b9ae928506b9af928507a5350aa8b1068504c8b1068505'
        'a5360aa8b1048595c8b104859660'
    )
    if rd(bank,0x801E,len(routine))!=routine:
        raise ValueError('Triple-indirect $801E selector instruction drift')
    if 0x801E not in candidates: raise ValueError('Selector source not in audited/candidate graph')

    # Hierarchy: 15 outer pointers -> 64 second-level pointer slots ->
    # 135 third-level pointer slots -> 113 four-byte payload roots and 16
    # seven-byte streams. It is not an emulated proof of gameplay liveness.
    stage_roots=[word(bank,p) for p in range(0x92AE,0x92CC,2)]
    assert len(stage_roots)==15
    if stage_roots != sorted(stage_roots) or stage_roots[0]!=0x92CC or stage_roots[8]!=0x9316 or stage_roots[9]!=0x9AF4 or stage_roots[-1]!=0x9B1A:
        raise ValueError('First-level selector group roots changed')
    pairs=[]
    for i,first in enumerate(stage_roots):
        nxt=(stage_roots[i+1] if i not in (8,14) else (0x9320 if i==8 else 0x9B20))
        if first>=nxt or (nxt-first)%2: raise ValueError('First-level indexed pointer list malformed')
        pairs.append((first,nxt))
    if sum((stop-start)//2 for start,stop in pairs)!=64:
        raise ValueError('64 second-level selector pointers drift')

    second=[]
    for st,en in pairs:
        second.extend(word(bank,a) for a in range(st,en,2))
    if len(set(second))!=64:
        raise ValueError('64 distinct nested selectors not preserved')
    if sorted(second) != second:
        raise ValueError('Nested selector ordering changed')
    if not all(0x9320<=p<0x93CC or 0x9B20<=p<0x9B82 for p in second):
        raise ValueError('Second-level pointer outside third-level table region')
    if second[0]!=0x9320 or second[41]!=0x93CA or second[42]!=0x9B20 or second[-1]!=0x9B7E:
        raise ValueError('Nested selector group boundaries drift')
    group_tables=[]
    all_terminal=[]
    exhaustive=[]
    for top,(st,en) in enumerate(pairs):
        for inner,cpu in enumerate(range(st,en,2)):
            second_root=word(bank,cpu)
            idx=second.index(second_root)
            next_root=second[idx+1] if idx+1<len(second) and idx!=41 else (0x93CC if idx==41 else 0x9B82)
            if (next_root-second_root)%2 or not second_root<next_root:
                raise ValueError('Third-level vector stride/boundary conflict')
            # Verify all selector triples expected from CPU $801E; actual ROM
            # addressing uses exact little-endian low/high byte reads.
            for tertiary,loc in enumerate(range(second_root,next_root,2)):
                leaf=word(bank,loc)
                simulated_stage=word(bank,0x92AE+top*2)
                simulated_middle=word(bank,simulated_stage+inner*2)
                simulated_leaf=word(bank,simulated_middle+tertiary*2)
                if (simulated_stage,simulated_middle,simulated_leaf)!=(st,second_root,leaf):
                    raise ValueError('Triple-indirect pointer address emulation differs')
                cpu_stage,cpu_middle,cpu_leaf,pcs=run_lookup_cpu(bank,top,inner,tertiary)
                if (cpu_stage,cpu_middle,cpu_leaf)!=(st,second_root,leaf):
                    raise ValueError('Original $801E CPU produces incorrect 3-level leaf address')
                if pcs[0]!=0x801E or pcs[-1]!=0x8046:
                    raise ValueError('Original CPU left bounded selector routine')
                all_terminal.append(leaf)
                exhaustive.append({'stage':top,'second':inner,'third':tertiary,
                                   'leaf_cpu':f'{leaf:04X}'})
            group_tables.append((second_root,next_root))
    if len(all_terminal)!=135 or len(group_tables)!=64:
        raise ValueError('Exhaustive selector root census changed')
    low_roots=sorted({p for p in all_terminal if 0x93CC<=p<0x9AF4})
    hi_roots=sorted({p for p in all_terminal if 0x9B82<=p<0x9F6E})
    seven_roots=sorted({p for p in all_terminal if 0xAB1F<=p<0xAFA4})
    if (len(low_roots),len(hi_roots),len(seven_roots))!=(70,43,16) or len(set(all_terminal))!=129:
        raise ValueError('Expected 113 four-byte leaves + 16 seven-byte streams')
    if len(low_roots)+len(hi_roots)+len(seven_roots)!=len(set(all_terminal)):
        raise ValueError('Unknown hierarchy leaf category')
    for roots,a,b in ((low_roots,0x93CC,0x9AF4),(hi_roots,0x9B82,0x9F6E)):
        if roots[0]!=a:raise ValueError('4-byte cell pool does not start at first root')
        for i,st in enumerate(roots):
            stop=roots[i+1] if i+1<len(roots) else b
            if (stop-st)%4 or stop<=st:raise ValueError('Leaf pool does not consist of whole 4-byte cells')
            for loc in range(st,stop,4):
                payload=rd(bank,loc,4)
                checked_claim(classes,nodes,loc,'.byte '+','.join(f'${x:02X}' for x in payload),4,7)
    if seven_roots[0]!=0xAB1F:raise ValueError('7-byte spawn pool does not begin at first root')
    seven_record_counts=[]
    for i,st in enumerate(seven_roots):
        stop=seven_roots[i+1] if i+1<len(seven_roots) else 0xAFA4
        length=stop-st
        if length<=1 or (length-1)%7 or rd(bank,stop-1)[0]!=0xFF:
            raise ValueError('Seven-byte stream does not end with expected FF terminator')
        count=(length-1)//7
        seven_record_counts.append(count)
        for loc in range(st,stop-1,7):
            payload=rd(bank,loc,7)
            if payload[0] not in (0,1,2,3):
                raise ValueError('Seven-byte structure first field outside observed 0..3 domain')
            checked_claim(classes,nodes,loc,'.byte '+','.join(f'${x:02X}' for x in payload),7,8)
        checked_claim(classes,nodes,stop-1,'.byte $FF',1,9)
    if sum(seven_record_counts)!=163:
        raise ValueError('163 seven-byte entries expected')
    # Tier 2 and tier 3 pointer bytes become independently assembled words.
    for a,b in REGIONS['level2'] + REGIONS['level3']:
        for loc in range(a,b,2):
            checked_claim(classes,nodes,loc,f'.word ${word(bank,loc):04X}',2,6)
    for top,(st,en) in enumerate(pairs):
        labels[st].append(f'room0a_stage_{top:02d}_second_level')
    for i,st in enumerate(second):
        labels[st].append(f'room0a_third_level_{i:02d}')
    for i,st in enumerate(low_roots):labels[st].append(f'room0a_four_cell_low_{i:03d}')
    for i,st in enumerate(hi_roots):labels[st].append(f'room0a_four_cell_high_{i:03d}')
    for i,st in enumerate(seven_roots):labels[st].append(f'room0a_seven_cell_stream_{i:02d}')

    # A separate, original audited B8CC room-message lookup is a two-tier
    # selector: 0/1 -> one of five room stages -> 0xFF-terminated payload.
    # We do NOT extend this interpretation to the remaining B937-C000 bytes.
    if rd(bank,0xB8DC,5)!=bytes.fromhex('b909b98508'):
        # See original B8DC absolute,Y load ($B909), rather than relying on
        # an incidental 6502 byte sequence occurring in raw data.
        raise ValueError('Original B8DC room-message selector drift')
    message_group_roots=[word(bank,a) for a in (0xB909,0xB90B)]
    if message_group_roots!=[0xB90D,0xB917]:
        raise ValueError('Room-message first-level pointers changed')
    message_roots=[word(bank,a) for a in range(0xB90D,0xB921,2)]
    if len(message_roots)!=10 or message_roots[0]!=0xB921 or message_roots[-1]!=0xB935 or message_roots!=sorted(message_roots):
        raise ValueError('Room-message second-level pointer structure changed')
    for address in (0xB909,0xB90B,*range(0xB90D,0xB921,2)):
        checked_claim(classes,nodes,address,f'.word ${word(bank,address):04X}',2,10)
    messages=[]
    for i,root in enumerate(message_roots):
        stop=message_roots[i+1] if i+1<len(message_roots) else 0xB937
        raw=rd(bank,root,stop-root)
        if not 2<=len(raw)<=3 or raw[-1]!=0xFF or 0xFF in raw[:-1]:
            raise ValueError('Room-message byte stream does not terminate at bounded FF')
        checked_claim(classes,nodes,root,'.byte '+','.join(f'${v:02X}' for v in raw),len(raw),11)
        labels[root].append(f'room0a_message_{i:02d}')
        messages.append({'root_cpu':f'{root:04X}','bytes':len(raw),'contents_hex':raw.hex()})
    if sum(x['bytes'] for x in messages)!=22:raise ValueError('Expected ten terminated messages totaling 22 bytes')

    stats=Counter(classes)
    expected={0:3684,1:2162,2:168,3:2910,4:966,5:2057,6:398,7:2836,8:1141,9:16,10:24,11:22}
    if dict(stats)!=expected:
        raise ValueError(f'Unexpected complete bank breakdown: got {stats}, expected {expected}')
    if sum(stats.values())!=0x4000:
        raise ValueError('Bank address partition not complete')

    lines=['; Original Japanese VRC6 raw PRG bank $0A, CPU $8000-$BFFF.',
           '; 0538 bank-wide hierarchical room-data source; not complete semantic decomp.',
           '; 0536 AUDITED opcode source retained; 0537 candidate roots NOT certified.',
           '; 3-tier tables and 4/7 byte leaf data have exact structural bounds.',
           '; Selector values are locally enumerated, not proven live at runtime.',
           '.org $8000']
    tag={0:'UNRESOLVED',1:'AUDITED 6502',2:'AUDITED TABLE',
         3:'STATIC 6502 CANDIDATE (UNPROVED)',4:'STRUCTURAL PTR (0537)',
         5:'FIXED-WIDTH RECORD (0537)',6:'TIER-2/3 SELECTOR PTR',
         7:'FOUR-BYTE PAYLOAD CELL',8:'SEVEN-BYTE PAYLOAD RECORD',9:'FF STREAM TERMINATOR',10:'ROOM MESSAGE POINTERS',11:'FF TERMINATED ROOM MESSAGE'}
    pc=START;last=None
    while pc<END:
        ty=classes[pc-START]
        if ty!=last:lines.append(f'; {tag[ty]} starts ${pc:04X}');last=ty
        for lab in labels.get(pc,[]):lines.append(lab+':')
        if ty in (1,3):
            if pc not in (known if ty==1 else candidates):
                raise ValueError(f'Missing 6502 node at {pc:04X}')
            mn,mode,n,arg=(known if ty==1 else candidates)[pc]
            lines.append('    '+mnemonic(mn,mode,arg))
        elif ty in (2,4,5,6,7,8,9,10,11):
            if pc not in nodes:raise ValueError(f'Missing data node ${pc:04X}')
            n,src=nodes[pc]
            lines.append('    '+src)
        else:
            n=1
            while pc+n<END and classes[pc+n-START]==0 and n<16:n+=1
            lines.append('    .byte '+','.join(f'${v:02X}' for v in rd(bank,pc,n)))
        pc+=n
    asm='\n'.join(lines)+'\n'
    if assemble(asm, START, 0x4000)!=bank:
        raise ValueError('Independently reassembled bank0A differs from original')

    report={
        'goal':'entire original raw bank0A recovery, not a small-byte certificate',
        'rom_sha256':base.JP_SHA,'raw_bank_0a_sha256':CODE_SHA,
        'bank_cpu':'8000-BFFF','complete_original_bank_size':16384,
        'source':'BYTE-EXACT; SEMANTICALLY INCOMPLETE',
        'whole_bank_classification_requires_unverified_candidates':True,
        'counts':{tag[k]:stats[k] for k in range(12)},
        'unresolved':stats[0],
        'already_audited_6502':stats[1],
        'unverified_6502_candidate':stats[3],
        'additional_hierarchical_source_vs_0537':stats[6]+stats[7]+stats[8]+stats[9],
        'room_message_source_bytes':stats[10]+stats[11],
        'hierarchical_source_total_including_0537_top_table':30+stats[6]+stats[7]+stats[8]+stats[9],
        'hierarchy':{'top_selector_words':len(stage_roots),
                     'second_level_selector_words':len(second),
                     'third_level_selector_words':len(all_terminal),
                     'four_byte_distinct_roots':len(low_roots)+len(hi_roots),
                     'four_byte_cells':stats[7]//4,
                     'seven_byte_distinct_roots':len(seven_roots),
                     'seven_byte_records':sum(seven_record_counts),
                     'seven_byte_ff_terminators':len(seven_roots),
                     'selector_triplets_tested':len(exhaustive),
                     'lookup_routine_cpu':'801E-8046',
                     'instruction_exact_local_6502_cases':len(exhaustive),
                     'live_selector_bounds_proven':False},
        'bounded_room_messages':messages,
        'address_partition':[{'start_cpu':f'{a:04X}','end_cpu_exclusive':f'{b:04X}',
                  'kind':tag[t],'bytes':b-a}
                 for a,b,t in contiguous_spans(classes)],
        'not_proven':['global mapper state and selector producer ranges',
                      'incoming control-flow root and CPU frame liveness',
                      'field meanings inside 4- and 7-byte leaf cells',
                      'the remaining 3,684 unknown bank bytes',
                      'candidate 2,910 instruction/operand bytes',
                      'native C++ gameplay parity'],
        'strict_new_unique_rom_bytes':0,
    }
    return {'asm':asm,'report':report,'source_bank':bank,'selector_cases':exhaustive,
            'classes':classes,'nodes':nodes}


def contiguous_spans(classes):
    p=0
    for i in range(1,len(classes)+1):
        if i==len(classes) or classes[i]!=classes[p]:
            yield START+p,START+i,classes[p]
            p=i


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--rom',type=Path)
    ap.add_argument('--baseline',type=Path)
    ap.add_argument('--out',type=Path)
    ap.add_argument('--smoke',action='store_true')
    x=ap.parse_args()
    if x.smoke:
        assert len(REGIONS['level2'])==2 and len(REGIONS['cells4'])==2
        print('PASS raw0A bank-hierarchy source smoke')
        return
    if not x.rom or not x.baseline or not x.out:
        ap.error('--rom, --baseline, --out required')
    rom=x.rom.read_bytes()
    if hashlib.sha256(rom).hexdigest()!=base.JP_SHA:raise ValueError('Original Japanese ROM identity failed')
    bank=rom[16+10*16384:16+11*16384]
    result=classify(bank,x.baseline.read_text(encoding='ascii'))
    x.out.mkdir(parents=True,exist_ok=True)
    (x.out/'prg_raw0a.asm').write_text(result['asm'],encoding='ascii')
    (x.out/'raw0a_hierarchy_atlas.json').write_text(json.dumps(result['report'],indent=2)+'\n')
    (x.out/'raw0a_valid_selector_triplets.json').write_text(json.dumps(result['selector_cases'],indent=2)+'\n')
    print('ORIGINAL FULL RAW0A BANK PASS 16384/16384')
    print('Additional tiered structure:',result['report']['additional_hierarchical_source_vs_0537'],
          'bytes; room messages:',result['report']['room_message_source_bytes'],'bytes; unresolved:',result['report']['unresolved'])


if __name__=='__main__':main()
