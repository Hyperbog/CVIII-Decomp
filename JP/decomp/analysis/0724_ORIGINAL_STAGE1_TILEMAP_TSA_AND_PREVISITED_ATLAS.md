# JP0724 — Original-ROM Stage 1 tilemap/TSA producer and previsited atlas

**Source:** original Japanese Akumajou Densetsu, Mapper24 VRC6, 393,232-byte cartridge, exact owner ROM SHA256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`. No original retail tiles, CHR, screenshots, ROM or owner-private packs are embedded in this repository. The C11 extraction API accepts caller-authenticated ROM memory; an iNES size/mapper check **alone is not cryptographic authentication**.

## New original-source closure

The original Wallachia/Stage 1 layout records occupy iNES **file offsets** $020039–$020450, physically PRG16 bank $08. These are original header bytes (additional screen count) followed by 48 metatiles per horizontal screen or 64 per vertical screen. Stage 1's 8 room layouts contain **1,040 metatile indices**. Original Wallachia metatile definitions are $020451–$020D60: 145 definitions × 16 PPU tile IDs (4×4 8-pixel tiles), followed immediately by the corresponding **145 attribute bytes** at $020D61–$020DF1. Each attribute byte holds four 2-bit palette quadrant selectors. This extends the independent documentation in GMvania's Japanese-specific ROM map (https://gmvania.blogspot.com/2012/08/bookmark-this-blog-entry-last-update.html).

The original *code* producing these tiles is not merely hypothetical:

- In physically mapped original PRG8 bank $1E (CPU $C000–$DFFF), original $CF35–$CF50 reads a room map metatile ID via `LDA ($10),Y`, multiplies it by 16 with four `ASL A; ROL $03` pairs, and adds the tile-definition pointer in RAM $5A/$5B to form pointer $02/$03.
- Original $CBEA–$CC09 consumes four sequential bytes at `($02),Y` into the $0300 PPU update staging queue, repeatedly entered from $CB9C–$CBD2. $CC14 and $CD29 also read `($5C),Y` to enqueue palette attributes. Original PRG31 $ED46 (JP0723 decoder) consumes those queued PPU commands.
- In the recorded original JP0718 Stage 1 CPU RAM, $5A/$5B = $8441 and $5C/$5D = $8D51. The *source ROM file offsets* $020451 and $020D61 map exactly to CPU $8441 and $8D51 when physical PRG16 bank $08 occupies $8000–$BFFF. This independently authenticates the live source pointers. It is not a proof of every producer entry or all PPU bus phases.

## Original ROM / original Mesen agreement

The C11 geometry decoder produces **16,640 individual 8×8 background tile IDs**, each with a 2-bit palette selector, from the 1,040 original metatile references across all eight Stage 1 source records. Stage 1 selectors $00/$00/$00, $00/$01/$00..$03, $00/$02/$00..$01, and $00/$03/$00 have explicit room source mappings. The $00/$01/$01 room's 128 metatiles are structurally a two-vertical-screen layout; gameplay-screen orientation/position for that specific selector is not independently verified here.

Independent Python ROM expansion and compiled native C11 decoding match the **recorded original Mesen PPU** for three static room/screens:

| Selector | Original captured samples | Background tiles compared | Attribute bytes compared |
| --- | --- | --- | --- |
| 00/00/00 | 15, 16, 17 | 704/704 each | 40/40 each |
| 00/01/00 | 44, 45, 46 | 704/704 each | 40/40 each |
| 00/03/00 | 206, 207, 208 | 704/704 each | 40/40 each |

Comparison covers physical PPU nametable rows $06–$1B (22×32) and corresponding five attribute rows, excluding original HUD/partially overwritten top rows. It is a **source-data background tile/attribute match**, not a final RGB/sprite, dynamic animation, pixel scrolling or complete level parity claim.

## Public code and actual limitations

- `cviii_stage1_rom_0724.c/.h`: ROM-only, source-bounded eight-room tile and attribute expansion API; callback receives x/y in 8-pixel tile coordinates.
- `cviii_stage1_atlas_0724.c/.h`: an independent pregame world cache holding all 16,640 tile IDs and palette selectors from the original ROM before the player travels anywhere, plus a side-only 426×240 presentation painter. Rendering resolves the room's current original CHR bytes and palette colors via caller-supplied runtime functions, and never touches the native center.
- Both are **dormant source-level modules** in the public tree. The user's JP0720–JP0722 private compositor patches are not represented in the public repository. Runtime wiring, definitive camera/room origin, per-room CHR banking, sprite continuation and a real Windows widescreen screenshot are still **unverified**. Source is ready for a game-owned compositor to invoke but is not automatically in a shipping binary.
- All eight layouts passed synthetic ROM-free C11 tests; local GCC/Clang ASan/UBSan checks passed for atlas behavior, bounded source inputs, and center-image immutability. Do not treat synthetic rendering as live original gameplay evidence.

**Progress metrics stay unchanged:** VPP 31/100; strict semantically certified original PRG 49,504/262,144 bytes (18.8843%). No stage gameplay liveness uplift is asserted from source identification or synthetic tests.

## Reproduction

```sh
cc -std=c11 -O2 -Wall -Wextra -Werror -pedantic \
 JP/recomp/native/enhanced/cviii_stage1_rom_0724.c \
 JP/recomp/native/enhanced/cviii_stage1_rom_test_0724.c -o /tmp/jp0724-tilemaps
/tmp/jp0724-tilemaps

cc -std=c11 -O2 -Wall -Wextra -Werror -pedantic \
 JP/recomp/native/enhanced/cviii_stage1_rom_0724.c \
 JP/recomp/native/enhanced/cviii_stage1_atlas_0724.c \
 JP/recomp/native/enhanced/cviii_stage1_atlas_test_0724.c -o /tmp/jp0724-atlas
/tmp/jp0724-atlas
```
