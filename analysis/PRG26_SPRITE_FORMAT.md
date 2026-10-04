# PRG26 sprite selector hierarchy and OAM descriptor format

This file records the current reconstruction of the NMI-called renderer at `PRG26:$8070..$817E`. All claims below were rechecked against the verified Japanese ROM.

## Seven parallel 28-byte render arrays

`PRG26:$8001` iterates object indices `0..$1B`. The renderer-facing state is a structure-of-arrays occupying seven consecutive 28-byte regions:

| range | renderer use | conservative name |
|---|---|---|
| `$0400-$041B` | zero suppresses object; otherwise used as byte offset into second-level pointer table | frame/pointer offset |
| `$041C-$0437` | added to decoded per-sprite Y delta | base Y |
| `$0438-$0453` | added to per-sprite X delta | base X |
| `$0454-$046F` | if nonzero, replaces low two bits of descriptor attribute byte | palette/attribute-low override |
| `$0470-$048B` | bit 7 set suppresses rendering in `$8001` | render suppression flags |
| `$048C-$04A7` | byte offset into first-level pointer table at `$817F` | sprite-set selector |
| `$04A8-$04C3` | zero chooses horizontally mirrored renderer; nonzero chooses non-mirrored renderer | orientation-path flag |

These names describe only proven renderer behavior, not higher-level gameplay semantics.

## First-level selector table

`$8070` uses `$048C,X` directly as a byte offset into the little-endian pointer block at `$817F-$819C`:

| selector | pointer |
|---:|---:|
| `$00` | `$819D` |
| `$02` | `$820D` |
| `$04` | `$8265` |
| `$06` | `$82AF` |
| `$08` | `$8AB0` |
| `$0A` | `$9545` |
| `$0C` | `$AAA6` |
| `$0E` | `$ABEA` |
| `$10` | `$9E6D` |
| `$12` | `$8BB0` |
| `$14` | `$ABA6` |
| `$16` | `$819D` |
| `$18` | `$820D` |
| `$1A` | `$8265` |
| `$1C` | `$82AF` |

The high selectors `$16/$18/$1A/$1C` alias the first four geometry/frame tables. Producer evidence at `PRG25:$ADA3` directly supplies those four values.

A whole-ROM proof that every runtime producer stays within the canonical selector set is still pending. Do not add a host-side bounds check yet.

## Second-level pointer lookup

After the first-level pointer is loaded into `$08/$09`, `$8070` uses `$0400,X` as another byte offset and reads a little-endian pointer from the selected table. The resulting `$0A/$0B` pointer addresses a sprite descriptor stream:

`$048C selector -> sprite-set pointer -> $0400 frame offset -> descriptor stream`.

Example: selector `$10` points to `$9E6D`. Frame offset `$14` reads pointer bytes at `$9E81-$9E82` and resolves to descriptor `$9FA9`.

## Corrected descriptor format: variable-length records

**Correction to Batch 03:** records are not uniformly four bytes.

Descriptor byte 0 is still the sprite count. Each sprite begins with a packed **Y/control byte**. Its low bit is a record-format flag; the remaining seven signed bits encode Y delta after an arithmetic right shift by one.

The 6502 implements this literally:

- if the Y/control byte is nonnegative, clear carry before `ROR`
- if it is negative, set carry before `ROR`
- `ROR` therefore performs a signed arithmetic shift by one
- the carry produced by `ROR` is the original bit 0

Thus:

- `bit0 = 0`: full record = `Y/control, tile, attribute, X` (4 bytes)
- `bit0 = 1`: compressed record = `Y/control, tile, X` (3 bytes), and the attribute byte is **reused from zero-page `$10`**

This flag is handled identically by the mirrored and non-mirrored renderer paths.

### Attribute cache `$10`

For a full record, the renderer obtains the descriptor attribute byte, applies any object low-two-bit override, applies horizontal-flip XOR `$40` on the mirrored path, then stores the **final emitted attribute** in zero-page `$10` before writing OAM.

For a compressed record, no attribute byte is read from the descriptor. The renderer loads `$10` and writes that cached final attribute directly to OAM.

`$8001` and `$8070` do not initialize `$10` on entry. Therefore `$10` is renderer input/output state, not a temporary that may be reset per object in a native translation.

### Concrete proof: descriptor `$9FA9`

Selector `$10`, frame offset `$14` resolves to `$9FA9`. Its bytes begin:

```text
04 DF 8A F0  E1 8C F8  E5 8E 00  04 E4 90 03
```

Decoded exactly:

| sprite | Y/control | shifted Y delta | flag | tile | attribute source | X |
|---:|---:|---:|---:|---:|---|---:|
| 0 | `$DF` | `$EF` (-17) | 1 | `$8A` | cached `$10` | `$F0` |
| 1 | `$E1` | `$F0` (-16) | 1 | `$8C` | cached `$10` | `$F8` |
| 2 | `$E5` | `$F2` (-14) | 1 | `$8E` | cached `$10` | `$00` |
| 3 | `$04` | `$02` (+2) | 0 | `$E4` | descriptor `$90`, then cached to `$10` | `$03` |

This descriptor begins with **three compressed sprites before any full record in that descriptor**. A native implementation that initializes the cached attribute at descriptor/object entry would therefore be observably wrong.

## Tile transform for selectors `$16+`

Helper `$8172` checks the first-level selector saved in `$0F`. When `$0F >= $16`, it returns the current descriptor tile plus `$80` and sets carry. Callers use carry to choose between the raw byte and the transformed byte.

This applies on the encoded `$AD != 0` paths. Selectors `$16/$18/$1A/$1C` therefore reuse geometry/frame tables while selecting the alternate tile-number half.

## Attribute transform

For full records, if `$0454,X != 0`:

`(descriptor_attributes & $FC) | $0454,X`

replaces the descriptor low two attribute bits. The mirrored path then toggles bit `$40`.

The resulting byte is cached in `$10` and emitted. Compressed records reuse that already-transformed cached byte unchanged.

## X transform and horizontal mirroring

Non-mirrored path uses descriptor X delta directly before base-X addition.

Mirrored path computes `$F8 - descriptor_x_delta` before adding base X. `$F8 == 256 - 8`, matching the encoded 8-pixel sprite-width reflection arithmetic.

Both paths contain explicit carry/sign range checks. Failed X-range tests hide the sprite by writing OAM Y=`$F4`.

## OAM-slot permutation

`$8001` starts with `$07=$40` available sprites. After each emitted/hidden sprite, `$8070` advances the OAM byte offset by `$C4` modulo 256 (`-15` four-byte OAM slots). Since 15 is coprime with 64, this visits all 64 OAM slots before repeating.

At frame start, `$22` advances by `$44` (`17` OAM slots) and becomes the initial byte offset.

The permutation is proven; its likely sprite-priority/flicker-distribution purpose remains interpretation.

## Non-local OAM-full return

When `$07` reaches zero inside `$8070`, the routine executes:

```asm
PLA
PLA
RTS
```

This discards `$8070`'s own return address and returns directly to `$8001`'s caller. Consequently `$8001`'s unused-slot fill loop is skipped when all 64 OAM slots were consumed.

A structured native lift may model this with an explicit propagated result, but must preserve the exact outcome.

## Current boundaries

Proven:

- renderer code: `$8070-$817E`
- canonical first-level selector block: `$817F-$819C`
- first second-level table begins at `$819D`
- seven 28-byte renderer arrays at `$0400-$04C3`
- descriptor starts with sprite count
- each sprite is either a 4-byte full record or 3-byte compressed record
- Y/control bit 0 selects cached-attribute reuse
- `$10` stores the final transformed OAM attribute and is state across renderer calls
- `$9FA9` is a concrete descriptor whose first three records are compressed

Still unresolved:

- whole-ROM closure of every `$048C` producer
- exact higher-level meaning of global `$AD`
- complete extents and semantic names of all second-level frame tables
- producer/gameplay meaning of all object-array fields
- full lifetime/ownership contract of zero-page `$10` outside this renderer subsystem
