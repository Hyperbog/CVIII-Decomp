#!/usr/bin/env python3
"""Recomp owner-ROM level layout source inventory.

Extracts NO game tiles, palettes, or actor entries into repo/distributable
assets. Enumerates uniquely parseable *candidate* contiguous metatile
layout blocks preceding the known 4x4 TSA regions. Only the eight Wallachia
layout headers have an independently verified room-selector mapping.
Others are explicitly NOT drawable/assigned NPC entities by this tool.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass, asdict
from functools import lru_cache
import hashlib
import json
from pathlib import Path

ROM_SHA256 = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
ROM_SIZE = 393232
# Source regions physically ordered. Inclusive ROM offsets.
TSA_REGIONS = (
    ("Catacombs", 0x182D0, 0x187CF, 80),
    ("Abandoned Mines", 0x18EDB, 0x19EDA, 256),
    ("Main Hall", 0x1A2FB, 0x1A8FA, 96),
    ("Inner Hall", 0x1AC9A, 0x1B269, 93),
    ("Castle Keep", 0x1B592, 0x1BD51, 124),
    ("Causeway", 0x1C459, 0x1C9B8, 86),
    ("Swamp", 0x1CD94, 0x1D143, 59),
    ("Alucard's Cave", 0x1D78E, 0x1DD8D, 96),
    ("Sunken City", 0x1E3BE, 0x1E9BD, 96),
    ("Lookout Tower", 0x1EDFA, 0x1F3C9, 93),
    ("Wallachia", 0x20451, 0x20D60, 145),
    ("Clocktower", 0x2141A, 0x21965, 0),  # malformed definition span
    ("Forest", 0x22120, 0x2263F, 82),
    ("Ghost Ship", 0x22C7D, 0x232BC, 100),
    ("Tower", 0x23737, 0x23BB6, 72),
)
# Exactly eight independently validated Stage 1 layout headers, source order.
WALLACHIA_HEADERS = (
    0x20039, 0x200BA, 0x2014B, 0x2017C,
    0x201DD, 0x2026E, 0x202FF, 0x20390,
)
MAX_RECORDS = 64
MAX_PATHS_REPORTED = 2

@dataclass(frozen=True)
class Record:
    header_offset: int
    screens: int
    metatiles_per_screen: int
    bytes: int
    sha256: str

def longest_chains(source: bytes, before: int, after: int,
                   max_tile_index: int) -> tuple[int, list[tuple[tuple[int,int,int], ...]]]:
    """Dynamic programming for contiguous 1+48*n or 1+64*n layout sequences.
    Returns longest length and up to two distinct paths; ambiguity fails closed.
    """
    if not (0 <= before <= after <= len(source)) or max_tile_index <= 0:
        return 0, []
    @lru_cache(maxsize=None)
    def walk(end: int) -> tuple[int, tuple[tuple[tuple[int,int,int],...],...]]:
        best_count, best = 0, ((),)
        for screens in range(1,5):
            for tiles_per in (48,64):
                start = end - 1 - screens*tiles_per
                if start < before or source[start] != screens-1:
                    continue
                if any(idx >= max_tile_index for idx in source[start+1:end]):
                    continue
                prev_count, prev_paths = walk(start)
                score = prev_count+1
                paths = tuple(p+((start,screens,tiles_per),) for p in prev_paths)
                if score > best_count:
                    best_count, best = score, paths[:MAX_PATHS_REPORTED]
                elif score == best_count:
                    best = (best + paths)[:MAX_PATHS_REPORTED]
        return best_count, best
    n, paths = walk(after)
    return n, [p for p in paths if p]

def validate_original(data: bytes) -> None:
    if len(data) != ROM_SIZE or hashlib.sha256(data).hexdigest() != ROM_SHA256:
        raise ValueError("owner Japanese ROM SHA-256/length mismatch")
    if data[:4] != b"NES\x1a" or data[4:6] != bytes((16,16)):
        raise ValueError("iNES size/header mismatch")
    if data[6] >> 4 | (data[7] & 0xF0) != 24:
        raise ValueError("not Japanese Mapper24")

def inventory(data: bytes) -> dict:
    validate_original(data)
    rows=[]
    previous_end = 0x1800F
    for name, start, end, patterns in TSA_REGIONS:
        if name == "Wallachia": previous_end = 0x2000F
        if start <= previous_end or end >= len(data):
            raise ValueError("overlapping TSA source bounds")
        if patterns == 0:
            rows.append(dict(region=name, status="unsupported_tsa_span",
                             layout_count=0, candidate_records=[],
                             note="4x4 TSA source byte count is not divisible by 16"))
        else:
            if end-start+1 != patterns*16:
                raise ValueError("incorrect named TSA source span")
            n, paths=longest_chains(data,previous_end+1,start,patterns)
            unique=len(paths)==1
            if name == "Wallachia":
                expected = tuple(x[0] for x in paths[0]) if unique else ()
                if n != 8 or expected != WALLACHIA_HEADERS:
                    raise ValueError("known Stage 1 layout source headers drifted")
                status="known_stage1_layouts"
            elif not unique:
                status="absent_or_ambiguous_layout_prefix"
            else:
                status="unassigned_structural_candidates"
            candidate = []
            if unique:
                for addr, screens, width in paths[0]:
                    length=1+screens*width
                    candidate.append(asdict(Record(
                        header_offset=addr,screens=screens,
                        metatiles_per_screen=width,bytes=length,
                        sha256=hashlib.sha256(data[addr:addr+length]).hexdigest()
                    )))
            rows.append(dict(region=name,status=status,layout_count=n,
                             candidate_records=candidate,
                             candidate_paths_seen=min(2,len(paths)),
                             verified_room_mapping=(name=="Wallachia"),
                             palettes_verified=(name=="Wallachia")))
        previous_end=end
    return dict(schema="cviii-recomp-source-layout-inventory/v1",
                original_rom_sha256=ROM_SHA256,
                source_regions=rows,
                known_original_stage1_layout_count=8,
                complete_stage_widescreen_verified=False,
                npc_item_spawn_types_identified=False,
                game_logic_modified=False,
                message="Only Stage1 has authenticated room-key map; other candidates are not scene maps.")

def self_test():
    data=bytearray([255]*2048)
    # Three contiguous blocks; 2 horizontal 48-mt and 1 vertical 64-mt.
    at=401
    specs=((2,48),(1,64),(3,48))
    for screens,unit in specs:
        data[at]=screens-1
        data[at+1:at+1+screens*unit]=bytes([7])*(screens*unit)
        at+=1+screens*unit
    count, paths=longest_chains(data,400,at,32)
    assert count==3 and len(paths)==1 and paths[0][0][0]==401
    assert len(paths[0])==3
    count, paths=longest_chains(data,400,at,7)
    assert count==0 and paths==[]
    print("PASS: strict private-ROM gate; source-chain parser accepts only tile-range-safe chains")

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rom",type=Path)
    p.add_argument("--out",type=Path,help="private local metadata JSON (no game pixels)")
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if args.self_test:
        self_test()
        return
    if not args.rom: p.error("--rom required unless --self-test")
    result=inventory(args.rom.read_bytes())
    encoded=json.dumps(result,indent=2)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(encoded,encoding="utf-8")
    else: print(encoded,end="")

if __name__=="__main__":
    try: main()
    except (ValueError,OSError) as e:
        raise SystemExit("CVIII recomp layout inventory: "+str(e))
