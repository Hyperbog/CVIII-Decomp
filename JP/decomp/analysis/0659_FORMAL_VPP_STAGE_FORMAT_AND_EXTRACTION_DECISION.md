# JP0659 — Formal two-subpoint Stage/world VPP decision

**Decision:** Under the repository's existing immutable VPP rubric,
Stage / world / progression advances **1 → 3 of 20**:
one more `stage/room data formats` point (now **2/5**) and
one `reproducible stage-data extraction tooling` point
(now **1/2**). **VPP 29 → 31/100.**
No category weight or unrelated source credit is changed.

## Stage/room format second of five (distinct from JP0657)

JP0657 earned the *first* format point for authentic raw0A's
15/64/135 hierarchical pointer catalog and 709×4/163×7 record
source geometry. The new JP0659 format is a **separate physically
banked stream consumer**:

- Original Japanese **raw0A:$B7F7–$B872**,
  124 authenticated instruction/operand bytes, uses original
  $07A0 stage resource selection and exact fixed-$FB96
  raw0A→raw0E→raw0A mapper-readable transactions.
- All **five original PRG0E resource streams** at
  $BE8B–$BF39, exactly 175 contiguous authenticated bytes,
  20 header bytes + **30 five-byte record instances** +
  five FF terminators. All five positional fields have
  **original source-proven RAM destinations**, not guessed
  modern object labels.
- Executable C11 native source-consumer, not a static source
  index. **1,280/1,280** real original-opcode 6502 versus
  compiled C11 state comparisons pass:
  **879,360 source opcode steps, 2,293,760 nonstack RAM bytes,
  47,360 raw0E reads and 94,720 precise mapper register writes**.
  Both original flags and full mapped-bank sequence agree.
- Additional **1,280 ROM-free full native C11** invented-source
  tests with variable record counts and terminating/ordinary
  FF differentiation; error/rejection gates and Clang
  sanitizers pass.

This closes a reusable **second stage-source format**,
not a live rendered room, camera-scrolling, 2A03 cycle trace,
observed emulator-liveness proof or complete loader producer
domain. Remaining **three** stage/room format points stay OPEN.

## Stage extraction tooling first of two (independently testable)

`jp_room_resources_0659.py` accepts only the SHA-locked original
Japanese cartridge, identifies physically exact 175 bytes,
extracts five streams/30 records to a private, editor-ready
versioned JSON with stable IDs, physical source positions,
raw positional fields and source-verified RAM output destinations,
then validates and re-encodes an unmodified export to **the exact
175 original bytes and hash**. A fully synthetic source-bank
roundtrip and **7 input-corruption rejection types** are
run without ROM assets on public CI. Edited resource blocks
can be packed locally without embedding retail data in GitHub,
but **no live mod, ROM patch, editor GUI or commercial
artwork redistribution is claimed**.

The second extraction-tool point remains OPEN for the other
original stage-data sources, CHR/tilemaps, integrated authoring,
and stable runtime mod interfaces. No category of claimed
actual gameplay parity is incremented.

## Strict PRG reconciliation

The original-source **124 code + 175 data = 299 physically mapped
bytes** are newly translated/typed in this bounded unit,
but they are already at least structurally covered in
historical bank-0A/0E source atlases. The case matrix is a
conditional original opcode replay with synthetic RAM/PC
entry, not an independently captured natural MesenCE
playthrough. **Zero strict PRG bytes are promoted**.

Strict historical verified PRG stays **49,504 / 262,144
(18.8843%)**; original semantic checkpoint stays **0508**;
fixed PRG31 frontier stays **$FB96**. R-001/R-002 remain
OPEN; no score point for original gameplay scrolling,
mapper/PPU cycle parity or pixel output.

Evidence: [JP0659 full ROM/native tests and reconstruction](0659_ORIGINAL_BANKED_ROOM_OBJECTS_AND_STAGE_EXTRACTOR.md),
[fixed rubric](../docs/PROGRESS_METRIC.md),
[score CSV](PROGRESS_SCORE.csv),
[evidence ledger](NATIVE_EVIDENCE_LEDGER.json).
