# Decompilation progress ledger

## Current status

Work proceeds in **small bounded checkpoints**: one narrow question, direct ROM verification, focused artifact/audit update, commit, then stop.

Byte-budget policy: default to roughly **1 KiB of new ROM span per checkpoint**, with an allowed range of about **500-5000 bytes**. Stop and report before expanding beyond that span unless a few isolated signatures are needed to prove the same question.

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

PRG06 `$823E-$8251` chooses animation ID `$09` when base Y is `$A0-$A7` and installs selector `$10`. Fixed selector-`$10` animation record `$09` is `$F28D: 14 08 02`, so `$EF93` writes frame `$14`.

### 04E4 — owner/scheduler link

The fixed active-object loop processes slots `$01-$12`. Primary type `$08` routes through the common dispatcher to `PRG06:$8021`. Internal state `$01` reaches `$81E0`, sets `$0470=$40`, and can reach `$823E`. The same scheduler iteration can run movement integration and `$EF93`.

Renderer resolution:

```text
selector $10 -> table $9E6D
frame $14    -> descriptor $9FA9
```

### 04E5 — deterministic vertical path

State `$00` initializes base Y `$C0` and exact vertical velocity `-2`. The bank-`$0B` movement integrator therefore steps `$C0,$BE,...,$A8,$A6,$A4,$A2,$A0,...` while state `$01` is active. For the established consumer domain, the target table max is `$98`, so the `$A0-$A7` animation-`$09` window is necessarily crossed.

### 04E6 — root `$0645` producer closure

Normal low-type construction clears `$0606/$061D/$0633/$0645` before type `$08` is stored. The PRG20 constructor that later writes room-position byte `$73` to `$0645` is a high-type-only spawner path; its audited record tables contain no type `$08` record.

Thus normal root type `$08` begins with `$0633=$0645=0`. State `$00` makes the first state-1 index exactly `$01`, with target `$840F[$01]=$90`.

Therefore the normal state-machine path necessarily reaches selector `$10` + frame `$14` and renders descriptor `$9FA9`.

Evidence:

- `analysis/PRG06_TYPE08_823E_OWNER.md`
- `analysis/PRG06_TYPE08_VERTICAL_PATH.md`
- `analysis/PRG06_TYPE08_0645_PRODUCERS.md`
- `tools/audit_prg06_type08_owner.py`
- `tools/audit_prg06_type08_vertical_path.py`
- `tools/audit_prg06_type08_0645.py`

### 04F1 — incoming `$10` is inherited variable state

Primary ROM span for this checkpoint: PRG26 `$8001-$81FF` plus isolated verification of `$9FA9` and two PRG28 slot-0 mirror-state writes.

The outer renderer walks slots strictly upward from `$00` through `$1B` and does not initialize ZP `$10`. Compressed records read `$10`; full records store their final transformed attribute into `$10`.

`$9FA9` begins:

```text
04 DF 8A F0  E1 8C F8  E5 8E 00  04 E4 90 03
```

Its first three records are compressed. Therefore their attribute is inherited from prior shared renderer state.

The value is **not a single game constant**. It is:

- the final explicit attribute emitted by the highest lower-index object that rendered earlier in the frame; or
- the pre-render shared RAM value if no lower slot emitted an explicit attribute.

JP PRG28 also contains immediate writes of both `1` and `0` to slot-0 `$04A8`. Since `$04A8==0` selects the mirror path and the mirror path XORs `$40` before updating `$10`, an earlier slot can legitimately leave different cache values solely from mirror state.

The native regression suite already includes `test_cache_persists_across_object_boundary()`, which verifies that a compressed record in a later object consumes the prior object's cached attribute.

Evidence:

- `analysis/PRG26_9FA9_INCOMING_ATTR.md`
- `tools/audit_prg26_9fa9_cache.py`
- `tests/oam_renderer_test.cpp`

**VPP remains 21/100 after 04F1.** This closes an exact renderer-state contract but does not complete another fixed-rubric point.

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
- `analysis/PRG26_9FA9_INCOMING_ATTR.md`
- `analysis/PRG06_SELECTOR10_FIXED_ANIM.md`
- `analysis/PRG06_TYPE08_823E_OWNER.md`
- `analysis/PRG06_TYPE08_VERTICAL_PATH.md`
- `analysis/PRG06_TYPE08_0645_PRODUCERS.md`
- `src/oam_renderer.*`
- `tests/oam_renderer_test.cpp`
- current audit scripts under `tools/`

## Unresolved / do not assume

- whether any verified IRQ handler can write ZP `$10` between NMI `CLI` and the PRG26 renderer call
- whole-ROM type-transition / selector-frame producer closure
- higher-level meaning of `$AD`
- semantic identities of individual sprite descriptors
- exact visual/game-state meanings of IRQ states
- conservative ROM-byte code/data coverage companion metric

## Next manageable checkpoint

**04F2 — IRQ-side `$10` interference only.** Restrict new ROM analysis to the verified IRQ handler region `PRG02/PRG03:$9F99-$A526` (about 1.4 KiB) plus the fixed IRQ entry/exit signatures already mapped. Determine whether any reachable IRQ handler can write ZP `$10` during the NMI window before `PRG26:$8001`. Do not expand into other gameplay banks or background rendering.
