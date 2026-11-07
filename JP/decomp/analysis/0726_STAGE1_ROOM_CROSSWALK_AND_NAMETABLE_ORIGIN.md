# JP0726 — Correct Stage 1-02 source records and validate live room origin

## Corrected original-ROM layout selection

The JP0724 initial source-to-selector crosswalk accidentally swapped the original Japanese Stage 1-02 source records for selectors `00/01/02` and `00/01/03`. The source data and the original PPU are not wrong: the association of those source records to the original game's live $34/$35/$36 selectors was wrong.

Authentic SHA-verified original JP Mapper24 cartridge:
`958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.

| RAM $34/$35/$36 | Correct ROM file header | Metatile count | Orientation |
| --- | --- | ---: | --- |
| 00/00/00 | $0200BA | 144 | 3 horizontal screens |
| 00/01/00 | $02014B | 48 | 1 horizontal screen |
| 00/01/01 | $020039 | 128 | 2 vertical screens |
| **00/01/02** | **$0201DD** | **144** | 3 horizontal screens |
| **00/01/03** | **$02017C** | **96** | 2 horizontal screens |
| 00/02/00 | $02026E | 144 | 3 horizontal screens |
| 00/02/01 | $0202FF | 144 | 3 horizontal screens |
| 00/03/00 | $020390 | 192 | 4 horizontal screens |

The two original room files contain the same aggregate 240 metatiles regardless of their assignment, so the complete Stage 1 atlas remains **1,040 metatiles = 16,640 8×8 tile positions**. All public tests and synthetic header fixtures now use the corrected crosswalk.

## Direct original-ROM versus actual archived native PPU comparison

The owner-private JP0719 complete native replay includes 245 observation snapshots, with full 4KiB nametables, 2KiB CPU RAM, per-scanline PPU address/fine-X/control/mask state, and physical CHR page IDs. The offline oracle independently expands the owner-verified original ROM's Stage 1 metatile/TSA definitions and compares scene-local projected tile IDs to actual native PPU nametable memory.

Steady original-background comparison samples by selector (20 source tile rows × 30 columns = 600 positions per observation), with physical PPU page selected from the **actual** per-scanline scroll state:

- `00/00/00`: **28/28** observations agree on **600/600** tile IDs each.
- `00/01/00`: **73/73** steady observations agree on **600/600** each (three additional transition observations have x positions beyond the one-screen layout and must not be rendered).
- `00/01/03`: **42/42** agree on **600/600** each, using original file offset $02017C.
- `00/01/02`: **51/51** observations have the corrected **$0201DD** layout, with some local tile mutations; several samples match 600/600 and the later samples remain approximately 97% tile-identical.

When the two latter source records were reversed, `00/01/03` matched only roughly 4–24% and `00/01/02` roughly 4–42%, an independently visible failure. The corrected crosswalk removes that structural mismatch.

The PPU's physical horizontal origin can be 0 **or 256** within a room. For example, native JP0719 sample 43 has selector `00/01/00`, room-local RAM $53/$54 = 0, but actual scanline horizontal scroll = 256. This is legitimate gameplay, **not** a 256-pixel camera divergence. Conversely, samples 40–42 retain `00/01/00` before that room's local coordinate resets and exceed its true source geometry; they must not receive preloaded side scenery.

Across the 194 eligible steady horizontal-room observations, physical pattern CHR pages $1000–$1FFF remained **40,45,47,43** (1KiB page indices), so the current CHR mapper source is constant in this covered segment. This is not proof that all stages/rooms use the same mapping.

## Runtime fail-closed room confirmation

`cviii_stage1_host_0725.c` now:

1. Accepts only physical PPU room origins 0 and 256 with residual camera/PPU disagreement at most 2 pixels.
2. Derives camera position from actual PPU scroll phase and the ROM-local 16-bit coordinate RAM $53/$54, including modulo-512 wrap.
3. Before painting margins, probes 12 actual live PPU nametable tiles, spaced over four columns and three background rows, against independently ROM-decoded tile IDs at the predicted world coordinates.
4. Requires at least six bounded probes and 75% tile agreement. This rejects stale previous-room VRAM and non-indexed or incomplete rooms while tolerating isolated legitimate mutable tiles.
5. Continues to omit horizontal side scenery for the vertical chapel marked by RAM $65 bit 7.
6. Never changes CPU-visible RAM/PPU or overwrites the original 61,440 center pixels.

Offline application of this exact 12-probe decision rule to the existing native replay confirms **194/194 source-bounded horizontal gameplay states accepted**, and **3/3 selector-transition observations rejected**. It is a regression against existing evidence, not a new user gameplay capture or a full native-game screenshot certification.

## Boundaries

This implementation addresses Stage 1 static background geometry and room-local horizontal origins. It does not prove the original game's offscreen enemy behavior, tile animation, full per-scanline presentation effects, complete stage traversal parity, vertical viewport geometry, or final retail Windows onscreen pixel parity. All relevant source/test changes remain ROM-free in the public repository. No new VPP or semantic PRG source credit: **31/100** and **49,504/262,144 bytes** respectively.
