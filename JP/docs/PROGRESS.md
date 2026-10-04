# Decompilation progress ledger

## Current status

Work proceeds in bounded, ROM-backed checkpoints. Normal new-ROM budget is **500-5000 bytes**, now generally using the upper half of that range when one coherent dependency can be closed safely. Material findings are reported during the checkpoint.

Primary metric: **Verified Parity Progress (VPP) = 21 / 100 (21%)**.

VPP is a fixed evidence rubric, not a time estimate or raw-byte percentage. See `docs/PROGRESS_METRIC.md`, `analysis/PROGRESS_SCORE.csv`, and `tools/progress_score.py`.

## Stable foundation

- Exact Japanese `Akumajou Densetsu` Mapper-24/VRC6a ROM identity is locked.
- PRG is modeled as 32 physical 8 KiB banks (`PRG00..PRG31`).
- Fixed vectors: RESET `$E00B`, NMI `$E057`, IRQ `$E0F5`.
- VRC6 PRG bank helpers and fixed/switchable contexts are mapped.
- NMI bank `$0D` call `$8001` resolves to `PRG26:$8001`.
- IRQ raw bank `$01` resolves into `PRG02/PRG03`.

## IRQ subsystem

`PRG02:$9F01-$9F5A` is the exact 45-entry IRQ table for states `$00-$2C`; `$9F5B` is code. `$80` is the high-bit bypass sentinel. The old `$9F60` overlap hypothesis is disproved.

`$E118` clears VRC6 IRQ Control `$F001`; `$E11D` enters at IRQ acknowledge `$F002` without the control clear. Preserve the distinction.

Evidence: `analysis/PRG02_IRQ_dispatch.md`, `analysis/IRQ_STATE_MACHINE.csv`, `tools/audit_irq_dispatch.py`.

## OAM / sprite subsystem

`PRG26:$8001` iterates 28 render slots using seven 28-byte arrays `$0400-$04C3`.

Sprite descriptors are variable width:

- bit0 clear: `Y,tile,attribute,X`
- bit0 set: `Y,tile,X`, reusing persistent ZP `$10`

Full records update `$10`; compressed records consume it unchanged. `$9FA9` is the only referenced descriptor whose first record is compressed and begins with three compressed records.

Native baseline: `src/oam_renderer.*`, `tests/oam_renderer_test.cpp`.

Core evidence: `analysis/PRG26_SPRITE_FORMAT.md`, `analysis/SPRITE_MASTER_TABLES.csv`, `analysis/OAM_OBJECT_FIELDS.csv`, `analysis/ZP10_OAM_STATE.md`.

## `$9FA9` reachability / `$10` provenance chain

- **04D:** PRG22 `$8745` rejected; type `$26` uses selectors `$12/$08`, not `$10`.
- **04E1:** PRG18 type `$E1` rejected; selector `$10` frames stay in `$E8/$EA/$EC/$EE`.
- **04E2:** direct PRG06/07 selector-`$10` setup does not produce frame `$14`.
- **04E3:** PRG06 `$823E-$8251` selects animation `$09` for base Y `$A0-$A7`; fixed record `$F28D: 14 08 02` makes `$EF93` write frame `$14`.
- **04E4:** primary type `$08` in slots `$01-$12` reaches this path under its state machine and scheduler.
- **04E5:** state `$00` establishes Y `$C0` and exact vertical velocity `-2`; state `$01` remains active through `$A0-$A7`.
- **04E6:** normal low-type construction gives `$0633=$0645=0`; first state-1 target is exactly `$90`, so normal gameplay reaches selector `$10` + frame `$14` -> descriptor `$9FA9`.
- **04F1:** renderer order is ascending and `$10` is not initialized at frame/object entry. `$9FA9` therefore consumes variable inherited shared state rather than a constant default.

## Pre-render `$10` provenance

### 04F2 — IRQ graph preserves `$10`

`PRG02/PRG03:$9F99-$A526`, 1422 bytes. No verified IRQ handler, reachable local helper, called fixed helper, or IRQ prologue/exit writes or aliases ZP `$10`.

Evidence: `analysis/IRQ_ZP10_PRESERVATION.md`, `tools/audit_irq_zp10.py`.

### 04F3 — fixed NMI span preserves `$10`

`PRG31:$E057-$E365`, 783 bytes. In-span NMI work preserves `$10` and identified three external dependencies: `$ED46`, raw bank `$0C:$89E2`, and `$E7FB`/inline dispatch.

Evidence: `analysis/NMI_FIXED_ZP10_PRESERVATION.md`, `tools/audit_nmi_fixed_zp10.py`.

### 04F4 — `$ED46` helper graph preserves `$10`

`PRG31:$EC00-$EFFF`, 1024 bytes. Complete `$ED46` reachable graph preserves `$10`.

Evidence: `analysis/NMI_ED46_ZP10_PRESERVATION.md`, `tools/audit_nmi_ed46_zp10.py`.

### 04F5 — raw bank `$0C:$89E2` static closure

The initial PRG24 window expanded within budget to:

```text
physical PRG24 / CPU $8000-$91FF
4608 bytes
SHA-256 2bd1badec12d9f68bf829c272105d85097966d6fb0419c206566eb54c7011734
```

Starting at `$89E2`, the conservative static graph reaches 1488 accepted instruction starts and proves no direct, indirect, zero-page-indexed, or absolute-indexed write can affect `$10`. Five indirect dispatches had local finite domains. `$842D` was left open because its ten-entry table has no local bounds check.

Evidence: `analysis/NMI_BANK0C_ZP10_BOUNDARY.md`, `tools/audit_nmi_bank0c_zp10.py`.

### 04F6 — `$842D` corrected as a state/bank over-approximation

New ROM span:

```text
physical PRG24 / CPU $9200-$9FFF
3584 bytes
SHA-256 d7387b04a03289ebb1a0567ef49240d90b0bb177a0c128c8b06dbccabdb0776f
```

Fixed helper `$E1AF` loads the current instrument-data bank from `$06D3,X` and jumps to CPU `$8001`. PRG24 `$8DCD` selects main vs alternate parser from bit 0 of `$011B,X`.

The JP metadata/control audit proves 139 bank-$0C instrument references / 125 distinct roots. Only five initialize alternate-parser mode; all are immediate `$FF` roots. All raw `$E7` bytes in referenced PRG24 stream data belong to main-parser roots. `$011B,X` has one mode initializer and later direct writers preserve bit 0.

Therefore PRG24 `$842D` is not a live bank-$0C stream edge. Do not add a host-side bound to its ten-entry table.

Evidence: `analysis/NMI_BANK0C_PARSER_MODE.md`, `tools/audit_nmi_bank0c_parser_mode.py`.

### 04F7 — raw bank `$04` parser core + first 23 roots

Exact new-byte footprint:

```text
raw bank $04 / physical PRG08
contiguous CPU $8000-$9209: 4618 bytes
span SHA-256 cfdd27fa72b9e990c31bb12e1511fa7229ffe2c898dcc361586c77b71543caa6
plus 73 isolated one-byte root-mode probes
TOTAL: 4691 new bytes
```

Bytes `$8001-$87AD` are byte-identical to the bank `$0C` alternate-parser core. The resolved executable graph contains 786 accepted instruction starts and no write form capable of modifying or aliasing ZP `$10`; its fixed exits are already covered by 04F3.

Metadata gives 102 bank-$04 references / 96 distinct roots, all alternate-parser mode. Twenty-three roots begin before `$920A`.

**04F8 correction:** the original 04F7 write-up called each root's first raw `$FF` a terminator. Eleven of those 23 first-`$FF` positions are actually the marker in `FE FF lo hi` pointer commands. 04F8 recursively rechecked all 23 roots with the actual `FB`/`FD`/`FE` control grammar: no `$E7` command is reachable, every pointer target remains inside `$87AE-$9209`, and the latest reachable command is `$9208`. Thus the 04F7 safety result remains valid; only the old terminator interpretation was wrong.

Evidence: `analysis/NMI_BANK04_ALT_PARSER_BOUNDARY.md`, `tools/audit_nmi_bank04_alt_parser.py`, plus the corrective decoder in `tools/audit_nmi_bank04_prg08_tail.py`.

### 04F8 — PRG08 tail + minimal PRG09 closure

Dependency span:

```text
raw bank $04 / CPU $920A-$A011
3592 bytes
SHA-256 69e6d56aed2875f3f2840ebb4b5c52b844da4482a150a4db3647cd933bc79b8e
```

Eleven root bytes inside this span were already counted as 04F7 mode probes, so the exact 04F8 new-byte footprint is **3581 bytes**.

CPU `$A000-$A011` is an 18-byte physical PRG09 extension required to close the same dependency: root `$9E85` reaches `$A010: FE FF 85 9E`, which jumps back to `$9E85`.

04F8 closes exactly 11 later roots from sound IDs `$5D,$5E,$60`. The recursive stream decoder visits **3312 abstract parser states / 3025 unique command addresses**. Every `FD`/`FE` pointer target remains inside `$920A-$A011`; there are zero raw or decoded `$E7` commands in the closed domain. Since the executable parser core is already `$10`-clean, these 11 additional roots preserve ZP `$10` and cannot activate `$842D`.

After 04F8, **34 of 96** bank-$04 roots are closed and **62 later PRG09 roots remain unresolved**, beginning at `$A014`.

Evidence: `analysis/NMI_BANK04_PRG08_TAIL.md`, `tools/audit_nmi_bank04_prg08_tail.py`.

**VPP remains 21/100 after 04F8.**

## Current provenance boundary

```text
verified IRQ graph                 -> preserves $10
fixed NMI span $E057-$E365        -> preserves $10
$ED46 helper graph                 -> preserves $10
raw bank $0C / PRG24              -> preserves $10 on live bank-$0C paths
raw bank $04 parser $8001-$87AD   -> preserves $10 on resolved graph
raw bank $04 first 23 roots       -> recursively closed; no live $E7
raw bank $04 next 11 roots        -> closed through $A011; no live $E7
raw bank $04 later 62 roots       -> unresolved, first root $A014
raw instrument bank $05           -> unresolved
$E7FB / inline dispatch            -> unresolved
PRG26 renderer                     -> consumes/persists $10 exactly
```

## Unresolved / do not assume

- whether later raw bank `$04` / physical PRG09 stream data can activate `$842D` or any other path relevant to ZP `$10`;
- whether raw instrument bank `$05` can write/alias ZP `$10` while servicing the pre-render sound update;
- whether `$E7FB` or its inline-dispatch targets can write `$10` before rendering;
- whole-ROM type-transition / selector-frame producer closure;
- higher-level meaning of `$AD`;
- semantic identities of individual sprite descriptors;
- exact visual/game-state meanings of IRQ states;
- conservative ROM-byte code/data coverage companion metric.

## Next manageable checkpoint

**04F9 — continue raw bank `$04` through physical PRG09.**

Start at CPU `$A012` (physical PRG09). A good initial bounded window is `$A012-$B1FF` (4590 contiguous bytes); subtract any root bytes already counted as 04F7 mode probes when reporting exact new-byte coverage. Carry the recursive `FB`/`FD`/`FE` stream state and prove pointer-target closure rather than using raw `$FF` as a terminator. Do not open raw bank `$05` or fixed `$E7FB` in the same checkpoint.
