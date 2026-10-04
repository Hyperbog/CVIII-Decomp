# Decompilation progress ledger

## Current status

Work proceeds in **small bounded checkpoints**: one narrow question, direct ROM verification, focused artifact/audit update, commit, then stop.

Byte-budget policy: normally **500-5000 bytes of new ROM span per checkpoint**, defaulting near 1 KiB. A checkpoint may expand within that range when newly discovered local control-flow edges are required to close the same question; do not stop at an arbitrary boundary or silently exceed about 5 KiB. Provide short status updates after material findings.

Primary high-level metric: **Verified Parity Progress (VPP) = 21 / 100 (21%)**.

VPP is a fixed evidence rubric, not a time estimate or raw disassembly-byte percentage. See `docs/PROGRESS_METRIC.md`, `analysis/PROGRESS_SCORE.csv`, and `tools/progress_score.py`.

## Stable foundation

- Exact Japanese `Akumajou Densetsu` ROM identity is locked: Mapper 24 / VRC6a, 256 KiB PRG, 128 KiB CHR.
- PRG is modeled as 32 physical 8 KiB banks (`PRG00..PRG31`).
- Fixed vectors: RESET `$E00B`, NMI `$E057`, IRQ `$E0F5`.
- VRC6 PRG helpers and fixed/switchable bank contexts are mapped.
- NMI bank `$0D` call `$8001` resolves to `PRG26:$8001`.
- IRQ raw bank `$01` resolves into `PRG02/PRG03`.

## IRQ subsystem

`PRG02:$9F01-$9F5A` is the authoritative 45-entry IRQ table for states `$00-$2C`; `$9F5B` is code. `$80` is the high-bit bypass sentinel. The old `$9F60` overlap hypothesis was disproved.

`$E118` and `$E11D` are distinct exits: `$E118` clears VRC6 IRQ Control `$F001`; `$E11D` acknowledges via `$F002` and restores tracked bank state.

Evidence:

- `analysis/PRG02_IRQ_dispatch.md`
- `analysis/IRQ_STATE_MACHINE.csv`
- `tools/audit_irq_dispatch.py`

## OAM / sprite subsystem

`PRG26:$8001` iterates 28 render slots using seven 28-byte arrays `$0400-$04C3`. `$048C,X` selects a sprite-set pointer window; `$0400,X` is the frame-pointer byte offset.

Descriptor records are variable width:

- bit0 clear: `Y,tile,attribute,X`
- bit0 set: `Y,tile,X`, reusing persistent ZP attribute cache `$10`

Full records update `$10`; compressed records consume it unchanged. `$9FA9` is the only referenced descriptor whose first record is compressed; it begins with three compressed records.

Native baseline:

- `src/oam_renderer.hpp`
- `src/oam_renderer.cpp`
- `tests/oam_renderer_test.cpp`

Core evidence:

- `analysis/PRG26_OAM_frame.md`
- `analysis/PRG26_SPRITE_FORMAT.md`
- `analysis/SPRITE_SET_TABLE.csv`
- `analysis/SPRITE_MASTER_TABLES.csv`
- `analysis/OAM_OBJECT_FIELDS.csv`
- `analysis/ZP10_OAM_STATE.md`

## `$9FA9` reachability / `$10` provenance chain

### 04D — PRG22 `$8745` rejected

PRG22 `$8745` writes frame `$14`, but its owning type `$26` uses selectors `$12/$08`, not `$10`.

### 04E1 — PRG18 type `$E1` rejected

Type `$E1` starts selector `$10` at frame `$E8/$EC` and mutates only to `$EA/$EE`.

### 04E2 — direct PRG06/07 stores rejected

Direct selector-`$10` setup frames do not include `$14`; the direct frame `$14` setup is paired with selector `$0E`.

### 04E3 — transitive animation mechanism

PRG06 `$823E-$8251` chooses animation ID `$09` for base Y `$A0-$A7` and installs selector `$10`. Fixed animation record `$F28D: 14 08 02` makes `$EF93` write frame `$14`.

### 04E4 — owner/scheduler link

Primary type `$08` in active slots `$01-$12` routes to `PRG06:$8021`. Internal state `$01` can reach `$823E`; the same scheduler iteration can run movement integration and `$EF93`.

Renderer mapping:

```text
selector $10 -> table $9E6D
frame $14    -> descriptor $9FA9
```

### 04E5 — deterministic vertical path

State `$00` establishes base Y `$C0` and exact vertical velocity `-2`. State `$01` stays active through `$A0-$A7`, so the trajectory necessarily crosses the animation-`$09` window.

### 04E6 — root `$0645` producer closure

Normal low-type construction clears `$0633/$0645`. State `$00` makes the first state-1 index exactly `$01`, target `$840F[$01]=$90`. Therefore normal gameplay type `$08` necessarily reaches selector `$10` + frame `$14` and descriptor `$9FA9`.

Evidence:

- `analysis/PRG06_TYPE08_823E_OWNER.md`
- `analysis/PRG06_TYPE08_VERTICAL_PATH.md`
- `analysis/PRG06_TYPE08_0645_PRODUCERS.md`
- matching audits under `tools/`

### 04F1 — incoming `$10` is variable inherited state

Primary span: PRG26 `$8001-$81FF` plus isolated `$9FA9` and slot-0 mirror-state signatures.

Renderer order is ascending and `$10` is not initialized at frame/object entry. `$9FA9` begins:

```text
04 DF 8A F0  E1 8C F8  E5 8E 00  04 E4 90 03
```

Its first three records therefore inherit shared renderer state, normally the last explicit attribute emitted by an earlier rendered object. There is no valid constant host-side initializer.

Evidence:

- `analysis/PRG26_9FA9_INCOMING_ATTR.md`
- `tools/audit_prg26_9fa9_cache.py`
- `tests/oam_renderer_test.cpp`

### 04F2 — verified IRQ graph preserves `$10`

Primary span: `PRG02/PRG03:$9F99-$A526`, 1422 bytes, SHA-256 `fb0f709699ad64b6cb49fa4eaeb2de8e1a260e23745341fc2f48b38fedd8ded3`.

No reachable handler or called helper writes or aliases ZP `$10`; fixed IRQ prologue/exit `$E0F5-$E130` also preserves it. An IRQ taken after NMI `CLI` and before rendering therefore does not modify `$10` for the proven IRQ graph.

Evidence:

- `analysis/IRQ_ZP10_PRESERVATION.md`
- `tools/audit_irq_zp10.py`

### 04F3 — fixed pre-render NMI span preserves `$10`

Primary span: `PRG31:$E057-$E365`, 783 bytes, SHA-256 `b0e367bb5971310da3bbd066f54cc3def543e82134f4df6b7b82feef06166176`.

The renderer-reaching NMI body and all contained helper bodies preserve `$10`; locally indexed writes are proven bounded away from it.

Three external pre-render dependencies were identified:

```text
$ED46
raw bank $0C : CPU $89E2
$E7FB / inline-dispatch targets
```

Evidence:

- `analysis/NMI_FIXED_ZP10_PRESERVATION.md`
- `tools/audit_nmi_fixed_zp10.py`

### 04F4 — `$ED46` helper graph preserves `$10`

The planned 512-byte window was expanded, within the agreed byte budget, to close local targets `$ED17`, `$EF5C`, and `$EC85`.

Final primary span:

```text
PRG31:$EC00-$EFFF
1024 bytes
SHA-256 e83c0d832fc23590c0dde2448a9943ef217ada4e4f520d0da0e3f85f863dc797
```

Starting from `$ED46`, the audit proves:

- 323 reachable instruction starts;
- no reachable call/jump/branch leaves the 1 KiB window;
- no dynamic/indexed write exists on the reachable graph;
- reachable writes are confined to ZP `$00`, ZP `$1E`, `$0300`, and PPU registers `$2000/$2006/$2007`.

Therefore the complete NMI-called `$ED46` helper graph preserves ZP `$10`.

Evidence:

- `analysis/NMI_ED46_ZP10_PRESERVATION.md`
- `tools/audit_nmi_ed46_zp10.py`

**VPP remains 21/100 after 04F4.** This closes another exact shared-RAM provenance dependency but does not complete a new fixed-rubric milestone.

## Current provenance boundary

```text
verified IRQ graph             -> preserves $10
fixed NMI span $E057-$E365    -> preserves $10
$ED46 helper graph             -> preserves $10
raw bank $0C : CPU $89E2      -> unresolved
$E7FB / inline dispatch        -> unresolved
PRG26 renderer                 -> consumes/persists $10 exactly
```

## Authoritative continuation files

- `docs/DECOMPILATION_CONTINUITY.md`
- `docs/PROGRESS.md`
- `docs/PROGRESS_METRIC.md`
- `docs/ROM_IDENTITY.md`
- `analysis/PROGRESS_SCORE.csv`
- `analysis/PRG31_boot_and_interrupts.asm`
- `analysis/PRG02_IRQ_dispatch.md`
- `analysis/IRQ_STATE_MACHINE.csv`
- `analysis/IRQ_ZP10_PRESERVATION.md`
- `analysis/NMI_FIXED_ZP10_PRESERVATION.md`
- `analysis/NMI_ED46_ZP10_PRESERVATION.md`
- `analysis/PRG26_SPRITE_FORMAT.md`
- `analysis/ZP10_OAM_STATE.md`
- `analysis/PRG26_9FA9_INCOMING_ATTR.md`
- `src/oam_renderer.*`
- `tests/oam_renderer_test.cpp`
- current audit scripts under `tools/`

## Unresolved / do not assume

- whether bank `$0C:$89E2` can write ZP `$10` before `PRG26:$8001`;
- whether `$E7FB` or its inline-dispatch targets can write ZP `$10` before rendering;
- whole-ROM type-transition / selector-frame producer closure;
- higher-level meaning of `$AD`;
- semantic identities of individual sprite descriptors;
- exact visual/game-state meanings of IRQ states;
- conservative ROM-byte code/data coverage companion metric.

## Next manageable checkpoint

**04F5 — bank `$0C:$89E2` pre-render helper only.** Start with physical `PRG24:$8800-$8BFF` (1 KiB), because raw VRC6 bank `$0C` maps CPU `$8000-$9FFF` to PRG24. Follow only the control flow reachable from CPU `$89E2`; expand within the 500-5000-byte budget only if necessary to close the same question. Determine whether this NMI-called banked path can modify ZP `$10`. Do not open `$E7FB` in the same checkpoint.
