# Permanent technical discovery and behavior log

**Status:** ACTIVE. This is a readable, append-only *index* of major findings. It is not a substitute for physical byte manifests, the machine [resume state](../analysis/RESUME_STATE.json), or the narrative [subsystem chapters](README.md). All source claims must be rechecked against the immutable Japanese ROM and their linked audits.

## Historical checkpoint-to-behavior index

| Checkpoints | Technical discovery/behavior | Evidence |
|---|---|---|
| 04F2–04F4 | IRQ has 45 encoded states; fixed NMI and ED46 helper examined for shared-ZP preservation | [IRQ](../analysis/PRG02_IRQ_dispatch.md), [fixed NMI](../analysis/NMI_FIXED_ZP10_PRESERVATION.md) |
| 04F5–04FA | Bank $0C sound parser and raw bank $04 metadata parser, 96/96 roots; stream parameter bytes kept as data | [bank $0C](../analysis/NMI_BANK0C_PARSER_MODE.md), [raw $04](../analysis/NMI_BANK04_ALT_PARSER_BOUNDARY.md) |
| 04FB–04FD | Raw bank $05 sound parser, 72/72 roots; E7 index restricted by actual producer | [raw $05](../analysis/NMI_BANK05_PRG11_TAIL.md) |
| 04FE–0500 | $E7FB pops the JSR return and tail-jumps through inline pointers; $18/$2C/$68 encoded dispatches mapped with live-domain caveats | [E7FB ABI](../analysis/NMI_FIXED_E7FB_DISPATCH.md), [$68](../analysis/NMI_FIXED_68_DISPATCH.md) |
| 0501–0502 | Object scheduler calls banked collision paths; seven real bank-$0B ZP $10 writes; exhaustive native 8-bit collision math | [scheduler](../analysis/NMI_FIXED_SCHEDULER_BANKED_0501.md), [scratch](../analysis/NMI_BANK0B_COLLISION_ZP10_0502.md) |
| 0503–0504 | $BD11 AI-script interpreter; producer-backed script ID $1B, actions $0B/$45/$46; fixed $FC1F contributes five more ZP $10 writes | [script seed](../analysis/RAW0B_AI_SCRIPT_SEED_0504.md), [AI decoder](../analysis/RAW0B_AI_DISPATCH_NATIVE_0503.md) |
| 0505–0506 | Distinct $FD62,Y data index domain stays unproved; fixed $FB96 temporarily banks raw $0E, reads indirect and restores $0A; raw-$0A room state candidate transition | [fixed lookup](../analysis/FIXED_TILE_PROBE_0505.md), [banked loader](../analysis/CROSSBANK_AI_ATLAS_0506.md) |
| 0507 | Fixed NMI $E526 selects raw bank $0A and jumps $B4CC; exactly five new verified entry bytes; 281 starts/582-byte room graph remains conditional | [0507 JP proof](../analysis/NMI_BANK0A_ROOM_DISPATCH_0507.md) |

At 0507, conservative strict PRG floor is **49,404 / 262,144 (18.8461%)** and VPP is **24/100**. These are a historical snapshot, not a live metric. [PROGRESS.md](../docs/PROGRESS.md) and [RESUME_STATE](../analysis/RESUME_STATE.json) own current values.

## Negative discoveries and hypothesis corrections to preserve

- **C-001 (checkpoint 0500):** accounting error (933 vs 982 bytes) was fixed after recovering $F800-$F830; a *tooling mistake*, not a game bug.
- **Q-001:** The $E7FB inline dispatcher *intentionally* consumes its caller's JSR return and pointer literals.
- **Q-002:** ZP $10 is inherited by compressed sprite descriptors, but later collision/background code also writes to it; local audio-path preservation does not imply whole-frame preservation.
- **L-001:** Mechanical action $9E maps into script pointer/fallback data at $BEA3/$BF79; treating all 256 action words as live executable handlers would be false.
- **D-001:** Script IDs $24/$25/$26 have mechanically corresponding actions but no proved live script-ID producers; some tempting immediate values write unrelated RAM fields.
- **U-004 (separate domain):** $FD62,Y must not be limited to the modulo-12 $FD4D,Y index just because the reads share a helper.

See [Q/D/L/C/U register](10_QUIRKS_CORRECTIONS_AND_UNKNOWNS.md) for canonical ownership and current unknown status.

## Future update template

For each **completed** checkpoint, append:

1. Checkpoint ID, branch commit and authoritative ROM SHA.
2. Original machine fact — physical 8-KiB PRG / raw bank, CPU start/end and code/data classification; producer → parser/handler → consumer; register, stack, mapper/PPU/APU effects.
3. Evidence grade and reproduction command; distinguish static CFG, strict accounted byte manifest, native unit test and reference-emulator parity.
4. Corrections/contradictions, negative findings, Q/D/L/C/U IDs changed, R-IDs affected.
5. Strict new unique PRG bytes, strict cumulative PRG and VPP *without recounting*.
6. Exact next unknown and its proof requirement.

The owning chapter, this log, and the relevant Q/D/L/C/U entry should be updated in the same **semantic checkpoint** before progress/continuity, with the machine resume state **last**. Editing archival prose alone earns zero ROM bytes and zero parity points.

**Documentation adoption (separate zero-byte transaction):** modeled on the private [RLOFT PreservationArchive](https://github.com/Hyperbog/RLOFT/tree/code1-decompilation/PreservationArchive), while original JP bytes remain authority. No static archive completion certificate and no full native parity are claimed.

## Interim 0508 research preservation — not a completed checkpoint

The [Phase 1–5 research commit](https://github.com/Hyperbog/CVIII-Decomp/commit/bcf85ba64b50611a2ae7e7220cbadec8742202f3) records the bank-$0A 935-start candidate graph, predecessor $18 transition, $07A6 descriptor progressions, and five conditional bank-$0E room streams (175 bytes). Every claim is bounded and producer-domain caveats remain active.

[Phase 6](../analysis/0508_PHASE6_FINDINGS.md) independently checks all previously admitted IRQ handler roots and their local/fixed helper closure: 558 handler instruction starts and 138 handler write sites, with two $0789,X writes bounded away from room indices. Fixed E2D2 maps bank $01 on IRQ entry without altering the tracker $23, and E2D0 restores the tracked PRG bank on exit. This removes the **verified IRQ handler graph** as a writer of $08/$09/$10/$18/$19/$23/$54/$68/$07A0/$07A6; NMI interleaving and non-IRQ producer liveness remain unknown. **No new strict PRG-byte count, VPP or resume-state advancement** is inferred from the intermediate research commits.


## 0508 provisional research preserved in Git (not an authoritative checkpoint)

- **Phase 7:** [conditional two-entry NMI witness](../analysis/0508_PHASE7_FINDINGS.md) executes fixed `E51E` → raw `0A:AFA4` → `E7FB` → `B36B`, setting `$18=$0D,$19=0`. The next dispatch under unchanged selectors selects `B570`. All 65,536 test pairs pass under synthetic-parent and precondition constraints; no reset-to-frame liveness is asserted. R-001/R-002 remain open.
- Earlier 0508 [Phase 5](../analysis/0508_PHASE5_FINDINGS.md) records the bounded five-stream bank-`$0E` loader; [Phase 6](../analysis/0508_PHASE6_FINDINGS.md) records IRQ-side preservation of selector and pointer RAM. These are **provisional findings**, not newly credited strict ROM coverage. Current completed checkpoint remains 0507; 49,404 strict PRG bytes and 24/100 VPP.

### Provisional 0508 Phase 8 (not a completed checkpoint)

[ROM-backed state-zero prefix](../analysis/0508_PHASE8_FINDINGS.md): mapped raw `$0A:$B570` executes fixed `$E7B6` clear, zeroing `$07A0/$07A6/$0789/$68` while preserving `$0781` through `PHA/PLA` (stops at `$EB82`, 768 cases). This is a conditional initialization anchor for **R-001/R-002**, not a live selector-domain or five-pointer-table bound. No newly credited PRG bytes or VPP; retain completed recovery checkpoint 0507 until full reconciliation.

### Provisional 0508 Phase 9 — state-zero PPU stream and indexed room handoff

[Phase 9 ROM audit](../analysis/0508_PHASE9_FINDINGS.md): raw `$0A:$B570` conditionally calls fixed `$EB82`, which reads 42 previously counted ROM-data bytes `$EC1D-$EC46` to write 2,048 zeros to `$2007`. Return via `$B589` increments `$19=0→1`, preserving local `$07A0/$07A6/$68=0` and saved `$0781`. 512 original-instruction partial-PPU tests pass; increment-32 PPUCTRL produces VRAM-address aliases. R-001/R-002/R-006 remain OPEN because no reset-to-frame liveness or reference PPU trace exists. **Zero strict new PRG bytes, VPP remains 24/100, authoritative machine checkpoint still 0507.**

## Provisional research addendum — 0508 Phase 10

[ROM-locked Phase 10](../analysis/0508_PHASE10_FINDINGS.md): conditional bank-$0A:$B58C room state one passes immediate audio command $6B to fixed $E249, maps raw $0C, and runs $8850->$87AE sound reset (nine ordered APU/VRC6 writes, 256 bounded original-instruction executions). The actual sound parser is not followed past $8860. A distinctly *injected* hypothetical return checks the fixed bank-restore suffix and subsequent $68=0/$19=2 update; this is not proof of original audio-handler completion or live stage progression. R-001/R-002/R-007 remain open; register U-006. Zero newly credited strict bytes, 49,404/262,144 lower bound, VPP 24/100.


## Provisional 0508 Phase 11 — command-$6B original sound-return witness

[Audit and complete byte evidence](../analysis/0508_PHASE11_FINDINGS.md): raw VRC6 $0C:$9034 points to the 20-byte command-$6B metadata at $94B5-$94C8; six slot/pointers select raw bank $05, whose first byte is $D9 at every selected root. Original fixed $E19F maps $05 for each read then restores $0C; original $8850 RTS and fixed $E249 restore raw bank $0A and allow raw-$0A room $19=1→2, $68=0. **256 × 650 original-instruction tests passed**. This corrects the *Phase 10 research limitation* (previously injected hypothetical RTS), not original game behavior. R-001/R-002/R-007 stay OPEN. Strict new bytes 0, 0507 machine frontier unchanged. No sound waveform or reset-to-frame parity claim.


**Provisional 0508 bulk research (not a completed checkpoint):** [32-KiB raw-bank `$0A/$0E` manifest and reset-loop proof](../analysis/0508_BULK_0A0E_FINDINGS.md) records 2,505 distinct labeled bytes, only 120 known previously credited, with **zero newly promoted** bytes. [Generic 6502/VRC6 partial bus/trace core](../analysis/0508_TRACE_CORE_AND_E7FB_CORRECTION.md) passes 272 ROM-path cases and E7FB/ALU edge tests, finding **C-003:** the old partial native room decoder incorrectly read the second inline table byte without modeling 8-bit Y wrap at selectors `$7F/$FF`. Corrected source/test and Phase 2 audit/report retain ROM authority. Last completed machine checkpoint stays 0507; strict 49,404 bytes, VPP 24. Live selector provenance and original reference frame traces remain open.


**Provisional 0508 bulk M1 trace follow-up:** [ROM-fetched RESET + 450 synthetic NMIs](../analysis/0508_RESET_NMI_SYNTHETIC_TRACE.md), **1,599,939** original instruction steps, under exactly stated synthetic PPU/no-IRQ/zero-input conditions. Bounded first NMI `$18/$19:00/00→00/01`; repeated artificial no-input injections stay `00/01`. This is not reset-to-gameplay `$0C/$13` liveness or external emulator parity; R-001/R-006 remain OPEN, no new strict bytes/VPP.


**0508 extended synthetic dynamic-byte/RAM-producer census (research, zero strict bytes):** [reproducible multi-bank audit and controlled input fork](../analysis/0508_BULK_DYNAMIC_PRODUCER_TRACE.md) execute 4,669,348 + 7,132,248 original instructions respectively, cataloguing 11,127 distinct fetched physical instruction+operand bytes, 16,718 read PRG bytes and exact selector/room index writer sites. Nineteen cloned controller input policies remain in artificial first-level state `$04`; they are not proof real gameplay cannot reach `$0C/$0D`. Fixed `$F6AE` OR-guard and Start test are locally decoded. R-001, R-002 and R-006 stay OPEN; strict 49,404 PRG, VPP24 and 0507 machine frontier unchanged.


**0508 modeled-vblank CPU execution extension (provisional, zero new semantic bytes):** [technical evidence](../analysis/0508_EXPERIMENTAL_VBLANK_CYCLE_TRACE.md) adds 151-opcode timing-class checks and 960 synthetic PPU frames / 948 model-generated NMI entries / 8,864,752 original instructions under three input policies. The broadest first-level sequence is `00→02→0A→09→03→04`; no `$0C/$0D`. PPU, mapper IRQ and DMA timing not reference certified; this does not advance strict PRG floor 49,404, VPP 24/100 or last completed checkpoint 0507.
