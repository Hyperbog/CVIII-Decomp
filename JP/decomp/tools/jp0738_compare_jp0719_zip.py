#!/usr/bin/env python3
"""JP0738C: paired owner JP0718 Mesen ZIP / JP0719 native ZIP forensic bridge.

Read-only: all retail recordings stay local. A nearby nominal-frame sample
is NOT a cycle-synchronized parity test. This is a different native executable
and format from the later JP0737 CYCFRAME v2 engine.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import zipfile
from pathlib import Path

from jp0738_camera_window import (
    JP_SHA, components, file_sha256, original_frames,
)

BUTTON_BITS = {'A':128,'B':64,'SELECT':32,'START':16,
               'UP':8,'DOWN':4,'LEFT':2,'RIGHT':1}
FOCUS = (9376,9440,9504,9576,9760,10272,10328)
SIZES = {'nametables_4k.bin':4096,'palette_32.bin':32,
         'physical_chr_pages_8.bin':8,'cpu_ram_2k.bin':2048,
         'original_rgb24_256x240.bin':184320,'scanlines_1200.bin':1200}


def singleton(names: list[str], ending: str) -> str:
    found = [n for n in names if n.endswith(ending)]
    if len(found) != 1:
        raise ValueError('expected exactly one '+ending)
    return found[0]


def original_chr(zip_path: Path) -> dict[int, bytes]:
    with zipfile.ZipFile(zip_path) as z:
        n = singleton(z.namelist(), '-ppu.tsv')
        out = {}
        for line in z.read(n).decode('ascii').splitlines():
            if not line.startswith('S\t'):
                continue
            r = line.split('\t')
            if len(r) < 14:
                raise ValueError('truncated original PPU row')
            frame = int(r[2])
            if frame in FOCUS:
                b = bytes.fromhex(r[6])
                if len(b) != 8:
                    raise ValueError('wrong Mesen original CHR page count')
                out[frame] = b
        return out


def original_polls(zip_path: Path) -> list[tuple[int, int, int]]:
    with zipfile.ZipFile(zip_path) as z:
        rows = z.read(singleton(z.namelist(), '-input.tsv')).decode('ascii').splitlines()
    header = rows[0].split('\t')
    if len(header) != 5 or header[:2] != ['JP0718INPUT','1']:
        raise ValueError('expected original Mesen JP0718 input evidence')
    footer = rows[-1].split('\t')
    if footer[:1] != ['END'] or int(footer[2]) != len(rows)-2:
        raise ValueError('incomplete original Mesen input stream')
    out = []
    for line in rows[1:-1]:
        r = line.split('\t')
        if len(r) != 7 or r[0] != 'P':
            raise ValueError('bad Mesen input record')
        frame = int(r[1])  # ABSOLUTE FRAME; r[2] is the local frame!
        if out and frame <= out[-1][0]:
            raise ValueError('Mesen absolute input frame not strictly increasing')
        out.append((frame, int(r[4],16), int(r[5],16)))
    return out


def read_native(path: Path) -> tuple[dict[int,dict],str]:
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:
            raise ValueError('invalid native archive CRC')
        names = z.namelist()
        manifest = singleton(names, '-manifest.tsv')
        prefix = manifest[:-13]
        reader = csv.DictReader(io.StringIO(z.read(manifest).decode('ascii')),
                                delimiter='\t')
        rows = list(reader)
        if not rows:
            raise ValueError('native manifest empty')
        wanted = {}
        for r in rows:
            num = int(r['sample']); frame = int(r['sample_tick'])*8
            if frame in wanted:
                raise ValueError('duplicate native nominal frame')
            root = prefix+'-'+format(num,'06d')+'-'
            for suffix,size in SIZES.items():
                name = root+suffix
                if name not in names or z.getinfo(name).file_size != size:
                    raise ValueError('native buffer missing or wrong size: '+name)
            if min(abs(frame-t) for t in FOCUS) > 64:
                continue
            fields = {k:z.read(root+k) for k in
                      ('nametables_4k.bin','palette_32.bin',
                       'physical_chr_pages_8.bin','cpu_ram_2k.bin')}
            ram=fields['cpu_ram_2k.bin']
            if r['selector_343536'].lower() != ram[0x34:0x37].hex():
                raise ValueError('native manifest selector/RAM disagreement')
            wanted[frame] = dict(cycle=int(r['cycle_since_power']),
                                 ram=ram, nt=fields['nametables_4k.bin'],
                                 palette=fields['palette_32.bin'],
                                 chr=fields['physical_chr_pages_8.bin'])
        schedule = z.read(singleton(names,'-original-controller-input.input')).decode('ascii')
    return wanted,schedule


def validate_input(polls: list[tuple[int,int,int]], schedule: str) -> dict:
    changes = {1:{0:0},2:{0:0}}
    last_frame = -1
    for line in schedule.splitlines():
        line = line.split('#',1)[0].strip()
        if not line:
            continue
        fields=line.split()
        if len(fields)!=2 or ':' not in fields[1]:
            raise ValueError('invalid native input change')
        frame=int(fields[0]);port_s,buttons=fields[1].split(':')
        port=int(port_s)
        if port not in changes or frame < 0:
            raise ValueError('invalid native controller/frame')
        parts=[] if buttons=='-' else buttons.split('+')
        if len(parts)!=len(set(parts)) or any(p not in BUTTON_BITS for p in parts):
            raise ValueError('invalid button name')
        bits=0
        for p in parts: bits |= BUTTON_BITS[p]
        if frame < last_frame or frame in changes[port] and frame != 0:
            raise ValueError('invalid native input chronology')
        last_frame=frame
        changes[port][frame]=bits
    held={1:0,2:0}
    failures=[]
    for frame,p1,p2 in polls:
        for port in (1,2):
            held[port]=changes[port].get(frame,held[port])
        if (held[1],held[2])!=(p1,p2):
            failures.append(frame)
    if failures:
        raise ValueError('recorded input diverges at original absolute frame '+str(failures[0]))
    return {'original_polls_compared':len(polls),
            'mask_mismatches':0,'input_schedule_sha256':hashlib.sha256(schedule.encode('ascii')).hexdigest(),
            'cpu_controller_bus_read_parity_proved':False}


def snapshot_differences(o, n, physical_chr):
    original_cycle, original_ram, original_palette, original_nt=o
    ram=n['ram']
    return {
        'cpu_cycle_native_minus_original':n['cycle']-original_cycle,
        'cpu_ram_differing_bytes':sum(a!=b for a,b in zip(ram,original_ram)),
        'logical_nametable_differing_bytes':sum(a!=b for a,b in zip(n['nt'],original_nt)),
        'physical_chr_eight_pages_equal':n['chr']==physical_chr,
        'nonalias_palette_differing_bytes':sum(
            original_palette[i]!=n['palette'][i]
            for i in range(32) if i not in (16,20,24,28)),
        'original_player_camera':components(original_ram),
        'native_player_camera':components(ram),
    }


def compare(original:dict, chr_original:dict, native:dict) -> dict:
    rows=[]
    for frame in FOCUS:
        if frame not in original:
            rows.append({'original_frame':frame,'status':'MISSING_ORIGINAL_SAMPLE'})
            continue
        candidates=sorted(native)
        before=[t for t in candidates if t <= frame]
        after=[t for t in candidates if t >= frame]
        neighbors = sorted(set(
            ([before[-1]] if before and frame-before[-1]<=32 else [])+
            ([after[0]] if after and after[0]-frame<=32 else [])))
        if not neighbors:
            rows.append({'original_frame':frame,'status':'NO_NEARBY_NATIVE_SAMPLE'})
            continue
        current = []
        for nf in neighbors:
            row=snapshot_differences(original[frame],native[nf],
                                     chr_original[frame])
            row['native_nominal_frame']=nf
            row['native_minus_original_nominal_frames']=nf-frame
            row['same_cpu_cycle']=False
            current.append(row)
        rows.append({'original_frame':frame,'status':'NEARBY_NOT_CYCLE_ALIGNED',
                     'native_context':current})
    return {'schema':'JP0738-JP0718-original-vs-JP0719-native/v1',
            'native_generation':'JP0719, NOT JP0737 ROM-at-launch CYCFRAME',
            'same_frame_or_cpu_cycle_parity_proved':False,
            'first_divergent_cpu_writer_located':False,
            'certification':{'vpp':31,'strict_prg_bytes':49504,
                             'strict_prg_total':262144,'new_credit':0},
            'samples':rows}


def smoke():
    p=[(2,0,0),(3,1,0),(4,0,0)]
    inp='0 1:-\n0 2:-\n3 1:RIGHT\n4 1:-\n'
    assert validate_input(p,inp)['original_polls_compared']==3
    try:
        validate_input(p,inp.replace('3 1:RIGHT','3 1:LEFT'))
    except ValueError: pass
    else: raise AssertionError('bad input accepted')
    ram=bytearray(2048)
    ram[0x53]=93;ram[0x41c]=155;ram[0x565]=8
    rn=bytearray(ram);rn[0x53]=56;rn[0x41c]=44
    orig={9576:(100,bytes(ram),bytes(32),bytes(4096))}
    nat={9560:dict(cycle=90,ram=bytes(rn),nt=bytes(4096),
                   palette=bytes(32),chr=bytes(8))}
    item=compare(orig,{9576:bytes(8)},nat)
    sample=next(q for q in item['samples'] if q['original_frame']==9576)
    assert sample['native_context'][0]['native_player_camera']['camera']==56
    assert sample['native_context'][0]['original_player_camera']['camera']==93
    assert sample['native_context'][0]['cpu_ram_differing_bytes']==2
    assert item['certification']['new_credit']==0
    print('PASS JP0738 JP0718/JP0719 invented archive bridge, button masks and camera fields')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--smoke',action='store_true')
    p.add_argument('--rom',type=Path)
    p.add_argument('--mesen-zip',type=Path)
    p.add_argument('--native-jp0719-zip',type=Path)
    args=p.parse_args()
    if args.smoke:
        smoke();return
    if not (args.rom and args.mesen_zip and args.native_jp0719_zip):
        p.error('--rom, --mesen-zip and --native-jp0719-zip required')
    data=args.rom.read_bytes()
    if len(data)!=393232 or hashlib.sha256(data).hexdigest()!=JP_SHA:
        raise ValueError('not original authenticated Japanese Mapper24 ROM')
    with zipfile.ZipFile(args.mesen_zip) as z:
        if z.testzip() is not None:
            raise ValueError('invalid original Mesen archive CRC')
    orig=original_frames(args.mesen_zip)
    chr_orig=original_chr(args.mesen_zip)
    if any(f not in chr_orig for f in orig):
        raise ValueError('missing original physical CHR for snapshot')
    native,inp=read_native(args.native_jp0719_zip)
    result=compare(orig,chr_orig,native)
    result['authenticated_original_rom_sha256']=JP_SHA
    result['original_mesen_zip_sha256']=file_sha256(args.mesen_zip)
    result['native_jp0719_zip_sha256']=file_sha256(args.native_jp0719_zip)
    result['controller_intent']=validate_input(original_polls(args.mesen_zip),inp)
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=='__main__':
    main()
