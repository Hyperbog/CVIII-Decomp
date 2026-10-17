# JP0664 — FamiStudio VRC6 reference preflight for *Beginning*

**Scope:** First, bounded step toward native **faithful** independent Music/SFX. FamiStudio is a secondary **observation and analysis** tool, not a replacement original-JP driver or native mixer. This change does **not** introduce music/SFX production, alter `JP/recomp` game execution, synthesize licensed music, or enable the currently dormant JP0647 mixer.

## Inputs and provenance

- Authenticated Japanese Mapper24 original ROM, 393,232 bytes, SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.
- Authenticated 28-track modified VRC6 NSF, 53,376 bytes, SHA-256 `302b79d8b2df9cb7fe94936feca6582cc35294844a93325c9bbfbb37d8e98008`.
- Optional authenticated M3U, SHA-256 `48b75d2df330c569a393e0aacfd22c453783bc3b1e5f31b826f30a3721bb85ae`, associates NSF one-based track **1** with **Beginning (Block-1)**. FamiStudio's CLI uses **zero-based** `-nsf-import-song:0`.
- JP0654 already proved eleven of thirteen NSF 4KiB source pages identical to the ROM. The ripped NSF **replaces original bank0C $A000–$A2FF** and a small bank03 trailer. Its INIT/PLAY entry points are rip-specific, and its observed notes **cannot** establish original retail sound-command IDs, note ownership in live gameplay, or mapper-state parity.

## Owner-local capture (not yet executed)

Install [FamiStudio](https://github.com/BleuBleu/FamiStudio) on the private development PC (4.5.3 available when this step was written). Keep input/output files **outside Git**. On Windows PowerShell, adjusting paths:

```powershell
$fami = 'C:\Tools\FamiStudio\FamiStudio.exe'
$nsf = 'C:\Private\Akumajou.nsf'
$rom = 'C:\Private\Akumajou Densetsu (Japan).nes'
$m3u = 'C:\Private\Akumajou.m3u'
$txt = 'C:\Private\Beginning-FamiStudio.txt'
& $fami $nsf famistudio-txt-export $txt -nsf-import-song:0 -nsf-import-duration:90 -nsf-import-pattern-length:160
python JP/decomp/tools/jp_famistudio_reference_0664.py `
  --rom $rom --nsf $nsf --m3u $m3u --song-index 0 `
  --famistudio-txt $txt --json 'C:\Private\JP0664-Beginning-summary.json'
```

This particular FamiStudio command is **source-documented, not exercised in the current environment**. Use the program's desktop NSF import/export if its command-line behavior differs. Capture the exact FamiStudio version and any import warnings in the private work log. Review the per-channel note and automation events in FamiStudio and compare by ear against direct NSF playback **before** treating anything as a usable reference.

## Executable preflight and fail-closed limitations

`JP/decomp/tools/jp_famistudio_reference_0664.py`:

1. SHA-authenticates the user-owned ROM, NSF and optional playlist; checks the NSF VRC6 bit, load/init/play addresses, and exact track index.
2. Without a FamiStudio TXT, emits `capture.status = not_exercised`. **Authenticated inputs do not imply an imported or verified song.**
3. With an owner-local FamiStudio TXT, validates one VRC6 song, known 2A03/VRC6 channel types, bounded patterns/instances and note timing fields; produces **aggregate counts only**: pattern definitions/uses, note triggers, automation fields, instruments and DPCM declarations. It records a TXT SHA, **not notes, instrument data, per-note timing, pitch, WAV, DPCM bytes, or reconstructible patterns**.
4. Labels the TXT census **structural** only. It does not prove its TXT came from the authenticated NSF. Pattern instances can reuse the same note definitions, so its note counts are **not event-liveness counts**. It does not classify any sound as gameplay Music vs SFX or infer the original game's command IDs.

### Validation

```sh
python3 JP/decomp/tools/jp_famistudio_reference_0664.py --smoke
python3 JP/decomp/tools/jp_famistudio_reference_0664.py \
  --rom '/private/Akumajou Densetsu (Japan).nes' \
  --nsf '/private/Akumajou.nsf' --m3u '/private/Akumajou.m3u' \
  --json '/private/JP0664-Beginning-source-summary.json'
```

Locally performed in JP0664: **ROM-free invented 2A03+VRC6 reference and seven corrupt fixtures PASS**, and uploaded user-provided ROM/NSF/M3U identities **PASS**, yielding `capture.status = not_exercised`. The actual FamiStudio application is not present in this environment; FamiStudio TXT import, register/audio comparison, original retail MesenCE trace, genuine gameplay, native audio producer and independent audible SFX are **NOT EXERCISED**. No application output was fabricated.

## Owner-supplied FamiStudio 4.5.1 structural capture (2026-10-17)

A private owner upload `CV3JP.txt` was audited locally using the JP0664 tool (SHA-256 `df25db714eb378072e797230a8d90ff105a3d010d4ea63b36e7a39950ebffd30`). **The TXT contains actual licensed music/sample data and is NOT committed.** Only this aggregate evidence is committed.

- Export metadata: `Project Version="4.5.1"`, `Expansions="VRC6"`, one song labeled **`Song 1`**, `Length="29"`, `PatternLength="32"`, `NoteLength="8"`, `LoopPoint="0"`.
- All eight standard Japanese-CVIII APU/VRC6 channels are declared. **Seven contain note/effect data; Triangle is empty**.
- **20,083** tracker note/effect rows across 29 distinct patterns per channel, including **8,216** pitch/sample-trigger rows. Count is of FamiStudio's exported representation, **not** original ROM note-script opcodes, not unique instruments, and not a runtime sound-event count.
- Three sample payloads defined in the export (256, 64, and 512 bytes) each occur **byte-for-byte** in both the authenticated original ROM PRG and modified Japanese NSF payload. Sample bytes and raw source offsets are excluded from Git. This supports **DPCM asset provenance** but does not prove those samples were triggered in the retail game's Beginning stage.
- Full aggregate channel census (rows/triggers):
  - Square1: 3,657 / 1,236
  - Square2: 2,978 / 1,343
  - Triangle: 0 / 0
  - Noise: 2,329 / 1,770
  - DPCM: 717 / 717
  - VRC6Square1: 3,912 / 1,424
  - VRC6Square2: 2,331 / 1,232
  - VRC6Saw: 4,159 / 494
- The TXT does **not encode the original NSF track number**, and its `Song 1` label is generic. Thus the intended **Beginning** track association remains **owner-export-step assumed, not independently attested**. Do not infer sound-command IDs, original source-note envelopes or gameplay parity from it.
- The updated tool parses sample hex only owner-locally, reports the number of source-matched samples without their data, and adds a synthetic malformed-DPCM input test: **8 intentionally corrupt fixtures rejected**, plus synthetic valid fixture and uploaded-source checks PASS.

**Owner-private test performed:** `python3 JP/decomp/tools/jp_famistudio_reference_0664.py --rom ORIGINAL_JP.nes --nsf JAPANESE.nsf --m3u JAPANESE.m3u --famistudio-txt CV3JP.txt --json PRIVATE_METADATA_ONLY.json`. This tests structural parsing and byte-source membership; it **does not execute FamiStudio 4.5.1, MesenCE, or the playable game**.

## Next evidence step

After an authentic *Beginning* FamiStudio capture, compare its **channel envelopes and note/volume/pitch changes** against owner-private APU/VRC6 register events from JP0610 and music-program source decode via JP0652–JP0656. The original game source / live sound requests remain authority; FamiStudio's NSF notes are a lossy reference. A reference per-channel match does not establish original-event ownership. First genuine product proof requires one authenticated song and an overlapping original whip SFX played independently through JP0647, with reversibility, resynchronization after save/load and original APU/VRC6 hardware behavior preserved.

**Accounting:** native product unchanged; source VPP **31/100**; strict semantic PRG **49,504/262,144 (18.8843%)** unchanged; sound investigation **R-007 OPEN**. No new certification or playable-audio claim.