# PRG26 sprite selector hierarchy and OAM descriptor format

This file records the Batch 03 reconstruction of the NMI-called renderer at `PRG26:$8070..$817E`. All claims below were rechecked against the verified Japanese ROM.

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

`$8070` executes:

```asm
LDY $048C,X
STY $0F
LDA $817F,Y
STA $08
LDA $8180,Y
STA $09
```

The selector is therefore a **byte offset**, not an ordinal. The canonical pointer block at `$817F-$819C` is 30 bytes / 15 little-endian pointers:

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

`$819D` is also the first byte of the second-level table selected by `$00/$16`, so `$817F-$819C` is a natural table boundary. The four high selectors deliberately alias the geometry/frame tables used by `$00/$02/$04/$06`.

Producer evidence directly confirms the high aliases: `PRG25:$AD7B..$ADA2` multiplies `$0633,X` by three and indexes four 3-byte records at `$ADA3`; the selector bytes at record offsets `0,3,6,9` are exactly `$16,$18,$1A,$1C`.

Other directly reconciled producers use even selectors in the lower set, including `$00,$02,$04,$06,$08,$0C,$0E,$10,$12,$14`. A whole-ROM proof that no malformed/out-of-range selector can ever reach `$8070` is still pending, so the future native implementation must not add a bounds check unless the original producer domain is fully proved.

## Second-level pointer lookup

After the first-level pointer is loaded into `$08/$09`, `$8070` uses the object byte at `$0400,X` as another byte offset:

```asm
LDY $0400,X
LDA ($08),Y
STA $0A
INY
LDA ($08),Y
STA $0B
```

Thus `$0400,X` selects a little-endian pointer from the chosen sprite-set table. The resulting `$0A/$0B` pointer addresses a sprite descriptor stream.

Example: selector `$00` points to `$819D`, whose initial entries are:

```text
frame offset 00 -> $82F5
frame offset 02 -> $8339
frame offset 04 -> $8347
frame offset 06 -> $8352
frame offset 08 -> $8347
frame offset 0A -> $8360
...
```

This confirms a two-level hierarchy:

`object selector ($048C) -> sprite-set/frame-pointer table -> frame offset ($0400) -> sprite descriptor`.

## Sprite descriptor stream

At the resolved descriptor pointer, byte 0 is copied to `$03` and used as the sprite-count loop counter. Each sprite then consumes four descriptor bytes:

1. **Y delta byte**
2. **tile byte**
3. **attribute byte**
4. **X delta byte**

The output is a normal four-byte OAM record `[Y, tile, attributes, X]` in shadow OAM page `$0200-$02FF`.

### Y delta transform

For the first descriptor byte, the code chooses carry from the byte's sign bit and executes `ROR A`. This is an encoded arithmetic-right-shift by one of the signed 8-bit value. The result is then added to `$041C,X`.

Do not replace this casually with host signed division: negative odd values follow the 6502 shift result, not C/C++ truncation-toward-zero division.

### Tile transform for selectors `$16+`

Helper `$8172` is:

```asm
LDA $0F
CMP #$16
BCC return
LDA ($0A),Y
CLC
ADC #$80
SEC
RTS
return:
RTS
```

Call sites use carry to distinguish `raw descriptor tile` from the returned transformed tile. The helper is only consulted on the encoded `$AD != 0` paths.

Therefore selectors `$16/$18/$1A/$1C` reuse the same geometry/frame tables as `$00/$02/$04/$06`, but under the `$AD`-gated path their tile byte is offset by `$80` modulo 256.

### Attribute transform

If `$0454,X != 0`, the non-mirrored path computes:

`(descriptor_attributes & $FC) | $0454,X`

so the object value replaces the descriptor's low two attribute bits.

The mirrored path performs the same optional low-bit replacement and then `EOR #$40`, toggling the NES OAM horizontal-flip bit.

### X transform and horizontal mirroring

Non-mirrored path:

`output_x = base_x + signed_descriptor_delta`, with explicit carry/sign tests that hide the sprite on 8-bit wrap beyond the visible 0..255 domain.

Mirrored path first computes:

`$F8 - descriptor_x_delta`

then performs the same base-X addition / wrap test. `$F8` is exactly `256 - 8`, matching an 8-pixel sprite-width reflection in the encoded byte arithmetic.

When the X range test fails, the renderer writes `$F4` to the sprite's OAM Y byte instead of emitting a visible position.

## OAM-slot permutation

`$8001` starts with `$07=$40` available sprites. For every emitted/hidden descriptor record, `$8070` advances the OAM byte offset with:

`X = X + $C4 (mod 256)`.

Because `$C4 == -60` bytes == `-15` four-byte OAM slots, and 15 is coprime with 64, this visits every one of the 64 OAM slots exactly once before repeating.

At frame start, `$22` is advanced by `$44` (`17` OAM slots) and copied to the initial OAM byte offset. This changes the starting slot from frame to frame. The mathematical permutation is proven; its likely sprite-priority/flicker-distribution purpose remains an interpretation rather than a source-level name.

## Important non-local control-flow behavior

When `$07` reaches zero inside `$8070`, the code executes:

```asm
PLA
PLA
RTS
```

Those two `PLA`s discard `$8070`'s return address. The following `RTS` therefore returns directly to the caller of `$8001`, skipping the rest of `$8001` entirely. This is a real cross-function early-exit/shared-stack behavior and must not be lost in decompilation.

A native structured translation may represent this as an explicit `OamFull` result propagated from `$8070` to `$8001`, but equivalence must include the fact that no unused-slot fill loop runs once all 64 OAM slots have been consumed.

## Current boundaries

Proven:

- renderer code: `$8070-$817E`
- canonical first-level selector block: `$817F-$819C`
- first second-level table begins at `$819D`
- selectors `$16/$18/$1A/$1C` alias the first four geometry tables and select the tile `+$80` behavior under the encoded `$AD` condition
- seven 28-byte renderer arrays at `$0400-$04C3`
- descriptor record is one count byte followed by four-byte sprite records

Still unresolved:

- full producer-domain proof for every `$048C` write site
- exact higher-level meaning of global `$AD`
- complete extents of all second-level frame-pointer tables
- semantic names of individual sprite sets/frames
- producers and gameplay meanings of every object-array field
