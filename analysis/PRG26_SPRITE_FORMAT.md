# PRG26 sprite selector hierarchy and OAM descriptor format

This is the current reconstruction of the NMI-called renderer at `PRG26:$8001/$8070..$817E`. ROM bytes control all claims.

## Seven parallel 28-byte render arrays

`$8001` iterates object indices `0..$1B`:

| range | proven renderer use |
|---|---|
| `$0400-$041B` | zero suppresses object; otherwise byte offset into selected frame-pointer window |
| `$041C-$0437` | base Y |
| `$0438-$0453` | base X |
| `$0454-$046F` | if nonzero: `(descriptor_attr & $FC) | object_byte` |
| `$0470-$048B` | bit 7 suppresses rendering |
| `$048C-$04A7` | byte offset into selector block `$817F` |
| `$04A8-$04C3` | zero = mirrored path; nonzero = non-mirrored path |

Do **not** model `$0454` as only a two-bit palette value. Direct producers include values above `$03`; the encoded renderer clears only the descriptor's low two bits and then ORs the full object byte.

## First-level selector block

`$048C,X` is used directly as Y against `$817F/$8180`, so it is a byte offset, not an ordinal. `$817F-$819C` contains 15 pointer entries:

`00->819D, 02->820D, 04->8265, 06->82AF, 08->8AB0, 0A->9545, 0C->AAA6, 0E->ABEA, 10->9E6D, 12->8BB0, 14->ABA6, 16->819D, 18->820D, 1A->8265, 1C->82AF`.

`$16/$18/$1A/$1C` alias `$00/$02/$04/$06`; when `$AD != 0`, helper `$8172` adds `$80` to tile bytes for selectors `>= $16`.

Whole-ROM producer closure is still pending. Native code therefore preserves direct addressing and does not invent a selector bounds check.

## Five master frame-pointer blocks

Batch 04 proved the selector targets are windows into five physical masters, not 15 independent tables. For each master, entry 0 points exactly to the first descriptor byte immediately following the pointer block, giving a direct boundary.

| master | pointer bytes | entries | selector windows |
|---|---|---:|---|
| A | `$819D-$82F4` | 172 | `$00/$16` entry 0; `$02/$18` entry 56; `$04/$1A` entry 100; `$06/$1C` entry 137 |
| B | `$8AB0-$8C2D` | 191 | `$08` entry 0; `$12` entry 128 |
| C | `$9545-$9620` | 110 | `$0A` entry 0 |
| D | `$9E6D-$9F6C` | 128 | `$10` entry 0 |
| E | `$AAA6-$AC5B` | 219 | `$0C` entry 0; `$14` entry 128; `$0E` entry 162 |

Y is 8-bit, so one selector exposes at most 128 aligned 16-bit entries (`$00..$FE`). `$12` and `$14` deliberately begin exactly `$100` bytes into larger masters, making later frames reachable with an 8-bit offset. `analysis/SPRITE_MASTER_TABLES.csv` records every window and the physically available even frame-offset range.

## Second-level lookup

`$0400,X` is used directly as Y against the selected frame-pointer window:

```asm
LDY $0400,X
LDA ($08),Y
STA $0A
INY
LDA ($08),Y
STA $0B
```

Y wrap between low/high reads is real 6502 behavior. The native lift preserves it instead of silently widening the index.

## Variable-length compressed descriptor records

Batch 03's original uniform-four-byte description was incorrect. Descriptor byte 0 is sprite count. Each sprite is:

1. Y/control byte
2. tile byte
3. attribute byte **only when Y/control bit 0 is clear**
4. X byte

Therefore records are either four bytes (explicit attribute) or three bytes (cached attribute).

### Y/control byte

The code selects carry from the sign bit and performs `ROR`, producing a signed arithmetic right shift by one. The outgoing carry is the original bit 0:

- bit 0 clear: read a new attribute byte
- bit 0 set: omit attribute from the stream and reuse ZP `$10`

The shifted result is added to `$041C,X`. This is not equivalent to C/C++ signed division for negative odd values.

### Persistent attribute cache `$10`

For a full record, the renderer transforms the attribute, stores the final emitted byte in ZP `$10`, and writes it to OAM. A compressed record writes the existing `$10` directly; it does not reapply override or mirror transforms.

`$8001/$8070` never initialize `$10`, so it persists across records **and object calls**. Descriptor `$9FA9` proves this matters: its first three sprites are compressed before its first explicit attribute.

`$9FA9` begins:

```text
04 DF 8A F0  E1 8C F8  E5 8E 00  04 E4 90 03
```

The first three records are `Y/control,tile,X` and consume the previously cached attribute.

### Attribute transform

For an explicit attribute:

- `$0454,X == 0`: use descriptor byte unchanged
- otherwise: `(descriptor_attr & $FC) | $0454,X`
- mirrored path then XORs `$40`
- final value becomes ZP `$10`

### Tile transform

If `$AD != 0` and selector `$0F >= $16`, helper `$8172` returns current tile + `$80` modulo 256. Otherwise the raw tile is emitted.

### X transform and clipping

Non-mirrored path treats descriptor X as a signed displacement from base X. Mirrored path first computes `$F8 - descriptor_x` modulo 256 and applies the same signed range logic. If the mathematical sum falls outside `0..255`, OAM Y is overwritten with `$F4` to hide the sprite.

## Corpus audit

`tools/audit_sprite_descriptors.py` parses all five master blocks with the corrected variable-width format and currently verifies:

- **745 unique referenced descriptors**
- maximum **27 sprites** in one descriptor
- maximum encoded descriptor length **96 bytes**
- **2,310** compressed attribute-reuse records
- no referenced descriptor exceeds the 8-bit stream cursor
- `$9FA9` is the only referenced descriptor whose first sprite is compressed

## OAM permutation and non-local return

`$8001` starts with 64 OAM slots. Each sprite advances OAM byte offset by `$C4` modulo 256 (`-15` slots); frame start advances `$22` by `$44` (`17` slots).

When the slot count reaches zero, `$8070` executes `PLA; PLA; RTS`, discarding its own return and returning directly to `$8001`'s caller. `$04/$03` are not updated on that path and the unused-slot fill loop is skipped.

`src/oam_renderer.cpp` is the first faithful native lift of this subsystem. It keeps NES RAM as explicit state, retains wrapped 8-bit table cursors, persistent `$10`, full-byte override semantics, mirror/tile transforms, clipping, and represents the non-local return as `OamFrameResult::OamFull`. `tests/oam_renderer_test.cpp` regression-tests those behaviors.

## Still unresolved

- complete executable producer-domain proof for `$048C` selectors
- complete producer-domain proof for `$0400` frame offsets
- higher-level meaning of `$AD`
- semantic identities of individual sprite sets/frames
- gameplay meanings of object arrays beyond renderer behavior
- ownership/lifetime of ZP `$10` outside this rendering path
