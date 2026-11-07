#!/usr/bin/env python3
"""JP0740: validate original and native mapped CPU-write traces fail-closed.

It does NOT call an event 'first incorrect' based on same-numbered frames.
A common, cycle/register/physical-bank anchor is still required for that.
No private RAM dump, input schedule or original graphics committed here.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import tempfile
import zipfile

ROM_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
SHA1='a0f3b31d4e3b0d2ca2e8a34f91f14ad99a5ad11f'
WATCH=(0x62,0x53,0x54,0x55,0x63,0x6b,0x41c,0x438,
       0x4c4,0x4f2,0x509,0x520,0x565,0x5c1)
ANCHOR_FRAMES=(9376,9440,9504,9576)
FOCUS=(0x62,0x565,0x520,0x41c)

def authenticated_rom(path: Path) -> bytes:
    image=path.read_bytes()
    if (len(image)!=393232 or hashlib.sha256(image).hexdigest()!=ROM_SHA
        or image[:4]!=b'NES\x1a'
        or ((image[6]>>4)|(image[7]&0xF0))!=24):
        raise ValueError('original Japanese Mapper24 ROM identity mismatch')
    return image

def anchors_from_mesen(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise ValueError('original Mesen archive CRC mismatch')
        names=[n for n in archive.namelist() if n.endswith('-ram.tsv')]
        if len(names)!=1:raise ValueError('expected one JP0718 RAM TSV')
        rows=archive.read(names[0]).decode('ascii').splitlines()
    if not rows[0].startswith('JP0718RAM\t1\t'+SHA1):
        raise ValueError('Mesen original ROM header mismatch')
    found={}
    for row in rows[1:]:
        if not row.startswith('R\t'):continue
        parts=row.split('\t')
        frame=int(parts[2]);cycle=int(parts[3])
        ram=bytes.fromhex(parts[5])
        if len(ram)!=2048:raise ValueError('incomplete original RAM row')
        if frame in ANCHOR_FRAMES:
            if frame in found:raise ValueError('duplicate historical frame')
            found[frame]=(cycle,''.join(f'{ram[a]:02X}' for a in WATCH))
    if set(found)!=set(ANCHOR_FRAMES):
        raise ValueError('missing original Mesen anchor frames')
    return 'JP0740_ANCHORS\t1\n'+''.join(
        f'{f}\t{found[f][0]}\t{found[f][1]}\n' for f in ANCHOR_FRAMES)

def read_trace(path:Path,kind:str,rom:bytes)->dict:
    lines=path.read_text(encoding='ascii').splitlines()
    expected=('JP0740\t1\t'+SHA1+'\t17562' if kind=='mesen'
              else 'JP0740_NATIVE\t1')
    if not lines or lines[0]!=expected:
        raise ValueError('wrong '+kind+' trace header')
    if not lines[-1].startswith('END\tCOMPLETE\t'):
        raise ValueError('missing successful complete trace footer')
    ordinal=0;frame_prev=-1;cycle_prev=-1
    anchors=[]
    counts=Counter()
    writers=Counter()
    modes=Counter()
    first={}
    for row in lines[1:-1]:
        p=row.split('\t')
        if p[0]=='ANCHOR_OK':
            if kind!='mesen' or len(p)!=3:
                raise ValueError('unexpected source anchor')
            anchors.append(int(p[1]));continue
        if p[0]=='ANCHOR_FAIL':
            raise ValueError('original gameplay replay diverged from archived anchor')
        if p[0]=='W' and len(p)==10:
            seq,frame,cycle=map(int,p[1:4])
            addr=int(p[4],16);old=int(p[5],16);new=int(p[6],16)
            bus=int(p[7],16);pc=int(p[8],16);phys=int(p[9],16)
            if addr!=0x4016 and (addr not in WATCH or (bus&0x7FF)!=addr):
                raise ValueError('invalid CPU RAM target/mirror')
            if not 0<=old<=255 or not 0<=new<=255:
                raise ValueError('write data outside 8-bit range')
            counts[f'W_{addr:04X}']+=1
            writers[(addr,pc,phys)]+=1
            if addr==0x62:modes[new]+=1
            first.setdefault(f'{addr:04X}',{'frame':frame,'cycle':cycle,
                 'pc':f'{pc:04X}','physical_prg_offset':f'{phys:05X}',
                 'old':f'{old:02X}','new':f'{new:02X}'})
        elif p[0]=='R' and len(p)==8:
            seq,frame,cycle=map(int,p[1:4])
            addr=int(p[4],16);new=int(p[5],16)
            pc=int(p[6],16);phys=int(p[7],16)
            if addr not in (0x4016,0x4017) or not 0<=new<=255:
                raise ValueError('invalid controller bus read')
            counts[f'R_{addr:04X}']+=1
        else:
            raise ValueError('corrupt CPU bus event row')
        if seq!=ordinal+1 or frame<frame_prev or cycle<cycle_prev:
            raise ValueError('nonmonotone trace event ordering')
        if phys!=0xFFFFF and not (pc>=0x8000 and
                0<=phys<262144 and (phys&0xFFF)==(pc&0xFFF)):
            raise ValueError('invalid physical mapped opcode PC')
        ordinal=seq;frame_prev=frame;cycle_prev=cycle
    footer=lines[-1].split('\t')
    if kind=='mesen':
        if (len(footer)!=5 or int(footer[2])!=ordinal or
           int(footer[4])<3 or not {9440,9504,9576}.issubset(anchors)):
            raise ValueError('original Mesen anchors/footer missing')
    elif len(footer)!=3 or int(footer[2])!=ordinal:
        raise ValueError('native trace footer count mismatch')
    return {'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'kind':kind,'event_count':ordinal,'first_write_by_address':first,
            'counts':dict(sorted(counts.items())),
            'mode62_write_values':{f'{k:02X}':v for k,v in sorted(modes.items())},
            'watched_writer_pc_counts':[
                {'address':f'{addr:04X}','cpu_pc':f'{pc:04X}',
                 'physical_prg_offset':f'{phys:05X}' if phys!=0xFFFFF else None,
                 'count':n}
                for (addr,pc,phys),n in writers.most_common()],
            'verified_original_anchor_frames':anchors}

def compare(original:dict,native:dict)->dict:
    return {'schema':'JP0740-CPU-write-observer/v1',
        'original_rom_sha256':ROM_SHA,'original':original,'native':native,
        'source_and_native_write_provenance_available':True,
        'first_incorrect_write_certified':False,
        'why_not':'no independently established cross-engine CPU cycle/register/mapper anchor; do not align by frame or write ordinal',
        'native_frame_index_is_zero_based':True,
        'vpp':31,'strict_prg_bytes':49504,'strict_prg_total':262144,
        'new_certified_bytes':0}

def smoke()->None:
    fake=bytes(393232)
    with tempfile.TemporaryDirectory() as t:
        o=Path(t)/'source.tsv';n=Path(t)/'native.tsv'
        hdr='JP0740\t1\t'+SHA1+'\t17562'
        rows=[hdr,
            'W\t1\t9440\t101\t0062\t02\t01\t0062\t86E2\t386E2',
            'R\t2\t9440\t102\t4016\t01\t86E4\t386E4',
            'ANCHOR_OK\t9440\t103',
            'ANCHOR_OK\t9504\t200','ANCHOR_OK\t9576\t300',
            'END\tCOMPLETE\t2\t100\t3']
        o.write_text('\n'.join(rows)+'\n')
        n.write_text('JP0740_NATIVE\t1\n'
            'W\t1\t9439\t102\t0062\t02\t02\t0062\t936E\t3936E\n'
            'END\tCOMPLETE\t1\n')
        a=read_trace(o,'mesen',fake);b=read_trace(n,'native',fake)
        result=compare(a,b)
        assert result['first_incorrect_write_certified'] is False
        assert a['mode62_write_values']=={'01':1}
        for damaged in (rows[:-1],
                        [*rows[:-1],'END\tINCOMPLETE\t2\t100\t3'],
                        [rows[0],rows[1].replace('386E2','386E3'),*rows[2:]]):
            o.write_text('\n'.join(damaged)+'\n')
            try:read_trace(o,'mesen',fake)
            except ValueError:pass
            else:raise AssertionError('corrupt provenance accepted')
    print('PASS JP0740 ROM-free source/native CPU event schema and hard rejection')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--smoke',action='store_true')
    p.add_argument('--rom',type=Path)
    p.add_argument('--make-original-anchors',type=Path)
    p.add_argument('--anchor-out',type=Path)
    p.add_argument('--original-trace',type=Path)
    p.add_argument('--native-trace',type=Path)
    a=p.parse_args()
    if a.smoke:smoke();return
    if not a.rom:p.error('--rom required')
    image=authenticated_rom(a.rom)
    if a.make_original_anchors:
        if not a.anchor_out:p.error('--anchor-out required')
        a.anchor_out.write_text(anchors_from_mesen(a.make_original_anchors))
        print('PASS original private owner-Mesen checkpoint anchors generated')
        return
    if not(a.original_trace and a.native_trace):
        p.error('require --original-trace and --native-trace')
    print(json.dumps(compare(read_trace(a.original_trace,'mesen',image),
                             read_trace(a.native_trace,'native',image)),indent=2))

if __name__=='__main__':main()
