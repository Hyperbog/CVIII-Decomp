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

**Certification unchanged: VPP 31/100, strictly certified PRG 49,504/262,144 (18.8843%), checkpoint 0508.** ROM-free synthetic tests are not a real game parity pass.
