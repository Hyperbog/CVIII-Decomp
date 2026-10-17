#!/usr/bin/env python3
"""JP0630: fail-closed provenance audit; synthetic tests do not prove gameplay."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROM_SHA = '958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
EVENT = re.compile(r'^JP0630_EVT (\d+) ([PTRWCSNI]) ([0-9A-F]{4}) ([0-9A-F]{5}) ([0-9A-F]{2}) ([0-9A-F]{2}) ([0-9A-F]{4}) (\d+)$')
ENTRIES = {'P': (0xBB57, 0x07B57, 1), 'T': (0xBB5E, 0x07B5E, 1),
           'C': (0xB7F7, 0x2B7F7, 10), 'S': (0xB806, 0x2B806, 10)}
ROOTS = {0xBEA4, 0xBEDB, 0xBF03, 0xBE8B, 0xBF1C}

def original_prg(rom: bytes) -> bytes:
    if len(rom) != 393232 or rom[:4] != b'NES\x1a' or hashlib.sha256(rom).hexdigest() != ROM_SHA:
        raise ValueError('expected SHA-authenticated retail Japanese iNES image')
    return rom[16:16 + 262144]

def pointer(prg: bytes, selector: int) -> int:
    pos = 0x28000 + 0xB8C2 - 0x8000 + ((2 * selector) & 255)
    if pos + 2 > len(prg):
        raise ValueError('short PRG pointer lookup')
    return int.from_bytes(prg[pos:pos + 2], 'little')

def parse(log: str, prg: bytes) -> dict:
    lines = [s[s.index('JP0630_'):].strip() for s in log.splitlines() if 'JP0630_' in s]
    if not lines or lines[0] != 'JP0630_BEGIN 1' or len(lines) < 2:
        raise ValueError('no single valid capture header')
    if not re.fullmatch(r'JP0630_END \d+', lines[-1]):
        raise ValueError('incomplete capture')
    if lines.count('JP0630_BEGIN 1') != 1 or sum(s.startswith('JP0630_END') for s in lines) != 1:
        raise ValueError('multiple capture sessions')
    if any(s.startswith(('JP0630_TRUNCATED', 'JP0630_MAPPING_ERROR', 'JP0630_STATE_LOADED', 'JP0630_RESET')) for s in lines):
        raise ValueError('interrupted or corrupt mapping')
    events = []
    last_cycle = -1
    old_by_address = {}
    for ordinal, line in enumerate(lines[1:-1], 1):
        m = EVENT.fullmatch(line)
        if m is None:
            raise ValueError('malformed/unknown event')
        n, kind, pc, physical, bank, value, aux, cycle = m.groups()
        e = dict(seq=int(n), kind=kind, pc=int(pc, 16), physical=int(physical, 16),
                 bank=int(bank, 16), value=int(value, 16), aux=int(aux, 16), cycle=int(cycle))
        if e['seq'] != ordinal or e['cycle'] < last_cycle:
            raise ValueError('missing/reordered event or backwards CPU cycle')
        last_cycle = e['cycle']
        if kind in ENTRIES and (e['pc'], e['physical'], e['bank']) != ENTRIES[kind]:
            raise ValueError('entry does not map to authenticated physical PRG')
        if kind in 'PTRW' and e['aux'] > 255:
            raise ValueError('non-byte RAM snapshot')
        if kind in 'NI' and (e['value'] != 0 or e['aux'] != 0):
            raise ValueError('invalid interrupt marker')
        if kind == 'C' and e['aux'] != pointer(prg, e['value']):
            raise ValueError('incorrect mapper-table pointer at consumer')
        if kind in 'RW':
            if kind in old_by_address and e['aux'] != old_by_address[kind]:
                raise ValueError('unobserved intervening RAM mutation')
            old_by_address[kind] = e['value']
        events.append(e)
    if int(lines[-1].split()[1]) != len(events):
        raise ValueError('footer event count does not match')
    counts = Counter(e['kind'] for e in events)
    recent_p = recent_t = last_w = pending_c = None
    links = []
    completed = []
    interrupts = 0
    writes = 0
    for e in events:
        kind = e['kind']
        if kind in 'NI':
            interrupts += 1
        elif kind == 'P':
            recent_p = e
        elif kind == 'T':
            recent_t = (e, recent_p, interrupts)
        elif kind == 'W':
            writes += 1
            t = recent_t
            matched = bool(t and t[0]['seq'] == e['seq'] - 1 and
                           t[0]['value'] == e['value'] and
                           interrupts == t[2])
            last_w = (e, t[0]['seq'] if matched else None,
                      t[1]['seq'] if matched and t[1] else None)
            recent_t = None
        elif kind == 'C':
            candidate = bool(last_w and last_w[0]['value'] == e['value'])
            links.append({'consumer_seq': e['seq'], 'selector': f"{e['value']:02X}",
                          'expected_pointer': f"{e['aux']:04X}",
                          'last_write_seq': last_w[0]['seq'] if candidate else None,
                          'physically_gated_sta_seq': last_w[1] if candidate else None,
                          'candidate_source_entry_seq': last_w[2] if candidate else None,
                          'known_stream_root': e['aux'] in ROOTS,
                          'producer_to_consumer_causality_proved': False})
            if pending_c is not None:
                raise ValueError('nested consumer entry without completed postcondition')
            pending_c = (e, interrupts, writes)
        elif kind == 'S':
            if pending_c is None:
                raise ValueError('postcondition without consumer entry')
            start, before, before_writes = pending_c
            completed.append({'consumer_seq': start['seq'], 'post_seq': e['seq'],
                              'expected_pointer': f"{start['aux']:04X}",
                              'observed_pointer': f"{e['aux']:04X}",
                              'pointer_matches': start['aux'] == e['aux'],
                              'interrupts_between': interrupts - before,
                              'writes_to_07a0_between': writes - before_writes,
                              'selector_changed': e['value'] != start['value']})
            pending_c = None
    return {'schema': 1, 'rom_sha256': ROM_SHA, 'status': 'TRACE_FORMAT_AND_POSTCONDITIONS_ONLY',
            'event_counts': {k: counts[k] for k in 'PTRWCSNI'}, 'total_events': len(events),
            'producer_ram30_values': sorted({f"{e['value']:02X}" for e in events if e['kind'] == 'P'}),
            'consumer_links': links[:100], 'links_omitted': max(len(links)-100, 0),
            'pointer_postconditions': completed[:100], 'postconditions_omitted': max(len(completed)-100, 0),
            'orphan_consumer_entries': 1 if pending_c else 0,
            'strict_new_prg_bytes': 0, 'r002_closed': False,
            'independent_gameplay_session_verified': False}

def smoke() -> None:
    prg = bytearray(262144)
    at = 0x28000 + 0xB8C2 - 0x8000
    prg[at:at+2] = (0xBEA4).to_bytes(2, 'little')
    base = ['JP0630_BEGIN 1',
            'JP0630_EVT 1 R 9000 00000 0A 00 0000 8',
            'JP0630_EVT 2 P BB57 07B57 01 00 0000 10',
            'JP0630_EVT 3 T BB5E 07B5E 01 00 0000 15',
            'JP0630_EVT 4 W BB5E 07B5E 01 00 0000 19',
            'JP0630_EVT 5 N E057 3E057 01 00 0000 22',
            'JP0630_EVT 6 C B7F7 2B7F7 0A 00 BEA4 30',
            'JP0630_EVT 7 S B806 2B806 0A 00 BEA4 45',
            'JP0630_END 7']
    good = '\n'.join(base) + '\n'
    actual = parse(good, bytes(prg))
    assert actual['pointer_postconditions'][0]['pointer_matches']
    assert actual['consumer_links'][0]['physically_gated_sta_seq'] == 3
    assert actual['event_counts']['N'] == 1
    for bad in (good.replace('07B57', '17B57'), good.replace('2B806 0A', '2B806 01'),
                good.replace('00 BEA4 30', '00 0000 30'),
                good.replace('JP0630_END 7', 'JP0630_END 8'),
                good.replace('JP0630_END 7', 'JP0630_STATE_LOADED\nJP0630_END 7'),
                good.replace('JP0630_END 7', 'JP0630_RESET\nJP0630_END 7'),
                good.replace('JP0630_END 7', 'JP0630_TRUNCATED\nJP0630_END 7'),
                good.replace('JP0630_EVT 4 W', 'JP0630_EVT 9 W'),
                good.replace('0000 22', '0000 12'),
                good.replace('JP0630_EVT 7 S', 'JP0630_EVT 7 X')):
        try:
            parse(bad, bytes(prg))
        except ValueError:
            continue
        raise AssertionError('accepted invalid provenance fixture')
    changed = good.replace('00 BEA4 45', '00 BEEF 45')
    assert not parse(changed, bytes(prg))['pointer_postconditions'][0]['pointer_matches']
    print('PASS JP0630 ROM-free provenance and postcondition contract; no gameplay claimed')

def main() -> None:
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--smoke', action='store_true')
    a.add_argument('--rom', type=Path)
    a.add_argument('--trace', type=Path)
    a.add_argument('--out', type=Path)
    args = a.parse_args()
    if args.smoke:
        smoke()
        return
    if not args.rom or not args.trace:
        a.error('--rom and --trace required')
    report = parse(args.trace.read_text(encoding='utf-8'), original_prg(args.rom.read_bytes()))
    result = json.dumps(report, indent=2, sort_keys=True) + '\n'
    if args.out:
        args.out.write_text(result, encoding='utf-8')
    print(result, end='')

if __name__ == '__main__':
    main()
