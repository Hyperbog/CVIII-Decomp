# Decompilation progress ledger

## Current status

Project initialized from the verified Japanese `Akumajou Densetsu` Mapper-24 ROM. Work is proceeding in **small bounded checkpoints**: one narrow binary question, direct ROM verification, documentation/audit/test update, commit, then stop.

Primary high-level progress metric: **Verified Parity Progress (VPP) = 21 / 100 (21%)**.

VPP is a fixed evidence rubric, not a time estimate or raw disassembly-byte percentage. See `docs/PROGRESS_METRIC.md`, `analysis/PROGRESS_SCORE.csv`, and `tools/progress_score.py`. Useful micro-checkpoints may leave the score unchanged; points are added only when a larger committed parity milestone satisfies the fixed rubric.

## Stable foundation

- Verified immutable ROM identity and iNES mapper/size information.
- PRG modeled as 32 physical 8 KiB banks (`PRG00..PRG31`).
- Fixed vectors: RESET `$E00B`, NMI `$E057`, IRQ `$E0F5`.
- VRC6 PRG helpers: tracked 16 KiB bank in `$23`, raw/tracked selectors `$E2D2/$E2D0`, `$C000` 8 KiB selector via `$E2C4`.
- NMI bank `$0D` call `$8001` resolves to `PRG26:$8001`.
- IRQ raw bank `$01` resolves table/handlers into `PRG02/PRG03`.

## Batch 02 — IRQ state machine

Authoritative IRQ table is `PRG02:$9F01-$9F5A`: 90 bytes / 45 entries / states `$00-$2C`. `$9F5B` is executable code. The old `$9F60` overlap hypothesis was disproved and must not be restored.

Normal active states are `$00-$2C`; `$80` is a high-bit bypass sentinel. Highest explicit chain: `29 -> 2A -> 2B -> 2C`, with `$2C` terminal/non-incrementing.

The fixed exits are distinct:

- `$E118` clears VRC6 IRQ Control `$F001`, then falls through
- `$E11D` acknowledges via `$F002` and restores the tracked PRG bank

Ledger: `analysis/IRQ_STATE_MACHINE.csv`.

## Batch 03 — PRG26 OAM hierarchy

`PRG26:$8001` iterates 28 render-object slots backed by seven consecutive 28-byte arrays `$0400-$04C3`.

`$048C,X` indexes the first-level pointer block `$817F-$819C` with even byte offsets `$00..$1C`. High selectors `$16/$18/$1A/$1C` alias the first four geometry tables and can select tile `+$80` behavior under the encoded `$AD` path.

OAM byte offset advances by `$C4` per sprite and frame seed by `$44`. When all 64 OAM slots are consumed, `$8070` executes `PLA; PLA; RTS`, discarding its own return and returning directly to `$8001`'s caller.

## Checkpoint 04A — corrected variable-length sprite descriptors

Descriptor byte 0 is sprite count. Each sprite begins with a packed Y/control byte. The renderer performs a signed arithmetic right shift via sign-selected carry + `ROR`; the outgoing carry is the original bit 0.

- bit 0 clear: `Y/control, tile, attribute, X` — 4 bytes
- bit 0 set: `Y/control, tile, X` — 3 bytes; attribute is reused from zero-page `$10`

Full records store the final transformed OAM attribute into `$10`; compressed records consume `$10` directly. `$8001/$8070` do not initialize `$10` at object/descriptor entry.

Descriptor `$9FA9` begins with three compressed records before its first explicit attribute, proving a per-descriptor reset would be wrong.

Five physical master pointer blocks are proven; `tools/audit_sprite_descriptors.py` verifies 745 unique referenced descriptors, maximum 27 sprites, maximum encoded length 96 bytes, and 2,310 compressed attribute-reuse records.

When `$0454,X` is nonzero, the exact machine operation is `(descriptor_attribute & $FC) | $0454,X`; the object byte is not masked to two bits.

## Native OAM baseline

The first faithful native subsystem exists in:

- `src/oam_renderer.hpp`
- `src/oam_renderer.cpp`
- `tests/oam_renderer_test.cpp`

The lift preserves 8-bit pointer-index wrap, variable descriptor width, persistent `$10`, full-byte `$0454` OR semantics, mirror/tile transforms, signed X clipping, OAM permutation, and the `$8070` non-local OAM-full exit.

## Checkpoint 04B — zero-page `$10` lifetime

Inside `$8001-$817E`, `$10` is read at `$8064/$8166` and updated at `$80BF/$811B`. There is no renderer-side initialization before object processing. Bank-$03` gameplay code also uses `$10` as unrelated scratch, proving it is shared zero-page state rather than renderer-private storage.

Evidence: `analysis/ZP10_OAM_STATE.md`; audit: `tools/audit_oam_zp10.py`.

## Checkpoint 04C — `$9FA9` reachability boundary

`$9FA9` requires selector `$048C[slot]=$10` plus frame `$0400[slot]=$14`.

Checked direct selector-`$10` setup paths use high frame values, not `$14`. PRG22 `$8745` writes frame `$14` without locally writing the selector, making it the first candidate persistent-selector transition.

Evidence: `analysis/PRG26_9FA9_REACHABILITY.md`.

## Checkpoint 04D — owner of PRG22 `$8745`

Dispatcher/state-table reconstruction rejects `$8745` as the selector-`$10` route. `$8745` belongs to object type `$26`; that state machine's explicit selectors are only `$12/$08`, and its ordinary `$871E` entries are directly preceded by selector `$12` setup.

Evidence: `analysis/PRG22_8745_OWNER.md`; audit: `tools/audit_prg22_8745_owner.py`.

## Checkpoint 04E1 — PRG18 type `$E1` selector-`$10` closure

PRG18 type `$E1` starts selector `$10` at frame `$E8` or `$EC`. Its six-state table has only one frame mutation: two increments, producing `$EA` or `$EE`. It cannot reach frame `$14` through its authoritative state machine.

Evidence: `analysis/PRG18_E1_SELECTOR10_FRAME.md`; audit: `tools/audit_prg18_e1_frame.py`.

**VPP remained 21/100 after 04E1.**

## Checkpoint 04E2 — PRG06/07 direct selector-`$10` domain

This checkpoint inventories direct indexed writes to renderer selector `$048C` and frame `$0400` in VRC6 bank `$03` (`PRG06/PRG07`).

Direct selector stores occur only at `$8D4F,$8EB9,$8EF9,$9479,$9482`. `$8D4F` stores selector `$0E`; the other four explicitly store selector `$10`.

Direct frame stores occur only at:

- X: `$8E34,$8EF4,$9474,$9ADB,$9C58,$9D19`
- Y: `$8D4A,$8DFA,$8ED5,$947D`

The bank pair contains no direct indexed `INC/DEC $0400,X`.

The **only literal frame `$14` setup** is `$8D4A`, and the same setup immediately writes selector `$0E` at `$8D4F`.

The canonical helpers `$9474/$947D` store the supplied A value as frame and then force selector `$10`. Reconciliation of every absolute call/jump to those helpers and their local tables gives this directly proven selector-`$10` frame domain:

```text
$C0,$C2,$C4,$C6,$C8,$CA,$CC,$CE,
$D0,$D2,$D4,$D6,$E0,$E4,$F0,
$F4,$F6,$F8,$FA,$FC,$FE
```

Frame `$14` is absent. `$9ADB`, another apparently dynamic frame store, follows fixed helper `$FF24`; `$FF24` returns with A=`$00`, so that site stores frame zero.

Therefore **no direct indexed PRG06/07 selector-`$10` setup path produces frame `$14`**. This does not yet close transitive mutation through fixed-bank/shared helpers or another PRG bank.

Evidence: `analysis/PRG06_SELECTOR10_DIRECT_DOMAIN.md`; audit: `tools/audit_prg06_selector10_direct.py`.

**VPP remains 21/100 after 04E2.** This is useful reachability closure but does not satisfy another full rubric point.

## Authoritative continuation files

1. `docs/DECOMPILATION_CONTINUITY.md`
2. `docs/PROGRESS.md`
3. `docs/PROGRESS_METRIC.md`
4. `docs/ROM_IDENTITY.md`
5. `analysis/PROGRESS_SCORE.csv`
6. `analysis/PRG31_boot_and_interrupts.asm`
7. `analysis/PRG02_IRQ_dispatch.md`
8. `analysis/IRQ_STATE_MACHINE.csv`
9. `analysis/PRG26_OAM_frame.md`
10. `analysis/PRG26_SPRITE_FORMAT.md`
11. `analysis/SPRITE_SET_TABLE.csv`
12. `analysis/SPRITE_MASTER_TABLES.csv`
13. `analysis/OAM_OBJECT_FIELDS.csv`
14. `analysis/ZP10_OAM_STATE.md`
15. `analysis/PRG26_9FA9_REACHABILITY.md`
16. `analysis/PRG22_8745_OWNER.md`
17. `analysis/PRG18_E1_SELECTOR10_FRAME.md`
18. `analysis/PRG06_SELECTOR10_DIRECT_DOMAIN.md`
19. `src/oam_renderer.hpp`
20. `src/oam_renderer.cpp`
21. `tests/oam_renderer_test.cpp`
22. `tools/progress_score.py`
23. current ROM/subsystem audit scripts under `tools/`

## Unresolved / do not assume

- transitive fixed-bank/shared-helper frame mutation for PRG06 selector-`$10` objects
- actual reachable mechanism, if any, producing selector `$10` plus frame `$14`
- which object slots can reach `$9FA9`
- whether object ordering guarantees a prior explicit-attribute sprite before `$9FA9`
- exact preceding `$10` value on every reachable `$9FA9` path
- whole-ROM proof of every `$048C` producer and invalid-selector impossibility
- producer-domain closure for `$0400` frame offsets
- exact higher-level meaning of global `$AD`
- semantic identities of individual frame tables/descriptors
- exact visual/game-state meanings of IRQ states `$00-$2C`
- conservative ROM-byte code/data coverage metric (future companion metric, not VPP)

## Next manageable checkpoint

**04E3: PRG06 transitive frame mutation through shared/fixed helpers only.** Starting from the proven PRG06 selector-`$10` setup paths, inspect only calls into fixed/shared routines that can write or derive `$0400` for the same object. Determine whether any such path can create frame `$14`. Do not expand into unrelated object families or stage logic. Update VPP only if the fixed rubric earns another point.
