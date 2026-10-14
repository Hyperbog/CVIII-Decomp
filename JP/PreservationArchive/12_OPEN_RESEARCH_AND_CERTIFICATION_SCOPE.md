# 12 — Remaining Evidence, Research Queue and Documentation Certification Rules

**Status:** ACTIVE research ledger; **NO STATIC OR RUNTIME COMPLETION CERTIFICATE**. The archival chapter structure is complete as a starting skeleton only; many game subsystems lack original proofs. RLOFT's final certificate demonstrates how to delimit claims; it does not transfer certification to this project.

## Current scope as of committed 0507

- Strict semantic PRG lower bound: **49,404/262,144 (18.8461%)**.
- Structural exact-or-normalized JP↔US candidates: **149,607/262,144 (57.0705%)**, not verified code or tested parity.
- **24/100 VPP**; most stage/world, combat/player, bosses, audio output, and native executable/runtime work remains.
- Fixed PRG31 investigation frontier **$FB96**, with explicitly unclaimed holes $FAA0-$FAA9, $FB96-$FBF5, $FC17-$FC1E, $FD59-$FDE3, $FEEA-$FF55 and $FF7A-$FFFF. Consult live [resume](../analysis/RESUME_STATE.json) before any new work.

## Immediate evidence queue

1. [0507 room entry](../analysis/NMI_BANK0A_ROOM_DISPATCH_0507.md): prove $18=0D liveness, $19 selector/alias range, $68 cross-frame producer and the $B6A4 carry gate; then promote *only* actually justified room-loader/FB96 ranges.
2. [AI](05_AI_SCRIPT_AND_ACTION_VM.md): show actual producers of script IDs $24/$25/$26, subscript indexes and execution of $FC17 calls; resolve source of state-dependent handlers rather than mechanically accepting pointer-table width.
3. [Tile lookup](../analysis/FIXED_TILE_PROBE_0505.md): bound $54/$14 producers, indexed FD62,Y CPU-visible reads and overlap with fixed code bytes.
4. [OAM shared state](03_PPU_OAM_SPRITE_PIPELINE.md): reconstruct final ZP $10 writer ordering and 256-byte OAM frame goldens.
5. [Audio](07_AUDIO_STREAMS_VRC6_APU.md): full driver/stream-to-APU/VRC6 register trace and native sound.
6. Entire stage/world progression, physics, enemies, bosses, menus/passwords/endings and alternate branches not yet described.
7. Full mapped 6502 instruction tests, NMI/IRQ traces, PPU and frame parity; native boot-to-ending coverage.

## Future publication gate (not currently passed)

Only consider static archive certification after: all planned chapters have a defined bounded scope; cross-links resolve; claims have ROM/audit addresses and evidence grades; overlapping claims and Q/D/L/C/U unknowns are reconciled; every remaining unknown is explicitly bounded; a final **independent original-source audit** states tested inputs and exclusions. A static certificate must never imply executable/native full-game parity, original design source ownership, or a faithful replica of unverified alternate Japanese/US editions.

## Checkpoint update contract

A checkpoint producing new observations must update the owning chapter or [10](10_QUIRKS_CORRECTIONS_AND_UNKNOWNS.md) and record **what was ruled out** as carefully as what was proved. A provisional atlas hit never becomes a live code/data claim from repetition. Commit analysis/audit first, archive chapters and their link audit next, progress and continuity after, and [machine resume state](../analysis/RESUME_STATE.json) LAST. No checkpoint is credited solely for publishing prose.


## Stable research tasks (R-IDs)

The Q/D/L/C/U register in [Chapter 10](10_QUIRKS_CORRECTIONS_AND_UNKNOWNS.md) classifies facts, but this table assigns **actionable proof work**. As in RLOFT, retain these IDs permanently; append new IDs rather than renumbering. A task becomes PROVED only with a committed Japanese-ROM/trace witness, exact input/mapper state and regression.

| ID | Priority | Status | Concrete evidence required |
|---|---|---|---|
| R-001 | P0 | OPEN | Prove NMI selector $18=0D and live room states $19/$68 across NMI/IRQ/frame boundaries |
| R-002 | P0 | OPEN | Establish B6A4 carry-flag precondition, $07A0 pointer table bounds, and promote justified $0A room graph bytes |
| R-003 | P0 | OPEN | Prove live producers of AI script IDs $24/$25/$26, subscript indexes and calls to fixed $FC17, or refute with source evidence |
| R-004 | P0 | OPEN | Reconstruct actual ZP $10 final writer/value at PRG26 renderer entry for representative and edge frames |
| R-005 | P0 | OPEN | Resolve both $54/$14 producer domains and the full $FD62,Y indexed ROM read range |
| R-006 | P0 | OPEN | Build repeatable 2A03/mapper/PPU reset–NMI–IRQ original-vs-native trace comparisons |
| R-007 | P1 | OPEN | Attribute every VRC6 + APU sound register event and certify a bounded audio-parity test |
| R-008 | P1 | OPEN | Prove stage/room layouts, route progression, character movement, enemy/boss states and serialization |
| R-009 | P1 | OPEN | Classify remaining fixed PRG31 raw gaps as actual code/data with nonoverlapping source manifests |
| R-010 | P2 | EVIDENCE DEPENDENT | Recover authentic original author/developer identifiers or alternate-release source media if available |

P0 = needed for faithful native runtime; P1 = subsystem documentation and reconstruction; P2 = historical/source archaeology. Closure must link a specific byte audit and/or reference trace; the absence of a trace is not a defect in the *static* description, but forbids native parity claims.

## Interim checkpoint-0508 research commits (R-001/R-002/R-004; still OPEN)

The [Phase 1–5 research commit](https://github.com/Hyperbog/CVIII-Decomp/commit/bcf85ba64b50611a2ae7e7220cbadec8742202f3) preserves reproducible ROM audits and local findings, **without closing checkpoint 0508**. See [Phase 5 conditional bank-$0E streams](../analysis/0508_PHASE5_FINDINGS.md) and the [Phase 6 IRQ preservation audit](../analysis/0508_PHASE6_FINDINGS.md). The latter proves that the previously admitted IRQ-handler graph does not overwrite key room-loader pointer/index/state RAM, but no original reset-to-room trace, all-writer global bound, or native full-frame parity exists. R-001, R-002, R-004 and R-006 remain OPEN. The strict coverage floor stays 49,404 bytes and VPP stays 24; consult RESUME_STATE for the last **completed** checkpoint.


### 0508 Phase 7 provisional evidence — R-001 remains OPEN

[Phase 7](../analysis/0508_PHASE7_FINDINGS.md) reproduces the original 6502 `E7FB` stack ABI and conditional pair `$18=$0C,$19=$13` → `$B36B` → `$18=$0D,$19=0` → next dispatch `$B570` under an explicit no-intervening-writer assumption. 65,536 cases pass; this does not prove the first input pair is reached from reset or close all NMI-side writers. Phase 6 showed the already-admitted IRQ graph preserves the relevant selectors. **R-001 and R-002 remain OPEN, with no new strict PRG bytes or VPP.** The completed-checkpoint and raw-frontier values above are unchanged.

### 0508 Phase 8 bounded evidence (R-001/R-002 remain OPEN)

[Phase 8](../analysis/0508_PHASE8_FINDINGS.md) proves from ROM-executed instructions that the **conditional** room state-zero `$B570` prefix clears `$07A0/$07A6/$0789/$68` and restores `$0781`, stopping before fixed `$EB82`. This narrows the room-index source to a known zeroing point **for that entry only**; it does not bound later producers, prove the initial NMI selector pair is live, or close $EB82 effects. Exactly 768 local tests pass. Research evidence only; strict floor **49,404**, VPP **24/100**, machine frontier **$FB96** unchanged.

### 0508 Phase 9 bounded state-one transition (R-001/R-002/R-006 still OPEN)

[Phase 9](../analysis/0508_PHASE9_FINDINGS.md) runs 512 original ROM-backed conditional `$B570→EB82→B589` executions. It fully consumes fixed `$EC1D-$EC46` stream data and tests 2,048 `$2007` writes plus RAM/index/stack postconditions under increment-1 and increment-32 PPUCTRL. It demonstrates a local `$19:0→1` state handoff with `$07A0/$07A6=0`, **not** actual gameplay reachability, arbitrary PPU/NMI/IRQ timing, later `$B58C` behavior, or a global room index bound. Fixed PRG stream bytes are already counted; strict coverage remains **49,404**, VPP **24/100**, resume checkpoint **0507**, frontier **$FB96**.

## 0508 Phase 10 evidence — research tasks remain open

[Phase 10](../analysis/0508_PHASE10_FINDINGS.md) establishes the conditional $B58C -> $E249 -> raw-bank-$0C:$8850 -> $87AE original sound-reset path with 256 bounded tests and nine APU/VRC6 bus writes. The music interpreter after $8860, its proper return, and any $25/scratch interactions remain unexecuted. A separately injected return proves only a conditional state-one-to-two suffix; it does not close R-001, R-002 or R-007. The authoritative strict floor remains 49,404 PRG bytes, VPP 24/100, checkpoint 0507, and fixed PRG31 frontier $FB96.


## Provisional research refinement: 0508 Phase 11 (no completion certificate)

[Original-ROM conditional execution](../analysis/0508_PHASE11_FINDINGS.md) closes the state-one command-$6B sound metadata return: six raw-$05 instrument byte reads, 20 raw-$0C metadata bytes, 14 mapper writes and real RTS to room state two across 256 cases. **R-001 and R-002 remain OPEN** because reset-to-NMI liveness and the B6A4 carry/index path are unproved; **R-007 remains OPEN** because full audio event/waveform parity is absent. This is a provisional result committed to Git, **not** a new strict-coverage certificate; 49,404/262,144 and VPP 24/100 remain authoritative from completed 0507.


## Large-batch completion plan — 2026-10-09 (policy, not a new byte certificate)

See [subsystem progress and large-batch completion roadmap](../docs/COMPLETION_ROADMAP.md) for the fixed VPP category percentages, the eleven-phase zero-credit stall diagnosis, ≥16 KiB bank-level discovery target, the evidence-qualified 8–16 KiB new-byte ambition, M1–M8 system milestones and explicit Git/recovery discipline. The immediate blocker is an original reset/frame producer witness for $18/$19/$68 and $07A0/$07A6; R-001 and R-002 stay OPEN. This entry changes neither VPP, strict PRG coverage nor RESUME_STATE.


## 0508 bulk methodology application (provisional research, R-001/R-002/R-006 OPEN)

The initial [32-KiB bank-$0A/$0E + 256-KiB producer-encoding census](../analysis/0508_BULK_0A0E_FINDINGS.md) and [general CPU/mapper partial trace core](../analysis/0508_TRACE_CORE_AND_E7FB_CORRECTION.md) replace repeated one-handler interpreter fragments. The former proves RAM clear `$18=$19=$68=$07A0=$07A6=0` at reset-loop end and separates **2,505** tagged candidate/already-audited bytes; the latter executes **334,912** original instructions across two conditional subsystems and catches native E7FB selector `$7F/$FF` high-byte wrap error. Both are committed **without** claiming reset-to-gameplay selector liveness, full 2A03/VRC6/PPU/IRQ parity, extra PRG bytes or VPP points. Next is a real reset-to-NMI frame reference trace and fully producer-qualified state-two gate; R-001, R-002, R-006 stay OPEN. Source error C-003 is recorded in [chapter 10](10_QUIRKS_CORRECTIONS_AND_UNKNOWNS.md).


### M1 executable cold-start trace boundary — provisional, not external parity

[450 manually injected NMIs](../analysis/0508_RESET_NMI_SYNTHETIC_TRACE.md) across three synthetic CPU-idle budgets execute **1,599,939** ROM instructions from the original RESET vector with stubbed PPU status, controller zero and no IRQ. The tested pair starts `$18=0,$19=0`, first NMI advances to 0/1 and no-input tests stay 0/1. This **narrows** reset origin but does not close R-001: actual gameplay path `$18=$0C,$19=$13` has no hardware/input/timing witness. R-006 remains OPEN because the harness does not supply reference-emulator cycles, PPU, IRQ or true input; it is a preparatory trace framework, not a completed VPP gate. All percentages remain unchanged.


### 0508 expanded multi-bank dynamic producer census (R-001/R-002/R-006 remain OPEN)

The [physical-byte and RAM-writer manifest](../analysis/0508_BULK_DYNAMIC_PRODUCER_TRACE.md) records 4,669,348 original ROM instructions across 1,800 artificial NMIs, union 11,127 fetched code/operand physical bytes and 16,718 PRG bytes read; **all discovery, not new strict coverage**. Nineteen forked post-`$18=04` controller schedules exercise 7,132,248 additional instructions and 2,280 additional NMIs without reaching `$18=0C/0D`. Since NMI is injected manually and the PPU/IRQ schedule is simulated incompletely, these are bounded negative observations only. Next evidence requirement is a genuine reference-timed reset/playthrough trace and producer-domain closure. 0507 remains last completed checkpoint; VPP 24/100, strict PRG 49,404/262,144 and fixed `$FB96` frontier are unchanged.


### 0508 experimental modeled-vblank NMI progression (R-001/R-006 not closed)

The [CPU-cycle/PPU-vblank synthetic trace](../analysis/0508_EXPERIMENTAL_VBLANK_CYCLE_TRACE.md) models nominal CPU instruction timing and vblank-generated NMI edges rather than manually injecting every NMI. Three synthetic controller scenarios produce **8,864,752 original ROM instruction steps**, **948 modeled NMI entries**, and `$18=00,02,0A,09,03,04` on the broadest trace, but neither original reference-emulator trace parity nor `$18=$0C/$19=$13` gameplay liveness is established. Key gaps: instruction-cycle PPU access precision, VRC6 IRQ, real OAMDMA, CHR/PPU rendering, CPU/PPU odd frame timing and authentic controller input. VPP and strict PRG unchanged; R-001, R-002, R-006 OPEN.


### 0508 bulk IRQ-vector experiments — R-006 remains OPEN

[Integrated IRQ source, CPU-vector execution and NMI experiment](../analysis/0508_VRC6_IRQ_INSTRUCTION_BOUNDARY_TRACE.md) reuses the repository's native VRC6 IRQ semantics and runs 350 original-ROM IRQ handlers to RTS/RTI return across 960 synthetic frames, with 948 NMIs and 8,861,056 original instruction steps. The verified source/handler paths and 267 component checks are useful for M1 trace infrastructure, but these are **not independent reference-console traces**. R-001/R-002/R-006 stay OPEN. Strict PRG 49,404/262,144; VPP 24/100; fixed frontier $FB96; RESUME_STATE remains checkpoint 0507.


## 2026-10-09 independent CI/testing gate (VPP 25/100, byte frontier unchanged)

[Successful native CI build and tests](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/37993214808) now close the previously open **reproducible build-and-test gate**, one fixed validation point. Eight native binaries compiled and four ROM-free suites executed on GitHub Actions; local SHA-verified Japanese ROM enables the four ROM-dependent suites. The reference CPU/PPU trace, frame parity and bootable native game remain OPEN. VPP **25/100**; strict PRG **49,404/262,144**; completed checkpoint **0507** and next fixed frontier **FB96** unchanged. The 0508 research trace claims above remain provisional.


## Cross-game research accelerator — reusable NES/FDS source and signature evidence

The [SharedNES library](../SharedNES/README.md) and its [source catalog](../SharedNES/SOURCE_CATALOG.md) record current and historical NESdev material, older archived documentation, emulator debugger/test ROMs, cc65/da65, FDS BIOS API/revision aids, VRC6a/VRC6b and the supplied three PDF references. Its [ROM-byte-safe JP↔US initial comparison](../analysis/NES_REUSE_JP_US_CANDIDATES.json) detects 364 sampled exact 32-byte candidate windows (348 unique-target) from 1,018 sampled windows; **none is proven a live shared routine**. Per-game caller/mapper/register/data producers and RAM side effects remain mandatory. The common CPU/PPU/FDS model can be reused, but neither 2026 community forum anecdotes nor vendor name alone certifies Konami game-code sharing. The original-ROM and source-code rights remain separate. This is documented research/tooling only: **VPP 25/100; strict 49,404 PRG bytes; semantic checkpoint 0507 unchanged.**


## Shared code-reuse provenance study (2026-10-09, not checkpoint completion)

[Source-certified JP 0501 ↔ US cross-edition census](../SharedNES/JP_0501_CROSS_EDITION_REUSE.md) identifies 1,273 of 4,364 already verified Japanese source PRG bytes under unique 16-byte US physical-PRG signatures, with **31/31 source-range hash audits**. This is an accelerator for subsequent caller/bank/behavior proofs, not a new strict byte certificate and not cross-mapper equivalence. The ROM remains authoritative; the 0507 recovery checkpoint and 25/100 VPP are unchanged.

## 2026-10-09 — external Code/Data Logger ingestion boundary

The reproducible [FCEUX/Mesen CDL bridge and provisional JP/US exact-window census](../SharedNES/0508_CDL_CROSS_EDITION_EVIDENCE.md) imports genuine logs **only when separately supplied**, as metadata keyed by physical PRG offset. The measured 420 manually injected NMIs are a **synthetic CPU-instruction observer, not Mesen/FCEUX reference logging**. No original emulator-code/data log for full game parity is available from these tests. No change to R-001/R-002 live producer claims, strict 49,404 PRG bytes, or VPP 25/100.


## 2026-10-09 — First independent original-JP gameplay emulator evidence (supersedes prior synthetic-only limitation)

The [1,100-frame authentic Mesen2 mapper-24 gameplay witness](../SharedNES/0508_MESEN_ORIGINAL_GAMEPLAY_REFERENCE.md) now reaches first playable Stage 1 from RESET/title/name/prayer with normal controller input, collects **12,885 distinct physical PRG executed-code bytes** and independently overlaps **463 already admitted checkpoint-0501 bytes**. This is the first actual emulator-generated original-ROM reference/CDL for the project, separate from synthetic 0508 traces. It **does not** make all executed bytes strict decomp or establish mapper/IRQ state parity against our own runtime; it does establish authentic `$18=04` Stage 1 execution and identifies the earlier `$0A/$19=03` stall as normal name-entry waiting for START. Next: reconcile all physically unique observed starts/operands with the complete 0507 ledger and trace the original-game frame NMI/IRQ/mapper producer state to formal parity. **R-001/002 remain OPEN for `$18=0C/0D`**; stage/world item 0/20; VPP 26/100; semantic PRG 49,404; recovery state 0507 unchanged.


## 0508 independent original-game code admission / remaining certification scope

Independent Mesen2 original-JP Stage 1 route reaches playable BLK 1-02 in additional input forks and supplies actual program-counter breakpoints and physical CODE masks for [four previously uncredited fixed PRG31 fragments](../analysis/0508_MESEN_FIXED_LIVE_PROOF.md). **100 genuinely new code/operand bytes; 49,504/262,144 (18.8843%) strict JP PRG**, 26/100 VPP, fixed frontier FB96 unchanged. No raw ROM/CDL/savestate/image/trace is archived, only hashes, counts and regenerable source/test scripts. Source audited by [0508 script](../tools/audit_mesen_fixed_live_0508.py), linked to all seven gameplay forks in [branch corpus](../SharedNES/0508_STAGE1_MULTIBRANCH_REFERENCE.md). This is neither Stage 1 complete source reconstruction nor stage/world milestone progress; live $18=0C/0D, $19/$68 producer, full actor/script domains, native reference parity, and global 0507-byte overlap for *other* observed code remain OPEN. Future 0509 work should target these concrete gaps, not bulk-credit code flags.

## 0518 partial reference PRG reconciliation and scored native actor architecture

[0518 source and scoring decision](../analysis/0518_RECONCILIATION_AND_VPP_DECISION.md) maintains historical strict original-JP PRG **49,504/262,144**, checkpoint 0508, fixed frontier FB96. ROM-hash-locked 25 tracking windows contain 1,365 unique bytes; 546 in 0501 source certificate, 78 in 0508 new ranges, 741 outside those two references but not reconciled against 0502–0507. Two FF12–FF13 bytes are not in 0508 certificate. Independent original Mesen B1F8-to-FDFE 91-instruction connected actor collision/follower pipeline earns a separate gameplay movement/collision architectural point, shifting gameplay 2→3/25 and VPP 26→27/100. Source-positive contact, B243/B27C/B2A8 helpers, integrated frame, renderer R-004 and trace R-006 remain OPEN.

## JP0611 — R-007 sound-event boundary (research only)

See [JP0611 original ROM sound-request census](../analysis/0611_SOUND_REQUEST_ENTRY_CENSUS.md) and [self-contained ROM audit](../tools/jp_sound_request_census_0611.py). Fixed $E249's bank-$0C wrapper and three sound-command dispatch classes are ROM-byte verified, but 131 physical JSR/JMP patterns are **not** a live caller census. Required next: CPU-cycle-aligned E249 entry trace with A, mapper, caller stack context and hardware bus writes; independent reference validation of accepted versus suppressed requests. Do not claim independent music/SFX virtual voices, modify the hardware mixer, change strict PRG 49,504/262,144 or advance VPP 27/100. R-007 stays OPEN.

## JP0612 — R-007 original sound-request runtime ingress instrumentation

The [JP0612 implementation and limits](../analysis/0612_SOUND_REQUEST_RUNTIME_TRACE.md) observe real fixed $E249 instruction fetches, rather than accepting the 0611 physical pattern candidates as executable callers. Paired private request/register CSV outputs have not been collected and independently checked against original MesenCE audio timing. The event producers *before* $E249, any scheduler-dropped effects and music-versus-SFX voice allocation remain unknown. R-007 is OPEN; no original runtime/gameplay or native audio parity is certified.

## JP0615 — R-007 independent audio ingress parity still needs source captures

[JP0615](../analysis/0615_MESEN_SOUND_REQUEST_REFERENCE_GATE.md) prepares a hash-pinned original-Japanese-ROM Mesen2 execute callback for $E249 and a strict single-epoch JP0614 comparison. Three source-byte producer candidates ($B0C8/$06, $B1CE/$6A, $B58C/$6B) are authenticated; only $B58C has a historical conditional 6502 execution proof. No independent Mesen2 reference was actually executed in JP0615. Real matched controller inputs, original trace origin, request timing, game-side suppression and sound register ownership remain OPEN (R-007); unchanged strict PRG 49,504 and VPP27.

## JP0616 — R-007 dispatcher rejection branch proven structurally, liveness OPEN

The original JP raw-bank-$0C source establishes both $884F low-command guard and $8922 DMC-priority return predicates, and the prior $06DD increment even on some returns. [JP0616](../analysis/0616_ORIGINAL_SOUND_DISPATCH_GUARDS.md) covers all command/priority combinations with a bounded instruction-subset evaluator; Mesen independent guard-execution capture tooling is committed but has not run. No original Mesen2 sample proves any specific effect was muted, music/SFX ownership or eventual hardware output. R-007 remains OPEN; strict PRG 49,504/262,144, VPP27/100 unchanged.

## JP0617 — R-007 unified sound-dispatch trace prepared; authentic capture outstanding

The [unified JP0617 observer and parser](../analysis/0617_UNIFIED_SOUND_DISPATCH_REFERENCE.md) pair original driver $8852 commands with the $884F/$8860/$8922/$8928 decision boundaries, including $885D reset as an intermediate phase for $50–$6E. Original RAM $0109, $019E and $06DD is sampled before and after; a fail-closed parser distinguishes a selected branch from a proven audio output. Five synthetic paths and eleven negative tests passed. No Mesen2 execution, matched native run or earlier game-side sound trigger has been verified; R-007 OPEN. Strict PRG 49,504/262,144, VPP 27 unchanged.

## JP0618 — Enhanced shipping goal with gameplay fidelity

[JP0618 audio preferences](../analysis/0618_ENHANCED_AUDIO_LEVELS.md): The single player-facing product is Enhanced, while original Japanese gameplay and timing remain the reference baseline. Master/Music/SFX preferences are persisted as 0–100 in 1% increments, with an implemented enhanced-only Master PCM gain. Music/SFX separation and the health-bar-art/in-game-font slider interface remain pending, and original-Mesen source decisions are still relevant to reconstructing correctly independent buses. No semantic PRG/VPP promotion; native Windows/UI validation not claimed.
