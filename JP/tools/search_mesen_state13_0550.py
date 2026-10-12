#!/usr/bin/env python3
"""Branch replay from a *real* original-JP Mesen Stage-1 savestate.

The only valid source of live gameplay evidence is an authenticated Mesen2
emulator executing the unmodified user-supplied original ROM. This runner is
read-only with respect to game CPU memory/ROM, and NEVER fabricates a state-13
observation or assumes that a conditional state-13 path is live.

Two modes:
  --plan: offline audit of the 520+220+360 input-route plan and fork choices.
  --run: authenticate ROM/emulator; perform 0549 cold-boot capture; replay
         independent savestate forks; validate each Mesen JSONL transcript.

Original ROM, raw logs, screenshot, savestates and Mesen binary remain private.
Only the bounded *derived* report is safe to commit, after inspection.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Sequence

from audit_mesen_state13_0549 import authenticate, audit, scan, digest, AuditError

FRAME_COUNTS = (520, 220, 360)
BASE_NAMES = ('play520', 'stage220', 'stage360')
FORK_FRAMES = 1200
# Deterministic exploratory routes. These reflect 0508's already documented
# Stage-1 branch *input schedules*, but this observer is new and unexecuted
# until the authenticated original emulator is actually run.
FORKS = {
    'idle_1200': (),
    'right_1200': ('0:right@1-1200',),
    'right_jump_1200': ('0:right@1-1200',) + tuple(f'0:a@{i}-{i+10}' for i in range(45, 946, 100)),
    'right_whip_1200': ('0:right@1-1200',) + tuple(f'0:b@{i}-{i+9}' for i in range(25, 906, 80)),
    'holdjump_1200': ('0:right@1-1200', '0:a@1-1200', '0:b@200-215', '0:b@400-415'),
}


def plan() -> dict:
    assert sum(FRAME_COUNTS) == 1100
    for name, buttons in FORKS.items():
        assert name.endswith('_1200') and all(x.startswith('0:') for x in buttons)
    return {
        'schema': 'JP-0550-natural-mesen-branch-plan/v1',
        'dependency': '0549 authenticated 520+220+360 cold-boot capture',
        'parent_savestate': 'stage360.mss',
        'cold_boot_frames': sum(FRAME_COUNTS),
        'fork_frames_each': FORK_FRAMES,
        'independent_forks': [{'name': k, 'frames': FORK_FRAMES, 'controller_inputs': list(v)}
                              for k, v in FORKS.items()],
        'total_emulated_frames_if_executed': 1100 + FORK_FRAMES * len(FORKS),
        'provenance': 'PLAN_ONLY_NO_NEW_GAMEPLAY_EVIDENCE',
        'strict_prg_credit': 0,
    }


def validate_fork(name: str, log: Path, *, parent_final_frame: int,
                  parent_savestate_sha256: str, input_args: Sequence[str]) -> dict:
    if name not in FORKS:
        raise AuditError('Unknown or unsanctioned input route')
    if tuple(input_args) != FORKS[name]:
        raise AuditError('Input route differs from pinned search schedule')
    if not isinstance(parent_final_frame, int) or parent_final_frame < 1:
        raise AuditError('Invalid parent savestate frame')
    if len(parent_savestate_sha256) != 64 or any(x not in '0123456789abcdef' for x in parent_savestate_sha256):
        raise AuditError('Missing authenticated parent savestate fingerprint')
    result = scan(log)
    if result['start_frame'] != parent_final_frame:
        raise AuditError('Fork does not begin at verified parent savestate frame')
    if result['frames'] != FORK_FRAMES:
        raise AuditError('Fork did not execute required 1200 frames')
    return {
        'name': name,
        'parent_savestate_sha256': parent_savestate_sha256,
        'controller_inputs': list(input_args),
        'transcript_sha256': digest(log),
        **result,
    }


def assemble_report(bootstrap: dict, parent_state: Path,
                    forks: Sequence[tuple[str, Path]],
                    *, original_hashes_verified: bool) -> dict:
    if bootstrap.get('total_frames') != sum(FRAME_COUNTS):
        raise AuditError('Original Stage 1 bootstrap must execute exactly 1100 frames')
    segments = bootstrap.get('segments', [])
    if [v.get('name') for v in segments] != list(BASE_NAMES):
        raise AuditError('Bootstrap stage names/order do not match reference route')
    if [v.get('frames') for v in segments] != list(FRAME_COUNTS):
        raise AuditError('Bootstrap stages have incorrect frame counts')
    if len(set(n for n, _ in forks)) != len(forks):
        raise AuditError('Duplicate input-route fork')
    parent_frame = segments[-1].get('final_frame')
    if not parent_state.is_file() or parent_state.stat().st_size == 0:
        raise AuditError('Missing/empty real emulator parent savestate')
    sha = digest(parent_state)
    branches = [validate_fork(name, path, parent_final_frame=parent_frame,
                              parent_savestate_sha256=sha, input_args=FORKS[name])
                for name, path in forks]
    all_cases = list(segments) + branches
    hits = [
        {'segment': x.get('name'), **hit}
        for x in all_cases for hit in x.get('e526_state13_samples', [])
    ]
    return {
        'schema': 'JP-0550-natural-mesen-state13-fork-search/v1',
        'original_rom_sha256_authenticated': bool(original_hashes_verified),
        'cold_boot_frames': sum(FRAME_COUNTS),
        'independent_fork_frames_each': FORK_FRAMES,
        'number_of_forks': len(branches),
        # A fork is a replayed alternative, *not* the next sequential
        # segment; summing frames must never be called a continuous route.
        'total_emulator_frames_executed': sum(FRAME_COUNTS) + FORK_FRAMES * len(branches),
        'longest_contiguous_input_route_frames': sum(FRAME_COUNTS) + (FORK_FRAMES if branches else 0),
        'parent_savestate_sha256': sha,
        'bootstrap': bootstrap,
        'forks': branches,
        'state13_e526_observed': bool(hits) if original_hashes_verified else False,
        'unauthenticated_test_hits_not_gameplay_evidence': len(hits) if not original_hashes_verified else 0,
        'verified_e526_state13_hits': hits[:60],
        'conditional_state13_native_parity_not_automatic': True,
        'native_full_frame_parity': 'NOT ESTABLISHED',
        'new_strict_prg_bytes': 0,
        'observation': ('UNAUTHENTICATED_FIXTURE_NO_GAMEPLAY_CLAIM' if not original_hashes_verified else
                        ('STATE13_OBSERVED_IN_SUPPLIED_EMULATOR_RUNS' if hits else
                         'STATE13_NOT_OBSERVED_IN_THESE_BOUNDED_INPUT_ROUTES')),
    }


def run_child(command: list[str], stdout: Path) -> None:
    stdout.parent.mkdir(parents=True, exist_ok=True)
    with stdout.open('w', encoding='utf-8') as dest:
        subprocess.run(command, stdout=dest, check=True, timeout=240)


def run(rom: Path, emulator: Path, output: Path, *, forks: list[str]) -> dict:
    authenticate(rom, emulator)
    base = Path(__file__).resolve().parents[2]
    runner = base/'JP/tools/run_mesen_state13_0549.sh'
    lua = base/'JP/tools/mesen_0549_state13_provenance.lua'
    if not runner.is_file() or not lua.is_file():
        raise AuditError('Missing 0549 original-game observer/boot runner')
    output.mkdir(parents=True, exist_ok=True)
    subprocess.run(['bash', str(runner), str(rom), str(emulator), str(output)],
                   check=True, timeout=900)
    bootstrap = audit(rom, emulator, [(n, output/f'{n}.jsonl') for n in BASE_NAMES])
    if bootstrap['total_frames'] != 1100:
        raise AuditError('Bootstrap frame count mismatch')
    parent = output/'stage360.mss'
    if not parent.is_file() or not parent.stat().st_size:
        raise AuditError('Stage1 fork savestate absent')
    recorded=[]
    for name in forks:
        if name not in FORKS or name in [n for n,_ in recorded]:
            raise AuditError(f'Invalid/repeated fork: {name}')
        command = [str(emulator/'mesen-agent'),str(rom),
                   '--home',str(output/f'home-{name}'),
                   '--load-state',str(parent), '--frames',str(FORK_FRAMES),
                   '--timeout','180','--lua',str(lua),
                   '--save-state',str(output/f'{name}.mss')]
        for button in FORKS[name]:command.extend(['--input',button])
        path=output/f'{name}.jsonl'
        run_child(command, path)
        recorded.append((name,path))
        # Authenticate each completed fork *before* running the next branch.
        validate_fork(name,path,parent_final_frame=bootstrap['segments'][-1]['final_frame'],
                      parent_savestate_sha256=digest(parent),input_args=FORKS[name])
    result=assemble_report(bootstrap,parent,recorded,original_hashes_verified=True)
    (output/'derived_state13_search.json').write_text(json.dumps(result, indent=2)+'\n',encoding='utf-8')
    return result


def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--plan',action='store_true',help='ROM-free inputs + provenance plan')
    ap.add_argument('--rom',type=Path)
    ap.add_argument('--emulator',type=Path)
    ap.add_argument('--out',type=Path)
    ap.add_argument('--fork',action='append',choices=sorted(FORKS))
    args=ap.parse_args()
    if args.plan:
        print(json.dumps(plan(),indent=2));return
    if not args.rom or not args.emulator or not args.out:
        ap.error('run mode requires --rom, --emulator and --out')
    selected=args.fork or list(FORKS)
    report=run(args.rom,args.emulator,args.out,forks=selected)
    print(f"PASS authenticated natural Mesen replay: {report['total_emulator_frames_executed']} "
          f"frames across independent forks; state13 E526 observed={report['state13_e526_observed']}")

if __name__=='__main__':main()
