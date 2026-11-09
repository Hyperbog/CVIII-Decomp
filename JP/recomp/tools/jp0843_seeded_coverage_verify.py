#!/usr/bin/env python3
"""JP0843: one-run verification of an existing JP0842 seeded retail build.

Uses the already recorded JP0837 private native input/hash/miss evidence.
Does not execute MesenCE, create new input routes, or certify whole-game parity.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

FRAMES = 3901
SUMMARY = re.compile(r'mode=native\s+frames=(\d+)\s+cycles=(\d+)\s+native_cycles=(\d+)')
FALLBACK = re.compile(r'interpreted:\s+ROM\s+(\d+)\s+\([^\n]*?RAM\s+(\d+)')


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def counters(output):
    """Pinned engine may omit the interpreter line when execution is all native."""
    m = SUMMARY.search(output)
    need(m is not None, 'missing pinned NESRecomp native summary')
    frames, total, native = map(int, m.groups())
    need(frames == FRAMES and total > 0 and 0 <= native <= total,
         'incorrect frame epoch or impossible native cycle accounting')
    fallback = FALLBACK.search(output)
    if fallback:
        rom, ram = map(int, fallback.groups())
    else:
        need(native == total, 'missing interpreter counters despite fallback cycles')
        rom = ram = 0
    return dict(frames=frames, total_cpu_cycles=total, native_cpu_cycles=native,
                native_cycle_fraction=native / total,
                interpreted_rom_cycles=rom, interpreted_ram_cycles=ram)


def compare_hashes(reference, new):
    need(reference.keys() == new.keys(), 'hash frame ranges differ')
    for frame in reference:
        if reference[frame] != new[frame]:
            fields = {k: dict(baseline=reference[frame].get(k), seeded=new[frame].get(k))
                      for k in reference[frame] if reference[frame][k] != new[frame].get(k)}
            return dict(frame=frame, fields=fields)
    return None


def verify_engine(folder, pin):
    command = ['git', '-C', str(folder), 'rev-parse', 'HEAD']
    p = subprocess.run(command, capture_output=True, text=True, timeout=20)
    need(p.returncode == 0 and p.stdout.strip() == pin,
         'actual external NESRecomp checkout is not the pinned revision')
    return p.stdout.strip()


def verify_setup(rom, baseline, build, out):
    import jp0842_seed_profile as seeds
    import jp0836_stage1_fresh_replay as replay
    manifest = json.loads((build / 'jp0842-bank-qualified-manifest.json').read_text())
    report = json.loads((build / 'jp0575_build_report.json').read_text())
    old, baseline_meta = seeds.verify_evidence(baseline, rom)
    need(len(old) == manifest.get('seed_count') and
         manifest.get('seed_sha256') == report.get('coverage_seeds', {}).get('seed_sha256') and
         manifest.get('miss_log_sha256') == baseline_meta['miss_log_sha256'] and
         manifest.get('native_hashes_sha256') == baseline_meta['native_hashes_sha256'] and
         manifest.get('source_archive_sha256') == baseline_meta['source_archive_sha256'],
         'seed/build metadata not tied to the authenticated JP0837 execution')
    seed_file = build / 'jp0842-bank-qualified-seeds.txt'
    need(seed_file.is_file() and sha(seed_file) == manifest['seed_sha256'],
         'built seed profile modified or unavailable')
    need(seeds.validate(rom, seed_file)['seed_count'] == len(old),
         'built physical-bank seed validation failed')
    need(report.get('build_completed') is True and
         report.get('ppu_implementation') == 'LLE' and
         report.get('rom', {}).get('sha256') == replay.ROM_SHA256,
         'build is not the authenticated original-JP LLE runtime')
    exe = Path(report['runner']).resolve(strict=True)
    need(sha(exe) == report['runner_sha256'], 'seeded executable hash changed')
    revision = verify_engine(build / '_external' / 'nesrecomp', seeds.PIN)
    input_file = baseline / 'native-local.input'
    expected = replay.schedule({f: (replay.expected_mask(f), 0)
                                for f in range(1, replay.END_FRAME + 1)})
    need(input_file.read_text(encoding='ascii') == expected,
         'existing replay input is not the exact JP0835 controller schedule')
    root = seeds.ROOT.resolve()
    target = out.resolve()
    need(target != root and root not in target.parents and
         target != baseline.resolve() and target != build.resolve() and
         target not in baseline.resolve().parents and
         target not in build.resolve().parents and
         baseline.resolve() not in target.parents and
         build.resolve() not in target.parents,
         'results must be in a separate private output directory')
    need(not target.exists() or not any(target.iterdir()),
         'output directory must be empty; previous evidence must not be overwritten')
    return exe, input_file, revision, report, baseline_meta, old


def verify(rom, baseline, build, out):
    import jp0837_bank_coverage_firstdiff as coverage
    rom, baseline, build, out = (p.resolve() for p in (rom, baseline, build, out))
    exe, input_file, revision, report, meta, old = verify_setup(rom, baseline, build, out)
    out.mkdir(parents=True, exist_ok=True)
    hash_file, miss_file = out / 'seeded.hashes', out / 'seeded.misses'
    cmd = [str(exe), str(rom), '--headless', '--edition', 'original',
           '--frames', str(FRAMES), '--input', str(input_file),
           '--hash-out', str(hash_file), '--miss-log', str(miss_file)]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    (out / 'seeded.stdout').write_text(proc.stdout, encoding='utf-8')
    (out / 'seeded.stderr').write_text(proc.stderr, encoding='utf-8')
    need(proc.returncode == 0, f'seeded NESRecomp exited {proc.returncode}; see seeded.stderr')
    old_hashes = coverage.hashes(baseline / 'native.hashes')
    new_hashes = coverage.hashes(hash_file)
    diff = compare_hashes(old_hashes, new_hashes)
    old_hits = sum(x['interpreter_entry_count'] for x in old)
    remaining = coverage.bank_misses(miss_file, coverage.rom_prg(rom))
    hits = sum(x['interpreter_entry_count'] for x in remaining)
    stats = counters(proc.stdout + '\n' + proc.stderr)
    result = {
        'schema': 'CVIII-JP0843-seeded-native-route-coverage/v1',
        'status': 'pass' if diff is None and hits < old_hits else
                  'hash_mismatch' if diff is not None else 'no_interpreter_hit_reduction',
        'original_japanese_rom_sha256': report['rom']['sha256'],
        'engine_checkout_sha': revision, 'seeded_executable_sha256': sha(exe),
        'seed_sha256': report['coverage_seeds']['seed_sha256'],
        'baseline_native_hashes_sha256': meta['native_hashes_sha256'],
        'seeded_native_hashes_sha256': sha(hash_file),
        'frames_compared': len(old_hashes), 'first_native_hash_difference': diff,
        'baseline_interpreter_instruction_start_sites': len(old),
        'remaining_interpreter_instruction_start_sites': len(remaining),
        'baseline_interpreter_entry_hits': old_hits,
        'remaining_interpreter_entry_hits': hits,
        'interpreter_hits_eliminated': old_hits - hits,
        'interpreter_hits_reduction_percent': round((old_hits-hits)*100/old_hits, 4),
        'remaining_4k_banks': sorted({x['bank4k'] for x in remaining}),
        'runtime': stats,
        'original_mesen_parity_claimed': False,
        'full_game_compiled_coverage_claimed': False,
    }
    (out / 'jp0843-report.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    return result


def smoke():
    sample = ('mode=native frames=3901 cycles=100000 native_cycles=99000 (99.0%)\n'
              '  interpreted: ROM 800 (0.8%, add to cycle_seed_file)'
              '  RAM 200 (0.2%, CPU RAM code no view covers: --capture-log)\n')
    assert counters(sample)['interpreted_rom_cycles'] == 800
    assert counters('mode=native frames=3901 cycles=100 native_cycles=100')['interpreted_ram_cycles'] == 0
    assert compare_hashes({0: {'trace':'A'}},{0:{'trace':'A'}}) is None
    assert compare_hashes({0: {'trace':'A'}},{0:{'trace':'B'}})['frame'] == 0
    for bad in (sample.replace('frames=3901','frames=3900'),
                sample.replace('cycles=100000','cycles=1'),
                'mode=native frames=3901 cycles=100 native_cycles=99'):
        try:
            counters(bad)
        except ValueError:
            pass
        else:
            raise AssertionError('invalid native summary accepted')
    print('PASS JP0843 ROM-free native coverage summary and first-hash-difference smoke')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path)
    p.add_argument('--jp0837-dir', type=Path)
    p.add_argument('--seeded-build', type=Path)
    p.add_argument('--out-dir', type=Path)
    p.add_argument('--smoke', action='store_true')
    args = p.parse_args()
    if args.smoke:
        smoke()
        return 0
    need(all((args.rom, args.jp0837_dir, args.seeded_build, args.out_dir)),
         'require --rom --jp0837-dir --seeded-build --out-dir')
    result = verify(args.rom, args.jp0837_dir, args.seeded_build, args.out_dir)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result['status'] == 'pass' else 1


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, subprocess.TimeoutExpired) as exc:
        print('JP0843 ERROR: '+str(exc), file=sys.stderr)
        raise SystemExit(2)
