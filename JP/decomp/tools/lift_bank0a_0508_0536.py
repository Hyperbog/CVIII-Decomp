#!/usr/bin/env python3
"""0536 source lift of 0508 conditional bank-$0A room graph and typed tables.

Original 0508 evidence: JP/decomp/tools/audit_0508_expanded.py and
JP/decomp/tools/audit_0508_bulk_0a0e.py. CPU entrypoints are authenticated
via bank-$0A mapper writes from fixed E51E/E526, but live selector
and frame path are NOT proved. This is not novel strict PRG coverage.
"""
from collections import deque
from hashlib import sha256
from audit_nmi_fixed_scheduler_banked import OPS, BR, TERM
from lift_bank04_parser_0532 import fmt

ROM_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
INLINE={0xAFA6:(0xAFA9,20),0xB122:(0xB125,22),0xB4CE:(0xB4D1,12),0xB68B:(0xB68E,11)}
TABLE_SHA={0xAFA6:'422e65c2a5a5c30ea2e6a7c77978d54c2d1cd64b99628e7f94662a29f9f7d396',0xB122:'2c3db8027fdab36d434b87aa7b8e550617cf3e8fd2f14b59e0c7db47d0b1adba',0xB4CE:'380ecdac9478f19215c9a5628e8395dce3a11ba951218f5f01583fa6dabdfa7c',0xB68B:'c237cfadfe6c2f0c2e1bd4c6317adf57de417096779750133694c992b14c0583'}
ENTRY_SHA='0cbfd39d34523da29edaa6a2dcf5cdb4b62de628d0e5568ea3879d7de5a1c0c7'
DESCRIPTORS=(0xB8A6,0xB8C2)
ROOM_PTRS=(0xB8C2,0xB8CC) # 10 bytes original 0508 report

def sha(x):return sha256(x).hexdigest()

def decode(bank,pc):
    if not 0x8000<=pc<0xC000:raise ValueError('Banked target outside original raw0A')
    op=bank[pc-0x8000]
    if op not in OPS:raise ValueError(f'Unverified 6502 opcode at {pc:04X} {op:02X}')
    mn,mode,n=OPS[op];v=bank[pc-0x8000:pc+n-0x8000]
    if len(v)!=n:raise ValueError('Escaped 16KiB PRG page')
    arg=v[1] if n==2 else int.from_bytes(v[1:],'little') if n==3 else None
    if mode=='rel':arg=(pc+n+(arg if arg<128 else arg-256))&65535
    return mn.lower(),mode,n,arg

def _graph(bank,roots):
    q=deque(roots);ins={};used=set();external=[];inline=[]
    while q:
        pc=q.popleft()
        if pc in ins:continue
        if not 0x8000<=pc<0xc000:external.append(pc);continue
        mn,mode,n,arg=decode(bank,pc)
        occupied=set(range(pc,pc+n))
        if used&occupied:raise ValueError('0508 control-flow instruction overlap')
        used|=occupied;ins[pc]=(mn,mode,n,arg)
        if pc in INLINE:
            if (mn,arg)!=('jsr',0xe7fb):raise ValueError('Changed inline dispatcher JSR')
            inline.append(pc);continue
        if mn in ('bpl','bmi','bvc','bvs','bcc','bcs','bne','beq'):
            q.extend((arg,pc+n))
        elif mn=='jsr':q.extend((arg,pc+n))
        elif mn=='jmp':
            if mode=='ind':external.append((pc,arg,'indirect'))
            else:q.append(arg)
        elif mn not in {x.lower() for x in TERM}:q.append(pc+n)
        if len(ins)>=10000:raise ValueError('Unbounded control-flow')
    return ins,used,external,inline

def lift(prg, taken=None):
    if len(prg)!=262144:raise ValueError('Requires 256KiB Japanese PRG')
    bank=prg[10*16384:11*16384];fixed=prg[31*8192:32*8192]
    rd=lambda a,n=1:bank[a-0x8000:a+n-0x8000]
    fx=lambda a,n=1:fixed[a-0xe000:a+n-0xe000]
    if sha(rd(0xafa4,5))!=ENTRY_SHA or rd(0xafa4,5)!=rd(0xb4cc,5):
        raise ValueError('0508 original fixed selected bank0A entrypoints changed')
    if fx(0xe51e,8)!=bytes.fromhex('a90a20d0e24ca4af') or fx(0xe526,8)!=bytes.fromhex('a90a20d0e24cccb4'):
        raise ValueError('Original mapper write and fixed jump target changed')
    pointers={}
    for site,(start,count) in INLINE.items():
        if rd(site,3)!=bytes.fromhex('20fbe7'):raise ValueError('Dispatcher call changed')
        b=rd(start,count*2)
        if sha(b)!=TABLE_SHA[site]:raise ValueError('0508 inline table ROM fingerprint changed')
        pointers[site]=tuple(int.from_bytes(b[i:i+2],'little') for i in range(0,len(b),2))
        if any(not 0x8000<=p<0xc000 for p in pointers[site]):raise ValueError('Bad table target')
    roots=(0xafa4,0xb4cc)+tuple(p for ps in pointers.values() for p in ps)
    ins,used,external,visited=_graph(bank,roots)
    if (len(ins),len(used),sorted(visited))!=(935,2042,sorted(INLINE)):
        raise ValueError(f'0508 annotated graph drift {len(ins)}, {len(used)}, {visited}')
    table_used=set()
    fragments=[]
    for site,(start,count) in sorted(INLINE.items()):
        end=start+count*2
        table_used.update(range(start,end))
        values=pointers[site]
        lines=[f'; 0508 inline pointer table at {start:04X}: {count} pointers; live selector domain unproved',f'Bank0A_Dispatch_{site:04X}:']
        for i in range(0,count,8):
            lines.append('    .word '+','.join(f'${v:04X}' for v in values[i:i+8]))
        fragments.append({'a':start,'b':end,'src':'0536 0508 typed E7FB inline dispatch pointers (conditional)', 'lines':lines})
    if table_used&used:raise ValueError('Inline table overlaps 6502 code')
    taken=set() if taken is None else set(taken)
    for pc,(_mn,_mode,n,_arg) in ins.items():
        word=set(range(pc,pc+n))
        if taken&word and not word<=taken:
            raise ValueError(f'Original 0508 code only partially overlaps previously classified source at ${pc:04X}')
    new_ins={pc:row for pc,row in ins.items() if set(range(pc,pc+row[2])).isdisjoint(taken)}
    labels={pc:f'Bank0A_Room_{pc:04X}' for pc in new_ins if pc in roots or any(
        name in BR|{'JSR','JMP'} and mode!='ind' and value==pc
        for name,mode,n,value in ((mn.upper(),mo,sz,arg) for mn,mo,sz,arg in new_ins.values()))}
    runs=[];group=None
    for pc,(mn,mode,n,arg) in sorted(new_ins.items()):
        if group is None or group['b']!=pc:
            group={'a':pc,'b':pc,'src':'0536 0508 original bank0A conditional mapped 6502 graph', 'lines':[]}
            runs.append(group)
        if pc in labels:group['lines'].append(labels[pc]+':')
        group['lines'].append('    '+fmt(mn,mode,arg,labels));group['b']=pc+n
    fragments=[fragment for fragment in fragments if set(range(fragment['a'],fragment['b'])).isdisjoint(taken)]
    fragments+=runs
    for a,b,label in ((0xb8a6,0xb8c2,'Bank0A_0E_Room_Descriptors'),(0xb8c2,0xb8cc,'Bank0A_0E_Room_Pointers')):
        if set(range(a,b)) & (used|table_used):raise ValueError('Typed room structure overlaps instructions or dispatch data')
        text=rd(a,b-a)
        if a==0xb8a6:
            if [text[3*i] for i in range(9)]!=[0x24,0x25,0x25,0x25,0x25,0x26,0x26,0x26,0x26] or text[27]!=0xff:
                raise ValueError('0508 room descriptor signature changed')
            lines=[f'{label}:']+['    .byte '+','.join(f'${x:02X}' for x in text[i:i+3]) for i in range(0,27,3)]+['    .byte $FF']
        else:
            lines=[f'{label}:','    .word '+','.join(f'${int.from_bytes(text[i:i+2],"little"):04X}' for i in range(0,len(text),2))]
        if set(range(a,b)) & taken:
            raise ValueError('Overlap with prior room descriptor classification')
        fragments.append({'a':a,'b':b,'src':'0536 original 0508 room-IO descriptor / pointer data (conditional)', 'lines':lines})
    b0e=prg[14*16384:15*16384]
    span=b0e[0xbe8b-0x8000:0xbf3a-0x8000]
    if sha(span)!='977745b341cfa56056be96e454d2e49e5d91084b798e82b1a1e819dcfcdab479':
        raise ValueError('Original 0508 phase5 bank0E 175-byte source fingerprint mismatch')
    if rd(0xb8c2,10)!=bytes.fromhex('a4bedbbe03bf8bbe1cbf'):
        raise ValueError('0508 mapped room pointer producer changed')
    # 5 independently validated original header+5-byte object+FF records;
    # emitted in physical address order, not table index order.
    records=(
      (0xbe8b,0xbea4,4,'21020000','2e2a12c1e26ad9fc2441246e9f5da2aabc594fc205da311c76db042fbcebe42a'),
      (0xbea4,0xbedb,10,'41200101','d615e38ee43e56072ac883b1509fc9bda21061ae0bc7eafa6c77875ad2bbc905'),
      (0xbedb,0xbf03,7,'11010002','ab1a532f59b395dad6a69351adb0bc7700626470fc070ad4ef791c91149d0e20'),
      (0xbf03,0xbf1c,4,'81030103','09b183d31652121dc1e5668a186aff96eb628f4bfc4c91ee96a5945845217b8a'),
      (0xbf1c,0xbf3a,5,'b1020000','c349435f174096b6fdeb1d4957780dabbc00d8276e5d0556de6e9db43f8571ea'))
    lines=['; 0508 phase5 original mapper-switched sound/room objects;',
           '; 5 header + object streams; conditional $07A0=0..4 simulation,',
           '; but no global index/domain liveness is claimed.']
    for a,b,count,header,h in records:
        blob=b0e[a-0x8000:b-0x8000]
        if len(blob)!=4+5*count+1 or sha(blob)!=h or blob[:4]!=bytes.fromhex(header) or blob[-1]!=255:
            raise ValueError(f'0508 bank0E record structure/fingerprint changed at ${a:04X}')
        if any(blob[4+5*i]==255 for i in range(count)):
            raise ValueError('0508 stream object collides with terminator')
        lines.append(f'Bank0E_Room_{a:04X}: ; {count} five-byte object records')
        lines.append('    .byte '+','.join(f'${x:02X}' for x in blob[:4])+' ; header: two packed fields, flags and metadata')
        for i in range(count):
            lines.append('    .byte '+','.join(f'${x:02X}' for x in blob[4+5*i:9+5*i]))
        lines.append('    .byte $FF ; loader sentinel')
    fragments0e=[{'a':0xbe8b,'b':0xbf3a,'src':'0536 authenticated 0508 bank0E 5 mapper-read streams, 30 typed objects; frame liveness unproved','lines':lines}]
    opcode_new=sum(n for mn,mode,n,arg in new_ins.values())
    tables_new=sum(x['b']-x['a'] for x in fragments if x['src'].startswith('0536 0508 typed'))
    if (opcode_new,tables_new)!=(1540,106):raise ValueError('0535/0508 double-credit exclusion drift')
    return {'raw0A':fragments,'raw0E':fragments0e},{
        'original_0508_graph_instruction_count':len(ins),
        'original_0508_graph_opcode_bytes':len(used),
        'original_0508_graph_pointer_table_bytes':len(table_used),
        'new_instruction_count':len(new_ins),'new_instruction_bytes':opcode_new,
        'new_inline_pointer_bytes':tables_new,
        'new_descriptor_pointer_bytes':38,
        'bank0E_mapper_read_stream_bytes':len(span),'bank0E_object_count':sum(r[2] for r in records),
        'previously_classified_source_bytes':len(used)-opcode_new +len(table_used)-tables_new,
        'new_total_classified_bytes':opcode_new+tables_new+38+len(span),
        'status':'0508 conditional graph and mapper-switched source reads; runtime frame/selector reachability remains unproved'}

def smoke():
    assert sum(n*2 for _,n in INLINE.values())==130
    print('PASS 0536 original ROM 0508 0A inline table schema')
