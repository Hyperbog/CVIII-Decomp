#!/usr/bin/env python3
"""JP0672: private, non-mutating Mesen2 / native 2A03+VRC6 cycle-phase audit.

Input is read-only. The report contains aggregates/hashes, NEVER game-derived
register values, individual events or cycle timestamps. Identical address/value
ordering is required before interpreting timestamps. No clock rebasing is used
for strict parity. A +1-cycle phase probe is *diagnostic*, not certification.

Usage:
 python jp0672_audio_cycle_audit.py --mesen-log private/JP0671-Mesen-original-fixed.log \\
      --native-dir private/JP0668-Native-StderrFix-... --replay private/JP0668-window-input.txt \\
      --out private/JP0672-timing-report.json
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import re
from collections import Counter
from pathlib import Path

EXPECTED_REPLAY_SHA = '1ae01d6032847d2e37e151e09398c1f6f6765ed1915fe0623069d5d96d40ab3c'
M_CSV = ('cycle', 'chip', 'voice', 'register', 'value', 'previous', 'delta_cycles', 'rapid_rewrite')
W = re.compile(r'^JP0668_WRITE (\d+) (\d+) ([A-F0-9]{4}) ([A-F0-9]{2})$')
F = re.compile(r'^JP0668_FRAME (\d+) (\d+)$')
P = re.compile(r'^JP0668_POLL (\d+) (\d+) (\d+) ([A-F0-9]{2})$')
E = re.compile(r'^JP0668_END (\d+) (\d+) (\d+) (\d+)$')
ROUTE = re.compile(r'^JP0671_ROUTE frame=(\d+) cycle=(\d+) start=(\d+) p2=(\d+)$')
START = re.compile(r'^JP0671_CPU_START frame=(\d+) ordinal=(\d+) cycle=(\d+) bus=([A-F0-9]{2}) bit=(\d+)$')


def insist(test: bool, message: str) -> None:
    if not test: raise ValueError(message)


def valid_register(addr: int) -> bool:
    return 0x4000 <= addr <= 0x4013 or addr in (0x4015, 0x4017) or (
        0x9000 <= addr <= 0x9003 or 0xA000 <= addr <= 0xA002 or 0xB000 <= addr <= 0xB002)


def mask_at(frame: int) -> int:
    windows = {
        0x08: ((90,92),(180,182),(300,302),(530,531),(745,746)),
        0x80: ((370,520),(645,730),(830,1065)),
        0x01: ((460,469),(1010,1012)),
        0x02: ((470,475),(650,652),(870,872)),
    }
    return sum(bit for bit, spans in windows.items()
               if any(a <= frame <= b for a,b in spans))


def parse_original(log: str, *, full: bool=True) -> tuple[list[tuple[int,int,int]], dict]:
    events: list[tuple[int,int,int]] = []
    frames = polls = started = 0
    last_cycle = -1
    ready = begin = end = False
    gate = route = 0
    witnesses = 0
    for raw in log.splitlines():
        pos = raw.find('JP0668_')
        if pos < 0: pos = raw.find('JP0671_')
        if pos < 0: continue
        line = raw[pos:]
        if line == 'JP0668_READY v2':
            insist(not ready and not begin, 'duplicated/late ready'); ready=True; continue
        if line.startswith('JP0668_BEGIN '):
            insist(ready and not begin and int(line.split()[-1]) >= 0, 'bad begin');begin=True;continue
        if line.startswith(('JP0668_INVALID','JP0668_TRUNCATED','JP0671_INVALID')):
            raise ValueError('invalid or truncated Mesen observer')
        if line.startswith('JP0671_GATE '):
            insist(line=='JP0671_GATE route_checks=1099 start_read_hits=2 start_read_samples=2',
                   'input gate incomplete or failed')
            gate += 1
            continue
        m=ROUTE.fullmatch(line)
        if m:
            insist(begin and not end, 'route outside session')
            frame,cycle,start,p2=map(int,m.groups())
            insist(frame==90 and start==1 and p2==0 and cycle>=last_cycle, 'bad first-start pad route')
            route += 1;continue
        m=START.fullmatch(line)
        if m:
            frame,ordinal,cycle,bus,bit=m.groups()
            insist(begin and not end and int(frame)==90 and int(ordinal) in (4,12)
                   and int(bus,16)&1==1 and int(bit)==1 and int(cycle)>=last_cycle,
                   'CPU Start witness invalid')
            witnesses += 1;continue
        m=W.fullmatch(line)
        if m:
            n,cyc,reg,val = m.groups(); cyc=int(cyc); reg=int(reg,16);val=int(val,16)
            insist(begin and not end and int(n)==len(events)+1 and cyc>=last_cycle
                   and valid_register(reg),'bad Mesen write event')
            events.append((cyc,reg,val));last_cycle=cyc;continue
        m=F.fullmatch(line)
        if m:
            n,cyc=map(int,m.groups())
            insist(begin and not end and n==frames+1 and cyc>=last_cycle,'bad Mesen frame')
            frames=n;last_cycle=cyc;continue
        m=P.fullmatch(line)
        if m:
            n,fr,cyc,mask=m.groups();cyc=int(cyc);fr=int(fr)
            insist(begin and not end and int(n)==polls+1 and fr==frames+1 and
                   int(mask,16)==mask_at(fr) and cyc>=last_cycle,'bad Mesen poll, cycle or input mask')
            polls+=1;last_cycle=cyc;continue
        m=E.fullmatch(line)
        if m:
            f,w,p,cyc=map(int,m.groups())
            insist(begin and not end and (f,w,p)==(frames,len(events),polls)
                   and cyc>=last_cycle,'Mesen END counts or cycle incorrect')
            end=True;continue
        if line.startswith('JP0671_'):
            # Other observer provenance lines are allowed, but cannot claim an invalid or failed gate.
            insist('FAIL' not in line, 'JP0671 provenance failure')
            continue
        raise ValueError('unrecognized Mesen protocol record')
    insist(ready and begin and end and len(events)>0,'incomplete original trace')
    if full:
        insist(frames==1100 and polls==1099,'original must complete 1100 frames and 1099 observed polls')
        insist(route==1 and witnesses==2 and gate>=1,'missing independent CPU Start/input-route gate')
    return events, dict(frames=frames,polls=polls,route_records=route,
                        start_witnesses=witnesses,input_gate_records=gate)


def parse_native(raw: str) -> list[tuple[int,int,int]]:
    reader=csv.DictReader(io.StringIO(raw))
    insist(tuple(reader.fieldnames or ())==M_CSV,'unexpected native CSV columns')
    results=[]; last=-1
    for row in reader:
        insist(None not in row and all(v is not None for v in row.values()),'invalid native CSV row')
        try:
            cyc=int(row['cycle']); reg=int(row['register'],16);val=int(row['value'],16)
            old=int(row['previous'],16);delta=int(row['delta_cycles']);rapid=int(row['rapid_rewrite'])
        except (TypeError,ValueError) as e:raise ValueError('invalid native CSV numeric field') from e
        insist(cyc>=0 and cyc>=last and valid_register(reg) and 0<=val<256 and 0<=old<256
               and delta>=0 and rapid in (0,1),'native event out of domain')
        insist(row['chip']==('2a03' if reg<0x9000 else 'vrc6'), 'native chip classification invalid')
        results.append((cyc,reg,val));last=cyc
    insist(len(results)>0,'empty native trace')
    return results


def verify_session(native_dir: Path) -> dict:
    manifest=json.loads((native_dir/'CVIII-Audio-Session.json').read_text(encoding='utf-8-sig'))
    insist(manifest['schema']=='CVIII-JP-audio-session/v1','wrong native session schema')
    for key,name in [('registers','CVIII-Audio-Registers.csv'),('requests','CVIII-Sound-Requests.csv'),('epochs','CVIII-Audio-Epochs.csv')]:
        entry=manifest['files'][key]
        insist(entry['name']==name and entry['sha256']==hashlib.sha256((native_dir/name).read_bytes()).hexdigest(),
               'native session integrity check failed')
    with (native_dir/'CVIII-Audio-Epochs.csv').open(encoding='utf-8-sig',newline='') as f:
        rows=list(csv.DictReader(f))
    insist(len(rows)==1 and rows[0]['epoch']=='0' and rows[0]['event']=='power_on'
           and rows[0]['session_id']==manifest['session_id'] and rows[0]['register_rows']=='0'
           and rows[0]['request_rows']=='0','not a single native power-on epoch')
    return dict(native_session_manifest_sha256=hashlib.sha256(
        (native_dir/'CVIII-Audio-Session.json').read_bytes()).hexdigest(),
        native_epoch_verified=True)


def audit(original: list[tuple[int,int,int]], native: list[tuple[int,int,int]]) -> dict:
    """Raises on different address/value stream. Never outputs raw events."""
    insist(len(original)==len(native) and len(original)>1,'audio event count unequal')
    for i,(m,n) in enumerate(zip(original,native),1):
        insist(m[1:]==n[1:],f'address/value mismatch at event {i}; cannot analyze cycle phase')
    shifts=[n[0]-m[0] for m,n in zip(original,native)]
    jump=[shifts[i]-shifts[i-1] for i in range(1,len(shifts))]
    original_intervals=[original[i][0]-original[i-1][0] for i in range(1,len(original))]
    first_dpcm_index=next((i+1 for i,(_c,a,_v) in enumerate(original) if 0x4010<=a<=0x4013),None)
    deltas_before_dpcm=shifts[:first_dpcm_index-1] if first_dpcm_index else shifts
    at_most_10=[j for j,g in zip(jump,original_intervals) if g<=10]
    at_most_100=[j for j,g in zip(jump,original_intervals) if g<=100]
    exact=sum(d==0 for d in shifts)
    return {
        'schema':'JP0672-audio-cycle-phase-audit/v1',
        'ordered_audio_register_and_value_match':True,
        'matched_write_count':len(shifts),
        'strict_unadjusted_cycle_timestamp_parity':exact==len(shifts),
        'strict_exact_cycle_count':exact,
        'native_minus_mesen_cycle_offset_min':min(shifts),
        'native_minus_mesen_cycle_offset_max':max(shifts),
        'native_minus_mesen_offset_histogram':{str(k):v for k,v in sorted(Counter(shifts).items())},
        'adjacent_native_and_mesen_write_intervals_exact':sum(j==0 for j in jump),
        'total_adjacent_intervals':len(jump),
        'intervals_with_mesen_gap_le_10':len(at_most_10),
        'those_intervals_with_equal_native_gap':sum(j==0 for j in at_most_10),
        'intervals_with_mesen_gap_le_100':len(at_most_100),
        'those_intervals_with_equal_native_gap':sum(j==0 for j in at_most_100),
        'first_dpcm_descriptor_write_ordinal':first_dpcm_index,
        'offset_min_before_first_dpcm_descriptor':min(deltas_before_dpcm),
        'offset_max_before_first_dpcm_descriptor':max(deltas_before_dpcm),
        # Mesen StartCpuCycle increments before the write; native hw_cycle_finish after.
        # This diagnostic +1 is NOT used in strict pass/fail logic above.
        'hypothetical_native_plus_one_phase_exact_count_UNCERTIFIED':sum(x==-1 for x in shifts),
        'hypothetical_phase_probe_applied_to_verdict':False,
        'cycle_phase_equivalence_proven':False,
        'cycle_exact_parity_certified':exact==len(shifts) and False,
        'pcm_parity_certified':False,
        'interpretation':'Counter phase accounts for an initial -1 sample, not all variable offsets; additional CPU/PPU/interrupt/DMA timing requires independent evidence.',
    }


def inspect(mesen_path: Path,native_dir: Path,replay_path: Path|None=None) -> dict:
    original_raw=mesen_path.read_bytes()
    native_path=native_dir/'CVIII-Audio-Registers.csv'
    native_raw=native_path.read_bytes()
    original,stats=parse_original(original_raw.decode('utf-8-sig'))
    native=parse_native(native_raw.decode('utf-8-sig'))
    provenance=verify_session(native_dir)
    if replay_path:
        b=replay_path.read_bytes()
        insist(len(b)>0,'empty replay')
        # This particular sealed JP0668/JP0671 test uses an immutable 1100-frame replay.
        # The source-side Mesen poll schedule has been checked independently above.
        replay_hash=hashlib.sha256(b).hexdigest()
        insist(replay_hash==EXPECTED_REPLAY_SHA,'native replay hash differs from owner-validated schedule')
    else:replay_hash=None
    result=audit(original,native)
    result.update(original_capture_sha256=hashlib.sha256(original_raw).hexdigest(),
                  native_register_csv_sha256=hashlib.sha256(native_raw).hexdigest(),
                  original_trace_frame_count=stats['frames'], original_input_polls=stats['polls'],
                  original_start_cpu_witnesses=stats['start_witnesses'],
                  replay_sha256=replay_hash,**provenance)
    return result


def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--mesen-log',type=Path,required=True)
    ap.add_argument('--native-dir',type=Path,required=True)
    ap.add_argument('--replay',type=Path)
    ap.add_argument('--out',type=Path)
    a=ap.parse_args()
    data=inspect(a.mesen_log,a.native_dir,a.replay)
    result=json.dumps(data,indent=2,sort_keys=True)+'\n'
    if a.out:a.out.write_text(result,encoding='utf-8')
    print(result,end='')

if __name__=='__main__':main()