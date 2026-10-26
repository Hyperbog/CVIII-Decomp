#!/usr/bin/env python3
"""Owner-local Windows NESRecomp keyboard Player 1 profiles.

Edits only [Keyboard.Player1] and [Input] Player1Source in the pinned
NESRecomp config.ini. Never edits game ROM, save states, controller mappings,
audio, display, shortcut bindings, or the upstream SDL host source.
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

SCHEMA = 'cviii-native-keyboard-profile/v1'
KEYS = ('a', 'b', 'select', 'start', 'up', 'down', 'left', 'right')
DEFAULT = dict(zip(KEYS, ('Z', 'X', 'Backslash', 'Return', 'Up', 'Down', 'Left', 'Right')))
WASD = dict(zip(KEYS, ('J', 'K', 'Right Shift', 'Return', 'W', 'S', 'A', 'D')))
PRESETS = {'default': DEFAULT, 'wasd': WASD}
NAME = re.compile(r'[a-z][a-z0-9_-]{0,31}\Z', re.ASCII)
SECTION = re.compile(r'^\s*\[([^\]\r\n]+)\]\s*$', re.ASCII)
ENTRY = re.compile(r'^\s*([^=\r\n]+?)\s*=\s*([^\r\n]*)$', re.ASCII)
VALID_SCANCODES = {chr(k) for k in range(ord('A'), ord('Z')+1)} | {
    str(i) for i in range(10)} | {f'F{i}' for i in range(1, 25)} | {
    'Backslash', 'Return', 'Escape', 'Tab', 'Space', 'Left Shift', 'Right Shift',
    'Left Ctrl', 'Right Ctrl', 'Left Alt', 'Right Alt', 'Up', 'Down', 'Left',
    'Right', 'Backspace', 'Delete', 'Home', 'End', 'PageUp', 'PageDown',
    'Insert', 'Minus', 'Equals', 'Comma', 'Period', 'Slash', 'Semicolon',
    'Apostrophe', 'Left Bracket', 'Right Bracket', 'Grave', 'CapsLock'}
BLOCKED = {'Escape', 'F4', 'F6', 'F8', 'F9', 'F10', 'F11', 'F12'}


def fail(reason: str) -> None:
    raise ValueError(reason)


def name_ok(value: str) -> str:
    if not NAME.fullmatch(value) or value in PRESETS:
        fail('Unsafe or reserved custom profile name (use lowercase letters, digits, _ or -)')
    return value


def validate(mapping: dict) -> dict[str, str]:
    if not isinstance(mapping, dict) or set(mapping) != set(KEYS):
        fail('Profile must contain exactly the eight NES Player 1 buttons')
    out = {}
    for key in KEYS:
        value = mapping[key]
        if type(value) is not str or value not in VALID_SCANCODES or value in BLOCKED:
            fail(f'Unsupported or reserved keyboard scancode for {key}: {value!r}')
        out[key] = value
    if len(set(out.values())) != len(KEYS):
        fail('A keyboard scancode cannot control two Player 1 actions')
    return out


def file_bytes(path: Path, max_bytes: int) -> bytes:
    if path.is_symlink() or not path.is_file():
        fail(f'Required regular non-symlink file missing: {path}')
    if path.stat().st_size > max_bytes:
        fail(f'File is larger than the safe configuration bound: {path.name}')
    data = path.read_bytes()
    if b'\x00' in data:
        fail('NUL byte in settings/profile file')
    return data


def read_ini(raw: bytes) -> tuple[str, list[str], str]:
    try:
        content = raw.decode('utf-8-sig')
    except UnicodeError as e:
        raise ValueError('config.ini must be UTF-8/ASCII text') from e
    if '\ufeff' in content:
        fail('Unexpected mid-file BOM')
    newline = '\r\n' if b'\r\n' in raw else '\n'
    return content, content.splitlines(keepends=True), newline


def inspect(lines: list[str]) -> tuple[dict[str, dict[str, tuple[int, str]]], dict[str, list[int]]]:
    sections: dict[str, dict[str, tuple[int, str]]] = {}
    starts: dict[str, list[int]] = {}
    active = ''
    for ix, line in enumerate(lines):
        stripped = line.rstrip('\r\n')
        m = SECTION.fullmatch(stripped)
        if m:
            active = m.group(1).casefold()
            starts.setdefault(active, []).append(ix)
            sections.setdefault(active, {})
            continue
        if active not in ('keyboard.player1', 'input'):
            continue
        if not stripped.strip() or stripped.lstrip().startswith((';', '#')):
            continue
        m = ENTRY.fullmatch(stripped)
        if not m:
            fail(f'Malformed binding settings line {ix+1}; refusing to modify original')
        key = m.group(1).strip().casefold()
        relevant = (active == 'keyboard.player1' and key in KEYS) or (
            active == 'input' and key == 'player1source')
        if relevant:
            if key in sections[active]:
                fail(f'Duplicate {active}.{key}; original settings unchanged')
            sections[active][key] = (ix, m.group(2).strip())
    for section in ('keyboard.player1', 'input'):
        if len(starts.get(section, [])) > 1:
            fail(f'Duplicate [{section}] blocks; settings unchanged')
    return sections, starts


def active_profile(raw: bytes) -> dict[str, str]:
    _content, lines, _newline = read_ini(raw)
    sections, starts = inspect(lines)
    section = sections.get('keyboard.player1', {})
    if not starts.get('keyboard.player1') or set(section) != set(KEYS):
        fail('Run the native game once to create complete [Keyboard.Player1] bindings')
    return validate({key: section[key][1] for key in KEYS})


def rewrite(raw: bytes, mapping: dict[str, str]) -> bytes:
    mapping = validate(mapping)
    content, lines, newline = read_ini(raw)
    sections, starts = inspect(lines)
    if not content.strip():
        fail('Existing config.ini is empty; launch the native game once')
    changes = {'keyboard.player1': mapping, 'input': {'Player1Source': '1'}}
    # Work in reverse section order so insertions do not shift earlier indices.
    for section in sorted(changes, key=lambda s: starts.get(s, [len(lines)])[0], reverse=True):
        target = changes[section]
        if section not in starts:
            if lines and not lines[-1].endswith(('\n', '\r')):
                lines[-1] += newline
            lines.append(f'[{"Keyboard.Player1" if section.startswith("keyboard") else "Input"}]'+newline)
            for key, value in target.items():
                lines.append(f'{key} = {value}'+newline)
        else:
            existing = sections.get(section, {})
            for key, value in target.items():
                if key.casefold() in existing:
                    ix, _prev = existing[key.casefold()]
                    lines[ix] = f'{key} = {value}'+newline
                else:
                    # Insert at section end; first add missing keys after all updates.
                    pass
            missing = [(key, val) for key, val in target.items() if key.casefold() not in existing]
            if missing:
                beginning = starts[section][0]+1
                end = next((j for j in range(beginning, len(lines)) if SECTION.fullmatch(lines[j].rstrip('\r\n'))), len(lines))
                lines[end:end] = [f'{key} = {value}'+newline for key, value in missing]
    result = ''.join(lines).encode('utf-8')
    # All unrelated config blocks survive; and exact effective target values are checked.
    assert active_profile(result) == mapping
    return result


def profile_file(directory: Path, name: str) -> Path:
    return directory / (name_ok(name) + '.json')


def read_profile(path: Path) -> dict[str, str]:
    data = file_bytes(path, 4096)
    try:
        doc = json.loads(data.decode('utf-8'))
    except (ValueError, UnicodeError) as e:
        raise ValueError('Profile is not valid UTF-8 JSON') from e
    if not isinstance(doc, dict) or set(doc) != {'schema', 'bindings'} or doc['schema'] != SCHEMA:
        fail('Unexpected controls-profile schema')
    return validate(doc['bindings'])


def exclusive_write(path: Path, data: bytes) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def atomic_replace(path: Path, raw: bytes) -> None:
    temp = path.parent / (path.name + f'.new-{os.getpid()}-{time.time_ns()}')
    exclusive_write(temp, raw)
    try:
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def execute(root: Path, action: str, name: str = '',
            remap: tuple[str, str] = ('', '')) -> str:
    if root.is_symlink() or not root.is_dir():
        fail('Private native-game folder must exist and must not be a symlink')
    config = root / 'config.ini'
    profiles = root / 'control-profiles'
    if profiles.is_symlink():
        fail('Refusing symlink control-profiles folder')
    if action == 'list':
        names = sorted(p.stem for p in profiles.glob('*.json') if
                       p.is_file() and not p.is_symlink() and NAME.fullmatch(p.stem)) if profiles.is_dir() else []
        return 'Built-ins: default, wasd\nSaved: ' + (', '.join(names) if names else '(none)')
    original = file_bytes(config, 262144)
    if action == 'show':
        return 'Current Player 1: ' + ', '.join(f'{key}={val}' for key, val in active_profile(original).items())
    if action == 'save':
        name_ok(name)
        source = active_profile(original)
        profiles.mkdir(exist_ok=True)
        doc = (json.dumps({'schema': SCHEMA, 'bindings': source}, sort_keys=True, indent=2)+'\n').encode('utf-8')
        exclusive_write(profile_file(profiles, name), doc)
        return f'Saved custom profile {name}; game settings unchanged'
    if action in ('apply', 'remap'):
        if action == 'apply':
            if name in PRESETS:
                values = PRESETS[name]
            else:
                values = read_profile(profile_file(profiles, name))
            description = name
        else:
            button, scancode = remap
            if button not in KEYS:
                fail('Unknown NES Player 1 button; choose a,b,select,start,up,down,left,right')
            if scancode not in VALID_SCANCODES or scancode in BLOCKED:
                fail('Unsupported or reserved keyboard scancode: ' + repr(scancode))
            values = active_profile(original).copy()
            old_key = values[button]
            # Swap the other button if this key is already in use. Never
            # create an ambiguous double-binding or drop an existing key.
            other = next((k for k in KEYS if k != button and values[k] == scancode), None)
            if other is not None:
                values[other] = old_key
            values[button] = scancode
            values = validate(values)
            description = f'{button} to {scancode}' + (' (swap)' if other else '')
        patched = rewrite(original, values)
        if patched == original:
            return f'Binding/profile {description} already active; no files written'
        # Back up before replacing settings; never overwrite an earlier backup.
        backups = root / 'control-backups'
        if backups.is_symlink():
            fail('Refusing symlink control-backups folder')
        backups.mkdir(exist_ok=True)
        # Windows system time may have much coarser resolution than time_ns.
        # O_EXCL + an attempt suffix guarantees no prior backup is clobbered.
        for attempt in range(100):
            backup = backups / ('config-' + str(time.time_ns()) +
                                '-' + str(attempt) + '.ini.bak')
            try:
                exclusive_write(backup, original)
                break
            except FileExistsError:
                continue
        else:
            fail('Could not allocate a unique settings backup; config unchanged')
        atomic_replace(config, patched)
        return f'Applied {description}; prior settings backed up as {backup.name}'
    fail('Expected list, show, save, apply or remap action')


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', required=True, type=Path, help='Actual private AlphaCandidate directory (contains config.ini)')
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument('--list', action='store_true')
    group.add_argument('--show', action='store_true')
    group.add_argument('--save', metavar='NAME')
    group.add_argument('--apply', metavar='NAME')
    group.add_argument('--remap', nargs=2, metavar=('BUTTON', 'SCANCODE'))
    a = p.parse_args()
    action = next(x for x in ('list', 'show', 'save', 'apply', 'remap') if getattr(a, x))
    try:
        print(execute(a.root, action,
                      getattr(a, action) if action in ('save', 'apply') else '',
                      tuple(a.remap) if action == 'remap' else ('', '')))
        return 0
    except (ValueError, OSError) as e:
        print(f'Control profiles: {e}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
