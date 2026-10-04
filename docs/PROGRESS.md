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

`PRG26:$8001` iterates 28 render-object slots backed by seven consecutive 28-byte arrays `$0400-$04C3`:

- `$0400-$041B`: frame/second-level pointer-table byte offset; zero suppresses object
- `$041C-$0437`: base Y
- `$0438-$0453`: base X
- `$0454-$046F`: attribute-low/palette override
- `$0470-$048B`: bit-7 render suppression
- `$048C-$04A7`: first-level sprite-set selector byte offset
- `$04A8-$04C3`: orientation-path flag; zero selects mirrored path

`$048C,X` indexes the canonical first-level pointer block `$817F-$819C` with even byte offsets `$00..$1C`. High selectors `$16/$18/$1A/$1C` alias the first four geometry tables and can select tile `+$80` behavior under the encoded `$AD` path.

OAM byte offset advances by `$C4` per emitted sprite and frame seed by `$44`. When all 64 OAM slots are consumed, `$8070` executes `PLA; PLA; RTS`, discarding its own return and returning directly to `$8001`'s caller.

## Checkpoint 04A — corrected variable-length sprite descriptors

This checkpoint corrects one Batch 03 error before native code is written.

### Record encoding

Descriptor byte 0 is the sprite count. Each sprite begins with a packed Y/control byte. The renderer sets carry from that byte's sign and performs `ROR`; this is a signed arithmetic right shift and leaves the original bit 0 in carry.

Therefore bit 0 is also a record-format flag:

- bit 0 clear: `Y/control, tile, attribute, X` — 4 encoded bytes
- bit 0 set: `Y/control, tile, X` — 3 encoded bytes; attribute is reused from zero-page `$10`

For a full record, the renderer applies attribute override/mirroring first, then stores the **final emitted OAM attribute** to `$10`. A compressed record writes `$10` directly. `$8001/$8070` do not initialize `$10` on object/descriptor entry, so a faithful native renderer must model it as carried renderer state rather than a fresh local.

### Concrete proof

Selector `$10` points to master frame table `$9E6D`. Frame offset `$14` resolves to descriptor `$9FA9`:

`04 DF 8A F0 E1 8C F8 E5 8E 00 04 E4 90 03`

It decodes as four sprites:

1. `$DF,$8A,$F0` — compressed, Y=-17, reuse `$10`
2. `$E1,$8C,$F8` — compressed, Y=-16, reuse `$10`
3. `$E5,$8E,$00` — compressed, Y=-14, reuse `$10`
4. `$04,$E4,$90,$03` — full, Y=+2, attribute `$90`

Thus `$9FA9` begins with three compressed records before any full record in the descriptor. Initializing `$10` per descriptor/object would be wrong.

### Master frame-table census

Direct ROM audit establishes five master frame-pointer blocks in the active PRG26/27 16 KiB window:

- `$819D-$82F4`: 172 pointers; entry 0 points to first descriptor `$82F5`
- `$8AB0-$8C2D`: 191 pointers; entry 0 -> `$8C2E`
- `$9545-$9620`: 110 pointers; entry 0 -> `$9621`
- `$9E6D-$9F6C`: 128 pointers; entry 0 -> `$9F6D`
- `$AAA6-$AC5B`: 219 pointers; entry 0 -> `$AC5C`

Across those tables there are **745 unique descriptor pointers**. Auditing all 745 with the corrected variable-length parser finds:

- maximum sprites in one descriptor: **27**
- maximum encoded descriptor length: **96 bytes**
- compressed attribute-reuse records: **2310**
- the only descriptor whose **first sprite** reuses the prior cached attribute is `$9FA9`

These facts are reproduced by `tools/audit_sprite_descriptors.py`.

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
10. `analysis/OAM_OBJECT_FIELDS.csv`
11. `tools/analyze_rom.py`
12. `tools/audit_irq_dispatch.py`
13. `tools/audit_oam_tables.py`
14. `tools/audit_sprite_descriptors.py`

## Unresolved / do not assume

- Full lifetime/ownership of zero-page `$10` outside the OAM renderer.
- Whole-ROM proof of every `$048C` producer and invalid-selector impossibility.
- Exact higher-level meaning of global `$AD`.
- Semantic identities of individual frame tables/descriptors.
- Gameplay meaning/producers of every `$0400-$04C3` field beyond proven renderer behavior.
- Exact visual/game-state meanings of IRQ states `$00-$2C`.
- Whole-PRG code/data accounting denominator.

## Next manageable checkpoint

**04B: `$10` renderer-state lifetime only.** Trace executable writes/reads of zero-page `$10` around the NMI/OAM path and determine what initializes the cached attribute before `$9FA9` can be used. Do not expand into general object-producer analysis in the same checkpoint.
