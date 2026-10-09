#!/usr/bin/env python3
"""Cross-NES cartridge inventory and ROM-free portable signature/audit infrastructure.

Candidate evidence ONLY: exact windows and operand-masked disassemblies do not
establish runtime equivalence. Supports iNES, NES2, .FDS headered/raw geometry.
No copyrighted ROM payload is ever written to output. Standard library only.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

OPROWS = '''
00:BRK:i 01:ORA:x 05:ORA:z 06:ASL:z 08:PHP:i 09:ORA:m 0A:ASL:a 0D:ORA:A 0E:ASL:A
10:BPL:r 11:ORA:y 15:ORA:X 16:ASL:X 18:CLC:i 19:ORA:Y 1D:ORA:B 1E:ASL:B
20:JSR:A 21:AND:x 24:BIT:z 25:AND:z 26:ROL:z 28:PLP:i 29:AND:m 2A:ROL:a 2C:BIT:A 2D:AND:A 2E:ROL:A
30:BMI:r 31:AND:y 35:AND:X 36:ROL:X 38:SEC:i 39:AND:Y 3D:AND:B 3E:ROL:B
40:RTI:i 41:EOR:x 45:EOR:z 46:LSR:z 48:PHA:i 49:EOR:m 4A:LSR:a 4C:JMP:A 4D:EOR:A 4E:LSR:A
50:BVC:r 51:EOR:y 55:EOR:X 56:LSR:X 58:CLI:i 59:EOR:Y 5D:EOR:B 5E:LSR:B
60:RTS:i 61:ADC:x 65:ADC:z 66:ROR:z 68:PLA:i 69:ADC:m 6A:ROR:a 6C:JMP:d 6D:ADC:A 6E:ROR:A
70:BVS:r 71:ADC:y 75:ADC:X 76:ROR:X 78:SEI:i 79:ADC:Y 7D:ADC:B 7E:ROR:B
81:STA:x 84:STY:z 85:STA:z 86:STX:z 88:DEY:i 8A:TXA:i 8C:STY:A 8D:STA:A 8E:STX:A
90:BCC:r 91:STA:y 94:STY:X 95:STA:X 96:STX:Z 98:TYA:i 99:STA:Y 9A:TXS:i 9D:STA:B
A0:LDY:m A1:LDA:x A2:LDX:m A4:LDY:z A5:LDA:z A6:LDX:z A8:TAY:i A9:LDA:m AA:TAX:i AC:LDY:A AD:LDA:A AE:LDX:A
B0:BCS:r B1:LDA:y B4:LDY:X B5:LDA:X B6:LDX:Z B8:CLV:i B9:LDA:Y BA:TSX:i BC:LDY:B BD:LDA:B BE:LDX:Y
C0:CPY:m C1:CMP:x C4:CPY:z C5:CMP:z C6:DEC:z C8:INY:i C9:CMP:m CA:DEX:i CC:CPY:A CD:CMP:A CE:DEC:A
D0:BNE:r D1:CMP:y D5:CMP:X D6:DEC:X D8:CLD:i D9:CMP:Y DD:CMP:B DE:DEC:B
E0:CPX:m E1:SBC:x E4:CPX:z E5:SBC:z E6:INC:z E8:INX:i E9:SBC:m EA:NOP:i EC:CPX:A ED:SBC:A EE:INC:A
F0:BEQ:r F1:SBC:y F5:SBC:X F6:INC:X F8:SED:i F9:SBC:Y FD:SBC:B FE:INC:B
'''
MODES = {'i':1,'a':1,'z':2,'X':2,'Z':2,'x':2,'y':2,'m':2,'r':2,
         'A':3,'B':3,'Y':3,'d':3}
OPCODES = {int(x.split(':')[0],16):(x.split(':')[1],x.split(':')[2])
           for x in OPROWS.split()}
assert len(OPCODES)==151


def sha(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()


def nes2_size(low:int,high:int,unit:int)->int:
    if high==0xF:
        # NES2 exponent/multiplier: 2**exponent * (2*multiplier+1).
        return (1<<(low>>2)) * (2*(low&3)+1)
    return ((high<<8)|low)*unit


def fds_info(data:bytes)->dict[str,Any]:
    if data[:4]==b'FDS\x1a':
        if len(data)<16:raise ValueError('truncated FDS header')
        payload=data[16:]
        if not payload or len(payload)%65500:raise ValueError('FDS image has incomplete 65500-byte side(s)')
        count=len(payload)//65500
        if data[4] not in (0,count):raise ValueError('FDS header side count conflicts with image')
        return {'format':'FDS-headered','file_sha256':sha(data), 'side_count':count,
                'side_payload_bytes':65500,'bios_included':False,
                'evidence_level':'format-only; disk checksums, contents and BIOS ABI unverified'}
    if len(data)>=65500 and len(data)%65500==0:
        # Geometry alone is insufficient to prove the actual disk format.
        return {'format':'FDS-raw-candidate','file_sha256':sha(data),
                'side_count':len(data)//65500,'side_payload_bytes':65500,
                'bios_included':False,'evidence_level':'geometry-only; not FDS identity proof'}
    raise ValueError('unrecognized NES/FDS image')


def load(path:str|Path)->tuple[dict[str,Any],bytes]:
    data=Path(path).read_bytes()
    if data[:4]!=b'NES\x1a':return fds_info(data),b''
    if len(data)<16:raise ValueError('truncated iNES header')
    h=data[:16];nes2=(h[7]&0x0C)==0x08
    mapper=(h[6]>>4)|(h[7]&0xF0)
    if nes2:
        mapper|=(h[8]&15)<<8
        prg_size=nes2_size(h[4],h[9]&15,16384)
        chr_size=nes2_size(h[5],h[9]>>4,8192)
        fmt='NES2.0'
    else:
        prg_size=h[4]*16384;chr_size=h[5]*8192
        fmt='iNES1'
    if prg_size>64*1024*1024 or chr_size>64*1024*1024:
        raise ValueError('unsupported gigantic PRG/CHR size')
    trainer=512 if h[6]&4 else 0
    off=16+trainer;end=off+prg_size+chr_size
    if len(data)<end:raise ValueError('truncated PRG/CHR region')
    prg=data[off:off+prg_size];chr_=data[off+prg_size:end]
    warnings=[]
    if not nes2 and any(h[12:16]):warnings.append('legacy/dirty iNES header; high mapper bits may be unreliable')
    if len(data)>end:warnings.append('extra trailing bytes; inspect PlayChoice/title/misc data before attributing')
    if h[6]&8: warnings.append('four-screen nametable flag; mapper/board must resolve')
    out={'format':fmt,'file_sha256':sha(data), 'mapper':mapper,
         'submapper':(h[8]>>4) if nes2 else None,
         'trainer_bytes':trainer,'prg_bytes':len(prg),'chr_bytes':len(chr_),
         'prg_sha256':sha(prg),'chr_sha256':sha(chr_),
         'battery_flag':bool(h[6]&2),
         'mirroring_header':'vertical' if (h[6]&1) else 'horizontal',
         'prg_8k_banks':[{'index':i//8192,'sha256':sha(prg[i:i+8192])}
                         for i in range(0,len(prg),8192)],
         'warnings':warnings, 'trust':'container bytes only; not mapper/runtime proof'}
    # Vector mapping is ONLY statically determined for these bank arrangements.
    if mapper in (24,26) and len(prg)>=8192:
        last=prg[-8192:]
        out['fixed_vectors']={k:hex(int.from_bytes(last[n:n+2],'little'))
                              for k,n in [('nmi',0x1FFA),('reset',0x1FFC),('irq',0x1FFE)]}
    elif mapper==0 and len(prg) in (16384,32768):
        last=prg[-16384:]
        start=len(last)-6
        out['fixed_vectors']={k:hex(int.from_bytes(last[start+n:start+n+2],'little'))
                              for k,n in [('nmi',0),('reset',2),('irq',4)]}
    return out,prg


def normalized_instructions(data:bytes)->tuple[bytes,int]:
    """For KNOWN instruction-aligned code only: mask JSR/JMP abs target bytes.
    Preserves all RAM/data operands, relative branches and indirect pointers.
    Rejects undecoded bytes; never guesses that a region is code.
    """
    out=bytearray(data);p=0;count=0
    while p<len(out):
        code=OPCODES.get(data[p]);
        if code is None:raise ValueError(f'unsupported opcode {data[p]:02x} at +{p:04x}')
        m,mode=code;length=MODES[mode]
        if p+length>len(out):raise ValueError('region ends midway through opcode operands')
        if (m,mode) in (('JSR','A'),('JMP','A')):
            out[p+1:p+3]=b'\x00\x00'
        count+=1;p+=length
    return bytes(out),count


def anchored_compare(prg_a:bytes,prg_b:bytes,manifest:dict[str,Any])->dict[str,Any]:
    """Two caller-supplied, preidentified anchored regions; cannot certify semantics."""
    left,right=manifest['left'],manifest['right']
    size=left['size']
    if not 16<=size<=65536 or size!=right['size']:
        raise ValueError('require equal anchored spans 16..65536 bytes')
    a=left['prg_offset'];b=right['prg_offset']
    if not (0<=a<=len(prg_a)-size and 0<=b<=len(prg_b)-size):
        raise ValueError('anchor outside PRG')
    x=prg_a[a:a+size];y=prg_b[b:b+size]
    if 'sha256' in left and sha(x)!=left['sha256']:raise ValueError('left anchor fingerprint mismatch')
    if 'sha256' in right and sha(y)!=right['sha256']:raise ValueError('right anchor fingerprint mismatch')
    equal=x==y
    normalized=False;insn=None;error=None
    if manifest.get('kind')=='code' and manifest.get('code_boundaries_verified') is True:
        try:
            nx,n1=normalized_instructions(x);ny,n2=normalized_instructions(y)
            normalized=nx==ny and n1==n2;insn=n1
        except ValueError as exc:error=str(exc)
    return {'name':manifest.get('name','unnamed'),'kind':manifest.get('kind','unknown'),
            'span_bytes':size,'left_offset':a,'right_offset':b,
            'left_sha256':sha(x),'right_sha256':sha(y),'exact_equal':equal,
            'opcode_aligned_normalized_match':normalized if not equal else normalized,
            'decoded_instruction_count':insn,'decode_error':error,
            'level':'candidate equivalence; execution/mapper/memory contracts require independent audit',
            'promoted_semantic_bytes':0}


def sliding_matches(left:bytes,right:bytes,window:int=32,stride:int=256,max_examples:int=24)->dict[str,Any]:
    """All-offset exact-byte discovery; never code classification or coverage."""
    if window<16 or stride<1:raise ValueError('window >=16 and stride >=1')
    hits=Counter();examined=0;skipped=0;unique=0;examples=[]
    for off in range(0,max(len(left)-window+1,0),stride):
        chunk=left[off:off+window]
        if len(set(chunk))<4 or max(Counter(chunk).values())>int(window*.80):
            skipped+=1;continue
        examined+=1;starts=[];p=right.find(chunk)
        while p>=0:
            starts.append(p)
            if len(starts)>64:break  # repeated patterns kept ambiguous
            p=right.find(chunk,p+1)
        if starts:
            hits[len(starts)]+=1
            if len(starts)==1:unique+=1
            if len(examples)<max_examples:
                examples.append({'left_prg_offset':off,'right_candidate_offsets':starts[:6],
                                 'right_match_count_at_least':len(starts),
                                 'window_sha256':sha(chunk)})
    return {'window_bytes':window,'left_stride':stride,
            'candidate_windows_tested':examined,'low_information_skipped':skipped,
            'candidate_windows_with_unique_target':unique,
            'candidate_windows_with_any_match':sum(hits.values()),
            'multiplicity_histogram':{str(k):v for k,v in sorted(hits.items())},
            'example_hashes_and_offsets':examples,
            'semantically_promoted_bytes':0,
            'note':'Candidates overlap and can be data. Unique target != live routine equivalence.'}


def compare(path_a:str,path_b:str,window:int=32,stride:int=256,manifests:list[dict]|None=None)->dict:
    ai,a=load(path_a);bi,b=load(path_b)
    if ai['format'].startswith('FDS') or bi['format'].startswith('FDS'):
        raise ValueError('FDS game code comparison requires disk-file extraction/BIOS loading first')
    if not a or not b:raise ValueError('empty PRG')
    return {'schema':1,'left':{k:v for k,v in ai.items() if k!='prg_8k_banks'},
            'right':{k:v for k,v in bi.items() if k!='prg_8k_banks'},
            'same_mapper':ai['mapper']==bi['mapper'],
            'hardware_adapter_required':ai['mapper']!=bi['mapper'],
            'exact_window_discovery':sliding_matches(a,b,window,stride),
            'anchored_audits':[anchored_compare(a,b,x) for x in (manifests or [])],
            'strict_new_verified_bytes':0,'gameplay_equivalence_proved':False,
            'ROM_byte_data_in_output':False}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='mode',required=True)
    a=sub.add_parser('inventory');a.add_argument('rom');a.add_argument('--out')
    c=sub.add_parser('compare');c.add_argument('left');c.add_argument('right');c.add_argument('--window',type=int,default=32);c.add_argument('--stride',type=int,default=256);c.add_argument('--manifest',action='append');c.add_argument('--out')
    args=p.parse_args()
    if args.mode=='inventory':result,_=load(args.rom)
    else:
        manifests=[]
        for f in args.manifest or []:
            j=json.loads(Path(f).read_text())
            manifests+=j if isinstance(j,list) else [j]
        result=compare(args.left,args.right,args.window,args.stride,manifests)
    output=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.out:Path(args.out).write_text(output)
    else:print(output)

if __name__=='__main__':main()
