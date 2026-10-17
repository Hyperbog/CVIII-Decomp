#!/usr/bin/env python3
"""JP0642 synthetic adapter/runner tests. Fake processes are NEVER parity."""
from __future__ import annotations
import json
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from jp_scenario_replay_0642 import (build_plan, execute, input_ranges,
    parse_mesen, png_identity, validate_core)

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / 'scenarios/title-start-preflight.json'
ROM_SHA = '958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'


def fail(action):
    try:
        action()
    except (ValueError, OSError, UnicodeError):
        return
    raise AssertionError('accepted malformed replay evidence')


def run():
    plan = build_plan(SAMPLE)
    assert plan['reference_intervals'] == ['0:start@90-92']
    assert plan['reference_gameplay'] == 'NOT_EXERCISED'
    assert plan['rendering_parity'] == 'NOT_EXERCISED'
    assert plan['strict_new_prg_bytes'] == 0
    with tempfile.TemporaryDirectory(prefix='jp0642-') as temp:
        p = Path(temp)
        native = p/'native'
        ref = p/'mesen-agent'
        core = p/'MesenCore.so'
        rom = p/'private.nes'
        for x in (native, ref, core, rom):
            x.write_bytes(b'synthetic-only')
        import hashlib
        core_sha = hashlib.sha256(core.read_bytes()).hexdigest()
        assert validate_core(ref, core_sha)['core_sha256'] == core_sha
        fail(lambda: validate_core(ref, '0'*64))
        lines = p/'buttons.txt'
        lines.write_text('0 START+A\n3 -\n5 LEFT+DOWN\n8 A\n', encoding='ascii')
        assert input_ranges(lines, 10) == [
            '0:a,start@0-2', '0:down,left@5-7', '0:a@8-9']
        good = '\n'.join(json.dumps(x) for x in (
            {'event': 'loaded', 'console': 'Nes'},
            {'event': 'screenshot_saved', 'file': 'private.png'},
            {'event': 'summary', 'ok': True, 'reason': 'frame_limit',
             'start_frame': 1, 'final_frame': 301, 'frames_executed': 300,
             'stop_code': 0})) + '\n'
        assert parse_mesen(good, 300)['frames'] == 300
        for bad in (
            good.replace('"console": "Nes"', '"console": "Snes"'),
            good.replace('"frames_executed": 300', '"frames_executed": 299'),
            good.replace('"reason": "frame_limit"', '"reason": "timeout"'),
            good.replace('"ok": true', '"ok": false'),
            good.replace('"stop_code": 0', '"stop_code": 2'),
            good + '{"event":"summary"}\n',
            good.replace('"event": "summary"', '"event": "lua_error"'),
            good[:-3],
        ):
            fail(lambda data=bad: parse_mesen(data, 300))
        png = p/'image.png'
        png.write_bytes(b'\x89PNG\r\n\x1a\n' + bytes(4) + b'IHDR'
                        + (256).to_bytes(4,'big') + (240).to_bytes(4,'big') + bytes(9))
        assert png_identity(png)['width'] == 256
        png.write_bytes(b'broken')
        fail(lambda: png_identity(png))
        png.write_bytes(b'\x89PNG\r\n\x1a\n' + bytes(4) + b'IHDR'
                        + (256).to_bytes(4,'big') + (240).to_bytes(4,'big') + bytes(9))
        observed = []
        def fake_run(argv, **kwargs):
            observed.append(argv)
            if '--home' in argv:
                out_dir = Path(argv[argv.index('--home')+1]).parent
                (out_dir/'reference-final.png').write_bytes(png.read_bytes())
                (out_dir/'reference-final-state.json').write_text('{}', encoding='utf-8')
                return SimpleNamespace(returncode=0, stdout=good.encode(), stderr=b'')
            return SimpleNamespace(returncode=0, stdout=b'native synthetic output', stderr=b'')
        pf = {'status': 'PASS', 'rom': {'sha256': ROM_SHA},
              'reference_executable_sha256': '1'*64,
              'native_executable_sha256': '2'*64}
        dummy = SimpleNamespace(verify=lambda *args: {'frame_records': 300})
        with patch('jp_scenario_replay_0642.preflight', return_value=pf), \
             patch('jp_scenario_replay_0642.subprocess.run', side_effect=fake_run), \
             patch.dict(sys.modules, {'validate_frame_artifacts_0578': dummy}):
            report = execute(SAMPLE, rom, ref, native, p/'out-success', core_sha, 180)
            assert report['status'] == 'PASS' and len(observed) == 2
            assert report['frame_count_consistency'] == 'PASS'
            assert report['rendering_parity'] == 'NOT_EXERCISED'
            assert report['cpu_trace_parity'] == 'NOT_EXERCISED'
            assert '--edition' in observed[1] and 'original' in observed[1]
            assert '--load-state' not in str(observed)
            fail(lambda: execute(SAMPLE, rom, ref, native, p/'out-success', core_sha, 180))
            fail(lambda: execute(SAMPLE, rom, ref, native, p/'within-repo', '0'*64, 180))
        # A failed reference run MUST NOT stop independent native execution.
        observed.clear()
        def ref_fails(argv, **kwargs):
            observed.append(argv)
            if '--home' in argv:
                return SimpleNamespace(returncode=3, stdout=b'', stderr=b'bad reference')
            return SimpleNamespace(returncode=0, stdout=b'native ok', stderr=b'')
        with patch('jp_scenario_replay_0642.preflight', return_value=pf), \
             patch('jp_scenario_replay_0642.subprocess.run', side_effect=ref_fails), \
             patch.dict(sys.modules, {'validate_frame_artifacts_0578': dummy}):
            report = execute(SAMPLE, rom, ref, native, p/'out-failure', core_sha, 180)
            assert report['status'] == 'FAIL' and len(observed) == 2
            assert report['reference_gameplay'] == 'FAIL' and report['native_gameplay'] == 'PASS'
            assert report['first_execution_failure'] == 'reference'
            assert report['frame_count_consistency'] == 'NOT_EXERCISED'
    print('PASS JP0642 synthetic dual-run adapter, identity, failure and evidence-status tests')


if __name__ == '__main__':
    run()
