# Decompilation progress ledger

## Current status

**RECOVERY HOLD:** `analysis/RESUME_STATE.json` is currently `BLOCKED_REPAIR_REQUIRED`. Do not begin 04F9 until the narrow 04F7/04F8 stream-boundary accounting described below is repaired and the resume checker reports a ready frontier.

Work otherwise proceeds in bounded, ROM-backed checkpoints. Normal new-ROM budget is **500-5000 genuinely new bytes**. Material findings are reported during the checkpoint.

Primary metric: **Verified Parity Progress (VPP) = 21 / 100 (21%)**.

VPP is a fixed evidence rubric, not a time estimate or raw-byte percentage. See `docs/PROGRESS_METRIC.md`, `analysis/PROGRESS_SCORE.csv`, and `tools/progress_score.py`.

After any interruption read `docs/INTERRUPTION_RECOVERY.md` and `analysis/RESUME_STATE.json` and run `tools/check_resume_frontier.py` before forward work.

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

Physical PRG24 / CPU `$8000-$91FF`, 4608 bytes, SHA-256 `2bd1badec12d9f68bf829c272105d85097966d6fb0419c206566eb54c7011734`.

The conservative graph reaches 1488 accepted instruction starts and contains no resolved write form capable of affecting `$10`. `$842D` was left open because its ten-entry table has no local bounds check.

Evidence: `analysis/NMI_BANK0C_ZP10_BOUNDARY.md`, `tools/audit_nmi_bank0c_zp10.py`.

### 04F6 — `$842D` corrected as a state/bank over-approximation

Physical PRG24 / CPU `$9200-$9FFF`, 3584 bytes, SHA-256 `d7387b04a03289ebb1a0567ef49240d90b0bb177a0c128c8b06dbccabdb0776f`.

Fixed helper `$E1AF` loads the current instrument-data bank from `$06D3,X` and jumps to CPU `$8001`. Parser mode is bit 0 of `$011B,X`; initialization comes from first stream byte + instrument index and later direct writers preserve bit 0.

The metadata/control audit proves 139 bank-$0C references / 125 roots. Only five initialize alternate-parser mode and all are immediate `$FF` roots; all raw `$E7` bytes in referenced PRG24 stream data belong to main-parser roots. Therefore PRG24 `$842D` is not a live bank-$0C edge.

Evidence: `analysis/NMI_BANK0C_PARSER_MODE.md`, `tools/audit_nmi_bank0c_parser_mode.py`.

### 04F7 — raw bank `$04` parser core and stream tranche

Recorded footprint was 4691 bytes: contiguous CPU `$8000-$9209` (4618 bytes, SHA-256 `cfdd27fa72b9e990c31bb12e1511fa7229ffe2c898dcc361586c77b71543caa6`) plus 73 isolated one-byte root-mode probes.

The stable result is the parser executable core: bytes `$8001-$87AD` are byte-identical to the bank `$0C` alternate-parser core; the resolved graph contains 786 accepted instruction starts and no write form capable of modifying/aliasing ZP `$10`. Metadata gives 102 bank-$04 references / 96 roots, all alternate-parser mode.

The later stream-boundary accounting is under recovery review; do not discard or broadly redo the prior root analysis.

### 04F8 — recursive stream work, currently provisional at the boundary

04F8 introduced the correct recursive stream grammar for `FB` loop anchors, `FD` call/return, counted `FE`, and `FE FF lo hi` pointer loads. This corrected the older mistake of using the first raw `$FF` as a terminator proxy.

The investigation found zero decoded `$E7` commands in the examined root sets and preserved the conclusion that the common executable parser core is `$10`-clean. However, the restart overlap exposed two range-accounting defects:

```text
04F7 root $9133 reaches $9208: FE FF 33 91
                              operands $920A-$920B are beyond old 04F7 span

04F8 root $9E85 reaches $A010: FE FF 85 9E
                              operands $A012-$A013 are beyond recorded 04F8 span
```

The second defect means the old 04F8 span `$920A-$A011` / 3592 bytes cannot be treated as the final authoritative dependency span even though the decoder read the pointer bytes.

Candidate corrected 04F8 span, pending hardened-audit confirmation:

```text
CPU $920A-$A013
half-open [$920A,$A014)
3594 bytes
SHA-256 728c86cd808e178821f7f72d1f0371eb16a5bde3a1dda495543338391a5e7b3c
11 prior mode-probe bytes overlap
candidate 3583 genuinely new bytes
candidate next unresolved root $A014
```

**Do not count this candidate as final until the audit enforces operand-in-span bounds and passes.**

Evidence under repair: `analysis/NMI_BANK04_ALT_PARSER_BOUNDARY.md`, `analysis/NMI_BANK04_PRG08_TAIL.md`, `tools/audit_nmi_bank04_alt_parser.py`, `tools/audit_nmi_bank04_prg08_tail.py`.

**VPP remains 21/100.** No credited rubric point depends on this boundary correction.

## Current provenance boundary

```text
verified IRQ graph                 -> preserves $10
fixed NMI span $E057-$E365        -> preserves $10
$ED46 helper graph                 -> preserves $10
raw bank $0C / PRG24              -> preserves $10 on live bank-$0C paths
raw bank $04 parser $8001-$87AD   -> preserves $10 on resolved graph
04F7/04F8 stream boundary cycles   -> recovery repair required
raw instrument bank $05           -> unresolved
$E7FB / inline dispatch            -> unresolved
PRG26 renderer                     -> consumes/persists $10 exactly
```

## Unresolved / do not assume

- do not assume 04F8 is a safe resume frontier until the blocked state is repaired;
- do not begin later raw bank `$04` / PRG09 stream analysis yet;
- whether raw instrument bank `$05` can write/alias ZP `$10` remains unresolved;
- whether `$E7FB` or its inline-dispatch targets can write `$10` before rendering remains unresolved;
- whole-ROM type-transition / selector-frame producer closure remains open;
- higher-level meaning of `$AD`, semantic identities of individual sprite descriptors, and exact visual meanings of IRQ states remain open.

## Next action

**Recovery repair, not 04F9.**

1. Run `tools/check_resume_frontier.py <ROM.nes>` and confirm it hard-stops on `BLOCKED_REPAIR_REQUIRED` while verifying the candidate bytes.
2. Harden `tools/audit_nmi_bank04_prg08_tail.py` so each decoded multi-byte command asserts all operand bytes lie inside the claimed range.
3. Revalidate only root `$9133`'s boundary cycle and the 04F8 root cycles that reach `$A010`; reuse the already-proven parser core and existing root metadata.
4. Reconcile the audit, `analysis/NMI_BANK04_PRG08_TAIL.md`, this progress file, `docs/DECOMPILATION_CONTINUITY.md`, and finally `analysis/RESUME_STATE.json`.
5. If the hardened audit confirms the candidate span, the first unresolved root becomes `$A014`; only then start 04F9.
