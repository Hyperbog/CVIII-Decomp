#!/usr/bin/env python3
"""Independent Mesen2 live JP actor dispatch witness, no RAM/PC injection.

Requires the user-supplied original JP ROM and the external mesen-agent 2.1.1.
All savestates and debugger traces remain private temporary files; writes only
sanitized ROM fingerprints, CPU states, addresses, hashes and test outcomes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

ROM_SHA = '958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
TRACE_SHA = 'dce02d6ce15c65a4b2dbdeea880b3171206514eeb7d35bb9168fcff56db48d93'


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(mesen: Path, rom: Path, root: Path, tag: str, opts: list[str]):
    argv = [str(mesen), str(rom), '--home', str(root / ('home-' + tag))] + opts
    completed = subprocess.run(argv, capture_output=True, text=True, timeout=75)
    if completed.returncode:
        raise AssertionError(f'{tag} exit {completed.returncode}: {completed.stderr[-800:]}')
    events = [json.loads(line) for line in completed.stdout.splitlines() if line.startswith('{')]
    failures = [e for e in events if e.get('event') == 'error']
    summaries = [e for e in events if e.get('event') == 'summary']
    if failures or len(summaries) != 1 or not summaries[0].get('ok'):
        raise AssertionError(f'{tag} Mesen runtime error: {failures}, summary={summaries}')
    if any(e.get('event') == 'lua_log' and e.get('error_count') for e in events):
        raise AssertionError(f'{tag} Lua reported errors')
    return events, summaries[0]


def memory(events, start):
    for e in events:
        if e.get('event') == 'memory_read' and e.get('start') == start:
            return bytes.fromhex(e['hex'])
    raise AssertionError(f'No Mesen read for RAM ${start:04X}')


def audit(mesen: Path, rom: Path):
    if file_sha(rom) != ROM_SHA:
        raise ValueError('Only the authenticated original Japanese Mapper24 ROM is supported')
    with tempfile.TemporaryDirectory(prefix='jp0509_mesen_live_') as temporary:
        root = Path(temporary)
        # Normal reset-to-gameplay, controller-only. No savestate, RAM or PC edit.
        phase0 = ['--frames', '1502', '--timeout', '65']
        for frame in (50, 170, 270, 370):
            phase0 += ['--input', f'0:start@{frame}-{frame+4}']
        phase0 += ['--input', '0:right@780-1501', '--input', '0:a@820-1501',
                   '--save-state', str(root / 'phase0.mss')]
        boot, boot_summary = run(mesen, rom, root, 'boot', phase0)
        if (boot_summary['reason'], boot_summary['final_frame']) != ('frame_limit', 1503):
            raise AssertionError('Live initial gameplay frame anchor changed')

        phase1 = ['--load-state', str(root / 'phase0.mss'), '--frames', '1100',
                  '--timeout', '65', '--input', '0:right@0-1099', '--input', '0:a@0-1099',
                  '--save-state', str(root / 'phase1.mss')]
        joined, joined_summary = run(mesen, rom, root, 'stage1', phase1)
        if (joined_summary['reason'], joined_summary['final_frame']) != ('frame_limit', 2603):
            raise AssertionError('Live stage-frame anchor changed')

        phase2 = ['--load-state', str(root / 'phase1.mss'), '--frames', '1200',
                  '--timeout', '65', '--breakpoint', 'NesMemory:0x84F3:x:[$23]==$0A',
                  '--input', '0:right@0-1199']
        for frame in range(0, 1200, 43):
            if frame+4 < 1200:
                phase2 += ['--input', f'0:a@{frame+4}-{min(frame+9,1199)}']
        for frame in range(0, 1200, 107):
            if frame+34 < 1200:
                phase2 += ['--input', f'0:up@{frame+34}-{min(frame+65,1199)}']
        phase2 += ['--pc', '--read-memory', 'NesInternalRam:0x18:24',
                   '--read-memory', 'NesInternalRam:0x50:64',
                   '--read-memory', 'NesInternalRam:0x540:160',
                   '--read-memory', 'NesInternalRam:0x7C2:56',
                   '--state-json', str(root / 'hit.json'),
                   '--save-state', str(root / 'hit.mss')]
        hit, hit_summary = run(mesen, rom, root, 'break', phase2)
        if (hit_summary['reason'], hit_summary['final_frame'], hit_summary['frames_executed']) != ('debugger_break', 3092, 489):
            raise AssertionError(f'Original actor entry did not reproduce: {hit_summary}')
        cpu = json.loads((root / 'hit.json').read_text())
        expected_cpu = {'cpu.pc':0x84F3, 'cpu.a':0x32, 'cpu.x':3, 'cpu.y':2,
                        'cpu.ps':0, 'cpu.sp':0xF1, 'cpu.cycleCount':92059934}
        if {k:cpu[k] for k in expected_cpu} != expected_cpu:
            raise AssertionError('Independent breakpoint register/cycle witness drift')
        z=memory(hit, 0x18)
        m50=memory(hit, 0x50)
        slots=memory(hit, 0x540)
        events=memory(hit, 0x7C2)
        x=cpu['cpu.x']
        if not (z[0] == 4 and z[0x23-0x18] == 0x0A and
                m50[0x53-0x50] == 0 and events[x] == 0x32 and
                events[6+x] == 0 and events[0x1E+x] == 0 and
                slots[0x054f-0x540:0x054f-0x540+12] == bytes(12)):
            raise AssertionError('Live actor-event selector/guard/occupancy drift')

        # Original mapped source word table: CPU $8523+2*$32 -> $8B26 -> $8B2C.
        prg = rom.read_bytes()[16:16+262144]
        bank = prg[0x0A*16384:0x0B*16384]
        word=lambda pc: bank[pc-0x8000] | (bank[pc-0x8000+1]<<8)
        table=word(0x8523+2*0x32)
        target=word(table)
        if (table,target)!=(0x8B26,0x8B2C):
            raise AssertionError('Original mapped two-level handler target changed')

        step_options=['--load-state',str(root/'hit.mss'),'--frames','0','--step','600',
                      '--timeout','30','--trace',str(root/'step600.trace'),
                      '--read-memory','NesInternalRam:0x18:24',
                      '--read-memory','NesInternalRam:0x540:160',
                      '--read-memory','NesInternalRam:0x7C2:56',
                      '--state-json',str(root/'step600.json')]
        stepped, step_summary = run(mesen, rom, root, 'step600', step_options)
        trace=(root/'step600.trace').read_bytes()
        trace_lines=trace.decode().splitlines()
        if len(trace_lines)!=600 or file_sha(root/'step600.trace')!=TRACE_SHA:
            raise AssertionError('Original Mesen 600-instruction CPU trace drift')
        counts = {pc: sum(line.startswith(pc+' ') for line in trace_lines)
                  for pc in ('84F3','8501','8520','8B2C','FF06','FF24','84F8')}
        if any(n!=2 for n in counts.values()):
            raise AssertionError(f'Expected two natural object dispatches: {counts}')
        post=memory(stepped,0x540)
        event_after=memory(stepped,0x7C2)
        if (post[0x054f-0x540],post[0x0550-0x540]) != (0x3D,0x3D):
            raise AssertionError('Live newly created actor type differs')
        if (event_after[0x07CB-0x7C2],event_after[0x07CC-0x7C2])!=(0x11,0x21):
            raise AssertionError('Live source-object script/event progression differs')
        later_cpu=json.loads((root/'step600.json').read_text())
        if later_cpu['cpu.cycleCount']!=92062031:
            raise AssertionError('Original Mesen post-step cycle contract drift')
        return {
          'schema':'JP-0509-original-mesen2-live-actor-dispatch/v1',
          'proof_status':'independent_gameplay_reached_bank0A_actor_dispatch_and_type3D_creation',
          'rom_sha256':ROM_SHA,
          'mesen_agent_sha256':file_sha(mesen),
          'mesen_core_sha256':file_sha(mesen.parent/'MesenCore.so'),
          'mesen_version':'2.1.1',
          'execution':'original ROM reset, actual Mesen2 CPU/mapper/PPU, controller input only; no RAM, PC, or bank edits',
          'clean_boot_checkpoint_frame':1503,
          'source_prebreak_checkpoint_frame':2603,
          'live_hit_frame':hit_summary['final_frame'],
          'live_hit_cpu':{'pc':'84F3','a':'32','x':'03','y':'02','p':'00','sp':'F1','cycles':cpu['cpu.cycleCount']},
          'mapped_bank_ram23':'0A','first_level_ram18':'04',
          'original_source_object_index':x,
          'event_selector_ram07C2_x':'32','subindex_ram07C8_x':'00',
          'guard_ram53':'00','guard_ram07E0_x':'00',
          'actor_free_slots_at_hit':12,
          'source_table_root':f'{table:04X}','source_target':f'{target:04X}',
          'trace_original_6502_instructions':len(trace_lines),
          'trace_sha256':TRACE_SHA,
          'trace_opcode_occurrences':counts,
          'live_allocated_slots':[1,2],
          'live_allocated_actor_type':'3D',
          'live_object_event_final_ram07CB':'11',
          'live_object_event_final_ram07CC':'21',
          'post_step_cycles':later_cpu['cpu.cycleCount'],
          'limits':'tested live handler is 8B2C, NOT 90C5/90DF/9133; no global event/input domain, frame parity or new strict PRG credit',
          'strict_new_prg_bytes':0,'new_vpp':0,
          'private_artifacts_not_exported':['ROM','savestates','CDL','raw instruction trace']}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('rom',type=Path)
    p.add_argument('--mesen-agent',type=Path,required=True)
    p.add_argument('--report',type=Path)
    args=p.parse_args()
    result=audit(args.mesen_agent.resolve(),args.rom.resolve())
    if args.report:args.report.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS independent original Mesen2: natural bank-$0A actor dispatch frame',
          result['live_hit_frame'], '600 instructions, actors',result['live_allocated_slots'])

if __name__=='__main__':main()
