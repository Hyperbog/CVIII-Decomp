#!/usr/bin/env python3
"""JP0648: authenticate original Japanese 15 DMC command descriptors.

A real cartridge is read only with --rom and never copied or emitted.
--smoke uses invented descriptor values and deliberately damaged tables.
This verifies source byte windows and bounded driver structure, NOT
hardware DPCM audio playback, per-command game liveness or music ownership.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

JP_SHA = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
ROM_SIZE = 393232
PRG_BANK_0C = 12
BANK_SIZE = 16384
META_START = 0x8F60
META_END = 0x9541
DMC_START = 0xA957
DMC_END = 0xA993
PROGRAMS = 15
META_SHA = "ff50c2a4cd6273ca001535a5e319a68526b7e0b7a1ab173b2ced00f5a32f7154"
GUARD_SHA = "ffaacc4b3eb0372295e0402162915ebe6eacc8c8329678432de8472af0d62afd"
WRITER_SHA = "b6f771d46d16919b2a00a8505ad3a5ddca3cffc75ccaafe6750df524804dde70"
TABLE_SHA = "02d705700fcb42b0b1fa7c5520e54734f8180458265f1286aa132613b4fc6b45"
WRITES = (0x4015, 0x4010, 0x4011, 0x4012, 0x4013, 0x4015)

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def read(bank: bytes, start: int, end: int) -> bytes:
    if not 0x8000 <= start < end <= 0xC000 or len(bank) != BANK_SIZE:
        raise ValueError("invalid original PRG0C physical read")
    return bank[start - 0x8000:end - 0x8000]

def verify_bank(bank: bytes) -> bytes:
    if digest(read(bank, META_START, META_END)) != META_SHA:
        raise ValueError("original JP indexed sound metadata not authenticated")
    if digest(read(bank, 0x8908, 0x8954)) != GUARD_SHA:
        raise ValueError("original JP sound priority branch sequence mismatch")
    if digest(read(bank, 0x8928, 0x8954)) != WRITER_SHA:
        raise ValueError("original JP DMC register-write opcode source mismatch")
    table = read(bank, DMC_START, DMC_END)
    if digest(table) != TABLE_SHA:
        raise ValueError("original 15-entry DMC source table mismatch")
    for index in range(PROGRAMS):
        descriptor = int.from_bytes(read(bank, META_START+2*(110+index),
                                          META_START+2*(111+index)), "little")
        expected_ptr = 0x9505 + 4*index
        if index == 11:
            expected_ptr = 0x9531
        # Metadata descriptor addresses are indexed rather than ordered;
        # validation follows the original pointer, not a guessed order.
        if not 0x9505 <= descriptor <= 0x953D or (descriptor-0x9505)%4:
            raise ValueError("out-of-range special bank00 metadata descriptor")
        data = read(bank, descriptor, descriptor+4)
        if data[:2] != b"\x00\x09" or int.from_bytes(data[2:],"little") != DMC_START+4*index:
            raise ValueError("sound record ID does not link to DMC source slot")
    if len(table) != 60:
        raise ValueError("DMC table length changed")
    return table

def plan(table: bytes, command: int, old_priority: int) -> dict:
    if len(table) != 60 or not 0x6F <= command <= 0x7D or not 0 <= old_priority <= 255:
        raise ValueError("unsupported original bounded DMC input")
    index = command-0x6F
    denied = old_priority >= 5 and index < old_priority
    return {
        "command": command,
        "index": index,
        "counter_increment": index >= 13,
        "accepted": not denied,
        "priority_after": old_priority if denied else index,
        "register_writes": [] if denied else [
            (address, value) for address, value in zip(
                WRITES,(15,*table[4*index:4*index+4],31))],
    }

def enumerate_domain(table: bytes) -> dict:
    accepted = denied = incremented = 0
    for cmd in range(0x6F,0x7E):
        for old in range(256):
            event=plan(table,cmd,old)
            assert event["accepted"] == not (old>=5 and cmd-0x6F<old)
            if event["accepted"]:
                accepted+=1
                assert len(event["register_writes"])==6
            else:
                denied+=1
                assert not event["register_writes"]
            incremented+=event["counter_increment"]
    assert accepted+denied==3840 and incremented==512
    return {"programs":PROGRAMS,"tested_inputs":3840,"accepted_inputs":accepted,
            "rejected_inputs":denied,"counter_increment_inputs":incremented,
            "actual_gameplay_liveness_verified":False,
            "independent_music_sfx_playback_verified":False}

def smoke() -> None:
    fixture=bytes((i*7+3)&255 for i in range(60))
    report=enumerate_domain(fixture)
    for cmd in (0x6E,0x7E,0xFF):
        try:plan(fixture,cmd,0)
        except ValueError:pass
        else:raise AssertionError("out-of-table command was admitted")
    for size in (0,59,61):
        try:plan(fixture[:size] if size <= 60 else fixture+b"X",0x6F,0)
        except ValueError:pass
        else:raise AssertionError("wrong-sized source table was admitted")
    for bad in (-1,256):
        try:plan(fixture,0x6F,bad)
        except ValueError:pass
        else:raise AssertionError("wrong priority domain was admitted")
    # The original $06DD increment is BEFORE priority denial:
    # indices 13/14 may increment even when $019E rejects playback.
    for cmd in (0x7C,0x7D):
        p=plan(fixture,cmd,255)
        assert not p["accepted"] and p["counter_increment"] and not p["register_writes"]
    print("PASS JP0648 ROM-free bounded DMC command mapping,",
          report["tested_inputs"],"priority inputs and negative cases")

def verify_rom(path: Path) -> dict:
    rom=path.read_bytes()
    if len(rom)!=ROM_SIZE or digest(rom)!=JP_SHA:
        raise ValueError("only the exact original Japanese mapper24 ROM is supported")
    if rom[:4] != b"NES\x1a" or rom[4:6] != bytes((16,16)) or        ((rom[6]>>4) | (rom[7]&0xF0)) != 24:
        raise ValueError("invalid original mapper24 iNES header")
    start=16+PRG_BANK_0C*BANK_SIZE
    bank=rom[start:start+BANK_SIZE]
    table=verify_bank(bank)
    report=enumerate_domain(table)
    report.update({"schema":"CVIII-JP-original-DMC-source/v1",
                   "original_rom_sha256":JP_SHA,
                   "original_dmc_table_sha256":TABLE_SHA,
                   "table_cpu_range":"A957-A992",
                   "driver_cpu_range":"8908-8953",
                   "validated_source_only":True})
    # Corrupt each independent authenticated source category; no private
    # ROM, DPCM sample or sound byte payload is ever serialized to Git.
    for address in (0x8908,0x8928,0x8F60,0x9505,0xA957,0xA992):
        damaged=bytearray(bank)
        damaged[address-0x8000]^=1
        try:verify_bank(bytes(damaged))
        except ValueError:pass
        else:raise AssertionError("modified original source was accepted")
    return report

def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--smoke",action="store_true")
    ap.add_argument("--rom",type=Path)
    ap.add_argument("--json",type=Path,help="owner-private summary, no ROM sound data")
    args=ap.parse_args()
    if not args.smoke and not args.rom:
        ap.error("provide --smoke or --rom ORIGINAL_JP")
    if args.smoke:smoke()
    if args.rom:
        result=verify_rom(args.rom)
        if args.json:
            args.json.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",
                                 encoding="utf-8")
        print("PASS JP0648 authenticated original Japanese 15 DMC programs,",
              result["tested_inputs"],"guard combinations and six tamper cases")

if __name__=="__main__":
    main()
