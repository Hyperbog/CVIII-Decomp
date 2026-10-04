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

- normally **500-5000 new ROM bytes**, default near 1 KiB;
- expand within that range only to close the same local question;
- do not silently exceed about 5 KiB;
- report material findings frequently;
- add a focused audit/evidence artifact;
- update `docs/PROGRESS.md` and this handoff as needed;
- commit before reporting;
- stop after the checkpoint.

## Fidelity rules

1. Never guess code/data boundaries, producer domains, or semantics.
2. Track physical PRG bank + CPU address.
3. Preserve 6502 widths, flags, wrapping, stack/interrupt and shared-zero-page behavior.
4. Preserve VRC6 bank/IRQ semantics exactly.
5. Never extend a table merely because following bytes decode plausibly.
6. Do not invent host-side bounds/defaults until producer domains are proved.
7. Preserve PRG26 sign/carry/`ROR` arithmetic and non-local OAM-full return.
8. Keep `$10` as shared NES RAM; never turn it into a per-object renderer local/default.
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
- `$048C,X` chooses the first-level sprite-set window; `$0400,X` is frame-pointer byte offset.
- descriptor records are variable width: full `Y,tile,attribute,X` or compressed `Y,tile,X` reusing ZP `$10`.
- full records update `$10`; compressed records consume it unchanged.
- `$0454,X != 0` performs `(descriptor_attr & $FC) | full_object_byte`.
- `$04A8,X == 0` selects mirrored rendering and toggles attr `$40`.
- OAM traversal adds `$C4`; OAM-full performs non-local `PLA; PLA; RTS`.
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

Expanded within budget to `PRG31:$EC00-$EFFF`, 1024 bytes. Complete `$ED46` reachable graph preserves `$10`.

Evidence: `analysis/NMI_ED46_ZP10_PRESERVATION.md`, `tools/audit_nmi_ed46_zp10.py`.

### 04F5 — raw bank `$0C:$89E2`

Initial PRG24 `$8800-$8BFF` window expanded, within budget, to:

```text
physical PRG24 / CPU $8000-$91FF
4608 bytes
SHA-256 2bd1badec12d9f68bf829c272105d85097966d6fb0419c206566eb54c7011734
```

Starting at `$89E2`, the audit reaches 1488 accepted instruction starts on the statically closed graph. It proves:

- no direct write/RMW to `$10` / `$0010`;
- no indirect `(zp,X)` / `(zp),Y` store;
- no zero-page-indexed write can alias `$10`;
- no absolute-indexed write domain reaches `$0010`;
- all explicit fixed-bank exits go only to helpers already proven `$10`-clean in 04F3.

Five indirect dispatches have code-local finite domains. One deliberately remains open:

```text
$842D
```

Command `$E7` advances to its next stream byte; that byte's high nibble indexes the pointer block `$8430-$8443`. The block has ten entries (all `$8444`) for high nibbles `$0-$9`, but the code does not bounds-check the parameter. **Do not infer `$00-$9F` from table shape alone.**

Evidence:

- `analysis/NMI_BANK0C_ZP10_BOUNDARY.md`
- `tools/audit_nmi_bank0c_zp10.py`

Current provenance boundary:

```text
verified IRQ graph             -> preserves $10
fixed NMI span $E057-$E365    -> preserves $10
$ED46 helper graph             -> preserves $10
bank $0C:$89E2 closed graph   -> preserves $10
$842D E7 parameter domain     -> unresolved
$E7FB / inline dispatch        -> unresolved
PRG26 renderer                 -> consumes/persists $10 exactly
```

VPP remains **21/100**.

## Repository workflow

Repository: `Hyperbog/CVIII-Decomp`

Working branch: `decompilation`

Always fetch branch state immediately before editing and confirm the branch ref before claiming a commit.

Primary hardware reference: NESdev Wiki. ROM bytes control game-specific behavior.

## Current next checkpoint

**04F6 — `$842D` / command-`$E7` stream-parameter producer domain only.**

The already-audited PRG24 area contains a sound-stream pointer table beginning at `$8F60`; its entries point into `$90xx-$93xx`. Reuse already-audited `$9000-$91FF` context and add only:

```text
physical PRG24 / CPU $9200-$9FFF
3584 new bytes
```

Parse only the actual stream records reachable from the driver pointer roots needed to establish the byte immediately following command `$E7`. Prove whether its high nibble is always `$0-$9`, or record a counterexample. Do **not** open `$E7FB` in the same checkpoint.

## User-facing handoff prompt

> Continue the faithful Akumajou Densetsu decomp/recomp on branch `decompilation`. Read the four primary handoff docs and branch head. Treat the exact JP Mapper-24 ROM as controlling evidence. Work one bounded 500-5000-byte checkpoint, report material status frequently, preserve exact 6502/VRC6/shared-ZP semantics, do not infer producer domains from table shape, update VPP only under the fixed rubric, commit, and stop. Current target: 04F6, prove the `$E7` next-byte high-nibble domain using PRG24 sound-stream data, adding only `$9200-$9FFF` as new ROM span.
