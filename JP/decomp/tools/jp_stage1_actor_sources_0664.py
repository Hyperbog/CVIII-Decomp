#!/usr/bin/env python3
"""Original JP Stage 1-02 source cells and scroll-refresh decision.

Private owner-ROM data export; no original bytes are included in source.
This models bounded source lookups, not a native offscreen spawn engine.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROM_SHA = '958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
BANK_SHA = '1460df577d44e114c64fdf34a8837629765f3f6a93d45796fdf81e5ffacb5ed8'
PRG_BANK = 0x0A
CPU_BASE = 0x8000
BANK_BYTES = 0x4000
SOURCE_ROOM = (0, 1, 0)       # conditional raw0A $801E selector triple
SOURCE_ROOT = 0x93E8          # twelve original room-source bytes
SOURCE_CELLS = 6
# ROM code / pointer locations, not original data embedded in the program.
FIRST_TIER = 0x92AE
LOW_POINTERS = 0x9F6E
HIGH_POINTERS = 0xA06E
EVENT_ROWS = 0x8523
AUX_LOW_POINTERS = 0xA56B
AUX_HIGH_POINTERS = 0xA66B
AUX_SCRIPTS = 0x8329
SLOT_PHASE = 0x8410


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def original_bank(rom: bytes) -> bytes:
    require(len(rom) == 393232 and rom[:4] == b'NES\x1a' and
            hashlib.sha256(rom).hexdigest() == ROM_SHA,
            'incorrect original Japanese cartridge')
    require((rom[6] >> 4 | rom[7] & 0xF0) == 24,
            'original mapper must be VRC6 mapper 24')
    bank = rom[16 + PRG_BANK * BANK_BYTES:16 + (PRG_BANK + 1) * BANK_BYTES]
    require(hashlib.sha256(bank).hexdigest() == BANK_SHA,
            'original physical raw0A fingerprint differs')
    return bank


def u8(bank: bytes, cpu: int) -> int:
    require(len(bank) == BANK_BYTES and CPU_BASE <= cpu < CPU_BASE + BANK_BYTES,
            'raw0A address escaped physical bank: $' + format(cpu, '04X'))
    return bank[cpu - CPU_BASE]


def word(bank: bytes, cpu: int) -> int:
    return u8(bank, cpu) | (u8(bank, cpu + 1) << 8)


def room_root(bank: bytes, stage: int, room: int, section: int) -> int:
    """Exact original $801E-$8046 three-level pointer selection."""
    require((stage, room, section) == SOURCE_ROOM,
            'only the independently sourced Stage 1-02 triple is admitted')
    middle = word(bank, FIRST_TIER + stage * 2)
    leaf_table = word(bank, middle + room * 2)
    root = word(bank, leaf_table + section * 2)
    require((middle, leaf_table, root) == (0x92CC, 0x9322, SOURCE_ROOT),
            'Stage 1-02 original pointer chain is inconsistent')
    return root


def source_pointer(bank: bytes, source_id: int, flag_07f6: int = 0) -> tuple[int, str]:
    """Original raw0A $8111-$813A: ASL carry and $07F6 fallback."""
    require(0 <= source_id <= 255 and 0 <= flag_07f6 <= 255,
            'source selector/flag must be unsigned bytes')
    y = (source_id << 1) & 255
    if source_id < 0x80 or (flag_07f6 == 0 and y >= 0xA0):
        table = LOW_POINTERS
        selected = 'low'
    else:
        table = HIGH_POINTERS
        selected = 'high'
    ptr = word(bank, table + y)
    require(CPU_BASE <= ptr <= 0xBFFB, 'source record escapes raw0A')
    return ptr, selected


def auxiliary_pointer(bank: bytes, auxiliary_id: int) -> int:
    """Original $818F-$81AF four-byte auxiliary object source."""
    require(0 <= auxiliary_id < 256, 'auxiliary source ID not a byte')
    table = AUX_HIGH_POINTERS if auxiliary_id & 0x80 else AUX_LOW_POINTERS
    ptr = word(bank, table + ((auxiliary_id << 1) & 255))
    require(CPU_BASE <= ptr <= 0xBFFC, 'auxiliary source leaves raw0A')
    return ptr


def stage1_cells(bank: bytes, flag_07f6: int = 0,
                 mask_f0: int = 0) -> list[dict]:
    """Six source slots: $8410 phase, $8111 source ID, $8140 active row."""
    require(0 <= mask_f0 <= 255, '$F0 bitfield must be a byte')
    root = room_root(bank, *SOURCE_ROOM)
    slots = []
    for phase in range(SOURCE_CELLS):
        slot = u8(bank, SLOT_PHASE + phase)
        require(slot == phase, 'unexpected first-six original slot mapping')
        source_id = u8(bank, root + 2 * phase)
        auxiliary_id = u8(bank, root + 2 * phase + 1)
        item = {'phase': phase, 'source_slot': slot,
                'room_source_id': source_id, 'auxiliary_id': auxiliary_id,
                'active': False}
        if source_id:
            ptr, table = source_pointer(bank, source_id, flag_07f6)
            fields = [u8(bank, ptr + j) for j in range(5)]
            item.update({'source_cpu': f'{ptr:04X}', 'source_table': table,
                         'record': fields, 'event_row': fields[0],
                         'active': fields[0] != 0,
                         'initial_event_index': 0,
                         'initial_guard_source': '($0A + carry from original X add) & 1'})
            if fields[0]:
                event_table = word(bank, EVENT_ROWS + 2 * fields[0])
                handler = word(bank, event_table)  # initial event index $00
                require(CPU_BASE <= handler < 0xC000, 'event dispatcher leaves raw0A')
                item.update({'event_table_cpu': f'{event_table:04X}',
                             'initial_handler_cpu': f'{handler:04X}'})
        # $8182 adds 13 to X, and $8440 checks $F0..$F3. In the
        # six phase indices for this room, the source byte is $F0.
        gate_mask = u8(bank, 0x8451 + phase)
        gate_group = u8(bank, 0x8471 + phase)
        require(gate_group == 0 and gate_mask == (1 << phase),
                'original Stage 1-02 auxiliary gate changed')
        item['auxiliary_slot'] = slot + 13
        item['auxiliary_gate_mask_f0'] = gate_mask
        item['auxiliary_enabled'] = False
        if auxiliary_id and not (mask_f0 & gate_mask):
            aptr = auxiliary_pointer(bank, auxiliary_id)
            ar = [u8(bank, aptr + j) for j in range(4)]
            require(ar[0] >= 0x80, 'auxiliary script index below $80')
            script = u8(bank, AUX_SCRIPTS + ar[0] - 0x80)
            item.update({'auxiliary_enabled': True,
                         'auxiliary_source_cpu': f'{aptr:04X}',
                         'auxiliary_record': ar,
                         'auxiliary_type': ar[0], 'auxiliary_script': script})
        slots.append(item)
    return slots


def refresh_gate(scroll_53: int, old_74: int, movement_6b: int,
                 stage_34: int = 0, room_35: int = 1, section_36: int = 0) -> dict:
    """$808F-$80D0 conditional source-cell refresh, NOT a frame clock.

    This gate assumes execution reaches raw0A:$808F and caller's
    $8491 check behaves as recorded; $53/$74/$6B are RAM inputs.
    """
    require(all(0 <= v < 256 for v in
                (scroll_53, old_74, movement_6b, stage_34, room_35, section_36)),
            'refresh gate inputs must be unsigned bytes')
    if (stage_34, room_35, section_36) == (0x0E, 1, 1):
        return {'refresh': False, 'reason': 'original $8491 excluded selector'}
    if movement_6b == 0:
        return {'refresh': False, 'reason': 'zero $6B: no movement'}
    fraction = scroll_53 & 0x3F
    if movement_6b == 2 and fraction == 1:
        candidate = scroll_53 & 0xFE
        edge = 'backward-one'
    elif movement_6b not in (1, 2, 255) and fraction == 63:
        candidate = (scroll_53 + 1) & 255
        edge = 'forward-boundary'
    elif fraction == 0:
        candidate = scroll_53
        edge = 'aligned-boundary'
    else:
        return {'refresh': False, 'reason': 'no qualifying 64-pixel boundary'}
    if candidate == old_74:
        return {'refresh': False, 'reason': 'already visited $74 boundary'}
    return {'refresh': True, 'edge': edge, 'new_74': candidate,
            'entry': '$80D1', 'slot_load': '$8106'}


def smoke() -> None:
    # Artificial bank: no retail ROM data. Exercises the same source ABI.
    b = bytearray(BANK_BYTES)
    def putword(addr: int, val: int) -> None:
        b[addr-CPU_BASE:addr-CPU_BASE+2] = val.to_bytes(2, 'little')
    putword(0x92AE, 0x92CC)
    putword(0x92CE, 0x9322)
    putword(0x9322, SOURCE_ROOT)
    b[SOURCE_ROOT-CPU_BASE+6] = 0x81
    b[SOURCE_ROOT-CPU_BASE+8] = 0x82
    for i in range(6):
        b[SLOT_PHASE-CPU_BASE+i] = i
        b[0x8451-CPU_BASE+i] = 1 << i
    for sid, addr, row in ((0x81, 0xA3A9, 0x22), (0x82, 0xA3AE, 0x23)):
        putword(HIGH_POINTERS + ((sid << 1) & 255), addr)
        b[addr-CPU_BASE:addr-CPU_BASE+5] = bytes((row, 0x28, 0x60, 0, 0))
        putword(EVENT_ROWS + row*2, 0x8B26)
    putword(0x8B26, 0x8B2C)
    b[SOURCE_ROOT-CPU_BASE+3] = 0x01
    putword(AUX_LOW_POINTERS + 2, 0xA890)
    b[0xA890-CPU_BASE:0xA894-CPU_BASE] = bytes((0x80, 1, 0x20, 0x48))
    b[AUX_SCRIPTS-CPU_BASE] = 0x31
    slots = stage1_cells(bytes(b))
    require([(x['source_slot'], x['event_row']) for x in slots if x['active']] ==
            [(3, 0x22), (4, 0x23)], 'artificial slot lookup failed')
    require(slots[1]['auxiliary_enabled'] and
            slots[1]['auxiliary_type'] == 0x80, 'auxiliary source not installed')
    require(not stage1_cells(bytes(b), mask_f0=0x02)[1]['auxiliary_enabled'],
            '$8440 mask did not prevent auxiliary install')
    require(refresh_gate(0x3F, 0x3F, 3)['new_74'] == 0x40,
            'forward 64-pixel boundary failed')
    require(refresh_gate(0x41, 0x41, 2)['new_74'] == 0x40,
            'backward boundary failed')
    require(not refresh_gate(0x40, 0x40, 1)['refresh'], 'duplicate refresh accepted')
    require(not refresh_gate(0x3F, 0, 255)['refresh'], 'negative delta bypass')
    print('PASS JP0664 synthetic six-slot catalog and conditional refresh gates')


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path)
    p.add_argument('--export-private', type=Path)
    p.add_argument('--flag-07f6', type=int, default=0)
    p.add_argument('--mask-f0', type=int, default=0)
    p.add_argument('--smoke', action='store_true')
    args = p.parse_args()
    if args.smoke:
        smoke()
    if args.rom:
        bank = original_bank(args.rom.read_bytes())
        slots = stage1_cells(bank, args.flag_07f6, args.mask_f0)
        active = [s for s in slots if s['active']]
        print('Original JP Stage 1-02: room $93E8, six slots,', len(active),
              'initial active event rows (conditional source state)')
        direct = [s for s in slots if s['auxiliary_enabled']]
        print('Original conditional auxiliary actors:', len(direct),
              'types', ','.join(f"{s['auxiliary_type']:02X}" for s in direct))
        for s in active:
            print(' slot', s['source_slot'], 'ID', f"{s['room_source_id']:02X}",
                  'record', s['source_cpu'], 'row', f"{s['event_row']:02X}",
                  'initial handler', s['initial_handler_cpu'])
        if args.export_private:
            payload = {'schema': 'JP-stage1-02-original-actor-cells/v1',
                       'original_rom_sha256': ROM_SHA, 'physical_prg': 'raw0A',
                       'stage_room_section': SOURCE_ROOM, 'root_cpu': '93E8',
                       'flag_07f6': args.flag_07f6,
                       'mask_f0': args.mask_f0, 'cells': slots,
                       'warning': 'Original source; private only. Not a spawn timeline or widescreen runtime.'}
            args.export_private.write_text(json.dumps(payload, indent=2)+'\n')
    elif not args.smoke:
        p.error('provide --rom or --smoke')


if __name__ == '__main__':
    main()
