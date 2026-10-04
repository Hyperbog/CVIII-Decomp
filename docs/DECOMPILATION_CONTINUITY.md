# Akumajou Densetsu decomp/recomp continuity playbook

This file is the durable handoff for future ChatGPT conversations working on `Hyperbog/CVIII-Decomp`. Read this file and `docs/PROGRESS.md` before doing new work. The repository must contain enough current state that a new chat can resume without relying on prior conversation history.

## Primary objective

Faithfully reverse engineer the Japanese NES release of **Akumajou Densetsu** into an evidence-accountable decompilation/recompilation that can execute natively on PC. Preserve original behavior first. Modern QoL/mod features are later layers and must not contaminate the faithful baseline.

The original ROM bytes are controlling evidence. Documentation, emulator behavior, names, NSF rips, and hypotheses are secondary. Never modify or commit the source ROM.

## Immutable target identity

- File: `Akumajou Densetsu (Japan).nes`
- Size: `393232` (`0x60010`)
- SHA-256: `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`
- PRG: 256 KiB, CRC32 `BA6BDD6A`
- CHR: 128 KiB, CRC32 `BF15255C`
- PRG+CHR CRC32: `E349AF38`
- Mapper 24 / Konami VRC6a

Run `python tools/analyze_rom.py <rom>` before relying on a local ROM.

## Progress metric

Primary high-level metric: **Verified Parity Progress (VPP)**.

- current score: **21/100**
- rubric: `docs/PROGRESS_METRIC.md`
- machine-readable score: `analysis/PROGRESS_SCORE.csv`
- validator: `tools/progress_score.py`

VPP is evidence-based, not a labor/time estimate and not raw disassembly-byte coverage. Category weights are fixed. Increase the score only when a committed artifact satisfies the rubric; corrections may reduce it. Every checkpoint report must include current VPP and state whether it changed.

If a conservative ROM-byte/code-data coverage ledger is later created, report it as a separate companion metric.

## Non-negotiable fidelity rules

1. Never guess code/data boundaries or routine semantics. Uncertain material stays unresolved.
2. Every translated routine must reconcile instruction-by-instruction to authoritative ROM bytes.
3. Track **physical PRG bank + CPU address**; banked CPU addresses are not globally unique.
4. Model VRC6 bank writes and interrupt-side restoration exactly.
5. Preserve 6502 widths, flags, wrapping, zero-page aliasing, stack behavior, interrupt behavior, and unusual cross-function control flow.
6. Never extend tables merely because following bytes decode plausibly; prove boundaries from consumers/producers/control flow.
7. Do not add defensive host checks absent from the ROM until producer domains are proved.
8. Preserve arithmetic literally where host semantics differ. PRG26 Y/control decoding uses sign-selected carry + `ROR`, not signed division.
9. Preserve non-local returns. `PRG26:$8070` can execute `PLA; PLA; RTS` and return directly past `$8001`.
10. Preserve shared zero-page state. OAM attribute cache `$10` is not initialized at object/descriptor entry and is also used as unrelated gameplay scratch.
11. Keep uncertain names conservative; names must not create false certainty.
12. NSF/M3U are corroborating audio evidence only; ROM bytes remain authoritative.
13. No original ROM bytes are committed to GitHub.
14. Every substantive checkpoint updates `docs/PROGRESS.md`; update this file when methodology, VPP rules, or a fidelity pitfall changes.

## Manageable checkpoint policy

Each user `continue` means **one bounded checkpoint**:

1. choose the narrow question listed as next work;
2. regenerate only the relevant ROM evidence;
3. add/update focused analysis/audit/source artifacts;
4. update `docs/PROGRESS.md` and VPP only if earned;
5. commit;
6. stop and report.

Do not combine unrelated subsystem work in one continuation. If a dependency expands scope, record it for the next checkpoint.

## Cartridge model

Mapper 24 / VRC6a CPU PRG map:

- `$6000-$7FFF`: 8 KiB PRG RAM
- `$8000-$BFFF`: 16 KiB switchable PRG ROM
- `$C000-$DFFF`: 8 KiB switchable PRG ROM
- `$E000-$FFFF`: fixed final 8 KiB PRG bank

Stable fixed-bank facts:

- NMI `$E057`
- RESET `$E00B`
- IRQ `$E0F5`
- `$E2D0` tracks 16 KiB bank in ZP `$23`; `$E2D2` writes VRC6 `$8000`
- `$E2C4` selects `PRG30` at `$C000-$DFFF`
- NMI bank `$0D` call `$8001` = `PRG26:$8001`
- IRQ raw bank `$01` = `PRG02/PRG03`

## IRQ checkpoint

Authoritative IRQ table: `PRG02:$9F01-$9F5A`, 45 states `$00-$2C`. `$9F5B` is code. The old `$9F60` overlap claim was false and must not be restored.

Normal states `$00-$2C`; `$80` is high-bit bypass. Highest explicit chain: `29 -> 2A -> 2B -> 2C`.

IRQ exits differ:

- `$E118`: clears VRC6 IRQ Control `$F001`, then falls through
- `$E11D`: acknowledges `$F002` and restores bank state

See `analysis/PRG02_IRQ_dispatch.md` and `analysis/IRQ_STATE_MACHINE.csv`.

## OAM/sprite checkpoint

Read `analysis/PRG26_SPRITE_FORMAT.md`, `analysis/SPRITE_SET_TABLE.csv`, `analysis/SPRITE_MASTER_TABLES.csv`, `analysis/OAM_OBJECT_FIELDS.csv`, and `analysis/ZP10_OAM_STATE.md` before changing this subsystem.

Stable facts:

- `PRG26:$8001` iterates 28 render-object slots in seven parallel 28-byte arrays `$0400-$04C3`.
- `$048C,X` is a byte offset into first-level block `$817F-$819C`.
- `$0400,X` is a byte offset into the selected frame-pointer window.
- the 15 selectors are windows into five physical master pointer blocks: `$819D-$82F4`, `$8AB0-$8C2D`, `$9545-$9620`, `$9E6D-$9F6C`, `$AAA6-$AC5B`.
- `$16/$18/$1A/$1C` alias `$00/$02/$04/$06` and can select tile `+$80` under `$AD != 0`.
- descriptor byte 0 is count; records are variable length:
  - Y/control bit0 clear: `Y,tile,attribute,X`
  - Y/control bit0 set: `Y,tile,X`, reusing cached final attribute from ZP `$10`
- full records update `$10`; compressed records reuse `$10` unchanged.
- `$9FA9` begins with three compressed records before its first explicit attribute.
- `$0454,X` operation is `(descriptor_attr & $FC) | full_object_byte` when nonzero; do not mask the object byte to two bits.
- `$04A8,X == 0` selects mirrored rendering; mirror toggles attr `$40` and uses `$F8-X` transform.
- OAM traversal adds `$C4` per sprite and frame seed adds `$44`.
- OAM-full path executes `PLA; PLA; RTS`, skipping `$8001` remainder.
- descriptor census: 745 unique referenced descriptors, max 27 sprites, max encoded length 96 bytes, 2,310 compressed attribute-reuse records.

### `$9FA9` reachability work

- checkpoint 04D proved `PRG22:$8745` belongs to type `$26`, whose explicit selector family is `$12/$08`, not `$10`.
- checkpoint 04E1 proved PRG18 type `$E1` starts selector `$10` at frame `$E8/$EC` and can only mutate to `$EA/$EE`; it cannot reach frame `$14`.
- checkpoint 04E2 proved the direct PRG06/07 selector-`$10` setup/helper domain is `$C0,$C2,$C4,$C6,$C8,$CA,$CC,$CE,$D0,$D2,$D4,$D6,$E0,$E4,$F0,$F4,$F6,$F8,$FA,$FC,$FE`; frame `$14` is absent. The only bank-resident literal frame `$14` setup immediately selects `$0E`.

See `analysis/PRG22_8745_OWNER.md`, `analysis/PRG18_E1_SELECTOR10_FRAME.md`, and `analysis/PRG06_SELECTOR10_DIRECT_DOMAIN.md`.

### Native baseline

- `src/oam_renderer.hpp`
- `src/oam_renderer.cpp`
- `tests/oam_renderer_test.cpp`

The structured lift keeps NES RAM explicit and preserves wrapped 8-bit pointer indexing, variable-width descriptors, persistent `$10`, full-byte `$0454` behavior, mirror/tile transforms, clipping, OAM permutation, and the non-local OAM-full effect via an explicit result.

## Repository workflow

Repository: `Hyperbog/CVIII-Decomp`

Working branch: `decompilation`

Primary handoff files:

- `docs/DECOMPILATION_CONTINUITY.md`
- `docs/PROGRESS.md`
- `docs/PROGRESS_METRIC.md`
- `docs/ROM_IDENTITY.md`

Always fetch current file/branch state immediately before editing. Never claim a GitHub change exists until commit/ref is confirmed.

## Documentation policy

Primary hardware reference: NESdev Wiki, especially VRC6, VRC IRQ, VRC6 audio, CPU, PPU, and APU. Hardware docs explain hardware; ROM bytes control game-specific behavior.

## Required behavior in future chats

When the user says `continue`, perform actual ROM analysis and commit **one bounded checkpoint** before replying.

Before a continuation:

1. read this file;
2. read current `docs/PROGRESS.md`, `docs/PROGRESS_METRIC.md`, and `docs/ROM_IDENTITY.md`;
3. inspect current branch head and relevant analysis/source;
4. reverify target ROM identity if available;
5. perform only the listed next checkpoint;
6. update VPP only if the rubric earns points;
7. commit and report exact findings + commit SHA + current VPP.

Never count unresolved work as translated.

## Current next checkpoint

**04E3 — PRG06 transitive frame mutation through shared/fixed helpers only.** Starting from the proven PRG06 selector-`$10` setup paths, inspect only calls into fixed/shared routines that can write or derive `$0400` for the same object. Determine whether any such path can create frame `$14`. Do not expand into unrelated object families or stage logic.

## User-facing handoff prompt

> Continue the faithful Akumajou Densetsu decomp/recomp in `Hyperbog/CVIII-Decomp` on branch `decompilation`. Read `docs/DECOMPILATION_CONTINUITY.md`, `docs/PROGRESS.md`, `docs/PROGRESS_METRIC.md`, and `docs/ROM_IDENTITY.md`, inspect current branch state, and treat the verified Japanese Mapper-24 ROM as immutable controlling evidence. Work one bounded checkpoint only, preserve 6502/VRC6/PPU/APU/interrupt/stack/shared-zero-page semantics exactly, do not invent bounds/table boundaries, update VPP only under its fixed rubric, and commit before reporting. Current next checkpoint: 04E3, trace only transitive fixed/shared helper frame mutations reachable from PRG06 selector-`$10` setup paths and determine whether any can produce frame `$14`.
