# Akumajou Densetsu decomp/recomp continuity playbook

This file is the durable handoff for future ChatGPT conversations working on `Hyperbog/CVIII-Decomp`. Read this file and `docs/PROGRESS.md` before doing new work. The repository must contain enough current state that a new chat can resume without relying on prior conversation history.

## Primary objective

Faithfully reverse engineer the Japanese NES release of **Akumajou Densetsu** into an evidence-accountable decompilation/recompilation that can execute natively on PC. Preserve original behavior first. Modern QoL features, mod APIs, widescreen/high-refresh presentation, replacement assets, scripting, etc. are later layers and must not contaminate the faithful baseline.

The original ROM bytes are controlling evidence. Documentation, emulator behavior, comments, names, NSF rips, and hypotheses are secondary. Never modify the source ROM.

## Immutable target identity

Expected source ROM:

- File: `Akumajou Densetsu (Japan).nes`
- Size: `393232` bytes (`0x60010`)
- Full-file SHA-256: `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`
- Full-file SHA-1: `a0f3b31d4e3b0d2ca2e8a34f91f14ad99a5ad11f`
- PRG: 256 KiB, CRC32 `BA6BDD6A`
- CHR: 128 KiB, CRC32 `BF15255C`
- PRG+CHR CRC32: `E349AF38`
- iNES mapper: 24 / Konami VRC6a

Run `python tools/analyze_rom.py <rom>` before relying on a local ROM.

## Non-negotiable fidelity rules

1. Never guess code/data boundaries or routine semantics. Uncertain material stays address-named and unresolved.
2. Every translated routine must reconcile instruction-by-instruction to authoritative ROM bytes.
3. Track **physical PRG bank + CPU address**. Banked CPU addresses are not globally unique.
4. Model VRC6 bank writes and interrupt-side restoration exactly.
5. Preserve 6502 widths, flags, wrapping, zero-page aliasing, stack behavior, interrupt behavior, and unusual cross-function control flow exactly.
6. Never extend a table merely because following bytes decode plausibly; prove boundaries from consumers/producers/control flow.
7. Do not add defensive host checks absent from the ROM until producer domains are proved.
8. Preserve arithmetic literally where host semantics differ. PRG26 Y/control decoding uses sign-selected carry plus `ROR`, not signed division.
9. Preserve non-local returns. `PRG26:$8070` can execute `PLA; PLA; RTS` and return directly past `$8001`.
10. Preserve persistent renderer state. Sprite attribute cache ZP `$10` is not initialized at object/descriptor entry; compressed records can reuse it immediately.
11. Keep uncertain names conservative; names must not create false certainty.
12. NSF/M3U are corroborating evidence for audio only; ROM bytes remain authoritative.
13. No original ROM bytes are committed to GitHub.
14. Every substantive checkpoint updates `docs/PROGRESS.md`; update this file when methodology or a fidelity pitfall changes.

## Manageable checkpoint policy

Each user `continue` now means **one bounded checkpoint only**:

1. choose one narrow question already listed as next work;
2. regenerate only the relevant ROM evidence;
3. add/update one focused analysis/audit artifact if useful;
4. update progress/continuity;
5. commit;
6. stop and report the checkpoint.

Do not combine unrelated subsystem work in one continuation. If a dependency expands scope, record it for the next checkpoint instead.

## Cartridge model

Mapper 24 / VRC6a CPU PRG map:

- `$6000-$7FFF`: 8 KiB PRG RAM
- `$8000-$BFFF`: 16 KiB switchable PRG ROM
- `$C000-$DFFF`: 8 KiB switchable PRG ROM
- `$E000-$FFFF`: fixed final 8 KiB PRG bank

PRG is analyzed as 32 physical 8 KiB banks `PRG00..PRG31`.

Stable fixed-bank facts:

- NMI `$E057`
- RESET `$E00B`
- IRQ `$E0F5`
- `$E2D0` tracks 16 KiB bank in ZP `$23`; `$E2D2` writes VRC6 `$8000`
- `$E2C4` selects physical `PRG30` at `$C000-$DFFF`
- NMI bank `$0D` call `$8001` = `PRG26:$8001`
- IRQ raw bank `$01` = `PRG02/PRG03`

## IRQ checkpoint

Authoritative IRQ table: `PRG02:$9F01-$9F5A`, 45 states `$00-$2C`. `$9F5B` is code. The old `$9F60` overlap claim was false and must not be restored.

Current producer audit supports normal states `$00-$2C` plus `$80` as high-bit bypass sentinel. Highest explicit chain: `29 -> 2A -> 2B -> 2C`.

IRQ exits remain distinct:

- `$E118`: clears VRC6 IRQ Control `$F001`, then falls through
- `$E11D`: acknowledges via `$F002` and restores bank state

See `analysis/PRG02_IRQ_dispatch.md` and `analysis/IRQ_STATE_MACHINE.csv`.

## OAM/sprite checkpoint

Read `analysis/PRG26_SPRITE_FORMAT.md`, `analysis/SPRITE_SET_TABLE.csv`, and `analysis/OAM_OBJECT_FIELDS.csv` before changing the renderer model.

Stable facts:

- `PRG26:$8001` iterates 28 render-object slots.
- Seven parallel 28-byte arrays occupy `$0400-$04C3`.
- `$048C,X` is a byte offset into first-level pointer block `$817F-$819C`.
- `$16/$18/$1A/$1C` alias `$00/$02/$04/$06` geometry tables and can select tile `+$80` behavior.
- `$0400,X` is a byte offset into the selected frame-pointer table.
- Descriptor byte 0 is sprite count.
- **Records are variable length:** Y/control bit 0 clear = `Y,tile,attribute,X`; bit 0 set = `Y,tile,X` and reuse cached final attribute from ZP `$10`.
- Y/control is arithmetic-right-shifted by the original sign-selected-carry `ROR` sequence.
- Full records update `$10` after attribute override/mirror transform; compressed records reuse `$10` unchanged.
- Descriptor `$9FA9` begins with three compressed records before its first full record; therefore resetting `$10` per descriptor/object is wrong.
- Current audit covers five master frame-pointer blocks and 745 unique descriptors; 2310 records use cached-attribute compression, max 27 sprites/descriptor, max encoded length 96 bytes.
- OAM traversal adds `$C4` per sprite and frame seed adds `$44`.
- OAM-full path performs `PLA; PLA; RTS`, skipping `$8001`'s remainder.

Reproducible audits:

- `tools/analyze_rom.py`
- `tools/audit_irq_dispatch.py`
- `tools/audit_oam_tables.py`
- `tools/audit_sprite_descriptors.py`

## Repository workflow

Repository: `Hyperbog/CVIII-Decomp`

Working branch: `decompilation`

Primary handoff files:

- `docs/DECOMPILATION_CONTINUITY.md`
- `docs/PROGRESS.md`
- `docs/ROM_IDENTITY.md`

Always fetch current file/branch state immediately before editing. Never claim a GitHub change exists until the commit/ref is confirmed.

## Documentation policy

Primary hardware reference: NESdev Wiki, especially VRC6, VRC IRQ, VRC6 audio, CPU, PPU, and APU. Hardware docs explain hardware; ROM bytes control game-specific behavior.

## Required behavior in future chats

When the user says `continue`, perform actual ROM analysis and commit **one bounded checkpoint** before replying.

Before a continuation:

1. read this file;
2. read current `docs/PROGRESS.md` and `docs/ROM_IDENTITY.md`;
3. inspect current branch head and relevant analysis files;
4. reverify target ROM identity if available;
5. perform only the listed next checkpoint;
6. commit and report exact findings + commit SHA.

Never count unresolved work as translated.

## Current next checkpoint

**04B — zero-page `$10` renderer-state lifetime only.** Trace executable reads/writes relevant to the NMI/OAM path and determine what establishes the cached attribute before `$9FA9` can begin with compressed records. Do not expand this checkpoint into general object-array producer analysis.

## User-facing handoff prompt

> Continue the faithful Akumajou Densetsu decomp/recomp in `Hyperbog/CVIII-Decomp` on branch `decompilation`. Read `docs/DECOMPILATION_CONTINUITY.md`, `docs/PROGRESS.md`, and `docs/ROM_IDENTITY.md`, inspect current branch state, and treat the verified Japanese Mapper-24 ROM as immutable controlling evidence. Work one bounded checkpoint only, preserve 6502/VRC6/PPU/APU/interrupt/stack semantics exactly, do not invent bounds/table boundaries, and commit before reporting. Current next checkpoint: 04B, establish the lifetime/initializer contract of the PRG26 cached OAM attribute in zero-page `$10`.
