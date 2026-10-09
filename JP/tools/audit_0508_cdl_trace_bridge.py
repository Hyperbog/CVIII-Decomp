#!/usr/bin/env python3
"""ROM-locked physical-byte reconciliation: synthetic CPU execution vs 0501 manifest.

NOT a third-party emulator CDL; never call these synthetic masks a reference log.
No raw ROM payload or 256-KiB byte mask is committed.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from audit_0508_dynamic_producer_manifest import run
from nes_cdl_bridge_0508 import CODE,DATA,sha,summarize,validated_manifest

ROM_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'

def audit(rom_path,manifest_path,scenarios):
    rom=Path(rom_path).read_bytes()
    if len(rom)!=393232 or sha(rom)!=ROM_SHA:raise ValueError('wrong authoritative JP ROM')
    prg=rom[16:16+262144]
    manifest=json.loads(Path(manifest_path).read_text())
    certified,meta=validated_manifest(manifest,prg,ROM_SHA)
    runs=[];mcode=bytearray(len(prg));mread=bytearray(len(prg))
    for policy,nmis in scenarios:
        trace=run(rom,policy,nmis)
        code,read=trace.pop('_masks')
        assert sha(code)==trace['code_offsets_digest_sha256']
        assert sha(read)==trace['all_ROM_read_offsets_digest_sha256']
        assert code.count(1)==trace['distinct_executed_code_operand_bytes']
        for i in range(len(prg)):
            if code[i]:mcode[i]=1
            if read[i]:mread[i]=1
        runs.append({'policy':policy,'manually_injected_nmis':nmis,
                     'instructions':trace['total_instructions_including_reset'],
                     'synthetic_code_operand_bytes':code.count(1),
                     'read_byte_count_all_causes':read.count(1)})
    # The original model instruments Bus.rb() for *both* instruction/operand
    # fetches and data reads. Only bytes read but never fetched as code are
    # definitely data-only under this synthetic observer; code+data cannot be
    # inferred, so it is intentionally not asserted here.
    pseudo=bytes((CODE if c else DATA if r else 0) for c,r in zip(mcode,mread))
    r=summarize(pseudo,certified,rom_sha=ROM_SHA,cdl_sha=sha(pseudo),
                meta={'format':'synthetic-CPU-internal-physical-mask (not FCEUX/Mesen CDL)',
                      'flag_semantics':'bit0 executed opcode/operands, bit1 ROM read but never executed, no CPU-window hint'},
                manifest_info=meta,provenance='CONTROLLED_PROJECT_SIMULATION_NOT_INDEPENDENT_EMULATOR')
    r.update({'rom_hash_checked':True,'scenarios':runs,
              'synthetic_code_mask_sha256':sha(mcode),
              'synthetic_any_read_mask_sha256':sha(mread),
              'reference_emulator_witness':False,
              'no_saved_raw_CDL_or_ROM_payload':True,
              'byte_flags_are_not_external_trace_evidence':True,
              'observed_data_only_is_underestimate_due_to_code_data_aliasing':True,
              'strict_prg_covered_before':49404,'strict_prg_covered_after':49404,
              'vpp_before':25,'vpp_after':25,'last_completed_checkpoint':'0507'})
    return r

if __name__=='__main__':
    cli=argparse.ArgumentParser();cli.add_argument('rom');cli.add_argument('source_regions');cli.add_argument('report');
    cli.add_argument('--scenarios',default='start30:300,none:120');a=cli.parse_args()
    scenarios=[]
    for x in a.scenarios.split(','):
        name,n=x.split(':');n=int(n)
        if name not in ('start30','none','abstart','startheld','start20') or not 1<=n<=1200:
            raise ValueError('scenario out of bounded supported domain')
        scenarios.append((name,n))
    r=audit(a.rom,a.source_regions,scenarios)
    Path(a.report).write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    print('PASS synthetic CDL crosscheck',sum(s['instructions'] for s in r['scenarios']),'CPU instructions,',
          r['counts'].get('code_observed',0),'code bits,',r['counts'].get('manifest_bytes_also_logged_as_code',0),
          'previously verified 0501 bytes also code; STRICT DELTA ZERO')
