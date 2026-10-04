# Decompilation progress ledger

## Current status

Work proceeds in **small bounded checkpoints**: one narrow binary question, direct ROM verification, focused artifact/audit update, commit, then stop.

Primary high-level progress metric: **Verified Parity Progress (VPP) = 21 / 100 (21%)**.

VPP is a fixed evidence rubric, not a time estimate or raw disassembly-byte percentage. See `docs/PROGRESS_METRIC.md`, `analysis/PROGRESS_SCORE.csv`, and `tools/progress_score.py`.

## Stable foundation

- Exact Japanese `Akumajou Densetsu` Mapper-24 ROM identity is locked.
- PRG is modeled as 32 physical 8 KiB banks (`PRG00..PRG31`).
- Fixed vectors: RESET `$E00B`, NMI `$E057`, IRQ `$E0F5`.
- VRC6 PRG helpers and fixed/switchable bank contexts are mapped.
- IRQ raw bank `$01` resolves into `PRG02/PRG03`.
- NMI bank `$0D` call `$8001` resolves to `PRG26:$8001`.

## IRQ subsystem

`PRG02:$9F01-$9F5A` is the authoritative 45-entry IRQ table for states `$00-$2C`; `$9F5B` is code. `$80` is the high-bit bypass sentinel. The old `$9F60` overlap hypothesis was disproved.

`$E118` and `$E11D` are distinct exits: `$E118` clears VRC6 IRQ Control `$F001`; `$E11D` acknowledges via `$F002` and restores tracked bank state.

Evidence:

- `analysis/PRG02_IRQ_dispatch.md`
- `analysis/IRQ_STATE_MACHINE.csv`
- `tools/audit_irq_dispatch.py`

## OAM/sprite subsystem

`PRG26:$8001` iterates 28 render slots using seven 28-byte arrays `$0400-$04C3`. `$048C,X` selects a sprite-set pointer window; `$0400,X` is the frame-pointer byte offset.

Descriptor records are variable width:

- bit0 clear: `Y,tile,attribute,X`
- bit0 set: `Y,tile,X`, reusing persistent ZP attribute cache `$10`

`$9FA9` is the only referenced descriptor whose first record is compressed; it begins with three compressed records. Native baseline is in `src/oam_renderer.*` with regression tests in `tests/oam_renderer_test.cpp`.

Evidence:

- `analysis/PRG26_OAM_frame.md`
- `analysis/PRG26_SPRITE_FORMAT.md`
- `analysis/SPRITE_SET_TABLE.csv`
- `analysis/SPRITE_MASTER_TABLES.csv`
- `analysis/OAM_OBJECT_FIELDS.csv`
- `analysis/ZP10_OAM_STATE.md`

## `$9FA9` reachability chain

### 04D — PRG22 `$8745` rejected

PRG22 `$8745` writes frame `$14`, but its owning type `$26` uses selectors `$12/$08`, not `$10`.

### 04E1 — PRG18 type `$E1` rejected

Type `$E1` starts selector `$10` at frame `$E8/$EC` and mutates only to `$EA/$EE`.

### 04E2 — direct PRG06/07 stores

Direct selector-`$10` setup frames are high values; the only direct frame `$14` setup is paired with selector `$0E`.

### 04E3 — transitive animation mechanism

PRG06 `$823E-$8251` chooses animation ID `$09` when base Y is `$A0-$A7` and installs selector `$10`. Fixed selector-`$10` animation record `$09` is:

```text
$F28D: 14 08 02
```

so `$EF93` writes frame `$14`.

### 04E4 — owner/scheduler link

The fixed active-object loop processes slots `$01-$12`. Primary type `$08` routes through the common dispatcher to `PRG06:$8021`. Internal state `$01` reaches `$81E0`, sets `$0470=$40`, and can reach `$823E`. The same scheduler iteration can run movement integration and `$EF93`.

Renderer resolution:

```text
selector $10 -> table $9E6D
frame $14    -> descriptor $9FA9
```

### 04E5 — deterministic vertical path

State `$00` initializes:

```text
$041C = $C0
$0537 = $00
$0520 = $FE
$0606 -> $01
```

The bank-`$0B` movement integrator therefore changes Y by exactly `-2` per scheduled tick.

For the established consumer index domain, the state-1 target table max is `$98`, so the trajectory necessarily includes `$A6/$A4/$A2/$A0`, all of which select animation `$09`.

### 04E6 — root `$0645` producer closure

The remaining root-construction uncertainty is now closed for the normal type-`$08` path.

Authoritative JP facts:

- fixed `$FF24` clears `$0606/$061D/$0633/$0645`;
- the standard low-slot allocator `PRG18:$86E3` resets through `$86D1/$8692` before storing its caller-supplied type;
- the PRG20 path that later writes room-position byte `$73` to `$0645` is a **high-type** spawner path only;
- its two pointer tables at `$A56B/$A66B` yield 251 valid pointed records in the audit, with **zero type `$08` records**; nonempty record first bytes are `$80+`;
- the complete PRG contains no literal `LDA #$08 / STA $054E,X` constructor.

Thus normal root type `$08` begins:

```text
$0606 = $00
$0633 = $00
$0645 = $00
```

State `$00` increments/masks `$0633`, making the first state-1 index exactly:

```text
$0633 + $0645 = $01
```

and target:

```text
$840F[$01] = $90
```

Therefore the normal state-machine path necessarily traverses `$A6/$A4/$A2/$A0`, selects animation `$09`, reaches selector `$10` + frame `$14`, and renders descriptor `$9FA9`.

**Normal gameplay `$9FA9` reachability is now proven for this root type-`$08` path.**

Evidence:

- `analysis/PRG06_TYPE08_823E_OWNER.md`
- `analysis/PRG06_TYPE08_VERTICAL_PATH.md`
- `analysis/PRG06_TYPE08_0645_PRODUCERS.md`
- `tools/audit_prg06_type08_owner.py`
- `tools/audit_prg06_type08_vertical_path.py`
- `tools/audit_prg06_type08_0645.py`

**VPP remains 21/100 after 04E6.** This closes a reachability dependency but does not yet complete another fixed-rubric gameplay/object-system point.

## Authoritative continuation files

- `docs/DECOMPILATION_CONTINUITY.md`
- `docs/PROGRESS.md`
- `docs/PROGRESS_METRIC.md`
- `docs/ROM_IDENTITY.md`
- `analysis/PROGRESS_SCORE.csv`
- `analysis/PRG31_boot_and_interrupts.asm`
- `analysis/PRG02_IRQ_dispatch.md`
- `analysis/IRQ_STATE_MACHINE.csv`
- `analysis/PRG26_OAM_frame.md`
- `analysis/PRG26_SPRITE_FORMAT.md`
- `analysis/ZP10_OAM_STATE.md`
- `analysis/PRG06_SELECTOR10_FIXED_ANIM.md`
- `analysis/PRG06_TYPE08_823E_OWNER.md`
- `analysis/PRG06_TYPE08_VERTICAL_PATH.md`
- `analysis/PRG06_TYPE08_0645_PRODUCERS.md`
- `src/oam_renderer.*`
- `tests/oam_renderer_test.cpp`
- current audit scripts under `tools/`

## Unresolved / do not assume

- incoming cached attribute `$10` at the first compressed record of reachable `$9FA9`
- whether object/render ordering guarantees the intended prior explicit-attribute value before `$9FA9`
- whole-ROM type-transition / selector-frame producer closure
- higher-level meaning of `$AD`
- semantic identities of individual sprite descriptors
- exact visual/game-state meanings of IRQ states
- conservative ROM-byte code/data coverage companion metric

## Next manageable checkpoint

**04F1 — reachable `$9FA9` incoming ZP `$10` only.** Trace the render ordering and immediately preceding attribute-cache writer for the proven type-`$08` `$9FA9` object. Determine the exact `$10` value consumed by its first compressed record, or prove that it is intentionally inherited from a variable prior object. Do not expand into unrelated sprite descriptors or background rendering.
