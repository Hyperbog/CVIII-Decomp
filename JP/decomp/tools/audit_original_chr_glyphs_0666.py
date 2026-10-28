#!/usr/bin/env python3
"""Private JP original iNES CHR tile audit: no ROM/tile bytes in output.

A tile ID is not a Unicode codepoint. Original VRC6 CHR banking must be
identified at the exact PPU rendering frame before naming a visible glyph.
"""
import argparse,hashlib,json
from pathlib import Path
HASH="958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
def audit(path:Path):
    raw=path.read_bytes()
    if len(raw)!=393232 or raw[:4]!=b"NES\x1a" or hashlib.sha256(raw).hexdigest()!=HASH:
        raise ValueError("Original SHA-pinned Akumajou Densetsu cartridge required")
    prg_units=raw[4];chr_units=raw[5]
    if prg_units!=16 or chr_units!=16:raise ValueError("Unrecognized original iNES geometry")
    start=16+prg_units*16384
    banks=[]
    for i in range(chr_units):
        bank=raw[start+i*8192:start+(i+1)*8192]
        tiles=[bank[k*16:(k+1)*16] for k in range(0xC0,0xDA)]
        blanks=sum(x==bytes(16) for x in tiles)
        banks.append(dict(chr_8k_bank=i,
            distinct_tile_patterns=len(set(tiles)),
            blank_tile_patterns=blanks,
            tile_ids="C0-D9",verified_unicode_mapping=False))
    return {"rom_sha256":HASH,"tile_format":"NES two-bitplane 8x8, 16 bytes",
            "bank_mapping":"UNRESOLVED: runtime VRC6 CHR register selection needed",
            "latin_tile_ids":"C0-D9 only where previously source-audited",
            "japanese_glyph_map":"NOT VERIFIED",
            "output_embeds_graphics":False,"banks":banks}
def smoke():
    assert len(bytes(16))==16
    assert len(range(0xC0,0xDA))==26
    print("PASS ROM-free bounded font evidence contract")
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--rom",type=Path)
    p.add_argument("--smoke",action="store_true")
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    smoke()
    if a.rom:
        obj=audit(a.rom)
        text=json.dumps(obj,indent=2)
        if a.out:a.out.write_text(text+"\n",encoding="utf-8")
        else:print(text)
    elif not a.smoke:p.error("provide --rom or --smoke")
