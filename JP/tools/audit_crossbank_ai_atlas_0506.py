#!/usr/bin/env python3
"""0506: ROM-locked bank-$0A -> bank-$0E loader and AI action candidate atlas.

Static table entries and raw opcode byte-pattern matches are NOT live proofs.
"""
import hashlib,json,sys
from pathlib import Path
from collections import Counter
ROM_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
EXPECTED_CALLS={'FB96':11,'FBA5':4,'FC17':6,'FC1F':43,'FCDE':92}
SCRIPT_COUNTS={2:4,3:9,9:5,10:6,11:12,12:1}
def audit(path):
    rom=Path(path).read_bytes()
    assert len(rom)==393232 and hashlib.sha256(rom).hexdigest()==ROM_SHA
    prg=rom[16:16+262144]
    bk=lambda n:prg[n*16384:(n+1)*16384]
    a,b=bk(10),bk(11)
    f=prg[31*8192:32*8192]
    ra=lambda p,n=1:a[p-0x8000:p-0x8000+n]
    rb=lambda p,n=1:b[p-0x8000:p-0x8000+n]
    rf=lambda p,n=1:f[p-0xE000:p-0xE000+n]
    assert hashlib.sha256(rf(0xFB96,15)).hexdigest()=='ee81729c39d9a6bafd877761fb04fd75bdfe777660fadabb52539d86e744cc2d'
    assert rf(0xFB96,15)==bytes.fromhex('a9 0e 20 d0 e2 b1 08 48 a9 0a 20 d0 e2 68 60')
    assert rf(0xE2D0,6)==bytes.fromhex('85 23 8d 00 80 60')
    assert hashlib.sha256(ra(0xB7F7,0x7C)).hexdigest()=='068cd9f225e38a3b2f0b6e19717bfa11b73a68b9419854d684c42cf55d66d15d'
    assert hashlib.sha256(ra(0xB689,0x1B)).hexdigest()=='7596c407bd8d6e20e9e5fdce89d0faef9381aeb07392da929b8670d948ea1578'
    assert ra(0xB597,3)==bytes.fromhex('20 89 b6')
    assert ra(0xB689,5)==bytes.fromhex('a5 68 20 fb e7')
    targets=[int.from_bytes(ra(0xB68E+i*2,2),'little') for i in range(11)]
    assert len(targets)==11 and targets[0]==0xB6A4
    assert ra(0xB6B1,3)==bytes.fromhex('20 f7 b7')
    assert ra(0xB825,6)==bytes.fromhex('29 0f 85 54 29 01')
    calls=[p for p in range(0xB7F7,0xB873) if ra(p,3)==bytes.fromhex('20 96 fb')]
    assert calls==[0xB808,0xB811,0xB819,0xB822,0xB832,0xB839,
                   0xB842,0xB84D,0xB854,0xB85B,0xB862]
    ptrs={i:int.from_bytes(rb(0xBEA3+2*i,2),'little') for i in range(107)}
    starts=sorted({p for p in ptrs.values() if 0xA4A6<=p<=0xB0DE})
    assert len(set(ptrs.values()))==72 and len(starts)==71
    assert all((v-u)%4==0 for u,v in zip(starts,starts[1:]))
    matches=[]
    for ident,p,action,target in [(0x24,0xA626,0x5D,0x8DC6),
                                  (0x25,0xAE1A,0x5F,0x8E10),
                                  (0x26,0xAE6E,0x89,0x8DF9)]:
        assert ptrs[ident]<=p and rb(p)[0]==action
        slot=(0xBE67 if action&128 else 0xBD67)+((action*2)&255)
        assert int.from_bytes(rb(slot,2),'little')==target
        matches.append({'script_id':f'{ident:02X}','candidate_record':f'{p:04X}',
                        'action':f'{action:02X}','handler':f'{target:04X}','live':False})
    hist=Counter(rb(p)[0] for p in range(0xA4A6,0xB106,4))
    assert sum(hist.values())==792 and len(hist)==163
    jsrs={}
    for h,want in EXPECTED_CALLS.items():
        target=int(h,16);pattern=bytes((0x20,target&255,target>>8));locations=[]
        for bank in range(16):
            data=bk(bank);idx=0
            while (idx:=data.find(pattern,idx))!=-1:
                locations.append(f'{bank:02X}:{idx+0x8000:04X}');idx+=1
        assert len(locations)==want
        jsrs[h]=locations
    init=[]
    for bank in range(16):
        data=bk(bank)
        for i in range(len(data)-4):
            if data[i]==0xA9 and data[i+2:i+5]==bytes.fromhex('9d ef 05'):
                init.append({'raw_bank':f'{bank:02X}','cpu':f'{i+0x8000:04X}',
                             'id':f'{data[i+1]:02X}','live':False})
    assert len(init)==37
    assert {bank:sum(x['raw_bank']==f'{bank:02X}' for x in init)
            for bank in SCRIPT_COUNTS}==SCRIPT_COUNTS
    assert any(x['cpu']=='B503' and x['id']=='1B' and x['raw_bank']=='0B' for x in init)
    return {'rom_sha256':ROM_SHA,'checkpoint':'0506','strict_new_bytes':0,
      'bank0a_dispatch':{'table_entries':11,'selector_68_live_domain':'unproved',
                         'index0_encoded_target':'B6A4','loader':'B7F7',
                         'calls_FB96':11,'temporary_read_bank':'0E',
                         'restore_bank':'0A','RAM54_local_range':'00-0F'},
      'script_atlas':{'mechanical_slots':107,'distinct_pointers':72,
         'candidate_starts':71,'candidate_lattice_cells':792,
         'distinct_first_action_values':163,'related_FC17_matches':matches,
         'all_script_records_live':False},
      'jsr_pattern_sites':jsrs,'script_store_patterns':init,
      'native_test_cases':65537,
      'unresolved':['bank0A B689 selector $68 producer and active mapper state',
       'script IDs $24/$25/$26 live producers','fixed FC17 valid inbound callers',
       'global $54/$14 writers into FD62,Y']}
if __name__=='__main__':
    if len(sys.argv) not in (2,3):
        sys.exit('usage: audit_crossbank_ai_atlas_0506.py JP.nes [report.json]')
    r=audit(sys.argv[1])
    if len(sys.argv)==3:Path(sys.argv[2]).write_text(json.dumps(r,indent=2)+'\n')
    print('0506 JP ROM PASS',r['rom_sha256'])
    print('BANK0A: 11 encoded dispatch pointers, index0 B6A4, B7F7 loader calls FB96 11 times')
    print('SCRIPT: 107 mechanical slots / 72 pointers / 71 starts / 792 provisional 4-byte cells')
    print('FC17 candidate scripts: 24->5D; 25->5F; 26->89')
    print('RAW: 156 JSR and 37 immediate script initializer patterns; neither proves live code')
    print('Strict new bytes: 0; active mapper/selector domains unresolved')
