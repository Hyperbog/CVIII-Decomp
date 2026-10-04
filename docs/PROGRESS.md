# Decompilation progress ledger

## Current status

Work proceeds in **small bounded checkpoints**: one narrow question, direct ROM verification, focused evidence/audit, commit, then stop.

Byte-budget policy: normally **500-5000 bytes of new ROM span per checkpoint**, default near 1 KiB. Expand within that range only when local control-flow edges are necessary to answer the same question. Provide short status updates after material findings.

Primary metric: **Verified Parity Progress (VPP) = 21 / 100 (21%)**.

VPP is a fixed evidence rubric, not a time estimate or raw-byte percentage. See `docs/PROGRESS_METRIC.md`, `analysis/PROGRESS_SCORE.csv`, and `tools/progress_score.py`.

## Stable foundation

- Exact Japanese `Akumajou Densetsu` Mapper-24/VRC6a ROM identity is locked.
- PRG is modeled as 32 physical 8 KiB banks (`PRG00..PRG31`).
- Fixed vectors: RESET `$E00B`, NMI `$E057`, IRQ `$E0F5`.
- VRC6 PRG helper/bank contexts are mapped.
- NMI bank `$0D` call `$8001` resolves to `PRG26:$8001`.
- IRQ raw bank `$01` resolves into `PRG02/PRG03`.

## IRQ subsystem

`PRG02:$9F01-$9F5A` is the exact 45-entry IRQ table for states `$00-$2C`; `$9F5B` is code. `$80` is the high-bit bypass sentinel. The old `$9F60` overlap hypothesis is disproved.

`$E118` clears VRC6 IRQ Control `$F001`; `$E11D` enters at IRQ acknowledge `$F002` without the control clear. Preserve the distinction.

Evidence: `analysis/PRG02_IRQ_dispatch.md`, `analysis/IRQ_STATE_MACHINE.csv`, `tools/audit_irq_dispatch.py`.

## OAM / sprite subsystem

`PRG26:$8001` iterates 28 render slots using seven 28-byte arrays `$0400-$04C3`.

Sprite descriptor records are variable width:

- Y/control bit0 clear: `Y,tile,attribute,X`
- Y/control bit0 set: `Y,tile,X`, reusing persistent ZP `$10`

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
- **04E6:** normal low-type construction gives `$0633=$0645=0`; first state-1 target is exactly `$90`, so normal gameplay necessarily reaches selector `$10` + frame `$14` -> descriptor `$9FA9`.
- **04F1:** renderer order is ascending; `$10` is not initialized at frame/object entry. `$9FA9` therefore consumes variable inherited shared state rather than a constant default.

Evidence for this chain is under `analysis/PRG06_*`, `analysis/PRG26_9FA9_INCOMING_ATTR.md`, and matching `tools/audit_*` scripts.

## Pre-render `$10` provenance

### 04F2 — verified IRQ graph preserves `$10`

Primary span `PRG02/PRG03:$9F99-$A526` = 1422 bytes. No verified IRQ handler, reachable local helper, called fixed helper, or IRQ prologue/exit writes or aliases ZP `$10`.

Evidence: `analysis/IRQ_ZP10_PRESERVATION.md`, `tools/audit_irq_zp10.py`.

### 04F3 — fixed pre-render NMI span preserves `$10`

Primary span `PRG31:$E057-$E365` = 783 bytes. In-span NMI code preserves `$10` and identified three external dependencies: `$ED46`, raw bank `$0C:$89E2`, and `$E7FB`/inline dispatch.

Evidence: `analysis/NMI_FIXED_ZP10_PRESERVATION.md`, `tools/audit_nmi_fixed_zp10.py`.

### 04F4 — `$ED46` helper graph preserves `$10`

Final bounded span `PRG31:$EC00-$EFFF` = 1024 bytes. Starting at `$ED46`, 323 reachable instruction starts stay in-window and no reachable write can affect `$10`.

Evidence: `analysis/NMI_ED46_ZP10_PRESERVATION.md`, `tools/audit_nmi_ed46_zp10.py`.

### 04F5 — raw bank `$0C:$89E2` bounded graph

Initial 1 KiB `PRG24:$8800-$8BFF` exposed same-bank helper targets, so the checkpoint expanded within the agreed budget to:

```text
physical PRG24 / CPU $8000-$91FF
4608 bytes
SHA-256 2bd1badec12d9f68bf829c272105d85097966d6fb0419c206566eb54c7011734
```

Starting at `$89E2`, the audit reaches **1488 accepted instruction starts** after resolving code-bounded indirect dispatches.

Proved on the closed graph:

- zero direct writes/RMW to ZP `$10` / `$0010`;
- zero `(zp,X)` or `(zp),Y` stores;
- zero zero-page-indexed writes that can wrap to `$10`;
- all absolute-indexed write domains remain away from `$0010`;
- every explicit fixed-bank exit goes only to helpers already proven `$10`-clean in 04F3.

Five indirect dispatches close from local code bounds. One remains intentionally open: `$842D`, reached by stream command `$E7`, uses the **next stream byte's high nibble** to index a ten-entry pointer block at `$8430-$8443`. The code itself does not bounds-check that byte to `$00-$9F`; table shape alone is not producer-domain proof.

Therefore 04F5 is a **bounded partial closure**: the statically closed bank-$0C graph preserves `$10`, but the actual `$E7` next-byte producer domain remains to be proved.

Evidence:

- `analysis/NMI_BANK0C_ZP10_BOUNDARY.md`
- `tools/audit_nmi_bank0c_zp10.py`

**VPP remains 21/100 after 04F5.**

## Current provenance boundary

```text
verified IRQ graph             -> preserves $10
fixed NMI span $E057-$E365    -> preserves $10
$ED46 helper graph             -> preserves $10
bank $0C:$89E2 closed graph   -> preserves $10
$842D E7 parameter domain     -> unresolved
$E7FB / inline dispatch        -> unresolved
PRG26 renderer                 -> consumes/persists $10 exactly
```

## Unresolved / do not assume

- producer domain of the byte following sound-stream command `$E7` at `$842D`;
- whether `$E7FB` or its inline-dispatch targets can write `$10` before rendering;
- whole-ROM type-transition / selector-frame producer closure;
- higher-level meaning of `$AD`;
- semantic identities of individual sprite descriptors;
- exact visual/game-state meanings of IRQ states;
- conservative ROM-byte code/data coverage companion metric.

## Next manageable checkpoint

**04F6 — `$842D` / command-`$E7` stream-parameter producer domain only.**

The already-audited `$8F60+` pointer area shows sound streams rooted in `$90xx-$93xx`. Reuse the already-audited `$9000-$91FF` bytes and add only:

```text
physical PRG24 / CPU $9200-$9FFF
3584 new bytes
```

Parse only stream records reachable from the sound-driver pointer roots needed to establish the byte immediately following command `$E7`. Prove whether its high nibble is always `$0-$9`, or record any counterexample. Do not open `$E7FB` in the same checkpoint.
