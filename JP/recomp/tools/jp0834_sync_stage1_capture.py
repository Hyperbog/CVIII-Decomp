#!/usr/bin/env python3
"""Private JP0718 Mesen/NESRecomp Stage1-02 frame bridge (no ROM assets exported).

Consumes an actual original-Mesen JP0718 ZIP and an existing native CYCFRAME
or executes a local native runtime with the authenticated original input.
Only comparable post-frame snapshots are admitted. ROM-free --smoke is synthetic.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jp0833_stage1_lifetime_diff as diff

ENTRY = struct.Struct('<9I')
ORIGINAL_CYCLE_ANCHORS = {9376: 279249268, 9440: 281155220,
                          9504: 283061172, 9576: 285205368}


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def original_frames(archive: Path):
    with zipfile.ZipFile(archive) as z:
        require(z.testzip() is None, 'owner archive failed ZIP CRC')
        matches = [p for p in z.namelist() if p.endswith('-ram.tsv')]
        require(len(matches) == 1, 'exactly one owner -ram.tsv required')
        rows = z.read(matches[0]).decode('ascii').splitlines()
    all_frames = {}
    for line in rows:
        if not line.startswith('R\t'):
            continue
        parts = line.split('\t')
        require(len(parts) >= 6, 'truncated owner RAM record')
        frame, cycles = int(parts[2]), int(parts[3])
        require(frame >= 0 and frame not in all_frames and cycles >= 0,
                'duplicate/bad Mesen timeline')
        raw = bytes.fromhex(parts[5])
        require(len(raw) == 2048, 'wrong original CPU RAM size')
        if frame in ORIGINAL_CYCLE_ANCHORS:
            require(cycles == ORIGINAL_CYCLE_ANCHORS[frame],
                    f'owner original Mesen cycle anchor mismatch at {frame}')
        all_frames[frame] = raw
    require(all_frames, 'no original RAM records')
    # The comparison is intentionally Stage1-02 only; do not align a
    # different room or fabricate a source-to-actor correspondence.
    room = {f: r for f, r in all_frames.items()
            if (r[0x34], r[0x35], r[0x36]) == (0, 1, 0)}
    require(len(room) >= 2, 'fewer than two original Stage1-02 snapshots')
    return dict(sorted(room.items()))


def native_frames(path: Path, selected: set[int]):
    out = {}
    with path.open('rb') as stream:
        require(stream.read(12) == b'CYCFRAME'+struct.pack('<I', 2),
                'expected NESRecomp CYCFRAME v2')
        previous = -1
        while header := stream.read(ENTRY.size):
            require(len(header) == ENTRY.size, 'truncated native frame header')
            frame, low, high, *sizes = ENTRY.unpack(header)
            require(frame > previous and all(0 <= size <= 2000000 for size in sizes),
                    'nonmonotonic native frames or implausible blob sizes')
            previous = frame
            require(sizes[0] == 2048 and sizes[1] in (2048,4096) and
                    sizes[4] == 122880, 'unsupported CYCFRAME RAM/PPU layout')
            metadata = stream.read(288)
            require(len(metadata) == 288, 'truncated palette/OAM block')
            if frame in selected:
                ram = stream.read(2048)
                require(len(ram) == 2048, 'truncated native RAM')
                out[frame] = ram
                stream.seek(sum(sizes)-2048, 1)
            else:
                stream.seek(sum(sizes), 1)
            # Verify each seek did not move past EOF, including skipped frames.
            require(stream.tell() <= path.stat().st_size, 'truncated native frame payload')
    require(set(out) == selected, 'native frame log missing Mesen-selected frames')
    return out


def actor_state(ram, slot):
    kind = ram[0x54e+slot]
    parent = ram[0x645+slot]
    if kind == 0x3d and (ram[0x470+slot]&4) and parent in (3, 4):
        return parent
    return None


def lifetime(frames):
    transitions = []
    previous = None
    for frame, ram in sorted(frames.items()):
        if previous is not None:
            earlier, old = previous
            for slot in range(1, 13):
                was, now = actor_state(old,slot), actor_state(ram,slot)
                if was == now:
                    continue
                event = ('linked' if was is None else
                         'lost_type_zero' if now is None and ram[0x54e+slot] == 0
                         else 'lost_or_reused' if now is None else 'changed_parent')
                transitions.append({'after_frame':earlier,'at_or_before_frame':frame,
                                    'slot':slot,'previous_parent':was,
                                    'next_parent':now,'event':event})
        previous = (frame, ram)
    return transitions


def private_write(path, content):
    descriptor = os.open(path, os.O_WRONLY|os.O_CREAT|os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'w', encoding='ascii') as file:
        file.write(content)


def export_trace(destination, source, samples, schedule_sha):
    records = [{'schema':diff.SCHEMA,'rom_sha256':diff.JP,
                'source':source,'boundary':'post-frame',
                'input_sha256':schedule_sha}]
    records.extend({'frame':f,'ram_hex':ram.hex()}
                   for f, ram in sorted(samples.items()))
    private_write(destination, ''.join(json.dumps(record,separators=(',',':'))+'\n'
                               for record in records))


def evaluate(mesen, native, original_input_sha):
    head = {'schema':diff.SCHEMA,'rom_sha256':diff.JP,
            'boundary':'post-frame','input_sha256':original_input_sha}
    comparison = diff.compare((dict(head,source='mesen'),mesen),
                              (dict(head,source='native'),native))
    original_life, native_life = lifetime(mesen), lifetime(native)
    linked = comparison['mesen_source3_4_sampled_slots']
    # Matching RAM without any actual observed source children must not
    # be elevated into an actor-lifetime comparison result.
    comparison['source3_and_source4_both_observed'] = linked[3]>0 and linked[4]>0
    comparison['original_lifetime_events'] = original_life
    comparison['native_lifetime_events'] = native_life
    comparison['sampled_lifetime_events_match'] = original_life == native_life
    comparison['accepted_sampled_actor_lifetime'] = (
        comparison['matched_actor_ram_samples'] and
        comparison['source3_and_source4_both_observed'] and
        comparison['sampled_lifetime_events_match'])
    comparison['continuous_lifetime_or_contact_proved'] = False
    return comparison


def smoke():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        base = bytearray(2048)
        base[0x35]=1
        for slot, parent in ((1,3),(2,4)):
            base[0x54e+slot],base[0x470+slot],base[0x645+slot] = 0x3d,4,parent
        gone = bytearray(base); gone[0x54f]=0; gone[0x471]=0
        frames = {3092:bytes(base),3093:bytes(gone)}
        assert lifetime(frames)[0]['event'] == 'lost_type_zero'
        log = root/'synthetic.cycframe'
        with log.open('wb') as f:
            f.write(b'CYCFRAME'+struct.pack('<I', 2))
            for frame,ram in frames.items():
                sizes=(2048,2048,0,0,122880,0)
                f.write(ENTRY.pack(frame,0,0,*sizes))
                f.write(bytes(288));f.write(ram)
                f.write(bytes(sum(sizes)-2048))
        assert native_frames(log,set(frames)) == frames
        zip_path = root/'synthetic.zip'
        with zipfile.ZipFile(zip_path,'w') as z:
            z.writestr('x-ram.tsv','\n'.join('R\t0\t%d\t123\t0\t%s' %
                                               (i,m.hex()) for i,m in frames.items()))
        assert original_frames(zip_path) == frames
        result = evaluate(frames,frames,'a'*64)
        assert result['accepted_sampled_actor_lifetime']
        mutated = dict(frames);mutated[3093]=bytes(base)
        mismatch = evaluate(frames,mutated,'a'*64)
        assert not mismatch['accepted_sampled_actor_lifetime']
        assert not mismatch['sampled_lifetime_events_match']
        # Truncation must fail, even if the selected frames themselves fit.
        log.write_bytes(log.read_bytes()[:-1])
        try: native_frames(log,set(frames))
        except ValueError: pass
        else: raise AssertionError('truncated native log accepted')
    print('PASS JP0834 synthetic owner/native parsing, event matching, divergence, truncation')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom',type=Path)
    parser.add_argument('--owner-capture',type=Path)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--native-exe',type=Path)
    group.add_argument('--native-frame-log',type=Path)
    parser.add_argument('--out-dir',type=Path)
    parser.add_argument('--smoke',action='store_true')
    opts = parser.parse_args()
    if opts.smoke:
        smoke()
        return 0
    require(opts.rom and opts.owner_capture and opts.out_dir and
            (opts.native_exe or opts.native_frame_log),
            'require --rom --owner-capture --out-dir and native EXE or CYCFRAME')
    diff.attest(opts.rom)
    # Owner input archive MUST be authenticated before claiming a common
    # timeline, and the native replay uses the original local frame epoch.
    jp = Path(__file__).resolve().parents[2]/'decomp'/'tools'
    sys.path.insert(0,str(jp))
    from jp0743_native_input_epoch import read_source, convert
    raw, member = read_source(opts.owner_capture)
    native_input, metadata = convert(raw)
    mesen = original_frames(opts.owner_capture)
    selected = set(mesen)
    opts.out_dir.mkdir(parents=True,exist_ok=True,mode=0o700)
    schedule_path = opts.out_dir/'native-local.input'
    private_write(schedule_path,native_input)
    if opts.native_exe:
        native_path=opts.out_dir/'native.cycframe'
        require(not native_path.exists(), 'refuse to overwrite private native log')
        cmd=[str(opts.native_exe.resolve()),str(opts.rom.resolve()),
             '--headless','--edition','original','--frames',str(max(selected)+1),
             '--input',str(schedule_path),'--frame-log',str(native_path),
             '--frame-log-frames',f'{min(selected)}:{max(selected)}',
             '--frame-log-at','mesen']
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=3600)
        require(p.returncode == 0, 'native replay failed: '+p.stderr[-1000:])
    else:
        native_path=opts.native_frame_log
    native=native_frames(native_path,selected)
    # An arbitrary external CYCFRAME does not carry authenticated input
    # provenance. Analyze it, but do not certify synchrony from a filename.
    bound_native_run=bool(opts.native_exe)
    digest=metadata['owner_input_sha256']
    export_trace(opts.out_dir/'mesen-postframe.jsonl','mesen',mesen,digest)
    export_trace(opts.out_dir/'native-postframe.jsonl','native',native,digest)
    result=evaluate(mesen,native,digest)
    report={'schema':'CVIII-JP0834-owner-archive-synchronized-lifetime/v1',
            'owner_input_sha256':digest,
            'original_rom_sha256':diff.JP,
            'owner_archive_sha256':hashlib.sha256(opts.owner_capture.read_bytes()).hexdigest(),
            'owner_input_member':member,'native_input_sha256':metadata['native_input_sha256'],
            'native_frame_log_at':'mesen',
            'native_replay_executed_in_this_invocation':bound_native_run,
            'synchronized_capture_certified':bound_native_run and
                result['accepted_sampled_actor_lifetime'],
            'actor_differential':result,
            'note':'Compared sampled owner Mesen post-frame RAM to native CYCFRAME; '
                   'no uninterrupted actor lifetime, writer PC, contact or full CPU/PPU parity proved.'}
    private_write(opts.out_dir/'jp0834-report.json',json.dumps(report,indent=2)+'\n')
    print(json.dumps({'sampled_frames':len(selected),
                      'watched_ram_equal':result['matched_actor_ram_samples'],
                      'actor_lifetime_samples_equal':result['accepted_sampled_actor_lifetime'],
                      'native_input_provenance_verified':bound_native_run,
                      'first_mismatches':result['first_mismatches'][:4]},indent=2))
    return 0 if bound_native_run and result['accepted_sampled_actor_lifetime'] else 1


if __name__ == '__main__':
    raise SystemExit(main())