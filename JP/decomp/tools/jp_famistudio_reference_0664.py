#!/usr/bin/env python3
"""JP0664: authenticated local NSF provenance + bounded FamiStudio TXT census.

Reference data only. Never exports notes, ROM bytes, samples, or synthesis.
The FamiStudio TXT comes from external tooling and CANNOT independently
attest original-game command IDs, gameplay liveness, or waveform parity.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import struct

ROM_SHA = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
NSF_SHA = "302b79d8b2df9cb7fe94936feca6582cc35294844a93325c9bbfbb37d8e98008"
M3U_SHA = "48b75d2df330c569a393e0aacfd22c453783bc3b1e5f31b826f30a3721bb85ae"
CHANNELS = ("Square1", "Square2", "Triangle", "Noise", "DPCM", "VRC6Square1", "VRC6Square2", "VRC6Saw")
ATTR = re.compile(r'([A-Za-z][A-Za-z0-9]*)="([^"\r\n]*)"')
MAX_TXT = 16 * 1024 * 1024


def check(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def source_identity(rom: bytes, nsf: bytes, m3u: bytes | None, track: int) -> dict:
    check(len(rom) == 393232 and sha(rom) == ROM_SHA, "Japanese ROM SHA/size mismatch")
    check(len(nsf) == 53376 and sha(nsf) == NSF_SHA, "NSF SHA/size mismatch")
    check(m3u is None or sha(m3u) == M3U_SHA, "M3U SHA mismatch")
    check(rom[:4] == b"NES\x1a" and nsf[:5] == b"NESM\x1a", "original header mismatch")
    check(nsf[5] == 1 and nsf[6] == 28 and nsf[7] == 1, "unexpected NSF track declaration")
    check(nsf[0x7b] & 1, "VRC6 flag missing")
    check(struct.unpack_from("<HHH", nsf, 8) == (0x8000, 0xE0E0, 0xE0D0), "NSF entry points changed")
    check(track == 0, "JP0664 currently scopes only zero-based index 0 (Beginning)")
    if m3u is not None:
        check(any("::NSF,1,Beginning (Block-1)," in line for line in
                  m3u.decode("utf-8-sig").splitlines()), "playlist has no Beginning track 1")
    return {"original_rom_sha256": ROM_SHA, "nsf_sha256": NSF_SHA,
            "playlist_sha256": M3U_SHA if m3u is not None else None,
            "nsf_track_index_zero_based": track,
            "nsf_track_number_one_based": track + 1,
            "source_identity": "authenticated",
            "nsf_note": "modified music rip; not an independent retail-game playback trace"}


def attrs(line: str) -> dict:
    result = {}
    for match in ATTR.finditer(line):
        k, value = match.groups()
        check(k not in result, "duplicate TXT attribute")
        result[k] = value
    return result


def as_int(value: str | None, kind: str, limit: int = 1_000_000) -> int:
    check(value is not None and re.fullmatch(r"[0-9]+", value) is not None,
          f"invalid {kind}")
    n = int(value)
    check(n <= limit, f"{kind} out of range")
    return n


def census(content: bytes, track: int, rom: bytes | None = None,
           nsf: bytes | None = None) -> dict:
    check(len(content) <= MAX_TXT, "FamiStudio TXT exceeds size limit")
    try:
        raw = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("FamiStudio TXT must be UTF-8") from exc
    check("\x00" not in raw, "NUL in FamiStudio TXT")
    check(track == 0, "only Beginning reference is in scope")
    project = False
    selected_song = False
    songs = 0
    channel = None
    pattern = None
    patterns: dict[str, set[str]] = {}
    instances: list[tuple[str, str]] = []
    summary: dict[str, Counter] = {}
    instruments = 0
    sample_count = 0
    samples: list[bytes] = []
    famistudio_version = None
    exported_song_name = None
    for line_no, line in enumerate(raw.splitlines(), 1):
        check(line_no <= 300_000 and len(line) <= 1_000_000,
              "FamiStudio TXT bounds exceeded")
        stripped = line.lstrip("\t ")
        if not stripped:
            continue
        tag = stripped.split(None, 1)[0]
        a = attrs(stripped)
        if tag == "Project":
            check(not project and songs == 0, "multiple or late TXT projects")
            check("VRC6" in a.get("Expansions", "").split(","),
                  "reference export does not declare VRC6")
            famistudio_version = a.get("Version")
            check(famistudio_version is None or
                  re.fullmatch(r"[0-9]+(?:\.[0-9]+){1,3}", famistudio_version) is not None,
                  "invalid FamiStudio version metadata")
            project = True
        elif tag == "DPCMSample":
            sample_count += 1
            sample_hex = a.get("Data", "")
            check(0 < len(sample_hex) <= 32768 and len(sample_hex) % 2 == 0 and
                  re.fullmatch(r"[0-9A-Fa-f]+", sample_hex) is not None,
                  "invalid DPCM sample data")
            samples.append(bytes.fromhex(sample_hex))
        elif tag == "Instrument":
            instruments += 1
        elif tag == "Song":
            check(project, "Song before Project")
            songs += 1
            selected_song = songs == 1
            channel = pattern = None
            if selected_song:
                exported_song_name = a.get("Name")
                check(bool(exported_song_name) and len(exported_song_name) <= 128,
                      "missing/oversized song name")
                check(as_int(a.get("Length"), "Song Length") > 0, "empty song")
        elif tag == "Channel" and selected_song:
            channel = a.get("Type")
            check(channel in CHANNELS and channel not in summary,
                  "unknown or duplicate sound channel")
            summary[channel] = Counter()
            patterns[channel] = set()
            pattern = None
        elif tag == "Pattern" and selected_song:
            check(channel is not None, "Pattern without Channel")
            pattern = a.get("Name")
            check(bool(pattern) and pattern not in patterns[channel], "invalid/duplicate Pattern")
            patterns[channel].add(pattern)
            summary[channel]["patterns"] += 1
        elif tag == "Note" and selected_song:
            check(channel is not None and pattern is not None, "Note without Pattern")
            as_int(a.get("Time"), "Note Time")
            summary[channel]["note_rows"] += 1
            if "Value" in a:
                summary[channel]["pitched_or_triggered_notes"] += 1
            else:
                summary[channel]["effect_only_rows"] += 1
            for key in ("Volume", "FinePitch", "DutyCycle", "VibratoSpeed", "VibratoDepth", "Instrument"):
                if key in a:
                    summary[channel]["with_" + key] += 1
        elif tag == "PatternInstance" and selected_song:
            check(channel is not None, "PatternInstance without Channel")
            as_int(a.get("Time"), "PatternInstance Time")
            check(bool(a.get("Pattern")), "PatternInstance missing Pattern")
            instances.append((channel, a["Pattern"]))
            summary[channel]["pattern_instances"] += 1
    check(project and songs == 1 and summary, "expected exactly one VRC6 song with channels")
    check(all(p in patterns[ch] for ch, p in instances), "PatternInstance references missing Pattern")
    check(sum(s["pitched_or_triggered_notes"] for s in summary.values()) > 0,
          "reference contains no note triggers")
    check((rom is None) == (nsf is None), "both source ROM and NSF required")
    dpcm_matching_sources = None
    if rom is not None and nsf is not None:
        check(len(rom) == 393232 and len(nsf) == 53376,
              "unexpected source lengths for sample comparison")
        dpcm_matching_sources = sum(s in rom[16:16 + 262144] and s in nsf[128:]
                                    for s in samples)
    return {"status": "external_famistudio_txt_parsed_not_gameplay_verified",
            "famistudio_version": famistudio_version,
            "exported_song_name": exported_song_name,
            "nsf_track_index_present_in_export": False,
            "dpcm_payloads_matching_both_original_rom_and_nsf": dpcm_matching_sources,
            "active_channel_count": sum(bool(s["note_rows"]) for s in summary.values()),
            "famistudio_txt_sha256": sha(content),
            "song_count": songs, "instrument_count": instruments,
            "dpcm_sample_declarations": sample_count,
            "channel_counts": {ch: dict(sorted(summary[ch].items())) for ch in CHANNELS if ch in summary},
            "total_note_rows": sum(s["note_rows"] for s in summary.values()),
            "total_note_triggers": sum(s["pitched_or_triggered_notes"] for s in summary.values()),
            "warning": "structural TXT census only; patterns may repeat; not sound-command or PCM parity"}


def smoke() -> None:
    fixture = b'''Project TempoMode="FamiStudio" Expansions="VRC6"
\tInstrument Name="Invented lead"
\tSong Name="Invented" Length="2" PatternLength="16"
\t\tChannel Type="Square1"
\t\t\tPattern Name="P"
\t\t\t\tNote Time="0" Value="C4" Duration="2" Volume="15"
\t\t\t\tNote Time="1" Volume="10" FinePitch="-2"
\t\t\tPatternInstance Time="0" Pattern="P"
\t\tChannel Type="VRC6Saw"
\t\t\tPattern Name="S"
\t\t\t\tNote Time="2" Value="E4"
\t\t\tPatternInstance Time="0" Pattern="S"
'''
    result = census(fixture, 0)
    check(result["total_note_rows"] == 3 and result["total_note_triggers"] == 2,
          "synthetic note census mismatch")
    check(result["channel_counts"]["Square1"]["with_FinePitch"] == 1,
          "synthetic effect census mismatch")
    bad = [fixture.replace(b'Expansions="VRC6"', b'Expansions="MMC5"'),
           fixture.replace(b'Channel Type="VRC6Saw"', b'Channel Type="Unknown"'),
           fixture.replace(b'Pattern="S"', b'Pattern="Missing"'),
           fixture.replace(b'Note Time="2"', b'Note Time="-1"'),
           fixture.replace(b'Note Time="0"', b'Note Time="0" Time="1"'),
           fixture.replace(b'Value="C4"', b'').replace(b'Value="E4"', b''),
           fixture + b'\nSong Name="Extra" Length="1"\n',
           fixture.replace(b'Project ', b'DPCMSample Name="bad" Data="xyz"\nProject ')]
    for idx, changed in enumerate(bad):
        try:
            census(changed, 0)
        except ValueError:
            continue
        raise AssertionError(f"corrupt artificial fixture accepted: {idx}")
    print(f"PASS JP0664 artificial VRC6 census, {len(bad)} invalid TXT cases")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rom", type=Path)
    ap.add_argument("--nsf", type=Path)
    ap.add_argument("--m3u", type=Path)
    ap.add_argument("--famistudio-txt", type=Path)
    ap.add_argument("--song-index", type=int, default=0)
    ap.add_argument("--json", type=Path, help="owner-private metadata-only JSON path")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.smoke:
        smoke()
        if args.rom is None and args.nsf is None:
            return
    if args.rom is None or args.nsf is None:
        ap.error("--rom and --nsf must be supplied together")
    proof = source_identity(args.rom.read_bytes(), args.nsf.read_bytes(),
                            args.m3u.read_bytes() if args.m3u else None,
                            args.song_index)
    result = {"schema": "jp0664-famistudio-structural-reference/v1",
              "capture": {"status": "not_exercised"},
              "source": proof,
              "original_sound_command_id": None,
              "retail_gameplay_trace_parity": "not_exercised",
              "independent_music_sfx_playback": "not_implemented"}
    if args.famistudio_txt:
        result["capture"] = census(args.famistudio_txt.read_bytes(), args.song_index,
                                   args.rom.read_bytes(), args.nsf.read_bytes())
    if args.json:
        args.json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("PASS JP0664 authenticated private ROM+NSF" +
          ("; FamiStudio TXT structurally checked (NOT retail parity)" if args.famistudio_txt
           else "; FamiStudio capture NOT EXERCISED"))


if __name__ == "__main__":
    main()
