# JP0657 — Formal first Stage/Room Data Format VPP decision

**Score decision:** Stage / world / progression increases **0 → 1/20**,
specifically **first of five** `stage/room data formats` subpoints.
Overall Verified Parity Progress increases **28 → 29/100**.
No other VPP point is promoted. All fixed rubric weights and the
historical independent 0508 strict PRG certificate remain unchanged.

The category now has **a reusable, compiled, fully bounded stage source
data model** rather than only the exploratory JP0538 structural atlas:
`JP/recomp/native/enhanced/cviii_room_catalog_0657.c/.h` verifies all 15
original stage groups, 64 middle tables and 135 original leaf
choices, identifies 129 unique roots, partitions **709 four-byte**
and **163 seven-byte** original record groups, checks 16 `$FF`
terminators and the original 7-byte first-field range `$00–$03`.
All 4,421 source bytes across the hierarchy and its record payloads
are accounted in their original physical Mapper24 bank0A addresses,
without embedding any proprietary content. Invalid pointers and
record boundaries fail without changing the output.

The independent `JP/decomp/tools/jp_room_catalog_0657.py` executes the
authentic original **6502 instruction stream at bank0A:$801E–$8046**
for all 135 valid selector triples, verifies full bank SHA-256 and
matches all 135 leaf selections, lengths, record classes and source
roots against compiled native C11. A separate, newly lifted
original bank0A:$8001–$801D and $80D1–$8107 **84-byte connected
room-coordinate/phase prefix** matches all **131,072** original-ROM
6502/compiled-C11 scenarios, including zero/nonzero room-mode
branches, wrapping 16-bit calculation and resulting A/X/Y/C/Z/N/V.
Two independent ROM-free native C11 regression binaries, altered
source rejection, GCC/Clang and sanitizers verify regressions.

This is a **one-point historical stage/room data format architecture
milestone**, not any of these separately-scored categories:

- Remaining **four** stage/room data-format points.
- All four scrolling/room-transition points, all four collision/
  environment-map points, all route/progression and menu/ending points.
- The two stage extraction-tool points, which require a separately
  tested editor-ready resource export format, not only a private ROM
  verifier.
- Natural original Mesen Stage 1 execution coverage and original
  PPU/frame/input/mapper timing parity. This remains OPEN, and
  historical strict PRG certification stays **49,504/262,144**
  (18.8843%), independent 0508 checkpoint and $FB96 frontier.

The JP0538 source atlas already classified the structural bytes:
this checkpoint does not claim new unique strict code/data positions.
The native modules are linked but dormant; live game behavior,
user-visible maps, savestates and authored/modded stages are not
affected. No editor or public mod API is claimed.

**Audit links:** [bounded source and native tests](0657_STAGE_ROOM_NATIVE_CATALOG_AND_COORDINATE.md),
[score CSV](PROGRESS_SCORE.csv), [rubric](../docs/PROGRESS_METRIC.md),
[native evidence ledger](NATIVE_EVIDENCE_LEDGER.json).
