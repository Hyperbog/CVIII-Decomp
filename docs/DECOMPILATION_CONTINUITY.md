# Akumajou Densetsu decomp/recomp continuity playbook

This is the durable handoff for future conversations working on `Hyperbog/CVIII-Decomp`. Read this file, `docs/PROGRESS.md`, `docs/PROGRESS_METRIC.md`, and `docs/ROM_IDENTITY.md` before new work. The repository must be sufficient to resume without chat history.

## Objective and controlling evidence

Faithfully reverse engineer the Japanese NES release of **Akumajou Densetsu** into an evidence-accountable native PC decompilation/recompilation. Preserve original behavior first; QoL/mod features come later.

The ROM bytes are controlling evidence. Hardware documentation, emulator behavior, NSF/M3U data, names, and hypotheses are secondary. Never modify or commit the source ROM.

Target identity:

- size `393232` (`0x60010`)
- SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`
- PRG 256 KiB, CRC32 `BA6BDD6A`
- CHR 128 KiB, CRC32 `BF15255C`
- Mapper 24 / Konami VRC6a

Run `python tools/analyze_rom.py <rom>` before relying on a local ROM.

## Progress metric

Primary metric: **Verified Parity Progress (VPP) = 21/100**.

- rubric: `docs/PROGRESS_METRIC.md`
- machine-readable score: `analysis/PROGRESS_SCORE.csv`
- validator: `tools/progress_score.py`

VPP is evidence-based, not a labor/time estimate or raw disassembly-byte percentage. Increase it only when committed evidence satisfies the fixed rubric.

## Bounded-checkpoint policy

Each user `continue` means one bounded checkpoint.

- normal new-ROM budget: **500-5000 bytes**, default near 1 KiB;
- a checkpoint may expand within that range when newly discovered local edges are necessary to close the same narrow question;
- do not stop merely because an initial 512-byte/1 KiB sub-window ends;
- do not silently expand beyond about 5 KiB;
- isolated signatures outside the primary span are allowed only to prove the same question;
- provide short status updates after material findings;
- commit before reporting.

Checkpoint flow:

1. read current continuity/progress/metric/identity and branch head;
2. choose only the listed next question and initial byte span;
3. regenerate ROM evidence;
4. expand only as needed within the byte budget to close that question;
5. add/update focused analysis/audit/source artifacts;
6. update progress and VPP only if earned;
7. update this handoff when the target/methodology changes;
8. commit;
9. stop and report.

## Fidelity rules

1. Never guess code/data boundaries or semantics.
2. Reconcile translated routines instruction-by-instruction to ROM bytes.
3. Track physical PRG bank + CPU address.
4. Preserve VRC6 bank writes and interrupt-side restoration exactly.
5. Preserve 6502 widths, flags, wrapping, zero-page aliasing, stack/interrupt behavior, and unusual control flow.
6. Never extend a table merely because following bytes decode plausibly.
7. Do not invent host-side bounds/default behavior until producer domains are proved.
8. Preserve PRG26 sign/carry/`ROR` arithmetic literally.
9. Preserve PRG26 non-local `PLA; PLA; RTS` OAM-full behavior.
10. Preserve shared ZP state: OAM attribute cache `$10` is shared RAM, not a per-object local.
11. Keep uncertain names conservative.
12. NSF/M3U are corroborating audio evidence only.
13. No original ROM bytes in Git.

## Cartridge / interrupt stable facts

VRC6 CPU map:

- `$6000-$7FFF`: PRG RAM
- `$8000-$BFFF`: switchable 16 KiB PRG ROM
- `$C000-$DFFF`: switchable 8 KiB PRG ROM
- `$E000-$FFFF`: fixed PRG31

Fixed vectors:

- RESET `$E00B`
- NMI `$E057`
- IRQ `$E0F5`

Bank helpers:

- `$E2D0/$E2D2`: tracked/raw 16 KiB bank selection
- `$E2C4`: selects PRG30 at `$C000-$DFFF`
- NMI bank `$0D` call `$8001` = `PRG26:$8001`
- IRQ raw bank `$01` = PRG02/PRG03

IRQ table is exactly `PRG02:$9F01-$9F5A`, 45 states `$00-$2C`; `$9F5B` is code. The old `$9F60` overlap claim was false and must not be restored. `$80` is a high-bit bypass sentinel. Highest explicit chain: `29 -> 2A -> 2B -> 2C`.

IRQ exits differ:

- `$E118`: clears VRC6 IRQ Control `$F001`, then acknowledges;
- `$E11D`: enters at acknowledge `$F002` without the control clear.

See `analysis/PRG02_IRQ_dispatch.md` and `analysis/IRQ_STATE_MACHINE.csv`.

## OAM / sprite stable facts

Read before changing renderer code:

- `analysis/PRG26_SPRITE_FORMAT.md`
- `analysis/SPRITE_SET_TABLE.csv`
- `analysis/SPRITE_MASTER_TABLES.csv`
- `analysis/OAM_OBJECT_FIELDS.csv`
- `analysis/ZP10_OAM_STATE.md`
- `analysis/PRG26_9FA9_INCOMING_ATTR.md`

Stable facts:

- `PRG26:$8001` iterates 28 render slots in seven arrays `$0400-$04C3`.
- `$048C,X` indexes first-level selector block `$817F-$819C`.
- `$0400,X` is the selected frame-pointer byte offset.
- descriptor byte 0 is sprite count.
- Y/control bit0 clear: `Y,tile,attribute,X`.
- Y/control bit0 set: `Y,tile,X`, reusing ZP `$10`.
- full records update `$10`; compressed records reuse it unchanged.
- `$0454,X != 0`: `(descriptor_attr & $FC) | full_object_byte`.
- `$04A8,X == 0`: mirrored path, toggles attr `$40` and applies `$F8-X`.
- OAM traversal adds `$C4` per sprite; frame seed adds `$44`.
- OAM-full path executes `PLA; PLA; RTS` and skips the rest of `$8001`.
- descriptor census: 745 unique referenced descriptors, max 27 sprites, max encoded length 96 bytes, 2,310 compressed records.

Native baseline:

- `src/oam_renderer.hpp`
- `src/oam_renderer.cpp`
- `tests/oam_renderer_test.cpp`

## `$9FA9` closure

`$9FA9` requires selector `$10` + frame `$14`.

Established chain:

- 04D: PRG22 `$8745` rejected; its type `$26` uses selectors `$12/$08`.
- 04E1: PRG18 type `$E1` rejected; selector `$10` frames only `$E8/$EA/$EC/$EE`.
- 04E2: direct PRG06/07 selector-`$10` frames do not include `$14`.
- 04E3: PRG06 `$823E-$8251` selects animation `$09` for base Y `$A0-$A7`; `$F28D: 14 08 02` causes `$EF93` to write frame `$14`.
- 04E4: primary type `$08` in slots `$01-$12` routes to `PRG06:$8021`; state `$01` reaches `$823E` and same scheduler iteration can reach `$EF93`.
- 04E5: state `$00` establishes Y `$C0` and exact `-2` vertical motion; state `$01` remains active through `$A0-$A7`.
- 04E6: normal low-type construction gives `$0633=$0645=0`; state `$00` makes first state-1 index `$01`, target `$90`. Normal gameplay `$9FA9` reachability is proven.
- 04F1: renderer order is ascending and `$10` is not initialized at frame/object entry. `$9FA9` begins with three compressed records, so they consume variable inherited shared state rather than a constant default.

Exact path:

```text
normal root type $08
-> $0633=$0645=0
-> state $00 -> target $90
-> Y crosses $A6/$A4/$A2/$A0
-> selector $10 / animation $09
-> $EF93 writes frame $14
-> descriptor $9FA9
-> first three sprites consume inherited ZP $10
```

## Pre-render `$10` provenance checkpoints

### 04F2 — verified IRQ graph preserves `$10`

Primary span `PRG02/PRG03:$9F99-$A526` = 1422 bytes.

Proved:

- no direct ZP/absolute `$10` write encoding occurs in the handler span;
- no reachable indexed/indirect write form can alias `$10`;
- local `$9F5B`, fixed `$E001/$E005`, and fixed `$E2FA/$E30B-$E351` helper closure preserves `$10`;
- IRQ prologue/exit `$E0F5-$E130` preserves `$10`.

Evidence:

- `analysis/IRQ_ZP10_PRESERVATION.md`
- `tools/audit_irq_zp10.py`

### 04F3 — fixed NMI span preserves `$10`

Primary span:

```text
PRG31:$E057-$E365
783 bytes
SHA-256 b0e367bb5971310da3bbd066f54cc3def543e82134f4df6b7b82feef06166176
```

The renderer-reaching NMI body and all in-span helper bodies preserve `$10`. Three external pre-render dependencies were identified: `$ED46`, raw bank `$0C:$89E2`, and `$E7FB`/inline dispatch.

Evidence:

- `analysis/NMI_FIXED_ZP10_PRESERVATION.md`
- `tools/audit_nmi_fixed_zp10.py`

### 04F4 — `$ED46` helper graph preserves `$10`

The initial `$ED46-$EF45` window was expanded within the allowed budget to absorb local control-flow edges `$ED17`, `$EF5C`, and `$EC85`.

Final span:

```text
PRG31:$EC00-$EFFF
1024 bytes
SHA-256 e83c0d832fc23590c0dde2448a9943ef217ada4e4f520d0da0e3f85f863dc797
```

Starting from `$ED46`, the audit proves:

- 323 reachable instruction starts;
- no call/jump/branch leaves the 1 KiB window;
- no reachable dynamic/indexed write exists;
- reachable writes are limited to ZP `$00`, ZP `$1E`, `$0300`, `$2000`, `$2006`, `$2007`.

Therefore the complete `$ED46` graph preserves ZP `$10`.

Evidence:

- `analysis/NMI_ED46_ZP10_PRESERVATION.md`
- `tools/audit_nmi_ed46_zp10.py`

Current provenance boundary:

```text
verified IRQ graph             -> preserves $10
fixed NMI span $E057-$E365    -> preserves $10
$ED46 helper graph             -> preserves $10
raw bank $0C : CPU $89E2      -> unresolved
$E7FB / inline dispatch        -> unresolved
PRG26 renderer                 -> consumes/persists $10 exactly
```

VPP remains **21/100**.

## Repository workflow

Repository: `Hyperbog/CVIII-Decomp`

Working branch: `decompilation`

Primary handoff files:

- `docs/DECOMPILATION_CONTINUITY.md`
- `docs/PROGRESS.md`
- `docs/PROGRESS_METRIC.md`
- `docs/ROM_IDENTITY.md`

Always fetch current file/branch state immediately before editing. Never claim a commit until the branch ref confirms it.

Primary hardware reference: NESdev Wiki, especially VRC6/VRC IRQ/CPU/PPU/APU pages. Hardware docs explain hardware; ROM bytes control game behavior.

## Current next checkpoint

**04F5 — raw bank `$0C:$89E2` pre-render helper only.**

Initial primary span:

```text
raw VRC6 bank $0C
CPU $8800-$8BFF
physical PRG24
1024 bytes
```

Raw bank `$0C` maps CPU `$8000-$9FFF` to physical PRG24. Follow only control flow reachable from CPU `$89E2`. Expand within the 500-5000-byte checkpoint budget if local edges are required to close the same question. Determine whether this NMI-called banked path can write or alias ZP `$10`. Do not analyze `$E7FB` in the same checkpoint.

## User-facing handoff prompt

> Continue the faithful Akumajou Densetsu decomp/recomp in `Hyperbog/CVIII-Decomp` on branch `decompilation`. Read the four primary handoff docs and current branch head. Treat the exact Japanese Mapper-24 ROM as immutable controlling evidence. Work one bounded checkpoint only, normally 500-5000 new ROM bytes and preferably about 1 KiB; expand within that range only to close the same local control-flow question; provide frequent material status updates; preserve exact 6502/VRC6/PPU/APU/interrupt/stack/shared-zero-page semantics; do not invent bounds or initializers; update VPP only under its fixed rubric; commit before reporting. Current next checkpoint: 04F5, audit raw bank `$0C:$89E2` using initial physical PRG24 span `$8800-$8BFF`; do not open `$E7FB` in the same checkpoint.
