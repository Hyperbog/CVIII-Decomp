# Verified Parity Progress (VPP)

This project uses **Verified Parity Progress (VPP)** as its primary high-level progress metric.

VPP is a fixed 100-point evidence rubric. It is **not** an estimate of remaining labor, calendar time, lines of code, or percentage of ROM bytes disassembled. A point is earned only when the corresponding behavior/structure is supported by the authoritative ROM and a durable repository artifact (analysis, source, test, or audit).

The machine-readable score is `analysis/PROGRESS_SCORE.csv`; `tools/progress_score.py` validates and prints it.

## Current score

**VPP: 28 / 100 (28%)**

The latest point is **Audio → music/SFX data formats (first of two)**: original-ROM authenticated 125 sound descriptors, 325 bank-qualified refs, 148 phrase pointers, and a complete bounded phrase byte grammar ($00–$FA arithmetic and $FB–$FF control branches), with 5,610 JP0655 ordinary and 1,827 JP0656 original-6502/native test cases. All outputs remain dormant and natural original-game audio parity is not proved. [JP0656 evidence](../analysis/0656_ORIGINAL_SOUND_CONTROL_COMPLETE.md).

The preceding gameplay point is a distinct reusable original-Stage-1 native actor collision subsystem: the 0514-0517 connected B1F8 to FDFE path matches original Mesen across 91 source CPU instructions and all 1,792 non-stack RAM bytes plus A/X/Y/P. A formal fixed-rubric review (analysis/0518_RECONCILIATION_AND_VPP_DECISION.md) advances gameplay movement/collision from 1/4 to 2/4. This is not full-frame parity or a strict PRG-byte promotion.

The preceding validation point was independent CPU state+cycle trace conformance: the project's ROM-fetched 6502 core plus a separate test-only stable undocumented opcode extension matches all **8,991** preinstruction PC/A/X/Y/P/SP/cycle states of the independently recorded Nintendulator nestest log. [Green SHA-pinned Actions run 38010689051](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/38010689051). This earns **one of the existing two validation trace-harness points**; the second point and separate original Japanese VRC6 CPU/interrupt trace-parity point remain OPEN. Strict game PRG coverage is unchanged.

| category | weight | earned | current basis |
|---|---:|---:|---|
| Foundation / cartridge model | 5 | 4 | exact ROM identity, physical PRG/CHR map, vectors, VRC6 CPU-window model; complete mapper-register use inventory still open |
| CPU / mapper / interrupts | 10 | 8 | RESET path, PRG helpers, top-level NMI, IRQ table/state machine, control-vs-ack behavior, native VRC6 PRG/CHR mapper, native VRC6 IRQ scheduler; trace parity still open |
| Rendering / PPU | 10 | 5 | OAM arrays, selector/master tables, variable descriptor encoding, exact sprite transforms/state, native OAM lift; background/CHR/PPU parity open |
| Gameplay / object systems | 25 | 3 | original object dispatcher architecture, isolated collision-math architecture, and distinct connected B1F8-to-FDFE actor collision/follower pipeline with 91-instruction original Mesen parity; remaining player/combat/enemy/boss systems open |
| Stage / world / progression | 20 | 0 | stage data, room/scrolling, collision maps, route/progression, menus/password/end flow not yet reconstructed |
| Audio | 12 | 2 | NSF/retail correlation plus first original phrase/data-format point (JP0652–JP0656); second format, driver, native APU/VRC6 and parity work remain open |
| Native runtime / platform | 10 | 1 | isolated faithful native OAM subsystem exists; native mapper/IRQ/collision primitives now exist but complete memory/PPU integration and executable are open |
| Validation / tooling | 8 | 5 | ROM identity/subsystem audits, native tests and CI; independent Nintendulator CPU register/status/stack/cycle trace 8991/8991; original JP VRC6 mapper/IRQ trace and frame goldens open |
| **Total** | **100** | **27** | |

## Fixed rubric

### 1. Foundation / cartridge model — 5 points

One point each:

1. exact target ROM identity and immutable hashes — **earned**
2. physical PRG/CHR segmentation/bank map — **earned**
3. vectors and fixed-bank entrypoints — **earned**
4. VRC6 CPU PRG-window model — **earned**
5. complete game-specific mapper-register usage inventory — open

### 2. CPU / mapper / interrupts — 10 points

One point each:

1. RESET path reconciled — **earned**
2. tracked/raw PRG bank helper semantics — **earned**
3. top-level NMI path reconciled — **earned**
4. IRQ dispatch table bounded and mapped — **earned**
5. IRQ state-transition ledger closed — **earned**
6. VRC6 IRQ control vs acknowledge behavior preserved — **earned**
7. transitive NMI helper/bank-context closure — open
8. native VRC6 PRG/CHR mapper implementation — **earned** (`src/vrc6_mapper.*`, `tests/vrc6_mapper_test.cpp`)
9. native IRQ timing/scheduler implementation — **earned** (`src/vrc6_irq.*`, `tests/vrc6_irq_test.cpp`)
10. CPU/interrupt trace parity against reference execution — open

### 3. Rendering / PPU — 10 points

One point each:

1. OAM object arrays and slot permutation — **earned**
2. sprite selector/master frame-pointer hierarchy — **earned**
3. variable-width descriptor encoding — **earned**
4. exact sprite transform/cache/clipping/non-local-exit semantics — **earned**
5. native faithful OAM renderer source — **earned**
6. background/nametable update pipeline — open
7. CHR banking/raster-render setup — open
8. sprite/background integration in native runtime — open
9. PPU register/timing parity for required game behavior — open
10. deterministic frame/image parity tests — open

### 4. Gameplay / object systems — 25 points

Subweights:

- object dispatcher/state-table architecture: 5 points — **1 earned / 5**
- player control/state machine: 4 — open
- movement/physics/collision behavior: 4 — **2 earned / 4** (`analysis/NMI_BANK0B_COLLISION_ZP10_0502.md`, `src/collision_math.*`, `tests/collision_math_test.cpp`)
- combat/weapons/damage: 4 — open
- common enemy/actor AI: 4 — open
- bosses/special actors: 4 — open

Partial points in this category require a committed, reusable architectural result; isolated routine naming alone does not earn a point.

### 5. Stage / world / progression — 20 points

- stage/room data formats: 5 — open
- scrolling/room transitions: 4 — open
- collision/environment maps: 4 — open
- route/stage progression: 3 — open
- menus/password/ending flow: 2 — open
- reproducible stage-data extraction tooling: 2 — open

### 6. Audio — 12 points

- NSF/retail-ROM correlation: 1 — **earned**
- music/SFX driver architecture: 3 — open
- music/SFX data formats: 2 — **1 earned / 2**, source-authenticated complete JP primary descriptor / secondary phrase format plus original-6502 versus native ordinary and control-byte interpreter (JP0652–JP0656); raw04/05 stream grammar and full producer ownership remain open
- native 2A03 + VRC6 implementation/integration: 3 — open
- game-side sound-event mapping: 2 — open
- audio register/output parity: 1 — open

### 7. Native runtime / platform — 10 points

- at least one faithful native subsystem lift: 1 — **earned** (`src/oam_renderer.*`)
- CPU/static-recomp execution core: 3 — open
- memory/mapper/PPU integration: 2 — open
- input + deterministic frame loop: 1 — open
- audio backend integration: 1 — open
- bootable/playable native executable: 1 — open
- reproducible cross-platform build/package: 1 — open

The standalone mapper, IRQ and collision-math source do not themselves earn additional native-runtime integration credit; that requires wiring them into the CPU/memory/PPU frame runtime.

### 8. Validation / tooling — 8 points

- immutable ROM identity audit: 1 — **earned**
- ROM-backed subsystem audit tooling: 1 — **earned**
- native subsystem regression tests: 1 — **earned**
- CPU/bank/interrupt trace comparison harness: 2 — **1 earned** (independent CPU/NROM state and cycle reference log 8,991/8,991, pinned green CI 38010689051); **1 open** (original JP VRC6 mapper and interrupts against external reference execution)
- deterministic frame-state/image golden tests: 2 — open
- CI/reproducible build-and-test gate: 1 — **earned** (ROM-free [GitHub Actions](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/37993214808); exact JP-ROM extensions runnable locally through `JP/tools/run_native_regressions.sh`)

## Scoring rules

1. Category weights never change merely to make the percentage look better.
2. A score increase requires a committed evidence artifact and a note in `docs/PROGRESS.md`.
3. Corrections can reduce the score if previously credited evidence is invalidated.
4. Partial category credit is allowed only where the rubric explicitly gives a multi-point subweight.
5. Do not derive VPP from raw disassembly coverage. Data tables, overlapping semantics, and banked execution make raw byte percentage misleading at this stage.
6. Report conservative ROM-byte/code-data coverage as a separate metric, never as a replacement for VPP.
7. Every user-facing checkpoint report should include the current VPP and whether it changed.

## 0518 fixed-rubric VPP reassessment

The **second** (of four) movement/physics/collision subpoints credits the connected and reusable original-JP B1F8/B217/B339/B235/B29D-to-fixed-FDFE actor pipeline, **not** another point for previously counted isolated collision arithmetic. The naturally reached original Mesen actor executes 91 source CPU instructions; the native result matches 1,792/1,792 non-stack RAM bytes and return A/X/Y/P. 0517 alternative branches have bounded synthetic tests, not independent natural liveness. Full collision response, player physics, native integrated frame, original PPU and new strict PRG coverage are **not** credited. See [decision](../analysis/0518_RECONCILIATION_AND_VPP_DECISION.md).
