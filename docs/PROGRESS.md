# Decompilation progress ledger

## Current status

Project initialized from the verified Japanese `Akumajou Densetsu` Mapper-24 ROM. Work is proceeding in **small bounded checkpoints**: one narrow binary question, direct ROM verification, documentation/audit update, commit, then stop. No global translated-byte percentage is claimed yet; whole-PRG accounting remains intentionally deferred until the denominator is conservative and reproducible.

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

The lift keeps NES RAM explicit and preserves 8-bit pointer-index wrap, variable descriptor width, persistent `$10`, full-byte `$0454` OR semantics, mirror/tile transforms, signed X clipping, OAM permutation, and the `$8070` non-local OAM-full exit via an explicit propagated result. Current C++17 regression tests compile cleanly with `-Wall -Wextra -pedantic` and pass.

## Checkpoint 04B — zero-page `$10` lifetime at renderer entry

This checkpoint was intentionally limited to `$10` state ownership.

### Proven renderer accesses

Inside the proven `$8001-$817E` renderer region:

- `$8064`: `LDA $10` — compressed non-mirrored record
- `$80BF`: `STA $10` — cache final non-mirrored explicit attribute
- `$811B`: `STA $10` — cache final mirrored explicit attribute
- `$8166`: `LDA $10` — compressed mirrored record

There is no renderer-side initialization before object processing.

### NMI boundary

The top-level fixed-bank NMI instruction stream from `$E057` through the bank-$0D call at `$E0C7` contains no direct `STA/STX/STY $10`. This is deliberately **not** a transitive claim about every helper called by NMI.

### Shared scratch proof

Direct gameplay code in VRC6 bank `$03` uses the same byte for unrelated temporary state:

- bank03 `$9752`: `STA $10`
- bank03 `$9769`: `LDA $10`, then stores the value into object base-X state

Thus `$10` is not renderer-private storage or a descriptor-local cache initializer. It is shared zero-page machine state that the renderer consumes and conditionally overwrites.

### Consequence for `$9FA9`

No dedicated initializer has been proved before `$9FA9`; the bytes prove the opposite architectural requirement: the descriptor consumes the **pre-existing shared RAM value** until a full record updates it. A faithful native baseline must therefore expose `$10` through shared NES RAM and must not invent a renderer/object/descriptor default.

What remains unresolved is which exact preceding write/value is observed on every reachable gameplay path to `$9FA9` and whether object ordering guarantees a preceding full sprite record. That is now a separate reachability/scheduling question.

Evidence: `analysis/ZP10_OAM_STATE.md`; reproducible audit: `tools/audit_oam_zp10.py`.

## Authoritative continuation files

1. `docs/DECOMPILATION_CONTINUITY.md`
2. `docs/PROGRESS.md`
3. `docs/ROM_IDENTITY.md`
4. `analysis/PRG31_boot_and_interrupts.asm`
5. `analysis/PRG02_IRQ_dispatch.md`
6. `analysis/IRQ_STATE_MACHINE.csv`
7. `analysis/PRG26_OAM_frame.md`
8. `analysis/PRG26_SPRITE_FORMAT.md`
9. `analysis/SPRITE_SET_TABLE.csv`
10. `analysis/SPRITE_MASTER_TABLES.csv`
11. `analysis/OAM_OBJECT_FIELDS.csv`
12. `analysis/ZP10_OAM_STATE.md`
13. `src/oam_renderer.hpp`
14. `src/oam_renderer.cpp`
15. `tests/oam_renderer_test.cpp`
16. `tools/analyze_rom.py`
17. `tools/audit_irq_dispatch.py`
18. `tools/audit_oam_tables.py`
19. `tools/audit_sprite_descriptors.py`
20. `tools/audit_oam_zp10.py`

## Unresolved / do not assume

- exact preceding `$10` value on every reachable `$9FA9` path
- whether object ordering guarantees an explicit-attribute sprite before `$9FA9`
- whole-ROM proof of every `$048C` producer and invalid-selector impossibility
- producer-domain closure for `$0400` frame offsets
- exact higher-level meaning of global `$AD`
- semantic identities of individual frame tables/descriptors
- gameplay meaning/producers of every `$0400-$04C3` field beyond proven renderer behavior
- exact visual/game-state meanings of IRQ states `$00-$2C`
- whole-PRG code/data accounting denominator

## Next manageable checkpoint

**04C: `$9FA9` reachability/object ordering only.** Trace the executable selector-`$10` / frame-`$14` producer path far enough to identify which object slot(s) can render `$9FA9` and whether a prior rendered slot or other proven path establishes `$10` first. Do not expand into the full object system in the same checkpoint.
