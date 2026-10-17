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

## JP0664 continuation — confirmed Beginning and rip-to-original program (2026-10-17)

**Owner explicitly confirmed** that uploaded private FamiStudio 4.5.1 `CV3JP.txt` is **Beginning (Block-1)**, one-based NSF track 1 / zero-based FamiStudio index 0. This resolves the human export selection; the TXT's generic `Song 1` label still does not encode track number. The owner statement is recorded as owner confirmation, **not independently attested by the TXT**.

**New source-authenticated static bridge:**

1. In the authenticated modified VRC6 NSF, the 32-byte initialization wrapper at NSF virtual `$E0E0–$E0FF` has SHA-256 `dcb05368b636ff14a9125bea67fd9489bc8d78466eec0ecc7a32f326a0906aeb`. Its trailing 6502 instructions restore the track-index A from the stack into X, load `[$E100+X]`, then dispatch via `JMP $8850`.
2. The complete 28-byte ripped-NSF track lookup at virtual `$E100–$E11B` has SHA-256 `6a1931c4ffa9b7e300d32264b0b461bae9d13b38935b620d5912598cb441c178`. **Zero-based track 0 maps to command `$51`**. This table and wrapper are **rip-authored**, not original game source or an observed gameplay request.
3. The **independently SHA-authenticated original-JP raw0C sound directory** maps sound ID **`$51`** to one bank-qualified descriptor containing **six opaque references to physical 16KiB PRG bank `$05`**. Their mode bytes/CPU roots are not asserted to be FamiStudio channels, and proprietary source pointer lists remain owner-private.
4. All 16 KiB of the original physical raw05 containing those six source streams are **byte-identical** to the corresponding four 4KiB NSF payload banks (4–7). This is an **exact source-byte** relationship, not per-note semantic parity. The code `jp_famistudio_driver_bridge_0664.py` requires exact ROM/NSF/M3U identities, pinned NSF wrapper/table bytes, original program structure and the full raw05 equality; it also counts source-matched DPCM and FamiStudio channels only as **private aggregate evidence**.

**Local actual-media verification:** Authenticated NSF wrapper/table hashes and original ROM raw0C sound metadata matched, selected NSF index0 sound ID `$51` matched original six-root raw05 program, and original raw05/NSF 16KiB copy matched byte-for-byte. A ROM-free source-independent selector smoke (with seven corrupt synthetic cases) is registered for CI.

**Evidence boundary:** The `$51` link supplies a concrete historical program target for further semantic work. It does **not** prove original game live command ingress, decoded raw05 token semantics, exact 2A03/VRC6 register writes, song repeat/loop control, original Mesen parity, or independent sound effect playback. Original gameplay instrumentation from JP0610/JP0646 and matched original/runtime event traces remain required before activating JP0647.

### Owner-private reproduction

```sh
python3 JP/decomp/tools/jp_famistudio_driver_bridge_0664.py --smoke
python3 JP/decomp/tools/jp_famistudio_driver_bridge_0664.py \
  --rom '/private/Akumajou Densetsu (Japan).nes' \
  --nsf '/private/Akumajou.nsf' \
  --m3u '/private/Akumajou.m3u' \
  --famistudio-txt '/private/CV3JP.txt' \
  --owner-confirmed --json '/private/JP0664-Beginning-source-bridge.json'
```

## Original six-stream graph decoding (JP0664 continuation)

**Authority:** original-Japanese ROM sound ID `$51`, its source directory pointer, and all six original raw05 stream bodies. The preceding static NSF wrapper/index0 -> `$51` bridge and owner-confirmed FamiStudio `Beginning` reference are unchanged.

The new ROM-authenticated utility `JP/decomp/tools/jp_beginning_stream_graph_0664.py` reuses the **previously admitted 04FB alternate-parser grammar** for the `$87AE–$9A6A` bank05 stream span (source SHA-256 `58f4a24e41ba95766529e1eaa531c63fc666ca51abc668ec4eb3ba3f4e50eb6b`). It traverses each of the six descriptor-rooted streams without assuming musical note meaning:

- Modes are still the **opaque, original descriptor mode bytes** `0,1,2,3,4,7`, **not** mapped to the six FamiStudio non-DPCM channel names.
- Non-mode7 byte widths: upper nibble `0–C` is one byte, `D` consumes four, and `E` has its inherited one/two/variable-length cases. Mode7 consumes each non-`F` byte singly. `FB` anchors, `FD` call/return, `FE nn` counted repeats (both possible paths abstractly), `FE FF lo hi` absolute pointer transfers, and `FF` termination follow historical audited 04FB syntax. This does **not** decode tempo, pitches, APU writes or exact conditional-repeat counts.
- Every source-read byte and branch target is bounded to the authenticated 04FB stream region; the tool rejects missing loop anchors, invalid pointer targets, truncated operands, wrong cartridge/region and changed source graph fingerprints.
- Only aggregate state/command/control counts go into reports; raw ROM operands and reconstructible stream/source-pointer lists stay owner-private.

| Original opaque mode | Abstract parser states | Distinct command-byte addresses | Distinct command+operand addresses | Distinct `E7` sites |
| --- | ---: | ---: | ---: | ---: |
| `$00` | 759 | 345 | 457 | 2 |
| `$01` | 813 | 364 | 473 | 2 |
| `$02` | 781 | 385 | 462 | 3 |
| `$03` | 927 | 510 | 651 | 1 |
| `$04` | 820 | 371 | 510 | 1 |
| `$07` | 366 | 320 | 332 | 0 |

**All six** graphs contain a source-authenticated `FE FF lo hi` absolute transfer back into their stream graph and **no visited `FF` terminator**. A recurring code path is therefore structurally present, which is **not** a proven song loop duration or an audible loop point. `E7` high nibble parameters across all six are within previously certified `$0/$5/$8` domains; no new parameter bounds are assumed.

### Comparison against owner-confirmed FamiStudio

The original program has **six source streams**; the FamiStudio tracker has **six active non-DPCM channels, one active DPCM channel, and an empty Triangle channel**. The equal six-vs-six count is a **hypothesis-generating coincidence**, **not** a verified mode-to-chip/channel mapping. Likewise, the FamiStudio `LoopPoint=0` is not proof that these six original control-flow cycles complete with the same tick/sample timing. FamiStudio reports **8,216 source-independent note-trigger rows** across all its channels. The original parsed byte-stream graphs are **unique syntax sites / possible abstract states**, so their counters must never be compared one-to-one with tracker trigger counts.

**Verified now:** owner-authenticated ROM, six stream roots, 04FB source span/hash, six bounded cyclic control graphs, parser token widths/control pointers, and local synthetic graph regression (including three deliberately corrupt streams). **Remaining unknown:** first-byte/note semantics, mode-to-hardware register mapping, tick scheduling and tempo, counted-repeat execution cadence, active-game original sound requests, SFX preemption, exact FamiStudio note/pitch/volume correspondence, and independent native PCM mixing.

Reproduce **locally** with the owner ROM; JSON stores aggregate counts only:

```sh
python3 JP/decomp/tools/jp_beginning_stream_graph_0664.py --smoke
python3 JP/decomp/tools/jp_beginning_stream_graph_0664.py \
  --rom '/private/Akumajou Densetsu (Japan).nes' \
  --json '/private/JP0664-Beginning-six-stream-graph.json'
```

No new VPP or strict PRG credit; no player audio, mixer or save-state changes.

## Next evidence step

After an authentic *Beginning* FamiStudio capture, compare its **channel envelopes and note/volume/pitch changes** against owner-private APU/VRC6 register events from JP0610 and music-program source decode via JP0652–JP0656. The original game source / live sound requests remain authority; FamiStudio's NSF notes are a lossy reference. A reference per-channel match does not establish original-event ownership. First genuine product proof requires one authenticated song and an overlapping original whip SFX played independently through JP0647, with reversibility, resynchronization after save/load and original APU/VRC6 hardware behavior preserved.

**Accounting:** native product unchanged; source VPP **31/100**; strict semantic PRG **49,504/262,144 (18.8843%)** unchanged; sound investigation **R-007 OPEN**. No new certification or playable-audio claim.