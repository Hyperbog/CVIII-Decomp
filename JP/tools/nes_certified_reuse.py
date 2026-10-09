#!/usr/bin/env python3
"""Cross-ROM exact-window reuse of PREVIOUSLY certified source PRG spans.

Generic across NES mappers: only physical PRG offsets are compared. Source
semantic evidence, destination mapper/CPU buses, gameplay and cross-game
liveness are different obligations; this command never promotes target bytes.
Never prints original code/data, only region hashes, offsets and bounded stats.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
from typing import Any
from nes_reuse import load


def sha(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()


def input_regions(manifest:dict[str,Any],source:bytes,target:bytes,source_id:str,target_id:str)->list[dict[str,Any]]:
    if manifest.get('schema')!='nes-semantic-origin-regions/v1':
        raise ValueError('unexpected manifest schema')
    if manifest.get('source_rom_sha256')!=source_id or manifest.get('target_rom_sha256')!=target_id:
        raise ValueError('manifest image identity does not match supplied ROMs')
    rows=manifest.get('regions')
    if not isinstance(rows,list) or not rows:raise ValueError('manifest has no regions')
    mapped=set();out=[]
    for i,rec in enumerate(rows):
        start=rec.get('source_prg_offset');n=rec.get('size');h=rec.get('sha256')
        if not isinstance(start,int) or isinstance(start,bool) or not isinstance(n,int) or isinstance(n,bool):
            raise ValueError(f'region {i}: bad offset or size')
        if start<0 or n<=0 or start+n>len(source):raise ValueError(f'region {i}: outside source PRG')
        if not isinstance(h,str) or len(h)!=64:raise ValueError(f'region {i}: missing source hash')
        s=source[start:start+n]
        if sha(s)!=h:raise ValueError(f'region {i}: source SHA-256 mismatch')
        if any(k in mapped for k in range(start,start+n)):
            raise ValueError(f'region {i}: overlapping certified source spans')
        mapped.update(range(start,start+n))
        out.append(rec)
    if manifest.get('total_certified_source_bytes') is not None and len(mapped)!=manifest['total_certified_source_bytes']:
        raise ValueError('certified source total mismatch')
    return out


def match_source(source:bytes,target:bytes,regions:list[dict],window=16,max_candidates=48)->dict:
    if not 8<=window<=64:raise ValueError('window must be 8..64')
    if not 0<=max_candidates<=512:raise ValueError('max candidates out of range')
    counts=defaultdict(lambda:{'certified_source_bytes':0,'source_bytes_with_unique_exact_target_anchor':0,
            'source_bytes_with_ambiguous_only_anchor':0,'source_bytes_without_exact_window':0,
            'unique_window_positions':0})
    rows=[];best_candidates=[]
    n_unique=n_ambig=n_none=n_total=0
    for i,rec in enumerate(regions):
        start=rec['source_prg_offset'];length=rec['size'];data=source[start:start+length]
        unique=set();ambig=set();best=None
        n_unique_positions=0
        for shift in range(max(length-window+1,0)):
            fragment=data[shift:shift+window]
            p=target.find(fragment)
            if p<0:continue
            if target.find(fragment,p+1)>=0:
                ambig.update(range(shift,shift+window))
                continue
            n_unique_positions+=1
            unique.update(range(shift,shift+window))
            n=window
            while shift+n<length and p+n<len(target) and data[shift+n]==target[p+n]:n+=1
            candidate={'source_prg_offset':start+shift,'target_prg_offset':p,
                       'target_physical_prg_bank_8k':p//8192,'match_length':n,'sha256':sha(data[shift:shift+n])}
            if best is None or (n,-shift)>(best['match_length'],-(best['source_prg_offset']-start)):
                best=candidate
            best_candidates.append(candidate)
        ambig-=unique
        u=len(unique);a=len(ambig);none=length-u-a
        n_total+=length;n_unique+=u;n_ambig+=a;n_none+=none
        bank=rec.get('source_bank','unspecified')
        v=counts[bank]
        v['certified_source_bytes']+=length
        v['source_bytes_with_unique_exact_target_anchor']+=u
        v['source_bytes_with_ambiguous_only_anchor']+=a
        v['source_bytes_without_exact_window']+=none
        v['unique_window_positions']+=n_unique_positions
        rows.append({**rec,'region_index':i,'unique_exact_target_anchored_source_bytes':u,
                     'ambiguous_only_anchored_source_bytes':a,'no_target_window_source_bytes':none,
                     'unique_window_positions':n_unique_positions,
                     'best_region_bounded_target_candidate':best})
    # Deduplicate overlapping candidate runs using only source physical intervals.
    unique_items={(x['source_prg_offset'],x['target_prg_offset'],x['match_length']):x for x in best_candidates}
    ordered=sorted(unique_items.values(),key=lambda x:(-x['match_length'],x['source_prg_offset'],x['target_prg_offset']))
    representative=[];covered=set()
    for x in ordered:
        if len(representative)>=max_candidates:break
        region=range(x['source_prg_offset'],x['source_prg_offset']+x['match_length'])
        if any(k in covered for k in region):continue
        representative.append(x);covered.update(region)
        if len(representative)>=max_candidates:break
    assert n_total==n_unique+n_ambig+n_none
    return {'minimum_exact_window':window,'source_certified_bytes':n_total,
            'source_certified_bytes_with_unique_exact_target_windows':n_unique,
            'source_certified_bytes_with_only_ambiguous_target_windows':n_ambig,
            'source_certified_bytes_without_target_windows':n_none,
            'source_fraction_unique_window':round(n_unique/n_total,6),
            'manifest_region_count':len(rows),'per_source_bank':dict(sorted(counts.items())),
            'verified_source_regions_with_target_candidates':rows,
            'representative_nonoverlapping_unique_target_candidates':representative,
            'strict_new_verified_source_bytes':0,'strict_new_verified_target_bytes':0,
            'whole_game_semantics_transferred':False,
            'claim':'exact byte similarity inside pre-certified source spans, NOT independent target-region code/data classification or target mapper/runtime equivalence'}


def audit(source_path:str,target_path:str,manifest_path:str,window=16,max_candidates=48)->dict:
    mi=Path(manifest_path);m=json.loads(mi.read_text())
    sinfo,source=load(source_path);tinfo,target=load(target_path)
    if not source or not target:raise ValueError('both inputs must contain NES-cartridge PRG')
    validated=input_regions(m,source,target,sinfo['file_sha256'],tinfo['file_sha256'])
    out=match_source(source,target,validated,window,max_candidates)
    return {'schema':'nes-crossrom-certified-source-census/v1',
            'source_image_sha256':sinfo['file_sha256'],'target_image_sha256':tinfo['file_sha256'],
            'source_mapper':sinfo['mapper'],'target_mapper':tinfo['mapper'],
            'different_mapper':sinfo['mapper']!=tinfo['mapper'],
            'source_evidence':m['source_evidence'],
            'source_verified_checkpoint':m.get('source_verified_checkpoint'),
            'source_evidence_type':m['source_evidence_type'],
            'manifest_sha256':sha(mi.read_bytes()),
            'rights':'hash/offset metadata only; PRG/CHR bytes are not embedded',
            **out}


def main()->None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source_rom');p.add_argument('target_rom');p.add_argument('manifest')
    p.add_argument('--window',type=int,default=16)
    p.add_argument('--max-candidates',type=int,default=48)
    p.add_argument('--out')
    a=p.parse_args()
    result=audit(a.source_rom,a.target_rom,a.manifest,a.window,a.max_candidates)
    s=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if a.out:Path(a.out).write_text(s)
    else:print(s,end='')
    print('source certified bytes',result['source_certified_bytes'],'uniquely anchored source bytes',result['source_certified_bytes_with_unique_exact_target_windows'], 'no strict byte credit')
if __name__=='__main__':main()
