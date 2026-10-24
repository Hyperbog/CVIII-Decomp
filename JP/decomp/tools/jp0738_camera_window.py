#!/usr/bin/env python3
"""JP0738: read-only original MesenCE vs CYCFRAME camera/actor forensic gate.

Only matched saved frame boundaries are compared. Controller intent does not
prove $4016 sampling; best-physical-CIRAM projections do not prove VRC6 mapping.
Only selected numeric RAM fields are reported; no raw RAM dump or pixels.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import struct
import tempfile
import zipfile
from pathlib import Path

JP_SHA = '958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
INPUT_SHA = '27b502aaeca9f5d5381f9f9a812cc188043d083d8ac8b3a89bc40c70f3c30196'
FRAMES = (9376, 9440, 9504, 9576, 9760, 10272, 10328)
# Source-qualified original-JP RAM: 0511/0512/0514 + 0725/0726.
WATCH = {
    'room_selector': (0x34, 0x35, 0x36),
    'camera_xy_room_local': (0x53, 0x54, 0x65, 0x6b),
    'player_position_and_subpixel': (0x041c, 0x0438, 0x0470, 0x04c4, 0x04db),
    'player_motion_terms': (0x04f2, 0x0509, 0x0520, 0x0537),
    'player_actor_descriptor': (0x0400, 0x048c, 0x054e, 0x05ef),
    'game_and_stage_context': (0x18, 0x19, 0x5a, 0x5b, 0x5c, 0x5d, 0x62),
    # GMvania 2012/2022 address notes are research hypotheses, not
    # independently JP-ROM-certified owners or controller bus-read proof.
    'game_controller_ram_hypotheses': (0x28, 0x29, 0x2a, 0x2b),
    'view_scroll_and_room_hypotheses': (0x55, 0x62, 0x63, 0x68, 0x6c, 0x6e, 0x70, 0x73),
    'player_action_collision_hypotheses': (0x8e, 0x565, 0x5c1, 0x5d8),
    'chr_mode_hypotheses': tuple(range(0x38, 0x40)) + (0x6f,),
}
HEADER = struct.Struct('<9I')
ALIAS = frozenset((0x10, 0x14, 0x18, 0x1c))


def original_frames(archive: Path) -> dict[int, tuple[int, bytes, bytes, bytes]]:
    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
        ram = [n for n in names if n.endswith('-ram.tsv')]
        ppu = [n for n in names if n.endswith('-ppu.tsv')]
        if len(ram) != 1 or len(ppu) != 1:
            raise ValueError('expected one Mesen original RAM and PPU TSV each')
        rr = [x.split('\t') for x in z.read(ram[0]).decode().splitlines()
              if x.startswith('R\t')]
        pp = [x.split('\t') for x in z.read(ppu[0]).decode().splitlines()
              if x.startswith('S\t')]
    if not rr or len(rr) != len(pp):
        raise ValueError('Mesen RAM/PPU frame count differs or is empty')
    scenes = {}
    last = -1
    for r, p in zip(rr, pp):
        if len(r) < 6 or len(p) < 14 or r[1:4] != p[1:4]:
            raise ValueError('Mesen snapshot timeline/schema mismatch')
        frame, cycle = int(r[2]), int(r[3])
        if frame <= last or cycle < 0:
            raise ValueError('Mesen frames not strictly increasing')
        last = frame
        if frame not in FRAMES:
            continue
        mem = bytes.fromhex(r[5]); palette = bytes.fromhex(p[7]); nt = bytes.fromhex(p[13])
        if len(mem) != 2048 or len(palette) != 32 or len(nt) != 4096:
            raise ValueError('Mesen RAM/palette/nametable size differs')
        scenes[frame] = cycle, mem, palette, nt
    return scenes


def native_frames(path: Path, wanted: set[int]):
    with path.open('rb') as f:
        if f.read(8) != b'CYCFRAME' or f.read(4) != struct.pack('<I', 2):
            raise ValueError('expected NESRecomp CYCFRAME v2')
        last = -1
        length = path.stat().st_size
        while head := f.read(HEADER.size):
            if len(head) != HEADER.size:
                raise ValueError('truncated native frame header')
            frame, lo, hi, *sizes = HEADER.unpack(head)
            if frame <= last or any(n > 2_000_000 for n in sizes):
                raise ValueError('invalid native frame number or payload length')
            last = frame
            payload = 32 + 256 + sum(sizes)
            if f.tell() + payload > length:
                raise ValueError('truncated native frame payload')
            if frame not in wanted:
                f.seek(payload, 1)
                continue
            pal, oam = f.read(32), f.read(256)
            fields = [f.read(s) for s in sizes]
            if len(pal) != 32 or len(oam) != 256 or any(
                len(b) != n for b, n in zip(fields, sizes)):
                raise ValueError('truncated native frame payload')
            if sizes[0] != 2048 or sizes[1] not in (2048, 4096) or sizes[4] != 122880:
                raise ValueError('native RAM/CIRAM/color class layout mismatch')
            if frame in wanted:
                yield frame, (hi << 32) | lo, fields[0], pal, fields[1]


def components(mem: bytes):
    return {
        'selector': ''.join(f'{mem[i]:02X}' for i in WATCH['room_selector']),
        'camera': mem[0x53] | (mem[0x54] << 8),
        'player_x_low': mem[0x438],
        'player_x_bit9': mem[0x470] & 1,
        'player_y': mem[0x41c],
        'player_x_fraction': mem[0x4c4],
        'player_x_speed': mem[0x4f2],
        'camera_subpixel_hypothesis': mem[0x55],
        'scroll_offset_hypothesis': mem[0x6c],
        'controller_press_ram_hypothesis': mem[0x28],
        'controller_hold_ram_hypothesis': mem[0x2a],
        'player_action_hypothesis': mem[0x565],
        'actor_scroll_delta': mem[0x6b],
    }


def inspect(original: dict, native: dict) -> dict:
    matched = sorted(set(original) & set(native))
    if not matched:
        raise ValueError('no overlapping authenticated Mesen/native focus frames')
    rows = []
    prior = None
    for frame in matched:
        oc, om, op, ont = original[frame]
        nc, nm, np, ciram = native[frame]
        if (len(om) != 2048 or len(nm) != 2048 or len(op) != 32 or
                len(np) != 32 or len(ont) != 4096 or
                len(ciram) not in (2048, 4096)):
            raise ValueError('incomplete frame data')
        orig, new = components(om), components(nm)
        categories = {
            name: [f'{i:04X}' for i in sites if om[i] != nm[i]]
            for name, sites in WATCH.items()
        }
        # Mesen's four logical nametables cannot be equated to the two
        # physical native CIRAM pages without the VRC6 mapping register.
        nt_projected = []
        for k in range(4):
            logical = ont[k*1024:(k+1)*1024]
            nt_projected.append(min(sum(a != b for a, b in zip(
                logical, ciram[o:o+1024])) for o in range(0, len(ciram), 1024)))
        row = {
            'frame': frame,
            'cycles_native_minus_mesen': nc-oc,
            'ram_mismatches': sum(a != b for a, b in zip(om, nm)),
            'first_ram_mismatch_offsets': [f'{i:04X}' for i in range(2048)
                                           if om[i] != nm[i]][:16],
            'watched_mismatch_addresses': categories,
            'original': orig, 'native': new,
            'camera_native_minus_original': new['camera']-orig['camera'],
            'nonalias_palette_mismatches': sum(op[i] != np[i] for i in range(32)
                                                if i not in ALIAS),
            'alias_palette_mismatches': sum(op[i] != np[i] for i in ALIAS),
            'nametable_best_page_differences': nt_projected,
        }
        if prior is not None:
            prev = prior
            for label in ('original', 'native'):
                current_state = row[label]
                before = prev[label]
                row[label+'_camera_advance_from_previous_sample'] = (
                    current_state['camera']-before['camera']
                    if before['selector'] == current_state['selector'] else None)
        rows.append(row)
        prior = row
    first = {}
    for group in WATCH:
        first[group] = next((r['frame'] for r in rows
                             if r['watched_mismatch_addresses'][group]), None)
    return {
        'schema': 'JP0738-window-read-only/v1',
        'window': [9440, 9576], 'matched_frames': matched,
        'causal_disambiguation': 'insufficient: sampled state differences cannot prove controller, collision, or scroll producer instruction ordering',
        'missing_requested_frames': sorted(set(FRAMES)-set(matched)),
        'first_sampled_difference_by_group': first,
        'first_sampled_is_not_first_actual_cpu_write': True,
        'controllers': 'input schedule and internal-RAM hypothesis fields only; no CPU $4016/$4017 bus read-phase log',
        'external_ram_annotations': 'GMvania CVIII RAM/ROM offsets (2012; updated 2022), corroboration required for JP-specific ownership',
        'ppu_chr_mapping': 'physical CHR bank timeline unavailable in these frame records',
        'oam': 'original Mesen OAM not decoded from archived snapshot schema',
        'nametable_metric': 'best of native physical CIRAM pages; not mapper equality',
        'certification': {'vpp': 31, 'strict_prg_bytes': 49504,
                          'strict_prg_total': 262144, 'new_credit': 0},
        'samples': rows,
    }


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def smoke():
    def mem(cam, x):
        b = bytearray(2048)
        b[0x35:0x37] = bytes((1, 2))
        b[0x53] = cam & 255; b[0x54] = cam >> 8; b[0x438] = x
        return bytes(b)
    a = bytes(32); nt = bytes(4096); ciram = bytes(2048)
    old = {9440: (100, mem(10, 80), a, nt),
           9576: (200, mem(93, 120), a, nt)}
    new = {9440: (100, mem(9, 80), a, ciram),
           9576: (201, mem(56, 99), a, ciram)}
    outcome = inspect(old, new)
    assert outcome['first_sampled_difference_by_group']['camera_xy_room_local'] == 9440
    assert outcome['first_sampled_difference_by_group']['player_position_and_subpixel'] == 9576
    assert outcome['samples'][1]['original_camera_advance_from_previous_sample'] == 83
    assert outcome['samples'][1]['native_camera_advance_from_previous_sample'] == 47
    assert outcome['samples'][1]['watched_mismatch_addresses']['player_position_and_subpixel'] == ['0438']
    try: inspect({}, new)
    except ValueError: pass
    else: raise AssertionError('empty overlap accepted')
    with tempfile.TemporaryDirectory() as d:
        bad = Path(d)/'bad.bin';bad.write_bytes(b'CYCFRAME'+struct.pack('<I', 2)+b'\x00')
        try: list(native_frames(bad, {9440}))
        except ValueError: pass
        else: raise AssertionError('truncated CYCFRAME accepted')
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        reference = root/'reference.zip'
        ppu = ['S','FAKE','9576','200','','','','00'*32,
               '','','','','unused.png','00'*4096]
        ram = ['R','FAKE','9576','200','',old[9576][1].hex()]
        with zipfile.ZipFile(reference, 'w') as z:
            z.writestr('invented-ram.tsv', '\t'.join(ram)+'\n')
            z.writestr('invented-ppu.tsv', '\t'.join(ppu)+'\n')
        output = root/'frames.bin'
        with output.open('wb') as f:
            f.write(b'CYCFRAME'+struct.pack('<I', 2))
            sizes = (2048, 2048, 0, 0, 122880, 0)
            f.write(HEADER.pack(9576, 201, 0, *sizes))
            f.write(bytes(32)+bytes(256)+new[9576][1])
            f.write(bytes(2048)+bytes(122880))
        source = original_frames(reference)
        target = {f: (c, r, pal, ciram) for f, c, r, pal, ciram in
                  native_frames(output, {9576})}
        assert inspect(source, target)['samples'][0]['camera_native_minus_original'] == -37
        assert len(file_sha256(reference)) == 64 and len(file_sha256(output)) == 64
        assert inspect(source, target)['first_sampled_difference_by_group']['view_scroll_and_room_hypotheses'] is None
    print('PASS JP0738 invented Mesen zip/CYCFRAME, camera/player and fail-closed regression; NOT gameplay')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--smoke', action='store_true')
    p.add_argument('--rom', type=Path)
    p.add_argument('--mesen-zip', type=Path)
    p.add_argument('--native-frame-log', type=Path)
    p.add_argument('--input-schedule', type=Path)
    args = p.parse_args()
    if args.smoke:
        smoke();return
    if not (args.rom and args.mesen_zip and args.native_frame_log):
        p.error('--rom, --mesen-zip and --native-frame-log are required')
    data = args.rom.read_bytes()
    if len(data) != 393232 or hashlib.sha256(data).hexdigest() != JP_SHA:
        raise ValueError('original Japanese retail ROM fingerprint mismatch')
    scenes = original_frames(args.mesen_zip)
    native = {f: (c, r, pal, ciram) for f, c, r, pal, ciram in
              native_frames(args.native_frame_log, set(scenes))}
    result = inspect(scenes, native)
    result['original_rom_sha256_verified'] = True
    # Identities are reproducible hashes, NOT independent provenance of who
    # executed the captures. Private originals are not redistributed.
    result['capture_file_sha256'] = {
        'mesen_archive': file_sha256(args.mesen_zip),
        'native_frame_log': file_sha256(args.native_frame_log),
    }
    result['capture_provenance_independently_certified'] = False
    if args.input_schedule:
        if hashlib.sha256(args.input_schedule.read_bytes()).hexdigest() != INPUT_SHA:
            raise ValueError('owner archived controller schedule hash mismatch')
        result['original_controller_schedule_sha256_verified'] = True
    else:
        result['original_controller_schedule_sha256_verified'] = False
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
