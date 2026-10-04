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
5. Preserve 6502 widths, flags, wrapping, zero-page aliasing, indirect addressing, stack behavior, interrupt behavior, and self-modifying/data-driven control flow exactly.
6. Treat NMI and IRQ as first-class control-flow roots. Preserve interrupt-side bank changes and restoration behavior.
7. Do not assume code and data are disjoint. `PRG02:$9F60` is already proven to be both the high byte of IRQ table entry `$2F` and the `A5` opcode of executable code beginning at `$9F60`.
8. Classify code, tables, text, compressed assets, level/object data, graphics metadata, music/SFX data, padding, and overlaps conservatively before assigning coverage.
9. Neutral names such as `sub_prg31_E183` are preferred until behavior is established. Names must not imply certainty.
10. NSF/M3U files are corroborating evidence for audio only; the retail ROM remains authoritative.
11. External docs may explain hardware, but never override observed ROM behavior.
12. No original ROM bytes are committed to GitHub. Repository artifacts must be derived analysis/source only.
13. Every substantive batch ends by updating `docs/PROGRESS.md` and this file when methodology or important pitfalls change.

## Cartridge model that must be respected

Mapper 24 / VRC6a CPU PRG map:

- `$6000-$7FFF`: 8 KiB PRG RAM
- `$8000-$BFFF`: 16 KiB switchable PRG ROM
- `$C000-$DFFF`: 8 KiB switchable PRG ROM
- `$E000-$FFFF`: fixed final 8 KiB PRG bank

For this 256 KiB PRG ROM, analysis uses 32 physical 8 KiB banks: `PRG00` through `PRG31`.

Initial fixed-bank analysis proved:

- NMI vector: `$E057`
- RESET vector: `$E00B`
- IRQ vector: `$E0F5`
- `PRG31:$E2D0` stores A in zero-page `$23`; `PRG31:$E2D2` writes A to `$8000`, selecting the VRC6 16 KiB window.
- `PRG31:$E2C4` loads `$1E` and writes it to `$C000`, selecting physical 8 KiB `PRG30` into `$C000-$DFFF` during boot.

The NMI path selects 16 KiB bank `$0D` and calls `$8001`, proving that target is `PRG26:$8001`. The IRQ path raw-selects bank `$01`, proving its `$9F01` dispatch table is in physical `PRG02` and its `$A000+` targets are in physical `PRG03`.

These bank-switch helpers and interrupt paths are foundational for later control-flow resolution.

## Critical discovered pitfall: overlapping code/data

`analysis/PRG02_IRQ_dispatch.md` documents an exact overlap:

- IRQ pointer entry `$2F` reads low byte `$26` at `$9F5F` and high byte `$A5` at `$9F60`, producing target `$A526`.
- `$9F60` simultaneously begins executable code `A5 7A` (`LDA $7A`).

Any coverage ledger, source representation, or extraction tooling must support one physical byte having multiple semantic roles. Do not force a one-byte/one-category partition and do not “fix” the overlap by moving either boundary.

## Working method

For each batch:

1. Reverify source identity.
2. Extract the physical PRG bank(s) involved.
3. Generate fresh disassembly from the ROM for the exact region.
4. Trace entry paths, branches, calls, indirect jumps, VRC6 bank writes, RAM/ZP dependencies, PPU/APU accesses, and interrupt context.
5. Classify code/data/overlap conservatively.
6. Add address-stable labels and comments to derived analysis files.
7. Translate only behavior directly justified by bytes. Keep uncertain work in analysis/staging and uncounted.
8. Add or update tests/tools that make findings reproducible.
9. Update `docs/PROGRESS.md` with exact addresses/banks, what was proved, unresolved dependencies, and the next high-value target.
10. Commit substantive work before reporting completion of the batch.

Do not stop at one blocker; record it and move to an independent region.

## Repository workflow

Repository: `Hyperbog/CVIII-Decomp`

Working branch: `decompilation`

Primary continuity: `docs/DECOMPILATION_CONTINUITY.md`

Progress ledger: `docs/PROGRESS.md`

ROM identity/bank ledger: `docs/ROM_IDENTITY.md`

Reproducible analysis tool: `tools/analyze_rom.py`

Always fetch current files/branch state before editing. Never claim a repository change exists until GitHub confirms it.

## Documentation policy

Primary hardware reference: NESdev Wiki, especially VRC6, VRC6 audio, CPU, PPU, APU, and mapper documentation. Hardware documentation is explanatory evidence; ROM bytes remain controlling.

When external documentation materially resolves an ambiguity, record the fact and source in `docs/PROGRESS.md` or adjacent source comments so the reasoning survives chat turnover.

## Required behavior in future chats

When the user says `continue`, `resume`, `keep going`, or equivalent, perform actual ROM analysis and commit substantive work before replying. Do not merely describe intended work.

Before each continuation:

1. Read this file.
2. Read current `docs/PROGRESS.md` and `docs/ROM_IDENTITY.md`.
3. Inspect the current `decompilation` branch head and relevant analysis/source files.
4. Reverify ROM identity if the ROM is available in the runtime.
5. Regenerate disassembly for the next region directly from the ROM.
6. Analyze, verify, commit, then report exact progress and unresolved dependencies.

Never claim a GitHub change exists until the connector confirms the commit/ref. Never count an unresolved byte/routine as translated.

## User-facing handoff prompt

> Continue the faithful Akumajou Densetsu decomp/recomp in `Hyperbog/CVIII-Decomp` on branch `decompilation`. First read `docs/DECOMPILATION_CONTINUITY.md`, `docs/PROGRESS.md`, and `docs/ROM_IDENTITY.md`, then inspect the branch head and current analysis/source. Treat the verified Japanese Mapper-24 ROM as immutable controlling evidence. Track physical PRG bank plus CPU address, regenerate disassembly directly from the ROM for every region, preserve 6502/VRC6/PPU/APU/interrupt semantics exactly, support overlapping code/data such as `PRG02:$9F60`, do not guess, and keep uncertain work uncounted. Perform substantive analysis and commit it before reporting progress.

Update this continuity file whenever a methodology change, newly proven architectural fact, or discovered pitfall would materially help the next conversation preserve fidelity.
