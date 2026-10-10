#!/usr/bin/env python3
"""Source-stepped actor allocation precheck at raw $0A:$90C5.

Executes authentic ROM instructions with synthetic initial RAM, using the
previous 0509 bounded CPU and the original $8CDD conditional tail-jump into
fixed $FF06. Conditional source semantics only: NOT original frame liveness.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from audit_actor_spawn_0509 import ActorSpawnCpu, RAW_BANK, FREE_EXIT, FULL_EXIT
from audit_actor_cpu_abi_0509 import authenticated_prg

PRECHECK_ENTRY = 0x90C5
PRECHECK_SHA = 'c1cd8387e6e6a0d5b7b460de3b869f77a2df3f3e15debfca42152acb85a65b06'
CALLER_SHA = 'c4d9c294a87d2b82fb2efb9e47a394029126a5873d29aa87d20ccce5e95b176c'
TABLE_SHA = 'a0f96ee2ce69a443b2f4d418e753150f57c2dfa574137305abccae3b78d717b6'


def audit(prg: bytes) -> dict:
    raw = prg[RAW_BANK * 0x4000:(RAW_BANK + 1) * 0x4000]

    def hashblock(start: int, end: int, expected: str) -> None:
        got = hashlib.sha256(raw[start - 0x8000:end - 0x8000]).hexdigest()
        if got != expected:
            raise ValueError(f'Physical raw $0A ${start:04X} block SHA mismatch')

    # Hash the full original $8CDD->$FF06 conditional scanner gate, the caller
    # JSR/BNE, and the four-entry structural pointer slice. Unlike pattern scans,
    # this step never treats adjacent pointer bytes as instruction opcodes.
    hashblock(0x8CDD, 0x8CEA, PRECHECK_SHA)
    hashblock(0x90C5, 0x90CA, CALLER_SHA)
    hashblock(0x90BC, 0x90C4, TABLE_SHA)
    pointers = tuple(raw[p - 0x8000] | (raw[p + 1 - 0x8000] << 8)
                     for p in (0x90BD, 0x90BF, 0x90C1, 0x90C3))
    if pointers != (0x90C5, 0x8E50, 0x90DF, 0x8E50):
        raise ValueError('Conditional actor dispatch pointer slice drift')

    result_hash = hashlib.sha256()
    counts = {'free_allocated': 0, 'all_full': 0,
              'state53_guard': 0, 'indexed_guard': 0}
    instruction_count = 0
    distinct_pcs: set[int] = set()
    # 4,096 occupancy masks x 3 mutually exclusive local precheck classes.
    for pattern in range(4096):
        first = next((i + 1 for i in range(12) if not pattern & (1 << i)), 13)
        for guard in range(3):
            # Deliberately vary incoming actor X to verify that the indexed
            # $07E0,X precheck consumes the original caller X, while $FF06
            # later overrides X with the first available actor slot.
            incoming_x = 1 + ((pattern * 7) % 12)
            ram = bytearray([0xA5]) * 0x800
            for i in range(12):
                ram[0x054F + i] = 0x81 if pattern & (1 << i) else 0
            ram[0x10] = 0x7F
            ram[0x53] = 1 if guard == 1 else 0
            ram[0x07E0 + incoming_x] = 1 if guard == 2 else 0
            before = bytes(ram)

            cpu = ActorSpawnCpu(prg, ram, start=PRECHECK_ENTRY, x=incoming_x)
            cpu.execute()

            active = guard == 0
            allocated = active and first < 13
            if allocated:
                category = 'free_allocated'
                expected_x, expected_pc, expected_a = first, FREE_EXIT, 0
                stores = [0x10, 0x054E + first, 0x05EF + first]
            elif active:
                category = 'all_full'
                expected_x, expected_pc, expected_a = 13, FULL_EXIT, 1
                stores = []
            elif guard == 1:
                category = 'state53_guard'
                expected_x, expected_pc, expected_a = incoming_x, FULL_EXIT, 1
                stores = []
            else:
                category = 'indexed_guard'
                expected_x, expected_pc, expected_a = incoming_x, FULL_EXIT, 1
                stores = []
            counts[category] += 1
            if (cpu.pc, cpu.x, cpu.a) != (expected_pc, expected_x, expected_a):
                raise ValueError(f'Unexpected source return/branch for {pattern:03X}, guard {guard}')
            if cpu.stores != stores or ram[0x10] != (0 if allocated else 0x7F):
                raise ValueError(f'Unexpected original actor write contract: {pattern:03X} guard {guard}')
            if allocated and (ram[0x054E + first] != 0x13 or
                              ram[0x05EF + first] != 0):
                raise ValueError('Active actor assignment differs from original instruction writes')
            # Assert no RAM mutation except byte-precise stores and the two
            # JSR/RTS stack frames; $01FC/$01FD are fixture return bytes.
            allowed = set(stores) | {0x1FA, 0x1FB, 0x1FC, 0x1FD}
            for k in range(0x800):
                if k not in allowed and ram[k] != before[k]:
                    raise ValueError(f'Unexpected source RAM mutation ${k:04X}')
            result_hash.update(bytes((guard, expected_pc & 255, expected_pc >> 8,
                                      cpu.x, cpu.a, cpu.p, cpu.sp, cpu.steps)))
            instruction_count += cpu.steps
            distinct_pcs.update(cpu.path)

    return {
        'schema': 'JP-0509-raw0A-actor-precheck-gated-source-execution/v1',
        'rom_sha256': '958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28',
        'raw_vrc6_bank': '0A', 'fixed_physical_prg_bank': 31,
        'entry_cpu': f'{PRECHECK_ENTRY:04X}', 'helper_cpu': '8CDD',
        'fixed_slot_scanner_cpu': 'FF06',
        'raw_8CDD_8CE9_sha256': PRECHECK_SHA,
        'raw_90C5_90C9_sha256': CALLER_SHA,
        'pointer_slice_90BC_90C3_sha256': TABLE_SHA,
        'pointer_slice_targets': [f'{x:04X}' for x in pointers],
        'occupancy_masks': 4096, 'precheck_classes': 3,
        'total_cases': 4096 * 3, 'cases_by_result': counts,
        'total_original_instructions_executed': instruction_count,
        'distinct_instruction_pcs': len(distinct_pcs),
        'outcome_sha256': result_hash.hexdigest(),
        'proof_limit': 'bounded ROM opcode execution with synthetic RAM; pointer table shape is structural only; actual gameplay callers and mapper lifetime open',
        'new_strict_prg_bytes': 0, 'new_vpp_points': 0,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('original_jp_rom', type=Path)
    ap.add_argument('--report', type=Path)
    args = ap.parse_args()
    report = audit(authenticated_prg(args.original_jp_rom))
    if args.report:
        args.report.write_text(json.dumps(report, indent=2) + '\n')
    print('PASS source-gated actor allocation:', report['total_cases'],
          'states,', report['total_original_instructions_executed'], 'instructions')


if __name__ == '__main__':
    main()
