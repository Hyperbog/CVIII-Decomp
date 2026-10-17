# Decompilation progress ledger

## Current dashboard

```text
whole JP PRG scanned/indexed                 262144 / 262144 = 100%
strict semantically verified PRG floor        49504 / 262144 = 18.8843%
exact unique JP<->US correspondence           115865 / 262144 = 44.1990%
exact-or-normalized structural candidates     149607 / 262144 = 57.0705%
VPP                                             31 / 100
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


## 0508 bank-scale research and native E7FB fidelity repair (no new credit)

After the [large-batch roadmap](COMPLETION_ROADMAP.md), a [32-KiB raw `$0A/$0E` pass](../analysis/0508_BULK_0A0E_FINDINGS.md) produced a physical candidate/previously-credited dependency manifest and 32-case RESET RAM clearing proof. A [reusable 151-official-opcode Python 2A03/VRC6 partial instruction-stepper](../analysis/0508_TRACE_CORE_AND_E7FB_CORRECTION.md) independently replays 334,912 original instruction steps across room initialization/PPU zeroing and sound command return. It revealed/corrected a native `$E7FB` high-byte read anomaly at selectors `$7F/$FF`; original sender stack/Y are now modeled and the C++ 65,536-case test was repaired. **All are provisional bounded/local proofs**: no full reset-to-NMI reference trace, no frame/native/audio parity, no new strict PRG bytes and no additional VPP points. Authoritative **49,404/262,144 (18.8461%)**, **24/100 VPP**, machine completed 0507, raw fixed frontier `$FB96`. Do not count the 2,505 classified bytes as additional coverage.


## 0508 multi-frame synthetic RESET/NMI instruction trace (provisional)

The [reusable 2A03/VRC6 stepper's RESET trace](../analysis/0508_RESET_NMI_SYNTHETIC_TRACE.md) runs original reset and **450 manually scheduled NMIs / 1,599,939 original CPU instructions** over three synthetic idle-loop budgets. Under fixed PPU readiness, zero controller and absent IRQ, original state is reset `$18/$19=00/00`, transitions to `00/01` on the first NMI and remains there. **This is not a frame timing/audio/PPU/video/reference-emulator test** and cannot establish live gameplay input, progression to `$18=$0C`, or new semantic-coverage/VPP credit. Machine last completed 0507, fixed frontier `$FB96`, strict floor 49,404 bytes, VPP 24/100 unchanged.


## 0508 expanded execution manifest — synthetic traces, not strict bytes

[The physical PRG/producer manifest](../analysis/0508_BULK_DYNAMIC_PRODUCER_TRACE.md) replays 1,800 manually injected NMIs under three controller schedules: **4,669,348 original ROM instructions**, with a **physical unique union of 11,127 executed code-and-operand bytes** and **16,718 PRG bytes read** across many banks. A separate cloned-state input search runs 19 controller policies × 120 NMIs = **2,280 additional NMIs / 7,132,248 instructions** from artificial state `$18=$04`. None reaches `$18=$0C/$0D`; some advance `$2C` through 0–3. These are not genuine hardware-playthrough reachability or new strict PRG; producer-site evidence and exact physical-mask hashes are in the linked audit. Next step: reference-timed PPU/NMI/IRQ + controller trace and actual room-entry provenance. **Verified PRG remains 49,404/262,144 (18.8461%), VPP 24/100; completed machine checkpoint 0507 and PRG31 `$FB96` unchanged.**


## 0508 modeled-vblank experimental NMI batch (infrastructure, zero strict-credit)

The [experimental cycle/vblank execution report](../analysis/0508_EXPERIMENTAL_VBLANK_CYCLE_TRACE.md) adds a mapped original-ROM CPU instruction-cycle accounting and modeled PPUSTATUS/PPUCTRL/NMI-edge scheduler. Three input cases run **960 modeled PPU frames, 8,864,752 original ROM instructions and 948 modeled NMI entries**. The 480-frame Start-pulse path reaches conditional `$18=00,02,0A,09,03,04` but not `$0C/$0D`; the independent unit audit passes cycle classes for 151 official opcodes and 27 representative opcode timings. CPU/PPU bus interleave, VRC6 IRQ, odd-frame PPU dot, DMA and reference-emulator parity remain unimplemented. This is not hardware gameplay liveness, a bootable native game, or a new score criterion: strict PRG **49,404**, VPP **24/100**, checkpoint **0507**, fixed frontier `$FB96` unchanged.


## Bulk 0508 IRQ-enabled RESET/NMI trace experiments (provisional)

[Reproducible VRC6 IRQ/CPU-vector experiment](../analysis/0508_VRC6_IRQ_INSTRUCTION_BOUNDARY_TRACE.md): 267 modeled IRQ component checks, 8,861,056 original ROM instruction steps in 960 modeled frames, 948 NMIs, 350 mapper IRQ vector entries and 350 corresponding returns. This explicitly replaces the previous no-mapper-IRQ experimental limitation for these bounded traces, **not** the still-missing cycle-accurate reference CPU/PPU/DMA trace or live room-$0C/$0D state proof. VPP remains **24/100**, strict PRG **49,404/262,144 = 18.8461%**, last completed resume **0507**.


## 2026-10-09 — Native regression CI gate (1 validation point; zero new PRG bytes)

[Green GitHub Actions run 37993214808](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/37993214808) proves a reproducible C++20 strict-warning build of all eight existing native subsystem tests; all four ROM-free executable suites passed; the fixed progress CSV and preservation-archive integrity audit also passed. Two accidental literal escaped-newline sequences in `tests/room_state_dispatch_test.cpp` and four in `src/room_state_dispatch.hpp` were repaired to restore an actual compiled high-byte read. `tools/run_native_regressions.sh <exact-JP-ROM.nes>` independently verifies ROM SHA-256 and enables four ROM-required suites plus two ROM-specific additional checks, without distributing the ROM in Git. **VPP validation/tooling 3→4 of 8; weighted VPP 24→25 of 100.** No new strict PRG bytes (49,404/262,144 = 18.8461%); no frame trace or playable-native-runtime claim. The research checkpoint 0508 remains provisional and last semantic checkpoint 0507 is unchanged.


## 2026-10-09 — Reusable NES/FDS cross-game evidence layer (candidate-only)

[SharedNES research library](../SharedNES/README.md) and its [curated historical/emulation source catalog](../SharedNES/SOURCE_CATALOG.md) now provide a standard-library cross-ROM cartridge inventory (iNES1/NES2 and cautious FDS disk-side identification), Mapper 24/26 physical bank mapping warnings, SHA-256 bank fingerprints, exact window candidate searches and bounded instruction-aligned JSR/JMP-operand relocation *hypotheses*. All outputs are derived hashes/offsets only, never ROM contents. Initial JP↔US test: **1,018** 32-byte windows examined, **364** exact candidate matches, **348** unique-target candidates (at stride 256; **not** strict semantic bytes); **26** automated test cases exercise parser, metadata, opcode and safety contracts. The two versions use **mapper 24 vs mapper 5**; no cross-game execution equivalence or hardware compatibility is asserted. See [example anchor](../SharedNES/EXAMPLE_JP_US_ANCHOR.json) for an exact but unclassified 32-byte match. This library consolidates NESdev hardware/test literature, legacy tools, FDS BIOS research, Mesen/FCEUX/cc65 and provided PDF manuals without importing copyrighted code. **No VPP or strict PRG increase: 25/100; 49,404/262,144; last completed checkpoint 0507.**


### Reusable VRC6a/VRC6b mapper adapter

`tools/nes_mapper_family.py` and nine ROM-free tests provide explicit-state physical PRG offsets for three VRC6 PRG windows, plus the VRC6b A0/A1 register swap normalized to VRC6a coordinates. They refuse an assumed bank state without producer/provenance evidence and do not imply shared sound drivers or gameplay architecture. This is analysis infrastructure only: no new strict PRG bytes, no VPP increase beyond 25/100.


## 2026-10-09 — Reuse overlay on strict 0501 source bytes (candidate-only)

The reusable [certified-source cross-edition census](../SharedNES/JP_0501_CROSS_EDITION_REUSE.md) verifies 31 physically nonoverlapping SHA-256-locked ranges from already credited checkpoint 0501 (4,364 code/operand bytes). In the US Castlevania III physical PRG, unique 16-byte exact windows cover **1,273** distinct JP source bytes; **5** have only ambiguous matches and **3,086** lack a matching 16-byte window entirely inside their original certified region. These are source-original code/data **transfer candidates only**; they are not newly certified bytes, nor proof of US MMC5 mapping/callers or executable parity. Tests and the hash-only 31-region report are committed. **New strict PRG bytes 0, cumulative 49,404/262,144 = 18.8461%, VPP 25/100, last semantic checkpoint 0507, fixed PRG31 frontier FB96 unchanged.**

## 2026-10-09 — 0508 model-CDL/source-manifest and multi-bank US cross-edition census (provisional)

The [shared NES CDL importer](../tools/nes_cdl_bridge_0508.py) implements separately parsed FCEUX/legacy-Mesen and Mesen2 CDLv2 layouts, explicit image/provenance caveats, physical 8-KiB code/data counts and overlap against SHA-pinned source regions. The [synthetic original-ROM path and cross-edition audit](../SharedNES/0508_CDL_CROSS_EDITION_EVIDENCE.md) executes **1,061,384 JP ROM-fetched instructions / 420 manually injected NMIs** (300 start30, 120 none); **4,979 unique code/operand PRG bytes** in the modeled traces. **Zero of 4,364** separately certified checkpoint-0501 source bytes are fetched in these two tested startup scenarios. Of **4,515 bytes** in 86 length-≥16 modeled code runs, **909** lie in unique exact US 16-byte windows, **146** have only ambiguous US matches and **3,460** lack 16-byte target matches. A **92-byte / 50-opcode** fixed-bank segment at JP E7B8–E813 matches US physical PRG31 candidate E82A–E885. This does **not** prove actual video/IRQ gameplay liveness, US mapped execution, or code/data coverage outside the checked 0501 subledger. Scores remain **VPP 25/100; strict PRG 49,404/262,144 (18.8461%); last completed checkpoint 0507; fixed frontier FB96**.


## 2026-10-09 — Independent 2A03 CPU golden reference conformance (+1 validation VPP)

The SHA-pinned [Nintendulator nestest reference audit](../SharedNES/NESTEST_REFERENCE_0508.md) passes **8,991/8,991** original preinstruction PC/A/X/Y/P/SP/cycle log rows in [CI run 38010689051](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/38010689051). The original game 151-official-opcode core is unchanged; stable NMOS undocumented instructions are available only through a separate NROM test adapter. One of the two existing validation CPU/bank/interrupt trace-harness points is now earned: validation **4/8 -> 5/8**, overall weighted **25/100 -> 26/100**. The other point requires original Japanese VRC6 mapper/IRQ reference execution. The CPU/mapper category's distinct whole-game reference trace-parity point remains unearned. **New strict PRG 0**, cumulative **49,404/262,144 = 18.8461%**, last completed semantic checkpoint **0507**, physical fixed frontier **FB96** unchanged.


## 2026-10-09 — Original Japanese-ROM independent playable Stage 1 reference (provisional, zero strict credit)

The first independently sourced original-ROM frame trace is now available from [Mesen2 2.1.1 via externally SHA-verified v0.1.0 headless CLI](../SharedNES/0508_MESEN_ORIGINAL_GAMEPLAY_REFERENCE.md). The private JP ROM executes **1,100 sequential emulator frames**, from intro/name screen through prayer into visibly playable Stage 1; the earlier state `0A/03` was the name-entry interface, resolved by normal **START** in the original game. The physical-bank CDLv2 evidence class is **independent Mesen execution**, not manually injected-NMI simulation. Across these runs **12,885 distinct PRG code/operand bytes, 7,890 data bytes** were marked; **463 of the 4,364 already certified checkpoint-0501 bytes** are executed within the real Stage 1 continuation, not new credit. Authentic `$18` sampled states include `00,02,0A,09,03,04`, with `$18=04/$2C=03` during gameplay; `$0C/$0D` remains OPEN. Neither the full 0507 strict-ledger overlap nor complete mapped instruction/producer closure has been computed, so **new strict PRG bytes=0; total strict 49,404/262,144 (18.8461%), VPP 26/100, last semantic checkpoint 0507, fixed frontier FB96 unchanged**. SHA-pinned, hash-only [report](../analysis/0508_MESEN_ORIGINAL_GAMEPLAY_REFERENCE_REPORT.json) plus [reproducible audit](../tools/audit_mesen_reference_0508.py) and 12 ROM-free importer tests committed; private Mesen CDL/savestates/ROM/screenshots are never committed.


## 0508 completed narrow fixed-bank certification — 100 NEW verified PRG bytes

New original-Mesen gameplay and original-source full-instruction proof: [0508 fixed live code certificate](../analysis/0508_MESEN_FIXED_LIVE_PROOF.md) and [hash-only machine evidence](../analysis/0508_MESEN_FIXED_LIVE_PROOF.json). Four **nonoverlapping** fixed PRG31 code/operand intervals: `$FBA5-$FBAF` (11), `$FBB0-$FBBA` (11), `$FF06-$FF11` (12), `$FF14-$FF55` (66). Independent real game breakpoints at frames 314, 605, 2030, 39 instruction starts decoded under fixed physical mapping, genuine mapper bank-$00 restoration and actual 160-instruction object-cleaner trace. All 100 bytes were explicitly unclaimed in 0507's fixed gap ledger; other gaps and `$FF12-$FF13` **remain uncredited**. **Strict floor 49,404 → 49,504 / 262,144 = 18.8843%; VPP remains 26/100; fixed CPU frontier FB96 remains.** Completed checkpoint 0508 is limited to these four proven source fragments and does not close earlier provisional 0508 room-$0D or external/native parity uncertainties.

The expanded independent [Stage 1 multi-branch suite](../SharedNES/0508_STAGE1_MULTIBRANCH_REFERENCE.md) executed **9,500 emulator frames in 10 jobs, seven divergent gameplay forks** from a common prior 1,100-frame route, reaching **BLK 1-02**. Physical code/data union **16,772 / 11,765** bytes (+3,887 / +3,875 newly *observed* relative to earlier reference), including **1,157** previously certified checkpoint-0501 code bytes. Cross-edition unique exact 16-byte candidate coverage: **3,165 JP code positions**; this is discovery evidence only, not additional semantic verification. All ROM/CDL/savestates/screenshots/instruction traces are private.


## Checkpoint 0509 — integrated native C++ CPU/mapper/IRQ headless execution (not playable)

[Native C++20 CPU/mapper/IRQ package](../native0509/README.md): 151 official 6502 opcodes, 2A03 binary ADC/SBC and instruction cycle costs, existing mapper 24 and VRC6 IRQ classes, controller serial I/O, RAM, partial PPU memory/registers, OAM DMA, modeled NMI scheduling and a bounded executable accepting the private original JP ROM. **262,144** exhaustive ADC/SBC arithmetic/flag cases passed locally, with synthetic mapped CPU/PPU/NMI tests. The first **7,828** original-ROM CPU PC addresses match an independently captured Mesen2 v2.1.1 PC stream; first divergence at **step 7,829** at PPU vblank polling. This is not standalone rewritten-game logic, CPU register or full hardware timing parity, a rendered game, or playable PC output. [Details and proof limits](0509_NATIVE_CPU_HEADLESS.md).

**VPP stays 26/100; strict JP PRG 49,504/262,144 = 18.8843%; semantic checkpoint 0508; research 0509; fixed frontier FB96. No new credit for ROM-dependent native execution.**


**0509 native reference follow-up:** The independent original-Mesen reset snapshot reports PPU scanline 0, cycle 31. An explicit test-fixture PPU phase selector in the native headless probe, with default startup unchanged, reproduces **24,773** consecutive original-ROM PC addresses; first mismatch at ordinal **24,774** is the NMI entry timing. Without the fixture seed the 7,828-step default result remains. Neither result proves register/cycle timing, PPU output, native playable port or new PRG bytes. [Golden evidence](0509_NATIVE_CPU_HEADLESS.md); [golden verifier](../tools/test_native_mesen_pc_0509.py). Strict **49,504**; VPP **26** unchanged.


## 0509 independent native object/OAM technical preview (ROM-free)

[Standalone native actor/sprite pipeline](../standalone0509/README.md) now compiles and runs with no original ROM. It integrates the prior verified bank-0D C++ OAM assembler, bank-0B 8-bit collision helper, and new source-locked PRG31 FF06/FF15/FF24 actor scanner/18-field cleaner. The native program generates **synthetic** sprite descriptors/2bpp CHR, produces a deterministic 256x240 PPM, and accepts scripted demonstration inputs. Original-game helper bytes are SHA-audited; 4096 occupancy bitmaps and 512 RAM field-clear mutation cases plus exact image goldens pass Release and local ASan/UBSan CTest. **This is not the original game or a playable port**: assets, player control, physics, stage and background are synthetic, and PPU/audio parity remain open. [Technical scope](0509_ROM_FREE_ACTOR_PIPELINE.md); [ROM source audit](../tools/audit_actor_slot_0509.py). **No new semantic PRG bytes; strict 49,504/262,144 (18.8843%), VPP 26/100 unchanged.**

## 0509 provisional cross-bank source actor allocation

[Actor spawn source audit](../analysis/0509_ACTOR_SPAWN_PRODUCER_FINDINGS.md) runs original raw $0A:$90CA into fixed $FF06 over all 4,096 occupancy masks: 4,095 available-slot routes and one full-slot exit; 73,717 source instructions. Exact scratch/actor/script RAM writes and 6502 flags/stack are checked. Conditional source code alone does not demonstrate game-frame entry or live mapper bank context. Strict verified PRG stays 49,504/262,144 (18.8843%), VPP stays 26/100, completed checkpoint 0508 and frontier FB96 unchanged.

## 0509 provisional raw-$0A actor precheck producer

[Source-stepped first-level actor gate](../analysis/0509_ACTOR_PRECHECK_PRODUCER_FINDINGS.md) extends $90CA back through $90C5: JSR $8CDD conditionally reads $53 and $07E0,X before tail-JMP $FF06. Only when both are zero and a slot is vacant does $90CA clear $10 and set $054E,X=$13 / $05EF,X=0; blocked/all-full routes branch to $9128. Original-ROM runner passes 12,288 synthetic-state scenarios and 188,332 fetched instructions; the four pointer words at $90BD are structural, not live-dispatch proof. No original Mesen gameplay reachability or mapper-time proof; **0 new strict PRG bytes**, PRG total **49,504/262,144**, VPP **26/100**, checkpoint 0508 and frontier FB96 unchanged.

## 0509 provisional actor guard producer arithmetic

[Raw-bank actor guard producer audit](../analysis/0509_ACTOR_GUARD_PRODUCERS_FINDINGS.md) now executes all four direct raw-$0A `$07E0,X` store encodings under bounded original-ROM CPU states (two 65,536-case signed-direction arithmetic paths, 512 carry-bit cases, 256 initializer cases). Source-accurate fixed PRG31 `$FB7A/$FB88` `$53/$54` increment/decrement passes 65,536 inputs in each direction. **262,912 local states / 3,280,384 authentic instructions**; the `$53/$54` paired arithmetic and `$07E0,X` bit masking are conditional source facts, not original Stage 1 entry/mapper liveness. Strict verified 49,504/262,144 (18.8843%), VPP26, checkpoint0508, frontierFB96 unchanged.

## 0509 integrated six-object event dispatch and original actor lifecycle (provisional)

[Source-stepped scheduler/dispatcher/actor chain](../analysis/0509_ACTOR_DISPATCH_CHAIN_FINDINGS.md) follows raw VRC6 bank $0A:$84EA scheduler through $8501 two-level indexed original-ROM pointers and $8CDD/fixed $FF06 guard into source $90C5/$90DF/$9133 (1/2/3 actor creations). **98,304 test states / 6,174,946 original instructions / 111 distinct PC addresses** pass with original ordered RAM writes, partial allocations, event progression only after complete success, source X/stack returns and $07C8 high-nibble masking. Source entry $9133 corrects an earlier provisional $9131 misidentification. This is bounded input-state evidence, not an original stage-liveness/PPU/frame certificate. [Optional independent Mesen2 trace recipe](0509_MESEN_ACTOR_DISPATCH_CAPTURE.md). **Zero new verified bytes**; strict PRG remains 49,504 / 262,144 (18.8843%), VPP 26/100, checkpoint 0508, fixed frontier FB96.

## 0509 verified independent Mesen2 Stage 1-02 actor-event source entry

[Live original-JP emulator evidence](../analysis/0509_MESEN_ACTOR_LIVE_FINDINGS.md) **closes the local game-frame reachability gap for raw bank $0A:$84EA→$84F3→$8501 and event row $32→$8B2C** on one naturally controlled Stage 1-02 route. Mesen2 2.1.1 hits frame 3092 with raw bank $0A and original X=3, $07C2,X=$32, $07C8,X=0, $53=$07E0,X=0; 600 actual CPU instructions contain two $84F3/$8501/$8520/$8B2C/$FF06/$FF24/$84F8 cycles, creating two type-$3D actors. Clean independent boot reproduces identical registers/cycles and trace SHA. The earlier synthetic $90C5/$90DF/$9133 actor handlers are **not** shown live by this event. Original Mesen savestates/CDL/traces and ROM remain private. Physical manifest overlap pending: strict PRG49,504, VPP26, certified 0508, frontier FB96 unchanged.

## 0509 physically mapped Mesen actor-producer feedback matrix (provisional)

[Seven-policy original emulator feedback report](../analysis/0509_MESEN_ACTOR_FEEDBACK_FINDINGS.md) executes seven independent 640-frame controller forks from the previously clean-boot-verified frame 2603, 4,480 total branch frames. Three jump-inclusive policies naturally activate raw-bank $0A source row $32 (frames 3088/3092/3094) and produce two live type-$3D actors each; four bounded policies do not. Source callbacks use Mesen physical PRG address conversion, not ZP mapper tracker alone. Authentic source $8143/$8157/$8182 row/guard/event writers, $8D90 actor setter, $8B71/$85DD event progression and original $A43F/$A444 five-byte descriptors are independently observed. [ROM-locked split-and-merge replay](../tools/audit_mesen_actor_feedback_0509.py) and [compact machine results](../analysis/0509_MESEN_ACTOR_FEEDBACK_REPORT.json). No strict promotion; 49,504/262,144, VPP26, last certified 0508, fixed FB96 unchanged.

## 0510 provisional native PC title-to-first-stage playable prototype

[Native host C++20 demonstrator](../native_demo0510/README.md) now implements a real PC title→short intro→single-room Stage 1 UI, keyboard movement/jump/attack, and local sample enemy/stage exit. The game logic is **not an emulator** but except for fixed $FF06/$FF24 actor slot/reset is currently **preview-authored**; visuals are local Mesen-derived Japanese scene reference stills that are **not committed in Git**. GCC14.2 X11 Release/ASan/UBSan, deterministic self-tests and clean ZIP unpack/rebuild pass locally. [Proof limitations](0510_NATIVE_PC_TITLE_STAGE_PROTOTYPE.md). This delivers a playable native starting point, not a Castlevania III source-equivalent port. Strict PRG49,504/262,144, VPP26/100, checkpoint0508, frontier FB96 unchanged.

0510 native PC demo packaging refinement: independently compiled and ROM-free CTest-verified Linux **and Windows** executables (GitHub Actions [run 38076049062](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/38076049062)). User-specific downloadable asset pack contains the private JP reference images, without committing game art. Windows GUI usability remains untested; native original gameplay parity remains unearned. Strict PRG/VPP unchanged.

## 0510 original game actor row-$32 native semantic lift (source/Mesen exact RAM)

[Source-faithful native C++ row-$32 handler](../analysis/0510_ROW32_NATIVE_LIFT_FINDINGS.md) replaces prototype rules with the actual raw-$0A:$8501→$8B2C source transition and its $8D5E/$8DC1/$8D76/fixed-$FF06/$FF24, raw-$0B:$A00F and $8B50 event packing. Two independently natural original Mesen Stage 1 frame-3092 actor dispatches (source objects 3,4; type-$3D actors in destination slots 1,2) are replayed against the C++ lift with **3,584/3,584 non-stack physical system-RAM bytes exact**; 4,111 separate ROM-free original-bounded tests pass and ASan/UBSan pass. Full 6502 stack/cycles, frame visual/audio, actor script follow-up and other event rows are not proved. No new strict PRG bytes or VPP; 49,504/262,144 (18.8843%), VPP26, completed 0508, fixed frontier FB96 unchanged.

## 0511 faithful actor movement lift: original raw $0B 8001 and 8037

[Source-exact native 2-axis actor arithmetic](../analysis/0511_ACTOR_MOTION_NATIVE_FINDINGS.md) now implements the actual original-JP raw bank $0B:$8001-$8036 and nested $8037-$804A source, not preview mechanics. Exhaustive/mixed **69,646 native arithmetic tests** and ASan/UBSan pass. An independent Mesen 2.1.1 naturally controller-produced type-$3D two-actor savestate permits exact native replay of two genuine $8001 calls: **3,584/3,584 nonstack RAM bytes, original A/Y/P, and 60 original instructions** at actual physical bank $0B (0x02Cxxx). The original Mesen source state is private/hash-locked; separate one-command full cold bootstrap intermittently stalls and is NOT claimed to pass. [Reproducer](../tools/audit_mesen_actor_motion_0511.py), [compact report](../analysis/0511_actor_motion_live_report.json). No full-frame native parity, no new strict PRG, VPP unchanged 26/100, certified 0508, physical frontier FB96.

## 0512 original fixed-$FDF8 bank-$0B horizontal actor displacement

[Faithful native original-JP `$0B:$80E3-$810E` horizontal branch](../analysis/0512_ACTOR_DISPLACEMENT_NATIVE_FINDINGS.md) is now separate C++ with original signed 8-bit `$6B`, 9th X bit `$0470,X`, double 6502 SBC carry/overflow and ZP `$00/$01` stores. **73,742 native mathematical/boundary test cases plus ASan/UBSan** pass. Mesen naturally reaches this exact source through fixed `$FDF2` bank switch / `$FDF8` call for both type-$3D actor slots; native 20-instruction per-call replay matches original **3,584/3,584 non-stack RAM bytes** and A/X/Y/P, physical PRG `$02C0E3`. Original live zero-delta only; negative `$65` vertical branch `$810F`, original $B1F8 continuation, collision/OAM and full frame remain OPEN. [ROM-locked replay](../tools/audit_mesen_displacement_0512.py); [compact Mesen results](../analysis/0512_live_displacement_report.json). Source strict PRG unchanged at 49,504/262,144, VPP26, last certified 0508, fixed FB96.

## 0513 source-faithful vertical actor displacement and 8843 type3B continuation

[Original raw $0B:$810F/$8140 → `$8843` native reconstruction](../analysis/0513_VERTICAL_DISPLACEMENT_NATIVE_FINDINGS.md) covers source `$65` negative-axis branch, signed Y and ninth-bit carry, actor removal gate `<$68` / negative types, and the real `$8843` type-$3B 16-bit extra-coordinate writer. **270,351** ROM-free native oracle inputs and ASan/UBSan pass. Independent original-Mesen **54 synthetic injected RAM/PC configurations**, each executed with unchanged original ROM code, match **96,768/96,768 non-stack RAM bytes** and return A/Y/P to fixed `$FDFB`. Do NOT call these natural gameplay paths: 300 natural original-Mesen Stage 1 frames observed no `$810F` entry. Genuine `$65` producer, fixed `$B1F8` downstream and complete native frame remain open. No new certified PRG/VPP; 49,504/262,144 (18.8843%), VPP26, last certified 0508, fixed frontier FB96.

## 0514 native original $6B producer and bank-$0B actor postprocess gate

[Verified Stage 1 actor preflight reconstruction](../analysis/0514_ACTOR_PREFLIGHT_NATIVE_FINDINGS.md) lifts original PRG30 `$D2FE–$D30C` ($62>=2 case, `$6B=$53-$08`) and raw bank-$0B `$B1F8–$B215` eligibility gate to original `$B1F7/$B217/$B258` outputs with A/X/Y/P. Original Mesen natural Stage 1 hit both; observer recorded 59 original `$6B=0` stores and 360 bank-qualified B1F8 calls in 60 frames (X1/2/14–17). The original direct `$65` writer at PRG30 `$D066` reads indexed room data and was **not** reached in those bounded samples; its input/liveness domain remains OPEN. 100,357 ROM-free native cases and sanitizers pass; 38 original-ROM emulator differential inputs (36 **injected synthetic**) match 68,096 non-stack RAM bytes plus flags and gate PCs. [Reproducer](../tools/audit_actor_preflight_0514.py) and [machine report](../analysis/0514_actor_preflight_report.json). No collision B217 continuation/full actor frame or strict PRG/VPP promotion; certified 0508 floor 49,504 bytes, VPP26, frontier FB96.

## 0515 original Stage 1 collision admission: composed native B1F8 → B217 → B232

[Authenticated JP source-faithful native collision precheck](../analysis/0515_COLLISION_ADMISSION_NATIVE_FINDINGS.md) extends the source-verified `$B1F8` gate through original raw-bank `$0B:$B217–$B231`: `$7E&$F0` bypass, `$054E,X` type ≥$69 route `$B162`, `$0470,X&2` route `$B1D8`, `$7D` bypass, or transfer `$B232` before `JSR $B339`. 82,947 ROM-free native cases + ASan/UBSan pass. Natural original-Mesen Stage1 actor X=1 passes composed 23 instructions and shorter 11-instruction tail with full 1,792 nonstack RAM, A/X/Y/P and PC exact each; 56 additional **RAM-injected synthetic** original-ROM branch cases also pass, 103,936 RAM bytes total. [ROM-locked audit](../tools/audit_b217_original_mesen_0515.py), [compact report](../analysis/0515_collision_precheck_mesen_report.json). Original next unlifted collision source `$B339→$80B3`. This is NOT full collision or frame native parity; strict PRG49,504/262,144, VPP26, completed certified 0508, fixed frontierFB96 unchanged.

## 0516 original native collision distance, composed B1F8 → B393

[Source-faithful native Japanese PRG `$0B:$B339-$B393` and `$80B3/$80C1` collision measurements](../analysis/0516_COLLISION_MEASURE_NATIVE_FINDINGS.md), including original room/player and actor type-indexed radius tables and correct 5-pixel `$B395` vertical offset, are integrated with the 0514/0515 gates into a single native B1F8→B393 path. **139,343 ROM-free C++ oracle cases** and ASan/UBSan pass. Independent original Mesen produces **50 windows**, two overlapping naturally reached paths on one Stage 1 actor (53 full prefix instructions; 29 measurement instructions) and 48 explicitly RAM-injected synthetic cases; **89,600/89,600 non-stack RAM bytes**, A/Y/P and next PC exact. Live original horizontal early exit; vertical path only synthetic Mesen differential. [ROM-locked automated replay](../tools/audit_collision_measure_0516.py), [compact machine report](../analysis/0516_collision_measure_mesen_report.json). Original `$B7/$E5BE`, `$B396`, `$B235` actual collision response and full frame remain OPEN. Strict PRG49,504/262,144 (18.8843%), VPP26, certified 0508, fixed frontier FB96 unchanged.

## 0517 native JP collision response / follower scan through fixed FDFE

[Faithful original $0B:$B235-$B27B, $B29D-$B2A7 and $B317-$B31F native lift](../analysis/0517_ACTOR_COLLISION_TAIL_NATIVE_FINDINGS.md) now composes previous B1F8/B217/B339 collision measurement with original collision-result/carry branching, $7E/$8D/$8E response state, type filters and empty follower scan X20..22. **91 authentic original-Mesen instructions** on one naturally reached Stage1 type-$3D actor from B1F8 to fixed FDFE match **1,792/1,792 non-stack physical RAM bytes, CPU A/Y/P**, plus shorter overlapping natural tail. 14 expressly RAM-injected synthetic branch windows test B243/B27C/B2A8 stops: 16 total source comparisons, **28,672/28,672** bytes exact. **65,539 ROM-free native test cases + ASan/UBSan pass**. [Original ROM replay](../tools/audit_actor_collision_tail_0517.py), [compact report](../analysis/0517_actor_collision_tail_report.json). This is NOT whole actor frame: fixed FE00 continuation, nonempty follower and contact paths, PPU/OAM remain OPEN. Strict certified 0508 PRG49,504/262,144, VPP26, FB96 unchanged.

## 0518 physical PRG overlap and VPP reassessment

[Deterministic source audit](../tools/audit_native_coverage_0518.py) inventories 25 SHA-locked windows (1,365 distinct original physical PRG bytes): 546 overlap 0501 certified regions, 78 overlap 0508 independently certified fixed bytes, and 741 are outside **only those two named references**. The 741 cannot be certified until the full historical 0502–0507 ledger is reconstructed. Original fixed FF12–FF13 remain excluded from 0508. No new strict PRG credit: **49,504/262,144 (18.8843%)**, semantic checkpoint 0508 and frontier FB96 unchanged.

[Formal VPP rubric review](../analysis/0518_RECONCILIATION_AND_VPP_DECISION.md) grants **one additional gameplay movement/collision architectural point** (1→2/4) for the reusable connected original-JP native collision route B1F8→FDFE, independently verified on one natural Stage 1 actor (91 original CPU instructions, 1,792 exact non-stack RAM bytes, original A/X/Y/P). Gameplay becomes **3/25**, total **VPP 27/100**. This does not prove positive contact during natural gameplay, full frame parity or extra native-runtime completion.

## 0519 original fixed FDFE scheduler decision, natural source-state native replay

[Source-faithful fixed-bank actor gate](../analysis/0519_FIXED_SCHEDULER_NATIVE_FINDINGS.md) reconstructs `$FDFE→$FE00` original CPU type/attribute branching and stops before the next unlifted JSR. Natural Stage1 Mesen frame2603 actor X15/type `$80` executes **ten original instructions** to `$FE31` before `JSR $BD11`; structured native C++ matches **2,048/2,048 original RAM bytes including the stack**, exact PC/A/X/Y/P, with no stores. **73,731 ROM-free native test cases**, sanitizer builds and project CI pass. [Machine report](../analysis/0519_fixed_scheduler_mesen_report.json). Other first-call stop branches are native-synthetic only, not natural gameplay. Original `$BD11` and later scheduler steps remain OPEN. No new strict PRG credit, VPP stays 27/100, certified checkpoint 0508, physical frontier FB96 unchanged.

## 0520 natural original JP BD11→FE34→FE60 scheduler continuation

[Original source-qualified scheduler followup](../analysis/0520_SCHEDULER_BD11_FE34_NATIVE_FINDINGS.md): raw-bank `$0B:$BD11` original early-return gate reads `$A8/$05EF,X`; fixed PRG31 `$FE34–$FE5F` actor type/attribute checks resume at `$FE60 JSR $EF93` (unlifted). Native structured C++ composes 0519 `$FDFE` through `$FE60` for one natural Stage1 actor X15/type80 across **28 original CPU instructions**, 1,792 non-stack Mesen RAM bytes and exact A/X/Y/P/PC. Natural shorter `$BD11→$FE60` spans 17 instructions and **all 2,048 RAM bytes including stack** exact. 12 additional **RAM-injected synthetic** source paths authenticate BD15/BD1F/FE4E/FE63/FE6E alternatives: 14 Mesen comparisons, **28,416/28,416** RAM bytes exact. **77,827 ROM-free native cases**, ASan/UBSan pass. [Reproducer](../tools/audit_scheduler_followup_0520.py) and [machine report](../analysis/0520_original_mesen_followup_report.json). Strict PRG49,504, VPP27, certified semantic 0508/frontier FB96 unchanged. Next: original `$EF93` call and indexed animation/timer state.

## 0521 original Japanese animation timer and source table F359

[Fixed EF93 original source lift](../analysis/0521_ORIGINAL_ANIMATION_NATIVE_FINDINGS.md): authenticated ROM pointer EFD2+$0E -> F359, native exact source timer DEC and 16 animation triples. Natural actor15/type80 FDFE→FE63 **57 original CPU instructions**, native 1,792 nonstack RAM bytes exact; overlapping natural EF93 window 28 steps/full 2048-byte RAM exact. **38 Mesen windows**, 36 explicitly injected synthetic, **77,568/77,568** RAM comparisons and A/X/Y/P/PC exact; **65,547** native cases and sanitizers pass. [Audit](../tools/audit_animation_ef93_0521.py), [report](../analysis/0521_original_mesen_animation_report.json), [evidence ledger](../analysis/NATIVE_EVIDENCE_LEDGER.json). Unsupported descriptors and FE63 callbacks remain open. Strict PRG 49,504, VPP 27, completed semantic 0508/frontier FB96 unchanged.

## 0525 — recover missing physical PRG evidence before further native expansion

[Source-mask and recomp recovery](../analysis/0525_PRG_RECOMP_RECOVERY.md) restores a checked 0500-0508 union of **6,029 disjoint original physical PRG bytes in 59 intervals**. The earlier 43,475-byte component of the 49,504-byte floor remains without a complete physical location mask. The 0510-0517 1,365-byte source-window inventory was corrected to identify 739 bytes outside the recoverable 0500-0508 union (2 fewer than the 0518 comparison against 0501/0508 alone). Optional authentic ROM checks and 59 literal byte-exact recomp fragments are reproducible. This is **accounting and recomp scaffolding, not a newly certified semantic byte increase**. Strict 49,504, VPP27, checkpoint0508, frontier FB96 unchanged.

## 0525 — First bank-qualified JP 6502 symbolic recompilation

[Original 6502 source](../recomp/actor_tail_0525.asm) and [fixed bank source](../recomp/fixed_tail_0525.asm) now compile with a bounded two-pass label/branch-aware opcode assembler ([exact native-ROM check](../tools/test_recomp_6502_0525.py)). The resulting **88/88 real instruction+operand bytes** in five noncontiguous original physical PRG spans have exact source fingerprints and were locally compared with the actual uploaded Japanese ROM. This differs from the 59 literal-byte-only provenance scaffolds: these are **mnemonics, operands, symbolic subroutine labels, branch relocation, and original bank-qualified locations**. They cover mapped raw0B reset $8193/$81B2/$B56B and fixed E2D0/FE63 scheduler continuation. All were already historical strict source bytes; **no duplicate strict PRG credit**, no Mesen claim and no VPP promotion.

## 0526 — Historical source PRG union and further genuine recompilation

[0526 verified source finding](../analysis/0526_PRG_RECOMP_FINDINGS.md): original Git 04FE 957 bytes/11 spans and corrected 04FF 931 bytes/6 spans recovered, independently SHA-256 ROM-verified. The 04FE–0508 physical union now comprises **76 disjoint source regions and 7,917 already certified bytes**, reducing unmapped older baseline to 41,587. The 0510–0517 739 ambiguous source bytes remain nonpromotable without older source evidence. Newly authored *actual 6502 mnemonic* [fixed scheduler](../recomp/fixed_scheduler_0526.asm) and [raw0B callback](../recomp/raw0b_callbacks_0526.asm) modules reassemble **315 more exact opcode/operand/table bytes**, raising the assembled source baseline from 88 to **403**, checked in CI by [two-pass assembler](../tools/test_recomp_6502_0526.py). No strict PRG or VPP point double credited: PRG49,504, VPP27, semantic0508 and fixed frontier FB96 unchanged.

## 0527 — Recover 14,168 more historically verified PRG source locations

[Historical bank05 PRG source audit](../analysis/0527_BANK05_SOURCE_RECOVERY.md) restored prior 04FB/04FC/04FD exact bank05 script-command/operand regions, **14,168 SHA-locked, original JP ROM-verified bytes in three contiguous spans**. Combined [0525](../analysis/0525_PRG_RECOMP_RECOVERY.md)/[0526](../analysis/0526_PRG_RECOMP_FINDINGS.md), the machine-checked historical physical union now covers **22,085 previously certified PRG bytes / 79 disjoint source intervals**. Only **27,419** earlier reported strict bytes lack a fully recovered physical mask. This is not 14,168 recompiled 6502 instruction bytes and not fresh strict coverage. Actual symbolic 6502 source remains **403 byte-exact bytes**; strict PRG 49,504, VPP27, semantic0508 and fixed FB96 unchanged.

## 0529 — Whole-cartridge original-JP bank source and bulk symbolic 6502 conversion

[Whole bank recompilation](../analysis/0529_WHOLE_CART_BANK_RECOMP.md) rebuilds **all 393,232 original iNES bytes** from **25 generated `.asm` modules**, with the 16-byte header retained from the validated ROM. The source generator uses the 0501 verified mapped 6502 graph to replace `.byte` placeholders with **4,030 additional mnemonic bytes (1,864 additional original instructions)**, bringing reassemblable symbolic source to **4,433 original PRG bytes** in bank-qualified fixed/raw09/raw0A/raw0B fragments. Remaining PRG 257,711 bytes and CHR 131,072 bytes are explicit opaque data fallback, not falsely reported as decompiled program logic. Generator is in [tools/build_whole_cart_recomp_0529.py](../tools/build_whole_cart_recomp_0529.py); full ROM-bank outputs are local only. ROM-free CI smoke checks the two-pass assembler; original retail-ROM full roundtrip verified locally. All newly expressed code was certified in 0501; strict PRG 49,504, VPP27, semantic0508, fixed FB96 unchanged.

## 0530 — Restore early fixed-bank dispatcher CFG at bulk scale

[Original fixed dispatch graph and whole-cart source](../analysis/0530_FIXED_DISPATCH_BULK_RECOMP.md) converts **1,218 more authentic 6502 instruction starts / 2,719 opcode bytes**, plus **154 SHA-verified bytes** of original first/nested/secondary dispatcher pointer tables from historical 04FE/04FF/0500, into recompilable source. Totals are now **7,306 source-classified bytes** = 7,146 instruction bytes + 160 typed inline-data bytes. Every original historical 04FE/04FF/0500 code/data interval is accounted for without decoding gaps or overlapping older work. Remaining **254,838 PRG bytes** are explicitly unclassified, not counted as symbolic. The full 393,232-byte Japanese ROM still reassembles exactly locally. GitHub CI validates ROM-free source/assembler syntax; optional private-original-ROM full bank proof is required for real source comparison. No novel strict credit, PRG 49,504, VPP27, semantic0508, fixed frontier FB96 unchanged.

## 0531 — Bank05 stage-script source reconstruction (14,168 bytes)

[Source/provenance report](../analysis/0531_BANK05_SCRIPT_SOURCE.md): original stage/mode metadata in raw0C $8F60 identifies 84 source-backed references to 72 unique bank05 script roots. The entire 04FB/04FC/04FD 14,168-byte parser-validated command/operand region is emitted in the complete 25-bank source with rooted labels and provenance (game data, not CPU instructions). Combined classified PRG source is now 21,474 bytes = 7,146 NMOS 6502 bytes + 160 typed dispatch pointer bytes + 14,168 producer-bound game script/data bytes; unclassified PRG remainder 240,670. Original Japanese ROM 393,232-byte roundtrip PASS locally. No strict PRG/VPP promotion; strict 49,504, VPP27, semantic0508 and frontier FB96 unchanged.

## 0532 — Bank04 14,032-byte producer-rooted script source and common 6502 sound parser

[0532 evidence and reproduction](../analysis/0532_BANK04_PARSER_SOURCE_FINDINGS.md): from original 04F7/04F8/04F9/04FA SHA-locked CPU $87AE–$BE7D stream windows, recover and label 102 original raw0C metadata references / 96 distinct bank04 stage-script roots, a **14,032-byte** producer-backed data source region. Recover the byte-identical CPU $8001–$87AD common sound parser in physical raw banks $04, $05 and $0C: **786 official 6502 instruction starts / 1,716 mnemonic bytes plus 249 local pointer/lookup bytes per bank**, totaling another **5,895 classified bytes**. This checkpoint adds **19,927** to source-classified PRG, not new strict certified PRG. Total typed 6502 12,294 bytes + local/inline lookup data 907 + scripted data 28,200 = **41,401/262,144 original PRG bytes classified** (220,743 still unclassified). All 25 bank source files and entire original JP retail iNES 393,232-byte roundtrip PASS; corrupt parser/script/metadata/ROM fixtures rejected. No original Mesen execution proof, no VPP adjustment; strict PRG 49,504, VPP 27/100, semantic checkpoint0508, fixed frontier FB96 unchanged.

## 0533 — Original JP bank0C sound metadata and interpreter (6,627 new classified bytes)

[ROM and source findings](../analysis/0533_BANK0C_SOUND_FINDINGS.md): source-audited 04F5 bank0C graph adds 702 genuine original NMOS instructions / **1,599 opcode bytes**; 125 sound record descriptors/index entries cover **1,505 bytes** and contain 325 sound producer references across raw banks04/05/0C; 139 references to 125 distinct bank0C source roots bound a **3,523-byte indexed sound pool**. 6,627 additional classified PRG bytes, exact 25-bank 393,232-byte iNES roundtrip and four tamper negatives locally. Classified PRG now **48,028 bytes** (13,893 code, 2,412 typed tables/data, 28,200 bank04/05 scripts, 3,523 bank0C rooted sound pool), remainder 214,116 unclassified. Indexed sound payload is not yet command-wise decoded. Strict 49,504/VPP27/semantic0508/frontierFB96 unchanged.

## 0534 — 0504 AI original assembly and bank0C secondary phrase tables

[Original JP source and evidence](../analysis/0534_SOUND_PHRASES_AND_AI_SOURCE.md): add 256 authenticated original 0504 6502 instructions (504 opcode+operand bytes, bank0B/fixed31), 72 bounded original AI table bytes; plus the structurally reconstructed bank0C $A304/$A404 sound phrase index (148 entries/140 distinct FF-terminated roots, 296 pointer bytes and 1,323 data bytes). The runtime selector domain is not proved: the 1,619 phrase bytes are explicitly source structural candidates, not new strict-semantic PRG credit. Cumulative classified source 50,223 PRG bytes: 14,397 genuine original 6502, 2,484 typed table/data, 28,200 old bank04/05 script bytes, 3,523 bank0C rooted stream pool, 1,619 secondary sound phrases; 211,921 still opaque. All 25 banks and original JP 393,232-byte iNES exact; nine negative-ROM mutations reject altered original source. Strict 49,504, VPP27, checkpoint0508 and fixed frontier FB96 unchanged.


## 0535 — Original bank0A 0506 state-machine control flow and conditional bank0C helpers

[ROM-backed findings](../analysis/0535_BANK0A_STATE_HELPER_FINDINGS.md) source-lift the original 0506 12-word state table at bank0A $B4D1 and 244 NMOS 6502 instruction starts / 502 code bytes through six exact, fingerprinted physical runs. Original bank0A state table adds 24 .word bytes. Encoded cross-bank callers plus bounded bank0C code graph add another 79 conditional 6502 helper bytes and 18 typed lookup bytes; mapper context/index producers for those 97 bytes remain OPEN. In total 623 more PRG bytes become bank-qualified recompilable source; **classified source 50,846**, original 6502 opcode/operand source **14,978**, typed lookup metadata **2,526**, unclassified PRG **211,298**. Whole original Japanese iNES reassembly remains 393,232/393,232 from 25 source bank files; ten deliberate corruption cases fail as required. Strict semantic 49,504 / 262,144, VPP27, certified0508, fixed FB96 unchanged; no duplicate credit or playable-native parity claim.

## 0536 — Mapper-aware original bank0A room graph and bank0E source streams

[0536 source/evidence](../analysis/0536_MAPPED_ROOM_SOURCE_FINDINGS.md) converts 691 additional original 0508 conditional 6502 instruction starts (1,540 opcode/operand bytes) in raw bank0A, 106 extra E7FB dispatch-pointer bytes, 38 room-descriptor/pointer bytes, and 175 original bank0E conditional mapper-read room-object bytes (5 streams/30 five-byte objects). Source-only 0508 graph comprises 935 starts/2,042 code bytes; **526 already-classified 0535 bytes are subtracted exactly**, leaving **1,859 newly typed bytes**. All 25 bank source modules reassemble the original 393,232-byte JP iNES exactly; ten independent negative corruption tests pass and prior 0532–0535 ROM-backed source gates are updated. Cumulative typed PRG rises from 50,846 to **52,705**, with **16,518 original 6502 instruction/operand bytes**, 2,670 typed tables, 28,200 bank04/05 script bytes, 3,523 indexed bank0C stream bytes, 1,619 sound-phrase structural bytes, 175 mapper-loaded bank0E object bytes; **209,439 unclassified**. 0508 original conditional mapper-bus 1,280-case evidence is preserved, but global room-index $07A0 bounds, gameplay path liveness, VRC6 frame parity and native gameplay recompilation remain unproved. No strict PRG/VPP double credit: 49,504/262,144, VPP27/100, semantic0508 and frontier FB96 unchanged.

## 0537 — Whole physical raw0A 16KiB bank recovery (open, not a tiny-byte checkpoint)

[Complete bank map and method](../analysis/0537_WHOLE_BANK_RAW0A_FINDINGS.md): original JP physical PRG bank0A CPU $8000-$BFFF is now tracked **byte-for-byte across all 16,384 positions**, with 2,162 previously audited 6502 instruction bytes; 168 prior audited table bytes; **2,910 static CFG candidate opcode/operand bytes (not certified)**; **3,023 structurally checked pointer/4- and 5-byte record data bytes**; and **8,121 explicitly unresolved bytes**. The non-overlapping candidate graph has 82 roots, while the typed data has 483 pointers to 460 distinct bounded records. The rebuilt bank and the 393,232-byte original JP whole-cartridge source substitution match exactly. Five ROM-backed pointer/source/identity tamper regressions passed. **This is a full-bank inventory and experimental source recovery, NOT a complete decompilation of this bank**, and it does NOT modify the prior cumulative 52,705 source-classified or 49,504 strictly certified PRG bytes, VPP27, original-Mesen parity or native playable-recomp claims. Raw0A remains the active unfinished bank-sized unit until candidate liveness, structural semantics, and unresolved data are closed.

## 0554 — NTSC PPU timing primitive (first native frame-scheduling foundation)

[Standalone C++20 2C02 clock](../analysis/0554_NTSC_PPU_FRAME_CLOCK.md) adds deterministic 341×262 dot scheduling, 3 PPU clocks/CPU clock, VBlank and NMI-line/read-clear edges, and the odd-frame prerender skipped dot when rendering is enabled. GCC and Clang unit tests pass; CMake/CTest registers a ROM-free test. **Not wired to 0553 CPU/Bus**: instruction cycles, DMA, true $2002/PPUCTRL bus timing, IRQ, frame output and Mesen gameplay parity remain open. No strict PRG/VPP advancement: 49,504/262,144, VPP27/100, last semantic checkpoint 0508/frontier FB96.

## 0554 Phase 2 — Account CPU instruction cycles and advance native PPU dot clock

[CPU timing foundation](../analysis/0554_PHASE2_CPU_CYCLE_ACCOUNTING.md) adds official 6502 opcode/mode base cycles to the shared static-native `Cpu::exec`, taken branch and branch-page-cross penalties, indexed-read page-cross penalties, and 7 CPU-cycle NMI entry. Each counted CPU cycle advances the existing deterministic NTSC PPU dot clock by 3; new CTest covers representative instructions, JSR/RTS/NMI/RTI, indexed-store/RMW distinctions and clock totals. **The 0553 scripted $2002 and injected-NMI bus policy remains untouched**; this does not implement cycle-positioned bus reads, DMA, IRQ or natural PPU/CPU game frames. Strict 49,504/262,144, VPP27/100, last semantic checkpoint 0508/frontier FB96 remain unchanged.

## 0554 Phase 3 — opt-in CPU/PPU register final-access cycle scheduling

[0554 Phase 3 source and tests](../analysis/0554_PHASE3_TIMED_PPU_BUS.md) add PPUCTRL/PPUMASK writes and PPUSTATUS VBlank-bit read/clear in the statically compiled CPU, with 8-byte register mirroring, direct absolute/indexed last-cycle timing and recorded CPU/PPU dot timestamps. Unsupported, indirect and unpositioned PPU register accesses fail closed. ROM-free CTest covers final-access positions before/after VBlank, NMI, indexed penalties, mirrors, legacy isolation and unsupported addresses. **The 0553 ROM reset/NMI trace still deliberately uses scripted $2002/I/O and injected NMI**; DMA, PPU graphics/VRAM, unmodeled bus phases, VRC6 IRQ and natural Mesen gameplay-frame parity are open. VPP 27/100, strict 49,504/262,144, checkpoint 0508/$FB96 unchanged.

## 0554 Phase 4A — bounded instruction-boundary NMI / external IRQ

[Interrupt scheduler](../analysis/0554_PHASE4A_INTERRUPT_BOUNDARY.md) adds an opt-in native CPU `service_interrupt_boundary()`: PPU NMI edge first, external level IRQ only when unmasked, interrupt vectors/stack flags, seven-cycle entry, CLI/SEI/PLP old-I polling approximation and RTI immediate I behavior. ROM-free CTest exercises vectors, NMI-over-IRQ, level re-entry and opt-in isolation. **Original 0553 replay still uses synthetic PPU status and manual NMI**, with no VRC6 IRQ counter or precise CPU bus-phase/DMA scheduling. VPP27, strict PRG 49,504/262,144, 4,261 instruction sites and last semantic frontier 0508/$FB96 unchanged.

## 0554 Phase 4B — VRC6a IRQ device foundation (ROM-free)

[IRQ counter report](../analysis/0554_PHASE4B_VRC6_IRQ_CLOCK.md) adds the standalone VRC6a $F000 latch/$F001 control/$F002 acknowledge register device. CPU-clocked counter offers cycle mode and scanline-approximation 114/114/113 prescaler; test checks IRQ overflow/reload, acknowledge/re-enable, disabled freeze, and register rejection. **Device remains disconnected from CPU/bus**; no source-derived gameplay timing or Mesen parity claim. Strict 49,504/262,144, VPP27/100, compiled starts 4,261, last semantic frontier 0508/$FB96 unchanged.

## 0554 Phase 4C — opt-in VRC6 IRQ wired to static-native CPU

[Integration proof](../analysis/0554_PHASE4C_VRC6_IRQ_INTEGRATION.md) wires the standalone VRC6a IRQ device to every native CPU cycle, final-cycle direct $F000/$F001/$F002 register stores and opt-in CPU interrupt priority. CTest covers overflow/ack, CPU cycle timestamps, NMI priority, indexed stores and fail-closed unknown addressing. 0553 scripted ROM boot is **not changed**. VPP 27/100, strict PRG 49,504/262144, 4,261 instruction sites; no original-frame or hardware-cycle parity claim.

## 0554 Phase 4D — OAMDMA 513/514 CPU stalls for bounded internal-RAM pages

[OAM DMA proof](../analysis/0554_PHASE4D_OAM_DMA_STALLS.md) adds opt-in $4014 RAM-page OAMDMA with explicit CPU get/put parity, 256 source read/OAM writes, 513/514 CPU stall cycles, per-byte bus-cycle timestamps and inherited PPU/VRC6 clocks during DMA. CTest covers RAM mirrors, OAM wrapping, NMI/IRQ emerging while DMA-halted, and fail-closed unsupported pages/bus phases. No DMC overlap, live $2003/$2004, PRG/I/O DMA sources or game-frame parity; the original 0553 scripted replay is untouched. VPP27/100, strict 49,504/262,144, 4,261 compiled sites unchanged.

## 0554 Phase 4E — OAM registers and DMA share memory

[Bounded PPU OAM register integration](../analysis/0554_PHASE4E_OAM_REGISTERS.md) adds timed $2003 OAMADDR, $2004 OAMDATA read/write, 8-byte mirroring and shared OAM backing with internal-RAM $4014 DMA. During enabled visible/pre-render periods or without a DMA-backed OAM instance, OAM accesses reject rather than fabricating rendering-time corruption. Existing scripted 0553 reset/NMI driver is unchanged. VPP27, strict 49,504/262,144; compiled starts 4,261.

## 0554 Phase 4F — bounded explicit DMC DMA sample fetch

[ROM-free DMC fetch gate](../analysis/0554_PHASE4F_DMC_DMA_FETCH.md) adds a request-driven 3/4-cycle DMC sample fetch from fixed PRG $C000–$FFFF, with caller-authenticated CPU read boundary and get/put phase. CPU/PPU/VRC6 clocks continue during the stall; competing OAM DMA requests reject, rather than asserting unsupported overlap accuracy. No automatic $4015 playback timing, sample sequencing, DMC IRQ, or actual game-frame parity. Strict49,504/262,144, VPP27/100, native compiled4,261 unchanged.

## 0560 — host-native C++ port of raw0A selector (source-first)

[0560 source translation report](../analysis/0560_RAW0A_NATIVE_ROOM_SELECTOR.md) introduces `native/bank0a/room_selector_native_0560.hpp`, a readable C++ implementation of original $801E–$8046 three-level pointer selection, with 15 stage groups, 64 middle roots, 135 bounded leaf indexes and original structural data types. Existing ROM-backed 135-case native-CPU driver now independently compares the original statically compiled 6502 path with the host-native routine. Synthetic 135-case ROM-free unit test and corrupt-boundary gates added. No extra instruction sites or strict-certified PRG bytes; VPP27/100, 49,504/262,144, 4,261 compiled sites remain unchanged.

## 0561 — raw0A original $B8CC room-message selector to readable C++

[0561 semantic source port](../analysis/0561_RAW0A_NATIVE_ROOM_MESSAGE.md) adds `native/bank0a/room_message_native_0561.hpp`: group predicate $07F6/$0781, 5 message stages per group, RAM $07A5 index, typed $FF terminal/next-offset contract. Ten original source message tables occupy 22 bytes; ROM-free corrupted-case tests and 10-entry original-ROM structural checks in the native bank0A driver. The external fixed-bank $EC47 renderer is *not* fabricated. VPP 27/100, strict 49,504/262,144, compiled 4,261 sites unchanged.

## 0562 — C11 static recompilation ABI and dynamic interpreter fallback

[Source-first C pivot](../analysis/0562_C11_STATIC_RECOMP_ARCHITECTURE.md) adds a portable C11 2A03 `JpCpu`/`JpBus` ABI, official-opcode semantic interpreter, physical VRC6 bank addressing, fail-closed unsupported hardware, ROM-free CTest and a generator that emits bank raw0A's 2,357 existing opcode sites as **local** C11 code from byte-exact authenticated ASM. Candidate code is off by default; fallback is opt-in and separately counted. The existing C++ hardware code and parity tests remain; this does **not** yet constitute a fully migrated game. Strict 49,504/262,144, 4,261 existing C++ sites and VPP 27/100 unchanged.

## 0563 — C11 generated raw0A actual original-6502 replay gate

[0563 source-native-C pipeline](../analysis/0563_C11_ORIGINAL_SELECTOR_REPLAY.md) adds a C original-bank driver (`native/c6502/raw0a_driver_0563.c`) and a generator/rebuild/original-CPU replay harness (`tools/test_c6502_regen_0563.py`). Privately supplied original JP ROM regenerates audited 0538 ASM, emits source-driven C11 instructions, compiles the result, executes all 135 bounded $801E selectors and independently compares stage/middle/leaf pointers with original 6502. Public CI compiles artificial generated C and rejects untrusted generator rows; **original-backed C results are local-only**, and no gameplay/strict-parity credit is added. Coverage unchanged.

## 0564 — C11 generators span existing native 4,261 instruction starts

[0564 full-current-site C11 source generation](../analysis/0564_C11_FIXED_AND_RAW0A_GENERATION.md) adds an original-JP C generator for 1,904 historical fixed31 + scripted reset/NMI physical instruction starts, and a `regen_c11_0564.py` local build command producing source-derived C11 for those and the prior 2,357 raw0A starts. C11 dispatcher admits bank-qualified fixed code; untrusted mapper aliases still reject. **Neither unproven candidate code nor synthetic scripted NMI counts as natural gameplay parity.** Existing C++ hardware remains, ROM-derived C artifacts are local-only, and coverage VPP27/100, 49,504/262,144 strict PRG remains unchanged.

## 0565 — link generated original game C into C-only bounded host

[0565 native-C executable](../analysis/0565_C11_NATIVE_HOST_LINK.md) adds `native/c6502/main.c` with private original-ROM load, reset-vector dispatch, fixed+raw0A generated C linkage, opt-in interpreter fallback, clear first-unsupported-PC diagnostic and bounded execution, plus `native/c6502/CMakeLists.txt` with explicit original-generated or host-only modes. Public ROM-free CI links and executes artificial C-generated fixture and rejects non-authenticated media. Does **not** implement real hardware frames, controller, PPU, APU, full VRC6 IRQ or gameplay yet. Strict PRG49,504, VPP27 and original 4,261 sites unchanged.

## 0566 — independent upstream NESRecomp VRC6 source and licensing audit

[0566 StarFox/NESRecomp compatibility audit](../analysis/0566_UPSTREAM_NESRECOMP_VRC6_AUDIT.md) confirms NESRecomp upstream cycle runtime has `runner/cyc/hw_vrc6.inc` and mapper24/26 tests, although published supported-game table does **not** certify mapper24 as playable. A fail-closed, non-vendoring local `tools/probe_nesrecomp_cycle_0566.py` authenticates the JP ROM then optionally invokes an external licensed `nesrecomp build --backend cycle` to identify generated C files; public CI exercises only ROM-free mapper and SHA rejection. NESRecomp is PolyForm Noncommercial 1.0.0, so direct code reuse requires license review; the current C11 implementation remains independently authored. VPP 27/100 and strict 49,504/262,144 unchanged.

## 0567 — Windows native C host compiles/links in CMake

[0567 Windows link gate](../analysis/0567_C11_NATIVE_HOST_WINDOWS_LINK.md) extends the existing boot CMake with a C-only `jp_c6502_host_link_0567` target. An **artificial** static-code fixture replaces local ROM-generated game code in public CI; this guarantees C11 `main.c`, native CPU and link ABI compile under Windows MSVC as well as Linux. Separate Linux tests execute a synthetic generated-C host and check the fail-closed original-ROM guard. No original gameplay/full-NES compatibility claimed; VPP27, strict49,504/262,144, existing sites4,261 unchanged.

## 0568 — optional cycle-accurate C11 VRC6 engine integration point

[0568 external C11 runtime build](../analysis/0568_EXTERNAL_NESRECOMP_CYCLE_BACKEND.md) adds `native/nesrecomp_cycle/CMakeLists.txt` using NESRecomp's external cycle-generation `nesrecomp_add_cycle_game`, with private original-JP SHA/mapper24 validation, external PolyForm-NC license gate and a bounded headless 120-frame invocation/report command in `tools/nesrecomp_cycle_0568.py`. CI tests synthetic command-building and failure gates; **actual upstream retail game execution has not yet been attempted in CI**. All copied/generated original-code and upstream runtime source stay outside this repo. Legacy C++ evidence and independent 0562–0567 C11 backend retained; VPP27, strict49,504/262,144, sites4,261 unchanged.

## 0569 — pinned upstream C11 mapper24 cycle test with synthetic cartridge

[0569 cycle-runner smoke](../analysis/0569_NESRECOMP_SYNTHETIC_MAPPER24_SMOKE.md) adds a ROM-free public action `jp_nesrecomp_cycle_mapper24.yml` that checks out the external PolyForm-NC C engine at pinned commit, builds a synthetic mapper24 VRC6 256KiB PRG/128KiB CHR cartridge, generates and compiles upstream cycle C, and requests three native headless frames. The artificial ROM exercises PRG bank switches, PPU NMI, $4014 DMA, VRC6 IRQ and WRAM gating. Results are **a hardware integration smoke only**, not Japanese commercial ROM frame parity. Coverage remains 27/100 and 49,504/262,144; 4,261 prior sites.

## 0570 — synthetic VRC6 loop/IRQ code separation

[0570 regression](../analysis/0570_SYNTHETIC_VRC6_LOOP_FIX.md) fixes a synthetic mapper24 fixture instruction collision: original synthetic $E02E JMP was overwritten by test IRQ code at $E030. IRQ/NMI moved to $E080/$E090; complete JMP, vectors and corruption rejection are tested. Earlier external 3-frame process success did **not** prove correct fixture execution. No original-game parity credit added.

## 0571 — strict synthetic VRC6 99% native-cycle and zero-interpreter CI

[0571 native-cycle proof](../analysis/0571_PINNED_VRC6_NATIVE_CYCLE_GATE.md) records corrected synthetic mapper24 test metrics: 86,951/86,958 CPU cycles executed by generated C11, zero ROM/RAM interpreter fallbacks in 3 headless frames. The external C11 runner workflow now parses stdout and REQUIRES ≥99% native-cycle share, exactly 3 frames, and no interpretation; process exit alone no longer counts. **These are synthetic test metrics, not Castlevania III retail gameplay parity.** No strict PRG/VPP progress credited.

## 0572 — original-ROM C cycle-runner records interpreted fallbacks

[0572 original-ROM metrics](../analysis/0572_ORIGINAL_JP_NATIVE_CYCLE_METRICS.md) splits upstream statistics handling into measurement-only `parse` and strict synthetic `check`. `nesrecomp_cycle_0568.py` now requires the actual requested number of completed frames and writes total/native CPU-cycle fraction plus ROM/RAM interpreter counts into its local JSON report. This prevents claiming a process success as 100% native code. Original-JP C cycle execution still needs an external licensed engine on the user's machine; no original gameplay/Mesen parity credit awarded.

## 0573 — actual Japanese ROM native C11 selector build (local)

[0573 real-ROM C compilation](../analysis/0573_ORIGINAL_ROM_C11_SELECTOR_BUILD.md) authenticated the user-uploaded Japanese mapper24 ROM and built a 24-instruction original-bank0A $801E selector into an executable with GCC C11. 135/135 bounded pointer results matched both authenticated ROM tables and an independent 6502 interpreter. `tools/build_original_c11_0573.py` now persists the existing source-generated **2,357-site bank0A C11 test** as a separate local executable/report, with synthetic smoke in CI. **This is not a full playable ROM build:** the external NESRecomp cycle source is unavailable in the local sandbox; no retail-game frames or new PRG/VPP coverage certified.

## 0574 — independent VRC6a $C000 PRG bank mapping in C11

[0574 VRC6a PRG correctness](../analysis/0574_C11_VRC6_INDEPENDENT_PRG_WINDOWS.md) corrects C11 ROM mapping: $8000–$BFFF selected 16 KiB, $C000–$DFFF **separately selected 8 KiB**, $E000–$FFFF fixed last 8 KiB, with $F003 address-register mirrors and a single common physical-offset resolver for native generated fixed code and interpreted reads. Focused tests cover selector independence and mirror behavior, not reconstruction census. External cycle backend still required for PPU/APU/VRC6 IRQ/audio/WRAM, and VPP27, strict49,504/262,144, 4,261 existing compiled sites unchanged.

## 0575 — single-command pinned external retail-JP C11 build

[0575 external original-game build](../analysis/0575_C11_RETAIL_GAME_BUILD_BOOTSTRAP.md) adds `tools/build_retail_cycle_0575.py --rom ORIGINAL.nes --out /private/jp-build --frames 120` to authenticate Japanese mapper24 ROM, clone exactly pinned PolyForm-NC NESRecomp outside Git, build C11 cycle game and report actual compiled/interpreted CPU cycles. Lightweight Windows/Linux C11 CI validates command safety, not ROM reconstruction. The full-game engine cannot be downloaded within this sandbox; original game playback remains unproven and VPP/strict PRG unchanged.

## 0576 — test actual external CMake wrapper without commercial media

[0576 exact-media C11 wrapper gate](../analysis/0576_C11_EXTERNAL_CMAKE_WRAPPER_GATE.md) switches the pinned external NESRecomp synthetic workflow to configure our **own** `native/nesrecomp_cycle/CMakeLists.txt` target, rather than upstream's example project. Adds default-OFF `JP_CYCLE_SYNTHETIC_MEDIA` option and SHA-exact synthetic fixture validation in `tools/validate_cycle_media_0576.py`; authenticated commercial ROM remains the only accepted production input. Targeted CI compiles and executes only synthetic mapper24 frames, with 0571 native-cycle and zero-interpreter assertions. No reconstruction tests/strict PRG/VPP claim.

## 0577 — original-JP C11 compile-only binary/report separate from gameplay

[0577 C11 native build evidence](../analysis/0577_ORIGINAL_C11_BUILD_ONLY_AND_BINARY_IDENTITY.md) adds `--build-only` to both external cycle and one-command pinned boot scripts. Native binary SHA-256, original ROM identity and CMake compile logs are recorded as `jp_cycle_build.json` immediately after successful compile, *even if a later guest boot fails*. A narrowly scoped Windows/Linux mocked-build test checks artifact persistence, authentic binary-fingerprint reporting and no false gameplay success; no ROM reconstruction runs. Full original game compile is still blocked locally by unavailable separately licensed upstream engine source; VPP27 and strict PRG unchanged.

## 0578 — C11 original-game headless frame hashes, screenshot, optional route

[0578 frame evidence](../analysis/0578_C11_FRAME_HASH_PNG_AND_INPUT.md) adds frame-indexed observable CPU/memory/hardware hashes and final 256x240 PNG for *private original-ROM* headless runs, plus optional `--input-script` controller schedule (no gameplay recording required). Reports include file SHA256, final PC/cycles and frame count, without claiming parity. The pinned public synthetic VRC6 workflow exercises actual NESRecomp `--hash-out`/`--screenshot` outputs; targeted malformed-evidence checks only, no reconstruction sweep. VPP27 and strict PRG unchanged.

## 0584 — real Japanese original-ROM C11 Alpha candidate compiled

[Release milestone status](RELEASE_MILESTONES.md) now reflects an authenticated original-JP mapper24 C11 game executable compiled for **Windows x64 with SDL2** and a private ROM-free archive/launcher. Local original game ran 600 seeded frames at 99.99996% native CPU cycles with 0 interpreted ROM/RAM and byte-identical per-frame observable hashes vs unseeded. A separate 3000-frame original-JP scripted-input route reached visible **Stage 1** at 96.8% native CPU cycles. Actual Windows interactive/controls/audio QA is **pending**. This is a privately shared Alpha *candidate*, not a qualified public release. No further reconstruction sweep or new VPP/strict PRG credit.

## 0585 — owner's first Windows Alpha playtest: no issues reported

The owner independently reported that the original Japanese native C11 Windows game is "playing flawlessly" and appears potentially playable through the whole game. Mark this **initial interactive Alpha acceptance** (reported, not independently reproduced here), not a completed full-game route or Beta/Final qualification. Next step is lightweight progression-based Beta checks: Stage 1 boss/exit, later stages, partners, pause/audio, saves if available. No reconstruction work or new strict PRG/VPP credit. [Release gates](RELEASE_MILESTONES.md).

## 0586 — user completes Stage 1 boss and enters lower Stage 2 route

Owner of the private native-C Windows Alpha confirms Stage 1 boss defeat and successful Stage 1 exit/branch transition, reaching **the start of Stage 2 bottom/lower route**. No fault reported. First Beta progression gate satisfied, but Stage 2 completion, alternate routes, characters, saves and endings not yet observed. Play normally and report only concrete blockers; no ROM reconstruction or gameplay recording needed. [Release gates](RELEASE_MILESTONES.md).

## 0587–0588 — Stage 4-0A, Sypha and dual-edition plan

User-confirmed Windows native C11 progression now reaches **Stage 4-0A**, with **Sypha recruited and character switching verified**; minor sprite artifacts reported in the purple area and tracked alongside distinct Stage 2 priority artifacts in [graphics issue #1](https://github.com/Hyperbog/CVIII-Decomp/issues/1). The user also defined two products on one engine: faithful **Original** and configurable **Enhanced**, including widescreen, sprite-limit removal, per-channel/music-SFX isolation, replacement music/graphics, rebindable input, and opt-in new moves that never silently change baseline mechanics. [Edition architecture and roadmap](ORIGINAL_ENHANCED_EDITIONS.md); issues #2–#9. No new code coverage, VPP or gameplay test claim.

## 0589 — executable Original/Enhanced C11 extension and experimental 64-OAM sprites

[0589 C11 host extras](../analysis/0589_ORIGINAL_ENHANCED_HOST_RENDERER.md) adds original-by-default `--edition original|enhanced`, persisted `[Game]` settings and an **opt-in experimental** background+64-OAM sprite presentation mode to the real external NESRecomp game target. The emulator's $2002, sprite-0 hit, sprite overflow, DMA and mapper logic remain unchanged. Focused mocked C11 present-contract test plus actual synthetic VRC6 CI compile; **no evidence yet of production-stage flicker repair or Stage 3/4 background correctness**. Issue #1 broadened to suspected shared background/nametable/scroll issue. VPP and PRG coverage unchanged.

## 0590 — Original renderer A/B backend for suspected shared background glitch

[0590 renderer diagnostic](../analysis/0590_SHARED_BACKGROUND_RENDERER_AB.md) provides `--ppu-impl LLE|HLE` with **LLE default** through authenticated private C11 build and real CMake, retaining both original-JP gameplay paths while isolating background rendering differences. Focused option contract test, no unneeded reconstruction. Owner's Stage 3?/4 purple foreground complaint remains issue #1; no root cause or fix claimed. VPP/strict PRG unchanged.

## 0591 — shared Original/Enhanced complete-machine save states with 10 slots

[0591 save-slot design and implementation](../analysis/0591_SHARED_ORIGINAL_ENHANCED_SAVESTATES.md) extends NESRecomp's existing F8/F9 **whole-machine** quick-save path through a private-build SDL host overlay: **Ctrl+0–9 selects a slot**, F8 saves/F9 loads, with on-screen toasts. Slot0 keeps the existing Alpha filename; numbered slots use `.slot1`–`.slot9`, shared across Original and Enhanced presentation presets. The pinned third-party source remains unmodified; build-time CMake rejects patch drift and unexpected host source lists. Focused ROM-free parser and actual upstream patch contract CI only; real windowed compile and interactive usability still need validation. No reconstruction/coverage increase.

## 0591a — repair cross-edition save-state renderer-section mismatch

Targeted Original-save/Enhanced-load CI exposed `cyc.background` aux-state length mismatch when capture was disabled in Original. The edition host now always captures presentation-only background data but only composites sprites when opted into Enhanced, so the same whole-machine state schema is valid in both. Original displayed pixels and CPU-visible NES state remain unchanged. Independent frame-hash comparison across editions is the acceptance gate; no reconstruction or PRG/VPP change.

## 0592 — Original/Enhanced Windows private Alpha 0.2 candidate

[0592 original-game Windows Alpha 0.2](../analysis/0592_ORIGINAL_ENHANCED_ALPHA_02_WINDOWS.md) is now cross-compiled from the owner-authenticated Japanese mapper24 ROM using C11/SDL2, with distinct Original and experimental Enhanced all-OAM sprite-compositor launchers. The private ZIP contains no ROM. Focused 600-frame CPU/PPU/memory hash logs are byte-identical between the two modes on the authentic game; Windows GUI Enhanced still needs owner testing. The public ROM-free builder kit was updated to 0.2.0-alpha.1 with separate launchers. Shared Stage 2/3?/4-0A background defect #1 remains unresolved. No reconstruction sweep or strict PRG/VPP credit.

## JP 0594 — F10 windowed stage / companion checkpoints

A real windowed F10 stage menu is patched onto the privately built
pinned NESRecomp SDL host *after* the 0591 ten-slot extension. It
pauses emulation, offers 18 stage labels and None/Alucard/Sypha/Grant,
captures the current **entire** machine state with F5 and loads the
selected captured checkpoint with Enter. Capture does not change
character inventory or stage; a checkpoint must already exist before
warping there. This is a genuine in-game checkpoint warp, not a direct
arbitrary-stage initializer or a decoded-password injection. It uses
the existing state loader's atomic validation, frame-counter reset,
session notification and netplay restriction. Debug overlays do not
alter the guest framebuffer or CPU/PPU mapper state.

Windowed synthetic-source compilation and owner GUI gameplay
acceptance are separate gates. Strict PRG 49,504 / 262,144 and
VPP 27 / 100 remain unchanged; semantic frontier PRG31 $FB96.

## JP0596 stage bootstrap

F10 now has a one-time password-entry bootstrap path, so test stages can
be requested without reaching/capturing every checkpoint individually.
On a stage snapshot miss, a valid captured password-entry machine is
loaded, the corresponding name-bound password filled at $0790..$079F,
and the **original game's password confirmation** performs stage init.
Normal/Hard (Tab) and companion route validation are supported.
Needs private real-JP GUI acceptance; semantic frontier and PRG/VPP
coverage are unchanged.


## JP0597 — ROM-authenticated private offline asset pack

The first asset-package slice extracts **complete physical CHR ROM**
(128 * 1 KiB pages; 8,192 planar NES tiles) and deterministic decoded
8x8 palette-index pixels. It also records all six original-JP password
tables at their authenticated physical 8 KiB PRG bank offsets.
Per-entry SHA256, per-page SHA256, a complete versioned manifest and
exact 2bpp-to-indices-to-2bpp reconstruction are checked. A later build
reuses a cache only after full verification; malformed or stale archives
fail closed. Private Windows Alpha builders create an owner-local
CVIII-Assets.bin, explicitly omitted from public CI artifacts.

This is **an offline cache**, not a rewritten graphics renderer, a
stage-data decompilation, or a substitute ROM for NESRecomp.
Background/sprite interpretation, metatiles, palettes, stage maps,
animation, music, and text extraction remain open; no strict semantic
PRG or VPP progress is claimed.

## JP0598 — Read-only CHR cache loaded by Enhanced (first integration gate)

The private Alpha builder now exports **CVIII-CHR-Index.dat** alongside
CVIII-Assets.bin. On Enhanced launch only, the host loads this fixed-size
(655,368-byte) cache through `--asset-index`. The standalone C11 index
reader checks exact geometry, magic, the pinned Japanese CHR content
identities and a complete **tile-by-tile 2bpp reconstruction**.
The Python exporter also verifies the canonical SHA-256 of the original
CHR and decoded tile index. Corrupt or wrong-ROM data fail closed.

**No game rendering has been redirected.** The NESRecomp PPU remains
authoritative for Original *and* Enhanced; no CPU, PPU, APU, VRC6 or
game-state writes are made. This creates a validated in-process CHR
source for later Enhanced rendering without assuming static graphics
can replace the original hardware's changing bank/palette registers.

Original launch does not request the cache. An Enhanced run with
no cache falls back to unchanged ROM graphics. In the private Windows
builder the cache is regenerated only when needed and remains local;
public CI uses synthetic pixels, not copyrighted cartridges.


## JP0599 — Optional VRC6 CHR mapping audit

JP0598 gave Enhanced a verified read-only cache of every original JP
CHR tile. JP0599 now observes which physical bank each of the eight
PPU pattern windows selects at **sampled frame boundaries**, plus
the current PPU palette RAM. To generate a private CSV:

    powershell -ExecutionPolicy Bypass -File .\Launch-Alpha.ps1 -Rom "C:\Games\Akumajou Densetsu (Japan).nes" -Edition Enhanced -ChrAudit

The opt-in **CVIII-CHR-Audit.csv** is created beside the private EXE.
It records one sample per 60 emulated frames: VRC6 mode/control,
eight physical 1-KiB bank IDs, current 32 PPU palette bytes, and
PASS/FAIL of an independent bank-map calculation against NESRecomp's
reported CHR offsets. Original retains its existing unmodified PPU
presentation; Enhanced does not yet draw from this cache.

**Scope limit:** A frame-end sample cannot see a bank switched in
and out during a scanline. This is not yet proof of pixel/scene
rendering parity. No user gameplay modifications are enabled by
the diagnostic. The editor remains a deferred future product.


## JP0600 — Actual PPU pattern-fetch cache parity, no renderer substitution

With a privately built Japanese Alpha, use the existing opt-in
**-ChrAudit** parameter on **Launch-Alpha.ps1** with **-Edition Enhanced**.
This now produces two separate owner-local reports:
- **CVIII-CHR-Audit.csv** — JP0599 end-of-frame VRC6 CHR bank selection
  and palette RAM every 60 emulated frames.
- **CVIII-CHR-Fetch.csv** — JP0600 sampled *actual PPU pattern reads*
  with the physical CHR-ROM page, cached 2bpp byte/indexed-pixel
  reconstruction parity, and observed CHR bank changes **within each
  scanline**. The native host only observes one out of 60 frames.

Example (run in your private AlphaCandidate directory):

    powershell -ExecutionPolicy Bypass -File .\Launch-Alpha.ps1 -Rom "C:\Games\Akumajou Densetsu (Japan).nes" -Edition Enhanced -ChrAudit

Validate/summarize the fetch log (Python tool is in JP/tools in the
repository, and requires no ROM for this analysis):

    python JP/tools/jp_chr_fetch_report_0600.py --csv "C:\Games\CVIII-CHR-Fetch.csv" --require-parity

The report lists total sampled pattern reads, bad cached bytes,
invalid mapped addresses, encountered physical CHR pages per PPU
window, and within-line bank changes. A nonzero exit from
--require-parity means that at least one observed read disagreed
with the loaded cache or had an invalid mapping.

**Limitations:** Synthetic CI establishes the instrumentation
interface and checks trace rules, but a privately observed Japanese
retail gameplay trace is still needed to establish acceptance in
real stages. The hook observes pattern reads, not all nametable
accesses, pixel priority or complete rendered-frame equivalence.
Neither Original nor Enhanced currently substitutes cached CHR data
for the stock PPU image. F10/password stage testing is unchanged.

## JP0601 — Synchronized original PPU frame evidence (diagnostic-only)

The opt-in Enhanced `-ChrAudit` private launch now produces an additional
**CVIII-Frame-Evidence.csv** aligned to the JP0600 1-in-60-frame pattern
fetch capture. Each sampled original NES PPU frame records:

- The sample frame number and the actual CHR read/mismatch/invalid counts
- Observed CHR bank switches during sampled scanlines
- Deterministic 64-bit checksums of the PPU's original 9-bit color indices
  (color and emphasis), background-opaque mask, and 240 scanline scroll/mask
  records serialized without C structure padding
- Background opaque pixel count and number of scanlines with background or
  sprite rendering enabled

These hashes are **original PPU observations**, never graphics generated
from the cache. Neither edition changes its default presentation or game
state. The report joins source-byte observations and original PPU outcomes
on the same sampled frames, rejecting missing frames, inconsistent read
counts, bank switch totals or malformed fingerprints.

When launched with `-Edition Enhanced -ChrAudit`, the private launcher
generates **CVIII-Frame-Evidence.json** after the game exits and requires
cache/PPU fetch-source-byte parity. To rerun the validation manually:

    python jp_frame_evidence_report_0601.py --fetch CVIII-CHR-Fetch.csv --evidence CVIII-Frame-Evidence.csv --require-parity

The original retail Japanese game still needs a local Windows GUI playtest
spanning multiple stages and companion routes. Successful source-byte
comparisons and original PPU fingerprints **do not establish independent
cache-backed sprite/background framebuffer parity**. Enhanced still renders
using the original PPU except for separately opted-in experimental effects.
This diagnostic milestone does not increase strict PRG/VPP semantic coverage.


## JP0602 — Private owner-only scene QA matrix

The JP0600/0601 frame/fetch observations are now collected without
overwriting earlier scenes. Use the new **Capture-QA-0602.ps1** in the
private AlphaCandidate directory:

    .\Capture-QA-0602.ps1 -Rom "C:\Games\Akumajou Densetsu (Japan).nes" -Scene village-entry -Area village -Character Trevor -Kind gameplay -Checkpoint 1-01

This starts the real Japanese native game with Enhanced mode's **stock
NES PPU presentation** and the read-only CHR diagnostics. Play the
declared scene and close the game. A distinct folder under local QA/
retains the five evidence CSV/JSON files and an authenticated
capture.json including the owner's ROM fingerprint, current native
EXE/CHR-index hashes and each evidence file's SHA256. Nothing is
automatically uploaded. **Scene/stage labels are user-supplied
annotations, not independent proof of which level was entered.**

Other suggested -Area values: title, clock_tower, forest, ship,
castle, boss and companion; set -Character to Trevor, Sypha, Grant
or Alucard where appropriate. Capture at least 10 sampled frames
per scene (about 600 emulated frames); one out of 60 frames is
instrumented. A shorter capture is retained but reported as shallow.

Then aggregate all local sessions:

    python .\jp_qa_matrix_0602.py --root .\QA --json .\QA\CVIII-QA-Matrix.json

Or pass --require-coverage to ask the checker to fail until all eight
target scene areas have sufficiently sampled trace evidence.
The checker verifies source-ROM declaration, per-file hashes, all
JP0600/0601 original PPU and physical-read count consistency and
stage/character scene coverage. Corrupt captures fail closed.
Different native executable fingerprints are reported, not silently
treated as same-build deterministic comparisons.

**Still not proven:** The actual retail Japanese game has not been
sampled across these routes here. Source CHR-byte matches and
original-PPU fingerprints do not demonstrate independent cached
renderer parity. Original's renderer, gameplay and F10 controls are
unchanged; Universal NES Studio remains future work.


## JP0605 — Single Enhanced Edition product decision

The owner elected to release one user-facing native **Enhanced Edition**
instead of two public "Original" and "Enhanced" choices. The authentic
Japanese NES ROM/cartridge is the baseline experience; do not duplicate
it as a separate public PC product. The former original renderer
and original simulation/PPU paths remain in the code as **internal
reference diagnostics** for Stage A-01 graphics parity and gameplay
regressions, accessible via an explicit developer `-Edition Original`
argument. Existing F10 debug tools stay private.
The ROM-free Alpha kit and private Windows candidate now offer the
single `Play-CVIII.bat` entry point, default to Enhanced, and keep
unverified compositing switched off. This is a product/UI change, not
a claim of Stage A-01 or sprite-layering bug fixes. The strict PRG
49,504/262,144 and VPP 27/100 remain unchanged.

## JP0606 — Stage A-01 shared PPU background corruption investigation

The first JP0606 slice adds **read-only actual nametable and attribute
bus read tracing**, not a speculative rendering change. The pinned
NESRecomp VRC6a mapper's common `$B003 = $20/$24/$28/$2C`
mirroring logic is consistent with NESdev's documented mode-0
behavior, so no hardware mapping is modified without gameplay
evidence. The shared Stage A-01 pixel corruption remains an open
defect in both reference/Enhanced rendering paths.

Rebuild the private native Enhanced candidate and launch Stage A-01 with
`Capture-QA-0602.ps1`. The captured scene folder contains an extra
`CVIII-NT-Fetch.csv` and `CVIII-NT-Fetch.json` in addition to the
preexisting QA-matrix evidence. Every sixtieth emulated frame the new
hook observes actual PPU nametable tile and attribute bytes, their
nametable/CIRAM-versus-cartridge source, timing and per-scanline hash.
The report checks that these samples align with the original PPU
frame fingerprints. Explicit empty samples represent frames with
rendering disabled during title transitions.

These extra JP0606 files do not alter the v1 QA manifest's expected
five files, preserving backward compatibility with older owner
captures. They remain in the same private scene directory for targeted
Stage A-01 analysis and comparison against MesenCE.
There is still **no** retested retail Stage A-01 screenshot proving a
graphics fix; ROM-free CI only verifies the observer, bus report,
private native build, and existing original-frame hash invariants.

## JP0611 — sound-request dispatcher and static caller research

New [ROM-locked audit](../tools/jp_sound_request_census_0611.py) and [analysis](../analysis/0611_SOUND_REQUEST_ENTRY_CENSUS.md) authenticate fixed $E249 -> raw-$0C $8850's three original command paths and count 123 JSR / 8 JMP $E249 **physical opcode-pattern candidates**, 120 with adjacent immediate-load bytes. This is explicitly NOT runtime caller liveness or independent music/SFX attribution. The next work requires real E249 request-entry/priority traces paired with the existing 0610 audio-register writer report. No strict verified PRG change (49,504/262,144), no VPP change (27/100), no semantic state-frontier change (0508, fixed FB96).

## JP0612 — owner-only fixed $E249 sound-request observer

The [JP0612 trace design](../analysis/0612_SOUND_REQUEST_RUNTIME_TRACE.md) and [private generated NESRecomp fetch-overlay tool](../tools/patch_cyc_sound_requests_0612.py) now provide an opt-in `CVIII-Sound-Requests.csv` next to JP0610 `CVIII-Audio-Registers.csv`. For real opcode fetches at original fixed $E249, the observer records command A and snapshot registers/cycle/bank/raw-stack bytes. It suppresses interrupt-discarded fetches, supports both native static and fallback interpreter paths and does not affect audio hardware, PPU, timing model or host PCM. Synthetic C11 and Python patch contract tests pass. Exact private native Windows integration and external original-Mesen trace comparison remain outstanding. **No semantic coverage/VPP change:** strict 49,504/262,144, VPP 27/100; certified 0508 and fixed FB96 unchanged.

## JP0613 — conservative source-request / register-write temporal windows

[ROM-free paired CSV validator](../tools/jp_sound_request_report_0613.py) and [evidence limits](../analysis/0613_SOUND_REQUEST_REGISTER_PROXIMITY.md) correlate JP0612 original $E249 ingress with JP0610 hardware-register writes only by bounded CPU-cycle proximity, rejecting malformed rows and backward cycles. No claim is made about true sound-request acceptance, speaker allocation, music/SFX source ownership or frame/audio parity. A synthetic CI smoke target was added; original owner-private capture replay and MesenCE comparison remain outstanding. Strict 49,504/262,144, VPP 27/100, certified 0508 / fixed FB96 remain unchanged.

## JP0614 — Sound trace provenance without runtime audio changes

[JP0614 private capture integrity](../analysis/0614_AUDIO_SESSION_EPOCH_PROVENANCE.md) ties the existing sound request and APU/VRC6 write CSVs to a new power-on/load epoch CSV by owner-local GUID, exact SHA-256 hashes and cumulative event-row boundaries. A save-state CPU clock rewind is therefore separated, not silently combined. Strict C11 and Python synthetic tests pass locally; current Windows native Alpha/MesenCE replay and CI results are not claimed. No original sound-driver source ownership or semantic PRG proof promoted: 49,504/262,144, VPP 27/100, certified checkpoint 0508, fixed FB96.

## JP0615 — Independent reference sound-request comparison prepared

[JP0615](../analysis/0615_MESEN_SOUND_REQUEST_REFERENCE_GATE.md) adds an original MesenCE/Mesen2 E249 Lua execute observer and a strict JP0614 native-to-reference request register/stack/command comparator, with independently pinned JP-ROM and reference executable SHA-256 requirements. Three physical PRG21 raw-$0A command producer patterns ($06/$6A/$6B) were individually verified; only $6B is separately conditionally executed in 0508 Phase 11. A ROM-free synthetic comparison passes; real original Mesen/Windows owner-trace parity, actual accepted SFX, audio output and source provenance remain OPEN. No ledger increment: strict 49,504/262,144, VPP 27/100, certified semantic 0508, fixed frontier FB96.

## JP0616 — ROM-authenticated sound dispatcher guard matrix

[JP0616](../analysis/0616_ORIGINAL_SOUND_DISPATCH_GUARDS.md) derives the exact $884F low-command state guard and $8922 DMC priority return from authenticated PRG24 $8842/$8908 bytecode. A bounded instruction-set evaluator independently checks 131,072 synthetic combinations and eight damaged-ROM witnesses. Original Mesen callback and strict gate-pair parser prepare real game-branch evidence, but independent Mesen2 reference execution and matched native owner trace remain unperformed. This establishes source branch logic, **not observable suppressed effects, live command producers, new mixer behavior or audio parity**. Strict 49,504/262,144 (18.8843%), VPP 27/100, certified 0508, fixed $FB96 unchanged.

## JP0617 — Single original command-to-terminal sound decision witness

The [JP0617 unified original-ROM reference gate](../analysis/0617_UNIFIED_SOUND_DISPATCH_REFERENCE.md) replaces ambiguous isolated gate callbacks with one monotonic request ID from source CPU $8852 and one terminal decision. Metadata commands $50–$6E first pass $885D JSR $87AE, then install at $8860; this normal two-stage path is not misclassified as an extra/orphan event. Local five-outcome synthetic regression and eleven rejection tests pass; original-ROM JP0616 131,072-case branch and eight mutation tests rerun. Lua callback execution in the pinned Mesen binary, native matched-gameplay request counts, dropped sound events and music/SFX ownership remain UNVERIFIED. Zero semantic advancement: 49,504/262,144, VPP 27/100, certified checkpoint 0508, fixed FB96.

## JP0618 — Enhanced-only audio volume foundation

[JP0618 specification and test evidence](../analysis/0618_ENHANCED_AUDIO_LEVELS.md) implement three persistent 0–100 volume settings with **1% steps** and 100% defaults. The Enhanced-only host audio callback applies working Master PCM attenuation; the unsplit mixed PCM prevents honest independent Music/SFX attenuation, so those two levels are stored but not yet applied. The player-facing three-slider menu must use original health-bar art plus in-game numeric font and has **not** yet been built. Game physics, original gameplay and sound-register timing are untouched; an internal Original path is retained for A/B debugging only, not shipping. Strict C11 standalone tests pass; native Windows/CI outcomes not independently verified. Verified PRG 49,504/262,144 (18.8843%), VPP27/100, semantic checkpoint 0508, fixed $FB96 unchanged.

## JP0619 — Authentic original-healthbar audio slider visual source + preview

[JP0619 original CHR audit](../analysis/0619_AUTHENTIC_AUDIO_SLIDER_ART.md) pins the Japanese ROM's actual health-meter graphics ($1085 outline/$1093 filled), 0–9 in-game font $1041..$104A, and Latin capitals $1050..$1069. An Enhanced-only, explicitly enabled preview renderer draws three authentic-art volume tracks and original font numbers with visually rounded per-pixel fill for all 0–100 levels. Strict C11 synthetic renderer test and local exact-ROM hash/planar-layout audit PASS; private ROM-derived local preview checked. This is NOT a player-accessible paused menu yet. Master remains the only audio level applied; Music/SFX are persisted but not bus-separated. Windows executable/CI outcomes not verified. Strict semantic PRG 49,504/262,144, VPP27/100, certified 0508, fixed $FB96 unchanged.

## Architecture decision — Expandable Start/Pause and modder-first Enhanced edition

The future [Enhanced modding architecture](ENHANCED_MODDING_ARCHITECTURE.md) reserves a registry-based menu with initial Save State, Load State, Audio and Quit, and easy additional page registration. All core game content is intended to become modular, ID-addressed, replaceable through validated versioned data packs with deterministic load/override order; level and general editors will later use the same formats as the runtime. Original gameplay remains the default faithful baseline, while explicit enhancements and repairs are permitted. **Design-only documentation:** there is not yet a mod SDK, menu registry, or editor. JP0619 remains the noninteractive authentic-CHR volume preview; strict 49,504/262,144, VPP27/100, checkpoint0508/$FB96 unchanged.

## JP0620 — Original-art F6 audio modal, host-native pause and menu setting registry

[JP0620 design/verification](../analysis/0620_PAUSED_ENHANCED_AUDIO_MENU.md) adds an Enhanced F6 modal with original-game health-bar CHR tracks, original-font digits and 1-percent Left/Right adjustment. Up/Down selects, F6/Escape/Backspace or pad B/Start closes. It reuses the pinned SDL window's frame-pausing, input-release, queued-audio and save-config paths via a private fail-closed JP0596-following source overlay. An optional `recomp-ui` build also gets three namespaced registry-backed host menu rows; CI currently disables recomp-ui, so this is separate from the F6 path. Exact committed Python patcher smoke and namespaced C11 registry tests PASS locally; actual pinned SDL overlay compilation, Windows GUI/gamepad, real pause and settings persistence across launches remain unverified. Music/SFX are explicitly marked PENDING; Master remains the only gain applied. Save/Load/Quit combined custom Start/Pause screen still planned. No strict PRG (49,504/262,144), VPP27, checkpoint0508, fixed $FB96 or RESUME_STATE promotion.

## JP0621 — Original pinned SDL four-overlay source-gate, no new UI claims

[JP0621 source-chain gate](../analysis/0621_PINNED_SDL_AUDIO_MENU_GATE.md) adds an executable `JP/tools/jp_audio_menu_pinned_gate_0621.py` that reads the exact pinned NESRecomp `runner/cyc/cyc_sdl.c` Git blob, runs the actual 0591 save slots → 0594 F10 stage → 0596 password → 0620 F6 audio overlay generators in memory, and rejects drift or loss of modal frame pause, key handling, state shortcut isolation and held-input release. It also checks F6 keyboard dispatch priority relative to F10 password debug and the optional `CYC_DEV_UI` shortcut. Both Linux and Windows workflows now exercise synthetic smoke **and** authentic pinned-source analysis before compiling. Verified upstream anchor uniqueness through connected GitHub source inspection; **the complete executable gate has not been run locally, and new CI/Windows executable/gamepad/playback results are not independently verified here**. This phase is an integration gate, not further functionality. Original music/SFX voice separation, unified menu, mod loader, editor and palette matching remain open. Certified strict PRG 49,504/262,144, VPP27/100, checkpoint0508, fixed $FB96 unchanged.

## JP0622 — Native F6 audio modal state isolated, source-identical C11 test PASS

[JP0622](../analysis/0622_ENHANCED_AUDIO_MODAL_STATE.md) moves the original-CHR F6 Audio menu's open/close/selected-row/1%-edit logic to a small host-independent `cviii_audio_menu_state_0622` C11 module. The live Enhanced host delegates its menu API to that module and now closes the modal on power-on, savestate load and engineering Original-mode selection. A strict GCC C11 standalone test was **actually compiled and executed locally using exact committed Git blob copies** of the JP0622 state/fixture and JP0618 volume sources; PASS for asset/mode gating, Master/Music/SFX row navigation, 0–100 endpoint behavior, closed-menu suppression and reset. ROM-free Windows/Linux CI and CMake host integration committed, but new Actions results, complete private native SDL build, owner Windows gameplay/pause/input and save-persistence remain unverified. The future mod-forward combined Start/Pause Save/Load/Audio/Quit menu is not yet implemented. Music/SFX remain settings only pending separate buses; strict PRG 49,504/262144, VPP27/100, checkpoint0508 and FB96 unchanged.

## JP0623 — Mod-forward Start/Pause action registry and original-CHR menu

[JP0623](../analysis/0623_MOD_FORWARD_START_PAUSE_MENU.md) builds the game-owned original-font **F4 Start/Pause** menu with stable built-in action IDs `core.save_state`, `core.load_state`, `core.audio`, `core.quit`. Save/Load call the native host's current-slot full-machine state handlers; Audio opens the existing original-healthbar 1%-step volume page; Quit requires two Accept confirmations before normal host exit. The controller and renderer handle up to 32 registered entries and six-row scrolling, reject privileged action spoofing, protect the panel from long labels, and preserve original gameplay input by requiring F4 from the keyboard to open for now (controller D-pad/A/B/Start operate only once open). No data-mod loader or runtime callable plugin registration exists yet; the four core entries are sealed at initialization. The fifth **private** SDL patch corrects prior JP0620/0621 CYC_DEV_UI event priority (F4→F6→F10→dev), extends the host pause/input-release predicate and composes original JP font from authenticated CHR; it does not alter CPU/PPU/APU registers or ROM data. **Actually run locally:** strict GCC C11 core-registry and original-font synthetic renderer tests PASS, with matching committed Git blobs. Both CI suites are wired to test C11 and run actual pinned five-stage Python source gates; **native owner Windows SDL build, gameplay, real save/load, controller, pause, and new GitHub Actions outcomes have not been verified**. Save-slot chooser/title-screen menu/controllers-open binding/independent Music/SFX remain future work. Semantic PRG 49,504/262144, VPP27/100, checkpoint0508 and fixed $FB96 unchanged.

## JP0624 — Generated F4 Start/Pause action shell gains ROM-free executable coverage

[JP0624](../analysis/0624_PAUSE_SHELL_NATIVE_HARNESS.md) adds `jp_start_pause_shell_test_0624.py`, a harness that **extracts the real `SHELL` C fragment from the committed JP0623 pinned SDL patcher** and compiles it with fake SDL/controller types, fake host actions and the actual game-owned registered action module. It covers F4 gating and repeat, modal gameplay-key ownership, keyboard Enter/gamepad A Save/Load/Audio action dispatch, double-accept Quit, cancellation, gamepad Start/Escape closure, and `NESRECOMP_NET` open refusal. Local strict GCC C11 tests of an equivalent mock host shell **PASS in offline and netplay variants**. The exact-patcher generated harness is committed and invoked on Linux CI; Windows CI verifies authentic shell extraction only. **Execution of that precise generated fixture, the five-layer full pinned SDL build, Windows GUI gamepad/keyboard gameplay and Actions results are not yet independently verified**. This is a testability improvement, not new game mechanics or a completed slot-picker/mod loader. Strict PRG 49,504/262144, VPP27/100, checkpoint0508, fixed $FB96 unchanged.

## JP0625 — Authentic-font graphical Save/Load slot 0–9 picker

[JP0625 implementation](../analysis/0625_ORIGINAL_FONT_SAVE_LOAD_SLOT_MENU.md) extends the Enhanced F4 Start/Pause actions: selecting Save State or Load State now opens a dedicated original-Japanese-font 0–9 slot chooser, not an immediate current-slot I/O call. Keyboard Up/Down/Left/Right and controller D-pad move a slot (wrapping 0↔9); Enter/A confirms the selection, Escape/Backspace/B cancels to parent without touching a file, F4/gamepad Start closes the full menu. Confirmation continues to use the original pinned host's `cviii_save_slot` and full-machine `save_state_slot/load_state_slot` functions, including existing netplay and error handling. A **sixth** private SDL patch layer, ROM-free game-owned C11 slot controller, actual original-CHR digit/letter renderer, six-stage pinned source gate and generated sixth-shell regression are in Git/CMake/CI. **Actually run locally, PASS:** strict GCC C11 slot controller and actual CHR-font Save/Load UI tests with exact authored Git blob hashes. Exact six-stage generator, CI runs, rebuilt Windows window/real state save/load and physical controller acceptance remain **unverified**. No mod loader, audio Music/SFX mixer or 6502 gameplay changes. Strict PRG 49,504/262144, VPP27/100, checkpoint0508, frontier FB96 unchanged.

## JP0626 — Start/Pause Audio Back preserves parent and input pause

[JP0626](../analysis/0626_NESTED_AUDIO_PAUSE_RETURN.md) fixes Start/Pause → Audio → Back returning directly to gameplay: the new game-owned `cviii_menu_stack_0626` parent/child focus boundary leaves the F4 Start/Pause open (Audio row selected) while the original-healthmeter F6 Audio child owns presentation/input. Closing Audio with F6/Escape/Backspace or controller B/Start restores the original-font Start/Pause menu **without advancing gameplay**; direct F6 from gameplay still returns to gameplay. A seventh fail-closed owner-private SDL patch changes Audio dispatch and preserves `open=true` within the **same SDL event batch**, avoiding transient input leakage on Back. CMake uses seventh overlay, and Linux/Windows CI include C11 menu-stack tests and genuine pinned-source seven-layer Python gate. **Actually run locally, PASS:** exact committed pure C11 source/tests with GCC `-Wall -Wextra -Werror -pedantic` and original-volume level code; exact seventh patcher smoke, Git blobs matched. Native Windows SDL executable, actual seven-stage pinned upstream gate and new Actions results remain unverified. Master gain remains real, Music/SFX saved only, gameplay baseline unchanged; strict 49,504/262144 PRG, VPP27, checkpoint0508/$FB96 unchanged.

## JP0627 — Private whole-ROM assembly reference generated and byte-replay proved

[JP0627 findings](../analysis/0627_COMPLETE_PRIVATE_ASM_REFERENCE.md) add
a complete physically indexed source-reference generator across the
**32 original 8 KiB PRG banks and 16 CHR banks**. The authenticated
393,232-byte original Japanese retail ROM was actually run through
the generator, with entire assembly source **re-parsed byte-for-byte
against the original image**; PASS. Per-bank hash manifest,
address-context-qualified physical-offset TSV and three structurally
identified PRG31 vectors (NMI $E057, Reset $E00B, IRQ $E0F5) are available.
Strict synthetic tests cover all 48 banks, determinism, corruption
rejection, roundtrip and refusing copyrighted output in Git. The
exact committed tool/test Git blobs match the locally executed files;
both Linux/Windows CI gates are wired, execution outcomes unverified.

**Important:** this is complete ROM byte representation, not 100%
classified 6502 code. Unclassified source bytes remain .byte. Already
proven mnemonics should be maintained in 0529/0538 lifting, not
reclassified from all-byte opcode candidate decoding. Semantic strict
PRG 49,504/262144 (18.8843%), VPP 27/100, checkpoint0508 and $FB96
are unchanged; no RESUME_STATE promotion.

## JP0628 — Original 6502 room-selector producer/consumer boundary, R-002 narrowed

[JP0628 original-ROM audit](../analysis/0628_ROOM_SELECTOR_PRODUCER_BOUNDARY.md)
executes actual Japanese 6502 instruction prefixes separately for raw01:$BB57
(indexed writer of RAM $07A0) and raw0A:$B7F7 (five-word room-stream
pointer consumer). Exhaustively tested **256 incoming $30 values and 256
incoming $07A0 values** against the original SHA-authenticated ROM and
independently checked each decoded pointer from physical raw0A bytes.
Only 10 selectors lead to one of the five documented stream roots
(indices 0..4 plus high-bit alias indices 128..132); 26 produce other
addresses inside the expected bank window but without validated stream
records; 220 produce pointers outside that raw-bank window.
Conditional witness: raw01 input $30=$06 can produce $07A0=$35, which
raw0A would interpret as pointer $FF63 if these independent code paths
were connected in that order. **No actual live chain or gameplay crash
proved.** Original ROM and synthetic smoke PASS locally; exact committed
script blob matched locally tested code; Linux/Windows CI gates added.
Fixed $FB96 recovery fingerprint and source-bank hashes preserved.
R-002 remains OPEN; no strict new bytes. Strict 49,504/262144 PRG,
VPP27/100, certified 0508, fixed frontier $FB96 unchanged.

## JP0629 — Nine-cell source boundary and real-Mesen R-002 provenance tooling

[JP0629](../analysis/0629_MESEN_ROOM_SELECTOR_PROVENANCE.md) inspects the authenticated original JP raw-bank01 source around $BB57. The $BB62–$BB6A read table contains nine separately SHA-pinned cells; $BB6B has a plausible original instruction entry and raw01:$B877 has the exact JMP $BB6B bytes. Over hypothetical RAM[$30]=$00–$11 (18 input bytes, accessing only these nine cells), downstream conditional raw0A:$B7F7 address formation yields six documented five-stream roots, four other *unvalidated* addresses within $8000–$BFFF and eight outside the intended switchable-bank0E window. This is NOT a proven live ROM call chain, illegal CPU pointer or game crash. Earlier all-256 tests intentionally read beyond the nine-cell table for large input values, so cannot establish normal gameplay bounds. Owner-only read-only Mesen Lua now records bank-qualified producer entry, all mirrored $07A0 writes, consumer entry/pointer and sequence/cycles. A ROM-authenticated Python parser fails closed on false physical banks, stale pointer results, truncation, savestate timeline resets and invalid chronology. Local original-ROM table audit and equivalent ROM-free parser negative fixture PASS; both CI workflows now smoke-test the committed parser (fresh run results unverified). **No Mesen gameplay capture performed here**; R-002 remains OPEN. Strict PRG 49,504/262144 (18.8843%), VPP27/100, checkpoint0508, frontier $FB96 unchanged.


## JP0630 — Original-Mesen STA/postcondition provenance watchpoints (not yet run in emulator)

[JP0630](../analysis/0630_MESEN_ROOM_CHAIN_POSTCONDITION.md) adds physically mapped raw01:$BB5E pre-STA A and raw0A:$B806 actual RAM $08/$09 pointer postcondition callbacks, mirrored RAM $30/$07A0 writes and NMI/IRQ chronology. A ROM-authenticated parser compares actual postcondition to original bank0A table and fails closed on event loss, wrong physical PRG, RAM continuity, reset or savestate load. **Only synthetic smoke and an owner-ROM-backed synthetic log were tested locally; no authentic Mesen playback trace exists yet.** R-002 OPEN; no semantic bytes or VPP promoted. Strict PRG 49,504/262,144 (18.8843%), VPP 27/100, 0508, fixed $FB96, RESUME_STATE unchanged.


## JP0634 — Raw01 parent selector route bounded conditionally

[JP0634](../analysis/0634_RAW01_SELECTOR_PARENT_CFG.md) authenticates the original raw01 B87A→B919→BAEF→BB57 route and steps all 256 inputs through the actual unsigned B91E clamp. For this no-interrupt route, source $30 is bounded to 00..11 and the nine-cell BB62 table index to 0..8. Other entries, live NMI/IRQ writers and the raw0A consumer connection remain unproven. R-002 OPEN, strict PRG 49,504/262,144, VPP27/100, checkpoint0508 and FB96 unchanged.


## JP0636 — F6 pinned source guard position corrected

[JP0636](../analysis/0636_F6_PREFIX_SOURCE_GATE.md) repairs a source-test false negative: JP0621 formerly searched for an F10 exclusion guard after F6's callback, while the actual JP0620 patch places the guard before that callback. An exact combined guard/callee check and tamper-negative fixtures replace it. Full native integration/Windows playtest still require independent CI and original reference emulator observation. Strict 49,504/262,144, VPP27, 0508, $FB96, R-002 unchanged.


## JP0637 — JP0625 six-stage F4 source gate spelling fix

[JP0637](../analysis/0637_SLOT_PICKER_SOURCE_GATE.md) fixes another source-audit typo: the source gate looked for `if(sc==SDL_SCANCODE_F4)` while authentic JP0623 inserts `if (sc==SDL_SCANCODE_F4) {`. The corrected assertion continues to require F4 before the child slot handling and child Escape before parent Escape, without changing the SDL overlay or game code. Fresh CI required; strict PRG49,504, VPP27, checkpoint0508, $FB96 and R-002 remain unchanged.


## JP0638 — ROM-free host linkage and CP1252 smoke diagnostic fixes

[JP0638](../analysis/0638_TEST_HOST_LINK_AND_CONSOLE.md) fixes two unrelated CI environmental errors exposed after six-layer SDL source verification: the isolated C11 edition fixture now provides an explicitly inert mock of pinned upstream `uint64_t cyc_cycle_count(void)`, and JP0626's smoke confirmation uses CP1252-compatible ASCII rather than a Unicode arrow. Production game modules and pinned SDL patch content remain unchanged. Owner gameplay and full emulator trace verification are still pending. Strict 49,504/262,144, VPP27, certified0508, $FB96 and R-002 OPEN.


## JP0639 — Windows seven-layer source gate log encoding

[JP0639](../analysis/0639_WINDOWS_UTF8_SOURCE_GATE.md) addresses a Windows CP1252 console failure after the actual seven-layer pinned SDL source check had generated and reported success. The JP0626 message now uses ASCII and the Windows GitHub Actions job explicitly requests UTF-8 Python output. These are diagnostic/environment changes, not CPU/gameplay corrections. Strict 49,504 PRG, VPP27, 0508 and FB96 unchanged; independent original Mesen capture and owner Windows playtest remain pending.


## JP0640 — Authenticated raw01 B801/B807 direct callsite boundary

[JP0640](../analysis/0640_RAW01_SELECTOR_DIRECT_CALLS.md) authenticates the full raw01 bank and $B7EF–$B813 window, decodes 14 original instruction boundaries, and identifies physical raw01:$B801 JSR $B87A and raw01:$B807 JSR $B877; the latter reaches JMP $BB6B following the separate $BB62–$BB6A table. A whole-bank literal-JSR census finds one occurrence of each encoding; this does not prove actual game liveness, independent physical mapping across helper calls or absence of indirect alternatives. Owner-ROM local source audit and ROM-free tamper fixtures PASS; R-002 OPEN, strict 49,504/262,144 PRG, VPP27, checkpoint0508, FB96 unchanged.


## JP0641 — Independent scenario replay preflight foundation (no execution)

[JP0641](../analysis/0641_SCENARIO_PREFLIGHT_CONTRACT.md) adds a strict versioned scenario manifest, SHA-pinned deterministic native input schedule, owner-only retail-ROM/executable identity preflight, and explicit PASS/FAIL/NOT_EXERCISED per phase. A ROM-free sample and synthetic tamper/negative tests are wired into separate Windows/Linux CI, leaving the recovered seven-layer SDL integration unchanged. The included sample is an input-probe contract, **not** a verified title-to-village route. No original Mesen or native gameplay was executed in this phase; replay/frame/CPU/render parity remain NOT_EXERCISED. Strict PRG 49,504/262,144 (18.8843%), VPP 27/100, certified 0508, fixed $FB96, R-002 OPEN.


## JP0642 — Pinned original-Mesen/native independent replay adapter

[JP0642](../analysis/0642_INDEPENDENT_REPLAY_ADAPTER.md) implements owner-local independent Mesen-agent and native C11 bounded frame execution from the exact JP0641 scenario file, translating verified frame-change controller input into Mesen's inclusive intervals and requiring SHA pins for the original JP ROM, both executables, and MesenCore. It validates actual reference NES JSONL summary/state/final PNG and native JP0578 frame-hash/PNG output without sharing savestates. Synthetic mocked-process and negative-fixture tests PASS locally; genuine original Mesen/native retail gameplay and inter-engine parity were NOT EXERCISED. Strict PRG49,504/262,144, VPP27/100, 0508, $FB96, R-002 OPEN.


## JP0644 — Enhanced F4/Save/Load failure transaction and actual seventh-shell test

[JP0644](../analysis/0644_ENHANCED_MODAL_TRANSACTION_AND_SDL_HARNESS.md) corrects a real host-menu transaction bug: failed quick-state Save/Load previously changed the selected host quick-slot and dismissed its selection child despite an I/O failure. The JP0625 generated SDL helper now restores the old slot and reopens the attempted child for retry/cancel; the original pinned native whole-machine state file format and host error notifications remain unchanged. The ROM-free JP0625 generated shell tests cover failed save/load, retry, old-slot preservation and cancel. New [seventh-layer fixture](../tools/jp_menu_roundtrip_shell_test_0644.py) applies the actual JP0623→0625→0626 C source transformations and links real game-owned action/slot/audio-level/audio-modal/modal-stack C modules, executing F4, failure/retry, Audio parent focus, F4 refusal while Audio owns input, game-input release, standalone F6 and two-accept Quit under offline/netplay flags. Windows Alpha builder [38836167641](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/38836167641) and Linux Mapper24 NESRecomp [38836167331](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/38836167331) **SUCCESS** including complete synthetic-media C11 SDL compilation. A new [owner Windows acceptance checklist](../release/alpha/QA_ENHANCED_MENUS_0644.md) remains outstanding: synthetic C and CI builds are not private original-JP live GUI/save-file tests. Modding is **deferred until after the Enhanced Edition ships**; graphics issue #1 remains owner-resolved. Strict PRG 49,504/262,144 (18.8843%), VPP27/100, semantic checkpoint 0508, frontier $FB96, R-002 OPEN.


## JP0645 — Original PRG26-proven logical sprite animation identity (Enhanced optional only)

[JP0645](../analysis/0645_STABLE_SPRITE_EMISSION_ANIMATION.md) hardens existing opt-in `-StableSprites` temporal sprite rendering without touching CPU/PPU/APU/gameplay or default/native Original output. Original JP PRG26 bytecode at physical file offsets 0x34019 (`LDA $22; CLC; ADC #$44; STA $22`) and 0x34051 (`TXA; CLC; ADC #$C4; TAX`) was **locally verified against the exact original-JP ROM hash**, and a ROM-free gate checks these motifs and all 4,096 logical/physical OAM permutation inverses. The new compositor first performs one-to-one **stable emission-identity** matching, tolerating normal sprite tile and flip animations despite original rotating OAM slots; a one-to-one spatial/tile fallback remains for unknown/non-word-aligned phases. No ghost survives beyond the historical one-frame cap; scene-collapse, priority, background masks and reset remain intact. New strict C11 synthetic tests include 64 simultaneous animated sprite pieces, phase wrap, duplicate lookalikes and invalid-phase fallback. [Linux NESRecomp integration](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/38838450730) and [Windows SDL2 Alpha build](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/38838450762) **SUCCESS**, including previous JP0608 tests and new JP0645 production-code tests; Windows/Linux ROM-free original-byte gate now added. Real retail-game private Windows sprite A/B and frame-perfect pixel parity were NOT EXERCISED. Issue #1 stays owner-resolved/closed. Modding deferred until Enhanced release. Strict PRG49,504/262,144 (18.8843%), VPP27/100, checkpoint0508, fixed frontier $FB96, R-002 OPEN.


## JP0646 — Read-only native PRG0C sound dispatch decision observability (Enhanced audio)

[JP0646](../analysis/0646_ORIGINAL_SOUND_TERMINAL_OBSERVER.md) adds the owner-opt-in `--sound-decision-trace` and a second private pinned NESRecomp `hw_machine.c` opcode overlay. Unlike JP0612's $E249 ingress-only requests, native execution now **can log** original mapper24 bank0C:$8852 entry plus $885D intermediate reset, and the five JP0617 terminal outcomes at $884F, $8860, $8922 and $8928 with read-only original RAM $EF, $0109, $019E and $06DD snapshots. The single original read helper remains patched for interpreted and compiled fetch paths, guards mapper24/non-interrupted opcode fetches and original wrapper RAM markers. Open/close/epoch boundaries, 100k-row limit, malformed opcode/decision/ordering flags, original hardware state and existing PCM mixer are protected; no audio modification or guessed music-vs-effect attribution. All five source-derived terminal classes and negatives pass ROM-free native C11 tests. Both [Linux Mapper24 integration](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/38842000015) and [Windows Alpha SDL2 builder](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/38841999987) **SUCCESS** at checkpoint 7518a0b6, including Windows Release-enabled test assertions. Real authentic-JP gameplay decision capture, independent Mesen comparison and separate Music/SFX virtual voices are **NOT EXERCISED**. R-007 remains OPEN, as do original sound request ownership and functioning independent Music/SFX sliders. Default Japanese game and Enhanced playback unchanged; modding deferred. Strict PRG 49,504/262,144 (18.8843%), VPP27/100, checkpoint0508, frontier $FB96, R-002 OPEN.


## JP0647 — Dormant independent 8+24 Music/SFX PCM renderer and deterministic synthetic scene

[JP0647](../analysis/0647_INDEPENDENT_VIRTUAL_AUDIO_BUS.md) implements a production, host-only PCM mixing component with independent 8-music and 24-effect voice pools, callback sources, no channel stealing, ID-stable reset, bounded render calls, 0–100 Music/SFX/Master levels and final signed-16 clipping. It is linked into the Enhanced edition host and automatically cleared on power-on/state load, but remains **dormant**: no decoder for original Japanese song or effect programs exists, no authentic music/effect voices are injected, and the real game audio callback continues using its existing 2A03/VRC6 output and working Master gain. In particular, the saved Music/SFX sliders do **NOT** yet control authentic gameplay audio. The source callback is synchronous and requires future thread synchronization when connecting actual game events to SDL.

Independent ROM-free C11 tests execute production voice allocation, tails, source progression during mute, 8+24 admission, no stealing, voice token overflow, reset, gain and overflow rejection, plus a deterministic synthetic 10,000-sample two-song/three-effect scene with identical output using 2000-, 257- and 1-sample callback blocks. Both [Windows Alpha 38847041444](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/38847041444) and [Linux NESRecomp 38847041479](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/38847041479) **SUCCESS** on implementation commit 670bea53. No copyrighted ROM or game-derived audio was committed. Real retail-JP sound program decoding, actual Mesen/native sound ownership match and owner real-game playback acceptance are still **NOT EXERCISED** (R-007 OPEN). No promotion of original source coverage: strict PRG 49,504/262,144 (18.8843%), VPP27/100, checkpoint0508, fixed frontier $FB96, R-002 OPEN. Modding deferred and owner-fixed graphics issue #1 closed.


## JP0648 — Source-authenticated original 15-entry DMC command path

[JP0648](../analysis/0648_AUTHENTIC_DMC_SOUND_PROGRAMS.md) joins the original SHA-256-authenticated Japanese PRG0C indexed sound metadata ($8F60..$9540), 15 sound IDs $6F..$7D linked to original DMC 60-byte program source ($A957..$A992), and the original high-command priority/write routine ($8908..$8953). The new owner-ROM-private Python verifier authenticates the physical metadata, DMC table and opcode window checksums and the 15 pointers without committing any ROM-derived sound bytes. A production C11 **pure read-only** event planner turns one bounded DMC command/old-priority state and caller-authenticated 60 original DMC parameter bytes into an accepted/denied plan, an original $06DD counter-increment bit (indices >=$0D even if denied), updated $019E priority and six original-order abstract APU writes ($4015=$0F, $4010..$4013, $4015=$1F). Commands below $6F or after $7D are **rejected as unverified**: beyond 15 known entries the original table indexing reaches unrelated source bytes/code. No packet executes writes or authentic DPCM waveform synthesis; game PCM and Music/SFX sliders remain unchanged, and JP0647's 8+24 voice mixer remains dormant. Strict C11 Windows Release/Linux tests cover **3,840 = 15 × 256** DMC guard inputs, exact packet order, malformed inputs and out-of-table refusal; ROM-free Python --smoke checks the same domain. The owner-uploaded genuine Japanese ROM's original source windows, record references and fingerprints were also independently checked locally. [Windows SDL2 Alpha CI](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/38848854199) **SUCCESS** and [Linux Mapper24 integration](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/38848854194) **SUCCESS** at implementation commit 1dccdecd. No genuine gameplay DMC execution/parity, DPCM sample bank mapping or independent Mesen comparison was exercised; R-007 OPEN. Owner-confirmed graphics issue #1 stays closed; modding remains deferred until Enhanced completion. Strict semantic PRG 49,504/262,144 (18.8843%), VPP27/100, checkpoint0508, frontier $FB96, R-002 OPEN.


## JP0649 — Authenticated DPCM sample geometry and dormant raw 7-bit decoder

[JP0649](../analysis/0649_DPCM_MEMORY_AND_TIMING.md) extends the verified 15 original Japanese DMC programs (JP0648) into source-authenticated sample geometry: the real SHA-256-pinned JP cartridge's 15 descriptor entries resolve to **8 unique CPU sample spans, all within switchable VRC6 $C000-$DFFF**, earliest start $C000 and latest end $DFC0; **two** variants set loop and none set DMC IRQ. A caller-supplied **observed** VRC6 $C000 bank8 (0..31) yields physical PRG offset, and out-of-window/cross-bank sample spans fail closed. No live original mapper bank is asserted: the static record does not establish the bank register during actual DMA.

New production C11 helper cviii_dpcm_decode_0649.h/.c parses only successful JP0648 register plans, checks original six-write sequence, computes NTSC/PAL raw-bit period metadata and emits **one-pass LSB-first seven-bit DAC delta levels** into caller-owned output with ±2 saturation and strict PRG/output bounds. This is **not a real-time 2A03 DMC simulation or working Japanese game sound**: no DMC sample-buffer/CPU DMA phase, IRQ/loop repetition, PCM resampling, interrupt arbitration, live mapper changes, or effect producer is supplied. JP0647 8+24 virtual Music/SFX mixer remains dormant and original 2A03/VRC6 PCM stays untouched. The owner-only ROM audit delegates actual source/pointer/driver fingerprints to JP0648; no copyrighted ROM/sample bytes are committed.

Strict production-backed C11 tests exercise 15×256 input guards, all 32 hypothetical physical PRG bank values for accepted commands, both DMC region rate tables, raw delta bit order, clamping, $DFFF window-crossing refusal and no output mutation on invalid input; ROM-free Python source/geometry negative cases pass. The authenticated owner-JP ROM audit passed locally. [Windows SDL2 Alpha run 38850407597](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/38850407597) **SUCCESS** and [Linux Mapper24 run 38850407592](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/38850407592) **SUCCESS** at implementation commit 088f6366. Real original-JP gameplay DMA/bank trace and independent-Mesen waveform parity **NOT EXERCISED**, R-007 OPEN. No new semantic PRG/VPP credit: strict 49,504/262,144 (18.8843%), VPP27/100, checkpoint0508, fixed $FB96, R-002 OPEN. Graphics issue #1 closed after owner resolution; all modding deferred until Enhanced release.


## JP0650 — Read-only native mapper24 DMC DMA-get source-bank instrumentation

[JP0650](../analysis/0650_DMC_DMA_FETCH_AND_MAPPER_TRACE.md) adds owner-opt-in --dmc-dma-trace to the pinned NESRecomp mapper24 runner. It observes each **actual DMC sample DMA get** (not speculative requests/dummy cycles) with the physical mapper PRG slot captured BEFORE the game's existing bus read, the actual returned byte, original CPU cycle and bytes remaining. It also records VRC6 $C000–$CFFF mapper bank-write INTENTS (not yet installed-bank proof) and power-on/state-load trace epochs. No extra bus read, original audio/CPU/mapper modification, game savestate schema change, or original copyrighted bytes in the repository. A 200,000-row cap emits trace_limit, rejected by the strict CSV verifier.

Independent ROM-free C11 tests exercise real source offset mapping, mapper bank-write intentions, source reads in C000/D000 and fixed E000, reset/load epochs, malformed offsets, cycle reversal, and overflow-marker validity in Windows Release and Linux. The private CSV verifier checks authenticated owner-JP ROM data, exact mapper24 physical slot offsets and reported bytes; it flags discrepancies, malformed events and truncated captures. Pinned APU/VRC6 private source-patch checks and full [Windows SDL2 Alpha](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/38851826980) and [Linux Mapper24 NESRecomp](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/38851827004) builds **SUCCESS** on implementation commit 374c0477.

Evidence boundary: native actual-hardware-read hook is built and synthetically tested; **real owner original-JP native gameplay capture, observed actual game bank values, independent original Mesen DMC DMA comparison, matched input and full Music/SFX separation are NOT VERIFIED**. JP0649 raw DPCM and JP0647 virtual mixer remain dormant. No live audio changes or modding; graphics issue #1 stays owner-resolved and closed. Strict semantic PRG 49,504/262,144 (18.8843%), VPP27/100, checkpoint0508, fixed $FB96, R-002/R-007 OPEN.


## JP0651 — Independent MesenCE DMC-only reference-source adapter and fail-closed native pairing

[JP0651](../analysis/0651_INDEPENDENT_MESEN_DMC_DMA_REFERENCE.md) introduces a source-pinned read-only observer for independent **MesenCE** CPU's true DMC DMA get branch, not a generic memory-read callback. The protected upstream source is MesenCE commit 4b8a196e299b3de297b204fd1208d2981562c89b, `Core/NES/NesCpu.cpp` Git blob d411c11981f16011bd8a19f7cc0b2a69cae1a019. The optional private source generator inserts a hook **after** the existing DMC-only `ProcessDmaRead` and reads the actual mapper absolute PRG offset, CPU address, cycle and returned sample byte without rereading memory, changing APU/DMA registers, replacing PCM, changing original CVIII ROM or shipping modified MesenCE code. Output is activated only through a private `CVIII_MESEN_DMC_TRACE` environment path. A 200k-row cap inserts a terminal `trace_limit` that always invalidates evidence.

`jp_mesen_dmc_dma_compare_0651.py` revalidates original SHA-256-authenticated Japanese ROM and the existing JP0650 native CSV, then requires one reset epoch, at least two true DMA samples in each source, one-to-one event counts and order, identical CPU addresses, physical PRG byte offsets and ROM-read values, and *exactly matching relative inter-fetch CPU cycle gaps*. The global cycle offset is **reported** rather than being concealed. It refuses missing, extra or reordered events, malformed or truncated captures, inconsistent ROM bytes, unmapped banks, native mapper request contradictions and CPU cycle drift. Its metadata-only JSON does **not** contain actual private sample bytes. A matching input pair would be structural evidence, **not an automatically authenticated MesenCE build or original-game input replay**; the owner must record original Japanese game execution independently with matched region and controller inputs. No such real Mesen/native trace was available here and **real-game parity is NOT certified**.

Both [Windows Alpha builder 38854153989](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/38854153989) and [Linux NESRecomp Mapper24 38854153973](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/38854153973) **SUCCESS** at implementation commit d73c5067, including the production suite and JP0651 ROM-free source-patch/comparison negatives. CI does NOT compile or execute MesenCE; owner-private pinned MesenCE compilation and live comparison remain future steps. Original hardware audio and JP0647 virtual Music/SFX mixer remain unchanged/dormant, R-007 OPEN, modding deferred. Strict PRG 49,504/262,144 (18.8843%), VPP27/100, checkpoint0508, fixed $FB96 and R-002 OPEN unchanged. Issue #1 remains owner-resolved closed.

## JP0652 — Original 125-program sound directory, complete structural index

[JP0652](../analysis/0652_COMPLETE_ORIGINAL_SOUND_DIRECTORY.md) provides a read-only, source-authenticated, physical-bank-qualified catalog of **all 125 original Japanese indexed sound-program descriptors** at raw PRG0C:$8F60–$9540. Of those, 110 descriptors contain **325 triplet source references** (139 raw0C, 102 raw04, 84 raw05) and 15 are the indexed special DMC records for command IDs $6F–$7D, linking exactly to PRG0C:$A957–$A992. The entire 1,505-byte directory and 3,523-byte source-addressed sound pool are separately SHA-pinned. Descriptor pointer order, full non-overlapping record coverage, bank-qualified CPU-to-physical mapping and DMC target order are checked against the owner's authenticated ROM; ROM-free invented directory and corruption guards run in Windows and Linux CI.

The catalog is **source metadata only**. Modes are opaque; no music/effect classification, phrase interpretation, live mapper state, hardware timing, source PCM, or game-owned voices are fabricated. Owner-generated JSON can contain reconstructible original directory metadata and stays private; no ROM or generated JSON is committed. Existing native audio, user-visible Music/SFX independence and JP0647 dormant virtual voices are unchanged. No actual original-Mesen/native replay is claimed; R-007 remains open. Strict PRG **49,504/262,144 (18.8843%)**, VPP **27/100**, certified checkpoint **0508**, frontier **$FB96**, R-002 open: **zero new certified bytes**.

## JP0653 — Source-authenticated original-6502 phrase lookup and dormant native parity

[JP0653](../analysis/0653_ORIGINAL_SOUND_PHRASE_POINTER_NATIVE.md) authenticates the two different original raw0C phrase lookup opcode windows at CPU $8B2C–$8B3A and $8D07–$8D14, both 8-bit `ASL; TAY` selectors that return an indirect pointer in ZP $E2/$E3. The first reads indexed RAM $01B7,X into the 128-entry $A304 table; the second reads ZP $06 into the separate 20-entry $A404 table. Both have exact 8-bit high-bit aliases; the second consumer's other 108 selector indices read physically adjacent phrase bytes and are **not** certified table entries. Entire source region $A304–$A956 is SHA-pinned: 148 pointers, 140 unique roots, and 1,323 fully accounted structural phrase bytes. The last source interval contains two $FF bytes ($A94F and $A956), which are preserved without inventing one continuous executable phrase.

A pure dormant C11 source resolver preserves original A/Y, Z/N, CPU read address, little-endian source word and fail-closed structural pointer membership. A separately opcode-stepping original-NMOS 6502 reference and native compiled resolver matched **3,072/3,072** original-JP ROM-backed bounded cases (both routines, all 256 byte selectors, six initial X seeds); artificial Python and C11 source/negative tests pass. The source module is compiled into the Enhanced host but has no live playback call site. No music/sound effect assignment, phrase interpreter, real game selector provenance, mapper-state observation or full audio parity is proved. R-007 open; R-002 open; no commercial ROM-derived data committed, no new strict PRG credit: **49,504/262,144 (18.8843%)**, VPP **27/100**, checkpoint **0508**, fixed frontier **$FB96**.

## JP0654 — NSF1 original-ROM provenance, 13 complete physical source-bank comparisons

[JP0654](../analysis/0654_ORIGINAL_JP_NSF_ROM_CROSSWALK.md) verifies the owner-supplied Japanese Zophar NSF ZIP against the authenticated original Mapper24 cartridge, under the [NESdev NSF specification](https://www.nesdev.org/wiki/NSF). The 28-song 53,376-byte NSF is a *modified audio rip*, not an original-ROM emulator trace: its 13 physical 4KiB payload segments map exactly to original PRG 4KiB blocks [16..23,48..50,14..15], with **11 full exact 4KiB banks**. Precisely 52,464 of 53,248 payload bytes lie outside two rip replacement windows and match retail bytes; 775 bytes actually differ. Raw0C CPU $A000–$A2FF replaces 768 original source-pool bytes (759 changed), and raw03 CPU $BFF0–$BFFF replaces 16/16 bytes. The rip's virtual $5FF8–$5FFF NSF bank registers and INIT $E0E0/PLAY $E0D0 are **not** original VRC6 mapper history or retail source entry points.

The sound directory $8F60–$9540, full JP0653 $A304–$A956 phrase table/pool and all 60 JP0648 $A957–$A992 DMC parameter bytes are byte-exact in both ROM and NSF. Original bank0C $8D15–$8D8F code is likewise source-identical; this **does not** make NSF playback a reference for original-game command timing, original sound IDs, Music/SFX voice ownership, or DMC DMA phases. New read-only Python source crosswalk validates SHA-pinned ROM/NSF/M3U, NSF1 header/bank mode, full bank equality outside strictly bounded rip edits, track indexing and metadata-only output. It reads ZIP members entirely in memory and has ROM-free synthetic/negative CI. Original gameplay/audio code unchanged; no commercial ROM, rip or sample data committed. Strict semantic PRG **49,504/262,144 (18.8843%)**, VPP **27/100**, certified checkpoint **0508**, fixed frontier **$FB96**, R-002/R-007 OPEN; no new bytes credited.

## JP0655 — Raw0C ordinary sound phrase arithmetic, complete bounded source replay

[JP0655](../analysis/0655_ORIGINAL_PHRASE_ARITHMETIC_NATIVE.md) reconstructs the actual authenticated original Japanese VRC6 physical raw0C original 6502 instruction path $8D15–$8D8F (**123 opcode and operand bytes**) through four connected subroutines. It lifts the $06AA,X cursor, ($E2),Y original byte fetch, high-nibble state at $03F2,X, 8-bit low-nibble sign and repeated-add scale at $03F7,X, restoration of X from $EE, and original $01AD,X/$01B2,X → $EC/$ED 16-bit carry/borrow result into portable pure C11. The original **factor-zero loop executes 256 iterations** rather than skipping the update; C11 preserves the modulo-256 result. Original 6502 A/X/Y and **C/Z/N/V**, individual original result bytes and the allowed RAM write footprint match native output. The entire earlier JP0653 1,323-byte phrase pool is accounted: 1,122 bytes <$FB are replayable as conditional ordinary-byte sources, while 201 $FB/$FE/$FF-valued source bytes are deliberately NOT interpreted as ordinary music commands.

The private-ROM actual-opcode 6502 runner matches **5,610/5,610** bounded native scenarios (1,122 original source byte positions × five synthetic RAM seeds), including all 1,122 factor-zero cases, with no first divergence; it SHA-pins the ROM, raw bank, four exact helper regions and phrase pool. ROM-free synthetic tests run 385,536 native C11 cases (251 byte values × 256 multiplier factors × six 16-bit edge seeds) and 4,096 Python arithmetic cases; GCC/Clang C11 and Clang ASan/UBSan passed locally. A new standalone CMake test and Windows/Linux workflow gates compile and exercise the dormant native module. **No game-audio output, DMA/mapper timing, savestate, input or gameplay was changed.** $FB–$FF original opcode branch at $8D90, natural source-to-consumer provenance, music/effect sound ownership and original Mesen/native full gameplay parity remain unproven, R-007 and R-002 open. Strict new semantic PRG bytes **0**, certified total **49,504/262,144 (18.8843%)**, VPP **27/100**, checkpoint **0508**, fixed frontier **$FB96** unchanged.

## JP0656 — Complete original phrase control grammar, score-backed first audio-format point

[JP0656](../analysis/0656_ORIGINAL_SOUND_CONTROL_COMPLETE.md) completes the original Japanese raw PRG0C sound phrase **one-byte control format** by original opcode-proof of $8D15–$8D1F and the whole $8D90–$8DCC 61-byte control handler. $00–$FA follows the JP0655 verified nibble arithmetic; $FB–$FD increment and save the per-channel cursor; $FE uses an 8-bit wrapped repeat parameter and counter to either rewind or clear-and-skip; $FF sets $03F2,X=$FF and returns. Both original conditional exits at $8D06 and $8DCC are explicitly bounded. All 201 control-valued byte positions in the complete original 1,323-byte phrase pool were read by original 6502 instructions in **1,827/1,827 owner-ROM-backed** compiled-C11 comparisons, with all A/X/Y, C/Z/N/V, exact RAM field results, writes and branch destinations matching. Original $FB=30, $FE=30, $FF=141; $FC/$FD are code-domain possibilities tested with 42 privately synthetic data mutations, not observed retail usage. ROM-free C11 executes **327,680** complete-token/cursor/counter cases with corruption rejection; GCC, Clang and sanitizers passed locally. Native source stays **dormant**; no audio playback path, UI or game logic changes.

The existing fully source-indexed **125-program/325-reference** sound directory (JP0652), **148-pointer/140-root** secondary phrase format (JP0653), ordinary data grammar (JP0655) and this now **complete $FB–$FF source-control grammar** earn **one fixed Audio music/SFX data-formats subpoint** under the two-point format rubric. Second format point, stream modes raw04/05, live music/SFX ownership, original Mesen/native frame parity and R-007 remain OPEN. **VPP advances 27 → 28/100 (Audio 1 → 2/12)**. Strict original gameplay/Mesen-certified PRG remains **49,504/262,144 (18.8843%)**, certified checkpoint **0508**, fixed frontier **$FB96**, R-002 open: no new independent Mesen liveness, no strict bytes promoted.

## JP0657 — Original stage/room data format and coordinate-native parity

[JP0657 implementation](../analysis/0657_STAGE_ROOM_NATIVE_CATALOG_AND_COORDINATE.md) adds two reusable dormant C11 source modules for the authentic original Japanese Mapper24 **raw0A stage/world system**. The complete room-data hierarchy is validated from original physical bank bytes: 15 stage groups, 64 second-level tables, 135 original 6502 leaf selectors, 129 distinct roots, 709 four-byte cells and 163 seven-byte records (16 FF terminators). An independent original-ROM instruction-fetched 6502 reference reproduces all **135/135** native source intervals. Connected original source at $8001–$801D and $80D1–$8107 is translated as room-coordinate/phase arithmetic; its original 6502 and native C11 outputs match **131,072/131,072** input combinations including all A/X/Y/C/Z/N/V flags. C11 full-hierarchy artificial bank tests and coordinate regression, GCC/Clang sanitizers passed.

[Formal JP0657 VPP decision](../analysis/0657_FORMAL_VPP_STAGE_FORMAT_DECISION.md): first of five original stage/room data-format rubric points is earned, **Stage 0→1/20 and VPP 28→29/100**. The 4,421 stage source bytes were already structurally represented in JP0538 and the newly translated 84 coordinate bytes were previously accounted there: **strict PRG unchanged 49,504/262,144 (18.8843%)**, semantic checkpoint 0508 and fixed $FB96 frontier preserved. No natural Mesen stage producer, frame rendering, scrolling, stage editor, or PPU/native parity is claimed; native code is linked but has no gameplay call site, R-002 OPEN.

## JP0658 — Original stage room-state-zero RAM and two-nametable PPU clear, native C11

[JP0658](../analysis/0658_ORIGINAL_ROOM_ZERO_PPU_NATIVE.md) reconstructs the entire connected **original Japanese raw0A:$B570–$B58B → fixed PRG31 $E2C4/$E616/$E7B6/$EB82/$E16C/$E827/$ED89 → raw0A:$B589 state-1 return**. The source-backed native C11 room-state transaction copies 2KiB RAM, applies **1,297 exactly bounded RAM zero writes**, preserves and restores original $0781, advances $19 from $00 to $01, records mapper $C000=$1E and $B003=$20 writes, and reconstructs the **complete ordered 2,048 PPUDATA $2007 writes** from the original $EC1D–$EC46 fixed-bank command stream, including $7F second nametable selection and PPUCTRL 1/32-byte VRAM increment. Actual original ROM code/data regions (273 instruction/operand bytes across eight linked disjoint routines + 42 stream bytes) are individually SHA pinned.

**512/512** source-original-opcode versus compiled C11 full room-initialization cases passed locally: **5,392,384 original 6502 instructions**, **917,504 non-stack RAM-byte comparisons** and **1,048,576 ordered PPU events**, both $2000 increment modes and 2 external register events per scenario. A separate isolated fixed-bank PPU replay passed 256 cases; a ROM-free C11 test runs 512 invented-stream cases plus bad-source/error cases, GCC/Clang/ASan/UBSan passed. The source byte windows were already in 0508 Phase 8/9. **No newly certified strict PRG bytes and no VPP point**: 49,504/262,144 (18.8843%), VPP **29/100**, semantic checkpoint **0508**, fixed frontier **$FB96**, R-001/R-002 OPEN. Native output remains a **dormant read-only event/postcondition plan**, not live gameplay or PPU pixel/cycle parity.

## JP0659 — Five authentic room-object streams installed natively; structured extractor

[JP0659 full source and independent native replay](../analysis/0659_ORIGINAL_BANKED_ROOM_OBJECTS_AND_STAGE_EXTRACTOR.md) connects original raw0A:$B7F7–$B872 **124 physically mapped original 6502 code bytes** to fixed PRG31:$FB96–$FBA4 source reads and raw0E's **175 contiguous source bytes at $BE8B–$BF39**. The five selector roots (source $07A0 values 0..4, **not globally proved live**) contain 20 header bytes, 30 five-byte records and five FF terminators. The native C11 importer maps each record's five positional bytes to real $048C/$0400/$0438/$041C/$04A8 indexed RAM fields, installs enabled $054E slots, and preserves two actual $8000 mapper bank transitions per source-byte read.

**1,280/1,280 original-retail 6502 opcode vs compiled native C11 cases PASS**, representing **879,360 actual opcode steps, 2,293,760 nonstack RAM bytes, 47,360 bank-qualified resource reads, 94,720 ordered mapper writes** and authentic 8-bit A/X/Y/status outcomes. Another 1,280 ROM-free synthetic C11 cases and altered-source/fail-closed tests pass. [Versioned stage-resource JSON tool](../tools/jp_room_resources_0659.py) exports **five streams/30 records with stable source IDs**, validates edits and repacks an unmodified original export to **175/175 identical bytes** privately; seven malformed-input classes rejected without committing original ROM data.

[Formal VPP decision](../analysis/0659_FORMAL_VPP_STAGE_FORMAT_AND_EXTRACTION_DECISION.md) earns **one distinct raw0E five-byte stage data-format point** and **one reversible stage-data extraction-tool point**: Stage/world **1 → 3/20**, total **VPP 29 → 31/100**. This conditionally reconstructed unit covers **299 physical source bytes** (124 code + 175 typed data) with source-level semantic evidence, but **new strict PRG certification is ZERO**: 49,504/262,144 (18.8843%), semantic checkpoint 0508, fixed PRG31 frontier $FB96. $07A0 producer domain, full room-loader entry, natural emulator gameplay, PPU/frame parity and native playable integration remain OPEN. The native code is compiled but dormant.

