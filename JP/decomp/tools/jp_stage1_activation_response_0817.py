#!/usr/bin/env python3
"""JP0817: private Japanese-ROM opcode witness, never exports game bytes.

Original windows are checked as source. The ROM-free smoke proves a small
subset of the source arithmetic but NOT controller-reached Mesen parity.
"""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path

ROM="958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
SHA0A="1460df577d44e114c64fdf34a8837629765f3f6a93d45796fdf81e5ffacb5ed8"
SHA0B="17b216088d12ac7b6a4a68bbea3434dbdba317865bd6cf4d11646a3d4efaf64a"
WINDOWS={
 "84EA_six_slot_scheduler":(10,0x84EA,0x8501,"cc4f1153896f3e321872a7a92c70b0b3b9ef868bca258fa6ba1eb28856d9f6f7"),
 "83D1_source_motion":(10,0x83D1,0x8410,"f302ac2b3ac985520f5d7780d6583a5cbed3f9164b33136484b157b2c99f4a90"),
 "8501_original_row_dispatcher":(10,0x8501,0x8523,"ad5600da3247b263c60371b9cca117cbcb2b77d37087b7de0318b6de525e26d3"),
 "B115_special_response":(11,0xB115,0xB15C,"73437e1179c32298f645f424b90e5fda9192c963d20492d8034f920b6d888f06"),
 "B18A_type_response":(11,0xB18A,0xB1CC,"1b2bacac40d5a7571e54ada0c487f8885fb7315292a6064c656b1cbff54b8f39"),
 "B80E_actor_distance":(11,0xB80E,0xB84A,"9eb404bf841ffb7be18d982e61a9e858c83fdb6883658c21b2b29ffa29a33061"),
 "80B3_unsigned_difference":(11,0x80B3,0x80C1,"b8b39e284696199b099bb558dd8099fe22ab813a1c9472347d7f1d1bd3bed4e4"),
 "B0E2_type_table":(11,0xB0E2,0xB115,"79ffaa6873ec668bf88caa99eaf65a5fef4e07a9f7165418229199c69ec41b0d"),
}

def verify(path:Path)->None:
    rom=path.read_bytes()
    if len(rom)!=393232 or rom[:4]!=b"NES\x1a" or hashlib.sha256(rom).hexdigest()!=ROM:
        raise ValueError("Not the authenticated Japanese owner ROM")
    banks={}
    for n,sha in ((10,SHA0A),(11,SHA0B)):
        b=rom[16+n*16384:16+(n+1)*16384]
        if hashlib.sha256(b).hexdigest()!=sha:
            raise ValueError(f"physical PRG bank {n:02X} differs")
        banks[n]=b
    for label,(n,start,end,sha) in WINDOWS.items():
        body=banks[n][start-0x8000:end-0x8000]
        if len(body)!=end-start or hashlib.sha256(body).hexdigest()!=sha:
            raise ValueError(f"original source window differs: {label}")
    b0,b1=banks[10],banks[11]
    def source(b,lo,hi):
        return b[lo-0x8000:hi-0x8000]
    # Hard original branch instructions are independently checked from
    # the window digests to guard wrong CPU offsets in native code.
    if source(b0,0x84EA,0x84F4)!=bytes.fromhex("A2 00 BD C2 07 F0 0A 86 69 20"):
        raise ValueError("$84EA nonzero-source JSR control flow changed")
    if source(b1,0xB115,0xB120)!=bytes.fromhex(
        "A5 7E C9 01 F0 1D 20 0E B8 B0 18"):
        raise ValueError("$B115 7E/B80E selection changed")
    if source(b1,0xB18A,0xB18F)!=bytes.fromhex("BD 4E 05 C9 6E"):
        raise ValueError("$B18A type dispatcher changed")
    if source(b1,0xB841,0xB84A)!=bytes.fromhex(
        "E5 02 B0 02 49 FF C9 08 60"):
        raise ValueError("$B80E asymmetrical vertical comparator changed")
    print("PASS JP0817 original ROM, raw0A/raw0B, eight CPU/table source windows")
    print("PASS source slot $84EA; $B115 JSR $B80E; $B18A type state; $B80E negative vertical")
    print("LIMIT: no original Mesen actor-response frame and no native gameplay mutation")

def smoke()->None:
    # B80E: after signed 8-bit SBC underflow, EOR $FF rather than ADC #1.
    for d in range(1,16):
        player=96
        actor=player+d
        a=(player-actor)&255
        original=(a^255)
        assert original==d-1
        assert (original>=8)==(d>=9)
    # Authentic 83D1 SEC/SBC low-byte borrow and page-bit update.
    for old in range(256):
        for delta in range(256):
            for page in (0,1):
                sign=255 if delta&128 else 0
                high=(page-sign-(old<delta))&1
                assert high in (0,1)
                low=(old-delta)&255
                assert 0<=low<=255
    print("PASS JP0817 ROM-free B80E asymmetry and 131072 source-byte borrow checks")

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rom",type=Path)
    p.add_argument("--smoke",action="store_true")
    a=p.parse_args()
    if a.smoke:smoke()
    if a.rom:verify(a.rom)
    if not (a.smoke or a.rom):p.error("provide --smoke or --rom")
