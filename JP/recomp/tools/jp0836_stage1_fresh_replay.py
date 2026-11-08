#!/usr/bin/env python3
"""JP0836 private JP0835 -> native controller replay and actor lifetime check.

No published ROM, controller, RAM, or native output. Native gameplay parity
requires a real NESRecomp run, not merely the successful source ZIP audit.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import zipfile

ROM_SHA256 = '958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
ROM_SHA1 = 'a0f3b31d4e3b0d2ca2e8a34f91f14ad99a5ad11f'
END_FRAME = 3900
FIRST_COMPARISON = 3090
BUTTONS = ((128,'A'),(64,'B'),(32,'SELECT'),(16,'START'),
           (8,'UP'),(4,'DOWN'),(2,'LEFT'),(1,'RIGHT'))


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def sha(value):
    return hashlib.sha256(value).hexdigest()


def expected_mask(frame):
    """Independent transcription of JP0835's *intent*, not bus-phase proof."""
    if frame < 1502:
        start = any(a <= frame <= a+4 for a in (50,170,270,370))
        return (16 if start else 0) | (1 if frame >= 780 else 0) | (
            128 if frame >= 820 else 0)
    if frame < 2602:
        return 129
    tick = frame - 2602
    return 1 | (128 if 4 <= tick % 43 <= 9 else 0) | (
        8 if 34 <= tick % 107 <= 65 else 0)


def actor_parent(ram, slot):
    if ram[0x54e+slot] == 0x3d and ram[0x470+slot]&4:
        parent = ram[0x645+slot]
        if parent in (3,4):
            return parent
    return None


def parse_archive(path):
    with zipfile.ZipFile(path) as z:
        need(z.testzip() is None, 'corrupt private source archive')
        names = z.namelist()
        inputs = [n for n in names if n.endswith('_input.tsv')]
        rams = [n for n in names if n.endswith('_ram.tsv')]
        need(len(inputs)==len(rams)==1, 'expected one JP0835 input and RAM TSV')
        input_bytes, ram_bytes = z.read(inputs[0]), z.read(rams[0])
    i_lines = input_bytes.decode('ascii').splitlines()
    r_lines = ram_bytes.decode('ascii').splitlines()
    head = f'1\t{ROM_SHA1}\t1'
    need(i_lines[0] == 'JP0835INPUT\t'+head and
         r_lines[0] == 'JP0835RAM\t'+head,
         'wrong Japanese ROM identity, capture protocol or start epoch')
    need(i_lines[-1] == f'END\tCOMPLETE\t{END_FRAME}\t{END_FRAME+1}',
         'input footer incomplete, frame epoch mismatched')
    need(len(i_lines) == END_FRAME+2, 'missing original controller poll')
    masks={}
    for frame, line in enumerate(i_lines[1:-1], 1):
        fields=line.split('\t')
        need(len(fields)==4 and fields[:2]==['P',str(frame)] and
             len(fields[2])==len(fields[3])==2,
             'duplicate/missing/invalid original controller frame')
        pair=(int(fields[2],16),int(fields[3],16))
        need(pair==(expected_mask(frame),0),
             f'original input schedule differs at local frame {frame}')
        masks[frame]=pair
    frames={}; previous_cycle=-1; source_counts={3:0,4:0}; first_both=None
    for line in r_lines[1:-1]:
        fields=line.split('\t')
        need(len(fields)==4 and fields[0]=='R', 'malformed original RAM row')
        frame,cycle=int(fields[1]),int(fields[2]); ram=bytes.fromhex(fields[3])
        need(frame not in frames and len(ram)==2048 and cycle>previous_cycle,
             'duplicate original frame, invalid RAM or nonmonotonic CPU cycles')
        need(tuple(ram[k] for k in (0x34,0x35,0x36))==(0,1,0),
             'original reference escaped Stage 1-02')
        frames[frame]=ram;previous_cycle=cycle
        pairs={(slot, actor_parent(ram,slot)) for slot in range(1,13)}
        for parent in source_counts:
            source_counts[parent]+=sum(p==parent for _,p in pairs)
        if (1,3) in pairs and (2,4) in pairs and first_both is None:
            first_both=frame
    need(len(frames)>=2 and list(frames)==list(range(min(frames),max(frames)+1)),
         'non-consecutive original Stage 1 RAM frames')
    footer=r_lines[-1]
    expected_footer=(f'END\tCOMPLETE\t{len(frames)}\t'
                     f'{source_counts[3]}\t{source_counts[4]}')
    need(footer==expected_footer, 'original footer does not match real actor samples')
    need(min(frames)<=FIRST_COMPARISON and max(frames)==END_FRAME and
         first_both is not None and first_both>FIRST_COMPARISON,
         'Stage 1 reference lacks pre-spawn and complete actor window')
    for frame in range(first_both,END_FRAME+1):
        ram=frames[frame]
        need(actor_parent(ram,1)==3 and actor_parent(ram,2)==4,
             f'original source-linked actor absent at frame {frame}')
    return masks,frames,{
        'schema':'CVIII-JP0836-JP0835-source-provenance/v1',
        'archive_sha256':sha(path.read_bytes()),'original_input_sha256':sha(input_bytes),
        'original_ram_sha256':sha(ram_bytes),'first_ram_frame':min(frames),
        'last_ram_frame':max(frames),'ram_frames':len(frames),
        'first_both_source_actors_frame':first_both,
        'consecutive_both_source_actor_frames':END_FRAME-first_both+1,
        'source3_samples':source_counts[3],'source4_samples':source_counts[4],
        'replay_input_epoch':'native frame 0 empty; source local poll 1 -> native frame 1',
        'cpu_bus_input_phase_verified':False,'native_gameplay_parity_verified':False,
    }


def buttons(mask):
    return '+'.join(name for bit,name in BUTTONS if mask&bit) or '-'


def schedule(masks):
    lines=['# JP0836 JP0835 source-local frame intent; actual CPU bus phase unverified',
           '0 1:-','0 2:-']
    last=(0,0)
    for frame in range(1,END_FRAME+1):
        pair=masks[frame]
        for port in (0,1):
            if pair[port]!=last[port]:
                lines.append(f'{frame} {port+1}:{buttons(pair[port])}')
        last=pair
    return '\n'.join(lines)+'\n'


def write_private(path, contents):
    if path.exists():
        need(path.read_bytes()==contents, f'existing private output differs: {path}')
        return
    descriptor=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(descriptor,'wb') as f:
        f.write(contents)


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path)
    p.add_argument('--owner-capture',type=Path)
    p.add_argument('--out-dir',type=Path)
    group=p.add_mutually_exclusive_group()
    group.add_argument('--native-exe',type=Path)
    group.add_argument('--native-frame-log',type=Path)
    p.add_argument('--smoke',action='store_true')
    args=p.parse_args(argv)
    if args.smoke:
        assert expected_mask(50)==16 and expected_mask(780)==1
        assert expected_mask(820)==129 and expected_mask(2602)==1
        assert buttons(137)=='A+UP+RIGHT'
        assert schedule({f:(expected_mask(f),0) for f in range(1,3901)}).count(' 1:')>10
        print('PASS JP0836 synthetic input-epoch and native schedule guards')
        return 0
    need(args.rom and args.owner_capture and args.out_dir,
         'require --rom --owner-capture --out-dir')
    image=args.rom.read_bytes()
    need(len(image)==393232 and sha(image)==ROM_SHA256 and
         hashlib.sha1(image).hexdigest()==ROM_SHA1,
         'wrong original Japanese mapper24 cartridge')
    masks,frames,report=parse_archive(args.owner_capture)
    args.out_dir.mkdir(parents=True,exist_ok=True,mode=0o700)
    native_input=schedule(masks)
    write_private(args.out_dir/'native-local.input',native_input.encode('ascii'))
    report['native_input_sha256']=sha(native_input.encode('ascii'))
    write_private(args.out_dir/'jp0836-provenance.json',
                  (json.dumps(report,indent=2)+'\n').encode('ascii'))
    if not(args.native_exe or args.native_frame_log):
        print(json.dumps(report,indent=2))
        return 0
    selected={f for f in frames if f>=FIRST_COMPARISON}
    native_path=args.native_frame_log
    if args.native_exe:
        native_path=args.out_dir/'native.cycframe'
        need(not native_path.exists(),'refuse to overwrite native gameplay trace')
        command=[str(args.native_exe.resolve()),str(args.rom.resolve()),
                 '--headless','--edition','original','--frames',str(END_FRAME+1),
                 '--input',str((args.out_dir/'native-local.input').resolve()),
                 '--frame-log',str(native_path.resolve()),
                 '--frame-log-frames',f'{FIRST_COMPARISON}:{END_FRAME}',
                 '--frame-log-at','mesen']
        finished=subprocess.run(command,text=True,capture_output=True,timeout=3600)
        need(finished.returncode==0,
             'native replay exited '+str(finished.returncode)+': '+finished.stderr[-600:])
    # The JP0834 CYCFRAME parser and JP0833 watched-RAM comparator are reused.
    import jp0834_sync_stage1_capture as bridge
    reference={f:frames[f] for f in sorted(selected)}
    native=bridge.native_frames(native_path,selected)
    compare=bridge.evaluate(reference,native,report['original_input_sha256'])
    # Input hash does NOT prove identical serial $4016 bus read timing.
    same=bool(args.native_exe) and compare['accepted_sampled_actor_lifetime']
    result={**report,'schema':'CVIII-JP0836-JP0835-native-lifetime/v1',
            'native_replay_executed_here':bool(args.native_exe),
            'sampled_ram_and_lifetime_match':same,
            'cpu_bus_input_phase_verified':False,
            'full_gameplay_parity_certified':False,
            'actor_differential':compare}
    write_private(args.out_dir/'jp0836-actor-differential.json',
                  (json.dumps(result,indent=2)+'\n').encode('ascii'))
    print(json.dumps({'original_frames':len(reference),
                      'native_run_here':bool(args.native_exe),
                      'sampled_ram_and_lifetime_match':same,
                      'first_mismatches':compare['first_mismatches'][:6]},indent=2))
    return 0 if same else 1


if __name__=='__main__':
    raise SystemExit(main())