# Native widescreen level background import — source integrity boundary

This is a **recompilation asset-build capability**, not game instruction
decompilation or an attempt to simulate original actor scripts.

## Completed in JP0831

`JP/recomp/tools/jp_level_layout_inventory_0831.py --rom ORIGINAL.nes
--out PRIVATE/layout-inventory.json` reads the original cartridge,
rejects unknown ROM revisions, identifies candidate contiguous 1+48×N
or 1+64×N metatile layout blocks before the known 4x4 TSA definition
tables and outputs metadata only: boundaries, widths, source SHA-256,
and structural ambiguity.

The algorithm uses *exhaustive bounded dynamic programming* and rejects
multiple equally plausible layouts. It must never pick an arbitrary
parse when two source boundaries are consistent with the raw byte range.
It contains no game tile/pixel data in source or report.

All eight original Wallachia/Stage 1 layouts are independently known by
their physical ROM file headers and verified against the scanner's
unique solution. Other regions are **not keyed to native stage/room
selectors** and have no independently certified palette selection.
Thus all other source-consistent sequences are only unassigned candidates,
not playable 426x240 backgrounds.

## Original Japanese owner-ROM inventory results

Validated SHA-256: `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.

| Region | Maximum contiguous structural layouts | Safe render mapping |
|---|---:|---|
| Wallachia | 8, unique | Yes — existing Stage 1 atlas |
| Abandoned Mines | 10, unique | No |
| Main Hall | 4, unique | No |
| Causeway | 8, unique | No |
| Ghost Ship | 5, unique | No |
| Forest | 2, unique | No |
| Swamp | 1, unique | No |
| Sunken City | 1, unique | No |
| Tower | 9, ambiguous | No |
| Inner Hall | 7, ambiguous | No |
| Castle Keep | 6, ambiguous | No |
| Lookout Tower | 7, ambiguous | No |
| Catacombs | 5, ambiguous | No |
| Alucard's Cave | 0 | No |
| Clocktower | Unsupported 4x4 source span | No |

**The candidate lengths above are source-scan results, not an assertion
that each named region contains exactly that many rooms or stages.**

## Still necessary for complete widescreen

1. Connect original CPU stage/subarea/room selector values to the actual
   bounded background header for **every** room; verify each candidate
   against the game-rendered PPU and original screen captures.
2. Reconstruct screen positioning, vertical routing, room joins and
   dynamic changed tiles without repeated edge filling.
3. Establish correct palette/attribute arrays for all graphics regions,
   including the malformed Clocktower definition span.
4. Identify player-visible object/enemy/NPC/item templates and static
   placements. Preload their data only; original game continues to own
   spawning, despawning, AI, collision and pickups.
5. Verify original game pixels/state are bit-for-bit identical across
   gameplay, bosses, death/respawn, switches, pause/saves and endings.

The native engine's existing 15-stage / 135-selector source payload
preload and conservative real-PPU margin painter are separate modules.
The candidate scanner does not feed unverified layouts to the live
presenter. **Do not mark widescreen all-levels complete.**
