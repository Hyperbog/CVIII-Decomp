#!/usr/bin/env python3
"""JP0662: guard moving retired 0509/0510 packages and 6502 assembly.

This is not an all-folders/production-code migration. It tests the exact
selected historical moves and the consumer rewrite boundary, ROM-free.
"""
from __future__ import annotations
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MOVED = (
    ('JP/native0509/CMakeLists.txt','JP/decomp/legacy/native0509/CMakeLists.txt'),
    ('JP/native0509/README.md','JP/decomp/legacy/native0509/README.md'),
    ('JP/standalone0509/CMakeLists.txt','JP/decomp/legacy/standalone0509/CMakeLists.txt'),
    ('JP/standalone0509/README.md','JP/decomp/legacy/standalone0509/README.md'),
    ('JP/native_demo0510/CMakeLists.txt','JP/decomp/legacy/native_demo0510/CMakeLists.txt'),
    ('JP/native_demo0510/README.md','JP/decomp/legacy/native_demo0510/README.md'),
    ('JP/native_demo0510/.gitignore','JP/decomp/legacy/native_demo0510/.gitignore'),
    ('JP/native_demo0510/run_linux.sh','JP/decomp/legacy/native_demo0510/run_linux.sh'),
    ('JP/native_demo0510/src/main.cpp','JP/decomp/legacy/native_demo0510/src/main.cpp'),
    ('JP/native_demo0510/tools/make_test_assets.py',
     'JP/decomp/legacy/native_demo0510/tools/make_test_assets.py'),
    ('JP/recomp/actor_tail_0525.asm','JP/decomp/asm/actor_tail_0525.asm'),
    ('JP/recomp/fixed_tail_0525.asm','JP/decomp/asm/fixed_tail_0525.asm'),
    ('JP/recomp/fixed_scheduler_0526.asm','JP/decomp/asm/fixed_scheduler_0526.asm'),
    ('JP/recomp/raw0b_callbacks_0526.asm','JP/decomp/asm/raw0b_callbacks_0526.asm'),
)
SCRIPTS = (
    '.github/workflows/jp-native-regressions.yml',
    '.github/workflows/jp_native_pc_demo.yml',
    'JP/decomp/tools/run_native_regressions.sh',
    'JP/decomp/tools/build_whole_cart_recomp_0529.py',
    'JP/decomp/tools/test_recomp_6502_0525.py',
    'JP/decomp/tools/test_recomp_6502_0526.py',
)
OLD_ROOTS = ('JP/native0509', 'JP/standalone0509',
             'JP/native_demo0510')
NEW_ROOTS = ('JP/decomp/legacy/native0509',
             'JP/decomp/legacy/standalone0509',
             'JP/decomp/legacy/native_demo0510')


def require(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def audit(root: Path = ROOT) -> dict:
    require(root.is_dir(), f'Missing repository root: {root}')
    require(len(MOVED) == 14 and len({old for old, _ in MOVED}) == len(MOVED) and
            len({new for _, new in MOVED}) == len(MOVED),
            'Moved historic file census drift')
    for old, new in MOVED:
        require(not (root / old).exists(), f'Superseded root still exists: {old}')
        require((root / new).is_file(), f'Lost original historic source: {new}')
    for old in OLD_ROOTS:
        require(not (root / old).exists(), f'Old prototype root not removed: {old}')
    for new in NEW_ROOTS:
        require((root / new).is_dir(), f'New historic source root missing: {new}')
    for md in ('JP/decomp/README.md','JP/decomp/legacy/README.md',
               'JP/recomp/README.md'):
        require((root / md).is_file(), 'Workstream landing page missing: '+md)
    require(set(p.name for p in (root/'JP/recomp').iterdir()) >= {'README.md','native','release','tools'},
            'Old asm or source has been mixed back into native JP/recomp product entry')
    source_0509=(root/'JP/decomp/legacy/native0509/CMakeLists.txt').read_text()
    source_standalone=(root/'JP/decomp/legacy/standalone0509/CMakeLists.txt').read_text()
    for s, n in ((source_0509,'native0509'),(source_standalone,'standalone0509')):
        require('../../src' in s and '../../tools' in s and
                '../../tests' in s, 'CMake source directories broken: '+n)
    workflows={p:(root/p).read_text() for p in SCRIPTS}
    for p, content in workflows.items():
        for old in OLD_ROOTS:
            require(old not in content, f'Stale old path {old} in {p}')
    asm='JP/decomp/asm'
    for n in ('build_whole_cart_recomp_0529.py',
              'test_recomp_6502_0525.py','test_recomp_6502_0526.py'):
        content=workflows['JP/decomp/tools/'+n]
        require(("'asm'" in content or '"asm"' in content) and "ROOT" in content,
                'Mnemonic source consumer was not migrated: '+n)
    for p in ('JP/decomp/analysis/RESUME_STATE.json','JP/decomp/analysis/PROGRESS_SCORE.csv',
              'JP/recomp/native/nesrecomp_cycle/CMakeLists.txt',
              'JP/recomp/release/alpha/Build-And-Play.ps1',
              'JP/decomp/tools/audit_native_evidence_ledger.py'):
        require((root/p).is_file(), 'Active product/certificate was damaged: '+p)
    return {'relocated_historical_source_files':len(MOVED),
            'remaining_old_prototype_directories':0,
            'native_game_build_paths_unchanged':True,
            'semantic_evidence_paths_unchanged':True}


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo-root',type=Path,default=ROOT)
    a=p.parse_args()
    result=audit(a.repo_root.resolve())
    print('PASS JP0662 separated retired C++/6502 sources:',result)


if __name__=='__main__':
    main()
