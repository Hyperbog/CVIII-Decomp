# Decompilation progress ledger

## Current dashboard

```text
whole JP PRG scanned/indexed                 262144 / 262144 = 100%
strict semantically verified PRG floor        49504 / 262144 = 18.8843%
exact unique JP<->US correspondence           115865 / 262144 = 44.1990%
exact-or-normalized structural candidates     149607 / 262144 = 57.0705%
VPP                                             26 / 100
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
