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
- PRG+CHR SHA-1: `beb7e005bcbac031ce61613fa47df24ad151e9ab`
- iNES mapper: 24 / Konami VRC6a

Run `python tools/analyze_rom.py <rom>` before relying on a local ROM. Do not continue against a mismatched dump without explicitly documenting the new target.

## Non-negotiable fidelity rules

1. Never guess code/data boundaries or routine semantics. Uncertain material stays address-named and unresolved.
2. Every translated routine must be reconcilable instruction-by-instruction to the authoritative ROM bytes.
3. Track **physical PRG bank + CPU address**. `$8000` is not globally unique on a banked cartridge.
4. Model VRC6 bank writes exactly. Do not flatten banked calls until the active bank is proven for that path.
5. Preserve 6502 widths, flags, wrapping, zero-page aliasing, indirect addressing, stack behavior, interrupt behavior, and unusual cross-function stack/control flow exactly.
6. Treat NMI and IRQ as first-class control-flow roots. Preserve interrupt-side bank changes and restoration behavior.
7. Never extend a table merely because following bytes also decode as plausible addresses. Boundaries require consumer/producer/control-flow evidence.
8. Do not add defensive host checks absent from the ROM until the producer domain is proved. This currently applies to the `$048C` sprite-set selector.
9. Preserve arithmetic literally where host language semantics differ. Example: the OAM Y-delta path uses sign-selected carry plus `ROR`, not signed division; negative odd values differ from C/C++ truncation toward zero.
10. Preserve non-local returns/shared stack behavior. `PRG26:$8070` can execute `PLA; PLA; RTS` when OAM fills, discarding its own return and returning directly to `$8001`'s caller.
11. Classify code, tables, text, compressed assets, level/object data, graphics metadata, music/SFX data, padding, and any proven overlaps conservatively before assigning coverage.
12. Neutral names are preferred until behavior is established. Names must not create false certainty.
13. NSF/M3U files are corroborating evidence for audio only; the retail ROM remains authoritative.
14. External docs may explain hardware, but never override observed ROM behavior.
15. No original ROM bytes are committed to GitHub. Repository artifacts must be derived analysis/source only.
16. Every substantive batch ends by updating `docs/PROGRESS.md` and this file when methodology or important pitfalls change.

## Cartridge model

Mapper 24 / VRC6a CPU PRG map:

- `$6000-$7FFF`: 8 KiB PRG RAM
- `$8000-$BFFF`: 16 KiB switchable PRG ROM
- `$C000-$DFFF`: 8 KiB switchable PRG ROM
- `$E000-$FFFF`: fixed final 8 KiB PRG bank

For this 256 KiB PRG ROM, analysis uses 32 physical 8 KiB banks: `PRG00` through `PRG31`.

Initial fixed-bank facts:

- NMI `$E057`
- RESET `$E00B`
- IRQ `$E0F5`
- `$E2D0` tracks 16 KiB bank in ZP `$23`; `$E2D2` writes VRC6 `$8000`
- `$E2C4` writes `$1E` to VRC6 `$C000`, selecting physical `PRG30`
- NMI bank `$0D` call `$8001` = `PRG26:$8001`
- IRQ raw bank `$01` = `PRG02/PRG03`

## IRQ checkpoint

Authoritative IRQ table is `PRG02:$9F01-$9F5A`, 45 entries, states `$00-$2C`. `$9F5B` is code. The old `$9F60` overlap claim was false and must not be restored.

Current producer audit supports normal active states `$00-$2C` plus `$80` as a high-bit bypass sentinel. The highest explicit chain is `29 -> 2A -> 2B -> 2C`.

IRQ exits remain semantically distinct:

- `$E118`: clears VRC6 IRQ Control `$F001`, then falls through
- `$E11D`: acknowledges via `$F002` and restores bank state

See `analysis/PRG02_IRQ_dispatch.md` and `analysis/IRQ_STATE_MACHINE.csv`.

## OAM/sprite checkpoint

Read `analysis/PRG26_SPRITE_FORMAT.md`, `analysis/SPRITE_SET_TABLE.csv`, and `analysis/OAM_OBJECT_FIELDS.csv` before modifying the renderer model.

Stable facts:

- `PRG26:$8001` iterates 28 render-object slots.
- Seven parallel 28-byte arrays occupy `$0400-$04C3` and feed `$8070`.
- `$048C,X` is a byte offset into the canonical first-level pointer block `$817F-$819C`.
- Canonical selectors are represented by table offsets `$00,$02,...,$1C`; whole-ROM producer closure is still pending, so do not invent a bounds check.
- `$16/$18/$1A/$1C` alias the same second-level geometry tables as `$00/$02/$04/$06`.
- Under the encoded `$AD != 0` path, helper `$8172` adds `$80` to the tile byte for selectors `>= $16`.
- `$0400,X` is another byte offset into the selected second-level pointer table.
- Final sprite descriptor begins with count, then four-byte records: Y delta, tile, attribute, X delta.
- `$0454,X` can replace attribute low two bits; mirrored path also toggles attribute bit `$40`.
- `$04A8,X == 0` selects the mirrored path.
- OAM traversal adds `$C4` to byte offset per sprite; frame seed adds `$44`.
- When all 64 OAM slots are consumed, `$8070` executes `PLA; PLA; RTS`, causing a non-local early return past `$8001`'s remainder.

Do not simplify any of those behaviors during the faithful baseline.

## Working method

For each batch:

1. Reverify source identity.
2. Extract the physical PRG bank(s) involved.
3. Generate fresh disassembly from the ROM for the exact region.
4. Trace entry paths, branches, calls, indirect jumps, VRC6 bank writes, RAM/ZP dependencies, PPU/APU accesses, and interrupt context.
5. Classify code/data/table boundaries conservatively and record evidence for extents.
6. Reconcile producer domains before adding host-side validation or bounds checks.
7. Add address-stable labels and machine-readable ledgers when useful.
8. Translate only behavior directly justified by bytes. Keep uncertain work in analysis/staging and uncounted.
9. Add/update reproducible audit tools.
10. Update `docs/PROGRESS.md`, commit substantive work, then report exact findings and commit SHA.

Do not stop at one blocker; record it and move to an independent region.

## Repository workflow

Repository: `Hyperbog/CVIII-Decomp`

Working branch: `decompilation`

Primary continuity: `docs/DECOMPILATION_CONTINUITY.md`

Progress ledger: `docs/PROGRESS.md`

ROM identity: `docs/ROM_IDENTITY.md`

Current audits:

- `tools/analyze_rom.py`
- `tools/audit_irq_dispatch.py`
- `tools/audit_oam_tables.py`

Always fetch current files/branch state immediately before editing. Never claim a repository change exists until GitHub confirms it.

## Documentation policy

Primary hardware reference: NESdev Wiki, especially VRC6, VRC IRQ, VRC6 audio, CPU, PPU, APU, and mapper documentation. Hardware documentation is explanatory evidence; ROM bytes remain controlling.

When external documentation materially resolves an ambiguity, record the fact/source in `docs/PROGRESS.md` or adjacent analysis/source comments so the reasoning survives chat turnover.

## Required behavior in future chats

When the user says `continue`, `resume`, `keep going`, or equivalent, perform actual ROM analysis and commit substantive work before replying.

Before each continuation:

1. Read this file.
2. Read current `docs/PROGRESS.md` and `docs/ROM_IDENTITY.md`.
3. Inspect current branch head and relevant analysis/source files.
4. Reverify ROM identity if available.
5. Regenerate disassembly for the next region directly from the ROM.
6. Analyze, verify, commit, then report exact progress and unresolved dependencies.

Never count unresolved work as translated.

## User-facing handoff prompt

> Continue the faithful Akumajou Densetsu decomp/recomp in `Hyperbog/CVIII-Decomp` on branch `decompilation`. First read `docs/DECOMPILATION_CONTINUITY.md`, `docs/PROGRESS.md`, and `docs/ROM_IDENTITY.md`, then inspect the branch head and current analysis/source. Treat the verified Japanese Mapper-24 ROM as immutable controlling evidence. Track physical PRG bank plus CPU address, regenerate disassembly directly from the ROM, preserve 6502/VRC6/PPU/APU/interrupt and stack semantics exactly, do not guess table boundaries or add unproved bounds checks, and keep uncertain work uncounted. Preserve the IRQ table boundary `$9F01-$9F5A` and the PRG26 OAM non-local `PLA; PLA; RTS` behavior. Perform substantive analysis and commit it before reporting progress.

Update this continuity file whenever a methodology change, corrected hypothesis, newly proven architectural fact, or discovered pitfall would materially help the next conversation preserve fidelity.
