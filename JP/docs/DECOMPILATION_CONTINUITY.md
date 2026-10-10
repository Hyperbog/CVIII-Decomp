# Akumajou Densetsu decomp/recomp continuity playbook

Durable handoff for `Hyperbog/CVIII-Decomp`, branch `decompilation`.

## Recovery

After interruption:

1. read `docs/INTERRUPTION_RECOVERY.md`, `docs/ACCELERATION_POLICY.md`, `docs/WHOLE_PRG_ATLAS.md`;
2. read `analysis/RESUME_STATE.json` and `docs/PROGRESS.md`;
3. inspect the live branch for commits newer than the state transaction;
4. run `python tools/check_resume_frontier.py <JP ROM>`;
5. run the audit named by `previous_checkpoint_audit`;
6. continue only after both pass.

Authority: JP ROM / observed JP execution -> reproducible JP-ROM audits -> NES/VRC6 hardware docs -> atlas, JP<->US matching and external disassemblies as accelerators. Never commit ROM-equivalent lossless dumps.

JP SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.
US comparison SHA-256 `1c7b2ed2c1fb5839a6764006aa476f5c9d48f99465b6141980f3a5af1dfec0d6`.

## Dashboard

```text
whole JP PRG scanned/indexed                 262144 / 262144 = 100%
strict semantically verified PRG floor        49504 / 262144 = 18.8843%
exact unique JP<->US correspondence           115865 / 262144 = 44.1990%
exact-or-normalized structural candidates     149607 / 262144 = 57.0705%
VPP                                             26 / 100
```

The newest VPP point is the native C++20 reproducible build/CI regression gate (eight suites compile, four ROM-free suites run; run 37993214808 green); before it, the raw-bank `$0B` collision scratch/distance architecture with native exact-8-bit collision test earned the previous point. Cross-version and dispatch-atlas percentages remain candidate structural coverage only.

## Semantic chain through 0502

```text
IRQ + fixed NMI + ED46                    -> $10-clean on admitted graphs
raw bank $0C                              -> $10-clean on live admitted graph
raw bank $04 parser + 96/96 roots         -> $10-clean
raw bank $05 parser + 72/72 roots         -> $10-clean
$E7FB / 04FF / 0500 fixed graphs          -> locally $10-clean
0501 fixed scheduler                      -> locally $10-clean
0501 raw bank $09                         -> locally $10-clean
0501 raw bank $0A                         -> locally $10-clean
0501/0502 raw bank $0B object/collision   -> WRITES $10 as collision scratch
PRG26 renderer                            -> consumes/persists inherited $10
```

0501 evidence: `analysis/NMI_FIXED_SCHEDULER_BANKED_0501.md`, `tools/audit_nmi_fixed_scheduler_banked.py`.

0501 result:

```text
fixed PRG31                    161 starts    298 new bytes
raw bank $09                   479 starts   1050 new bytes
raw bank $0A                    57 starts    120 new bytes
raw bank $0B                  1338 starts   2896 new bytes
----------------------------------------------------------
0501                           2035 starts   4364 new bytes
```

Tagged manifest SHA `639e20f7e96e816a40ef4ef7d8585c809ce670ac5384f3c2fabc9a77d275737e`.

Scheduler-proven bank roots:

```text
raw $0B: $80E3 $B1F8 $BD11 $8001 $8161 $826C
raw $09: $8001
raw $0A: $84EA
```

`$FE95` shifts `$0565,X` right six times and dispatches via `$E7FB`; `$FE98-$FE9D` contains exactly three pointers `$FE9E,$FEB1,$FEC6`. Live selector `$03` remains open.

## 0502 collision architecture

Evidence:

```text
analysis/NMI_BANK0B_COLLISION_ZP10_0502.md
tools/audit_nmi_bank0b_collision_zp10.py
src/collision_math.hpp
src/collision_math.cpp
tests/collision_math_test.cpp
```

Verified raw-$0B direct `$10` stores:

```text
$B3B6 $B3D2 $B40E $B460 $B65F $B740 $B76C
```

Fixed `$FDE4` invokes `$B1F8` near the start of each active outer slot `X=$01..$12`; later admitted per-slot bank `$09/$0B/$0A` calls are `$10`-clean. Therefore the renderer-facing value is the last qualifying `$B1F8` scratch write by the latest active slot, or older inherited `$10` if no admitted writer fires.

Within one `$B1F8` invocation the writer-family order is:

```text
$B634/$B64B vertical/proximity
  -> $B339 object/player hitbox
  -> $B3EC weapon/projectile probe
  -> $B447 peer loop, $9B=$14,$15,$16
```

The writer formulas are exact 8-bit wrapped coordinate/probe construction or adjustment. `$B707/$B713/$B71D` and `$80B3/$80C1/$80CB/$80D5` share the same 8-bit absolute-distance idiom.

`$B394-$B395 = 00 05` is locally selected only by `Y=0/1`; these are the only 2 new ROM bytes in 0502. Strict floor is **48,823 bytes = 18.6245%**.

The native collision-math test exhaustively validates all 65,536 input pairs for the absolute-difference primitive.

## Raw-bank `$0B` action-dispatch atlas

Evidence:

```text
analysis/RAW0B_ACTION_DISPATCH_ATLAS.md
tools/extract_raw0b_action_dispatch.py
tools/audit_raw0b_action_dispatch.py
```

Mechanical action mapping:

```text
$00-$7F -> word at $BD67 + 2*action
$80-$FF -> word at $BE67 + 2*(action-$80)
```

The 512 interpreted bytes hash to `eb075c21401906325dc497d6537978590dccf193abc3897d42a4935533800a13`; 256 mechanical slots yield 217 distinct raw-bank targets.

Do **not** count those 512 bytes as strict semantic coverage yet. `$9E` mechanically indexes `$BEA3`, which is also script-pointer data and yields `$BF79`; this proves live action bounds must come from JP producer/script evidence, not table shape.

## Native VRC6 components

Mapper: `analysis/NATIVE_VRC6_MAPPER.md`, `src/vrc6_mapper.*`, `tests/vrc6_mapper_test.cpp`.

IRQ: `analysis/NATIVE_VRC6_IRQ.md`, `src/vrc6_irq.*`, `tests/vrc6_irq_test.cpp`.

The mapper implements target PRG RAM/PRG/CHR/CIRAM mapping. The IRQ source implements `$F000/$F001/$F002`, cycle mode and scanline-mode **114,114,113** CPU-cycle cadence. CPU-side IRQ polling/latency, PPU integration and VRC6 audio remain open.

## Cross-version accelerators

Exact matcher: 115,865 unique exact JP bytes (44.1990%), 821 runs, 73 conflicting overlap bytes excluded.

Normalized matcher: 24,014 unique matches; exact-or-normalized union 149,607 bytes (57.0705%); calibration 13,232/13,232 exact-supported starts agree with zero disagreements.

## Next checkpoint — 0503

Primary: prove the **live JP script/action producer domain** feeding `$BD56/$BD64`, intersect it with the action-dispatch atlas, and bulk-close only the handlers actually justified by JP data/control flow.

Then continue the final `$10/$11` value-domain proof from real object/state predicates.

Also open: `$A15A/$A2CC/$A3A9` raw-$0B `$E7FB` sites; raw-$09 `$E5DA` callees; `$0565>>6` selector `$03`; `$18/$2C/$68` producer closure; `$FAA0-$FAA9`; complete mapper-register inventory; CPU/interrupt trace parity; full native memory/PPU/audio/runtime.

Raw fixed investigation frontier remains `$FB96`; 0501 was noncontiguous from `$FDE4` and mapper-selected callees.

```text
overlap $FB76-$FB95
SHA e4fa5e06e439ca12a84d935eb80224f448276c722399fe76fe0ce60013cc4ee7
fingerprint $FB96-$FBB5
SHA a5437f0f20034ba34d65afeec353d28846a321134061f765814d28eaa3f69157
raw tail $FB96-$FFFF
SHA 0cbfd0aa79f3c7d1db7a756c08c47bfe01cba321900fb8955e77ec8525d38d44
```

Transaction order: analysis -> audit -> exact-ROM run -> progress/continuity -> `RESUME_STATE.json` last -> recovery checker -> branch-head confirmation.


## 0503 completed — AI-script dispatcher native address lift

Source `src/ai_script_dispatch.hpp/.cpp`, integration test `tests/ai_script_dispatch_test.cpp`, exact-JP-ROM audit `tools/audit_raw0b_ai_dispatch_0503.py`, analysis `analysis/RAW0B_AI_DISPATCH_NATIVE_0503.md`.

Script ID $05EF,X selects $BEA3 + uint8(script_id*2) after prechecks; subscript $05C1,X adds uint8(subscript*4) with 16-bit carry to script base; the first 4-byte-record byte selects an action word at $BD67 or $BE67 depending on bit 7. Native code returns mechanical addresses and final A/Y/C/Z/N values but does **not** execute prechecks or write CPU state. Real JP ROM hash for $BD11-$BD66: `fbad027357da9de96af06f073ab22c6251d372af2a5f31a80edb0bf9e60f3e79`.

Action $9E mechanically maps $BEA3 -> $BF79, which is script data. The 256-slot/217-target mechanical atlas cannot prove action liveness. Whole-ROM byte patterns for $05EF writers have been inventoried provisionally (96 STA X, 23 STA Y, 5 STA absolute, 2 STY absolute, 1 ORA X). Verify reachable code/indices and aliases before using this as a producer domain.

**0503 adds zero newly accounted PRG bytes** (the decoder code was admitted in 0501). Floor 48,823 (18.6245%); VPP 24/100. Physical fixed frontier remains $FB96; unclaimed $FAA0-$FAA9 unchanged.

Resume 0504 by running the ROM checker and `audit_raw0b_ai_dispatch_0503.py`, then prove live $05EF,X and $05C1,X producers and script record action bytes. Do not guess mapper state, full-table liveness, ROM data bounds, or CPU side effects.


## Checkpoint 0504: AI-script seed $1B and fixed $FC1F — completed

Evidence:
- `analysis/RAW0B_AI_SCRIPT_SEED_0504.md`
- `tools/audit_ai_script_seed_0504.py`

Prior admitted raw-$0B script producer at $B503 writes ID $1B to $05EF,X and calls $B516 to reset subscript $05C1,X to zero. JP $BED9-$BEDA points to $B03A. Its first three records have actions $0B, $45, $46 and corresponding handler roots $8519, $965D, $96B4. $0B and $45 increment subscript, $46 implements countdown/movement/cleanup.

The handlers use five tables at $968C-$96B3 indexed only through an AND #$07 producer. Action $46 invokes fixed PRG31:$FC1F through bank-$0B:$85F2. The fixed local graph has 185 starts and is mapper-stable, but introduces five direct shared-ZP $10 writers: $FBFC (STA), $FC1F (STA), $FC4F (STA), $FCA0 (STY), $FCF9 (STY). Renderer-facing final-$10 provenance remains open.

Code: raw-$0B 71 starts/169 bytes; fixed31 185 starts/335 bytes. Bounded data: raw-$0B 60, fixed31 $FD4D-$FD58 12 (index reduced modulo $0C). **Total 576 genuinely new bytes**, manifest of 16 tagged noncontiguous ranges SHA `4416db601cba553569d4ccc4aba410a6d843a6da3504dac1d735317ca1106eb4`. Conservative strict PRG floor **49,399 = 18.8442%**, VPP **24/100**.

**Do not mark $FD62,Y data as closed.** Unlike $FD4D,Y, the $FD62,Y index has no complete producer bound; the 0504 audit leaves it explicitly open. Broader script-ID pointer atlas remains structural only: 107 entries (IDs 00-6A), 72 pointer values, 71 distinct candidate starts, 792 four-byte lattice positions in $A4A6-$B105; **NOT 792 live actions/records**. Never promote all table bytes just from shape.

Next checkpoint **0505**: close fixed $FD62,Y index-domain producer if feasible; expand live script-ID/subscript record proofs and connected handler graphs; track the five new fixed $10 writer sites to PRG26 renderer; continue native parity infrastructure.

Physical fixed investigation frontier is **still $FB96**, with $FAA0-$FAA9 unclaimed, and 0504 fixed new intervals only $FBF6-$FC16 / $FC1F-$FD4C plus 12 bytes at $FD4D-$FD58. Keep exact noncontiguous accounting.

Checkpoint transaction: analysis/audit committed, progress/continuity updated before machine resume state. Resume tool `check_resume_frontier.py` must still pass. No ROM material committed.


## 0505 — fixed-$FD62,Y source-domain investigation and native test

Evidence: `analysis/FIXED_TILE_PROBE_0505.md`, `tools/audit_fixed_tile_probe_0505.py`, `src/fixed_tile_probe.hpp`, `tests/fixed_tile_probe_test.cpp`.

The native address/data lift runs the **actual mapped CPU read** at $FD62 + Y, followed by OR with $13 >> 5, iterative modulo-12 reduction, bounded $FD4D table read and ADC $11. The $FD62,Y source is **NOT proven within 12 bytes**; Y may come from either ($54+carry)&FF or ($54+$14+carry)&FF and whole-program values of $54/$14 are not yet closed. Without a live domain, overapproximate 256 possible CPU addresses FD62-FE61; reads may overlap executable bytes. No host clamp permitted. Tests pass 524,288 input combinations with JP fixed PRG31 ROM; not a full execution trace.

The ROM-locked audit also records **156 provisional raw JSR byte-pattern candidates** to fixed $FB96/$FBA5/$FC17/$FC1F/$FCDE, and 37 provisional immediate script-ID stores to $05EF,X. Their physical code/data and bank contexts are not automatically proven. In particular $FC17-$FC1E remains 8 **unclaimed** bytes despite six plausible JSR patterns.

0505 has **zero newly admitted ROM bytes** because all lifted $FD11-$FD2B mechanics were already audited in 0504. Strict verified PRG stays **49,399 = 18.8442%**, VPP **24/100**. Fixed raw frontier **FB96**, with six unclaimed gaps unchanged.

For 0506: independently replay ROM checker and `audit_fixed_tile_probe_0505.py`. Establish live $54/$14 producer domains and mapper-backed JSR callers before claiming FD62 indexed data or $FC17 code. Expand JP-proven $05EF and $05C1 values for real script record/handler closure. Consult original MOS CPU manual, NESDoc and EveryNES for flags/memory/PPU timing; JP ROM remains authority.


## Checkpoint 0506 completed — $FB96 mapper transaction and AI candidate atlas

Evidence: `analysis/CROSSBANK_AI_ATLAS_0506.md`, `tools/audit_crossbank_ai_atlas_0506.py`, `src/temporary_prg_bank_read.hpp`, `tests/temporary_prg_bank_read_test.cpp`.

The **15-byte fixed $FB96** helper itself has known JP semantics (select raw bank $0E via $E2D0, LDA ($08),Y, restore $0A); $E2D0 stores A to RAM $23 and VRC6 $8000. Do not treat the bank as permanently switched, use an array slice instead of an active mapped CPU bus, or omit $23/write-order effects. Native lift tests 65,537 combinations and preserves restored mapper; it is NOT a full 6502 stack/cycle simulation.

Under **conditional** raw-$0A context: $B597 -> $B689 (LDA $68; JSR $E7FB); pointer slot 0 -> $B6A4 -> $B7F7; room loader $B7F7-$B872 has eleven JSR $FB96 calls. The local mask $B825 AND #$0F, $B827 STA $54 establishes a **local** low-nibble field bound, not global FD62,Y data coverage. Selector $68 liveness and inbound mapper context are open.

Structural JP AI-script parallels: ID $24 record $A626 action $5D -> $8DC6; ID $25 record $AE1A action $5F -> $8E10; ID $26 record $AE6E action $89 -> $8DF9. Handler families contain raw JSR FC17 but **no script/handler liveness proof**. $FC17-$FC1E and fixed $FB96-$FBA4 remain unclaimed. This specifically prevents accidental code/data inflation from the 107 script pointers/792 candidate lattice cells.

All new work is infrastructure/semantic mechanism, with **zero strict new bytes**, PRG floor 49,399 (18.8442%), VPP 24/100. Fixed raw frontier $FB96; preserve six unclaimed gaps. Run previous ROM audit and native regression before 0507. 0507 should resolve first concrete inbound bank0A state selector and AI ID24/25/26 producers, then promote only exact consumed ROM bytes if evidence closes.


**0506 supplementary recovery edge:** raw bank-$0A:B4CC dispatcher is $19/JSR E7FB with 12 encoded targets. Its state index 1 B58C calls B4E9 (LDA #00; STA $68; RTS) then increments $19. State index 2 B597 invokes B689; $68=0 would select B6A4 and potentially B7F7. **This is conditional**, not live mapper/transitive $19/$68 proof. Run `tools/audit_bank0a_state_chain_0506.py` in addition to `audit_crossbank_ai_atlas_0506.py`. For 0507 trace caller bank state, interrupt/other $19/$68 mutations, and carry-gate at B6A4. Do not advance 0506 verified bytes or fixed physical frontier.


## 0507 closed — raw-bank $0A B4CC NMI state entry; conditional 582-byte graph

Reproducible evidence: `analysis/NMI_BANK0A_ROOM_DISPATCH_0507.md`, `tools/audit_nmi_room_dispatch_0507.py`, `src/room_state_dispatch.hpp`, `tests/room_state_dispatch_test.cpp`. Re-run the audit on the authoritative JP ROM and 65536-case C++ test for next recovery.

Existing fixed first-level `E363` table slot **$0D** points to **$E526**; `E526: LDA #$0A; JSR $E2D0; JMP $B4CC`, E2D0 stores to $23 and VRC6 $8000. This proves **raw bank $0A** for $B4CC on that NMI dispatch. Newly credited code is *only* five bytes `raw0A:$B4CC-$B4D0 = A5 19 20 FB E7`, physical PRG21, SHA `0cbfd39d34523da29edaa6a2dcf5cdb4b62de628d0e5568ea3879d7de5a1c0c7`. All fixed E526/E2D0/E7FB bytes pre-covered and not recounted.

The **12** mechanically encoded room-state pointer words $B4D1-$B4E8 plus second-level index0 $B6A4 yield a candidate **281-instruction/582-byte** graph (six noncontiguous ranges; SHA `807363d09368f7ae6ceaeae000df0fc50f56bba5bd2871ca749d7236ec9f3828`). This is **structural only**, except for $B4CC's 5 bytes. E7FB uses 8-bit ASL and can read beyond the encoded 12 entries for high state IDs; do **not** invent a $19 bound, clamp or classify all 582 bytes as verified. Selector $18=0D liveness, mapper state after external helpers, inter-frame $19/$68 mutations, B6A4 carry gate, and $07A0 B8C2 table producer remain unproved.

Four superficially plausible AI ID24/25/26 **direct** producers are ruled out by destinations: bank0B $863B stores #24 to $0606,X; $9234 stores #25 to $05C1,X; $9531 #26 and $B4BC #24 call E249. Do not assume these write AI-script selector $05EF,X. Script IDs 24/25/26 and FC17 remain provisional.

Native E7FB partial selector/Y lift has 65536 ROM-backed test cases. The ABI's final Z/N flags reflect **restored incoming Y**, not target high byte. No stack, zero-page side effects or full CPU parity claim.

Coverage: **49,404/262,144 = 18.8461%**; VPP 24/100. Fixed investigation frontier still FB96 and all six fixed physical gaps retained. Next 0508 focus: producer $18/$19/$68 and helper bank state; conditional B6A4->B7F7, $07A0 table producer; only then commit further graph bytes; AI script IDs and FD62,Y unresolved.


## Canonical subsystem documentation / preservation archive

The RLOFT-inspired, game-specific `JP/PreservationArchive/README.md` and numbered chapters `00..12` were added as a **separate preservation workstream** after semantic checkpoint 0507. Historical analysis reports in `JP/analysis/` remain byte-evidence/audit records; the archive is the continually corrected **human-readable source of subsystem behavior, technical models, quirks, restrictions and modding contracts**.

On every semantic checkpoint: (1) establish JP ROM identity, physical bank and covered operands; (2) commit reproducible source/audit; (3) update relevant archive chapters with evidence class and scope, including negative findings; (4) maintain Q/D/L/C/U register in chapter 10 and open roadmap in chapter 12; (5) run `JP/tools/audit_preservation_archive.py`; (6) update `PROGRESS.md`/this continuity; and (7) write `analysis/RESUME_STATE.json` **LAST**. Both published archive chapters and native algorithm tests can change without moving strict PRG/VPP counters.

The initial edition documents 0507's committed **49,404 verified PRG bytes (18.8461%)** and VPP **24/100**; this documentation update **adds zero semantic bytes and no rubric points**. Chapter publication is **not** a static-documentation completion certificate, a complete decomp, or a native playable/per-frame parity claim. Continue 0508 from actual schema-v23 ROM-verified resume state, not from archival section order.


## Post-0507 independent validation rubric update

GitHub Actions [run 37993214808](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/37993214808) passes the new `jp-native-regressions.yml`: compile eight native test binaries, run four ROM-free suites, validate the fixed VPP rubric, and audit archive links. A SHA-verified local ROM enables the remaining tests through `JP/tools/run_native_regressions.sh`. **VPP is now 25/100** by validation item 8.8. Strict verified PRG remains 49,404; the prior checkpoint 0507 and fixed frontier FB96 do **not** advance due to this tooling point. The RESUME_STATE VPP number is updated independently LAST after all other documents.


## Independent Nintendulator CPU reference conformance (separate validation milestone)

The [shared-library NES CPU golden test](../SharedNES/NESTEST_REFERENCE_0508.md) passes all 8,991 original nestest Nintendulator register/flags/stack/cycle states in [Actions run 38010527144](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/38010527144), with upstream test fixture SHA pins and 11 local ROM-free NROM/undocumented-opcode regression groups. This earns 1/2 of the two-point **validation reference trace harness** rubric: 4/8 -> 5/8, weighted VPP 25->26/100. The remaining validation point requires genuine JP VRC6 mapper/interrupt reference traces; the independent *CPU/mapper category's* original-game parity point remains open. Verified JP PRG stays 49,404; finished semantic checkpoint 0507; frontier FB96 unchanged.


## 0508 completed (narrow independent-Mesen fixed PRG source proof)

Checkpoint [0508](../analysis/0508_MESEN_FIXED_LIVE_PROOF.md) adds **exactly 100** original ROM bytes after 0507's 49,404: fixed PRG31 CPU **FBA5-FBAF (11), FBB0-FBBA (11), FF06-FF11 (12), FF14-FF55 (66)**. Real third-party Mesen2 breakpoint and stepped code evidence proves intro/prayer bank-00 stream-call restoration and Stage 1-02 active-object slot scanning/field clearing; independent disassembly verifies 39 original instruction starts and all 100 physical CODE-marked bytes. All credited new bytes lie inside 0507's *unclaimed* fixed gaps. **New strict lower bound 49,504 / 262,144 = 18.8843%; VPP 26/100, fixed frontier FB96 unchanged.** Reproduce with `tools/audit_mesen_fixed_live_0508.py JP.nes [report.json]` (source checks) and optional `--reference-emulator EMULATOR_DIR --private-evidence PRIVATE_DIR` (complete external witness); replay `audit_0508_predecessor.py` and 0507 native regression before further strict promotion. Previous 0508 room-$0D, $07A0 and full-frame/native parity questions remain OPEN; next research checkpoint 0509.


## Native 0509 compiled CPU integration, not standalone port

The new JP/native0509 CMake project builds a native C++ 2A03 interpreter with 151 official opcodes, VRC6a mapper and IRQ integration, controller and partial PPU/OAM/VRAM bus, and a headless original-source-ROM probe. It requires the exact Japanese ROM; it is **not yet playable**, pixel accurate, or independent of original PRG/CHR assets. An authenticated external Mesen2 original-ROM PC stream matches the first **7,828** instruction addresses; the first observed divergence at **7,829** is a PPU vblank timing mismatch, with native CPU state and gameplay reference parity still open. Synthetic and arithmetic regression tests run in CI. Technical note: docs/0509_NATIVE_CPU_HEADLESS.md. VPP 26/100, strict 49,504 bytes, last completed checkpoint 0508, fixed FB96 frontier retained.


**0509 PPU startup phase controlled cross-check:** Explicit reference-only PPU phase seed 31 (from Mesen2 initial 0:31 debugger snapshot) extends PC-address prefix match from 7,828 default to **24,773**; NMI entry at 24,774 diverges. Default native startup remains unmodified. Full frame parity and ROM-independent port remain open; VPP26 and 49,504 verified ROM bytes unchanged. See docs/0509_NATIVE_CPU_HEADLESS.md.


## 0509 native ROM-independent sprite/actor demonstrator

`JP/standalone0509` builds a native C++20 program with **no original ROM file or embedded game code/data**. It executes actual source-verified original JP actor-slot scan FF06, field-clear helper FF15/FF24, existing bank0D OAM shadow lift and bank0B collision math, with **synthetic** descriptors, planar CHR, scripted positions and software sprite preview. ROM-free CTest verifies all 4096 slot occupancy cases, all 256 indexed clear states per helper, real OAM output and deterministic generated-pixel fixture; ASan/UBSan checks passed locally. This is NOT playable Castlevania III, correct player/AI/scroll/game-stage flow, full PPU frame parity or a creditable new PRG range. [Technical note](0509_ROM_FREE_ACTOR_PIPELINE.md) and [build](../standalone0509/README.md). VPP 26/100, strict 49,504 bytes, last completed semantic checkpoint 0508, fixed first unprocessed FB96 remain unchanged.

## 0509 raw-$0A callsite verification (provisional)

A ROM-executed [cross-bank actor producer audit](../analysis/0509_ACTOR_SPAWN_PRODUCER_FINDINGS.md) traces raw bank $0A:$90CA through fixed $FF06 with all 4,096 occupancy combinations and 73,717 fetched source instructions. The branch-selected actor allocation writes $054E,X=$13 and $05EF,X=0; the preamble writes $10=0. No genuine reference-frame source liveness, global mapper lifetime, strict new ROM bytes or VPP point is established. Last certified checkpoint remains 0508; PRG floor 49,504, VPP26, fixed frontier FB96.

## 0509 actor allocation conditional source-producer gate

[Mapped raw-bank $0A:$90C5 conditional actor gate](../analysis/0509_ACTOR_PRECHECK_PRODUCER_FINDINGS.md) verifies original source JSR $8CDD, conditional $53/$07E0,X checks and fixed $FF06 first-free-slot scanner, then the $90CA actor allocation body. 4,096 occupancy masks times three precondition families; 12,288 bounded cases, 188,332 original instruction fetches, 25 distinct PCs. Confirmed when it **would not** allocate as well as when it would; real game-frame liveness and global input domains remain open. Last certified source checkpoint 0508, strict 49,504 PRG bytes (18.8843%), VPP26, fixed frontier FB96 unchanged. No machine RESUME_STATE update for provisional research.

## 0509 guard-source producers, provisional

[Original ROM-stepped $53/$54 and `$07E0,X` producer proof](../analysis/0509_ACTOR_GUARD_PRODUCERS_FINDINGS.md): source bank-$0A `$8154/$82A5/$83EE/$8402` indexed stores tested with carry/sign extension/6502 borrow and bit-0 masks; fixed `$FB7A-$FB95` paired counter tested exhaustively as a 16-bit wrapping increment/decrement. 262,912 source test cases and 3,280,384 instruction executions; three previous actor ROM audits also replayed locally. Global writers, genuine mapped caller and per-frame renderer effects still unknown. Not a new semantic PRG or VPP claim; completed checkpoint 0508, 49,504 verified PRG bytes, VPP26, fixed frontier FB96 unchanged.
