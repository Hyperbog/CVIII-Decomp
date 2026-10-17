#!/usr/bin/env python3
"""0537: exhaustive physical bank $0A coverage atlas and candidate instruction source.

The entire 16-KiB bank is represented, but NOT automatically decompiled.
Certified source positions are imported from the earlier authenticated 0536
bank source. Additional 6502-looking control-flow is marked CANDIDATE only.
No mere opcode-pattern match is promoted to verified or newly strict-certified.

Run from the CVIII-Decomp JP repository:
 python3 JP/decomp/tools/build_whole_cart_recomp_0529.py --rom JP.nes --out /tmp/jp_src
 python3 JP/decomp/tools/recover_raw0a_bank_0537.py --rom JP.nes \
   --baseline /tmp/jp_src/prg_raw0a.asm --out /tmp/bank0a0537
Or --smoke for a ROM-free self-test.
"""
from __future__ import annotations
import argparse, collections, hashlib, json
from pathlib import Path

from audit_nmi_fixed_scheduler_banked import OPS, BR, TERM
from build_whole_cart_recomp_0529 import assemble, mnemonic

JP_SHA = '958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
BANK_SHA = '1460df577d44e114c64fdf34a8837629765f3f6a93d45796fdf81e5ffacb5ed8'
BANK=10
LO=0x8000
HI=0xc000
# Distinguish the two local 6502 code neighborhoods from ROM data islands.
# This is a search guard, NOT a proof that every byte in these spans is code.
SEARCH_WINDOWS=((0x8001,0x9200),(0xb000,0xb900))
INLINE_DISPATCH={0xafa6,0xb122,0xb4ce,0xb68b}
ENTRY_CANDIDATES=(0x8001,0x801e,0x8047,0xb7f7)
BRANCHES={x.lower() for x in BR}
TERMINALS={x.lower() for x in TERM}


def digest(payload:bytes)->str:return hashlib.sha256(payload).hexdigest()

def instruction(bank:bytes,pc:int):
    if not LO<=pc<HI:raise ValueError('Outside original CPU mapping')
    op=bank[pc-LO]
    if op not in OPS:raise ValueError(f'Unknown official opcode ${op:02X} at ${pc:04X}')
    name,mode,n=OPS[op]
    if pc+n>HI:raise ValueError('Instruction crosses CPU bank')
    b=bank[pc+1-LO:pc+n-LO]
    arg=(b[0] if n==2 else int.from_bytes(b,'little') if n==3 else None)
    if mode=='rel':arg=(pc+2+(arg if arg<128 else arg-256))&0xffff
    return name.lower(),mode,n,arg


def read_baseline(bank:bytes,source:str):
    """Split region comments and decode instructions, checking whole-bank bounds."""
    classes=bytearray(16384);ins={};nodes={};labels=collections.defaultdict(list)
    pc=None;region='unclassified';all_written=bytearray(16384)
    for line in source.splitlines():
        if line.startswith('; VERIFIED '):region='verified'
        elif line.startswith('; UNCLASSIFIED '):region='unclassified'
        s=line.split(';',1)[0].strip()
        if not s or s.lower().startswith('.equ '):continue
        if s.lower().startswith('.org '):pc=int(s.split('$')[1],16);continue
        if s.endswith(':'):
            if pc is None:raise ValueError('Label without origin')
            labels[pc].append(s[:-1]);continue
        if pc is None:raise ValueError('No origin')
        if s.startswith('.byte '):n=s.count(',')+1;kind=2 if region=='verified' else 0
        elif s.startswith('.word '):n=2*(s.count(',')+1);kind=2
        else:
            row=instruction(bank,pc)
            if row[0]!=s.split()[0].lower():raise ValueError(f'Instruction/source conflict at ${pc:04X}')
            n=row[2];kind=1;ins[pc]=row
        if not LO<=pc<HI or pc+n>HI:raise ValueError('Bank source extends outside physical bank')
        if any(all_written[x-LO] for x in range(pc,pc+n)):
            raise ValueError(f'Bank source byte overlap at ${pc:04X}')
        for x in range(pc,pc+n):
            all_written[x-LO]=1
            classes[x-LO]=kind
        if kind==2:nodes[pc]=(n,s)
        pc+=n
    if not all(all_written):raise ValueError('Bank input has a hole')
    if (sum(v==1 for v in classes),sum(v==2 for v in classes))!=(2162,168):
        raise ValueError('Expected 0536 exact 2162 code + 168 dispatch/room data bytes')
    return classes,ins,nodes,labels


def in_search(pc:int,n:int=1)->bool:
    return any(a<=pc and pc+n<=e for a,e in SEARCH_WINDOWS)


def walk_candidate(bank:bytes,root:int):
    q=collections.deque([root]);result={};used={};edges=[];problems=[]
    while q:
        pc=q.popleft()
        if pc in result:continue
        if not in_search(pc):
            edges.append((pc,'outside-recovery-window'));continue
        try:mn,mode,n,arg=instruction(bank,pc)
        except ValueError as e:
            problems.append((pc,str(e)));continue
        if not in_search(pc,n):
            problems.append((pc,'instruction escapes bounded search neighborhood'));continue
        if any(x in used for x in range(pc,pc+n)):
            problems.append((pc,'overlapping instruction boundary'));continue
        result[pc]=(mn,mode,n,arg)
        for x in range(pc,pc+n):used[x]=pc
        if pc in INLINE_DISPATCH:
            if (mn,arg)!=('jsr',0xe7fb):
                problems.append((pc,'inline E7FB dispatcher mismatch'))
            continue
        if mn in BRANCHES:q.extend((arg,pc+n))
        elif mn=='jsr':q.extend((arg,pc+n))
        elif mn=='jmp':
            if mode=='abs':q.append(arg)
            else:edges.append((pc,'indirect'));continue
        elif mn not in TERMINALS:q.append(pc+n)
        if len(result)>5000:
            problems.append((pc,'graph exceeds candidate bound'));break
    return result,used,edges,problems


def candidate_source(bank:bytes,classes:bytearray,known_ins:dict):
    raw_sources=collections.defaultdict(list)
    for offset in range(16384-2):
        pc=LO+offset
        if not in_search(pc,3) or bank[offset] not in (0x20,0x4c):continue
        target=bank[offset+1]|bank[offset+2]<<8
        if in_search(target):raw_sources[target].append(pc)
    roots=set(ENTRY_CANDIDATES)|set(raw_sources)
    for pc in range(LO+1,HI):
        if not in_search(pc) or classes[pc-LO]!=0:continue
        if bank[pc-LO-1] in (0x60,0x40):roots.add(pc)
    priority=lambda r:(0 if r in ENTRY_CANDIDATES else 1,
                       -len(raw_sources[r]),r)
    selected={};used={};roots_accepted=[];roots_rejected=[]
    for root in sorted(roots,key=priority):
        if root in used or classes[root-LO]!=0:continue
        graph,bytes_seen,out,problems=walk_candidate(bank,root)
        if problems or len(graph)<3:
            roots_rejected.append((root,problems[:1] or [('short-graph',len(graph))]));continue
        if any(pc+i in used and used[pc+i]!=pc for pc,row in graph.items() for i in range(row[2])):
            roots_rejected.append((root,[('overlap with earlier candidate',)]));continue
        if any(classes[pc+i-LO]==2 for pc,row in graph.items() for i in range(row[2])):
            roots_rejected.append((root,[('crosses verified data',)]));continue
        if any(classes[pc+i-LO]==1 and (pc not in known_ins or known_ins[pc]!=row)
               for pc,row in graph.items() for i in range(row[2])):
            roots_rejected.append((root,[('conflicts with verified instruction start',)]));continue
        new={pc:row for pc,row in graph.items() if classes[pc-LO]==0}
        if not new:continue
        for pc,row in new.items():
            if any(classes[pc+i-LO]!=0 for i in range(row[2])):
                raise AssertionError('Candidate instruction partially overlaps authenticated source')
            selected[pc]=row
        for pc,row in graph.items():
            for i in range(row[2]):used[pc+i]=pc
        roots_accepted.append({'root_cpu':f'{root:04X}',
                               'direct_opcode_pattern_references':len(raw_sources[root]),
                               'candidate_opcode_bytes':sum(row[2] for row in new.values()),
                               'candidate_instructions':len(new),
                               'scope':'bounded-static-candidate; no execution provenance'})
    if any(classes[pc+i-LO] for pc,row in selected.items() for i in range(row[2])):
        raise AssertionError('Previous classified source conflict')
    return selected,roots_accepted,roots_rejected,raw_sources


def structure_data(bank:bytes,classes:bytearray,candidate:dict):
    """Recover large, separately classified, pointer-indexed original data.

    Pointer and record structure is checked for every entry, not inferred by
    accepting a convenient byte count. Producer instruction sites are only
    bounded static CANDIDATES, so these remain STRUCTURAL evidence (no liveness).
    """
    specs=(
        # site start/end, record start/end, row width, expected count, linked code read
        (0x92ae,0x92cc,None,None,None,15,0x8022),
        (0x9f6e,0xa12e,0xa12e,0xa56b,5,224,0x8117),
        (0xa56b,0xa753,0xa753,0xab1f,4,244,0x8197),
    )
    nodes={};results=[]
    for table_begin,table_end,record_begin,record_end,width,nptrs,producer in specs:
        if producer not in candidate:raise ValueError(f'Original bank0A pointer producer not decoded at ${producer:04X}')
        mn,mode,n,absolute=candidate[producer]
        if mode!='absy' or absolute!=table_begin:
            raise ValueError(f'Wrong original bank0A table producer at ${producer:04X}')
        if (table_end-table_begin)!=2*nptrs:raise ValueError('Pointer extent inconsistent')
        pointers=[]
        for pc in range(table_begin,table_end,2):
            if any(classes[x-LO] for x in (pc,pc+1)):
                raise ValueError('Structural pointer overlaps claimed source')
            ptr=int.from_bytes(bank[pc-LO:pc+2-LO],'little')
            if not LO<=ptr<HI:raise ValueError('Structural pointer outside PRG bank')
            pointers.append(ptr)
            nodes[pc]=(2,f'.word ${ptr:04X}')
            classes[pc-LO:pc+2-LO]=bytes([4,4])
        if record_begin is None:
            # The first table has variable-width script entries. Do not label
            # the payload as fixed records, but assert its producer-rooted
            # array starts at the next byte and has distinct in-bank targets.
            if pointers[0]!=table_end or len(set(pointers))!=nptrs or any(
                    not table_end<=value<0x9f6e for value in pointers):
                raise ValueError('Variable-record table rooted pointer drift')
        if record_begin is not None:
            if min(pointers)!=record_begin:raise ValueError('First record pointer did not match structural bound')
            valid=set(range(record_begin,record_end,width))
            if (record_end-record_begin)%width or set(pointers)!=valid:
                raise ValueError('Pointer root census does not cover exact record stride')
            for pc in range(record_begin,record_end,width):
                if any(classes[x-LO] for x in range(pc,pc+width)):
                    raise ValueError('Record structure overlaps recovered code/data')
                b=bank[pc-LO:pc+width-LO]
                nodes[pc]=(width,'.byte '+','.join(f'${v:02X}' for v in b))
                classes[pc-LO:pc+width-LO]=bytes([5]*width)
            roots=len(valid)
        else:roots=None
        results.append({'table_cpu_start':f'{table_begin:04X}',
            'table_end_exclusive':f'{table_end:04X}',
            'table_sha256':digest(bank[table_begin-LO:table_end-LO]),
            'pointer_count':len(pointers),'distinct_pointers':len(set(pointers)),
            'producer_candidate_cpu':f'{producer:04X}',
            'record_start_cpu':f'{record_begin:04X}' if record_begin else None,
            'record_end_exclusive':f'{record_end:04X}' if record_end else None,
            'record_width':width,'unique_records':roots,
            'record_sha256':digest(bank[record_begin-LO:record_end-LO]) if width else None,
            'proof_level':'pointer and record layout verified, producer execution not proved'})
    return nodes,results


def spans(classes:bytearray):
    items=[];a=0
    for b in range(1,len(classes)+1):
        if b==len(classes) or classes[b]!=classes[a]:
            items.append({'start_cpu':f'{LO+a:04X}','end_cpu_exclusive':f'{LO+b:04X}',
                          'bytes':b-a,'category':('unresolved','audited_6502','audited_data','candidate_6502','structural_ptr','structural_record')[classes[a]]})
            a=b
    return items


def render(bank:bytes,known:dict,nodes:dict,labels:dict,candidates:dict,classes:bytearray):
    output=['; FULL PHYSICAL JP raw bank $0A, 16KiB. All original bytes represented.',
            '; AUDITED source comes from 0536. CANDIDATE source is NOT certified.',
            '; UNRESOLVED bytes have no code/data semantic proof.',
            '; CPU bank $8000-$BFFF; mapper 24 / VRC6.',
            '.org $8000']
    pc=LO;last=None
    while pc<HI:
        ty=classes[pc-LO]
        if ty==1:
            if pc not in known:raise ValueError('Missing verified instruction boundary')
            mn,mo,n,arg=known[pc]
        elif ty==3:
            if pc not in candidates:raise ValueError('Missing candidate instruction boundary')
            mn,mo,n,arg=candidates[pc]
        elif ty in (2,4,5):
            if pc not in nodes:raise ValueError('Missing verified data node')
            n,raw=nodes[pc]
        else:
            end=pc+1
            while end<HI and classes[end-LO]==0 and end-pc<16:end+=1
            n=end-pc
        if ty!=last:
            output.append(f'; {("UNRESOLVED", "AUDITED 6502", "AUDITED pointer/data", "STATIC CANDIDATE 6502 (NOT CERTIFIED)", "STRUCTURAL POINTERS (NON-LIVE)", "STRUCTURAL RECORDS (NON-LIVE)")[ty]} from ${pc:04X}')
            last=ty
        for label in labels.get(pc,[]):output.append(label+':')
        if ty in (1,3):output.append('    '+mnemonic(mn,mo,arg))
        elif ty in (2,4,5):output.append('    '+raw)
        else:output.append('    .byte '+','.join(f'${v:02X}' for v in bank[pc-LO:pc+n-LO]))
        pc+=n
    return '\n'.join(output)+'\n'


def audit(rom:bytes,baseline:str,out:Path):
    if len(rom)!=393232 or digest(rom)!=JP_SHA:raise ValueError('Original JP ROM identity mismatch')
    bank=rom[16+BANK*16384:16+(BANK+1)*16384]
    if len(bank)!=16384 or digest(bank)!=BANK_SHA:raise ValueError('Bank 0A SHA mismatch')
    if assemble(baseline,LO,16384)!=bank:raise ValueError('Original 0536 bank source does not reassemble')
    classes,known,nodes,labels=read_baseline(bank,baseline)
    candidate,accepted,rejected,sources=candidate_source(bank,classes,known)
    for pc,row in candidate.items():
        for i in range(row[2]):
            assert classes[pc+i-LO]==0
            classes[pc+i-LO]=3
    structure,structural_evidence=structure_data(bank,classes,candidate)
    nodes.update(structure)
    source=render(bank,known,nodes,labels,candidate,classes)
    if assemble(source,LO,16384)!=bank:raise ValueError('New full bank 0A mnemonic source reassembly failed')
    counts=collections.Counter(classes)
    windows=[]
    for start in range(LO,HI,512):
        histogram=collections.Counter(classes[start-LO:start+512-LO])
        windows.append({'start_cpu':f'{start:04X}','end_cpu_inclusive':f'{start+511:04X}',
                        'verified_opcode_bytes':histogram[1],
                        'verified_table_bytes':histogram[2],
                        'candidate_opcode_bytes':histogram[3],
                        'structural_pointer_bytes':histogram[4],
                        'structural_record_bytes':histogram[5],
                        'unresolved_bytes':histogram[0]})
    report={'checkpoint':'0537 bank-wide recovery investigation',
      'rom_sha256':JP_SHA,'raw_bank_0a_sha256':BANK_SHA,
      'bank_cpu_span':'8000-BFFF','bank_size_bytes':16384,
      'source_identity':'COMPLETE BYTE-EXACT; SEMANTIC RECOVERY INCOMPLETE',
      'classification':{'audited_6502_opcode_operand_bytes':counts[1],
           'audited_pointer_and_data_bytes':counts[2],
           'new_static_6502_candidate_bytes_NOT_CERTIFIED':counts[3],
           'structural_pointer_bytes_NOT_LIVE':counts[4],
           'structural_fixed_record_bytes_NOT_LIVE':counts[5],
           'unresolved_bytes':counts[0],
           'sum':sum(counts.values())},
      'producer_linked_fixed_width_record_structures':structural_evidence,
      'candidate_roots_accepted':accepted,
      'candidate_roots_rejected_count':len(rejected),
      'candidate_roots_rejected_first_30':[{'root_cpu':f'{a:04X}','reason':str(why)} for a,why in rejected[:30]],
      'source_reference_discovery':{'candidate_targets':len(sources),'limitation':'All-offset JSR/JMP patterns are NOT instruction alignment or liveness evidence'},
      'window_512_byte_atlas':windows,
      'address_partition':spans(classes),
      'not_proved':['Candidate CFG entry reachability','Candidate instruction alignment from an external live caller',
           'Most remaining 9200-AFFF and B900-BFFF data formats still unresolved',
           'Bank switch state across unknown fixed/banked callees',
           'Original Mesen gameplay parity','Native C++ complete game recompilation'],
      'strict_prg_certified_bytes_added':0}
    assert counts[1]==2162 and counts[2]==168
    assert sum(counts.values())==16384
    out.mkdir(parents=True,exist_ok=True)
    (out/'raw0a_fullbank_0537.asm').write_text(source,encoding='ascii')
    (out/'raw0a_fullbank_0537_atlas.json').write_text(json.dumps(report,indent=2)+'\n')
    print('FULL BANK PASS raw0A 16384/16384 independently assembled bytes, SHA256',BANK_SHA)
    print('Audited 6502',counts[1],'typed data',counts[2],'CANDIDATE 6502',counts[3],
          'STRUCTURAL',counts[4]+counts[5],'UNRESOLVED',counts[0],'accepted candidate roots',len(accepted))
    return report


def smoke():
    bank=bytearray(16384)
    bank[0x0001:0x0004]=bytes.fromhex('A9 05 60')
    ins,used,edges,problems=walk_candidate(bytes(bank),0x8001)
    assert not problems and len(ins)==2 and len(used)==3
    assert instruction(bytes(bank),0x8001)==('lda','imm',2,5)
    assert spans(bytearray([0,0,1,1,3,2]))[-1]['category']=='audited_data'
    print('PASS ROM-free bank0A whole-bank CFG/boundary smoke')


if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--rom',type=Path)
    ap.add_argument('--baseline',type=Path)
    ap.add_argument('--out',type=Path)
    ap.add_argument('--smoke',action='store_true')
    x=ap.parse_args()
    if x.smoke:smoke()
    else:
        if x.rom is None or x.baseline is None or x.out is None:
            ap.error('--rom, --baseline, and --out are mandatory without --smoke')
        audit(x.rom.read_bytes(),x.baseline.read_text(),x.out)
