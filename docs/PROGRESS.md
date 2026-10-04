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

### Master frame-table census

Five physical master pointer blocks are now proven:

- A `$819D-$82F4`: 172 pointers
- B `$8AB0-$8C2D`: 191 pointers
- C `$9545-$9620`: 110 pointers
- D `$9E6D-$9F6C`: 128 pointers
- E `$AAA6-$AC5B`: 219 pointers

The 15 first-level selector targets are windows into these masters, not 15 independent tables. `analysis/SPRITE_MASTER_TABLES.csv` records the entry offsets/ranges.

`tools/audit_sprite_descriptors.py` verifies all referenced descriptors:

- 745 unique descriptor pointers
- maximum 27 sprites per descriptor
- maximum encoded length 96 bytes
- 2,310 compressed attribute-reuse records
- `$9FA9` is the only referenced descriptor whose first sprite is compressed

### `$0454` correction

When nonzero, the machine operation is `(descriptor_attribute & $FC) | $0454,X`. The object byte is not masked to two bits; direct producers can supply values above `$03`.

## Native OAM baseline added

The first faithful native subsystem now exists:

- `src/oam_renderer.hpp`
- `src/oam_renderer.cpp`
- `tests/oam_renderer_test.cpp`

The lift keeps NES RAM explicit and preserves 8-bit pointer-index wrap, variable descriptor width, persistent `$10`, full-byte `$0454` OR semantics, mirror/tile transforms, signed X clipping, OAM permutation, and the `$8070` non-local OAM-full exit via an explicit propagated result.

The test suite includes a first-record compression regression: it seeds incoming `$10=$A7`, starts the object's descriptor with a compressed record, and verifies that exact cached byte is emitted unchanged.

## Checkpoint 04B — zero-page `$10` lifetime at renderer entry

Inside the proven `$8001-$817E` renderer region:

- `$8064`: `LDA $10` — compressed non-mirrored record
- `$80BF`: `STA $10` — cache final non-mirrored explicit attribute
- `$811B`: `STA $10` — cache final mirrored explicit attribute
- `$8166`: `LDA $10` — compressed mirrored record

There is no renderer-side initialization before object processing. Direct gameplay code in VRC6 bank `$03` also uses `$10` as unrelated scratch, proving it is shared zero-page machine state rather than renderer-private storage.

Evidence: `analysis/ZP10_OAM_STATE.md`; audit: `tools/audit_oam_zp10.py`.

## Checkpoint 04C — `$9FA9` reachability boundary

`$9FA9` requires selector `$048C[slot]=$10` plus frame `$0400[slot]=$14`.

Checked direct selector-`$10` setup paths use high frame values (`$F0`, `$F4-$FE`, `$D2/$C0/$C6/$CC/$E4/$E0`, `$E8/$EC`), not `$14`.

PRG22 `$8745` writes frame `$14` without locally writing the selector, making it the first candidate for a persistent-selector transition. Full notes: `analysis/PRG26_9FA9_REACHABILITY.md`.

## Checkpoint 04D — owner of PRG22 `$8745`

Direct dispatcher/state-table reconstruction rejects `$8745` as the selector-`$10` route.

The PRG23 object dispatcher uses `$05EF,X` as object type and `$05C1,X` as a four-byte state-record index. Object type `$26` points to state table `$AE6A-$AF29` (48 states).

Action dispatch proves:

- action `$5C` -> `PRG22:$871E`
- action `$8A` -> `PRG22:$86F2`
- both can reach the shared `$8734-$874D` tail containing `$8745: LDA #$14 / STA $0400,X`

Within type `$26`, the two normal action-`$5C` entries are immediately preceded by explicit action-`$0B` sprite setup:

- state `$07`: `0B 12 12 00` -> selector `$12`, frame `$12`
- state `$08`: action `$5C`
- state `$13`: `0B 12 12 00` -> selector `$12`, frame `$12`
- state `$14`: action `$5C`

Enumerating every action-`$0B` record in the complete type-`$26` table shows that its explicit selector values are only `$12` and `$08`; selector `$10` never occurs.

Therefore `$8745` belongs to the type-`$26` `$12/$08` sprite-set family and does **not** establish the missing selector-`$10` + frame-`$14` path to `$9FA9`.

Evidence: `analysis/PRG22_8745_OWNER.md`; audit: `tools/audit_prg22_8745_owner.py`.

## Checkpoint 04E1 — PRG18 type `$E1` selector-`$10` closure

This checkpoint closes one proven selector-`$10` family without expanding into the PRG06 families.

PRG18 creation code at `$9DE0-$9E1B` sets:

- type `$05EF = $E1`
- selector `$048C = $10`
- state `$05C1 = 0`
- initial frame `$0400 = $E8` or `$EC`

The PRG18/19 dispatcher maps type `$E1` to exactly six two-byte state records at `$8FC4-$8FCF`.

The only frame mutation in that six-state path is state `$04`, action `$46`, parameter index `$58`. The three parameter bytes are `FF 00 FF`. Action `$46` interprets the first `$FF` as two `INC $0400,X` operations.

Thus the complete proven type-`$E1` frame evolution is:

```text
$E8 -> $EA
or
$EC -> $EE
```

State `$05` resolves to `$8662`, which is `RTS`. Type `$E1` therefore cannot produce selector `$10` + frame `$14` through its authoritative state machine and does not establish `$9FA9` reachability.

Evidence: `analysis/PRG18_E1_SELECTOR10_FRAME.md`; audit: `tools/audit_prg18_e1_frame.py`.

**VPP remains 21/100 after 04E1.** This closure is useful evidence but does not complete another point in the fixed gameplay/object-system rubric.

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
18. `src/oam_renderer.hpp`
19. `src/oam_renderer.cpp`
20. `tests/oam_renderer_test.cpp`
21. `tools/progress_score.py`
22. current ROM/subsystem audit scripts under `tools/`

## Unresolved / do not assume

- whether any PRG06 selector-`$10` family can mutate `$0400` to `$14`
- actual reachable mechanism, if any, producing selector `$10` plus frame `$14`
- which object slots can reach `$9FA9`
- whether object ordering guarantees a prior explicit-attribute sprite before `$9FA9`
- exact preceding `$10` value on every reachable `$9FA9` path
- whole-ROM proof of every `$048C` producer and invalid-selector impossibility
- producer-domain closure for `$0400` frame offsets
- exact higher-level meaning of global `$AD`
- semantic identities of individual frame tables/descriptors
- gameplay meaning/producers of every `$0400-$04C3` field beyond proven renderer behavior
- exact visual/game-state meanings of IRQ states `$00-$2C`
- conservative ROM-byte code/data coverage metric (future companion metric, not VPP)

## Next manageable checkpoint

**04E2: PRG06 selector-`$10` families only.** Enumerate the direct PRG06 selector-`$10` setup/helper paths and trace their frame mutations far enough to determine whether any authoritative PRG06 path can produce frame `$14`. Do not expand into unrelated banks/object families. Update VPP only if the fixed rubric actually earns another point.
