#!/usr/bin/env python3
"""JP0688c ROM-free independent checker for the Windows matrix + WRAM excerpt."""
import argparse
import json
import re
from pathlib import Path

SOURCE_PIN = '2b4fcdb98c9e702be3fb365cfc645003c50b5fc1'
TEST_PIN = '95d8f621ae55cee0d09b91519a8989ae0e64753b'
TESTS = ('vbl_set_time', 'nmi_control', 'nmi_timing', 'branch_delays_irq')
HEX64 = re.compile(r'^[0-9a-fA-F]{64}$')
WRAM = re.compile(r'^wram ([0-9a-fA-F]{4}):((?: [0-9a-fA-F]{2}){32})$')
MARKER = re.compile(r'^=== ([a-z_]+-align[0-3]) ===$')


def read_evidence(path):
    blocks = {}
    current = None
    for line in Path(path).read_text(encoding='ascii').splitlines():
        if not line.strip():
            continue
        marker = MARKER.fullmatch(line)
        if marker:
            current = marker.group(1)
            if current in blocks:
                raise ValueError(f'duplicate evidence case: {current}')
            blocks[current] = []
        elif current is None:
            raise ValueError('evidence line before case marker')
        else:
            parsed = WRAM.fullmatch(line)
            if not parsed:
                raise ValueError(f'bad WRAM line in {current}: {line[:100]}')
            expected = len(blocks[current]) * 32
            if int(parsed.group(1), 16) != expected:
                raise ValueError(f'nonconsecutive WRAM offset in {current}')
            if len(blocks[current]) >= 3:
                raise ValueError(f'excess WRAM excerpt in {current}')
            blocks[current].append(bytes.fromhex(parsed.group(2)))
    return blocks


def expected_verdict(code, signature, dump, result):
    if result['ExitCode'] != 0:
        return 'RUNTIME_ERROR'
    if not dump:
        return 'NO_DUMP'
    if code is None:
        return 'NO_WRAM_RESULT'
    if not signature:
        return 'INVALID_TEST_SIGNATURE'
    if code == 0:
        return 'PASS'
    if code == 0x80:
        return 'STILL_RUNNING'
    if code == 0x81:
        return 'RESET_REQUIRED'
    if 1 <= code <= 0x7F:
        return 'TEST_FAILURE_CODE'
    return 'INVALID_RESULT_CODE'


def verify(report, blocks):
    failures = []
    expect = {f'{test}-align{a}' for test in TESTS for a in range(4)}
    if report.get('Protocol') != 'JP0688c-v1':
        failures.append('protocol mismatch')
    if report.get('SourcePin') != SOURCE_PIN or report.get('TestPin') != TEST_PIN:
        failures.append('pinned source or public ROM revision mismatch')
    if report.get('Host') != 'cyc_interp' or report.get('PRGRAMHeaderCopiesOnly') is not True:
        failures.append('host or header-only procedure mismatch')
    if report.get('FrameCount') != 900 or report.get('SampleFrame') != 899:
        failures.append('frame window mismatch')
    roms = report.get('RomMetadata', [])
    if len(roms) != 4 or {r.get('Test') for r in roms} != set(TESTS):
        failures.append('ROM metadata incomplete')
    for r in roms:
        if r.get('HeaderPRGRAMBytes') != 8192:
            failures.append(f'wrong patched RAM size: {r.get("Test")}')
        a, b = r.get('OriginalSHA256', ''), r.get('HeaderOnlyCopySHA256', '')
        if not HEX64.fullmatch(a) or not HEX64.fullmatch(b) or a.lower() == b.lower():
            failures.append(f'invalid ROM SHA256 metadata: {r.get("Test")}')
    results = report.get('Results', [])
    seen = {}
    for row in results:
        key = f'{row.get("Test")}-align{row.get("Alignment")}'
        if key in seen:
            failures.append(f'duplicate result: {key}')
        seen[key] = row
    if set(seen) != expect:
        failures.append(f'wrong result matrix: missing={sorted(expect-set(seen))}, extra={sorted(set(seen)-expect)}')
    if set(blocks) != expect:
        failures.append(f'wrong evidence matrix: missing={sorted(expect-set(blocks))}')
    observed = []
    for key in sorted(expect):
        if key not in seen or key not in blocks:
            continue
        row, lines = seen[key], blocks[key]
        first = lines[0] if lines else b''
        code = first[0] if len(first) >= 4 else None
        sig = len(first) >= 4 and first[1:4] == b'\xDE\xB0\x61'
        dump = row.get('DumpExists') is True
        expected = expected_verdict(code, sig, dump, row)
        code_str = f'{code:02X}' if code is not None else None
        if row.get('Verdict') != expected or row.get('ResultCode') != code_str:
            failures.append(f'{key}: claimed {row.get("Verdict")}/{row.get("ResultCode")}, derived {expected}/{code_str}')
        if row.get('SignatureValid') is not sig:
            failures.append(f'{key}: signature flag conflicts with actual WRAM')
        observed.append((key, code_str, expected))
    return failures, observed


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('report', type=Path)
    p.add_argument('evidence', type=Path)
    args = p.parse_args()
    report = json.loads(args.report.read_text(encoding='utf-8-sig'))
    failures, observed = verify(report, read_evidence(args.evidence))
    for key, code, status in observed:
        print(f'{key:29} {code or "NA":>2} {status}')
    if failures:
        print('\nEVIDENCE REJECTED:')
        for fail in failures:
            print('  -', fail)
        return 2
    passes = sum(status == 'PASS' for _, _, status in observed)
    test_failures = sum(status == 'TEST_FAILURE_CODE' for _, _, status in observed)
    unresolved = len(observed) - passes - test_failures
    print(f'\nEvidence internally consistent: {passes} PASS, {test_failures} test failures, {unresolved} unresolved.')
    print('This verifies recorded test status, not independently established hardware correctness.')
    return 0 if not unresolved else 1


if __name__ == '__main__':
    raise SystemExit(main())
