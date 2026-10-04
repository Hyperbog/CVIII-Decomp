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

## Checkpoint 04E4 — PRG06 `$823E` owner and scheduler link

The fixed active-object loop processes X slots `$01-$12`. Primary type `$08` routes through bank `$09` common dispatch to VRC6 bank `$03`, behavior `PRG06:$8021`.

Internal state `$0606,X=$01` selects the `$81E0` path, which writes `$0470,X=$40` and can reach `$823E`. If base Y is `$A0-$A7`, `$823E` installs selector `$10` / animation `$09`. The same fixed-loop iteration can then run movement integration and `$FE60: JSR $EF93` for the same X slot.

Renderer mapping: selector `$10` -> table `$9E6D`; frame `$14` -> descriptor `$9FA9`.

Evidence: `analysis/PRG06_TYPE08_823E_OWNER.md`, `tools/audit_prg06_type08_owner.py`.

## Checkpoint 04E5 — type `$08` vertical path

State `$00` initializes:

```text
$041C,X = $C0
$0537,X = $00
$0520,X = $FE
$0606,X -> $01
```

`$FF15` clears the movement bytes before `$0520=$FE` is installed. In state `$01`, there is no direct write/inc/dec of `$0520/$0537` before `$823E`.

The bank-`$0B` integrator performs low-byte addition followed by high-byte addition. With `$0537=$00` and `$0520=$FE`, scheduled movement changes base Y by exactly `-2` per tick:

```text
$C0,$BE,$BC,...,$AA,$A8,$A6,$A4,$A2,$A0,$9E,...
```

State `$01` gates this movement with target `$840F[$0633+$0645]`. State `$00` also consumes the same sum against the established 15-byte map `$81CE-$81DC`; `$81DD` is independently executable via direct jump `$8148 -> $81DD`. For currently table-valid indices `$00-$0E`, the corresponding target bytes `$840F[0..14]` are:

```text
70 90 70 98 78 98 70 90 70 60 50 60 70 60 50
```

Maximum target is `$98`. Therefore every object operating inside that established index domain necessarily continues through Y=`$A6`, which lies in `$A0-$A7` and makes `$823E` select animation `$09`.

This closes the motion/threshold part of the `$9FA9` reachability chain, but **does not yet close root producer values of `$0645,X`**. Do not infer its bound solely from table shape.

Evidence: `analysis/PRG06_TYPE08_VERTICAL_PATH.md`, `tools/audit_prg06_type08_vertical_path.py`.

**VPP remains 21/100 after 04E5.** This is a reachability refinement, not another completed fixed-rubric milestone.

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
- `analysis/PRG06_TYPE08_VERTICAL_PATH.md`
- `src/oam_renderer.*`
- `tests/oam_renderer_test.cpp`
- current audit scripts under `tools/`

## Unresolved / do not assume

- root/creation producer domain of `$0645,X` for primary type `$08`
- unconditional normal-gameplay reachability of `$9FA9` until that producer domain is closed
- incoming cached attribute `$10` at the first compressed sprite of reachable `$9FA9`
- whether render ordering guarantees a prior explicit-attribute sprite before `$9FA9`
- whole-ROM selector/frame producer closure
- higher-level meaning of `$AD`
- semantic identities of individual sprite frames/descriptors
- exact visual/game-state meanings of IRQ states
- conservative ROM-byte code/data coverage companion metric

## Next manageable checkpoint

**04E6: primary-type `$08` `$0645` producer domain only.** Trace root/creation writes that establish `$0645,X` before type `$08` state `$00`, and prove whether `$0633+$0645` stays within the established `$00-$0E` consumer domain. Do not expand into renderer cached-attribute `$10` ordering yet. Update VPP only if the fixed rubric earns another point.
