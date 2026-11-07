#!/usr/bin/env python3
"""JP0667 fail-closed original-Mesen vs native 2A03/VRC6 CPU writes.

No trace input -> NO PARITY CLAIM. Mesen original games must use the same JP
ROM, synchronized power-on epoch, controller inputs, NTSC and no savestates.
Tests deliberately use ONLY synthetic events; their pass is not a real trace.
Never commit private live register logs, especially DPCM effects traces.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import re
from pathlib import Path
ROM_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
COLUMNS=['cycle','chip','voice','register','value','previous','delta_cycles','rapid_rewrite']
WRITE=re.compile(r'^JP0667_WRITE ([1-9][0-9]*) ([0-9]+) ([0-9A-F]{4}) ([0-9A-F]{2})$')
ALLOWED=set(range(0x4000,0x4014))|{0x4015,0x4017}|set(range(0x9000,0x9004))|set(range(0xa000,0xa003))|set(range(0xb000,0xb003))
LIMIT=200000
MAX_CYCLE=(1<<53)-1

def validate_event(cycle,addr,value):
    if not(0<=cycle<=MAX_CYCLE and addr in ALLOWED and 0<=value<=255):
        raise ValueError('event out of supported CPU/write domain')

def parse_mesen(source):
    events=[]; boundaries=[]; next_id=1;last=-1
    for line in source.splitlines():
        # Mesen emu.log can supply a prefix; anchored mode allows only the
        # log-protocol payload (user should extract these lines verbatim).
        if line.startswith('JP0667_BOUNDARY '):
            name=line.removeprefix('JP0667_BOUNDARY ')
            if name not in ('reset','state_loaded'):raise ValueError('bad boundary')
            boundaries.append((name,len(events)))
            continue
        if line.startswith(('JP0667_TRUNCATED','JP0667_INVALID')):
            raise ValueError('Mesen log truncated or error')
        m=WRITE.fullmatch(line)
        if m is None:
            raise ValueError('unknown or malformed Mesen log event')
        seq,cycle,addr,value=int(m[1]),int(m[2]),int(m[3],16),int(m[4],16)
        validate_event(cycle,addr,value)
        if seq!=next_id or cycle<last:raise ValueError('Mesen event order/cycle regression')
        next_id+=1;last=cycle;events.append((cycle,addr,value))
        if len(events)>LIMIT:raise ValueError('Mesen events over hard cap')
    if not events or not boundaries or boundaries!=[('reset',0)]:
        raise ValueError('required one reset before events, no mid-session save/load')
    return events

def parse_native(source):
    reader=csv.DictReader(io.StringIO(source))
    if reader.fieldnames!=COLUMNS:
        raise ValueError('unexpected pinned JP0610 native register CSV format')
    events=[];last=-1
    for row in reader:
        if not row or None in row or any(v is None for v in row.values()):
            raise ValueError('malformed native CSV row')
        try:
            cycle=int(row['cycle'])
            addr=int(row['register'],16)
            value=int(row['value'],16)
            previous=int(row['previous'],16)
            delta=int(row['delta_cycles'])
            rapid=int(row['rapid_rewrite'])
        except(ValueError,TypeError) as exc:
            raise ValueError('malformed numeric native CSV') from exc
        validate_event(cycle,addr,value)
        if cycle<last or not 0<=previous<=255 or not 0<=delta<=MAX_CYCLE or rapid not in (0,1):
            raise ValueError('invalid native metadata/cycle order')
        # chip/voice is informational; reject incompatible host classifier.
        if row['chip'] not in ('2a03','vrc6') or not row['voice']:
            raise ValueError('invalid native chip/channel metadata')
        if addr<0x9000 and row['chip']!='2a03' or addr>=0x9000 and row['chip']!='vrc6':
            raise ValueError('native chip/address inconsistency')
        events.append((cycle,addr,value));last=cycle
        if len(events)>LIMIT:raise ValueError('native event cap exceeded')
    if not events:raise ValueError('native trace has no events')
    return events

def compare(mesen,native):
    a=parse_mesen(mesen);b=parse_native(native)
    # Exact CPU-cycle parity: no per-channel offset, no dropping unmatched
    # writes, no faking SFX silences or aligning by note index.
    if len(a)!=len(b):
        raise ValueError(f'original/native write count mismatch {len(a)} != {len(b)}')
    for i,(original,recomp) in enumerate(zip(a,b)):
        if original!=recomp:
            raise ValueError(f'original/native register or CPU cycle mismatch at event index {i}')
    return {'schema':'jp0667-register-cycle-align/v1',
            'comparison':'full_order_exact_absolute_cpu_cycle_addr_value',
            'events_compared':len(a),
            'matching_events':len(a),
            'mismatches':0,
            'note':'Conditional comparison only; original ROM, matched controller inputs, core callback clock origin and emulator identity must be independently established.',
            'full_envelope_verified':False,
            'independent_music_sfx_audio_verified':False}

def fake_native(events):
    out=io.StringIO();w=csv.writer(out,lineterminator='\n');w.writerow(COLUMNS)
    for cyc,addr,value in events:
        w.writerow((cyc,'vrc6' if addr>=0x9000 else '2a03',
                    'pulse1',f'{addr:04X}',f'{value:02X}','00',0,0))
    return out.getvalue()

def smoke():
    mesen='\n'.join(('JP0667_BOUNDARY reset','JP0667_WRITE 1 100 4000 30',
           'JP0667_WRITE 2 110 9001 40','JP0667_WRITE 3 115 4015 1F'))
    native=fake_native([(100,0x4000,0x30),(110,0x9001,0x40),(115,0x4015,0x1f)])
    assert compare(mesen,native)['events_compared']==3
    bad=[('cycle wrong',mesen,native.replace('110,vrc6','111,vrc6')),
         ('order wrong',mesen.replace('WRITE 2','WRITE 4'),native),
         ('value wrong',mesen,native.replace('9001,40','9001,41')),
         ('address wrong',mesen,native.replace('9001,40','9002,40')),
         ('truncated',mesen+'\nJP0667_TRUNCATED',native),
         ('savestate',mesen+'\nJP0667_BOUNDARY state_loaded',native),
         ('missing epoch',mesen.replace('JP0667_BOUNDARY reset\n',''),native),
         ('no original', '',native),
         ('no native',mesen,'')]
    for name,m,n in bad:
        try:compare(m,n)
        except ValueError:continue
        raise AssertionError('incorrectly certified synthetic '+name)
    print('PASS JP0667 3 invented exact events and',len(bad),'negative parity gates; live parity NOT EXERCISED')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--smoke',action='store_true')
    p.add_argument('--original-rom',type=Path)
    p.add_argument('--mesen-log',type=Path)
    p.add_argument('--native-csv',type=Path)
    p.add_argument('--matched-inputs-and-clock',action='store_true',
                   help='explicit private owner attestation; cannot be inferred from logs')
    p.add_argument('--json',type=Path,help='write aggregate verdict; no trace events')
    a=p.parse_args()
    if a.smoke:smoke()
    items=(a.original_rom,a.mesen_log,a.native_csv)
    if any(x is not None for x in items):
        if not all(x is not None for x in items) or not a.matched_inputs_and_clock:
            p.error('real comparison needs original JP ROM, BOTH traces, and explicit matched-inputs-and-clock attestation')
        rom=a.original_rom.read_bytes()
        if len(rom)!=393232 or hashlib.sha256(rom).hexdigest()!=ROM_SHA:
            raise ValueError('wrong Japanese original ROM')
        report=compare(a.mesen_log.read_text(),a.native_csv.read_text())
        report['authenticated_original_rom_sha256']=ROM_SHA
        report['matched_inputs_and_clock_owner_attested']=True
        if a.json:a.json.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
        print('PASS JP0667 conditional exact CPU register-event sequence,',report['events_compared'],'events; emulator authenticity separately attested')
    elif not a.smoke:p.error('provide --smoke or authenticated original ROM plus both traces')
if __name__=='__main__':main()
