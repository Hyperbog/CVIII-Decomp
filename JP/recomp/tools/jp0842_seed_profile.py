#!/usr/bin/env python3
"""JP0842: validate and stage owner-private bank-qualified NESRecomp seeds.

The source is an existing JP0837 native/interpreter run. This tool never
claims interpreter misses are complete code coverage or gameplay parity.
Output must remain outside the source repository.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
# JP0837 already implements the pinned mapper-24 physical bank validator.
import jp0837_bank_coverage_firstdiff as coverage

SCHEMA = 'CVIII-JP0842-bank-qualified-native-seed-profile/v1'
PIN = coverage.ENGINE_PIN
SOURCE_SHA = 'bd41c9c241d100e112c166ee8d0cf0928d39840399c3e28e854d58609ea4e46d'
INPUT_SHA = '6063057986a3beb22decb9407d4bb1d9e8eac5432f2c9c7e996423185fc63589'
FIRST_COMMENT = '# ROM instruction starts executed by the interpreter:'


def require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def private_path(path: Path) -> Path:
    target = path.resolve()
    require(target != ROOT and ROOT not in target.parents,
            'private coverage output cannot be written into the source tree')
    return target


def read_rows(rom: Path, source: Path) -> list[dict]:
    return coverage.bank_misses(source, coverage.rom_prg(rom))


def seed_text(rows: list[dict]) -> str:
    # The pinned NESRecomp cycle recompiler understands and preserves
    # 4k:BB:AAAA values; count is diagnostic and does not affect discovery.
    return (FIRST_COMMENT + ' JP0842 validated mapper24 4KB seeds\n'
            '# Generated privately from a JP0837 native interpreter miss log.\n'
            + ''.join(f'4k:{r["bank4k"]:02X}:{r["pc"]:04X} '
                      f'{r["interpreter_entry_count"]}\n' for r in rows))


def validate(rom: Path, seeds: Path) -> dict:
    """CMake gate: authenticate exact ROM and reject malformed physical seeds."""
    rows = read_rows(rom, seeds)
    require(seeds.read_text(encoding='ascii') == seed_text(rows),
            'seed profile is not canonical JP0842 output; regenerate it')
    require(len(rows) > 0, 'empty seed profile would not improve code coverage')
    return {'seed_count': len(rows),
            'bank4k_count': len({r['bank4k'] for r in rows}),
            'interpreter_entry_count': sum(r['interpreter_entry_count'] for r in rows),
            'seed_sha256': digest(seeds.read_bytes())}


def verify_evidence(folder: Path, rom: Path) -> tuple[list[dict], dict]:
    """Never elevate a standalone handwritten seed list to JP0837 evidence."""
    report = json.loads((folder/'jp0837-report.json').read_text(encoding='ascii'))
    require(report.get('status') == 'executed_here', 'missing real JP0837 run')
    require(report.get('engine_revision_expected') == PIN,
            'JP0837 report engine pin changed')
    require(report.get('source_archive_sha256') == SOURCE_SHA and
            report.get('input_sha256') == INPUT_SHA,
            'JP0837 owner-source identity differs')
    require(report.get('first_native_vs_interpreter_hash_difference') is None,
            'native/interpreter reported a hash divergence')
    # Independently validate source data and replayed hashes rather than
    # accepting counters or assertions copied from a JSON report.
    native = coverage.hashes(folder/'native.hashes')
    interpreted = coverage.hashes(folder/'interp.hashes')
    require(coverage.first_hash_difference(native, interpreted) is None,
            'native/interpreter output hashes disagree')
    source = folder/'native.misses'
    rows = read_rows(rom, source)
    require(len(rows) > 0, 'JP0837 observed no missing compiled ROM entries')
    require(len(rows) == report.get('bank_qualified_interpreter_entries') and
            sum(r['interpreter_entry_count'] for r in rows) ==
            report.get('total_logged_interpreter_entries') and
            sorted({r['bank4k'] for r in rows}) == report.get('bank_qualified_4k_banks'),
            'JP0837 coverage counts do not match actual miss-log contents')
    require((folder/'jp0837-bank-qualified-seeds.txt').read_text(encoding='ascii')
            == coverage.seeds(rows),
            'JP0837 exported seed list differs from the original miss-log')
    meta = {
        'schema': SCHEMA, 'original_rom_sha256': coverage.replay.ROM_SHA256,
        'pinned_engine_revision_expected': PIN,
        'engine_binary_revision_independently_verified': False,
        'source_archive_sha256': SOURCE_SHA, 'input_sha256': INPUT_SHA,
        'jp0837_report_sha256': digest((folder/'jp0837-report.json').read_bytes()),
        'miss_log_sha256': digest(source.read_bytes()),
        'native_hashes_sha256': digest((folder/'native.hashes').read_bytes()),
        'interpreter_hashes_sha256': digest((folder/'interp.hashes').read_bytes()),
        'native_interpreter_hashes_equal': True,
        'bank_qualified_interpreter_entries': len(rows),
        'physical_4k_prg_banks': sorted({r['bank4k'] for r in rows}),
        'total_logged_interpreter_entries': sum(r['interpreter_entry_count'] for r in rows),
        'seed_file_represents_total_code_coverage': False,
        'post_build_native_coverage_measured': False,
        'mesen_full_gameplay_parity_proven': False,
    }
    return rows, meta


def write_if_same(path: Path, value: bytes) -> None:
    if path.is_file():
        require(path.read_bytes() == value,
                f'existing private profile differs: {path}; use a fresh output directory')
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(value)


def prepare(rom: Path, folder: Path, output: Path) -> tuple[Path, dict]:
    rom = rom.resolve(strict=True)
    folder = folder.resolve(strict=True)
    output = private_path(output)
    rows, meta = verify_evidence(folder, rom)
    data = seed_text(rows).encode('ascii')
    meta['seed_sha256'] = digest(data)
    meta['seed_count'] = len(rows)
    path = output/'jp0842-bank-qualified-seeds.txt'
    manifest = output/'jp0842-bank-qualified-manifest.json'
    # Validate source-derived profile before exposing it to the CMake builder.
    with tempfile.TemporaryDirectory() as td:
        probe = Path(td)/'profile.txt'
        probe.write_bytes(data)
        require(validate(rom, probe)['seed_sha256'] == meta['seed_sha256'],
                'seed serialization failed independent validation')
    write_if_same(path, data)
    write_if_same(manifest, (json.dumps(meta, sort_keys=True, indent=2)+'\n').encode('ascii'))
    return path, meta


def smoke() -> None:
    # No ROM needed: parser/serializer round-trip is covered by the real-ROM
    # gate when a private owner profile is prepared or CMake is configured.
    rows = [{'bank4k': 0, 'pc': 0x8000, 'interpreter_entry_count': 2},
            {'bank4k': 63, 'pc': 0xF123, 'interpreter_entry_count': 9}]
    expected = (FIRST_COMMENT + ' JP0842 validated mapper24 4KB seeds\n'
                '# Generated privately from a JP0837 native interpreter miss log.\n'
                '4k:00:8000 2\n4k:3F:F123 9\n')
    assert seed_text(rows) == expected
    try:
        private_path(ROOT / 'JP' / 'recomp' / 'tools' / 'not_allowed.txt')
    except ValueError:
        pass
    else:
        raise AssertionError('private profile allowed in source tree')
    assert digest(b'abc') == 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
    print('PASS JP0842 bank-qualified seed serializer and private-output safety')


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path)
    p.add_argument('--jp0837-dir', type=Path)
    p.add_argument('--out', type=Path)
    p.add_argument('--seed-file', type=Path)
    p.add_argument('--validate-seeds', action='store_true')
    p.add_argument('--smoke', action='store_true')
    a = p.parse_args(argv)
    if a.smoke:
        smoke()
        return 0
    require(a.rom is not None, 'ROM path required')
    if a.validate_seeds:
        require(a.seed_file is not None and a.jp0837_dir is None and a.out is None,
                '--validate-seeds requires --rom and --seed-file only')
        print(json.dumps(validate(a.rom, a.seed_file), sort_keys=True))
        return 0
    require(a.jp0837_dir is not None and a.out is not None and a.seed_file is None,
            'prepare requires --rom --jp0837-dir --out')
    path, report = prepare(a.rom, a.jp0837_dir, a.out)
    print(json.dumps({'seed_file': str(path), **report}, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError, AssertionError) as e:
        print('JP0842 ERROR: '+str(e), file=sys.stderr)
        raise SystemExit(2)