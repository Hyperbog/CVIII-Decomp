#!/usr/bin/env python3
"""JP0838: inspect owner-private JP0835 vs existing JP0837 frame logs.

Read-only: report CPU cycle deltas, first watched RAM difference, and
source-linked actor timing.  A Mesen source frame is not CPU-bus parity proof.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys
# Placed beside jp0833, jp0834 and jp0836 in JP/recomp/tools.
ENTRY = struct.Struct('<9I')
SOURCE_FRAMES = range(3090, 3901)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def cycles(path: Path, expected: set[int]) -> dict[int, int]:
    found = {}
    with path.open('rb') as f:
        require(f.read(12) == b'CYCFRAME' + struct.pack('<I', 2),
                f'bad CYCFRAME v2: {path}')
        previous_frame = -1
        while head := f.read(ENTRY.size):
            require(len(head) == ENTRY.size, 'partial CYCFRAME header')
            frame, lo, hi, *sizes = ENTRY.unpack(head)
            require(frame > previous_frame and sizes[0] == 2048 and
                    sizes[4] == 122880 and all(0 <= k <= 2_000_000 for k in sizes),
                    f'invalid CYCFRAME frame {frame}')
            previous_frame = frame
            require(len(f.read(288)) == 288, 'truncated palette and OAM')
            if frame in expected:
                found[frame] = lo | hi << 32
            f.seek(sum(sizes), 1)
            require(f.tell() <= path.stat().st_size, 'truncated CYCFRAME payload')
    require(set(found) == expected, 'missing/extra selected CYCFRAME frames')
    return found


def originals(path: Path):
    # Existing strict parser verifies the controller schedule and Stage 1 actor
    # provenance before any reported source/native comparison is accepted.
    import jp0836_stage1_fresh_replay as replay
    _, ram, provenance = replay.parse_archive(path)
    import zipfile
    with zipfile.ZipFile(path) as z:
        matches = [n for n in z.namelist() if n.endswith('_ram.tsv')]
        require(len(matches) == 1, 'ambiguous source RAM member')
        clock = {}
        for line in z.read(matches[0]).decode('ascii').splitlines():
            if not line.startswith('R\t'):
                continue
            kind, frame, tick, _ = line.split('\t', 3)
            f = int(frame)
            require(f not in clock and int(tick) >= 0, 'duplicate clock')
            clock[f] = int(tick)
    return ram, clock, provenance


def linked(ram: bytes) -> tuple[bool, bool]:
    def owner(slot, expected):
        return (ram[0x54e + slot] == 0x3d and
                ram[0x470 + slot] & 4 != 0 and
                ram[0x645 + slot] == expected)
    return owner(1, 3), owner(2, 4)


def lifetime(frames: dict[int, bytes]):
    both = [frame for frame, ram in frames.items() if linked(ram) == (True, True)]
    return {'first_both_frame': min(both) if both else None,
            'both_sampled_frames': len(both),
            'last_both_frame': max(both) if both else None,
            'all_frames_after_first_contiguous': bool(both) and
                both == list(range(both[0], max(frames) + 1))}


def diff(a: bytes, b: bytes, watched: set[int]):
    changed = [i for i in range(2048) if a[i] != b[i]]
    watched_diff = [i for i in changed if i in watched]
    return {'different_bytes': len(changed),
            'watched_different_bytes': len(watched_diff),
            'first_different_address': f'{changed[0]:04X}' if changed else None,
            'first_watched_address': f'{watched_diff[0]:04X}' if watched_diff else None,
            'zp20_mesen': f'{a[0x20]:02X}',
            'zp20_native': f'{b[0x20]:02X}',
            'stack_01e0_01e9_mesen': a[0x1e0:0x1ea].hex(),
            'stack_01e0_01e9_native': b[0x1e0:0x1ea].hex(),
            'actor_pair_mesen': linked(a),
            'actor_pair_native': linked(b)}


def first_problem(reference, native, watched):
    first_any = first_watched = first_actor = None
    mismatched_frames = watched_frames = actor_frames = 0
    for frame in SOURCE_FRAMES:
        a, b = reference[frame], native[frame]
        changed = [i for i in range(2048) if a[i] != b[i]]
        if changed:
            mismatched_frames += 1
            if first_any is None: first_any = frame
        if any(i in watched for i in changed):
            watched_frames += 1
            if first_watched is None: first_watched = frame
        if linked(a) != linked(b):
            actor_frames += 1
            if first_actor is None: first_actor = frame
    return {'first_any_ram_difference': first_any,
            'first_watched_ram_difference': first_watched,
            'first_actor_pair_difference': first_actor,
            'frames_with_any_ram_difference': mismatched_frames,
            'frames_with_watched_difference': watched_frames,
            'frames_with_actor_pair_difference': actor_frames}


def report(archive: Path, folder: Path):
    import jp0833_stage1_lifetime_diff as actor
    import jp0834_sync_stage1_capture as bridge
    reference, source_cycles, prov = originals(archive)
    jp0837 = json.loads((folder / 'jp0837-report.json').read_text(encoding='ascii'))
    require(jp0837.get('status') == 'executed_here' and
            jp0837.get('source_archive_sha256') == prov['archive_sha256'] and
            jp0837.get('input_sha256') == prov['original_input_sha256'],
            'the JP0837 report is not bound to this original capture')
    expected = set(SOURCE_FRAMES)
    require(expected.issubset(reference), 'missing reference frame')
    native = bridge.native_frames(folder / 'native.cycframe', expected)
    interp = bridge.native_frames(folder / 'interp.cycframe', expected)
    nc = cycles(folder / 'native.cycframe', expected)
    ic = cycles(folder / 'interp.cycframe', expected)
    watched = set(actor.addresses())
    keys = list(SOURCE_FRAMES)
    require(keys == sorted(nc) == sorted(ic), 'not a complete aligned frame range')
    focus = list(range(3090, 3097)) + [3100, 3200, 3500, 3900]
    src_sel = {k: reference[k] for k in SOURCE_FRAMES}
    # Never call these results complete parity; intra-frame events are absent.
    rows = {}
    for f in focus:
        if f not in expected: continue
        rows[str(f)] = {'mesen_cycles': source_cycles[f],
                        'native_cycles': nc[f], 'interpreter_cycles': ic[f],
                        'native_minus_mesen_cycles': nc[f] - source_cycles[f],
                        'interp_minus_mesen_cycles': ic[f] - source_cycles[f],
                        **diff(reference[f], native[f], watched)}
    firsts = first_problem(src_sel, native, watched)
    actor_first = firsts['first_actor_pair_difference']
    if actor_first is not None and str(actor_first) not in rows:
        f = actor_first
        rows[str(f)] = {'mesen_cycles': source_cycles[f], 'native_cycles': nc[f],
                        'native_minus_mesen_cycles': nc[f] - source_cycles[f],
                        **diff(reference[f], native[f], watched)}
    return {'schema': 'CVIII-JP0838-private-first-actor-boundary/v1',
            'source_archive_sha256': prov['archive_sha256'],
            'native_frame_log_sha256': hashlib.sha256((folder/'native.cycframe').read_bytes()).hexdigest(),
            'compared_frames': len(keys), 'earliest_captured_frame': min(keys),
            'native_interp_ram_identical_all_selected_frames': native == interp,
            'native_interp_cycle_identical_all_selected_frames': nc == ic,
            'source_actor_lifetime': lifetime(src_sel),
            'native_actor_lifetime': lifetime(native),
            'interpreter_actor_lifetime': lifetime(interp),
            'source_vs_native': firsts,
            'selected_frames': rows,
            'bounds': {'original_Mesen_earlier_than_frame_3090_not_compared': True,
                       'cycle_deltas_are_observation_points_not_cpu_trace_alignment': True,
                       'guest_input_bus_phase_proved': False}}


def smoke():
    a = bytearray(2048)
    b = bytearray(a)
    b[0x20] = 2
    assert diff(a, b, {0x550})['watched_different_bytes'] == 0
    b[0x550] = 0x3d
    assert diff(a, b, {0x550})['first_watched_address'] == '0550'
    for slot, parent in ((1, 3), (2, 4)):
        a[0x54e + slot], a[0x470 + slot], a[0x645 + slot] = 0x3d, 4, parent
    assert linked(bytes(a)) == (True, True)
    assert lifetime({3090: bytes(2048), 3091: bytes(a)})['first_both_frame'] == 3091
    print('PASS JP0838 first watched/actor mismatch and actor-lifetime smoke')


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--owner-capture', type=Path)
    p.add_argument('--jp0837-dir', type=Path)
    p.add_argument('--smoke', action='store_true')
    args = p.parse_args(argv)
    if args.smoke:
        smoke(); return 0
    require(args.owner_capture and args.jp0837_dir, 'require --owner-capture and --jp0837-dir')
    result = report(args.owner_capture, args.jp0837_dir)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    try: raise SystemExit(main())
    except (ValueError, OSError, AssertionError) as e:
        print(f'JP0838 ERROR: {e}', file=sys.stderr)
        raise SystemExit(2)