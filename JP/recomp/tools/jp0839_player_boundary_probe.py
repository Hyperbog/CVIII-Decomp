#!/usr/bin/env python3
"""JP0839: owner-private, read-only player-slot boundary differential.

Analyze original JP0835 Mesen endFrame RAM versus pinned-engine JP0837
post-instruction-boundary CYCFRAME. Does not modify emulator/ROM or claim
instruction-synchronous comparison.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

import jp0838_actor_boundary_triage as gate
import jp0834_sync_stage1_capture as bridge

FRAMES = range(3090, 3901)
LABELS = {
    0x041c: 'actor_slot0_integer_y',
    0x04db: 'actor_slot0_fractional_y',
    0x0006: 'zero_page_06_role_unverified',
    0x057c: 'ram_057c_role_unverified',
    0x05d8: 'ram_05d8_role_unverified',
    0x0020: 'volatile_zero_page_20_role_unverified',
    0x01fc: 'stack_01fc',
    0x01e1: 'stack_01e1',
    0x01e2: 'stack_01e2',
    0x01e3: 'stack_01e3',
}


def hex8(value: int) -> str:
    return f'{value:02X}'


def runs(frames: list[int]) -> list[dict]:
    result: list[dict] = []
    for f in frames:
        if result and f == result[-1]['last'] + 1:
            result[-1]['last'] = f
            result[-1]['length'] += 1
        else:
            result.append({'first': f, 'last': f, 'length': 1})
    return result


def summarize_address(reference: dict, native: dict, address: int) -> dict:
    keys = sorted(reference)
    gate.require(keys == sorted(native) and keys == list(FRAMES),
                 'source and native frames must cover 3090..3900')
    differing = [f for f in keys if reference[f][address] != native[f][address]]
    transitions = sum(reference[f][address] != reference[f - 1][address]
                      for f in keys[1:])
    neighbor_earlier = sum(reference[f - 1][address] == native[f][address]
                           for f in differing if f - 1 in reference)
    neighbor_later = sum(reference[f + 1][address] == native[f][address]
                         for f in differing if f + 1 in reference)
    examples = []
    for f in differing[:6]:
        examples.append({
            'frame': f, 'mesen': hex8(reference[f][address]),
            'native': hex8(native[f][address]),
            'mesen_previous': hex8(reference[f - 1][address]) if f - 1 in reference else None,
            'mesen_next': hex8(reference[f + 1][address]) if f + 1 in reference else None,
            'native_previous': hex8(native[f - 1][address]) if f - 1 in native else None,
            'native_next': hex8(native[f + 1][address]) if f + 1 in native else None,
        })
    episodes = runs(differing)
    return {
        'label': LABELS[address], 'address': f'{address:04X}',
        'differing_frames': len(differing),
        'first_difference': differing[0] if differing else None,
        'last_difference': differing[-1] if differing else None,
        'distinct_mesen_values': len({reference[f][address] for f in keys}),
        'mesen_value_changes_between_frames': transitions,
        'mesen_value_constant': transitions == 0,
        'native_matches_mesen_previous_frame_on_mismatch': neighbor_earlier,
        'native_matches_mesen_next_frame_on_mismatch': neighbor_later,
        'episodes': len(episodes),
        'longest_episode': max((e['length'] for e in episodes), default=0),
        'first_episodes': episodes[:8],
        'first_examples': examples,
    }


def report(owner: Path, folder: Path) -> dict:
    # JP0838 authenticates original owner capture and JP0837 report identity,
    # checks all selected native/interpreter RAM frames, and records clocks.
    checked = gate.report(owner, folder)
    gate.require(checked['native_interp_ram_identical_all_selected_frames'] and
                 checked['native_interp_cycle_identical_all_selected_frames'],
                 'native/interpreter disagreement: do not classify Mesen alignment')
    originals, clocks, provenance = gate.originals(owner)
    frames = set(FRAMES)
    native = bridge.native_frames(folder / 'native.cycframe', frames)
    nc = gate.cycles(folder / 'native.cycframe', frames)
    ref = {f: originals[f] for f in FRAMES}
    deltas = [nc[f] - clocks[f] for f in FRAMES]
    content = {f'{a:04X}': summarize_address(ref, native, a) for a in LABELS}
    changed_player = [f for f in FRAMES if any(ref[f][a] != native[f][a]
                                              for a in (0x041c, 0x04db))]
    return {
        'schema': 'CVIII-JP0839-private-player-boundary/v1',
        'source_archive_sha256': provenance['archive_sha256'],
        'native_frame_log_sha256': checked['native_frame_log_sha256'],
        'frames_examined': len(FRAMES),
        'native_interpreter_postframe_identical': True,
        'cycle_offsets': {f'{k:+d}': v for k, v in sorted(Counter(deltas).items())},
        'player_y_integer_or_fraction_mismatch_frames': len(changed_player),
        'first_player_y_mismatch': changed_player[0] if changed_player else None,
        'player_y_mismatch_episodes': runs(changed_player)[:15],
        'addresses': content,
        'limits': {
            'first_discrepancy_before_frame_3090_unobservable': True,
            'neighbor_equalities_prove_frame_alignment': False,
            'all_source_ram_checked_at_same_instruction_boundary': False,
            'mapper_or_cpu_timing_bug_proved': False,
        },
    }


def smoke() -> None:
    a = bytearray(2048)
    b = bytearray(a)
    ref = {f: bytes(a) for f in FRAMES}
    nat = dict(ref)
    b[0x041c] = 0x90
    nat[3092] = nat[3093] = bytes(b)
    s = summarize_address(ref, nat, 0x041c)
    assert s['first_difference'] == 3092 and s['differing_frames'] == 2
    assert s['longest_episode'] == 2 and s['episodes'] == 1
    assert s['mesen_value_constant']
    assert runs([3091, 3093, 3094]) == [
        {'first': 3091, 'last': 3091, 'length': 1},
        {'first': 3093, 'last': 3094, 'length': 2},
    ]
    print('PASS JP0839 private player-boundary classification smoke')


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--owner-capture', type=Path)
    p.add_argument('--jp0837-dir', type=Path)
    p.add_argument('--smoke', action='store_true')
    args = p.parse_args(argv)
    if args.smoke:
        smoke()
        return 0
    gate.require(args.owner_capture is not None and args.jp0837_dir is not None,
                 'require --owner-capture and --jp0837-dir')
    print(json.dumps(report(args.owner_capture, args.jp0837_dir), indent=2))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, OSError, AssertionError) as error:
        print(f'JP0839 ERROR: {error}', file=sys.stderr)
        raise SystemExit(2)