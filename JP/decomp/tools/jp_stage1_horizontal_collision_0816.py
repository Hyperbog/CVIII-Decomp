#!/usr/bin/env python3
"""JP0816: original Stage1 horizontal resource / B1F8 route auditor.

Owner-ROM-only; public output is aggregate/provenance, never raw game data.
ROM-free smoke checks only the arithmetic, not original gameplay liveness.
"""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path

ROM = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
BANK0A = "1460df577d44e114c64fdf34a8837629765f3f6a93d45796fdf81e5ffacb5ed8"
BANK0B = "17b216088d12ac7b6a4a68bbea3434dbdba317865bd6cf4d11646a3d4efaf64a"
ROOMS = {
    (0, 0, 0): (0x93CC, 28),
    (0, 1, 0): (0x93E8, 12),
    (0, 1, 2): (0x93F4, 28),
    (0, 1, 3): (0x9410, 20),
    (0, 2, 0): (0x9424, 28),
    (0, 2, 1): (0x9440, 28),
    (0, 3, 0): (0x945C, 28),
}
WINDOWS = {
    "raw0A_8001_801D": (0, 0x8001, 0x801E,
      "a5bfb0b51b7d7e50ec5dbc1fd882490136b49e0d91f9245aa06dea86aa19a6bb"),
    "raw0A_80D1_8107": (0, 0x80D1, 0x8108,
      "73e0e407e4a2151a9af018b41f000e7ab4fd4d6693fccd594cef6cc29b7ac014"),
    "raw0B_B1F8_B231": (1, 0xB1F8, 0xB232,
      "1a3b482dca0425a679df117a9330247c727042eb6d4b71fae32092b837956356"),
    "raw0B_B162_B189": (1, 0xB162, 0xB18A,
      "fa1ab040d2151a4f57e853fdcac07a1b6cc479e57841f7d35907afb38e205249"),
    "raw0B_B634_B672": (1, 0xB634, 0xB673,
      "7fb2a283cdf0c3a7a372286b91a4e9d4d2a7395d9641d5c8a8295e791bd1930c"),
}

def require(pred: bool, message: str) -> None:
    if not pred:
        raise ValueError(message)

def byte(bank: bytes, cpu: int) -> int:
    require(0x8000 <= cpu <= 0xBFFF, "original raw PRG pointer escaped")
    return bank[cpu - 0x8000]

def word(bank: bytes, cpu: int) -> int:
    return byte(bank, cpu) | byte(bank, cpu + 1) << 8

def phase(camera16: int, direction62: int) -> int:
    """Original $8001 high-byte ASL/ROL*2 + $80D1 $62 add5."""
    return (((((camera16 + 2) & 65535) >> 6) & 255) + (5 if direction62 else 0)) & 255

def event_ptr(bank: bytes, source_id: int, flag07f6: int) -> int:
    a=(source_id << 1) & 255
    fallback = source_id >= 0x80 and not flag07f6 and a >= 0xA0
    table=0xA06E if source_id >= 0x80 and not fallback else 0x9F6E
    return word(bank, table + (0 if fallback else a))

def auxiliary_ptr(bank: bytes, source_id: int) -> int:
    table=0xA66B if source_id >= 0x80 else 0xA56B
    return word(bank, table + ((source_id << 1) & 255))

def audit(rom: bytes) -> None:
    require(len(rom)==393232 and rom[:4]==b"NES\x1a" and
            hashlib.sha256(rom).hexdigest()==ROM,
            "wrong original Japanese retail ROM")
    b0=rom[16+10*16384:16+11*16384]
    b1=rom[16+11*16384:16+12*16384]
    require(hashlib.sha256(b0).hexdigest()==BANK0A, "raw0A hash failed")
    require(hashlib.sha256(b1).hexdigest()==BANK0B, "raw0B hash failed")
    for label,(bank,start,end,h) in WINDOWS.items():
        source=(b0,b1)[bank][start-0x8000:end-0x8000]
        require(hashlib.sha256(source).hexdigest()==h,
                f"authenticated original CPU source changed: {label}")
    counts=[]
    total_event_ids=0
    total_aux_ids=0
    for key,(root,size) in ROOMS.items():
        t1=word(b0,0x92AE+2*key[0])
        t2=word(b0,t1+2*key[1])
        original=word(b0,t2+2*key[2])
        require(original==root,"source root is not from original $801E path")
        payload=b0[root-0x8000:root-0x8000+size]
        require(len(payload)==size and size%4==0, "invalid 4-byte cells")
        for off in range(0,size,2):
            sid,aid=payload[off:off+2]
            for f6 in (0,1):
                ptr=event_ptr(b0,sid,f6)
                require(0x8000<=ptr<=0xBFFB,"invalid original event pointer")
                _=byte(b0,ptr)
            if sid:total_event_ids+=1
            if aid:
                ptr=auxiliary_ptr(b0,aid)
                require(0x8000<=ptr<=0xBFFC,"invalid original auxiliary pointer")
                _=byte(b0,ptr)
                total_aux_ids+=1
        counts.append((key,size//2))
    # Source ID $D1 in the first 768px room is only an event if $07F6!=0.
    opening=b0[0x93CC-0x8000:0x93CC-0x8000+28]
    sid,aid=opening[10:12]
    require((sid,aid)==(0xD1,0x46),"opening cell5 identity failed")
    low=byte(b0,event_ptr(b0,sid,0))
    high=byte(b0,event_ptr(b0,sid,1))
    direct=byte(b0,auxiliary_ptr(b0,aid))
    require((phase(318,0),phase(318,1),low,high,direct)==
            (5,10,0,2,0x80),"original conditional source classification failed")
    # Original $B1F8: attribute mask or empty frame, $83+ early return,
    # $80-$82 to $B258 *before* $B217; $B162 is for $69-$7F.
    require(b1[0xB20B-0x8000:0xB20F-0x8000]==bytes.fromhex("C9 80 B0 49"),
            "original type80 $B258 bypass opcode changed")
    require(b1[0xB21D-0x8000:0xB227-0x8000]==
            bytes.fromhex("BD 4E 05 C9 69 90 03 4C 62 B1"),
            "$B162 entry prerequisite changed")
    print("PASS original JP ROM and two physical bank fingerprints")
    print("PASS original $8001/$80D1, $B1F8/$B162/$B634 hashes")
    print("Original horizontal pairs:",sum(x[1] for x in counts),
          "; nonzero event IDs:",total_event_ids,
          "; nonzero auxiliary IDs:",total_aux_ids)
    for k,n in counts:
        print("stage/room/section", "/".join(str(v) for v in k), "pairs",n)
    print("PASS opening phase5: $D1/$46 -> row00 or row02 by $07F6; auxiliary type80")
    print("PASS $80 B1F8->$B258, not $B162; B634 effects not simulated")

def smoke() -> None:
    for c in range(0,65536,37):
        actual=phase(c,0)
        expect=(((c+2)&0xffff)>>6)&0xff
        require(actual==expect and phase(c,1)==((expect+5)&255),
                "16-bit camera high-byte rotate arithmetic error")
    require(phase(318,0)==5 and phase(318,1)==10,
            "opening room source rotation sample changed")
    print("PASS ROM-free original source phase and 8-bit wrap smoke")

def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rom",type=Path)
    p.add_argument("--smoke",action="store_true")
    a=p.parse_args()
    if a.smoke:smoke()
    if a.rom:audit(a.rom.read_bytes())
    if not (a.smoke or a.rom):p.error("provide --smoke or --rom")

if __name__=="__main__":
    main()
