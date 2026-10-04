# Akumajou Densetsu decomp/recomp continuity playbook

This is the durable handoff for `Hyperbog/CVIII-Decomp`. Read this file, `docs/PROGRESS.md`, `docs/PROGRESS_METRIC.md`, and `docs/ROM_IDENTITY.md` before new work.

## Objective and controlling evidence

Faithfully reverse engineer the Japanese NES release of **Akumajou Densetsu** into an evidence-accountable native PC decompilation/recompilation. Preserve original behavior first; QoL/mod features come later.

ROM bytes are controlling evidence. Hardware documentation, public disassemblies, emulator behavior, NSF/M3U data, names, and hypotheses are secondary. Never modify or commit the source ROM.

Target:

- size `393232` (`0x60010`)
- SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`
- PRG 256 KiB, CRC32 `BA6BDD6A`
- CHR 128 KiB, CRC32 `BF15255C`
- Mapper 24 / Konami VRC6a

## Progress / checkpoint policy

Primary metric: **VPP = 21/100**. It is evidence-based, not a labor estimate or raw-byte percentage.

Each user `continue` means one bounded checkpoint:

- **500-5000 new ROM bytes**, now preferably using the upper half of the range when one dependency can be closed coherently;
- expand only to close the same question;
- never silently exceed the selected budget;
- report material findings frequently;
- add reproducible evidence/audit artifacts;
- update progress/handoff and VPP only if earned;
- commit and confirm the branch head before reporting.

## Fidelity rules

1. Never guess code/data boundaries, producer domains, or semantics.
2. Track physical PRG bank + CPU address.
3. Preserve 6502 widths, flags, wrapping, stack/interrupt and shared-zero-page behavior.
4. Preserve VRC6 bank/IRQ semantics exactly.
5. Never extend a table merely because following bytes decode plausibly.
6. Do not invent host-side bounds/defaults until producer domains are proved.
7. Preserve PRG26 sign/carry/`ROR` arithmetic and the non-local OAM-full return.
8. Keep `$10` as shared NES RAM; never turn it into a renderer-local default.
9. Keep uncertain names conservative.
10. No original ROM bytes in Git.

## Stable cartridge / interrupt facts

VRC6 CPU map:

- `$6000-$7FFF`: PRG RAM
- `$8000-$BFFF`: switchable 16 KiB PRG ROM
- `$C000-$DFFF`: switchable 8 KiB PRG ROM
- `$E000-$FFFF`: fixed PRG31

Vectors: RESET `$E00B`, NMI `$E057`, IRQ `$E0F5`.

NMI bank `$0D` call `$8001` = `PRG26:$8001`. IRQ raw bank `$01` = PRG02/PRG03.

IRQ table is exactly `PRG02:$9F01-$9F5A`, 45 states `$00-$2C`; `$9F5B` is code. `$80` is high-bit bypass. `$E118` clears IRQ Control before acknowledge; `$E11D` enters at acknowledge without that clear.

## Stable OAM / sprite facts

Read before changing renderer code:

- `analysis/PRG26_SPRITE_FORMAT.md`
- `analysis/SPRITE_MASTER_TABLES.csv`
- `analysis/OAM_OBJECT_FIELDS.csv`
- `analysis/ZP10_OAM_STATE.md`
- `analysis/PRG26_9FA9_INCOMING_ATTR.md`

Key facts:

- `PRG26:$8001` iterates 28 render slots in seven arrays `$0400-$04C3`.
- descriptor records are full `Y,tile,attribute,X` or compressed `Y,tile,X` reusing ZP `$10`.
- full records update `$10`; compressed records consume it unchanged.
- `$0454,X != 0`: `(descriptor_attr & $FC) | full_object_byte`.
- `$04A8,X == 0`: mirrored path, toggles attr `$40`.
- OAM-full executes non-local `PLA; PLA; RTS`.
- descriptor census: 745 unique descriptors, max 27 sprites, max encoded length 96, 2310 compressed records.

Native baseline: `src/oam_renderer.*`, `tests/oam_renderer_test.cpp`.

## `$9FA9` closure

`$9FA9` requires selector `$10` + frame `$14`.

Established chain:

- 04D rejected PRG22 `$8745` because its owner uses selectors `$12/$08`.
- 04E1 rejected PRG18 type `$E1`.
- 04E2 rejected direct PRG06/07 selector-`$10` setup frames.
- 04E3 found the real mutation: PRG06 `$823E-$8251`, animation `$09`, fixed record `$F28D: 14 08 02`.
- 04E4 tied it to primary type `$08` and the scheduler.
- 04E5 proved exact `-2` vertical motion crosses `$A0-$A7`.
- 04E6 proved normal root `$0633=$0645=0`, first state-1 target `$90`; normal gameplay reaches `$9FA9`.
- 04F1 proved `$9FA9`'s first three compressed sprites consume variable inherited `$10`, not a constant initializer.

## Pre-render `$10` provenance

### 04F2 — IRQ graph

`PRG02/03:$9F99-$A526`, 1422 bytes. Verified IRQ graph and called fixed helpers preserve `$10`.

Evidence: `analysis/IRQ_ZP10_PRESERVATION.md`, `tools/audit_irq_zp10.py`.

### 04F3 — fixed NMI span

`PRG31:$E057-$E365`, 783 bytes. In-span NMI work preserves `$10`; external dependencies found: `$ED46`, raw bank `$0C:$89E2`, `$E7FB`/inline dispatch.

Evidence: `analysis/NMI_FIXED_ZP10_PRESERVATION.md`, `tools/audit_nmi_fixed_zp10.py`.

### 04F4 — `$ED46`

`PRG31:$EC00-$EFFF`, 1024 bytes. Complete `$ED46` graph preserves `$10`.

Evidence: `analysis/NMI_ED46_ZP10_PRESERVATION.md`, `tools/audit_nmi_ed46_zp10.py`.

### 04F5 — raw bank `$0C:$89E2` static graph

PRG24 `$8000-$91FF`, 4608 bytes. Conservative graph proves all statically resolved writes are `$10`-clean but left PRG24 `$842D` open because a ten-entry pointer table has no local bounds check.

Evidence: `analysis/NMI_BANK0C_ZP10_BOUNDARY.md`, `tools/audit_nmi_bank0c_zp10.py`.

### 04F6 — PRG24 `$842D` state/bank correction

New span:

```text
physical PRG24 / CPU $9200-$9FFF
3584 bytes
SHA-256 d7387b04a03289ebb1a0567ef49240d90b0bb177a0c128c8b06dbccabdb0776f
```

Critical machine-state facts:

- fixed `$E1AF` loads current instrument-data bank `$06D3,X`, banks it in, then jumps CPU `$8001`;
- PRG24 `$8DCD` chooses main vs alternate parser using bit 0 of `$011B,X`;
- `$88E0-$88F4` initializes that bit from the first stream byte and instrument index;
- complete direct writer inventory shows every later `$011B,X` update preserves bit 0.

Metadata audit:

```text
sound IDs                  125
bank-$0C instrument refs   139
distinct bank-$0C roots    125
alternate-parser refs        5
```

Those five references are:

```text
sound $0C, instrument $08 -> $9D8F
sound $0D, instrument $08 -> $9F73
sound $22, instrument $08 -> $A303
sound $3A, instrument $08 -> $A303
sound $3B, instrument $08 -> $A303
```

All three distinct roots start with `$FF`.

The only raw `$E7` bytes in referenced PRG24 stream data are `$9695,$97BB,$97C7,$9D73`; each belongs to a root initialized in **main-parser** mode, so none feeds PRG24 `$8418/$842D`.

Therefore 04F5's `$842D` edge was a **state/bank over-approximation**, not an unproved local `$00-$9F` bound. Do not add a bounds check to the translated parser.

Evidence:

- `analysis/NMI_BANK0C_PARSER_MODE.md`
- `tools/audit_nmi_bank0c_parser_mode.py`

Current provenance boundary:

```text
verified IRQ graph              -> preserves $10
fixed NMI span $E057-$E365     -> preserves $10
$ED46 helper graph              -> preserves $10
live raw bank $0C / PRG24      -> preserves $10
raw instrument bank $04        -> unresolved
raw instrument bank $05        -> unresolved
$E7FB / inline dispatch         -> unresolved
PRG26 renderer                  -> consumes/persists $10 exactly
```

The alternate parser is duplicated in raw banks `$04/$05/$0C`; parser bytes match across the common prefix except for the bank-identifying byte. Remaining sound work is therefore the data/control-flow domain in banks `$04/$05`, not another PRG24 table scan.

VPP remains **21/100**.

## Repository workflow

Repository: `Hyperbog/CVIII-Decomp`

Working branch: `decompilation`

Always fetch branch state before editing and confirm the ref before claiming a commit.

Primary hardware reference: NESdev Wiki. ROM bytes control game behavior.

## Current next checkpoint

**04F7 — raw instrument bank `$04` alternate-parser graph.**

Raw VRC6 bank `$04` maps CPU `$8000-$BFFF` to physical `PRG08/PRG09`.

Primary new span:

```text
physical PRG08 / CPU $8000-$91FF
4608 bytes
```

Follow only live paths entered through fixed `$E1AF`, carrying parser-state constraints so impossible indirect edges are not seeded. Determine whether any reachable write can modify/alias ZP `$10`. Do not open raw bank `$05` or `$E7FB` in the same checkpoint.

## User-facing handoff prompt

> Continue the faithful Akumajou Densetsu decomp/recomp on branch `decompilation`. Read the four primary handoff docs and current branch head. Treat the exact JP Mapper-24 ROM as controlling evidence. Work one bounded 500-5000-byte checkpoint, preferably using the upper half of the range when one dependency can be closed coherently; report material findings frequently; preserve exact 6502/VRC6/shared-ZP semantics; model bank/parser state instead of seeding impossible static edges; update VPP only under the fixed rubric; commit and stop. Current target: 04F7, audit live alternate-parser paths in raw bank `$04` / physical PRG08 `$8000-$91FF` only.
