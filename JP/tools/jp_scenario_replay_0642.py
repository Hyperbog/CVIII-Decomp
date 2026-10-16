#!/usr/bin/env python3
"""JP0642 bounded reference/native fresh-start replay, fail-closed observations.

Runs only when explicitly requested and both private engines are SHA-pinned.
Frames from *different* engines are not comparable pixel/state hashes here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from jp_scenario_preflight_0641 import manifest, preflight, sha_file

REPO_ROOT = Path(__file__).resolve().parents[2]

SCHEMA = 'CVIII-JP-independent-replay/v1'
BUTTONS = ('A', 'B', 'SELECT', 'START', 'UP', 'DOWN', 'LEFT', 'RIGHT')
JSON_LIMIT = 8 << 20


def input_ranges(source: Path, frames: int) -> list[str]:
    """Translate the JP0641 verified single-pad schedule to Mesen intervals."""
    events = []
    for line in source.read_text(encoding='ascii').splitlines():
        if not line or line.startswith('#'):
            continue
        frame, buttons = line.split(' ')
        events.append((int(frame), set() if buttons == '-' else set(buttons.split('+'))))
    ranges = []
    for i, (start, pressed) in enumerate(events):
        end = (events[i + 1][0] if i + 1 < len(events) else frames) - 1
        if pressed:
            ordered = [b.lower() for b in BUTTONS if b in pressed]
            ranges.append('0:' + ','.join(ordered) + '@' + str(start) + '-' + str(end))
    if len(ranges) > 512:
        raise ValueError('reference CLI interval bound exceeded')
    return ranges


def parse_mesen(stdout: str, frames: int) -> dict:
    if len(stdout.encode('utf-8')) > JSON_LIMIT:
        raise ValueError('reference stdout exceeded evidence size bound')
    lines = [l for l in stdout.splitlines() if l.strip()]
    if not lines or len(lines) > 50000:
        raise ValueError('missing or oversized reference events')
    records = []
    for i, line in enumerate(lines, 1):
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError('invalid reference JSONL row ' + str(i)) from exc
        if not isinstance(row, dict) or not isinstance(row.get('event'), str):
            raise ValueError('malformed reference JSONL event')
        records.append(row)
    loaded = [r for r in records if r['event'] == 'loaded']
    summary = [r for r in records if r['event'] == 'summary']
    if len(loaded) != 1 or len(summary) != 1 or records[-1] is not summary[0]:
        raise ValueError('reference missing unique loaded/terminal summary')
    if loaded[0].get('console') != 'Nes':
        raise ValueError('reference loaded non-NES console')
    if any(r['event'] in ('lua_error', 'error', 'reset') for r in records):
        raise ValueError('reference error event')
    if any(r.get('event') == 'lua_log' and r.get('error_count', 0) != 0 for r in records):
        raise ValueError('reference Lua error count nonzero')
    final = summary[0]
    if (final.get('ok') is not True or final.get('reason') != 'frame_limit' or
        type(final.get('frames_executed')) is not int or final['frames_executed'] != frames or
        type(final.get('start_frame')) is not int or
        type(final.get('final_frame')) is not int or
        final['final_frame'] - final['start_frame'] != frames or
        type(final.get('stop_code')) is not int or final['stop_code'] != 0):
        raise ValueError('reference did not complete full independent frame budget')
    return {'frames': frames, 'start_frame': final['start_frame'],
            'final_frame': final['final_frame'], 'event_count': len(records),
            'log_status': 'PASS'}


def png_identity(path: Path) -> dict:
    raw = path.read_bytes()
    if len(raw) < 33 or len(raw) > (32 << 20) or raw[:8] != b'\x89PNG\r\n\x1a\n' or raw[12:16] != b'IHDR':
        raise ValueError('reference screenshot not a bounded PNG')
    size = (int.from_bytes(raw[16:20], 'big'), int.from_bytes(raw[20:24], 'big'))
    if size != (256, 240):
        raise ValueError('reference screenshot size differs from NES 256x240')
    return {'sha256': hashlib.sha256(raw).hexdigest(), 'width': size[0], 'height': size[1]}


def validate_core(reference: Path, core_sha: str) -> dict:
    if not re.fullmatch(r'[0-9a-f]{64}', core_sha):
        raise ValueError('Mesen core requires pinned lowercase SHA-256')
    suffix = {'.exe': 'MesenCore.dll', '.dylib': 'MesenCore.dylib'}
    name = suffix.get(reference.suffix.lower(), 'MesenCore.so')
    core = reference.parent / name
    if core.is_symlink() or not core.is_file():
        raise ValueError('missing or symlinked Mesen runtime core')
    digest = sha_file(core)
    if digest != core_sha:
        raise ValueError('independent Mesen runtime core SHA-256 mismatch')
    return {'core_sha256': digest, 'core_filename': name}


def build_plan(manifest_path: Path) -> dict:
    pf = preflight(manifest_path)
    if pf['status'] != 'PASS':
        raise ValueError('JP0641 scenario preflight: ' + pf.get('error', 'failed'))
    data, _ = manifest(manifest_path)
    intervals = input_ranges(manifest_path.parent / data['input']['file'], data['frames'])
    return {'schema': SCHEMA, 'scenario_id': data['id'], 'frames': data['frames'],
            'manifest_sha256': sha_file(manifest_path),
            'input_sha256': data['input']['sha256'],
            'reference_intervals': intervals,
            'reference_gameplay': 'NOT_EXERCISED', 'native_gameplay': 'NOT_EXERCISED',
            'frame_count_consistency': 'NOT_EXERCISED',
            'cpu_trace_parity': 'NOT_EXERCISED', 'rendering_parity': 'NOT_EXERCISED',
            'first_gameplay_divergence': None, 'strict_new_prg_bytes': 0,
            'new_vpp_points': 0}


def execute(source: Path, rom: Path, reference: Path, native: Path,
            out: Path, core_sha256: str, timeout: int) -> dict:
    if type(timeout) is not int or not 30 <= timeout <= 1800:
        raise ValueError('timeout must be 30..1800 seconds')
    plan = build_plan(source)
    pf = preflight(source, rom=rom, reference=reference, native=native)
    if pf['status'] != 'PASS':
        raise ValueError('preflight rejects execution: ' + pf.get('error', 'failed'))
    if len(set([rom.resolve(), source.resolve(), reference.resolve(), native.resolve(), out.resolve()])) != 5:
        raise ValueError('output cannot overwrite any input/executable')
    validate = validate_core(reference, core_sha256)
    if out.resolve() == REPO_ROOT or REPO_ROOT in out.resolve().parents:
        raise ValueError('private replay artifacts must live outside the repository')
    if out.is_symlink() or out.exists():
        raise ValueError('output directory must be new and must not be a symlink')
    out.mkdir(parents=True)
    report = dict(plan)
    report['schema'] = SCHEMA
    report['rom_sha256'] = pf['rom']['sha256']
    report['reference_executable_sha256'] = pf['reference_executable_sha256']
    report['native_executable_sha256'] = pf['native_executable_sha256']
    report.update(validate)
    commands = {
        'reference': [str(reference), str(rom), '--home', str(out/'mesen-home'),
                      '--frames', str(plan['frames']), '--timeout', str(timeout),
                      '--screenshot', str(out/'reference-final.png'),
                      '--state-json', str(out/'reference-final-state.json')],
        'native': [str(native), str(rom), '--edition', 'original',
                   '--frames', str(plan['frames']),
                   '--input', str((source.parent / manifest(source)[0]['input']['file']).resolve()),
                   '--hash-out', str(out/'native-frames.txt'),
                   '--screenshot', str(out/'native-final.png')]
    }
    for interval in plan['reference_intervals']:
        commands['reference'] += ['--input', interval]
    for role in ('reference', 'native'):
        report[role + '_gameplay'] = 'FAIL'
        log = out / (role + '.stdout')
        err = out / (role + '.stderr')
        try:
            completed = subprocess.run(commands[role], capture_output=True, timeout=timeout,
                                       check=False)
            log.write_bytes(completed.stdout)
            err.write_bytes(completed.stderr)
            report[role + '_stdout_sha256'] = sha_file(log) if log.stat().st_size else None
            report[role + '_stderr_sha256'] = sha_file(err) if err.stat().st_size else None
            if completed.returncode != 0:
                raise ValueError(role + ' returned nonzero exit ' + str(completed.returncode))
            if role == 'reference':
                report['reference_observation'] = parse_mesen(completed.stdout.decode('utf-8'), plan['frames'])
                report['reference_screenshot'] = png_identity(out/'reference-final.png')
                state = out/'reference-final-state.json'
                if state.is_symlink() or not state.is_file() or not 0 < state.stat().st_size <= JSON_LIMIT:
                    raise ValueError('missing/oversized original reference state snapshot')
                json.loads(state.read_text(encoding='utf-8'))
                report['reference_state_sha256'] = sha_file(state)
            else:
                from validate_frame_artifacts_0578 import verify
                report['native_observation'] = verify(out/'native-frames.txt', out/'native-final.png', plan['frames'])
            report[role + '_gameplay'] = 'PASS'
        except (OSError, ValueError, UnicodeError, json.JSONDecodeError, subprocess.TimeoutExpired) as exc:
            report[role + '_error'] = str(exc)
        report[role + '_command_argv'] = commands[role]  # owner-local report only
    if report['reference_gameplay'] == 'PASS' and report['native_gameplay'] == 'PASS':
        report['frame_count_consistency'] = 'PASS'
    report['first_execution_failure'] = next(
        (r for r in ('reference', 'native') if report[r + '_gameplay'] != 'PASS'), None)
    report['status'] = ('PASS' if all(report[r + '_gameplay'] == 'PASS'
                                     for r in ('reference', 'native')) else 'FAIL')
    (out/'replay-report.json').write_text(json.dumps(report, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    return report


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest', type=Path, required=True)
    p.add_argument('--rom', type=Path)
    p.add_argument('--reference-exe', type=Path)
    p.add_argument('--native-exe', type=Path)
    p.add_argument('--reference-core-sha256')
    p.add_argument('--out', type=Path)
    p.add_argument('--timeout', type=int, default=180)
    p.add_argument('--run', action='store_true')
    a = p.parse_args()
    try:
        if a.run:
            if not all((a.rom, a.reference_exe, a.native_exe, a.reference_core_sha256, a.out)):
                raise ValueError('--run requires --rom, both pinned binaries, --reference-core-sha256 and --out')
            record = execute(a.manifest, a.rom.resolve(strict=True),
                             a.reference_exe.resolve(strict=True), a.native_exe.resolve(strict=True),
                             a.out.resolve(), a.reference_core_sha256, a.timeout)
        else:
            record = build_plan(a.manifest)
            record['status'] = 'PASS'  # plan contract only
        print(json.dumps(record, indent=2, sort_keys=True))
        return 0 if record['status'] == 'PASS' else 2
    except (OSError, ValueError, json.JSONDecodeError, UnicodeError) as exc:
        print('JP0642 FAIL: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
