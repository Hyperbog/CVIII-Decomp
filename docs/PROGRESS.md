# Decompilation progress ledger

## Current status

Project initialized from the verified Japanese `Akumajou Densetsu` Mapper-24 ROM. Three bank-aware analysis batches are now committed. No global translated-byte percentage is claimed yet: whole-PRG code/data/overlap accounting is intentionally deferred until the project has a conservative denominator.

## Stable foundation

- Verified immutable ROM identity and iNES mapper/size information.
- PRG modeled as 32 physical 8 KiB banks (`PRG00..PRG31`).
- Fixed vectors established: RESET `$E00B`, NMI `$E057`, IRQ `$E0F5`.
- VRC6 PRG helpers established: tracked 16 KiB bank at `$23`, raw/tracked selectors `$E2D2/$E2D0`, `$C000` 8 KiB selector via `$E2C4`.
- NMI bank `$0D` call to `$8001` resolves to `PRG26:$8001`.
- IRQ raw bank `$01` resolves its table/handlers into `PRG02/PRG03`.
- Reproducible ROM, IRQ, and OAM-table audit tools are present under `tools/`.

## Batch 02 checkpoint — IRQ state machine

Authoritative IRQ table:

- `PRG02:$9F01-$9F5A`
- 90 bytes / 45 entries
- states `$00-$2C`
- `$9F5B` is executable code, not another table entry

The previous `$9F60` overlap hypothesis was disproved and removed. Normal active states are `$00-$2C`; `$80` is a high-bit bypass sentinel. The highest explicit chain closes `29 -> 2A -> 2B -> 2C` with `$2C` terminal/non-incrementing.

Machine-readable state ledger: `analysis/IRQ_STATE_MACHINE.csv`.

The fixed IRQ exits remain distinct:

- `$E118` clears VRC6 IRQ Control `$F001`, then falls through
- `$E11D` acknowledges via `$F002` and restores the tracked PRG bank

Do not merge those paths in native code.

## Batch 03 checkpoint — PRG26 sprite/OAM hierarchy

### Seven 28-byte renderer arrays

`PRG26:$8001` iterates 28 object indices (`0..$1B`). The renderer-facing state is seven consecutive parallel arrays from `$0400-$04C3`:

- `$0400-$041B`: frame / second-level pointer-table byte offset; zero suppresses object
- `$041C-$0437`: base Y
- `$0438-$0453`: base X
- `$0454-$046F`: attribute-low/palette override
- `$0470-$048B`: bit-7 render suppression
- `$048C-$04A7`: first-level sprite-set selector byte offset
- `$04A8-$04C3`: orientation-path flag; zero selects mirrored renderer

Machine-readable field ledger: `analysis/OAM_OBJECT_FIELDS.csv`.

### First-level sprite-set table

`$8070` uses `$048C,X` directly as a byte offset into the little-endian pointer block beginning at `$817F`.

The canonical block is `$817F-$819C`, 30 bytes / 15 pointer entries, selectors `$00,$02,...,$1C`:

`00->819D, 02->820D, 04->8265, 06->82AF, 08->8AB0, 0A->9545, 0C->AAA6, 0E->ABEA, 10->9E6D, 12->8BB0, 14->ABA6, 16->819D, 18->820D, 1A->8265, 1C->82AF`.

Selectors `$16/$18/$1A/$1C` deliberately alias the first four geometry/frame-pointer tables used by `$00/$02/$04/$06`. `PRG25:$ADA3` directly supplies those four high selector values.

The exact selector ledger is `analysis/SPRITE_SET_TABLE.csv`; `tools/audit_oam_tables.py` verifies the table, aliases, producer record, and key renderer opcode signatures against the ROM.

A complete proof that every possible runtime `$048C` producer remains within the canonical selector set is still pending. Do not add a host-side bounds check yet.

### Two-level hierarchy

The renderer then uses `$0400,X` as another byte offset into the selected table and reads a second little-endian pointer. That final pointer addresses a sprite descriptor stream:

`$048C selector -> first-level sprite-set pointer -> $0400 frame offset -> sprite descriptor`.

### Sprite descriptor format

Descriptor byte 0 is a sprite count. Each sprite consumes four bytes:

1. Y delta
2. tile index
3. OAM attribute byte
4. X delta

Output is one four-byte OAM record `[Y,tile,attribute,X]` in shadow OAM page `$0200-$02FF`.

Encoded details that must be preserved:

- Y delta is sign-aware `ROR` arithmetic-right-shifted by one before addition to base Y. Do not replace with ordinary signed division because negative odd values differ.
- If `$0454,X != 0`, attribute low two bits are replaced by that object byte after `AND #$FC`.
- Mirrored path toggles attribute bit `$40` and transforms X with `$F8 - descriptor_x` before base-X addition.
- X addition contains explicit carry/sign wrap checks; failed range tests hide the sprite by writing Y=`$F4`.
- Under encoded `$AD != 0` paths, helper `$8172` adds `$80` to the tile byte for selectors `>= $16`; the high selector aliases therefore reuse geometry while selecting the alternate tile-number half.

Full reconstruction notes: `analysis/PRG26_SPRITE_FORMAT.md`.

### OAM permutation and non-local return

Each emitted descriptor advances OAM byte offset by `$C4` modulo 256 (`-15` sprite slots). Since 15 is coprime with 64, all OAM slots are visited once before repeat. Frame start advances `$22` by `$44` (`17` sprite slots), changing the initial slot.

Critical control-flow fact: when the 64-slot counter reaches zero inside `$8070`, the code executes `PLA; PLA; RTS`, discarding `$8070`'s own return address and returning directly to `$8001`'s caller. Therefore `$8001`'s unused-slot fill loop is skipped when OAM is full. Any structured native lift must preserve this non-local early exit, likely via an explicit propagated result.

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

## Unresolved / do not assume

- Whole-ROM proof of every `$048C` producer and invalid-selector impossibility.
- Exact higher-level meaning of global `$AD`.
- Complete extents and semantic identities of every second-level frame-pointer table.
- Gameplay meaning/producers of every `$0400-$04C3` field beyond proven renderer behavior.
- Exact visual/game-state meanings of IRQ states `$00-$2C`.
- Whole-PRG code/data accounting denominator.

## Next batch

1. Audit all executable writes to `$048C` and close the runtime selector domain if possible.
2. Trace `$0400` frame-offset producers and prove stride/domain for the major sprite sets.
3. Parse representative descriptor tables into machine-readable frame/sprite records and cross-check mirrored/non-mirrored behavior.
4. Begin the first native faithful OAM subsystem source only after the selector/frame contracts are stable enough for regression tests.
5. Continue connecting IRQ program states to the frame-side visual setup that seeds them.

No translated-byte percentage is reported yet; that remains intentionally deferred until accounting is conservative and reproducible.
