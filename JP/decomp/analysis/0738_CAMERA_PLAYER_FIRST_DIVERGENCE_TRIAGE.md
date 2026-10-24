# JP0738 — First camera/player divergence, Stage 1-02

**Read-only analysis.** The original private MesenCE recording and paired native frame-log bytes are not mounted in this session. JP0738 does not change game execution.

## Authenticated original Japanese ROM

Original iNES 393,232 bytes, Mapper24, SHA-256 958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28.

Three original-ROM source intervals were verified again against the uploaded image and their archived source SHA-256 fingerprints:

- Physical PRG $3D2FE–$3D30C, bank30 CPU $D2FE–$D30C: conditional camera/object delta producer, RAM $6B=$53−$08 (JP0514).
- Physical PRG $2C001–$2C04A, raw0B CPU $8001–$804A: fixed-point actor X/Y movement and velocity/fraction updates (JP0511).
- Physical PRG $2C0E3–$2C10E, raw0B CPU $80E3–$810E: source actor displacement using $6B (JP0512).

Physical ROM bytes and static semantic identification do NOT prove which branch naturally caused the gameplay failure.

## Previous original/native checkpoint comparison

These numbers were reported in the original-ROM JP0737 evidence; they were not independently re-executed here.

| Frame | Mesen original camera | Native camera | Difference |
| ---: | ---: | ---: | ---: |
| 9,376 | 0 | 0 | 0 |
| 9,440 | 10 | 9 | -1 |
| 9,504 | 49 | 48 | -1 |
| 9,576 | 93 | 56 | -37 |
| 9,760 | 176 | 57 | -119 |
| 10,272 | 512 | 432 | -80 |
| 10,328 | 534 | 438 | -96 |

At frame 10,328, original room selector is 00/02/01 and native is 00/01/02, the first confirmed *sampled* room-selector difference. The substantial movement gap emerges between frames 9,504 and 9,576. The corrected Stage 1-02 source file is $0201DD (JP0726), not the earlier crosswalk $02017C. No static-atlas defect is demonstrated by these data.

The original input schedule includes Down+Right around 9,388–9,450, Left near 9,493, and A/B+Right around 9,536–9,550. Its archived native replay input file has SHA-256 27b502aaeca9f5d5381f9f9a812cc188043d083d8ac8b3a89bc40c70f3c30196. **Matching input intent is not a proof of actual CPU $4016/$4017 read-phase equivalence.**

## New diagnostic and reproduction

Source: JP/decomp/tools/jp0738_camera_window.py.

The read-only comparator accepts the existing original-Mesen ZIP containing RAM/PPU snapshot TSV, a native NESRecomp CYCFRAME v2 file, the authenticated original Japanese ROM, and optionally the original input schedule. It reports the first mismatched *sampled* camera, room selector, player slot-0 position/fraction/motion, context and actor fields, all-CPU-RAM difference counts, camera advances between checkpoints, palette alias/nonalias discrepancies and best-projected physical CIRAM nametable differences. It explicitly reports absent checkpoints.

To run the synthetic test (no commercial game data): python3 JP/decomp/tools/jp0738_camera_window.py --smoke

To compare the existing owner-private files, invoke:

    python3 JP/decomp/tools/jp0738_camera_window.py --rom "$JP_ORIGINAL_ROM" --mesen-zip /private/mesen.zip --native-frame-log /private/native.cycframe --input-schedule /private/controller.input

The private paths are illustrative. The matching recording must contain the 9,376–10,328 checkpoints. Output contains numeric comparison state only; no ROM, screenshot or derived art is checked into Git.

The comparator does NOT prove precise controller polling; it does NOT derive physical VRC6 nametable mappings from a best-page fit; it does NOT infer PPU/CHR bank switch timing from screenshots; and it does NOT claim original Mesen OAM equivalence without a verified original OAM field. To distinguish causes, compare **player X/Y, signed speed/fraction and collision state first**, then $53/$54/$6B and the original bank30 producer. A newly verified read-only $4016/$4017 bus/latch-cycle trace, OAM and CHR/PPU mapping history would be required for narrower causal attribution. Do not add gameplay patches or native handlers based on these observations.

## Supplemental GMvania address review (JP0738 follow-up)

The developer-authored [Castlevania III RAM and ROM offsets](https://gmvania.blogspot.com/2012/08/bookmark-this-blog-entry-last-update.html) (originally 2012, last updated 2022-10-08) documents RAM $0028 press, $002A hold, $0055 fractional view position, $0062 movement state, $006B actor view-scroll delta, $006C view/PPU offset, $006E room extent, and player slot 0 $0565 action state / $05C1 fall switch. It also documents $0438/$041C player coordinates and $04C4/$04F2/$0509 X fraction and speed. The author warns that Japanese and North American ROM and zero-page addresses differ. **This is a secondary research address map; newly watched fields are hypotheses until verified against the exact Japanese ROM producer and consumer and a naturally recorded execution.** The comparator explicitly groups these exploratory fields separately from the JP0511/0512/0514 byte-authenticated movement windows.

A particularly useful authentic JP ROM source window is physical PRG $3D2FE-$3D30C, fixed by SHA-256 7694f4922335fb8e25f4639f983714ea86112971811c3bc8afc6dc6a9aef5553. Its bytes begin **A4 62 F0 0F 88 F0 08**, choosing distinct $62=0/1 paths instead of the known $62>=2 path **A5 53 38 E5 08 85 6B 60**. This is static instruction-byte evidence of divergent code branches, **not** proof that $62 differs between the two paired games near frame 9,504.

The prior JP0738 script has now been extended to label internal game-side $0028/$002A input hypotheses, view subpixel $0055, view offset $006C, movement/transition/room-state fields, optional CHR selection/mode hypotheses, and player action/fall hypotheses. It calculates SHA-256 of the private capture files (if passed) for future exact-run reproducibility; those digests alone do **not** independently authenticate the source emulator, clock, input sampling, or archive provenance. The script continues to refuse to claim $4016 bus parity, actual CHR bank timeline, or earliest CPU-write causality from sampled RAM.

**2026-10-24 recovery update:** The authentic original JP0718 Mesen RAW-INPUT ZIP and older JP0719 native FULL-NATIVE-REPLAY ZIP, plus the JP0719 forensic report, are now supplied and ZIP CRC-verified. They have been compared below. The later JP0737 native CYCFRAME v2 recording remains unavailable here; it must not be conflated with the separate older JP0719 executable.

**Certification unchanged: VPP 31/100, strictly certified PRG 49,504/262,144 (18.8843%), checkpoint 0508.** ROM-free synthetic tests are not a real game parity pass.


## JP0738B — Authenticated original/native archived replay comparison

**Archive provenance (SHA-256):** JP0718 original Mesen ZIP
d2a54d01cbec9d4257d99df7a13a7b628fb41d59d5220bba66eb80c2a2f52878;
JP0719 native ZIP
ea18d677e232cb9fcc574d9453f064f335eacaa00e7ce2c567968ca0f2842aeb.
Both ZIP CRC checks passed. Original retail Japanese ROM SHA-256
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
rechecked. The JP0719 native executable SHA-256 in the archived run details is
5e7039fb74fc8423cd340e212a1f7b822a6d112d07140c28e967a94fafd7a710.

**Original input intent verified, not inferred:** the original Mesen input
absolute-frame column (first integer after P, not its local frame index) and
the JP0719 native replay's exact input epochs produce identical button masks
for both controller ports at **17,562/17,562** original poll records.
Mismatch count = **0**. The native input file SHA-256 is
27b502aaeca9f5d5381f9f9a812cc188043d083d8ac8b3a89bc40c70f3c30196.
This proves schedule conversion only: $4016/$4017 CPU-cycle sampling parity
is still unmeasured.

### Observed original versus older native state

| Run | Frame | Camera RAM $53/$54 | Player Y $041C | Mode $62 | Delta $6B | Action $0565 | Y speed $0520 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Mesen original | 9440 | 10 | 80 | 1 | 1 | 4 | 0 |
| JP0719 native | nominal 9432 | 0 | 80 | 2 | 0 | 4 | 0 |
| Mesen original | 9504 | 49 | 101 | 0 | 0 | 12 | 5 |
| JP0719 native | nominal 9496 | 54 | 80 | 0 | 255 | 4 | 0 |
| JP0719 native | nominal 9560 | 56 | 44 | 2 | 0 | 26 | 0 |
| Mesen original | 9576 | 93 | 155 | 1 | 1 | 8 | 5 |
| JP0719 native | nominal 9592 | 56 | 80 | 2 | 0 | 24 | 0 |
| Mesen original | 9760 | 176 | 96 | 2 | 0 | 20 | 255 |
| JP0719 native | nominal 9752 | 57 | 160 | 2 | 0 | 2 | 0 |

**TIMING LIMIT:** Mesen end-frame observations are event-driven. The
nominal native sample_tick*8 observation at 9432 precedes the original
9440 observation by **267,907 CPU cycles** (not aligned). Original frame
9576 is bracketed by native nominal samples 9560 and 9592. Do not
relabel these as exact-frame matches. However the *native recording itself*
shows camera 56 at both 9560 and 9592 while the original progresses from
49 at 9504 to 93 at 9576. The player Y/action and scrolling mode are
also substantially different, strongly prioritizing player-motion,
collision-state and scroll boundary / producer timing over extra native
boot handlers.

### PPU/CHR controls at nearby but unequal times

| Original / native nominal | Differing CPU RAM bytes | Differing 4KiB nametable bytes | Physical 8 CHR pages equal | Nonalias palette mismatches |
| --- | ---: | ---: | --- | ---: |
| 9440 / 9432 | 257 | 0 | yes | 0 |
| 9504 / 9496 | 294 | 8 | yes | 0 |
| 9576 / 9560 | 404 | 194 | yes | 0 |
| 9576 / 9592 | 389 | 194 | yes | 0 |
| 9760 / 9752 | 353 | 526 | yes | 0 |

Both captures' end-frame physical 1KiB CHR page IDs in the selected
window are **00 01 12 0F 40 45 47 43**. Original/native sprite palette
universal-color aliases may store 0F vs 00; nonalias logical palettes
agree. This does not certify per-scanline CHR bank parity. Increasing
nametable mismatches after the movement split may be a consequence
of scrolling and scene mutations, not necessarily their cause.

**Separate native generations:** The later JP0737 ROM-at-launch
CYCFRAME evidence reported original/native camera checkpoints 9440 10/9,
9504 49/48, 9576 93/56. The JP0719 ZIP analyzed here was produced by
a different native executable, has nominal periodic sample times, and
must not be presented as fresh JP0737 execution.


### JP0738D — Original Japanese fixed-bank scroll-gate semantics

Independent actual-cartridge byte inspection extends the existing
JP0514 authenticated fixed-bank source window with original physical
PRG offset $3D30D–$3D348 (CPU $D30D–$D348, 60 bytes), SHA-256
**3f5339caeff220c436bca6124c685d35bf0e74648b764b69d9aa6dd6d91f8e8b**.
The complete $D2FE–$D348 75-byte local window hashes to
**ffa88774d3c97eb6d7fa337d4ea1b37fc6fa64155dc27f25da01979c1353d435**.
These are source identity hashes, **not new strict PRG admission**.

Exact original 6502 branches from $D2FE:
- LDY $62; BEQ $D311 when $62=0, choosing LDA #$FF to
  initialize signed high byte scratch $00; otherwise DEY; BEQ $D30D
  for $62=1, choosing LDA #$00.
- For $62>=2, the $D305–$D30C path sets $6B=$53-$08
  and returns. **It does not advance $53/$54/$55.**
- The $62=0 or 1 camera motion continuation at $D315–$D328
  adds original subpixel X speed RAM $0509 to $55, then integer X speed
  RAM $04F2 to $53, with carry/sign high RAM $00 to $54.
- At $D340–$D348, source LDA $53; AND #$E0; CMP $63; BEQ $D305
  checks a **32-pixel camera boundary**; the non-equal continuation
  writes $63 and changes the scroll-boundary handling path.

At original 9504, captured RAM camera X=49, $63=$20, $62=0.
At original 9576, X=93, $63=$40, $62=1. The JP0719 native
9496 snapshot has X=54, $63=$20, $62=0; its 9560 and 9592
snapshots both have X=56, $63=$20, $62=2. **Conditionally, when
$D2FE runs**, the native mode 2 is consistent with skipping the
camera-advancement path, while original mode 1 selects it. This
does not establish which CPU instruction first wrote the divergent $62,
whether the $62 state was wrong, or whether an earlier collision/player
state legitimately selected that mode in the native run. All sampled
times remain non-cycle-aligned.

**Priority therefore moves to the original JP $62 mode producer and
player Y/action/collision chain before the $D2FE call;** separately
check the $63 32-pixel boundary and $6B displacement result.
Do not patch the source $D2FE semantics or the player renderer on
the basis of this static/archived evidence alone.

**Next certification gate:** locate the first player-state/scroll-delta
CPU writer with a physically mapped PRG PC on an authentically
synchronized trace, including actor Y, Y speed, $0565 action, $05C1
fall/collision state and $62/$6B camera producer. Saved traces establish
state divergence but do not identify the first divergent CPU instruction,
a controller-bus timing defect, or a CHR render defect. No new gameplay
code or handlers; VPP remains 31/100 and strict PRG 49,504/262,144.
