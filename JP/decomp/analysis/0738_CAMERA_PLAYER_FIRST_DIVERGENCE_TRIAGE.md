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

There are no original/private MesenCE ZIP or native CYCFRAME logs in the current Project/Library file inventory or mounted workspace. The publicly available CI engine-only ELF is not a replacement for the archived controller schedule or missing capture pair. Therefore the augmented comparator has **not** been used to assert a new retail player-state result.

**Certification unchanged: VPP 31/100, strictly certified PRG 49,504/262,144 (18.8843%), checkpoint 0508.** ROM-free synthetic tests are not a real game parity pass.
