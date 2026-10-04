#!/usr/bin/env python3
from __future__ import annotations
import hashlib, sys
from collections import Counter
from pathlib import Path
import build_whole_prg_atlas as atlas

EXPECTED_GLOBAL={
    'official_opcode_candidates':186258,
    'control_candidates':110127,
    'memory_candidates':87686,
    'zp_write_candidates':17841,
    'e7fb_bytepattern_candidates':35,
}
EXPECTED_FOCUS={0x10:534,0x18:311,0x2C:119,0x68:185}
EXPECTED_BANK31_SHA='963a69526dd9fe10bf57a702da1db9e4b1ac533680fa3d419605e20e3a91ee0a'
EXPECTED_VECTORS={'NMI':0xE057,'RESET':0xE00B,'IRQ':0xE0F5}

def main(path:str)->None:
    rom=Path(path).read_bytes()
    assert hashlib.sha256(rom).hexdigest()==atlas.ROM_SHA
    trainer=512 if rom[6]&4 else 0
    prg=rom[16+trainer:16+trainer+atlas.PRG_SIZE]
    assert len(prg)==atlas.PRG_SIZE
    g=Counter(); focus=Counter()
    for bank in range(32):
        b=prg[bank*atlas.BANK_SIZE:(bank+1)*atlas.BANK_SIZE]
        for off in range(atlas.BANK_SIZE):
            d=atlas.decode_at(b,off)
            if not d: continue
            g['official_opcode_candidates']+=1
            mn,mode,n,raw,operand=d
            if mn in atlas.CTRL:
                g['control_candidates']+=len(atlas.cpu_views(bank,off))
            ak=atlas.access_kind(mn)
            if ak and mode in atlas.MEMMODES:
                g['memory_candidates']+=1
                if mode in {'zp','zpx','zpy','indx','indy'} and operand in EXPECTED_FOCUS:
                    focus[operand]+=1
                if ak in {'write','readwrite'} and mode in {'zp','zpx','zpy','indx','indy'}:
                    g['zp_write_candidates']+=1
            if off+3<=atlas.BANK_SIZE and b[off:off+3]==bytes.fromhex('20FBE7'):
                g['e7fb_bytepattern_candidates']+=1
    assert dict(g)==EXPECTED_GLOBAL,(dict(g),EXPECTED_GLOBAL)
    assert dict(focus)==EXPECTED_FOCUS,(dict(focus),EXPECTED_FOCUS)
    b31=prg[31*atlas.BANK_SIZE:32*atlas.BANK_SIZE]
    assert hashlib.sha256(b31).hexdigest()==EXPECTED_BANK31_SHA
    vectors={name:b31[o]|b31[o+1]<<8 for name,o in [('NMI',0x1FFA),('RESET',0x1FFC),('IRQ',0x1FFE)]}
    assert vectors==EXPECTED_VECTORS,(vectors,EXPECTED_VECTORS)
    print('ROM identity: OK',atlas.ROM_SHA)
    print('whole-PRG atlas candidate counts: OK',dict(g))
    print('focused candidate counts: OK',{f'${k:02X}':v for k,v in focus.items()})
    print('PRG31 hash/vectors: OK',EXPECTED_BANK31_SHA,{k:f'${v:04X}' for k,v in vectors.items()})
    print('NOTE: candidate counts are acceleration metadata, not verified code coverage')

if __name__=='__main__':
    if len(sys.argv)!=2: raise SystemExit('usage: audit_whole_prg_atlas.py ROM.nes')
    main(sys.argv[1])
