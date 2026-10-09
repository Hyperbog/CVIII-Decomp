#!/usr/bin/env python3
"""Reproduce synthetic JP CPU code-bit paths and compare exact physical US PRG windows.

The synthesized execution witness is *NOT* an independently collected FCEUX
or Mesen CDL, and exact target bytes do *NOT* prove a US live code path.
The 0501 source manifest is an overlap accounting subset, not all strict 0507.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from audit_0508_dynamic_producer_manifest import run
from nes_certified_reuse import match_source
from nes_cdl_bridge_0508 import validated_manifest, sha
from nes_reuse import OPCODES,MODES

JP_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
US_SHA='1c7b2ed2c1fb5839a6764006aa476f5c9d48f99465b6141980f3a5af1dfec0d6'
PRG_LEN=262144
BANK=8192

def verified_image(path:str,expected:str)->bytes:
    b=Path(path).read_bytes()
    if len(b)!=393232 or sha(b)!=expected:raise ValueError('ROM image SHA-256 does not match pinned version')
    return b

def code_runs(mask:bytes,prg:bytes,min_length:int=16)->list[dict]:
    if len(mask)!=len(prg):raise ValueError('mask/physical PRG mismatch')
    if min_length<8 or min_length>64:raise ValueError('invalid minimum window')
    rows=[]
    for b in range(0,len(prg),BANK):
        start=None
        for p in range(b,min(b+BANK,len(prg))+1):
            code=p<min(b+BANK,len(prg)) and bool(mask[p])
            if code and start is None:start=p
            if not code and start is not None:
                n=p-start
                if n>=min_length:
                    rows.append({'source_prg_offset':start,'size':n,'sha256':sha(prg[start:p]),
                                 'source_bank':f'{start//BANK:02X}',
                                 'evidence_class':'synthetic ROM instruction/operand fetch only',
                                 'source_cpu_start':None})
                start=None
    return rows

def decode_full_region(code:bytes)->int|None:
    cursor=0;starts=0
    while cursor<len(code):
        instr=OPCODES.get(code[cursor])
        if instr is None:return None
        n=MODES[instr[1]]
        if cursor+n>len(code):return None
        cursor+=n;starts+=1
    return starts

def audit(jp_path:str,us_path:str,manifest_path:str,scenarios:list[tuple[str,int]])->dict:
    jpr=verified_image(jp_path,JP_SHA)
    upr=verified_image(us_path,US_SHA)
    jp=jpr[16:16+PRG_LEN];us=upr[16:16+PRG_LEN]
    manifest=json.loads(Path(manifest_path).read_text())
    pinned,pinmeta=validated_manifest(manifest,jp,JP_SHA)
    cseen=bytearray(PRG_LEN);scenarios_out=[]
    for policy,nmi in scenarios:
        trace=run(jpr,policy,nmi)
        codemask,reads=trace.pop('_masks')
        assert sha(codemask)==trace['code_offsets_digest_sha256']
        for i,seen in enumerate(codemask):
            if seen:cseen[i]=1
        scenarios_out.append({'name':policy,'manual_nmis':nmi,
                              'original_ROM_instruction_steps':trace['total_instructions_including_reset'],
                              'physical_code_operand_bytes':codemask.count(1)})
    runs=code_runs(cseen,jp,16)
    total_run_bytes=sum(x['size'] for x in runs)
    matched=match_source(jp,us,runs,window=16,max_candidates=40)
    assert matched['source_certified_bytes']==total_run_bytes
    # Matcher was designed for certified code. Here the input is only simulated
    # code-bit runs: strip inherited "certified" field names and classify as CANDIDATE.
    candidate_stats={
        'minimum_exact_window':16,
        'synthetic_executed_bytes_in_ge16_runs':matched['source_certified_bytes'],
        'synthetic_executed_bytes_with_unique_US_windows':matched['source_certified_bytes_with_unique_exact_target_windows'],
        'synthetic_executed_bytes_with_only_ambiguous_US_windows':matched['source_certified_bytes_with_only_ambiguous_target_windows'],
        'synthetic_executed_bytes_without_US_windows':matched['source_certified_bytes_without_target_windows'],
        'synthetic_runs_examined':matched['manifest_region_count'],
        'fraction_of_eligible_source_bytes_with_unique_US_windows':matched['source_fraction_unique_window'],
        'candidate_per_physical_bank':matched['per_source_bank'],
        'candidate_source_run_rows':matched['verified_source_regions_with_target_candidates'],
        'nonoverlapping_example_exact_US_matches':matched['representative_nonoverlapping_unique_target_candidates'],
        'evidence':'CANDIDATE ONLY; source is synthetic executed code bit, NOT source certified code and NOT target live US code',
        'strict_bytes_promoted':0,
    }
    overlap0501=sum(a and b for a,b in zip(cseen,pinned))
    direct_start=0x3E7B8;target_start=0x3E82A;direct_n=92
    fragment=jp[direct_start:direct_start+direct_n]
    assert all(cseen[direct_start:direct_start+direct_n])
    assert fragment==us[target_start:target_start+direct_n]
    assert us.find(fragment)==target_start and us.find(fragment,target_start+1)<0
    n_opcodes=decode_full_region(fragment)
    assert n_opcodes==50
    return {
        'schema':'nes-0508-synthetic-code-window-reuse/v1',
        'jp_rom_sha256':JP_SHA,'us_rom_sha256':US_SHA,
        'source_mapper':24,'target_mapper':5,
        'proof_grade':'SIMULATED_JP_INSTRUCTION_FETCH_PLUS_EXACT_US_BYTES_NOT_US_LIVENESS',
        'scenarios':scenarios_out,
        'distinct_synthetic_executed_code_operand_bytes':cseen.count(1),
        'physical_code_bit_mask_sha256':sha(cseen),
        'eligible_maximal_code_runs_ge16':len(runs),
        'eligible_code_run_bytes':total_run_bytes,
        'code_bit_bytes_in_runs_shorter_than16':cseen.count(1)-total_run_bytes,
        'checkpoint_0501_hash_locked_source_regions':pinmeta['manifest_region_count'],
        'checkpoint_0501_source_region_bytes':pinmeta['pinned_source_region_bytes'],
        'synthetic_code_bytes_overlapping_checkpoint_0501_regions':overlap0501,
        'source_span_to_target_exact_candidates':candidate_stats,
        'strongest_example':{'jp_physical_prg_offset':direct_start,
            'jp_cpu_address_if_fixed_PRG31':'E7B8',
            'us_physical_prg_offset':target_start,
            'us_cpu_address_if_last_PRG8K_fixed':'E82A',
            'byte_length':direct_n,'official_opcodes_in_linear_decode':n_opcodes,
            'exact_prg_sha256':sha(fragment),'unique_exact_target_occurrences':1,
            'whole_span_observed_in_synthetic_JP_execution':True,
            'target_US_live_code_path_proved':False},
        'new_strict_prg_bytes':0,'vpp_delta':0,
        'claim_limits':["Source execution is synthetic and excludes real PPU/IRQ hardware parity",
                        "An exact US match does not prove the target's mapper state or callers",
                        "Checkpoint 0501 is a subset, not the complete semantic 0507 byte ledger",
                        "CDL format parser is tested separately; these internal masks are NOT a foreign-emulator CDL"],
    }

if __name__=='__main__':
    cli=argparse.ArgumentParser();cli.add_argument('jp_rom');cli.add_argument('us_rom');
    cli.add_argument('manifest');cli.add_argument('report');cli.add_argument('--scenarios',default='start30:300,none:120')
    a=cli.parse_args()
    scenarios=[]
    for x in a.scenarios.split(','):
        name,ns=x.split(':');n=int(ns)
        if name not in ('start30','none','abstart','startheld','start20') or not 1<=n<=1200:
            raise ValueError('invalid scenario')
        scenarios.append((name,n))
    out=audit(a.jp_rom,a.us_rom,a.manifest,scenarios)
    Path(a.report).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    x=out['source_span_to_target_exact_candidates']
    print('PASS',out['distinct_synthetic_executed_code_operand_bytes'],'modeled code bytes;',
          x['synthetic_executed_bytes_with_unique_US_windows'],'unique-window source bytes in US;',
          out['strongest_example']['byte_length'],'exactly common JP code bytes / 50 opcodes; no strict credit')
