# Verified Parity Progress (VPP)

This project uses **Verified Parity Progress (VPP)** as its primary high-level progress metric.

VPP is a fixed 100-point evidence rubric. It is **not** an estimate of remaining labor, calendar time, lines of code, or percentage of ROM bytes disassembled. A point is earned only when the corresponding behavior/structure is supported by the authoritative ROM and a durable repository artifact (analysis, source, test, or audit).

The machine-readable score is `analysis/PROGRESS_SCORE.csv`; `tools/progress_score.py` validates and prints it.

## Current score

**VPP: 21 / 100 (21%)**

Baseline established during checkpoint 04E1.

| category | weight | earned | current basis |
|---|---:|---:|---|
| Foundation / cartridge model | 5 | 4 | exact ROM identity, physical PRG/CHR map, vectors, VRC6 CPU-window model; complete mapper-register use inventory still open |
| CPU / mapper / interrupts | 10 | 6 | RESET path, PRG helpers, top-level NMI, IRQ table/state machine, control-vs-ack behavior; native mapper/IRQ and trace parity open |
| Rendering / PPU | 10 | 5 | OAM arrays, selector/master tables, variable descriptor encoding, exact sprite transforms/state, native OAM lift; background/CHR/PPU parity open |
| Gameplay / object systems | 25 | 1 | only partial object dispatcher/state-machine architecture is currently proven; player/combat/enemy/boss systems remain overwhelmingly open |
| Stage / world / progression | 20 | 0 | stage data, room/scrolling, collision maps, route/progression, menus/password/end flow not yet reconstructed |
| Audio | 12 | 1 | NSF-to-ROM correlation is established; full driver/data/native APU+VRC6/parity work remains open |
| Native runtime / platform | 10 | 1 | isolated faithful native OAM subsystem exists; no complete CPU/game runtime executable yet |
| Validation / tooling | 8 | 3 | ROM identity audit, subsystem binary audits, and OAM unit tests exist; CPU traces, frame goldens, CI/end-to-end parity remain open |
| **Total** | **100** | **21** | |

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
8. native VRC6 PRG/CHR mapper implementation — open
9. native IRQ timing/scheduler implementation — open
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
- movement/physics/collision behavior: 4 — open
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
- music/SFX data formats: 2 — open
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

### 8. Validation / tooling — 8 points

- immutable ROM identity audit: 1 — **earned**
- ROM-backed subsystem audit tooling: 1 — **earned**
- native subsystem regression tests: 1 — **earned**
- CPU/bank/interrupt trace comparison harness: 2 — open
- deterministic frame-state/image golden tests: 2 — open
- CI/reproducible build-and-test gate: 1 — open

## Scoring rules

1. Category weights never change merely to make the percentage look better.
2. A score increase requires a committed evidence artifact and a note in `docs/PROGRESS.md`.
3. Corrections can reduce the score if previously credited evidence is invalidated.
4. Partial category credit is allowed only where the rubric explicitly gives a multi-point subweight.
5. Do not derive VPP from raw disassembly coverage. Data tables, overlapping semantics, and banked execution make raw byte percentage misleading at this stage.
6. When a conservative ROM-byte/code-data coverage ledger eventually exists, report it as a **separate metric**, never as a replacement for VPP.
7. Every user-facing checkpoint report should include the current VPP and whether it changed.
