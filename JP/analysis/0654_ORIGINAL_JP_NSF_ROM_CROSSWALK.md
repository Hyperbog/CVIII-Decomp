# JP0654 — Original Japanese ROM ↔ ripped NSF physical PRG crosswalk

## Source identities and epistemic boundary

**Original game:** owner-supplied Akumajou Densetsu (Japan).nes, exactly
393,232 bytes, SHA-256
`958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`,
Mapper24 VRC6a.

**Secondary artifact:** Zophar-style Japanese NSF 53,376 bytes,
SHA-256 `302b79d8b2df9cb7fe94936feca6582cc35294844a93325c9bbfbb37d8e98008`.
User archive `Castlevania 3 - Dracula's Curse JP (EMU).zophar.zip`
contains exactly that NSF and the byte-identical 3,929-byte M3U playlist
SHA-256 `48b75d2df330c569a393e0aacfd22c453783bc3b1e5f31b826f30a3721bb85ae`.
The original archive and an independently supplied NSF/M3U copy match.
The NSF is a **modified music rip**, not independent observed retail
gameplay, not a replacement Japanese cartridge ROM, and not evidence
that the NSFs' per-track indices are original command IDs.

Specification: https://www.nesdev.org/wiki/NSF . The NSF v1 header
has 28 tracks (starting track 1), program load $8000, INIT $E0E0,
PLAY $E0D0, NTSC interval 16,640 microseconds, NTSC-only flag and
**VRC6 audio** (sound-chip flag bit 0). It boots NSF virtual 4KiB pages
`[00,00,00,00,0B,0C,0A,0A]` into $8000–$FFFF. These NSF pages are
selected using **$5FF8–$5FFF**, *not* original mapper24 physical
16KiB PRG selection or its $C000 8KiB PRG register. INIT and PLAY
are rip-authored entry points, not certified original-game code PCs.

## Exhaustive 53,248-byte rip payload comparison

`JP/tools/jp_nsf_rom_crosswalk_0654.py` SHA-authenticates the game,
NSF and optional playlist, applies the NSF specification, then
checks every one of the 13 original **physical 4KiB PRG** source images
against its NSF payload bank. This is a **full exact byte comparison**,
not matching on loose strings or candidate opcodes.

| NSF 4KiB payload banks | Original physical PRG 4KiB banks | Status |
| --- | --- | --- |
| 0–3 | 16–19 (physical raw16 $04) | 4 × 4KiB exact |
| 4–7 | 20–23 (physical raw16 $05) | 4 × 4KiB exact |
| 8–9 | 48–49 (physical raw16 $0C) | 2 × 4KiB exact |
| 10 | 50 (physical raw16 $0C, CPU $A000–$AFFF conditional) | $300-byte prefix modified; $A300–$AFFF exact |
| 11 | 14 (physical raw16 $03) | 4KiB exact |
| 12 | 15 (physical raw16 $03) | final $10 bytes modified; preceding $FF0 exact |

Thus **11 of 13 entire 4KiB banks** match the retail source exactly.
The two bounded rip overlay windows occupy 784 bytes. All other
**52,464 of 53,248 payload bytes are provably unmodified**.
Of the 784 overlay bytes, 775 actually differ; nine happen to agree
by value. Do not silently treat those coincidentally equal nine bytes
as authenticated original runtime code.

1. Original physical raw16 bank $0C, conditional CPU **$A000–$A2FF**,
   NSF payload bank 10 offset $000–$2FF: **759/768 differing bytes**.
   These bytes overlap the original bank0C source-addressed sound-stream
   pool $9541–$A303 from JP0533. The music rip therefore does *not*
   contain the complete original bank0C sound stream pool.
2. Original physical raw16 bank $03, conditional CPU **$BFF0–$BFFF**,
   NSF payload bank 12 offset $FF0–$FFF: **16/16 differing bytes**.
   This is a rip trailer/replacement, not retail bank data.

**Verified preserved source:** the complete original sound metadata
directory $8F60–$9540 (JP0652), the entire 296-byte phrase-pointer
table $A304–$A42B and 1,323-byte phrase pool $A42C–$A956
(JP0653), and all 60 original DMC descriptor parameter bytes
$A957–$A992 (JP0648). The original raw0C $8D15–$8D8F
instruction region, an outstanding phrase arithmetic/parser research
target, also lies in an exact copied bank. Therefore the NSF is a
**second local byte-equality witness** for source and fixed-format
provenance; this does not determine dynamic selector limits, identify
voices, or prove whether the modified rip plays the same sound.

## Implementation, validation and reproduction

The new Python audit reads the commercial inputs privately and emits
**metadata only**. It rejects wrong ROM/NSF/M3U SHA, header geometry,
region/expansion flags, entry addresses, startup NSF bank assignment,
noncanonical source-to-rip banks, changes outside the two expected
rip overlays, truncation, malformed playlist song IDs, and wrong
original sound phrase/DMC bytes. ZIP entries are inspected in memory,
**never extracted to disk**, and must contain just a bounded NSF/M3U
pair. An artificial ROM/NSF builder and eight damaged-input negatives
run in public CI without any licensed bytes.

```sh
python3 JP/tools/jp_nsf_rom_crosswalk_0654.py --smoke
python3 JP/tools/jp_nsf_rom_crosswalk_0654.py \
  --rom "/private/Akumajou Densetsu (Japan).nes" \
  --archive "/private/Castlevania 3 - Dracula's Curse JP (EMU).zophar.zip" \
  --json "/private/JP0654-nsf-rom-crosswalk.json"
# An independently supplied NSF and M3U may replace --archive:
python3 JP/tools/jp_nsf_rom_crosswalk_0654.py \
  --rom "/private/Akumajou Densetsu (Japan).nes" \
  --nsf "/private/Akumajou Densetsu.nsf" \
  --m3u "/private/Akumajou Densetsu.m3u"
```

Locally executed against authentic uploaded ROM and NSF ZIP:
**PASS** all 13 complete source-bank diffs, 28 M3U indices, 11
exact source banks, two bounded overlays, retained metadata/phrase/DMC
sections. ROM-free synthetic and eight malformed-input cases PASS.
Additionally, local FFmpeg/libgme NSF playback produced non-silent
two-second mono samples for four distinct song indices (0,14,21,22);
these are not a verified APU register trace, PCM reference equivalence,
nor owner gameplay playback.

No NSF/game sample payload, ZIP, M3U or original ROM is committed.
Original cartridge gameplay, CPU and sound output are unchanged.
No native music interpreter, read-only game PCM mixer patch, or user
interaction has been introduced.

## Honest next step

Use this immutable rip/original distinction when lifting the
**original ROM** raw0C sound interpreter, including source bytes at
$8D15–$8D8F; do not accidentally execute the NSF $E0D0/$E0E0
shim as original 6502 engine behavior. Separate tasks are matching
NSF INIT/PLAY audio decisions and authentic Japanese gameplay
original-Mesen sound-request/mapper/DMC traces and identifying music
versus effects. Those parity claims are still unproved. Strict
semantically verified PRG stays **49,504/262,144 (18.8843%)**,
VPP **27/100**, certified checkpoint **0508**, fixed frontier
**$FB96**, R-002 and R-007 **OPEN**. No new certified bytes.
