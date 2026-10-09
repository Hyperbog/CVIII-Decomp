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
