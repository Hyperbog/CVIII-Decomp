# Whole-PRG atlas and large-sweep workflow

This document defines the high-throughput static-analysis layer for the Akumajou Densetsu JP decomp/recomp.

## Purpose

The project no longer needs to rediscover basic byte/xref information in 1-5 KiB windows. `tools/build_whole_prg_atlas.py` performs an aggressive sweep of the complete 256 KiB PRG ROM and generates a local analysis corpus in one pass.

The sweep is an **accelerator**, not a code/data oracle. Candidate decoding begins at every physical byte offset, so tables and graphics/data can look like legal 6502 instructions. Nothing from the atlas becomes verified code merely because it decodes.

Authority remains:

1. Japanese ROM bytes / observed JP execution;
2. reproducible semantic audits and parity tests;
3. NES/VRC6 hardware constraints;
4. generated atlas, external disassemblies and other hypothesis sources.

## Generated local corpus

Run:

```text
python tools/build_whole_prg_atlas.py <Akumajou Densetsu (Japan).nes> <output-dir>
```

The generator verifies ROM SHA-256 before producing anything.

It emits:

- `banks/prg00.asm` ... `banks/prg31.asm`: lossless per-physical-bank byte references with mapping annotations and candidate control-flow comments;
- `control_flow_candidates.tsv`: aggressive candidate branch/JSR/JMP/return index;
- `memory_access_candidates.tsv`: aggressive candidate RAM/IO/ROM access index;
- `zp_write_candidates.tsv`: zero-page write/RMW shortlist including indexed forms;
- `e7fb_call_candidates.tsv`: every exact `20 FB E7` byte-pattern location;
- focused `$10`, `$18`, `$2C`, `$68` candidate indexes;
- `manifest.json`: bank hashes, vectors and aggregate counts;
- `MASTER_REFERENCE.txt`: compact high-value text reference for review/search.

The full local corpus is intentionally **not committed**, because the lossless bank listings would be equivalent to committing the copyrighted ROM. The generator and compact non-lossless derived indexes are durable in Git; any session can reproduce the full corpus from the authoritative Project ROM in seconds.

## Current generation fingerprint

Authoritative ROM:

```text
SHA-256 958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
PRG      262144 bytes / 32 physical 8 KiB banks
```

Initial whole-PRG sweep totals:

```text
official-opcode candidates     186258
control-flow candidates        110127
memory-access candidates        87686
zero-page write candidates      17841
raw JSR $E7FB byte patterns        35
```

Focused candidate-reference counts:

```text
$10  534
$18  311
$2C  119
$68  185
```

These are raw candidate counts, **not verified instruction counts**.

The complete generated local set from the initial run had deterministic set digest:

```text
f0eb130043a8fff1a44bfa3da4504592e6e1d124c54ad26d86ed719d8e729291
```

`MASTER_REFERENCE.txt` SHA-256:

```text
813b9da1fb3a43709595f5c75e8777cb60e91d816574d3475f6d1ad9389eaf65
```

## Mapping representation

Physical identity is primary. For non-fixed banks the atlas records:

- the project's canonical 16 KiB raw-bank view for PRG00-PRG29;
- a `$C000-$DFFF` candidate view that remains mapper-state dependent.

PRG31 is recorded as the fixed `$E000-$FFFF` bank.

A `$C000` candidate address is never evidence that the bank was actually selected there. Mapper state must still be proven before a semantic traversal follows the edge.

## Querying without re-decoding the ROM

After generating the local corpus:

```text
python tools/query_whole_prg_atlas.py <atlas-dir> ram '$2C'
python tools/query_whole_prg_atlas.py <atlas-dir> ram '$2C' --writes-only
python tools/query_whole_prg_atlas.py <atlas-dir> ram '$68'
python tools/query_whole_prg_atlas.py <atlas-dir> jsr '$E7FB'
python tools/query_whole_prg_atlas.py <atlas-dir> e7fb
python tools/query_whole_prg_atlas.py <atlas-dir> bank 31
```

This makes whole-ROM producer/xref enumeration a query instead of repeated manual byte-window inspection.

## Large-sweep policy

Discovery and verification are now explicitly separated.

### Discovery sweep

May cover an entire 8 KiB bank, multiple banks, or the full 256 KiB PRG in one automated pass. Discovery results are provisional and may include false-positive decodes.

### Semantic promotion

Only code/data actually justified by control flow, producer domains, mapper context, parser semantics, runtime evidence or another explicit proof becomes verified coverage. Exact instruction/operand bytes are still tracked and prior overlaps are subtracted.

Therefore the project can perform **large discovery sweeps while retaining small, auditable evidence promotions**.

## Workflow integration

For each future semantic checkpoint:

1. query the whole-PRG atlas first;
2. use external US symbols/CDL/Ghidra as additional locators when useful;
3. identify candidate routines/tables/writers globally;
4. reconstruct the actual JP control/producer domain;
5. prove mapper state for switchable targets;
6. promote only ROM-backed semantic bytes;
7. run the checkpoint audit and update recovery state last.

When a new high-value RAM byte or dispatch idiom becomes important, extend the generator/query layer rather than repeatedly hand-searching the ROM.

## Next acceleration layers

The atlas is the base for:

- normalized JP<->US routine fingerprint matching;
- durable RAM-symbol candidate maps with confidence/evidence tags;
- automatic inline-dispatch table discovery;
- CDL/execution-trace overlays;
- static cross-bank CFG generation;
- later CPU/bank/interrupt parity traces.

Those layers must preserve the same rule: acceleration may propose; JP-ROM evidence promotes.

## JP0627 — Lossless private bank-addressed reference (separate from speculative atlas)

[JP0627 evidence and reproduction](../analysis/0627_COMPLETE_PRIVATE_ASM_REFERENCE.md)
provides a deterministic original-ROM-authenticated generator
[build_private_asm_reference_0627.py](../tools/build_private_asm_reference_0627.py)
with PRG00–31 and CHR00–15 physical 8 KiB bank listings, ROM.asm,
manifest with per-bank SHA-256, and physical-offset navigation TSV.
It re-parses its complete assembly-format .byte/.word output to prove
**393,232/393,232 exact original retail-ROM bytes**, including the iNES
header, without pretending all PRG bytes are executed instructions.
The reference specifically identifies the three fixed-bank hardware
vectors (NMI $E057, Reset $E00B, IRQ/BRK $E0F5) and distinguishes fixed
PRG31 CPU addresses from switchable mapper-dependent physical offsets.

**Division of labor:** JP0627 is the safe private, bank-addressed
*byte/reference* layer; this atlas remains the provisional whole-PRG
*discovery* layer; the existing 0529/0538 symbolic bank sources and
verified checkpoint audits remain the *authenticated code/data lift*
and semantic-certification layer. New candidate findings must first
be reconciled with original CPU/mapper state before adding mnemonic
annotations to a verified source. Do not commit JP0627-generated
ROM-equivalent ASM files. ROM-free tests run in Linux/Windows CI;
original-ROM roundtrip was successfully executed locally. Strict
49,504/262,144 PRG, VPP27, checkpoint0508, frontier $FB96 unchanged.
