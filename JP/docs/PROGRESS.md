# Decompilation progress ledger

## Current dashboard

```text
whole JP PRG scanned/indexed                 262144 / 262144 = 100%
strict semantically verified PRG floor        49404 / 262144 = 18.8461%
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


## 0503 — JP AI-script address lift (native and audited; zero newly counted bytes)

Evidence: `analysis/RAW0B_AI_DISPATCH_NATIVE_0503.md`, `src/ai_script_dispatch.hpp`, `src/ai_script_dispatch.cpp`, `tests/ai_script_dispatch_test.cpp`, `tools/audit_raw0b_ai_dispatch_0503.py`.

The exact JP raw-bank $0B interpreter at $BD11-$BD66 is now lifted into a CPU-bus-reader-based native address decoder, including script ID doubling, four-byte subscript-record addressing, 8-bit truncation, 16-bit carry and action bit-7 handler-table selection. Native tests cover all 256 mechanical action bytes and pointer-wrap scenarios; exact-ROM audit reproduces the $BD11-$BD66 hash `fbad027357da9de96af06f073ab22c6251d372af2a5f31a80edb0bf9e60f3e79` and the pre-existing 217 distinct mechanical targets. The decoder deliberately does not execute the stopwatch/script-$27 prechecks or write emulated CPU state.

A full-PRG raw-byte pattern census locates 96 candidate `STA $05EF,X`, 23 `STA $05EF,Y`, 5 `STA $05EF`, 2 `STY $05EF`, and 1 `ORA $05EF,X`. They are **not** verified live writers: code/data classification, mapper context, indexing, and indirect aliasing remain separate. In particular action $9E maps to script data at $BF79; do not promote all 256 entries.

**Strict verified floor stays 48,823/262,144 = 18.6245%; VPP stays 24/100.** All $BD11-$BD66 bytes were already counted in 0501. Next 0504: prove actual JP producer/value domains feeding $05EF,X and $05C1,X, then intersect live records and action values with the mechanical dispatch map. Raw fixed PRG31 frontier stays $FB96, $FAA0-$FAA9 unclaimed.


## 0504 — concrete AI-script seed, handler graph, fixed-$FC1F provenance

Committed evidence:
- `analysis/RAW0B_AI_SCRIPT_SEED_0504.md`
- `tools/audit_ai_script_seed_0504.py`

JP raw bank $0B:$B503 explicitly writes AI script $1B to $05EF,X, then calls $B516 to reset $05C1,X to $00. The ROM pointer at $BED9 resolves $B03A; the first three four-byte records give actions $0B/$45/$46, handler roots $8519/$965D/$96B4. Action $0B and $45 increment the subscript; $46 decrements the object timer and follows movement/cleanup logic. Five parameter tables have an eight-entry proven index bound from AND #$07.

The third handler calls fixed PRG31:$FC1F. Its 185-instruction local graph is mapper-stable (no JSR/indirect JMP or mapper-register write) and has **five direct ZP $10 stores**: $FBFC STA, $FC1F STA, $FC4F STA, $FCA0 STY, $FCF9 STY. This expands the final-$10 writer domain beyond the seven raw-bank $0B collision sites. The indexed $FD62,Y ROM producer is **still unproved** and those possible data bytes remain uncounted; $FD4D,Y is bounded to 12 entries by the local modulo-$0C loop.

**0504: 256 decoded instruction starts, 504 new code/operand bytes, 72 bounded data bytes, 576 new strict bytes.** Sixteen exact noncontiguous manifest ranges, SHA-256 `4416db601cba553569d4ccc4aba410a6d843a6da3504dac1d735317ca1106eb4`. New conservative floor **49,399 / 262,144 = 18.8442%**, **VPP stays 24/100**.

Bulk *structural-only* directory: 107 mechanical script IDs ($00-$6A), 72 distinct pointers, 71 aligned candidate starts, 792 four-byte lattice positions in $A4A6-$B105; not all candidate records or action bytes are live. Preserve pointer/record liveness policy.

Next 0505: close $FD62,Y index domain, expand mapper-aware script-ID/record producer seeds, and reconcile all new fixed $10 writers with scheduler/render ordering. The fixed physical frontier is still $FB96; $FAA0-$FAA9 remains unclaimed.


## 0505 — exact fixed-tile index lift and candidate source acceleration

Committed evidence: `analysis/FIXED_TILE_PROBE_0505.md`, `src/fixed_tile_probe.hpp`, `tests/fixed_tile_probe_test.cpp`, `tools/audit_fixed_tile_probe_0505.py`.

ROM-exact fixed PRG31 $FD11-$FD2B address/data behavior is now separately lifted to a CPU-bus-reader native primitive. Two known Y producers reach the $FD62,Y high-table read: ($54 + low-coordinate carry)&$FF from $FD0A-$FD10, and ($54 + $14 + carry)&$FF via $FC76-$FC7A. Neither currently has a whole-program live value bound. Thus the conservative read range is $FD62-$FE61, including fixed program code. **Do not clamp Y, silently assume a small table, or promote the potential 256 source bytes.** The different $FD4D,Y lookup is reduced modulo 12 by admitted code and its twelve bytes were counted in 0504.

Native regression covers **524,288** combinations of (8 low-coordinate equivalence classes, all 256 high-index values, all 256 fine offsets), including explicit Y=$FF reading executable fixed-bank bytes. It is **algorithm test evidence, not full CPU/PPU parity**.

The whole-PRG tool adds two reusable candidate lists: **156 raw JSR patterns** to fixed $FB96/$FBA5/$FC17/$FC1F/$FCDE (11/4/6/43/92 respectively), and **37 raw LDA #id; STA $05EF,X patterns** across banks 02/03/09/0A/0B/0C. These remain **unverified code/data and mapper-state candidates** until producers/callers are admitted. The 8-byte $FC17 alternate entry remains unclaimed.

**0505 advances tooling and native functionality, but adds 0 strict PRG bytes. Total stays 49,399/262,144 = 18.8442%; VPP remains 24/100.**

Next checkpoint 0506: prove JP mapper-selected inbound calls to $FB96/$FC17, bound live $54/$14 for $FD62,Y, and expand executable $05EF script-ID producers; preserve fixed physical frontier $FB96 and all six current gaps.


## 0506 — temporary VRC6 bank-read native lift and AI-script cross-links

Committed `analysis/CROSSBANK_AI_ATLAS_0506.md`, `src/temporary_prg_bank_read.hpp`, `tests/temporary_prg_bank_read_test.cpp`, and `tools/audit_crossbank_ai_atlas_0506.py`.

Fixed PRG31 $FB96-$FBA4 is a real conditional mapper transaction: writes $0E to $23 and $8000 through fixed $E2D0, performs LDA ($08),Y in the newly selected raw PRG bank $0E, then restores raw bank $0A through the same helper. Native mapped-bus regression passes **65,537 cases** (all 256 pointer-low × 256 Y combinations plus a wrap case), checking mapped value, write order, mapper restoration, and N/Z of returned A. This is a bus transaction partial lift, not CPU stack/frame parity.

Raw bank $0A:$B597 calls $B689, whose E7FB dispatch includes eleven encoded targets, index zero $B6A4. That target can call $B7F7, a room/object field loader with **eleven actual JSR $FB96 opcodes**. $B825/$B827 masks and stores low nibble into $54, so its **local** produced value is $00-$0F; no whole-program $54/$14 or FD62,Y domain is claimed. The $68 dispatch producer and inbound bank mapping still lack full liveness proof.

Candidate script IDs $24/$25/$26 contain first/second record actions $5D/$5F/$89, mechanically selecting raw bank-$0B handler roots $8DC6/$8E10/$8DF9, which contain calls into fixed $FC17. All three script IDs and the $FC17 caller graph remain **structural candidates** until runtime producers are proven. The candidate script directory remains 107 pointers, 72 distinct words, 71 aligned starts and 792 possible lattice cells; 156 raw JSR patterns and 37 immediate script-store patterns remain undecided.

**0506 adds zero newly proven ROM bytes**; strict floor **49,399/262,144 = 18.8442%**, VPP **24/100**. The source/test and ROM audit add a native mapper primitive and a much narrower producer-resolution queue without artificially advancing physical PRG coverage.

Next 0507: prove mapper-selected entry to $0A:B597/B689 and live $68=0; prove live source IDs $24/$25/$26 and $FC17 inbound calls; carry $54/$14 provenance through FD62,Y. Physical frontier $FB96 and six pending gaps remain unchanged.


**0506 follow-on producer proof:** JP raw bank $0A:$B4CC has 12 encoded $19 dispatch pointers (index 1 $B58C, index 2 $B597). $B58C calls $B4E9 to set $68=0 and increments $19, while $B597 calls the $68 dispatcher $B689. Under uninterrupted local state evolution, this is the missing conditional index-zero link to B6A4/B7F7. Still NOT global runtime proof: $19/$68 may change between frames, active VRC6 bank at B4CC unproven, and B6A4 has a carry gate. Supplement audit `tools/audit_bank0a_state_chain_0506.py`, appended analysis `analysis/CROSSBANK_AI_ATLAS_0506.md`. No additional ROM bytes promoted.


## 0507 — NMI maps raw bank $0A room dispatcher; 582-byte conditional CFG

Evidence: `analysis/NMI_BANK0A_ROOM_DISPATCH_0507.md`, `tools/audit_nmi_room_dispatch_0507.py`, native `src/room_state_dispatch.hpp`, test `tests/room_state_dispatch_test.cpp`.

The prior-admitted fixed first-level NMI inline pointer entry **index $0D -> E526** selects raw bank **$0A** by `LDA #$0A; JSR $E2D0; JMP $B4CC`. Fixed E2D0 writes $23 and VRC6 $8000. This closes the **bank identity** for the switched $B4CC entry. Raw-bank-$0A:$B4CC-$B4D0 (`A5 19 20 FB E7`) is five **new verified code/operand bytes**, physical 8-KiB PRG21, SHA-256 `0cbfd39d34523da29edaa6a2dcf5cdb4b62de628d0e5568ea3879d7de5a1c0c7`.

All **12 encoded state words** $B4D1-$B4E8 and secondary $68 entry0 $B6A4 seed allow a conditional official-opcode graph of **281 starts / 582 candidate code bytes** across six spans, with zero illegal opcodes/overlaps; fingerprint `807363d09368f7ae6ceaeae000df0fc50f56bba5bd2871ca749d7236ec9f3828`. **Only the five B4CC bytes are added to strict coverage**; $19 selector live domain, fixed-return bank contexts, B6A4 carry gate, $07A0 pointer table bound, and $18 index0D liveness remain open. Fixed $FB96 and $FC17 are NOT newly credited.

Native partial `E7FB` address/flag lift tests all **65,536** selector/Y pairs on JP bank0A ROM, including 8-bit ASL alias, C from selector bit7, Z/N from the ABI's restored incoming Y. No stack or scratch-RAM parity is claimed.

Negative AI producer evidence: bank0B `A9 24` at $863B writes $0606,X, `A9 25` at $9234 writes **$05C1,X**, and `A9 26` at $9531 / `A9 24` at $B4BC call $E249. None is a **direct** $05EF,X script-ID initializer. Indirect script-ID producers may still exist.

Strict verified floor **49,399 -> 49,404 / 262,144 = 18.8461%**; structural index **57.0705% unchanged**, VPP **24/100**. The six fixed physical gaps persist and fixed raw investigation frontier remains $FB96.

Next 0508: prove $18/$19 and $68 cross-frame values, B6A4 carry-gated B7F7 loader, mapper restoration across the encoded state handlers; resolve $07A0 pointer/data domain, then promote warranted conditional bytes in bulk. Also prove actual script IDs $24/$25/$26 and FC17 path; revisit FD62,Y/$10 provenance.


## Preservation Engineering Archive — documentation workstream established after 0507

The connected private `Hyperbog/RLOFT` `PreservationArchive` was reviewed for its scoped evidence grades, canonical subsystem chapters, original quirks/dormancy/corrections/UNKNOWN registers, programmer reference and deliberately separate static-certification process.

A new **`JP/PreservationArchive/`** directory now contains 13 substantive numbered chapters `00..12` and a README/index, adapted to this JP 6502/VRC6 decomp: ROM provenance, mapper, RESET/NMI/IRQ, OAM/PPU, object/collision, AI bytecode, room/world data, sound, native recomp, JP↔US atlas, Q/D/L/C/U ledger, programmer/modder contracts and open certification targets. The original ROM is NOT committed.

New `JP/tools/audit_preservation_archive.py` and GitHub workflow `.github/workflows/nes-preservation-archive.yml` validate chapter sequence and local links; this checks documentation structure, **not ROM semantics or native parity**. The acceleration policy, interruption recovery and continuity playbooks mandate archival updates alongside future semantic checkpoints.

This **documentation-only** transaction adds **0 newly verified PRG bytes** and **0 VPP**: the committed 0507 floor remains **49,404 / 262,144 = 18.8461%**, score **24/100**, and next semantic checkpoint **0508**. No source-path liveness, broader gameplay completion, or static documentation certification is inferred from the archive's existence.


## Forward completion plan — large verified subsystem batches (2026-10-09)

The score and strict-PRG dashboard above remain unchanged at **VPP 24/100 and strict 49,404/262,144**, despite eleven committed provisional 0508 research phases. Follow the new [subsystem-by-subsystem percentage dashboard, large-batch policy and acceptance-gated completion roadmap](COMPLETION_ROADMAP.md). Effective immediately, prioritize trace-backed selector producer closure and bank-scale room/stage sweeps over further single-handler micro-phases. The plan is not itself PRG or VPP evidence.
