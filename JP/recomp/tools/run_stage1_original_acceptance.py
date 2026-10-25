#!/usr/bin/env python3
"""Stage 1 original-JP power-on replay acceptance: one run, four canonical gates.

This is an acceptance command, not a synthetic proof or a new JP checkpoint.
All original ROM, owner input and frame logs remain owner-private.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import zipfile

JP_SHA256='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
FRAMES=(9376,9440,9504,9576)
TRANSITION_FRAME=9277  # Original DEC $36 source event at fixed $D3E9
FRAME_STRUCT=struct.Struct('<9I')
# Actual original Stage-1 functionality, not speculative unrelated RAM bytes.
WATCH=(0x34,0x35,0x36,0x53,0x54,0x62,0x63,0x65,0x28,0x2a,
       0x041c,0x0438,0x04c4,0x04f2,0x0509,0x0520,0x0565,0x05c1)
LABEL={0x34:'area',0x35:'room_group',0x36:'room_number',
       0x53:'camera_x',0x54:'camera_x_hi',0x62:'scroll_mode',
       0x63:'camera_boundary',0x65:'scroll_hi',0x28:'button_press',
       0x2a:'button_held',0x041c:'player_y',0x0438:'player_x',
       0x04c4:'player_x_subpixel',0x04f2:'player_vx',
       0x0509:'player_vx_subpixel',0x0520:'player_vy',
       0x0565:'player_action',0x05c1:'actor_collision'}
# The 4016/4017 bus-phase regressions are required to guard the two first
# observed input failures. Their input values are checked in dedicated traces,
# not guessed from periodic RAM frame logs.
BUS_GATES=(6839,7536)

def original_snapshots(archive:Path):
    with zipfile.ZipFile(archive) as z:
        if z.testzip():raise ValueError('original capture ZIP has failed CRC')
        names=[v for v in z.namelist() if v.endswith('-ram.tsv')]
        if len(names)!=1:raise ValueError('original RAM member missing/ambiguous')
        rows=z.read(names[0]).decode('ascii').splitlines()
    snapshots={}
    for line in rows:
        if not line.startswith('R\t'):continue
        r=line.split('\t')
        if len(r)<6:raise ValueError('bad archived original RAM row')
        frame=int(r[2])
        if frame in FRAMES:
            ram=bytes.fromhex(r[5])
            if len(ram)!=2048:raise ValueError('original RAM length mismatch')
            snapshots[frame]=(int(r[3]),ram)
    if set(snapshots)!=set(FRAMES):raise ValueError('missing exact owner RAM anchors')
    return snapshots

def native_snapshots(path:Path):
    result={}
    with path.open('rb') as f:
        if f.read(8)!=b'CYCFRAME' or f.read(4)!=struct.pack('<I',2):
            raise ValueError('unsupported CYCFRAME header/version')
        prev=-1
        while row:=f.read(FRAME_STRUCT.size):
            if len(row)!=FRAME_STRUCT.size:raise ValueError('truncated frame entry')
            frame,low,high,*lengths=FRAME_STRUCT.unpack(row)
            if frame<=prev or any(n>2000000 for n in lengths):
                raise ValueError('out-of-order or impossible frame entry')
            prev=frame
            payload_size=288+sum(lengths)
            if frame not in FRAMES and frame!=TRANSITION_FRAME:
                f.seek(payload_size,1);continue
            if lengths[0]!=2048:raise ValueError('native RAM size mismatch')
            f.seek(288,1)
            ram=f.read(2048)
            if len(ram)!=2048:raise ValueError('truncated native RAM')
            f.seek(sum(lengths)-2048,1)
            result[frame]=((high<<32)|low,ram)
    if set(result)!=set(FRAMES)|{TRANSITION_FRAME}:
        raise ValueError('native trace lacks required room transition or Stage 1 frames')
    return result

def evaluate(original,native):
    # The owner source event at local 9277 executes DEC $36:03->02.
    # Gate its result independently: a later matching room is not enough.
    transition_room=native[TRANSITION_FRAME][1][0x36]
    transition_pass=transition_room==2
    entries=[]
    passed=transition_pass
    for frame in FRAMES:
        oc,oa=original[frame]
        nc,na=native[frame]
        mismatches=[{'address':f'{i:04X}','state':LABEL.get(i,'unknown'),
                     'original':f'{oa[i]:02X}','native':f'{na[i]:02X}'}
                    for i in WATCH if oa[i]!=na[i]]
        passed=passed and not mismatches
        entries.append({'frame':frame,
                        'original_cycles':oc,'native_cycles':nc,
                        'native_minus_original_cycles':nc-oc,
                        'camera_original':oa[0x53]|(oa[0x54]<<8),
                        'camera_native':na[0x53]|(na[0x54]<<8),
                        'watched_mismatches':mismatches,
                        'all_ram_byte_mismatches':sum(a!=b for a,b in zip(oa,na))})
    return {
      'schema':'CVIII-stage1-original-JP-runtime-acceptance/v1',
      'accepted_watched_checkpoints':bool(passed),
      'stage1_full_hardware_parity_certified':False,
      'status':'PASS_WATCHED_CHECKPOINTS_ONLY' if passed
               else 'FAIL_ORIGINAL_STAGE1_GAMEPLAY',
      'note':'RAM snapshot parity is necessary, not complete CPU bus/PPU/audio parity',
      'requires_separate_controller_dma_bus_gates':list(BUS_GATES),
      'original_room_transition':{'frame':TRANSITION_FRAME,
                                  'source_cpu_pc':'D3E9',
                                  'address':'0036','expected_value':'02',
                                  'native_value':f'{transition_room:02X}',
                                  'passed':transition_pass},
      'owner_last_playtested_version':'JP0722',
      'certificate_unchanged':{'vpp':31,'strict_prg_bytes':49504,'strict_prg_total':262144},
      'frames':entries
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--owner-capture',type=Path,required=True)
    p.add_argument('--native-exe',type=Path)
    p.add_argument('--native-frame-log',type=Path,
                   help='Existing verified CYCFRAME from a power-on replay')
    p.add_argument('--report',type=Path,required=True)
    a=p.parse_args()
    if bool(a.native_exe)==bool(a.native_frame_log):
        p.error('specify one of --native-exe or --native-frame-log')
    image=a.rom.read_bytes()
    if len(image)!=393232 or hashlib.sha256(image).hexdigest()!=JP_SHA256:
        p.error('authenticated original Japanese ROM hash/size mismatch')
    base=original_snapshots(a.owner_capture)
    if a.native_exe:
        # Import the existing strict original absolute-to-local input converter.
        src=Path(__file__).resolve().parents[2]/'decomp'/'tools'
        sys.path.insert(0,str(src))
        from jp0743_native_input_epoch import read_source,convert
        input_data,_=read_source(a.owner_capture)
        schedule,metadata=convert(input_data)
        if metadata['owner_input_polls']!=17562:
            raise ValueError('incomplete owner input recording')
        with tempfile.TemporaryDirectory(prefix='cviii-stage1-private-') as t:
            schedule_path=Path(t)/'corrected-local.input'
            log_path=Path(t)/'native.cycframe'
            schedule_path.write_text(schedule,encoding='ascii')
            cmd=[str(a.native_exe.resolve()),str(a.rom.resolve()),
                 '--headless','--edition','original','--frames','9577',
                 '--input',str(schedule_path),
                 '--frame-log',str(log_path),'--frame-log-frames','9277:9576',
                 '--frame-log-at','mesen']
            result=subprocess.run(cmd,capture_output=True,text=True,timeout=3600)
            if result.returncode:
                raise RuntimeError('native power-on replay rejected, exit '+
                                   str(result.returncode)+'\n'+result.stderr[-1000:])
            output=evaluate(base,native_snapshots(log_path))
    else:
        output=evaluate(base,native_snapshots(a.native_frame_log))
    output['original_japanese_sha256']=JP_SHA256
    output['owner_capture_sha256']=hashlib.sha256(a.owner_capture.read_bytes()).hexdigest()
    a.report.write_text(json.dumps(output,indent=2)+'\n',encoding='utf8')
    print(output['status']+' | source room transition '+str(TRANSITION_FRAME)+
          ' and watched checkpoint frames '+','.join(map(str,FRAMES)))
    for entry in output['frames']:
        print(f"  f={entry['frame']} camera={entry['camera_original']}/{entry['camera_native']}"
              f" observed_mismatches={len(entry['watched_mismatches'])}")
    return 0 if output['accepted_watched_checkpoints'] else 1

if __name__=='__main__':
    sys.exit(main())
