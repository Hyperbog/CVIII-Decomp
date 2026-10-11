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

## 0509 original $84EA → $8501 → $8CDD/$FF06 → actor creation chain

[ROM-authenticated connected actor dispatcher](../analysis/0509_ACTOR_DISPATCH_CHAIN_FINDINGS.md) executes all selected four ROM-table routes to the three actor-handling entries $90C5, $90DF, $9133. Two entry modes (direct and upstream scheduler), 4096 occupancy masks each, 3 guard classes and masked high-nibble event variants cover **98,304 CPU cases and 6,174,946 instructions**. Byte-ordered memory mutation, register/flag/stack behavior and no-rollback partial allocation are checked; execution stops at scheduler $84F8 before $83D1. Real in-game dispatcher-row/mapper/frame liveness and global writer sets remain unproved. [Optional independent Mesen evidence checklist](0509_MESEN_ACTOR_DISPATCH_CAPTURE.md). Strict 49,504 PRG bytes, VPP26, last certified 0508, frontier FB96 unchanged; machine RESUME_STATE not advanced.

## 0509 Mesen2 independent gameplay actor event at frame 3092

The [source-backed live trace report](../analysis/0509_MESEN_ACTOR_LIVE_FINDINGS.md) and [compact machine JSON](../analysis/0509_MESEN_ACTOR_LIVE_REPORT.json) authenticate raw-$0A:$84F3→$8501→$8B2C under actual original-JP Mesen2 frame 3092 (X=$03, row=$32, subindex0, both $53/$07E0,X=0). 600 original source steps produce two type-$3D actor slots, execute fixed $FF06/$FF24 twice and return through $84F8. Clean-boot replay matches exact PC/cycles/trace hash; external emulator and unmodified user ROM are required for reproduction. **This settles a bounded live row, not all event rows**: direct $90C5/$90DF/$9133 remain synthetic-only; global $18 room and last-renderer $10 remain OPEN. Zero strict byte/VPP promotion, last completed 0508, verified floor 49,504, VPP26, fixed frontier FB96.

## 0509 seven-controller original Mesen live producer matrix

[Independent Mesen source/writer feedback loop](../analysis/0509_MESEN_ACTOR_FEEDBACK_FINDINGS.md) verifies 3 live row-$32 type-$3D spawn routes and 4 bounded negative routes across 7 separately completed 640-frame Mesen replays from verified clean ROM stage state. Physical PRG mapper conversion authenticates raw $0A RAM producer $8143/$8157/$8182, original dispatcher $84F3/$8501 and actor/event writers $8D90/$8B71/$85DD. Two bounded 5-byte source descriptors at original $A43F/$A444 are now linked to observed X=4/3 objects. Full cold-boot one-shot seven-fork driver was not completed due external orchestration timeout; isolated runs plus hash-constrained merger passed. No new coverage credit: checkpoint 0508, strict 49,504, VPP26, frontier FB96.

## 0510 native desktop title/intro/one-screen Stage 1 prototype (provisional)

[Source-native PC project](../native_demo0510/README.md) compiles a C++20 app, keyboard control and deterministic headless tests. The independently supplied Japanese Mesen frame/raster reference asset pack is private and ignored by Git; runtime performs no 6502/NES emulation. Except for FF06 vacancy and FF24 clear helpers, character movement, cutscenes, host sprites, level geometry and enemy AI are **placeholder source**, not reconstructed gameplay. Linux build and sanitizer/tests validated locally; Windows native code requires actual Windows CI verification. Last certified semantic checkpoint 0508, strict PRG49,504 and VPP26, fixed frontier FB96 unchanged. No RESUME_STATE promotion.

Windows build refinement: source-native Win32/GDI demo compiled and passed ROM-free CTest on GitHub's Windows Server 2025 VS2026 CI; Linux x86-64 CI also passed. Both binaries are packed with user-private reference assets outside repository, but Windows desktop/keyboard test remains pending. No source-equivalent game stage or PRG/VPP promotion. CI [run 38076049062](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/38076049062).

## 0510 faithful native C++ actor event row-$32 (not the PC demonstration)

[Independent Mesen original game row-$32 → C++ RAM-state comparator](../analysis/0510_ROW32_NATIVE_LIFT_FINDINGS.md) now includes an actual structured native semantic lift of $8501->$8B2C actor creation; type $3D, script $13, matching-count cap 3, first-free slot 1..12, fixed $FF24 field cleanup, original status/AI tables and source event high-nibble packing. Two naturally reached source object allocations X=3/4 at frame3092 match **all 1792 non-stack RAM bytes each**, across 383 original instructions; **4,111 native ROM-free test configurations**. Optional clean-boot original Mesen replay is source hash-locked and private savestate/output files are ephemeral. Original code/data spans are not promoted without certified physical overlap and all-route timing. Keep strict PRG49504, VPP26, last completed checkpoint0508 and fixed frontierFB96; no update to RESUME_STATE.json.

## 0511 source-equivalent native 2-axis actor motion with original game RAM goldens

[Validated original raw bank $0B:$8001 / $8037 source lift](../analysis/0511_ACTOR_MOTION_NATIVE_FINDINGS.md) integrates into `standalone0509` CMake and ROM-free regression gate; 69,646 oracle cases and sanitizers pass. Actual Mesen actor slots 1 and 2 spawned in natural Stage 1 gameplay have bank-qualified $0B 30-opcode movement calls, with all 1,792 nonstack RAM bytes and final A/Y/P matched for each. Real frame 2604 belongs to a 100-frame checkpoint-reload controller policy, not the earlier 0509 continuous frame3092 route. Original Mesen private state hash pinned; one-call cold replay bootstrap incomplete due Mesen headless stall. Next target original $0B:$80E3-$8100 writer and AI script dispatch, NOT host demo. Verified strict 49,504 PRG, VPP26, last completed 0508 and fixed frontier FB96 unchanged.

## 0512 fixed FDF8 → mapped $0B:80E3 horizontal 9-bit displacement source lift

[Verified 0512 native displacement](../analysis/0512_ACTOR_DISPLACEMENT_NATIVE_FINDINGS.md) reconstructs actual raw-bank `$0B:$80E3–$810E` branch with `SBC` signed delta and X ninth-bit carry, preserving original A/X/Y/P and scratch. Source fixed `$FDF2` maps bank $0B and `$FDF8` calls into it; physical mapping `$02C0E3` independently confirmed by Mesen. **73,742 native cases**, exact **1,792/1,792 RAM** for *each* of two naturally active type-$3D actors in original Mesen (3,584 overall). Their real `$65=$6B=0` while signed/overflow/wrap states are ROM-free math tests only. Original `$810F` vertical/actor-deletion branch and fixed `$B1F8` not lifted. [Private-state ROM-authenticated replay script](../tools/audit_mesen_displacement_0512.py). Preserve verified strict PRG49,504, VPP26, completed checkpoint0508, fixed CPU frontierFB96.

## 0513 vertical signed displacement native code with clearly synthetic original-ROM differential

[0513 original $0B:$810F/$8140/$8843 faithful C++ lift](../analysis/0513_VERTICAL_DISPLACEMENT_NATIVE_FINDINGS.md) closes these *instruction-defined semantic branches* for the bounded source entry, including original ZP scratch, 9-bit coordinate, `$054E/$0400` type gate, type-$3B `$0606/$061D` continuation and A/Y/P flag results. 270,351 independent ROM-free mathematical cases and 54 original Mesen forced-state CPU paths (96,768 nonstack RAM bytes exact). The Mesen 54 paths deliberately inject `$65/$6B` and PC; no gameplay liveness credit! Verified natural frame2603–2903 had no bank0B `$810F` branch. Next: actual `$65` producer domain, fixed `$B1F8` following `$FDFB`, native whole-actor frame goldens. PRG/VPP strict floor 0508, 49,504 bytes, 26 points and FB96 unchanged.

## 0514 original gameplay preflight: source delta producer + postprocess B1F8 gate

[0514 original-Mesen source and native differential](../analysis/0514_ACTOR_PREFLIGHT_NATIVE_FINDINGS.md): native PRG30 D2FE-D30C (`$62>=2` delta `$53-$08->$6B`) and bank0B B1F8-B215 actor type/frame eligibility, exact RAM/scratch plus A/X/Y/P and gate destination. 100,357 native mathematical/index tests; 38 original-ROM Mesen stepped cases (two natural-equivalent input, 36 forced RAM branch edges), 68,096 non-stack RAM bytes. Source `$D066` direct stage-row `$65` writer located via pointer `$0A/$0B` selected from `$34/$35/$36`, but genuine high-bit vertical input remains unobserved. Different scheduler vs allocator X ranges documented (1–17 vs 1–12). **Not** a reconstructed collision routine or complete frame: next original `$B217` / `$B258` and `$62=0/1` paths remain OPEN. Last completed strict 0508, PRG49504, VPP26 and fixed FB96 unchanged.

## 0515 original mapped actor collision admission through fixed collision call boundary

[Original Japanese native source-equivalent collision gate B217–B231](../analysis/0515_COLLISION_ADMISSION_NATIVE_FINDINGS.md) composes with 0514 B1F8 gate to `$B232` before actual `JSR $B339`. Hardware Mesen physical PRG `$02F217` and 27 original mapped bytes authenticated. **82,947 native test cases**, 58 original-Mesen RAM/CPU comparisons: TWO windows on the **same naturally reached actor X1** plus 56 explicitly RAM-injected synthetic branch cases, 103,936/103,936 non-stack RAM bytes and A/X/Y/P plus destination PC exact. No native B339 or collision helper yet; natural 48-instruction trace proves `$B339` table prelude then `$B36D JSR $80B3`, making this the next source-first frontier. Native index X1..17 does not alter FF06 allocation 1..12. Certification remains 0508: 49,504 PRG, VPP26, fixed frontier FB96, no RESUME_STATE promotion.

## 0516 composed native actor collision measurement, original ROM/CPU verified

[0516 original raw-bank0B B339/B393 collision measurement](../analysis/0516_COLLISION_MEASURE_NATIVE_FINDINGS.md) plus its absolute-difference subroutines `$80B3/$80C1` and authentic `$BB05/$BB0E/$BB80/$BC08/$B394` original data are source-lifted. The exact `$B394[1]=$05` was verified. New native code composes prior B1F8/B217 gates and B232 JSR B339 through B393. **139,343 C++ tests**, sanitizer pass; 50 original Mesen windows (2 overlapping windows on one naturally reached actor, 48 synthetic mutated RAM) exact across 89,600 nonstack RAM bytes and flags/PC. Natural actor takes horizontal early return; synthetic vertical path matches. Excluded original E5BE/B7 and B396 special branch; next source work is B235 collision response and alternate B396/E5BE. No new strict certified physical PRG bytes or VPP (0508 PRG49504/VPP26; FB96); source private artifacts retained locally.

## 0517 original collision-tail path now natively reaches $FDFE

[Original ROM source-backed collision-tail native state transfer](../analysis/0517_ACTOR_COLLISION_TAIL_NATIVE_FINDINGS.md): B235 carry branch skips/initializes $7E/$8E/$8D, B258 actor type and attachment gates, B29D empty follower slots 20..22 scan, B31F RTS return to fixed FDFE. Connected original B1F8→B217→B339→B393→B235→FDFE **91-instruction naturally reached CPU slice** matches full 1,792 nonstack Mesen RAM bytes and returned CPU registers/flags. Secondary 37-opcode natural tail overlaps same actor; 14 synthetic source comparisons cover type and attachment alternate stop branches, total 28,672 exact compared bytes. 65,539 ROM-free tests, sanitizers. Audit source SHA-locks bank0B windows and private controller-produced savestate; original FDFE continuation and B243/B27C/B2A8 helpers remain unlifted. Certified metrics 0508 PRG49,504, VPP26, physical frontier FB96 not promoted.

## 0518 evidence-based source accounting and gameplay VPP adjustment

[0518 formal decision](../analysis/0518_RECONCILIATION_AND_VPP_DECISION.md): 25 original source windows/1,365 physical PRG bytes, 546 already 0501, 78 already 0508, **741 unclassified against full history** (not new certified bytes); original FF12–FF13 remains uncredited. Gameplay movement/collision VPP +1 on independent reusable 91-instruction Stage1 B1F8-to-FDFE source/native state-matched actor pipeline: gameplay **3/25**, VPP **27/100**. No further native-runtime/validation awards. Last completed semantic checkpoint **0508**, strict floor **49,504**, fixed frontier **FB96**. Continue fixed FDFE scheduler and B243/B27C/B2A8; assemble full earlier byte union before strict promotion.

## 0519 first fixed-bank actor scheduler continuation beyond FDFE

[Original ROM Mesen natural FDFE→FE31 actor15/type80 gate](../analysis/0519_FIXED_SCHEDULER_NATIVE_FINDINGS.md) now has 10 instruction-boundary replay and exact full 2 KiB RAM parity, PC/A/X/Y/P; 73,731 native bounded gate cases plus sanitizer pass. Native file `src/scheduler_postcollision_0519.cpp` only chooses next original fixed CPU call boundary FE0B/FE1D/FE2C/FE31/FE36/FE6E; **does not** model $BD11/$FF56/$FE8C. Independent 0518 VPP27 and source strict PRG49504 remain unchanged, semantic source certificate 0508/frontier FB96. Next prove original BD11 continuation from natural X15 state; no whole-frame parity.

## 0520 original fixed/raw scheduler continuation with natural BD11->FE60

[0520 original ROM CPU source audit](../analysis/0520_SCHEDULER_BD11_FE34_NATIVE_FINDINGS.md) extends the natural 0519 actor15/type80 from `$FDFE` through `JSR $BD11`, original raw-bank0B `$BD11/$BD10` early return, fixed PRG31 `$FE34` type/attribute logic, to `$FE60` before `JSR $EF93`. Connected 28-instruction natural window matches all 1,792 nonstack RAM bytes + A/X/Y/P/PC; nested BD11->FE60 natural 17-instruction window matches full 2KiB, same original actor. Twelve RAM-injected original CPU edge cases cover BD15/BD1F and FE4E/FE63/FE6E, total 14 cases/28,416 RAM bytes exact. 77,827 ROM-free native unit states+sanitizers, audited ROM/Mesen hashes, no full actor frame. Last strict semantic 0508, PRG49,504 and VPP27, frontier FB96 unchanged. Next original source FE60 JSR EF93; preserve source hardware stack exclusion rule in composed path.

## 0521 original fixed EF93 animation/countdown now native-equivalent for descriptor $0E

[Natural original Mesen-to-native animation update](../analysis/0521_ORIGINAL_ANIMATION_NATIVE_FINDINGS.md) adds EF93 timer, ROM-authenticated pointer F359 and 16 source descriptor triples to earlier FDFE/BD11/FE34 gate. Original 57-opcode actor15 FDFE→FE63 matches **1,792 nonstack RAM** and A/X/Y/P/PC. Overlapping natural direct EF93 path matches all 2048 RAM bytes; 36 original-ROM synthetic branch probes test table limit equal/below and timer short exit, 38 comparisons/77,568 RAM bytes. 65,547 bounded C++ tests plus ASan/UBSan pass. Next FE63 bank-switch E2D0 and callback 8161/826C. Provenance ledger now checks 0521 natural/synthetic counts. No strict PRG/VPP promotion: 49,504, 27/100, 0508/frontier FB96.

## 0522 provisional fixed FE63 -> bank0B actor tail (not Mesen-certified)

[0522 source foundation](../analysis/0522_FOUNDATION_FINDINGS.md) authenticates original JP fixed E2D0, FE63-FE75, raw $0B:$8161-$81B1, and raw $0B:$826C-$8281. ROM-free structured native C++ handles X=$0D-$12, bit7 actor attributes, type/position early exits, bank write $23=$0B and next scheduler boundary FDEC/FE75; 110,592 supported states, 18,432 deliberately rejected $8193 callback cases and 5 invalid actor-index guards. Release assertions enforced and ASan/UBSan locally passed. The replay CLI compares 1,792 nonstack RAM bytes, CPU A/X/Y/P/PC, and PRG16 bank when private independent Mesen before/after captures become available. **No original 0522 Mesen replay has been executed, no native whole actor frame, no ledger row or score/certificate advancement.** Strict PRG49,504, VPP27, semantic0508 and fixed frontier FB96 remain unchanged.

## 0523 original-JP raw0B $8193 non-$4D reset return (source-verified only)

[0523 original reset source findings](../analysis/0523_SOURCE_FINDINGS.md): native bounded C++ composes previous FE63/8161/826C with mapped raw0B $8193-$81A8 for actor X=$0D-$12 and type $30-$65 except $4D when $041C,X>=$F8. Authenticated 22 original physical PRG bytes at 02C193; four actor fields $054E/$0470/$0400/$05EF,X clear before FE6E scheduler loop. 147,456 ROM-free configurations: 138,240 supported (18,432 new reset cases), 9,216 explicit $4D->$81B2/$B56B guard cases, 5 invalid-index guards; Release assertions and ASan/UBSan pass locally. Original-Mesen continuation remains unexecuted; replay CLI synthetic harness only. No original-Mesen evidence ledger row or score promotion. Strict PRG49,504, VPP27, semantic0508 and fixed frontier FB96 unchanged.

## 0524 source-bounded type4D linked actor callback, original Mesen pending

[Physical source findings](../analysis/0524_SOURCE_FINDINGS.md) establish the raw0B $81B2-$81CB conditional actor link from $061D,X, optional $B56B reset gated by $0470,linked & $81, unconditional second B56B on index $69, and fixed $FE6E scheduler CPX. Structured native implementation composes 0523, passing 110,592 ROM-free indexed states plus guards and ASan/UBSan. Exact ROM opcodes and hashes audited; synthetic-only RAM replay smoke tested, not original Mesen. No original-Mesen evidence ledger row, natural type4D event, strict PRG or VPP promotion; retain PRG 49,504, VPP 27/100, certified semantic 0508 and fixed FB96 frontier.

## 0525 reconstructed incremental physical PRG union; literal recomp bridge

[ROM and recomp evidence](../analysis/0525_PRG_RECOMP_RECOVERY.md): historic 0500 physical SHA-locked intervals restored; 0500/0501/0502/0504/0507/0508 account for **59 mutually disjoint regions / 6,029 bytes**. A separate pre-0500 43,475-byte physical mask has not been recovered. Against this explicit 0500-0508 mask the 0510-0517 1,365-byte inventory has **739 outside-known bytes**, NOT the older partial 741 (two B394-B395 table bytes belonged to 0502). Machine audit optionally verifies original retail ROM and emits 59 byte-for-byte roundtrip .asm literal scaffolds; these are not source-semantic lifts. No strict PRG or VPP promotion, semantic0508/FB96 unchanged.

## 0525 additional executable decomp/recomp milestone — first 88 source opcodes/operands

A real symbolic 6502 assembly reproduction of original PRG raw0B $8193/$81B2/$B56B and fixed E2D0/FE63 now reassembles **88/88** exact physical source bytes across five regions, including symbolic BEQ/BCS/JSR targets. Bounded two-pass reassembly checker is ROM-free in CI, exact-original-ROM byte comparison optional locally. [Source under JP/recomp](../recomp/actor_tail_0525.asm), [fixed source](../recomp/fixed_tail_0525.asm), [verifier](../tools/test_recomp_6502_0525.py). These source bytes were previously certified, so no strict PRG/VPP increase. This is static 6502 recompilation and does not demonstrate Mesen gameplay parity.

## 0526 — Incremental historical certificate reconstruction plus 403 exact 6502 assembly bytes

Git origin snapshots 78896c70544b and a7d31bf1e7d6 recover 04FE/04FF's correct original physical code/data certificates (17 regions / 1,888 bytes), checked via [ROM audit](../tools/audit_historical_prg_0526.py). Combined with 0525's 59 regions gives **76 disjoint verified physical intervals / 7,917 prior certified bytes**; 41,587 pre-04FE historical bytes still lack comprehensive physical mapping. [Recomp source](../recomp/fixed_scheduler_0526.asm) spans fixed FDE4-FE62 and FE76-FEE9 including symbolic FE98 pointer table, and [raw bank0B](../recomp/raw0b_callbacks_0526.asm) adds 8161-8192 and 826C-8281. [Assembler checker](../tools/test_recomp_6502_0526.py) locally reassembled all 315 new original JP ROM bytes with independent physical SHA and byte comparison, cumulative 403 real mnemonic bytes. CI without ROM checks embedded SHA fingerprints; CLI with ROM checks retail original separately. All 315 were historically credited, so strict 49,504/262,144 and VPP27/100, semantic checkpoint0508, fixed FB96 remain unchanged.

## 0527 historical exact original-JP raw bank05 command source

Original historic audits from 04FB/04FC/04FD expose three adjoining source-certified raw VRC6 bank05 command/data regions at physical PRG $0147AE-$017F05, **14,168 total previously strict-certified bytes**. [Reproducer](../tools/audit_bank05_certificate_0527.py) verifies mapper mapping, SHA256 fingerprints, and deduplicated 04FB-0508 union (79 intervals/22,085 bytes); retail ROM optional in GitHub CI but verified locally. Historic sources prove script operand producer bounds; no claim these 14,168 are executable 6502 or new strict bytes. Remaining legacy physical mask gap 27,419, source outside mapped historical mask 739 still unpromotable. Actual instruction reassembly remains 403/403 via 0525-0526. Strict 49,504/262,144 and VPP27, completed semantic0508/frontier FB96 unchanged.

## 0529 — Bulk original-JP 0501 mapped control-flow decompilation

Rather than individual tens-of-byte source lifts, [0529 bank source generator](../tools/build_whole_cart_recomp_0529.py) now converts **1,864 additional authenticated 0501 6502 instructions / 4,030 bytes** into native 6502 assembly with original physical 16KiB raw and 8KiB fixed bank mapping and a two-pass source verifier. These plus 403 human-authored bytes yield 4,433 symbolic original-PRG source bytes. A 25-module PRG/CHR image round-trips the original 393,232-byte retail JP iNES exactly; the 257,711 remainder of PRG is explicitly unclassified `.byte` fallback. [Source/provenance report](../analysis/0529_WHOLE_CART_BANK_RECOMP.md). CI runs the ROM-free assembler test and the full authenticated image regeneration only when the original JP ROM is provided. Strict PRG remains 49,504/262,144, VPP27/100, certified semantic0508 and frontier FB96 unchanged; no Mesen parity claim.

## 0530 bulk fixed-bank real opcode source with ROM SHA pinned dispatch metadata

Added [lift_fixed_dispatch_0530.py](../tools/lift_fixed_dispatch_0530.py) to the [full cart recompilation generator](../tools/build_whole_cart_recomp_0529.py): original 04FE/04FF/0500 PRG31 code graph, first 16-pointer E363 table, nested 32-pointer F39D table, F84E/F96A second-level 16+10 pointers and FB31 3-word data table. Exactly **2,719 further 6502 mnemonic bytes and 154 typed pointer bytes** (1,218 instructions) from three original SHA-locked historic decoded graphs, **7,306 cumulative known mnemonic+pointer bytes**. Original JP retail 393,232-byte iNES is reassembled from 25 bank modules with exact hash. No new certification: all 2,873 were previously credited; strict floor49,504, VPP27/100, semantic0508/frontier FB96 unchanged. Generated ROM-bearing source files remain local only.

## 0531 original bank05 script source

[Root-labelled source generator](../tools/lift_bank05_scripts_0531.py) consumes original raw0C producer metadata at CPU $8F60 and SHA-locks the raw05 $87AE-$BF05 14,168-byte historical 04FB/04FC/04FD script stream, with 84 producer references, 72 distinct script entry roots and stage/mode comments. No false 6502 decode of original game data. [Findings](../analysis/0531_BANK05_SCRIPT_SOURCE.md). 25-bank original JP image exact rebuild, 21,474 source-classified PRG bytes, 240,670 unclassified bytes. Existing strict 49,504 / VPP27 / semantic0508 / fixed frontier FB96 remain unchanged.

## 0532 original sound-parser/code and bank04 script integration

[Source classifier](../tools/lift_bank04_parser_0532.py) decodes 786 official NMOS instruction starts from original 04F7 dispatch CFG and preserves 249 physical lookup/table bytes, then instantiates the 1,965-byte byte-identical parser in original raw banks04/05/0C. Separately parses original raw0C $8F60 producer metadata to annotate 102 references/96 script roots, recovering all 14,032 source-authenticated bank04 $87AE–$BE7D data bytes across four historical checkpoints. Two-pass reassembly of the original NES is exact; [negative verifier](../tools/test_bank04_parser_0532.py) rejects malformed source data, changed bank parser and metadata/ROM. Total typed PRG 41,401, with 12,294 real instruction+operand bytes, 907 typed local/inline pointer bytes and 28,200 source-authenticated stream/data bytes; 220,743 unclassified. New 0532 increment 19,927 already historically admitted physical bytes, not strict progress. PRG strict 49,504/262,144, VPP27, certified semantic0508, fixed investigation frontier FB96 unchanged.
