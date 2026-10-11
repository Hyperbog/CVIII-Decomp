#!/usr/bin/env python3
"""JP 0532: original sound parser + bank04 script source, per-bank physical code.

ROM SHA-locked original 04F7-04FA producer evidence; official NMOS opcode CFG
with guarded indirect-dispatch roots. Source is real original 6502 mnemonic code
and explicitly typed parser-local lookup data, not speculative linear sweep.
"""
from __future__ import annotations
from collections import deque, defaultdict
import hashlib
import audit_nmi_fixed_scheduler_banked as proof

ROM_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
PARSER_BEGIN=0x8001
PARSER_END=0x87ae
WINDOWS=[
 ('04F7',0x87ae,0x920a,'cfdd27fa72b9e990c31bb12e1511fa7229ffe2c898dcc361586c77b71543caa6'),
 ('04F8',0x920a,0xa014,'728c86cd808e178821f7f72d1f0371eb16a5bde3a1dda495543338391a5e7b3c'),
 ('04F9',0xa014,0xb1f0,'55e35f223091a0c50beaf7ba0561445cc5c07d11ae83bfe827abcc22aa2d5a5b'),
 ('04FA',0xb1f0,0xbe7e,'a7f0a8308ed9335b27de8eaf3df440f0d28cd6f57fb97e4123222e3116fc5f55'),
]
PARSER_SHA='e2c3ff3d7e9f96b598610a8028f5b92a606fac7f9acb2977811146fa145fdb67'
ROOT_SHA='31bb930976270ba7a2b2b47429fa42baba6d374fe17a06fe39d28d5f5a90f578'
REF_SHA='4d9ab53a98c52535193dcc33b86260cc16f187516b3a331fc210275c2ae23d98'
DISPATCH_TARGETS={0x833d,0x837e,0x83b7,0x85b3,0x83f8,0x840f,0x8456,0x845a,0x848c,0x849f,0x84ed,0x851d,0x852a,0x8444,0x86a9,0x86b4,0x86bf,0x8644,0x8668,0x869e}
BR={m.lower() for m in proof.BR}
TERMINATE={m.lower() for m in proof.TERM}
INDIRECT_SITES={0x802e,0x83e1,0x842d,0x8641}
TABLES=[(0x83e4,0x83f8),(0x8430,0x8444),(0x86f9,0x870b),(0x870b,0x8713)]

def digest(data):return hashlib.sha256(data).hexdigest()

def fmt(mn,mode,arg,labels):
    if mode=='imp':return mn
    if mode=='acc':return mn+' a'
    if mode=='imm':return f'{mn} #${arg:02X}'
    if mode=='rel':return mn+' '+labels.get(arg,f'${arg:04X}')
    if mode in ('zp','zpx','zpy','indx','indy'):t=f'${arg:02X}'
    else:t=labels.get(arg,f'${arg:04X}') if mode in ('abs','ind') else f'${arg:04X}'
    if mode in ('absx','absy'):t=f'${arg:04X}'
    if mode in ('zpx','absx'):t+=',x'
    if mode in ('zpy','absy'):t+=',y'
    if mode=='indx':t='('+t+',x)'
    if mode=='indy':t='('+t+'),y'
    if mode=='ind':t='('+t+')'
    return mn+' '+t

def parser_instructions(raw):
    if digest(raw[PARSER_BEGIN-0x8000:PARSER_END-0x8000])!=PARSER_SHA:
        raise ValueError('Original common sound parser bytes do not match 04F7 proof')
    q=deque([PARSER_BEGIN,*sorted(DISPATCH_TARGETS)]);seen={}
    while q:
        start=q.popleft()
        if not PARSER_BEGIN<=start<PARSER_END or start in seen:continue
        pc=start
        while PARSER_BEGIN<=pc<PARSER_END and pc not in seen:
            op=raw[pc-0x8000]
            if op not in proof.OPS:raise ValueError(f'Illegal parser opcode at ${pc:04X}')
            mn,mode,n=proof.OPS[op];mn=mn.lower()
            if pc+n>PARSER_END:raise ValueError('Parser opcode operand escapes bounded body')
            chunk=raw[pc-0x8000:pc+n-0x8000]
            arg=None if n==1 else chunk[1] if n==2 else chunk[1]|chunk[2]<<8
            if mode=='rel':arg=(pc+2+(arg if arg<128 else arg-256))&0xffff
            seen[pc]=(mn,mode,n,arg)
            nxt=pc+n
            if mn=='jsr':
                if PARSER_BEGIN<=arg<PARSER_END:q.append(arg)
                pc=nxt;continue
            if mn=='jmp':
                if mode=='ind':
                    if pc not in INDIRECT_SITES:raise ValueError('Unproven parser indirect jump')
                elif PARSER_BEGIN<=arg<PARSER_END:q.append(arg)
                break
            if mn in TERMINATE:break
            if mn in BR:
                if PARSER_BEGIN<=arg<PARSER_END:q.append(arg)
                pc=nxt;continue
            pc=nxt
    if len(seen)!=786:raise ValueError(f'Original 04F7 parser graph drift: {len(seen)} instruction starts')
    covered={}
    for pc,(mn,mode,n,arg) in seen.items():
        for i in range(pc,pc+n):
            if i in covered:raise ValueError('Overlapping parser instruction footprints')
            covered[i]=pc
    if not all(PARSER_BEGIN<=a<PARSER_END for a in covered):raise ValueError('Parser source outside certified common window')
    if {pc for pc,(mn,mode,n,arg) in seen.items() if mn=='jmp' and mode=='ind'}!=INDIRECT_SITES:
        raise ValueError('Parser indirect dispatch graph drift')
    if any(i in covered for a,b in TABLES for i in range(a,b)):
        raise ValueError('Control/data conflict in original parser lookup tables')
    return seen,covered

def sound_roots(prg):
    b4=prg[4*16384:5*16384]
    b12=prg[12*16384:13*16384]
    def m(a,n=1):
        if not 0x8000<=a<a+n<=0xc000:raise ValueError('Original sound metadata pointer outside bank')
        return b12[a-0x8000:a+n-0x8000]
    refs=[]
    for sid in range(1,0x7e):
        ptr=int.from_bytes(m(0x8f60+(sid-1)*2,2),'little')
        if m(ptr)[0]!=0x04:continue
        count=m(ptr+1)[0]+1
        rec=m(ptr,2+count*3)
        for j in range(count):
            mode=rec[2+j*3];address=int.from_bytes(rec[3+j*3:5+j*3],'little')
            if not 0x87ae<=address<0xbe7e:raise ValueError('Root outside authenticated bank04 script span')
            if b4[address-0x8000]<0x10 or mode in (5,6):raise ValueError('Bank04 parser root mode changed')
            refs.append((sid,mode,address))
    roots=sorted({a for _,_,a in refs})
    if len(refs)!=102 or len(roots)!=96 or roots[0]!=0x87ae or roots[-1]!=0xbe7d:
        raise ValueError(f'Original bank04 producer-domain drift: {len(refs)} refs, {len(roots)} roots: {roots[-1:]!r}')
    if digest(('\n'.join(f'{a:04X}' for a in roots)).encode())!=ROOT_SHA:
        raise ValueError('Original raw0C bank04-root pointer identity mismatch')
    if digest(('\n'.join(f'{sid:02X},{mode:02X},{a:04X}' for sid,mode,a in refs)).encode())!=REF_SHA:
        raise ValueError('Original raw0C bank04-reference producer fingerprint mismatch')
    return refs,roots

def smoke():
    if sum(b-a for _,a,b,_ in WINDOWS)!=14032:
        raise ValueError('Historical script window length drift')
    if any(WINDOWS[i][2]!=WINDOWS[i+1][1] for i in range(3)):
        raise ValueError('Historic 04F7-04FA windows no longer contiguous')
    if PARSER_END-PARSER_BEGIN!=1965 or len(DISPATCH_TARGETS)!=20:
        raise ValueError('Original sound parser proof dimensions drift')
    for opcode,(_,mode,n) in proof.OPS.items():
        if mode=='rel' and n!=2:raise ValueError('Invalid NMOS relative operand length')
    print('PASS ROM-free bank04 14032-byte script/1965-byte parser contract')

def lift(prg):
    if len(prg)!=262144:raise ValueError('Expected JP 256K PRG')
    b4=prg[4*16384:5*16384]
    b5=prg[5*16384:6*16384]
    b12=prg[12*16384:13*16384]
    if b4[PARSER_BEGIN-0x8000:PARSER_END-0x8000]!=b5[PARSER_BEGIN-0x8000:PARSER_END-0x8000] or b4[PARSER_BEGIN-0x8000:PARSER_END-0x8000]!=b12[PARSER_BEGIN-0x8000:PARSER_END-0x8000]:
        raise ValueError('Bank04/05/0C common parser not byte-identical')
    seen,code=parser_instructions(b4)
    refs,roots=sound_roots(prg)
    for stage,lo,hi,want in WINDOWS:
        # For 04F7 the authenticated SHA includes the original header, parser
        # and beginning of the script, rather than only $87AE-$9209.
        if stage=='04F7':
            span=b4[0:0x920a-0x8000]
        else:span=b4[lo-0x8000:hi-0x8000]
        if digest(span)!=want:raise ValueError(stage+' authenticated original script source hash differs')
    fragments={}; mnemonic_bytes=len(code);table_bytes=PARSER_END-PARSER_BEGIN-mnemonic_bytes
    targets={PARSER_BEGIN,*DISPATCH_TARGETS}
    for pc,(mn,mode,n,arg) in seen.items():
        if (mn in BR or mn in ('jsr','jmp')) and mode!='ind' and isinstance(arg,int) and arg in seen:
            targets.add(arg)
    # Three identical physical copies of a source-authenticated executable
    # parser graph, each under its own explicit bank-qualified symbol prefix.
    for bank in (4,5,12):
        symbol=f'Bank{bank:02X}_Parser_'
        labels={pc:f'{symbol}{pc:04X}' for pc in sorted(targets) if pc in seen}
        lines=['; Original source-backed 6502 sound parser code + local lookup/data bytes.',
               '; Correspondence is byte-identical in VRC6 raw banks $04,$05,$0C.',
               '; CFG has 786 official instruction starts, 4 known indirect dispatchers.']
        pc=PARSER_BEGIN
        while pc<PARSER_END:
            if pc in seen:
                if pc in labels:lines.append(labels[pc]+':')
                mn,mode,n,arg=seen[pc]
                lines.append('    '+fmt(mn,mode,arg,labels))
                pc+=n
            else:
                start=pc
                while pc<PARSER_END and pc not in code:pc+=1
                for a in range(start,pc,16):
                    payload=b4[a-0x8000:min(a+16,pc)-0x8000]
                    if not payload:raise ValueError('Missing parser local data payload')
                    lines.append('    .byte '+','.join(f'${v:02X}' for v in payload))
        fragments.setdefault(f'raw{bank:02X}',[]).append({'a':PARSER_BEGIN,'b':PARSER_END,'src':f'04F7 original bank{bank:02X} parser; mnemonic and local data','lines':lines})
    refs_at=defaultdict(list)
    for sid,mode,a in refs:refs_at[a].append((sid,mode))
    lines=['; 04F7-04FA original bank04 script command and operand source.',
           '; 102 raw0C metadata references, 96 distinct rooted script streams.',
           '; Command streams are DATA, not NMOS 6502 instructions.']
    for index,a in enumerate(roots):
        b=roots[index+1] if index+1<len(roots) else 0xbe7e
        lines.append('; original metadata: '+', '.join(f'stage ${sid:02X} mode ${mode:02X}' for sid,mode in refs_at[a]))
        lines.append(f'Bank04_Script_{a:04X}:')
        for x in range(a,b,16):
            payload=b4[x-0x8000:min(x+16,b)-0x8000]
            lines.append('    .byte '+','.join(f'${v:02X}' for v in payload))
    fragments.setdefault('raw04',[]).append({'a':0x87ae,'b':0xbe7e,'src':'04F7-04FA producer-bounded bank04 script data','lines':lines})
    stats={'bank04_script_bytes':0xbe7e-0x87ae,'bank04_metadata_references':102,
           'bank04_script_roots':96,'common_parser_bytes_each':PARSER_END-PARSER_BEGIN,
           'identical_parser_physical_banks':['04','05','0C'],
           'per_parser_instruction_starts':len(seen),'per_parser_opcode_operand_bytes':mnemonic_bytes,
           'per_parser_lookup_and_local_data_bytes':table_bytes,
           'parser_copy_total_bytes':(PARSER_END-PARSER_BEGIN)*3,
           'newly_classified_source_bytes':(0xbe7e-0x87ae)+(PARSER_END-PARSER_BEGIN)*3,
           'source_boundary':'04F7..04FA producer-proof script windows and identical $8001-$87AD 6502 parser; no new strict PRG credit'}
    return fragments,stats
