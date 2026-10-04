# Decompilation progress ledger

## Current dashboard

```text
whole JP PRG scanned/indexed                 262144 / 262144 = 100%
strict semantically verified PRG floor        48823 / 262144 = 18.6245%
exact unique JP<->US correspondence           115865 / 262144 = 44.1990%
exact-or-normalized structural candidates     149607 / 262144 = 57.0705%
VPP                                             24 / 100
```

VPP is a fixed evidence rubric, not a byte-progress estimate. Cross-version and dispatch-atlas percentages/results are structural accelerators, not semantic verification.

Recovery: read `docs/INTERRUPTION_RECOVERY.md`, `docs/ACCELERATION_POLICY.md`, `docs/WHOLE_PRG_ATLAS.md`, `analysis/RESUME_STATE.json`; run `tools/check_resume_frontier.py` and the previous checkpoint audit before forward work.

## Durable foundation

- authoritative JP ROM SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`;
- US comparison ROM SHA-256 `1c7b2ed2c1fb5839a6764006aa476f5c9d48f99465b6141980f3a5af1dfec0d6`;
- JP: 256 KiB PRG, 128 KiB CHR, Mapper 24 / VRC6a; RESET `$E00B`, NMI `$E057`, IRQ `$E0F5`;
- IRQ table/state ledger and control-vs-ack behavior reconciled;
- native OAM renderer + tests;
- whole-PRG atlas + focused xrefs;
- exact and relocation-normalized JP<->US matchers + audits;
- native VRC6 PRG/CHR mapper + tests;
- native VRC6 IRQ timing/scheduler + tests;
- raw-bank `$0B` collision scratch/distance architecture + native exact-8-bit collision math/tests.

## Native VRC6 runtime components

### PRG/CHR mapper — earned VPP CPU/mapper item 8

`analysis/NATIVE_VRC6_MAPPER.md`, `src/vrc6_mapper.*`, `tests/vrc6_mapper_test.cpp` implement target-game PRG RAM enable, switchable 16 KiB/8 KiB PRG windows, fixed PRG31, Mapper-24 register mirrors, eight CHR registers/pattern modes and target CIRAM mirroring.

### IRQ timing/scheduler — earned VPP CPU/mapper item 9

`analysis/NATIVE_VRC6_IRQ.md`, `src/vrc6_irq.*`, `tests/vrc6_irq_test.cpp` implement `$F000` latch, `$F001` M/E/A control, `$F002` acknowledge, cycle mode and scanline-mode 341/3 prescaling. Tests verify the **114,114,113 CPU-cycle** cadence and the JP `$F001/$F002` distinction.

IRQ CPU polling/latency, full memory/PPU integration and VRC6 audio remain open.

## Shared ZP `$10` provenance through 0501

Earlier admitted IRQ/NMI/audio/fixed graphs, raw bank `$04` 96/96 roots and raw bank `$05` 72/72 roots preserve `$10`. The fixed `$E7FB`, 04FF `$2C` head and corrected 0500 `$68` graph are locally `$10`-clean.

0501 changed the global model and traversed:

```text
fixed PRG31                    161 starts    298 new bytes
raw bank $09                   479 starts   1050 new bytes
raw bank $0A                    57 starts    120 new bytes
raw bank $0B                  1338 starts   2896 new bytes
----------------------------------------------------------
0501                           2035 starts   4364 new bytes
```

Tagged manifest SHA-256: `639e20f7e96e816a40ef4ef7d8585c809ce670ac5384f3c2fabc9a77d275737e`.

Scheduler-proven banked roots:

```text
raw $0B: $80E3 $B1F8 $BD11 $8001 $8161 $826C
raw $09: $8001
raw $0A: $84EA
```

Raw banks `$09/$0A` are locally `$10`-clean. Raw bank `$0B` intentionally writes `$10` at exactly seven admitted sites:

```text
$B3B6 $B3D2 $B40E $B460 $B65F $B740 $B76C
```

## 0502 — collision scratch / final-writer ordering

Evidence:

```text
analysis/NMI_BANK0B_COLLISION_ZP10_0502.md
tools/audit_nmi_bank0b_collision_zp10.py
src/collision_math.hpp
src/collision_math.cpp
tests/collision_math_test.cpp
```

Fixed `$FDE4` calls `$B1F8` once near the start of each active outer slot `X=$01..$12`; later admitted per-slot bank `$09/$0B/$0A` calls are `$10`-clean. Therefore the renderer-facing value is the last `$B1F8` scratch write made by the latest active slot that takes one of the seven paths, or older inherited `$10` when none writes it.

Inside one `$B1F8` invocation the writer-family order is:

```text
early vertical/proximity ($B634/$B64B)
  -> object/player hitbox ($B339)
  -> active weapon probe ($B3EC)
  -> peer loop $B447 with $9B=$14,$15,$16
```

The seven writers are now identified as 8-bit wrapped coordinate/probe construction or adjustment, and `$B707/$B713/$B71D` plus `$80B3/$80C1/$80CB/$80D5` share the same unsigned 8-bit absolute-distance idiom.

`$B394-$B395 = 00 05` is locally indexed only by `Y=0/1`; those two bytes were outside 0501's `B323-B393` / `B396-B4D4` ranges and are the only newly promoted ROM bytes in 0502. Strict floor: **48,823 bytes = 18.6245%**.

The native `collision_math` lift preserves exact 8-bit wrap/absolute-distance/threshold semantics; its test exhaustively checks all 65,536 input pairs. This earns the first movement/physics/collision rubric point and advances VPP to **24/100**.

## Raw-bank `$0B` action-dispatch atlas

Evidence:

```text
analysis/RAW0B_ACTION_DISPATCH_ATLAS.md
tools/extract_raw0b_action_dispatch.py
tools/audit_raw0b_action_dispatch.py
```

The formerly opaque `$BD56/$BD64` exits are mechanically resolved for every 8-bit action value:

```text
$00-$7F -> word at $BD67 + 2*action
$80-$FF -> word at $BE67 + 2*(action-$80)
```

The 512-byte mechanical interpretation has SHA-256 `eb075c21401906325dc497d6537978590dccf193abc3897d42a4935533800a13` and yields 217 distinct raw-bank targets.

This is structural candidate coverage only. In particular `$9E` indexes `$BEA3`, which is also script-pointer data and mechanically yields `$BF79`; that alias is direct evidence that table shape cannot be used as a live action-domain proof. `$BD67-$BF66` is therefore **not** added to the strict semantic byte floor yet.

## `$FE95` dispatcher

`$FE8C-$FE95` shifts `$0565,X` right six times and calls `$E7FB`. `$FE98-$FE9D` contains exactly three encoded pointers: `$FE9E,$FEB1,$FEC6`. `$FE9E` is executable code, not a fourth pointer. Arithmetic selector `$03` remains an open producer-domain question.

## Cross-version acceleration

```text
exact unique JP bytes                 115865 = 44.1990%
exact correspondence runs                821
normalized unique starts              24014
normalized-candidate JP bytes         68009
exact-or-normalized candidate bytes  149607 = 57.0705%
calibration                           13232/13232 agree; 0 disagree
```

Evidence: `tools/match_jp_us_exact.py`, `tools/audit_jp_us_exact_match.py`, `analysis/JP_US_EXACT_MATCH_SUMMARY.md`, `tools/match_jp_us_normalized.py`, `tools/audit_jp_us_normalized_match.py`, `analysis/JP_US_NORMALIZED_MATCH_SUMMARY.md`.

## Critical invariants

- JP ROM and observed JP behavior control semantics.
- US labels/structures remain provisional until JP equivalence is demonstrated.
- table length never proves a selector/action domain;
- `$8000-$DFFF` traversal requires proven mapper state;
- semantic coverage is exact/noncontiguous; unreached bytes remain unclaimed;
- lossless ROM-equivalent generated dumps are never committed.

## Open edges / next checkpoint 0503

Primary: intersect the new `$BD56/$BD64` action atlas with **JP-proven live script/action producers**, then bulk-close the corresponding handler graph. Continue final `$10/$11` value-domain proof only from real object/state predicates.

Also open: raw-$0B `$E7FB` sites `$A15A/$A2CC/$A3A9`; raw-$09 `$E5DA` selected callees; `$0565>>6` selector `$03`; `$18/$2C/$68` producer closure; `$FAA0-$FAA9`; fixed raw frontier `$FB96`; complete mapper-register inventory; CPU trace parity; full native memory/PPU/audio/runtime.

The raw fixed investigation frontier remains `$FB96` because 0501 advanced from verified root `$FDE4` noncontiguously rather than claiming `$FB96-$FFFF` physically.
