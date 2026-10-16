# 09 — Whole-PRG Atlases, JP↔US Matching and Confidence Boundaries

**Status:** REPRODUCIBLE STRUCTURAL BASELINE; live semantics separate. Evidence: [whole-PRG focus](../analysis/WHOLE_PRG_FOCUS_SUMMARY.md), [exact matcher](../analysis/JP_US_EXACT_MATCH_SUMMARY.md), [normalized matcher](../analysis/JP_US_NORMALIZED_MATCH_SUMMARY.md), [policy](../docs/ACCELERATION_POLICY.md).

## Why the generated atlas exists

The original game mixes executable 6502 instructions, compact data and executable-looking pointer words in switchable physical PRG banks. A raw disassembler that linearizes every bank as code **cannot** prove executable status. To avoid repeatedly scanning narrow windows, tools index **all 262,144 PRG bytes**, but preserve candidate-vs-verified separation.

The whole-ROM candidate tool records about **186,258 official-opcode patterns**, **110,127 control-flow candidates**, **87,686 memory-access candidates**, **17,841 ZP-write candidates**, and 35 raw `JSR $E7FB` patterns. These are *byte-pattern counts with false positives*, not functions or verified instructions. A companion query utility extracts candidate RAM writers, JSR targets and banked xrefs. [Whole PRG atlas policy](../docs/WHOLE_PRG_ATLAS.md).

## Matching two regional cartridge editions

An exact unique 32-byte-anchor matcher maps **115,865 JP PRG bytes (44.1990%)** to unique US PRG locations. A second relocation-normalized 16-instruction signature matcher increases exact-or-normalized candidate coverage to **149,607 bytes (57.0705%)**, with 13,232/13,232 calibration matches agreeing and zero calibration disagreements. [Normalized report](../analysis/JP_US_NORMALIZED_MATCH_SUMMARY.md).

Normalization masks relocation-oriented branch/call/ROM targets but retains opcode, immediate and RAM/IO semantics. A high-confidence structural match is a **research hint**, not proof that US and JP have the same gameplay semantics, mapper, sound chip or actual execution reachability. Regional code changes and relocation/duplicated instructions remain possible.

## Classification ladder and counts

`RAW / CANDIDATE → STRUCTURALLY LIKELY → JP-VERIFIED BYTE/CODE/DATA → PRODUCER/LIVENESS VERIFIED → NATIVE ALGORITHM TESTED → TRACE/PARITY VERIFIED`.

Strict PRG coverage is only the unique physically-tagged bytes promoted with complete operand and table dependencies; no double-counting when revisiting known routines. Store exact manifest hashes at each checkpoint. Keep the generated **lossless** whole-bank `.byte` corpus local; do not commit a surrogate copy of the copyrighted ROM. The atlas tools and non-lossless derived indexes can be committed.

## What the matcher is for

Rapidly propose function boundaries, likely player/AI/collision/map subsystem owners and register-field meanings. Then verify JP bank selection, 6502 instruction starts, producer index domains and table/handler semantics independently before allocating semantic coverage or native parity credit. Use the archive chapters as the human-readable endpoint of that verified evidence.

## JP0654 — Music rip provenance is secondary structural evidence

[JP0654](../analysis/0654_ORIGINAL_JP_NSF_ROM_CROSSWALK.md)
fully crosswalks the 53,248-byte Japanese NSF audio rip payload against
the original Japanese cartridge physical PRG. The canonical 13-source-bank
mapping is original 4KiB PRG [16..23, 48..50, 14..15], of which 11 banks
are byte-exact, with only two bounded rip-edit regions (784 bytes total).
The 52,464 untouched bytes support source/offset navigation, not an
execution trace. In particular $A000–$A2FF of the original sound-stream
pool is replaced by the NSF-specific program, so the rip cannot replace
the complete original sound byte-source atlas. Never map NSF virtual
4KiB $5FF8–$5FFF banks to VRC6 cartridge 16KiB PRG selection.
The complete original-JP ROM remains the only byte authority; no
novel strict ROM-byte or gameplay-parity credits are earned.

