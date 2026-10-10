#!/usr/bin/env python3
"""Hash-only original-Mesen/CDLv2 Japanese Castlevania III reference witness.

Consumes local, independently emulated original JP-ROM runs and per-frame Lua
logs. Reports per-bank CODE/DATA flags and known-checkpoint overlaps; never
writes game ROM, save states, CDL masks, screenshots or CPU disassembly to Git.
Source execution => observed liveness, NOT automatically strict semantic credit.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
from typing import Iterable

PRG_SIZE=262144
CHR_SIZE=131072
ROM_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
MESEN_AGENT_SHA='95bcda9d4ff6428937183093386d993649c2d740273871ced78217d3d8f234d0'
MESEN_CORE_SHA='fa0e7af858dce0171f5857837f8cad92090078c354631ce74f8279185df97bd1'
MESEN_RELEASE_SHA='bff3c1d31a4b5ae5322b075330eccb3e78e96050d7a4e593c02804d8f1de7ae2'
CHECKPOINT_0501_REGIONS=((261604,262),(261974,36),(147457,335),(147794,17),
(148048,207),(148311,195),(148540,169),(149138,44),(149520,83),
(164817,63),(165098,57),(180225,74),(180403,360),(180819,62),
(180941,34),(181001,9),(181013,9),(182339,41),(188756,9),
(189129,6),(189225,61),(189350,6),(192774,538),(193315,113),
(193430,319),(193751,338),(194098,65),(194254,180),(194533,399),
(194950,186),(195856,87))
assert len(CHECKPOINT_0501_REGIONS)==31 and sum(n for _,n in CHECKPOINT_0501_REGIONS)==4364
STATE=re.compile(r'^STATE frame=(\d+) s=([\dA-F]{2}) ([\dA-F]{2}) ([\dA-F]{2}) ([\dA-F]{2}) ([\dA-F]{2}) ([\dA-F]{2})$')

def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()

def counts(mask:bytes)->dict:
    if len(mask)!=PRG_SIZE:raise ValueError('not one JP PRG mask')
    return {'code':sum(bool(f&1) for f in mask),
            'data':sum(bool(f&2) for f in mask),
            'either':sum(bool(f&3) for f in mask),
            'both':sum((f&3)==3 for f in mask)}

def known_overlap(mask:bytes)->dict:
    assert len(mask)==PRG_SIZE
    return {'regions':31,'certified_0501_bytes':4364,
            'code_0501_overlap':sum(bool(mask[o+i]&1) for o,n in CHECKPOINT_0501_REGIONS for i in range(n)),
            'data_0501_overlap':sum(bool(mask[o+i]&2) for o,n in CHECKPOINT_0501_REGIONS for i in range(n))}

def decode_cdl(data:bytes)->tuple[bytes,str]:
    if len(data)!=9+PRG_SIZE+CHR_SIZE or data[:5]!=b'CDLv2':
        raise ValueError('expected 9-byte Mesen2 CDLv2 header and exact 256 KiB PRG + 128 KiB CHR')
    return data[9:9+PRG_SIZE],data[5:9].hex()

def decode_log(text:str)->tuple[dict,list[dict]]:
    rows=[json.loads(s) for s in text.splitlines() if s.strip()]
    loaded=[r for r in rows if r.get('event')=='loaded'];summary=[r for r in rows if r.get('event')=='summary']
    if len(loaded)!=1 or len(summary)!=1 or not summary[0].get('ok') or summary[0].get('reason')!='frame_limit':
        raise ValueError('Mesen output did not finish exactly one successful bounded frame run')
    if loaded[0].get('mesen_version')!='2.1.1' or loaded[0].get('console')!='Nes':
        raise ValueError('Mesen emulator version or console mismatch')
    if not any(r.get('event')=='cdl_saved' for r in rows):raise ValueError('missing native Mesen CDL save event')
    if any(r.get('error_count',0)!=0 for r in rows if r.get('event')=='lua_log'):raise ValueError('Lua logger errors')
    st=[]
    for log in (r.get('text','') for r in rows if r.get('event')=='lua_log'):
        for line in log.splitlines():
            match=STATE.match(line)
            if match:
                f,*values=[int(v,16) if i>0 else int(v) for i,v in enumerate(match.groups())]
                st.append({'frame_in_segment':f,'18':values[0],'19':values[1],
                    '68':values[2],'2C':values[3], '07A0':values[4],'07A6':values[5]})
    summ=summary[0]
    if summ['final_frame']-summ['start_frame']!=summ['frames_executed'] or not st:
        raise ValueError('frame or state log inconsistent')
    return summ,st

def bank_rows(mask:bytes)->list[dict]:
    return [{'physical_PRG_bank':i,
             'observed_code_bytes':sum(bool(x&1) for x in mask[i*8192:(i+1)*8192]),
             'observed_data_bytes':sum(bool(x&2) for x in mask[i*8192:(i+1)*8192])}
            for i in range(32) if any(x&3 for x in mask[i*8192:(i+1)*8192])]

def build(rom:Path,emulator:Path,runs:list[tuple[str,Path,Path]],
          *,screenshot:Path|None=None)->dict:
    source=rom.read_bytes()
    if len(source)!=393232 or sha(source)!=ROM_SHA:raise ValueError('wrong JP original ROM')
    binary=emulator/'mesen-agent';core=emulator/'MesenCore.so'
    if sha(binary.read_bytes())!=MESEN_AGENT_SHA or sha(core.read_bytes())!=MESEN_CORE_SHA:
        raise ValueError('independent emulator binary not at expected published SHA')
    if not runs:raise ValueError('at least one real Mesen run required')
    mask=bytearray(PRG_SIZE);run_reports=[];last_final=None;crc=None
    for name,cdl,stdout in runs:
        source_mask,cdlcrc=decode_cdl(cdl.read_bytes())
        if crc is None:crc=cdlcrc
        if crc!=cdlcrc:raise ValueError('different ROM CRC in CDL files')
        summ,states=decode_log(stdout.read_text())
        if last_final is not None and summ['start_frame']!=last_final:
            raise ValueError('frame segments do not connect; must be replayed from matching state')
        last_final=summ['final_frame']
        for i,byte in enumerate(source_mask):mask[i]|=byte
        firstlevel=sorted({x['18'] for x in states if x['frame_in_segment']>=3})
        r={'segment':name,'frames_executed':summ['frames_executed'],
           'start_emulated_frame':summ['start_frame'],'final_emulated_frame':summ['final_frame'],
           'reference_lua_states':len(states),
           'firstlevel_RAM18_values_seen_at_sampled_frames':firstlevel,
           'firstlevel_transitions':[{**x,'absolute_frame':summ['start_frame']+x['frame_in_segment']-1}
                 for x in states if x['frame_in_segment']>=3 and x['18']!=0 and
                 (x['frame_in_segment']<15 or x['18'] in (0x0C,0x0D))][:35],
           'cdl_sha256':sha(cdl.read_bytes()), 'reference_stdout_sha256':sha(stdout.read_bytes()),
           'cdl_flags':counts(source_mask),'0501_overlap':known_overlap(source_mask)}
        run_reports.append(r)
    report={'status':'INDEPENDENT_MESEN2_ORIGINAL_JP_EXECUTION_NOT_AUTOMATIC_STRICT_COVERAGE',
            'original_JP_rom_sha256':ROM_SHA,
            'external_emulator':'Mesen2 v2.1.1 via mesen-agent v0.1.0, unmodified licensed upstream',
            'external_emulator_binary_sha256':MESEN_AGENT_SHA,
            'external_core_sha256':MESEN_CORE_SHA,
            'external_release_archive_sha256':MESEN_RELEASE_SHA,
            'emulator_provenance':'https://github.com/atonamy/mesen-agent/releases/tag/v0.1.0',
            'original_image_bytes_not_exported':True,
            'code_data_masks_not_exported':True,
            'savestates_not_exported':True,
            'segments':run_reports,
            'segments_are_contiguous_savestate_resumptions':len(runs)>1,
            'total_independently_emulated_frames':sum(x['frames_executed'] for x in run_reports),
            'cdl_header_type':'CDLv2','cdl_header_crc32_raw_be_in_hex':crc,
            'physical_PRG_union':counts(mask),
            'code_mask_sha256':sha(bytes(v&1 for v in mask)),
            'data_mask_sha256':sha(bytes((v&2)>>1 for v in mask)),
            'observed_per_bank':bank_rows(mask),'strict_0501_manifest_overlap':known_overlap(mask),
            'new_strict_prg_bytes':0,'prior_strict_PRG_floor':49404,
            'prior_vpp':26,'last_semantic_checkpoint':'0507',
            'open':['prove exact all-checkpoint overlap and unique physical-code instruction/operand boundaries before promotion',
                    'reconcile mapper/IRQ/source/PPU timing against project CPU core',
                    'room selector 0C/0D has not appeared in sampled logs',
                    'control samples do not establish all code alternatives or reachability']}
    if screenshot:
        report['private_last_frame_screenshot_sha256']=sha(screenshot.read_bytes())
        report['last_frame_visual_check']='manual screenshot: first playable level, HUD and controllable protagonist (not machine verified scene classifier)'
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('original_jp_rom',type=Path)
    p.add_argument('--emulator',required=True,type=Path)
    p.add_argument('--run',nargs=3,action='append',metavar=('NAME','CDL','STDOUT_JSONL'),required=True)
    p.add_argument('--screenshot',type=Path)
    p.add_argument('--out',required=True,type=Path)
    a=p.parse_args()
    result=build(a.original_jp_rom,a.emulator,
       [(n,Path(c),Path(s)) for n,c,s in a.run],screenshot=a.screenshot)
    a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print('Mesen independent reference PASS',result['total_independently_emulated_frames'],'frames',result['physical_PRG_union']['code'],'observed code bytes',result['strict_0501_manifest_overlap']['code_0501_overlap'],'strict-0501 previously counted bytes observed')
if __name__=='__main__':main()
