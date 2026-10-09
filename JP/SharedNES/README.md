# Shared NES/FDS Decomp Evidence Library — pilot

**Purpose:** build a reusable, copyright-conscious ROM research layer for NES and Famicom Disk System games. This directory is a **cross-game tool and evidence contract**, not a new emulator, a claim of code ownership, or a substitute for the JP game-specific certification ledger.

## Implemented (2026-10-09)

The standalone Python stdlib tool [`../tools/nes_reuse.py`](../tools/nes_reuse.py):

1. Identifies iNES 1.0 and NES 2.0 cartridge headers (including trainer offsets, NES2 mapper/submapper, linear and exponent/multiplier PRG/CHR sizes); records SHA-256 for the image, PRG, CHR and each physical 8 KiB PRG bank. Flags ambiguous legacy/dirty headers. Extracts fixed vectors **only** for mapper 0 and mapper 24/26 mappings with known fixed banks. It does not infer CPU bank state for other mappers.
2. Recognizes headered FDS image side geometry and *possible* unheadered 65,500-byte-sided image geometry. It does **not** parse the disk file directory, emulate the BIOS, or treat geometry as proof of identity.
3. Performs all-offset exact 32-byte cross-ROM candidate searches from configurable sampled PRG positions, rejecting trivial/low-entropy windows, reporting multiplicity and compact hashes/offsets rather than copying ROM bytes.
4. Checks user-supplied preanchored code/data regions against SHA-256. For **already justified instruction-aligned code boundaries**, optionally masks only the 16-bit operands of official `JSR abs` and `JMP abs` to discover potential relocation-only equivalents. Zero-page writes, indirect JMP addresses, relative branch offsets, sound data and mapper-register operands are **never** silently masked. Unsupported opcode or truncated instruction rejects that comparison.
5. Uses a deliberately conservative report contract: discovered matches are **candidate evidence**; `strict_new_verified_bytes` remains **0** until a separate game-specific producer/map/callee audit establishes liveness and semantic behavior. Do not equate signature hashes with function equivalence.

## Run

```sh
python3 JP/tools/nes_reuse.py inventory '/private/source_game.nes' --out /tmp/inventory.json
python3 JP/tools/nes_reuse.py compare '/private/source_game.nes' '/private/target_game.nes' --window 32 --stride 256 --out /tmp/candidates.json
python3 JP/tools/nes_reuse.py compare '/private/source_game.nes' '/private/target_game.nes' --manifest JP/SharedNES/EXAMPLE_JP_US_ANCHOR.json --out /tmp/audit.json
python3 JP/tests/test_nes_reuse.py  # ROM-free in CI; private JP+US pair used if present beside test
```

The example anchor is a 32-byte **unclassified exact physical PRG correspondence**, not yet a function. It exists to demonstrate deterministic fingerprint and mapper checks, not to raise coverage.

## Mapper-family adapter (implemented)

`../tools/nes_mapper_family.py` provides an explicit-provenance `BankContext` and physical PRG offset resolution for the 16 KiB switchable, 8 KiB switchable and fixed-last PRG windows of VRC6a/b. It normalizes mapper-26 A0/A1-swapped subregister addresses to mapper-24 chip-coordinate addresses without claiming the game actually wrote those registers. It raises errors on unknown mappers, missing bank-selection provenance and out-of-range banks. `../tests/test_nes_mapper_family.py` supplies nine ROM-free tests, including exhaustive register A0/A1 truth-table checks across 8 high-address pages. These are analytical adapters, **not a full VRC6 mapper emulator** and not an equivalence claim about different games.

## Engineering layers

| Layer | Share across games? | Current evidence | Next gate |
|---|---|---|---|
| 2A03 official instruction/address semantics | Yes within chip variant | CPU/PPU references, trace core and cross-run tests | Run independent `nestest` and blargg timing/dummy-bus suites |
| NES PPU/APU/controller, region timing | Hardware families, differing NTSC/PAL/Dendy | NESdev hardware references and user's EveryNES/NESDoc | PPU pixel/scanline frame goldens and sprite-zero tests |
| VRC6 a/b | Mapper-family adapter | Mapper-24 native implementation; hardware spec notes A0/A1 swap for mapper 26 | Mapper-26 register-address adapter with validation ROM or actual mapper-26 title |
| FDS RAM adapter and BIOS calls | FDS titles specifically | FDS BIOS specification, format and external BIOS revision disassembly configurations | Parse FDS blocks, model BIOS calling ABI separately from hardware; require legally obtained BIOS for real tests |
| Konami tools/code families | Unknown until compared | Initial JP↔US Castlevania III candidate matcher | User-provided legally accessible Konami ROMs, auditable code-region anchors and call/dataflow graphs |
| Gameplay, maps, AI and sounds | Game/engine-specific | Only conditional JP Castlevania evidence | Prove each execution/bank/data producer; library can *suggest* labels but not certify |

## Evidence ladder / confidence policy

- **S0 — source located:** archived manual, open-source implementation, forum, community interview. Keep URL, author, date/version and corrections. Not authoritative for a game.
- **S1 — hardware behavior cross-checked:** independent, reputable hardware specification or dedicated test ROM confirms a generic CPU/mapper/PPU behavior. Do not infer game liveness.
- **C0 — machine-detected byte coincidence:** same bytes or masked opcode signature. Might be data or coincidental or from different runtime contexts.
- **C1 — structurally compatible code:** boundary, control flow, operands and call/data graph checked against original game ROM. A shared routine is still not proven live.
- **G1 — target ROM-proven path:** target game establishes correct bank mapping, callers, inputs/producer domain, indirect targets, write/read side effects and full instruction/data bytes; manifest may be promoted under the game's strict ledger.
- **G2 — runtime parity:** independent reference emulator/console traces compare CPU, memory, PPU, mapper and (where relevant) audio, with exact tested conditions.

Different confidence dimensions are not interchangeable. In particular **S1+C0 is not G1**. An exact routine fingerprint may save rediscovery, but must be checked for caller, bank, RAM and register conventions in *each target*.

## Copyright and provenance policy

- Keep ROM/BIOS/disk files **outside Git**. Reports contain only SHA-256 hashes, offsets, counts and small derived metadata. No lossless ROM bank dumps or program listings.
- Source code, historical development kits and disassemblies found online have **independent licenses/permissions**. A publicly readable download is not necessarily permission to incorporate its code into a modern port.
- Open emulator code may be inspected for technical understanding; **do not copy GPL/LGPL implementation code into a differently licensed port** without legal/license review. Clean-room examples can be considered subject to their licenses.
- Archive scans and forums can contain inaccuracies; log corrections and verify against NESdev test suites and each game's original bytes.
- Track Nintendo FDS BIOS functionality separately from Konami game runtime. The original FDS BIOS is Nintendo code, not a universal cartridge-ROM library.

See [`SOURCE_CATALOG.md`](SOURCE_CATALOG.md) for external research provenance and manual index. Completion progress remains scored by `../analysis/PROGRESS_SCORE.csv`, not this library's adoption.
