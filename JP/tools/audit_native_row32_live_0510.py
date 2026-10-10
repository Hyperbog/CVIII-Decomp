#!/usr/bin/env python3
"""Compare a *native lifted C++ event* with independent Mesen2 original-JP RAM.

Uses a naturally reached (never edited) frame-3092 $84F3 savestate. Starts
from the *same* state for all four Mesen --step reads; no 6502 emulator is
used by the native program. Original emulator RAM snapshots are kept private.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

ROM_SHA = '958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
AGENT_SHA = '95bcda9d4ff6428937183093386d993649c2d740273871ced78217d3d8f234d0'
CORE_SHA = 'd2831c26d42aba675ed5d2cf392b2e12a67cb25274d981ef2c7741e552b72040'
# Authenticated original PRG raw physical bank $0A and bank $0B data.
BLOCKS = (
    (10, 0x8501, 0x8523, 'ad5600da3247b263c60371b9cca117cbcb2b77d37087b7de0318b6de525e26d3'),
    (10, 0x8B2C, 0x8B74, 'a50e778b1ff8816b70a6491f2397cd5bc85b92cffd40d4aee7afda1a5bbfebf5'),
    (10, 0x8D5E, 0x8D91, '689675814b8ed0ac154e83095176c1653e4c323302394a56bfede55aa900fb21'),
    (10, 0x8DC1, 0x8DE7, '8e5a6a5190286f99eb83eabb2df3a467b8707363ded3df65fd0337ef30f13058'),
    (10, 0x9194, 0x9244, 'a6348bc8c2c60c4c72b748b8dbfe610007e4f04867840db41fcc6d0c3cd47ae8'),
    (10, 0x9244, 0x9290, '927b91d6474c8814e2e4e54c6b622bf64d10e7674f9b30524286c4d8b6685f61'),
    (11, 0xA00F, 0xA060, '62b34daf7a29c73fa776ca5531a4bb0c47b1b962851687ed3b50b56786a32c3d'),
)

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def verify_rom(rom: Path) -> None:
    source = rom.read_bytes()
    if sha(source) != ROM_SHA or len(source) != 393232:
        raise ValueError('Unexpected Japanese ROM identity')
    prg = source[16:16 + 262144]
    for bank, begin, end, expected in BLOCKS:
        blob = prg[bank * 16384 + begin - 0x8000:
                   bank * 16384 + end - 0x8000]
        if sha(blob) != expected:
            raise ValueError(f'Original physical source drift bank ${bank:02X}:${begin:04X}')
    root=prg[10*16384:11*16384]
    for addr, pair in ((0x8587, bytes.fromhex("26 8b")), (0x8B26, bytes.fromhex("2c 8b"))):
        if root[addr-0x8000:addr-0x8000+2] != pair:
            raise ValueError(f"Original row32 dispatcher pointer changed: {addr:04X}")
    for bank, addr, value in ((10, 0x91C6, 0x13), (10, 0x921E, 0x3D),
                              (10, 0x928B, 0x01), (11, 0xA032, 0x20),
                              (11, 0xA052, 0x20)):
        if prg[bank * 16384 + addr - 0x8000] != value:
            raise ValueError(f'Original indexed data drift: {bank:02X}:{addr:04X}')

def run_probe(rom, mesen, state, native, destination, step):
    cmd = [str(mesen), str(rom), '--home',str(destination / f'home-{step}'),
           '--load-state', str(state), '--frames', '0', '--step', str(step),
           '--timeout', '30', '--pc', '--dump-memory',
           f'NesInternalRam={destination}/ram-{step}.bin', '--state-json',
           str(destination / f'state-{step}.json')]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
    logs = [json.loads(x) for x in p.stdout.splitlines() if x.startswith('{')]
    s = [x for x in logs if x.get('event') == 'summary']
    if p.returncode or len(s) != 1 or not s[0].get('ok'):
        raise AssertionError(f'Mesen step {step} failed: {p.stderr[-500:]} {s}')
    if s[0]['final_frame'] != 3092:
        raise AssertionError('Expected naturally reached original frame 3092')
    cpu = json.loads((destination / f'state-{step}.json').read_text())
    ram = (destination / f'ram-{step}.bin').read_bytes()
    if len(ram) != 2048:
        raise AssertionError('Mesen returned incorrect physical internal RAM size')
    return ram, cpu

def natural_original_breakpoint(rom, mesen, root):
    """Recreate original frame-3092 $84F3 live breakpoint from unmodified ROM.

    The only external inputs are controller button schedules; the save state
    is recorded after CPU/PPU/mapper originally reached the event naturally.
    """
    def phase(name, opts, frame, reason):
        cmd=[str(mesen),str(rom),'--home',str(root/f'boot-{name}')]+opts
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=145)
        events=[json.loads(line) for line in p.stdout.splitlines() if line.startswith('{')]
        summaries=[x for x in events if x.get('event')=='summary']
        if (p.returncode or len(summaries)!=1 or
            not summaries[0].get('ok') or
            summaries[0].get('final_frame')!=frame or
            summaries[0].get('reason')!=reason):
            raise AssertionError(f'Original boot {name} changed: {p.stderr[-600:]} {summaries}')
        return summaries[0]
    first=root/'start1503.mss';stage=root/'stage2603.mss';hit=root/'natural3092.mss'
    p0=['--frames','1502','--timeout','110']
    for f in (50,170,270,370):p0+=['--input',f'0:start@{f}-{f+4}']
    p0+=['--input','0:right@780-1501','--input','0:a@820-1501',
         '--save-state',str(first)]
    phase('start',p0,1503,'frame_limit')
    p1=['--load-state',str(first),'--frames','1100','--timeout','110',
        '--input','0:right@0-1099','--input','0:a@0-1099',
        '--save-state',str(stage)]
    phase('stage',p1,2603,'frame_limit')
    p2=['--load-state',str(stage),'--frames','1200','--timeout','110',
        '--breakpoint','NesMemory:0x84F3:x:[$23]==$0A',
        '--input','0:right@0-1199']
    for f in range(0,1200,43):
        if f+4<1200:p2+=['--input',f'0:a@{f+4}-{min(f+9,1199)}']
    for f in range(0,1200,107):
        if f+34<1200:p2+=['--input',f'0:up@{f+34}-{min(f+65,1199)}']
    p2+=['--save-state',str(hit)]
    phase('actor',p2,3092,'debugger_break')
    return hit

def audit(rom, mesen, state, native):
    verify_rom(rom)
    if sha(mesen.read_bytes()) != AGENT_SHA or sha((mesen.parent / 'MesenCore.so').read_bytes()) != CORE_SHA:
        raise ValueError('Mesen 2.1.1 source version changed')
    if not state.is_file():
        raise ValueError('Requires private original, untouched frame-3092 breakpoint state')
    rows = []
    with tempfile.TemporaryDirectory(prefix='jp0510_native_row32_') as d:
        tmp = Path(d)
        for start, stop, slot, source in ((0, 189, 1, 3), (213, 407, 2, 4)):
            original, before = run_probe(rom, mesen, state, native, tmp, start)
            expected, after = run_probe(rom, mesen, state, native, tmp, stop)
            if not (before['cpu.pc'] == 0x8501 and after['cpu.pc'] == 0x84F6 and
                    original[0x69] == source and original[0x07c2 + source] == 0x32 and
                    original[0x07c8 + source] == 0 and original[0x07e0 + source] == 0 and
                    expected[0x054e + slot] == 0x3D and
                    expected[0x07c8 + source] == (slot << 4) + 1):
                raise AssertionError(f'Original Mesen row32 real caller changed: {start}->{stop}')
            cmd = [str(native), str(tmp / f'ram-{start}.bin'), str(tmp / f'ram-{stop}.bin')]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if result.returncode or '1792/1792 non-stack bytes' not in result.stdout:
                raise AssertionError(f'Native != source original at event {source}: {result.stdout} {result.stderr}')
            rows.append({
                'source_object_x': source, 'actor_slot_x': slot,
                'begin_pc': '8501', 'end_pc': '84F6',
                'mesen_source_steps_parameter': start,
                'mesen_end_steps_parameter': stop,
                'cpu_original_instructions': stop - start,
                'ram_bytes_compared_excluding_stack': 1792,
                'before_non_stack_sha256': sha(original[:256] + original[512:]),
                'after_non_stack_sha256': sha(expected[:256] + expected[512:]),
                'mesen_original_final_cycle': after['cpu.cycleCount'],
                'native_vs_mesen': 'exact_all_non_stack_ram_bytes',
            })
    return {
        'schema': 'JP-0510-row32-native-lift-independent-mesen-ram-v1',
        'rom_sha256': ROM_SHA, 'mesen_agent_sha256': AGENT_SHA,
        'mesen_core_sha256': CORE_SHA,
        'original_source_frame': 3092, 'source_bank': '0A',
        'independent_live_events': rows,
        'verified_non_stack_ram_bytes': 1792 * len(rows),
        'stack_comparison': 'excluded: native structured code does not emulate JSR/RTS pushes',
        'missing_evidence': 'native full frame, all-event entry domains, renderer/audio, game continuation',
        'new_strict_prg_bytes': 0, 'new_vpp_points': 0,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('rom',type=Path)
    p.add_argument('--mesen',type=Path,required=True)
    p.add_argument('--natural-state',type=Path,help='Optional independent original frame-3092 savestate; otherwise cold boot ROM')
    p.add_argument('--native-replay',type=Path,required=True)
    p.add_argument('--report',type=Path)
    args=p.parse_args()
    with tempfile.TemporaryDirectory(prefix='jp0510_original_natural_boot_') as d:
        natural=(args.natural_state.resolve() if args.natural_state else
                 natural_original_breakpoint(args.rom.resolve(),args.mesen.resolve(),Path(d)))
        report=audit(args.rom.resolve(),args.mesen.resolve(),natural,args.native_replay.resolve())
    if args.report:args.report.write_text(json.dumps(report,indent=2)+'\n')
    print('PASS independent Mesen RAM = original source lifted native C++:',
          report['verified_non_stack_ram_bytes'],'bytes across 2 naturally spawned actors')

if __name__=='__main__':main()
