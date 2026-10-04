# Decompilation progress ledger

## Current status

Work proceeds in **small bounded checkpoints**: one narrow binary question, direct ROM verification, focused artifact/audit update, commit, then stop.

Primary high-level progress metric: **Verified Parity Progress (VPP) = 21 / 100 (21%)**.

VPP is a fixed evidence rubric, not a time estimate or raw disassembly-byte percentage. See `docs/PROGRESS_METRIC.md`, `analysis/PROGRESS_SCORE.csv`, and `tools/progress_score.py`.

## Stable foundation

- Verified immutable Japanese `Akumajou Densetsu` Mapper-24 ROM identity.
- PRG modeled as 32 physical 8 KiB banks (`PRG00..PRG31`).
- Fixed vectors: RESET `$E00B`, NMI `$E057`, IRQ `$E0F5`.
- VRC6 PRG helpers: tracked bank in `$23`, raw/tracked selectors `$E2D2/$E2D0`, `$C000` 8 KiB selector via `$E2C4`.
- NMI bank `$0D` call `$8001` resolves to `PRG26:$8001`.
- IRQ raw bank `$01` resolves its table/handlers into `PRG02/PRG03`.

## Batch 02 — IRQ state machine

Authoritative IRQ table is `PRG02:$9F01-$9F5A`: 45 entries / states `$00-$2C`; `$9F5B` is code. The old `$9F60` overlap hypothesis was disproved. Normal states are `$00-$2C`; `$80` is a high-bit bypass sentinel.

The fixed exits are distinct: `$E118` clears VRC6 IRQ Control `$F001`; `$E11D` acknowledges via `$F002` and restores the tracked bank.

Evidence: `analysis/PRG02_IRQ_dispatch.md`, `analysis/IRQ_STATE_MACHINE.csv`, `tools/audit_irq_dispatch.py`.

## Batch 03 — PRG26 OAM hierarchy/native baseline

`PRG26:$8001` iterates 28 render-object slots in seven 28-byte arrays `$0400-$04C3`. `$048C,X` selects a first-level sprite-set window; `$0400,X` is a frame-pointer byte offset. The 15 selectors resolve into five master pointer blocks.

Sprite descriptors are variable-width: count byte followed by sprite records whose Y/control bit 0 selects either `Y,tile,attribute,X` or compressed `Y,tile,X` reusing persistent zero-page attribute cache `$10`.

`$9FA9` is the only referenced descriptor whose first sprite is compressed; it begins with three compressed records. The renderer preserves OAM slot permutation and the original non-local `PLA; PLA; RTS` OAM-full return.

Native baseline: `src/oam_renderer.hpp`, `src/oam_renderer.cpp`, `tests/oam_renderer_test.cpp`.

## Checkpoint 04B — zero-page `$10` lifetime

Renderer reads `$10` at `$8064/$8166` and updates it at `$80BF/$811B`; it is not initialized at object/descriptor entry. Unrelated gameplay code also uses `$10` as shared scratch.

Evidence: `analysis/ZP10_OAM_STATE.md`, `tools/audit_oam_zp10.py`.

## Checkpoint 04C — `$9FA9` reachability boundary

`$9FA9` requires selector `$048C=$10` plus frame `$0400=$14`. Direct selector-`$10` setup paths initially examined used high frame values rather than `$14`.

Evidence: `analysis/PRG26_9FA9_REACHABILITY.md`.

## Checkpoint 04D — PRG22 `$8745` rejected

PRG22 `$8745` writes frame `$14`, but its owning object type `$26` uses selectors `$12/$08`, not `$10`. It is not the `$9FA9` route.

Evidence: `analysis/PRG22_8745_OWNER.md`, `tools/audit_prg22_8745_owner.py`.

## Checkpoint 04E1 — PRG18 type `$E1` rejected

PRG18 type `$E1` starts selector `$10` at frame `$E8/$EC` and can only mutate to `$EA/$EE` through its six-state table. It cannot reach frame `$14`.

Evidence: `analysis/PRG18_E1_SELECTOR10_FRAME.md`, `tools/audit_prg18_e1_frame.py`.

## Checkpoint 04E2 — direct PRG06/07 selector-`$10` stores

Direct PRG06/07 selector-`$10` setup frames are:

```text
$C0,$C2,$C4,$C6,$C8,$CA,$CC,$CE,
$D0,$D2,$D4,$D6,$E0,$E4,$F0,
$F4,$F6,$F8,$FA,$FC,$FE
```

The bank pair's only literal frame `$14` setup immediately selects `$0E`, not `$10`. Thus direct PRG06/07 frame stores do not establish `$9FA9`.

Evidence: `analysis/PRG06_SELECTOR10_DIRECT_DOMAIN.md`, `tools/audit_prg06_selector10_direct.py`.

## Checkpoint 04E3 — fixed animation system supplies frame `$14`

PRG06 `$823E-$8251` selects animation ID from base Y `$041C,X`: Y `>= $A8` -> `$08`; Y `$A0-$A7` -> `$09`; Y `< $A0` -> `$0A`. It then loads A=`$10` and tail-calls fixed helper `$EF7F`.

`$EF7F` installs selector `$10`, the animation ID, cursor zero, and timer one. Fixed updater `$EF93/$EF99` uses those fields and writes the resulting frame to `$0400,X` at `$EFB5`.

Selector `$10` points to animation table `$F272-$F37C`; animation ID `$09` is `$F28D: 14 08 02`. Its first update therefore writes frame `$14`.

Evidence: `analysis/PRG06_SELECTOR10_FIXED_ANIM.md`, `tools/audit_prg06_fixed_animation.py`.

**VPP remained 21/100 after 04E3.**

## Checkpoint 04E4 — PRG06 `$823E` owner and scheduler link

The fixed active-object loop processes X slots `$01-$12`. Primary types below `$30` are routed through VRC6 bank `$09`'s common dispatcher. For primary type `$08`, that dispatcher resolves:

```text
bank selector = $03
behavior pointer = $8021
```

so type `$08` executes `PRG06:$8021` with the same object-slot X.

Within PRG06, internal state `$0606,X=$01` selects the `$81E0` path, which writes `$0470,X=$40` and can reach `$823E`. If base Y `$041C,X` is `$A0-$A7`, `$823E` installs selector `$10` / animation ID `$09` through `$EF7F`.

After object-specific behavior returns, the same fixed-loop iteration observes `$0470` bit `$40` set and can run the bank-`$0B` movement integrator; bit `$20` is clear, so it then reaches `$FE60: JSR $EF93` for the same X slot. Checkpoint 04E3 proves that animation ID `$09` under selector `$10` writes frame `$14`.

The renderer mapping then resolves:

```text
selector $10 -> frame table $9E6D
frame offset $14 -> descriptor $9FA9
```

Thus the exact machine path is now proven conditionally:

```text
fixed slot X=$01..$12
primary type $08
  -> bank-$09 common dispatcher
  -> bank-$03 PRG06:$8021
  -> internal state $01
  -> base Y $A0-$A7
  -> selector $10 / animation $09
  -> same fixed-loop scheduler reaches $EF93
  -> frame $14
  -> PRG26 descriptor $9FA9
```

What is **not yet proved** is normal-gameplay provenance of the base-Y predicate `$A0-$A7`. Therefore `$9FA9` is machine-reachable under a fully reconciled state predicate, but normal-gameplay reachability is not yet claimed.

Evidence: `analysis/PRG06_TYPE08_823E_OWNER.md`, `tools/audit_prg06_type08_owner.py`.

**VPP remains 21/100 after 04E4.** This resolves owner/slot/scheduler structure but does not complete another fixed gameplay/object-system rubric point.

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
- `analysis/SPRITE_SET_TABLE.csv`
- `analysis/SPRITE_MASTER_TABLES.csv`
- `analysis/OAM_OBJECT_FIELDS.csv`
- `analysis/ZP10_OAM_STATE.md`
- `analysis/PRG26_9FA9_REACHABILITY.md`
- `analysis/PRG22_8745_OWNER.md`
- `analysis/PRG18_E1_SELECTOR10_FRAME.md`
- `analysis/PRG06_SELECTOR10_DIRECT_DOMAIN.md`
- `analysis/PRG06_SELECTOR10_FIXED_ANIM.md`
- `analysis/PRG06_TYPE08_823E_OWNER.md`
- `src/oam_renderer.*`
- `tests/oam_renderer_test.cpp`
- current audit scripts under `tools/`

## Unresolved / do not assume

- whether a normal primary-type `$08`, internal-state `$01` path actually attains base Y `$A0-$A7`
- incoming cached attribute `$10` at the first compressed sprite of reachable `$9FA9`
- whether render ordering guarantees a prior explicit-attribute sprite before `$9FA9`
- whole-ROM selector/frame producer closure
- higher-level meaning of `$AD`
- semantic identities of individual sprite frames/descriptors
- exact visual/game-state meanings of IRQ states
- conservative ROM-byte code/data coverage companion metric

## Next manageable checkpoint

**04E5: base-Y `$A0-$A7` provenance only.** Trace primary type `$08`, internal state `$01` from its authoritative initialization and velocity/update path far enough to prove or disprove that normal execution reaches `$041C,X=$A0-$A7`. Do not expand into cached-attribute `$10` ordering yet. Update VPP only if the fixed rubric earns another point.
