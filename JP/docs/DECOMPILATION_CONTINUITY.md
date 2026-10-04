# Akumajou Densetsu decomp/recomp continuity playbook

Durable handoff for `Hyperbog/CVIII-Decomp`. Before new work read this file, `docs/PROGRESS.md`, `docs/PROGRESS_METRIC.md`, and `docs/ROM_IDENTITY.md`, then confirm the current `decompilation` branch head.

## Objective and controlling evidence

Faithfully reverse engineer the Japanese NES release of **Akumajou Densetsu** into an evidence-accountable native PC decompilation/recompilation. Preserve original behavior first; QoL/mod work comes later.

ROM bytes are controlling evidence. Hardware documentation, public disassemblies, emulator behavior, NSF/M3U data, names, and hypotheses are secondary. Never commit the source ROM.

Target ROM:

- size `393232` (`0x60010`)
- SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`
- PRG 256 KiB, CRC32 `BA6BDD6A`
- CHR 128 KiB, CRC32 `BF15255C`
- Mapper 24 / Konami VRC6a

Primary metric: **VPP = 21/100**. It is evidence-based, not a labor estimate or raw-byte percentage.

## Checkpoint / fidelity policy

Each user `continue` means one bounded checkpoint:

- normally **500-5000 new ROM bytes**;
- expand only to close the same question and never silently exceed the budget;
- add reproducible audit/evidence artifacts;
- update progress/handoff and VPP only if earned;
- commit and confirm branch head before reporting.

Never guess code/data boundaries, producer domains, or semantics. Track physical PRG bank + CPU address. Preserve 6502 widths, flags, wrapping, stack/interrupt behavior and shared zero page. Preserve VRC6 bank/IRQ semantics. Never extend a table merely because following bytes decode plausibly. Do not invent host-side bounds/defaults until producer domains are proved. Keep `$10` as shared NES RAM. No original ROM bytes in Git.

## Stable cartridge / interrupt facts

VRC6 CPU map:

- `$6000-$7FFF`: PRG RAM
- `$8000-$BFFF`: switchable 16 KiB PRG ROM
- `$C000-$DFFF`: switchable 8 KiB PRG ROM
- `$E000-$FFFF`: fixed PRG31

Vectors: RESET `$E00B`, NMI `$E057`, IRQ `$E0F5`.

NMI bank `$0D` call `$8001` = `PRG26:$8001`. IRQ raw bank `$01` = PRG02/PRG03. IRQ table is exactly `PRG02:$9F01-$9F5A`, 45 states `$00-$2C`; `$9F5B` is code. `$80` is high-bit bypass. `$E118` clears IRQ Control before acknowledge; `$E11D` enters at acknowledge without that clear.

## Stable OAM / sprite facts

Read `analysis/PRG26_SPRITE_FORMAT.md`, `analysis/SPRITE_MASTER_TABLES.csv`, `analysis/OAM_OBJECT_FIELDS.csv`, `analysis/ZP10_OAM_STATE.md`, and `analysis/PRG26_9FA9_INCOMING_ATTR.md` before renderer changes.

`PRG26:$8001` iterates 28 render slots. Descriptors are full `Y,tile,attribute,X` or compressed `Y,tile,X`; compressed records consume persistent ZP `$10`. Full records update `$10`. OAM-full executes non-local `PLA; PLA; RTS`. Native baseline: `src/oam_renderer.*`, `tests/oam_renderer_test.cpp`.

`$9FA9` is normally reachable: checkpoints 04D-04E6 traced selector `$10` + frame `$14` to primary type `$08`; 04F1 proved its first three compressed sprites consume variable inherited `$10`, not a constant initializer.

## Pre-render `$10` provenance

- **04F2:** IRQ graph `PRG02/03:$9F99-$A526`, 1422 bytes, preserves `$10`.
- **04F3:** fixed NMI span `PRG31:$E057-$E365`, 783 bytes, preserves `$10`; external dependencies were `$ED46`, raw bank `$0C:$89E2`, and `$E7FB`/inline dispatch.
- **04F4:** `$ED46` graph in `PRG31:$EC00-$EFFF`, 1024 bytes, preserves `$10`.
- **04F5:** raw bank `$0C` / PRG24 `$8000-$91FF`, 4608 bytes, closed a conservative graph except `$842D`; all resolved writes are `$10`-clean.
- **04F6:** PRG24 `$9200-$9FFF`, 3584 bytes. `$842D` was proved to be a bank/parser-state over-approximation for bank `$0C`, not a missing local bounds check. Fixed `$E1AF` loads `$06D3,X`, banks it in, then jumps CPU `$8001`. Parser mode is bit 0 of `$011B,X`; initialization is from first stream byte + instrument index and later direct writers preserve bit 0. Bank `$0C`: 139 instrument refs, 125 roots, only five alternate-parser refs, all immediate `$FF` roots; all raw `$E7` bytes belong to main-parser roots. Evidence: `analysis/NMI_BANK0C_PARSER_MODE.md`, `tools/audit_nmi_bank0c_parser_mode.py`.
- **04F7:** raw bank `$04`, exact new-byte footprint **4691 bytes**: contiguous CPU `$8000-$9209` (4618 bytes, SHA-256 `cfdd27fa72b9e990c31bb12e1511fa7229ffe2c898dcc361586c77b71543caa6`) plus 73 isolated root-mode probes. Bytes `$8001-$87AD` are byte-identical to the bank `$0C` alternate-parser core. Resolved graph: 786 accepted instruction starts, no write form capable of modifying/aliasing ZP `$10`; fixed external helpers are already inside 04F3. Metadata gives 102 bank-$04 refs / 96 roots; all initialize alternate-parser mode. Twenty-three roots begin before `$920A`.
- **04F8 correction to 04F7:** the old 04F7 text called the first raw `$FF` after each root a terminator. Eleven of those 23 positions are actually `FE FF lo hi` pointer markers. 04F8 recursively rechecks all 23 roots with the actual `FB`/`FD`/`FE` grammar: no live `$E7`, every pointer target remains inside `$87AE-$9209`, and the latest reachable command is `$9208`. The 04F7 safety result stands; only the terminator interpretation was wrong.
- **04F8:** raw bank `$04` dependency span CPU `$920A-$A011`, 3592 bytes, SHA-256 `69e6d56aed2875f3f2840ebb4b5c52b844da4482a150a4db3647cd933bc79b8e`. Eleven bytes overlap 04F7 root probes, so exact new-byte footprint is **3581 bytes**. The 18-byte PRG09 extension `$A000-$A011` is required because root `$9E85` reaches `$A010: FE FF 85 9E`, which loops back to `$9E85`. Eleven roots from sounds `$5D,$5E,$60` close under the recursive decoder: 3312 abstract states / 3025 unique command addresses, every `FD`/`FE` target inside `$920A-$A011`, zero raw or decoded `$E7`. Evidence: `analysis/NMI_BANK04_PRG08_TAIL.md`, `tools/audit_nmi_bank04_prg08_tail.py`.

Current provenance boundary:

```text
verified IRQ graph                 -> preserves $10
fixed NMI span $E057-$E365        -> preserves $10
$ED46 helper graph                 -> preserves $10
live raw bank $0C / PRG24         -> preserves $10
raw bank $04 parser $8001-$87AD   -> preserves $10 on resolved graph
raw bank $04 first 23 roots       -> recursively closed; no live $E7
raw bank $04 next 11 roots        -> closed through $A011; no live $E7
raw bank $04 later 62 roots       -> unresolved, first root $A014
raw instrument bank $05           -> unresolved
$E7FB / inline dispatch            -> unresolved
PRG26 renderer                     -> consumes/persists $10 exactly
```

Do not add a host-side bound to `$842D`; its physical table remains ten entries at `$8430-$8443`.

## Repository workflow

Repository: `Hyperbog/CVIII-Decomp`

Working branch: `decompilation`

Primary hardware reference: NESdev Wiki. ROM bytes control game behavior.

## Current next checkpoint

**04F9 — raw bank `$04` physical PRG09 continuation.**

Begin at CPU `$A012`. Use an initial bounded window around `$A012-$B1FF` (4590 contiguous bytes), subtracting any root bytes already counted as 04F7 mode probes from the exact new-byte total. Carry the recursive stream state (`FB` loop anchor, `FD` call/return, `FE` counted/absolute pointer) and prove pointer-target closure; do not use first raw `$FF` as a terminator proxy. Do not open raw bank `$05` or fixed `$E7FB` in the same checkpoint.

## User-facing handoff prompt

> Continue the faithful Akumajou Densetsu decomp/recomp on branch `decompilation`. Read the four primary handoff docs and current branch head. Treat the exact JP Mapper-24 ROM as controlling evidence. Work one bounded 500-5000-new-byte checkpoint; preserve exact 6502/VRC6/shared-ZP semantics; carry bank/parser and stream-control state rather than seeding impossible static edges; add reproducible evidence; update VPP only under the fixed rubric; commit and stop. Current target: 04F9, continue raw bank `$04` from CPU `$A012` through physical PRG09 using the recursive `FB`/`FD`/`FE` decoder.
