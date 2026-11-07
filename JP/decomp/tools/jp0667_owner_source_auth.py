#!/usr/bin/env python3
"""JP0667 private original ROM proofs for D/E/frame/percussion/DMC source.

The authenticated original JP cartridge stays local. Report is metadata-only.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
ROM_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
CORE_SHA='e2c3ff3d7e9f96b598610a8028f5b92a606fac7f9acb2977811146fa145fdb67'
SOURCES=(
    ('D_E_local_handlers',5,0x837e,0x8531,'ff148fe350183ed545f2bfb1ed546edc93686dfdc3bbd743da069677274701c8'),
    ('percussion_sound_request_lookup',5,0x8072,0x807e,'157833d861853f2e17a643fb6fcdc2999a9fcf03f53796bd51cee62c90307612'),
    ('frame_voice_gate',12,0x8a7c,0x8aa1,'730a46288fbd1fd3f531a9a5c4e7fb540950c86fbce01d7d249931c7ce3885ed'),
    ('DMC_fourbyte_program_table',12,0xa957,0xa993,'02d705700fcb42b0b1fa7c5520e54734f8180458265f1286aa132613b4fc6b45'),
)
def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def verify(rom:bytes)->dict:
    if len(rom)!=393232 or sha(rom)!=ROM_SHA or rom[:4]!=b'NES\x1a':
        raise ValueError('unauthenticated Japanese Mapper24 original ROM')
    if (rom[6]>>4 | rom[7]&0xf0)!=24:
        raise ValueError('unexpected mapper')
    records=[]
    for name,bank,start,end,hash_hex in SOURCES:
        at=16+bank*16384+start-0x8000
        span=rom[at:at+end-start]
        if len(span)!=end-start or sha(span)!=hash_hex:
            raise ValueError('source drift '+name)
        records.append({'name':name,'physical_raw16':f'{bank:02X}',
                        'cpu_window':f'{start:04X}-{end-1:04X}',
                        'bytes':len(span),'sha256':hash_hex})
    bank05=rom[16+5*16384:16+6*16384]
    if sha(bank05[1:0x87ae-0x8000])!=CORE_SHA:
        raise ValueError('raw05 original common interpreter drift')
    # Source classifies seven class values as high DMC requests and five as
    # low original sound requests. Do not reproduce copyrighted data payloads.
    voices=bank05[0x72:0x7e]
    noise=sum(1<=v<=5 for v in voices)
    dmc=sum(0x6f<=v<=0x7d for v in voices)
    if (noise,dmc)!=(5,7):raise ValueError('original percussion request domain drift')
    return {'schema':'jp0667-authentic-original-source-witnesses/v1',
            'original_jp_rom_sha256':ROM_SHA,'source_witnesses':records,
            'original_percussion_noise_requests':noise,
            'original_percussion_dmc_requests':dmc,
            'original_source_rom_confirmed':True,
            'original_game_playback_traced':False,
            'frame_to_absolute_cpu_clock_verified':False,
            'independent_Mesen_parity_verified':False}
def smoke():
    for damaged in (b'',bytes(393232),b'NES\x1a'+bytes(393228)):
        try:verify(damaged)
        except ValueError:continue
        raise AssertionError('nonoriginal synthetic cartridge accepted')
    print('PASS JP0667 ROM-free source identity negative tests')
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path);p.add_argument('--smoke',action='store_true')
    p.add_argument('--json',type=Path);a=p.parse_args()
    if a.smoke:smoke()
    if a.rom:
        result=verify(a.rom.read_bytes())
        if a.json:a.json.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        print('PASS JP0667 authenticated D/E+frame+percussion+DMC exact original source')
    if not a.rom and not a.smoke:p.error('--smoke and/or --rom original JP required')
if __name__=='__main__':main()
