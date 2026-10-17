#!/usr/bin/env python3
"""ROM-fingerprinted FCEUX / Mesen legacy / Mesen2 CDLv2 PRG evidence audit.

This tool does not execute a game, assume provenance of imported logs, promote
PRG bytes, or export original game bytes. It distinguishes physical ROM offsets
from CPU mapping hints (which record only the most recent mapped CPU window).

Documentation:
  https://fceux.com/web/help/CodeDataLogger.html
  https://raw.githubusercontent.com/SourMesen/Mesen2/master/Core/Debugger/CodeDataLogger.cpp
  https://forums.nesdev.org/viewtopic.php?p=283235
"""
from __future__ import annotations
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from nes_reuse import load

CODE = 0x01
DATA = 0x02
WINDOW_MASK = 0x0C
INDIRECT_CODE = 0x10
INDIRECT_DATA = 0x20
PCM = 0x40
MESEN_SUB_ENTRY = 0x80
V2_MAGIC = b'CDLv2'
V2_HEADER = 9
BANK_BYTES = 8192

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def require_hex32(v: str | None) -> int | None:
    if v is None:
        return None
    try:
        n = int(v.removeprefix('0x'), 16)
    except ValueError as exc:
        raise ValueError('expected Mesen CDLv2 CRC must be a hex number') from exc
    if not 0 <= n <= 0xFFFFFFFF:
        raise ValueError('expected Mesen CDLv2 CRC outside uint32')
    return n

def decode_cdl(data: bytes, prg_bytes: int, chr_bytes: int,
               *, codec: str = 'auto', expected_mesen_rom_crc32: int | None = None) -> tuple[bytes, dict[str, Any]]:
    """Decode exactly bounded physical PRG flags; never confuse CHR or Mesen trailer with PRG."""
    if codec not in ('auto', 'fceux', 'mesen-legacy', 'mesen2'):
        raise ValueError('unsupported CDL encoding selector')
    if prg_bytes < 1 or chr_bytes < 0:
        raise ValueError('invalid cartridge PRG/CHR geometry')
    if data.startswith(V2_MAGIC):
        fmt = 'mesen2'
        if codec not in ('auto', fmt):
            raise ValueError('Mesen2 CDLv2 header cannot be read as raw legacy CDL')
        if len(data) < V2_HEADER:
            raise ValueError('truncated Mesen2 CDLv2 header')
        logged_crc = int.from_bytes(data[5:9], 'little')
        if expected_mesen_rom_crc32 is not None and logged_crc != expected_mesen_rom_crc32:
            raise ValueError('CDLv2 ROM CRC does not match independently supplied expected CRC')
        payload = data[V2_HEADER:]
    else:
        if codec == 'mesen2':
            raise ValueError('expected Mesen2 CDLv2 header')
        # FCEUX and older Mesen share the common code/data bits but do not
        # share all indirect/JSR-target semantics. Auto mode is conservative.
        fmt = codec if codec != 'auto' else 'fceux-or-mesen-legacy'
        logged_crc = None
        payload = data
        if expected_mesen_rom_crc32 is not None:
            raise ValueError('expected Mesen CRC supplied for a headerless CDL')
    if len(payload) not in (prg_bytes, prg_bytes + chr_bytes):
        raise ValueError('unsupported CDL payload length: require PRG bytes exactly or PRG+CHR bytes; do not guess offset')
    # A CHR-RAM game with chr_bytes=0 legitimately has the same two accepted lengths.
    prg = payload[:prg_bytes]
    metadata = {
        'format': fmt,
        'prg_flag_count': prg_bytes,
        'chr_flag_count': len(payload) - prg_bytes,
        'mesen2_rom_crc32': f'{logged_crc:08X}' if logged_crc is not None else None,
        'mesen2_rom_crc_verified_against_external_expected':
            logged_crc is not None and expected_mesen_rom_crc32 is not None,
        'log_image_identity_binding': ('external Mesen ROM CRC supplied and matched, '
                                       'not independently derived from ROM' if logged_crc is not None
                                       and expected_mesen_rom_crc32 is not None else
                                       'UNVERIFIED: raw CDL carries no ROM hash, or CDLv2 ROM CRC is not independently authenticated'),
        'flag7_interpretation': ('Mesen subroutine entry marker' if fmt in ('mesen2','mesen-legacy')
                                 else 'reserved/format-dependent; not treated as a code fetch'),
    }
    return prg, metadata

def validated_manifest(manifest: dict[str, Any], prg: bytes, image_sha256: str) -> tuple[bytearray, dict]:
    """Pin all source intervals with physical SHA; no claim that every span is executable code."""
    if manifest.get('schema') != 'nes-semantic-origin-regions/v1':
        raise ValueError('unknown certified-region manifest schema')
    if manifest.get('source_rom_sha256') != image_sha256:
        raise ValueError('manifest original-ROM identity does not match supplied image')
    regions = manifest.get('regions')
    if not isinstance(regions,list) or not regions:
        raise ValueError('manifest has no regions')
    occupied = bytearray(len(prg))
    for idx, r in enumerate(regions):
        st, length, h = r.get('source_prg_offset'), r.get('size'), r.get('sha256')
        if (type(st) is not int or type(length) is not int or
            st < 0 or length < 1 or st + length > len(prg)):
            raise ValueError(f'manifest region {idx}: outside physical PRG')
        if not isinstance(h,str) or sha(prg[st:st+length]) != h:
            raise ValueError(f'manifest region {idx}: SHA-256 mismatch')
        if any(occupied[st:st+length]):
            raise ValueError(f'manifest region {idx}: overlap')
        occupied[st:st+length] = b'\x01'*length
    counted = occupied.count(1)
    if manifest.get('total_certified_source_bytes') != counted:
        raise ValueError('manifest strict source-region total mismatch')
    return occupied, {
        'manifest_region_count':len(regions),
        'pinned_source_region_bytes':counted,
        'manifest_declared_source_checkpoint':manifest.get('source_verified_checkpoint'),
        'manifest_source_evidence':manifest.get('source_evidence'),
        'manifest_sha256':sha(json.dumps(manifest,sort_keys=True,separators=(',',':')).encode()),
        'interpretation':'source-region classification is supplied by the manifest, not inferred from CDL'
    }

def top_runs(flags:bytes, certified:bytearray, *, cap:int = 16, minimum:int = 16) -> list[dict]:
    """Candidate contiguous code-bit spans outside the selected source manifest (bank-local)."""
    found=[];start=None
    for bank_start in range(0,len(flags),BANK_BYTES):
        bank_end=min(len(flags),bank_start+BANK_BYTES)
        start=None
        for p in range(bank_start,bank_end+1):
            present=p<bank_end and bool(flags[p]&CODE) and not bool(certified[p])
            if present and start is None:start=p
            elif not present and start is not None:
                n=p-start
                if n>=minimum:
                    found.append({'physical_prg_offset':start,'physical_bank_8k':start//BANK_BYTES,
                                 'byte_length':n,'code_mask_sha256':sha(bytes(flags[start:p])),
                                 'evidence':'CDL code-bit sequence only; not instruction-aligned or liveness-certified'})
                start=None
    return sorted(found,key=lambda x:(-x['byte_length'],x['physical_prg_offset']))[:cap]

def summarize(flags:bytes, certified:bytearray, *, rom_sha:str, cdl_sha:str,
              meta:dict[str,Any], manifest_info:dict|None=None,
              provenance:str='unspecified', max_runs:int=16) -> dict[str,Any]:
    if len(flags)!=len(certified):
        raise ValueError('physical CDL and certified mask length mismatch')
    if not 0<=max_runs<=200:raise ValueError('max_runs out of range')
    stat=Counter()
    per_bank=[]
    for b in range(0,len(flags),BANK_BYTES):
        segment=flags[b:b+BANK_BYTES]
        cert=certified[b:b+BANK_BYTES]
        d=Counter()
        for byte,pin in zip(segment,cert):
            code=bool(byte&CODE);data=bool(byte&DATA)
            if code:d['code_observed']+=1
            if data:d['data_observed']+=1
            if code and data:d['both_code_and_data']+=1
            if code or data:d['code_or_data_observed']+=1
            else:d['not_observed_as_code_or_data']+=1
            if byte&INDIRECT_CODE:d['indirect_code_tag']+=1
            if byte&INDIRECT_DATA:d['indirect_data_tag']+=1
            if byte&PCM:d['pcm_tag']+=1
            if byte&MESEN_SUB_ENTRY:d['bit7_tag_format_dependent']+=1
            if pin:
                d['manifest_pinned_bytes']+=1
                if code:d['manifest_bytes_also_logged_as_code']+=1
                if data:d['manifest_bytes_also_logged_as_data']+=1
                if not code and not data:d['manifest_bytes_not_observed']+=1
                if data and not code:d['manifest_bytes_logged_data_only']+=1
            elif code:d['code_bit_outside_pinned_manifest']+=1
        stat.update(d)
        per_bank.append({'physical_prg8k_bank':b//BANK_BYTES,**dict(sorted(d.items()))})
    m={'schema':'nes-cdl-physical-evidence/v1', 'rom_sha256':rom_sha,
       'cdl_sha256':cdl_sha,'provenance_label_supplied_by_user':provenance,
       'imported_format':meta,'physical_prg_bytes':len(flags),
       'counts':dict(sorted(stat.items())), 'physical_banks':per_bank,
       'largest_contiguous_code_bit_candidates_outside_manifest':top_runs(flags,certified,cap=max_runs),
       'verified_source_manifest':manifest_info,
       'policy':{
           'strict_verified_prg_bytes_added':0,'vpp_points_added':0,
           'code_flag_means_observed_fetch_not_complete_call_graph':True,
           'unmarked_bytes_are_not_proven_unreachable':True,
           'code_data_overlap_is_valid_not_a_bad_log':True,
           'data_only_markers_inside_manifest_not_conflicts_without_same_scenario':True,
           'rom_hash_does_not_authenticate_external_cdl_provenance':True,
           'cpu_window_flags_are_last_access_hints_not_mapper_execution_proof':True,
           'raw_game_code_or_assets_exported':False}}
    return m

def audit(rom_path:str, cdl_path:str, *, manifest_path:str|None=None,
          format_name:str='auto',expected_mesen_rom_crc32:int|None=None,
          provenance:str='unspecified',max_runs:int=16)->dict:
    info,prg=load(rom_path)
    if not prg:raise ValueError('CDL physical-PRG audit requires a NES cartridge')
    cdl=Path(cdl_path).read_bytes()
    flags, meta=decode_cdl(cdl,len(prg),info['chr_bytes'],codec=format_name,
                          expected_mesen_rom_crc32=expected_mesen_rom_crc32)
    if manifest_path:
        manifest=json.loads(Path(manifest_path).read_text())
        cert,manifest_info=validated_manifest(manifest,prg,info['file_sha256'])
    else:
        cert=bytearray(len(prg));manifest_info=None
    report=summarize(flags,cert,rom_sha=info['file_sha256'],cdl_sha=sha(cdl),
                     meta=meta,manifest_info=manifest_info,provenance=provenance,max_runs=max_runs)
    report['rom_mapper_id']=info['mapper']
    report['cartridge_format']=info['format']
    report['trust_grade']='structural CDL flags; witness conditions require independent verification'
    return report

def main()->None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('rom');p.add_argument('cdl')
    p.add_argument('--source-regions',help='ROM-hash pinned verified source manifest')
    p.add_argument('--format',choices=('auto','fceux','mesen-legacy','mesen2'),default='auto')
    p.add_argument('--expected-mesen-rom-crc32',type=require_hex32)
    p.add_argument('--provenance',default='unspecified')
    p.add_argument('--max-runs',type=int,default=16)
    p.add_argument('--out')
    a=p.parse_args()
    r=audit(a.rom,a.cdl,manifest_path=a.source_regions,format_name=a.format,
            expected_mesen_rom_crc32=a.expected_mesen_rom_crc32,
            provenance=a.provenance,max_runs=a.max_runs)
    out=json.dumps(r,indent=2,sort_keys=True)+'\n'
    if a.out:Path(a.out).write_text(out)
    else:print(out,end='')
    print(f"CDL: {r['counts'].get('code_observed',0)} code-bit bytes, "
          f"{r['counts'].get('manifest_bytes_also_logged_as_code',0)} inside pinned source; "
          "0 new strict PRG bytes")
if __name__=='__main__':main()
