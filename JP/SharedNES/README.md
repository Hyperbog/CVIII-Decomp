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

See [`SOURCE_CATALOG.md`](SOURCE_CATALOG.md) for external research provenance and manual index, and [Konami sound-driver family hypotheses](KONAMI_DRIVER_HYPOTHESES.md) for a sourced cross-title comparison queue, explicitly not a proven common engine. Completion progress remains scored by `../analysis/PROGRESS_SCORE.csv`, not this library's adoption.

## Portable FDS and trace research (2026-10-09 expansion)

### FDS/QD file-block catalog
`../tools/nes_fds_catalog.py` is a **read-only structural index** for 65,500-byte FDS sides (optional 16-byte `FDS\x1A` header) and **65,536-byte QD** sides containing CRC words. It checks the original `*NINTENDO-HVC*` disk signature, block 1/2 metadata and declared block 3/4 file pairs; records per-file name, type, load address, size, offset and content SHA-256 only. It also marks potentially hidden block 3/4 pairs beyond the declared file count. It does not emit file data, validate CRC, mount the FDS BIOS or prove any ROM game routine.

```sh
python3 JP/tools/nes_fds_catalog.py /private/game.fds --out /tmp/fds-index.json
python3 JP/tests/test_nes_fds_catalog.py  # 14 synthetic image/format tests
```

### Independent CPU log comparison boundary
`../tools/nes_trace_compare.py` normalizes Nintendulator/nestest **pre-instruction** text and an explicit JSONL record schema. It compares `pc,a,x,y,p,sp`; cycle counts are opt-in, and physical PRG bank is compared **only when both logs supply it**. Flag bits 4/5 are ignored only with `--ignore-virtual-p-bits`, matching the convention documented by the NESdev trace-log discussions. A failed comparison exits nonzero and reports **only the first bounded register mismatches** plus log hashes, never disassembly bytes.

```sh
python3 JP/tools/nes_trace_compare.py /private/reference-nestest.log /private/candidate.jsonl --compare-cycles --out /tmp/trace-diff.json
python3 JP/tests/test_nes_trace_compare.py  # 16 synthetic log tests
```

JSONL rows: `{"pc":"C000","a":"00","x":"00","y":"00","p":"24","sp":"FD","cycles":7,"prg_bank":20}`. Hexadecimal string register values or decimal integer values are accepted; `prg_bank` and `cycles` are optional unless requested. **No original reference ROM execution was run against this tool yet; no CPU/interrupt parity or strict coverage is claimed.** The two tools are reusable across game publishers and mapper families but remain discovery/test infrastructure.

Details and limits: [FDS/trace evidence note](FDS_TRACE_EVIDENCE.md), [reference catalog](SOURCE_CATALOG.md).

### First ROM-audited cross-edition code match

[JP `$E7FB` ↔ US candidate `$E86D` exact 25-byte stack-dispatch routine](JP_US_DISPATCH_EXACT_MATCH.md): **15** identical original 6502 instructions, one US occurrence, plus a 134-byte physically contiguous but not entirely classified exact neighboring interval. Reproducible pinned JP+US tool: [`audit_shared_dispatch_jp_us.py`](../tools/audit_shared_dispatch_jp_us.py); hash-only [report](../analysis/shared_dispatch_jp_us_report.json) and [reusable anchor manifest](JP_US_DISPATCH_ANCHOR.json). **C1 local code equivalence only**, not US MMC5 bank mapping/caller/gameplay proof or additional strict PRG coverage.

### Whole-checkpoint strict-source reuse census (2026-10-09)

[Checkpoint 0501 cross-edition census](JP_0501_CROSS_EDITION_REUSE.md) verifies **31 SHA-pinned regions / 4,364 already-certified original JP PRG code/operand bytes** and locates **1,273 distinct JP source bytes** covered by unique exact 16-byte windows in the US game (29.17%). This is *additional transfer-discovery evidence*, not newly certified ROM coverage or US mapper/execution parity. The [portable matcher](../tools/nes_certified_reuse.py) accepts any pair of supplied NES ROMs plus a strictly hash-pinned source-region manifest; 18 deterministic tests cover collision/overlap/identity handling and an optional original ROM-pair integration.
