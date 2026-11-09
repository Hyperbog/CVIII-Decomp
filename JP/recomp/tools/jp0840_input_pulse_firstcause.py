#!/usr/bin/env python3
"""JP0840: compare original-JP controller intent with game-accepted A presses.

Owner-private, read-only. Mesen inputPolled intent is not a CPU bus trace.
Requires genuine JP0835 source, plus existing JP0837 CYCFRAME for native mode.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import jp0836_stage1_fresh_replay as replay
import jp0838_actor_boundary_triage as gate
import jp0834_sync_stage1_capture as frame_bridge

PRESSED_A = 0x80
ADDRS = ((0x28, 'button_press_28'), (0x2a, 'button_hold_2a'),
         (0x041c, 'player_y_integer'), (0x04db, 'player_y_fraction'),
         (0x0520, 'player_y_speed'), (0x0537, 'player_y_frac_speed'),
         (0x0565, 'player_action'), (0x05c1, 'player_fall_switch'))
FOCUS = range(3507, 3518)


def rises(mask_by_frame: dict[int, int]) -> list[int]:
    return [f for f in sorted(mask_by_frame) if f-1 in mask_by_frame and
            mask_by_frame[f] & PRESSED_A and not mask_by_frame[f-1] & PRESSED_A]


def pulse_onset(frames: dict[int, bytes], first: int, address=0x2a,
                lookahead: int=10) -> int | None:
    """First guest A hold within the pulse window, without assuming frame parity."""
    for f in range(first, first+lookahead):
        if f in frames and frames[f][address] & PRESSED_A:
            return f
    return None


def first_y_change(frames: dict[int, bytes], base: int, stop: int) -> int | None:
    if base-1 not in frames:
        return None
    before = frames[base-1][0x41c]
    for f in range(base, stop+1):
        if f in frames and frames[f][0x41c] != before:
            return f
    return None


def sample(ram: bytes) -> dict:
    return {label: f'{ram[address]:02X}' for address, label in ADDRS}


def report(owner: Path, jp0837_dir: Path | None) -> dict:
    masks, source, provenance = replay.parse_archive(owner)
    intent = {f: pair[0] for f, pair in masks.items()}
    starts = [f for f in rises(intent) if f >= min(source)+1]
    # JP0835 source frames 2695..3900, and all input pulses are 6 frames long.
    pulses = []
    for start in starts:
        accepted = pulse_onset(source, start)
        pulses.append({'input_intent_start': start,
                       'mesen_game_a_first_held': accepted,
                       'mesen_accept_delay_frames': (accepted-start if accepted is not None else None)})
    anomalies = [p for p in pulses if p['mesen_accept_delay_frames'] != 0]
    result = {
        'schema': 'CVIII-JP0840-original-A-onset/v1',
        'source_archive_sha256': provenance['archive_sha256'],
        'source_a_pulses_examined': len(pulses),
        'source_pulses_without_same_frame_guest_a': anomalies,
        'focus_intent_start': 3509,
        'focus_source_guest_a_held_first': pulse_onset(source, 3509),
        'focus_source_player_integer_y_first_moves': first_y_change(source, 3509, 3518),
        'input_bus_phase_certified': False,
        'native_mode': 'not_supplied',
    }
    if jp0837_dir is None:
        return result
    # Verifies owner archive identity and the actual native/interpreter trace
    # windows and reports their equivalence. Never trusts an unmatched log.
    previous = gate.report(owner, jp0837_dir)
    gate.require(previous['native_interp_ram_identical_all_selected_frames'] and
                 previous['native_interp_cycle_identical_all_selected_frames'],
                 'native/interpreter mismatch: do not attribute A transitions')
    selected = set(range(3090, 3901))
    native = frame_bridge.native_frames(jp0837_dir/'native.cycframe', selected)
    interpreter = frame_bridge.native_frames(jp0837_dir/'interp.cycframe', selected)
    gate.require(native == interpreter, 'native/interpreter RAM not identical')
    for pulse in pulses:
        if pulse['input_intent_start'] >= 3090:
            begin = pulse['input_intent_start']
            found = pulse_onset(native, begin)
            pulse['native_game_a_first_held'] = found
            pulse['native_accept_delay_frames'] = found-begin if found is not None else None
    result.update({
        'native_mode': 'authenticated_existing_JP0837',
        'focus_native_guest_a_held_first': pulse_onset(native, 3509),
        'focus_native_player_integer_y_first_moves': first_y_change(native, 3509, 3518),
        'focus_native_interp_ram_identical_811_frames': True,
        'pulse_table_3090_to_3900': [p for p in pulses if p['input_intent_start'] >= 3090],
        'focus_rows': [
            {'frame': f, 'intent_mask': f'{intent[f]:02X}',
             'mesen': sample(source[f]), 'native': sample(native[f])}
            for f in FOCUS
        ],
    })
    return result


def smoke():
    masks = {f: 0 for f in range(10, 19)}
    masks[12]=masks[13]=masks[14]=128
    assert rises(masks)==[12]
    a = bytes(2048)
    b = bytearray(a); b[0x2a]=128; b[0x41c]=0xB0
    x = {11:a,12:a,13:a,14:bytes(b)}
    assert pulse_onset(x,12)==14
    assert first_y_change(x,12,14)==14
    assert pulse_onset(x,12,0x28) is None
    print('PASS JP0840 original controller-intent/game-acceptance smoke')


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--owner-capture', type=Path)
    p.add_argument('--jp0837-dir', type=Path)
    p.add_argument('--smoke', action='store_true')
    args=p.parse_args(argv)
    if args.smoke:
        smoke(); return 0
    gate.require(args.owner_capture is not None, 'require --owner-capture')
    result=report(args.owner_capture,args.jp0837_dir)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    try: raise SystemExit(main())
    except (ValueError, OSError, AssertionError, KeyError) as e:
        print(f'JP0840 ERROR: {e}', file=sys.stderr)
        raise SystemExit(2)