#!/usr/bin/env python3
"""JP0654: private original JP cartridge versus ripped VRC6 NSF provenance.

ROM/NSF/ZIP bytes are read-only. The JSON contains aggregate provenance,
not music payloads, executable game bytes or per-song original-ROM IDs.
NSF $5FF8-5FFF 4KiB banks are NOT VRC6 cartridge PRG bank registers.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import struct
import zipfile
from pathlib import Path

ROM_SHA = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
NSF_SHA = "302b79d8b2df9cb7fe94936feca6582cc35294844a93325c9bbfbb37d8e98008"
M3U_SHA = "48b75d2df330c569a393e0aacfd22c453783bc3b1e5f31b826f30a3721bb85ae"
ROM_BYTES = 393232
NSF_BYTES = 53376
PRG_OFFSET, PRG_BYTES, NSF_OFFSET, BANK_BYTES = 16, 262144, 128, 4096
# Each source is an ORIGINAL PHYSICAL 4KiB PRG offset / $1000,
# not a mapper bank selected at runtime.
ORIGINAL_4K_BANKS = (16, 17, 18, 19, 20, 21, 22, 23, 48, 49, 50, 14, 15)
REPLACED = {10: (0x000, 0x300), 12: (0xFF0, 0x1000)}
NSF_INIT_BANKS = bytes((0, 0, 0, 0, 11, 12, 10, 10))


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(condition: bool, problem: str) -> None:
    if not condition:
        raise ValueError(problem)


def header(nsf: bytes) -> dict:
    require(len(nsf) == NSF_BYTES and nsf[:5] == b"NESM\x1a",
            "incorrect 128-byte header or 13-bank NSF length")
    version, songs, first = nsf[5:8]
    load, init, play = struct.unpack_from("<HHH", nsf, 8)
    ntsc = struct.unpack_from("<H", nsf, 0x6E)[0]
    pal = struct.unpack_from("<H", nsf, 0x78)[0]
    require((version, songs, first, load, init, play) ==
            (1, 28, 1, 0x8000, 0xE0E0, 0xE0D0),
            "unexpected rip version, track count or entry addresses")
    require((ntsc, pal, nsf[0x7A], nsf[0x7B], nsf[0x7C]) ==
            (0x4100, 0, 0, 1, 0),
            "unexpected NTSC region, VRC6 expansion bit or NSF2 features")
    require(nsf[0x70:0x78] == NSF_INIT_BANKS,
            "NSF $5FF8-$5FFF startup bank map changed")
    require(nsf[0x7D:0x80] == b"\0\0\0", "unexpected NSF1 extension")
    return {"format_version":version,"tracks":songs,"first_track":first,
            "load_address":f"{load:04X}","init_address":f"{init:04X}",
            "play_address":f"{play:04X}",
            "ntsc_period_microseconds":ntsc,"pal_period_microseconds":pal,
            "ntsc_only":True,"vrc6_audio_flag":True,
            "nsf_4k_initial_banks":list(NSF_INIT_BANKS)}


def playlist(m3u: bytes) -> int:
    require(len(m3u) < 65536, "playlist unexpectedly large")
    try:
        lines=m3u.decode("utf-8-sig").splitlines()
    except UnicodeError as exc:
        raise ValueError("playlist is not UTF-8") from exc
    entries=[]
    for line in lines:
        if "::NSF," in line and not line.startswith("#"):
            parts=line.split("::NSF,",1)[1].split(",",2)
            require(len(parts)>=2 and parts[0].isdigit() and bool(parts[1]),
                    "malformed numbered NSF playlist row")
            entries.append(int(parts[0]))
    require(len(entries)==28 and sorted(entries)==list(range(1,29)),
            "playlist must identify 28 distinct 1-based songs")
    return len(entries)


def archive(path: Path) -> tuple[bytes, bytes]:
    # Deliberately never extract user-controlled archive paths to disk.
    try:
        with zipfile.ZipFile(path) as zf:
            members=[z for z in zf.infolist() if not z.is_dir()]
            require(len(members)==2 and all(0<z.file_size<1000000 for z in members),
                    "expected only a bounded NSF and M3U")
            nsfs=[z for z in members if z.filename.lower().endswith(".nsf")]
            playlists=[z for z in members if z.filename.lower().endswith(".m3u")]
            require(len(nsfs)==len(playlists)==1,
                    "archive must contain exactly one NSF and one M3U")
            return zf.read(nsfs[0]), zf.read(playlists[0])
    except (OSError, zipfile.BadZipFile) as exc:
        raise ValueError("invalid NSF archive") from exc


def crosswalk(rom: bytes, nsf: bytes, m3u: bytes | None, *, authentic: bool) -> dict:
    require(len(rom)==ROM_BYTES and rom[:4]==b"NES\x1a" and
            rom[4:6]==b"\x10\x10" and
            ((rom[6]>>4)|(rom[7]&0xF0))==24,
            "wrong Japanese original Mapper24 cartridge geometry")
    if authentic:
        require(digest(rom)==ROM_SHA and digest(nsf)==NSF_SHA,
                "unexpected original Japanese ROM or source NSF identity")
        if m3u is not None:
            require(digest(m3u)==M3U_SHA, "unexpected NSF playlist identity")
    nheader=header(nsf)
    count=playlist(m3u) if m3u is not None else None
    prg=rom[PRG_OFFSET:PRG_OFFSET+PRG_BYTES]
    payload=nsf[NSF_OFFSET:]
    require(len(payload)==13*BANK_BYTES,"truncated NSF payload")
    unmodified=0
    actual_changed=0
    entries=[]
    for rip_bank,orig_bank in enumerate(ORIGINAL_4K_BANKS):
        source=prg[orig_bank*BANK_BYTES:(orig_bank+1)*BANK_BYTES]
        dest=payload[rip_bank*BANK_BYTES:(rip_bank+1)*BANK_BYTES]
        require(len(source)==len(dest)==BANK_BYTES,"source bank incomplete")
        lo,hi=REPLACED.get(rip_bank,(0,0))
        require(dest[:lo]==source[:lo] and dest[hi:]==source[hi:],
                f"NSF bank {rip_bank} changed authenticated data outside rip overlay")
        diff=sum(a!=b for a,b in zip(dest[lo:hi],source[lo:hi]))
        if authentic and rip_bank in REPLACED:
            require(diff=={10:759,12:16}[rip_bank],
                    "NSF rip-overlay modification signature drift")
        actual_changed+=diff
        unmodified+=BANK_BYTES-(hi-lo)
        entries.append({"nsf_bank4":rip_bank,"original_prg_bank4":orig_bank,
                        "original_prg_offset":orig_bank*BANK_BYTES,
                        "unaltered_bytes_outside_overlay":BANK_BYTES-(hi-lo),
                        "overlay_offset_start":lo if hi>lo else None,
                        "overlay_offset_end_exclusive":hi if hi>lo else None,
                        "changed_byte_count":diff})
    require(unmodified==52464,"proven source preservation census changed")
    if authentic:
        require(actual_changed==775, "rip modification count changed")
    # The 148 pointer words and 1323 phrase-pool bytes are copied exactly:
    # raw0C:$A304-$A956 => NSF bank 10 from offset $304 onward.
    phrase=prg[50*BANK_BYTES+0x304:50*BANK_BYTES+0x957]
    phrase_nsf=payload[10*BANK_BYTES+0x304:10*BANK_BYTES+0x957]
    require(phrase==phrase_nsf and len(phrase)==1619,
            "JP0653 original phrase pointer/stream bytes are not preserved")
    # JP0648 original DMC parameter bytes at raw0C $A957-$A992.
    require(prg[50*BANK_BYTES+0x957:50*BANK_BYTES+0x993] ==
            payload[10*BANK_BYTES+0x957:10*BANK_BYTES+0x993],
            "original JP 15 DMC descriptors changed in ripped NSF")
    return {"schema":"CVIII-JP-NSF-crosswalk/1",
            "status":"static_rip_provenance_not_original_gameplay_parity",
            "original_rom_sha256":ROM_SHA if authentic else None,
            "nsf_sha256":NSF_SHA if authentic else None,
            "m3u_sha256":M3U_SHA if authentic and m3u is not None else None,
            "header":nheader,"playlist_tracks":count,
            "source_bank_count":len(entries),
            "nsf_payload_bytes":len(payload),
            "exact_4k_banks":sum(e["changed_byte_count"]==0 for e in entries),
            "provably_untouched_bytes_outside_overlays":unmodified,
            "patch_region_bytes":len(payload)-unmodified,
            "actual_differing_bytes":actual_changed,
            "sound_directory_8F60_9540_preserved":True,
            "phrase_A304_A956_preserved":True,
            "dmc_A957_A992_preserved":True,
            "original_stream_A000_A2FF_replaced_in_rip":True,
            "track_to_original_sound_ID_mapping_verified":False,
            "original_nes_mapper_state_verified":False,
            "nsf_4k_to_original_prg":entries}


def fixture() -> tuple[bytes, bytes, bytes]:
    rom=bytearray(ROM_BYTES)
    rom[:16]=bytes.fromhex("4e45531a101080100000000000000000")
    for block in range(PRG_BYTES//BANK_BYTES):
        start=PRG_OFFSET+block*BANK_BYTES
        rom[start:start+BANK_BYTES]=bytes((i*7+block*13)&255 for i in range(BANK_BYTES))
    header=bytearray(128)
    header[:8]=b"NESM\x1a\x01\x1c\x01"
    struct.pack_into("<HHH",header,8,0x8000,0xE0E0,0xE0D0)
    struct.pack_into("<H",header,0x6E,0x4100)
    header[0x70:0x78]=NSF_INIT_BANKS
    header[0x7B]=1
    payload=bytearray(b"".join(rom[PRG_OFFSET+block*BANK_BYTES:PRG_OFFSET+(block+1)*BANK_BYTES]
                               for block in ORIGINAL_4K_BANKS))
    for rip,(lo,hi) in REPLACED.items():
        for k in range(lo,hi):
            payload[rip*BANK_BYTES+k]^=0x5A
    m3u=("# Synthetic track index only\n"+
         "".join(f"fixture.nsf::NSF,{i},Synthetic {i},0:00:01\n" for i in range(1,29))).encode()
    return bytes(rom),bytes(header+payload),m3u


def smoke() -> None:
    rom,nsf,m3u=fixture()
    result=crosswalk(rom,nsf,m3u,authentic=False)
    require(result["actual_differing_bytes"]==784 and result["source_bank_count"]==13,
            "synthetic differential test mismatch")
    # Normal in-memory ZIP roundtrip; no archive extraction.
    mem=io.BytesIO()
    with zipfile.ZipFile(mem,"w") as z:
        z.writestr("sound.nsf",nsf)
        z.writestr("sound.m3u",m3u)
    with zipfile.ZipFile(io.BytesIO(mem.getvalue())) as z:
        require(z.read("sound.nsf")==nsf,"synthetic ZIP NSF mismatch")
    invalid=[]
    for offset in (NSF_OFFSET, NSF_OFFSET+10*BANK_BYTES+0x300,
                   NSF_OFFSET+12*BANK_BYTES+0xFEF,0x7B,0x70,8):
        b=bytearray(nsf);b[offset]^=1
        invalid.append((rom,bytes(b),m3u))
    invalid.append((rom,nsf,m3u.replace(b"::NSF,1,",b"::NSF,2,")))
    invalid.append((rom[:-1],nsf,m3u))
    for data in invalid:
        try:crosswalk(*data,authentic=False)
        except ValueError:continue
        raise AssertionError("invalid artificial NSF/ROM/playlist accepted")
    require(playlist(m3u)==28,"synthetic playlist index")
    print("PASS JP0654 13 physical 4KiB source banks, 2 rip overlays, 28 tracks and 8 negative cases")


def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rom",type=Path)
    group=ap.add_mutually_exclusive_group()
    group.add_argument("--nsf",type=Path)
    group.add_argument("--archive",type=Path)
    ap.add_argument("--m3u",type=Path,help="playlist paired with --nsf")
    ap.add_argument("--json",type=Path,help="metadata-only owner-local report")
    ap.add_argument("--smoke",action="store_true")
    args=ap.parse_args()
    if args.smoke:smoke()
    if args.rom:
        if not args.nsf and not args.archive:
            ap.error("provide --nsf or --archive with --rom")
        if args.archive:
            if args.m3u:ap.error("--m3u is part of --archive")
            nsf,m3u=archive(args.archive)
        else:
            nsf=args.nsf.read_bytes()
            m3u=args.m3u.read_bytes() if args.m3u else None
        result=crosswalk(args.rom.read_bytes(),nsf,m3u,authentic=True)
        if args.json:
            args.json.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        print("PASS JP0654 original-JP NSF crosswalk: 13 source banks; 52464 bytes outside rip overlays unchanged; 775 altered bytes")
    elif not args.smoke:
        ap.error("provide --smoke or --rom ORIGINAL_JP and --nsf/--archive")


if __name__=="__main__":
    main()
