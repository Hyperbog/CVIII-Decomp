# Native widescreen: whole-game level preload and renderer completion boundary

This document describes the **native recompilation product**. It does not
promise that loading a resource record runs original game scripts, nor equate
unclassified source bytes with a specific item/enemy/NPC identity.

## Implemented in this branch

- The owner-supplied Japanese Mapper24 cartridge is authenticated by the full
  SHA-256 before the preload can replace resident resources.
- The native Enhanced host loads all 15 original game stage-source groups and
  indexes all **135** room selectors into immutable original-ROM byte views
  during its initial resource setup. No room-visit or viewport-scroll is
  required to have these records resident.
- All **1,478** source-bounded 4x4 tile definitions across **14** recognizable
  regions are preloaded as a parallel TSA index. The malformed Clocktower
  source span is **not** decoded or invented.
- The first gameplay frame of a new stage binds its already resident stage
  group. Switching stages changes only the presentation cache selector.
- The existing Stage 1 atlas still preloads eight complete static room
  backgrounds. Its 426x240 native presenter and original 256x240 gameplay
  center remain unchanged. Already-active original actor slots may be
  presented in the side margins by the existing Stage 1 painter.
- Every original spawn, despawn, NPC, item pickup, enemy AI, collision,
  controller, IRQ, PPU, APU, and save/load operation remains in the unchanged
  native game execution. **No preloaded record is executed as a script or
  spawned as an entity.** The cache is read-only, not a second game world.
- A corrupt ROM, malformed source record, incomplete array, or unsupported
  stage cannot partially install or activate resources. The default native
  game picture continues without the optional preload.
- Windows MSVC and strict Linux C11 synthetic tests cover every indexed
  room selector, all stage groups, original record-byte identity, unknown
  selectors, stage-change idempotency and transactional import failure.

## Original cartridge indexed room-selector counts

| Stage source index | Selector count |
|---:|---:|
| 0 | 8 |
| 1 | 18 |
| 2 | 10 |
| 3 | 12 |
| 4 | 9 |
| 5 | 6 |
| 6 | 6 |
| 7 | 10 |
| 8 | 7 |
| 9 | 5 |
| 10 | 14 |
| 11 | 7 |
| 12 | 5 |
| 13 | 11 |
| 14 | 7 |
| **Total** | **135** |

These were checked against the original user-supplied Japanese ROM. The
width-four / width-seven resource formats are **not yet a full gameplay
entity type catalog**. Counts of structural source records are not counts
of enemies or items.

## Remaining for genuinely complete game-wide widescreen

1. Recover each non-Stage-1 map's complete, source-backed metatile layout,
   attribute palettes, scrolling axes, CHR mapping and room transitions.
   Preloaded tile patterns without their positions do **not** reconstruct
   a level.
2. Attach real source-proven screen/room connections for all routes,
   including vertical sections, staircase transitions, bosses and endings.
   Unknown topology must not be filled with repeated or guessed tiles.
3. Identify and preindex actual enemy/NPC/item spawn definitions, script
   parameters, entity-to-graphic IDs and original room-entry triggers.
   Loading templates ahead of time is fine; **activating** them must still
   occur under the original game's precise state, position and timing gates.
4. Implement a per-stage renderer that paints the preloaded world outside
   the native NES viewport, handles sprite priority/dynamic tiles and
   keeps the original 256x240 picture/logic authoritative.
5. Complete owner-ROM native acceptance through all stages, alternate
   paths, bosses, death/respawn, companions, pickups, and credits. Verify
   toggling widescreen never changes original game machine-state hashes.

**Current acceptance:** the all-stage *source data preload* is implemented;
Stage 1 is the only area with a source-backed wide world painter. The user
request for fully drawn offscreen geometry and preidentified NPC/items in
every level is **not yet complete**. This must remain explicit in every
release description until proven by the native game.

## JP0830 — PPU-qualified cross-stage side painting

The optional read-only wide presenter now has two distinct paths:

- **Stage 1:** full original-ROM layout atlas and original active actor
  presentation in confirmed side areas, unchanged from the established build.
- **Other gameplay stages:** the native PPU may have a second populated
  nametable available during horizontal scrolling. The presenter reconstructs
  the unused 85-pixel side columns from those *currently mapped* original
  PPU nametable, attribute, CHR, scroll and palette bytes. It refuses to
  paint if mirrored pages, uncertain/blank adjacent geometry, IRQ pattern
  switches, invalid scroll, or sampled native-background parity fail.

The original 256x240 NES picture, original object slots, pickup timing,
enemy/companion AI, sprite/OAM logic, audio and save state are never changed
by this painter. The side tiles are a visual read-only extension; they
do **not** constitute a full persistent background map or offscreen spawn
simulation.

**Actual Japanese ROM smoke check:** the ROM-independent Linux interpreter
host built from this branch played 1,050 controller-only frames into Stage
1-01 in Enhanced mode and output a 426x240 presented PNG. Comparing it to
the native 256x240 screenshot at horizontal offset 85 showed an exact
61,440/61,440 RGB pixel match, including the 48-line HUD. This demonstrates
the unchanged Stage 1 gameplay frame. It is not a completed Stage 2+
widescreen or full-game gameplay test.

**Remaining release blockers:** all-stage ROM-backed tilemap positions,
multi-room topology and offscreen NPC/items/objects remain unknown or
unvalidated outside the currently sourced Stage 1 paths. A source-data
preload and visually matched PPU neighbor are valuable primitives, but
neither should be described as a fully reconstructed world.
