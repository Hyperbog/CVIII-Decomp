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
