#!/usr/bin/env python3
"""0506 supplementary conditional JP state-chain audit. Never claims live state."""
from pathlib import Path
import hashlib,sys
ROM_SHA='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
def check(path):
    rom=Path(path).read_bytes()
    assert len(rom)==393232 and hashlib.sha256(rom).hexdigest()==ROM_SHA
    b=rom[16+10*16384:16+11*16384]
    get=lambda a,n:b[a-0x8000:a-0x8000+n]
    assert get(0xB4CC,5)==bytes.fromhex('a5 19 20 fb e7')
    pointers=[int.from_bytes(get(0xB4D1+2*i,2),'little') for i in range(12)]
    assert pointers==[0xB570,0xB58C,0xB597,0xB5A3,0xB5CC,0xB5DA,
                      0xB614,0xB622,0xB64E,0xB5CC,0xB5DA,0xB662]
    assert get(0xB58C,11)==bytes.fromhex('a9 6b 20 49 e2 20 e9 b4 e6 19 60')
    assert get(0xB4E9,5)==bytes.fromhex('a9 00 85 68 60')
    assert get(0xB597,12)==bytes.fromhex('20 89 b6 a5 68 c9 ff d0 02 e6 19 60')
    assert get(0xB689,5)==bytes.fromhex('a5 68 20 fb e7')
    assert int.from_bytes(get(0xB68E,2),'little')==0xB6A4
    assert get(0xB6B1,3)==bytes.fromhex('20 f7 b7')
    return pointers
if __name__=='__main__':
    if len(sys.argv)!=2:sys.exit('usage: audit_bank0a_state_chain_0506.py JP.nes')
    check(sys.argv[1])
    print('0506 supplement: JP-ROM PASS; 12 encoded state pointers')
    print('state1 B58C -> B4E9 STA $68=0; INC $19 -> state2 B597 -> B689')
    print('conditional B689 selector0 -> B6A4 -> B7F7; live frame/mapper proof OPEN')
    print('new strict bytes 0')
