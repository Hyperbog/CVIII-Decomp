# JP0823 — User-observed BLK 1-03 widescreen margin dropout

## Owner reproduction

Four consecutive owner Enhanced 426x240 screenshots show Stage 1-03
scrolling past gravestones and houses. The original 256-pixel picture
remains playable, while extended left/right columns progressively
black out; the actor/candle/enemy gameplay remains restricted to the
original 4:3 screen. This is **two independent issues**.

### Root cause: renderer background graph

The owner ROM preloads the complete eight-area Stage1 atlas into
`cviii_stage1_rom_0724.c`. Specifically both original **BLK 1-03**
horizontal source selectors **`(0,2,0)`** and **`(0,2,1)`**
are independent 3-screen / 768-pixel source layouts.
The previous world compositor physically positioned only rooms
`(0,0,0)` and `(0,1,0)` at construction; other areas require
genuine transition evidence, which can be delayed or missed.
`cviii_world_paint_0806` returns zero if the selected area is
unplaced. Even when the selected room *is* placed, its painting
count was positive despite the next unplaced room being outside
the compositor's output: the old host guarded all neighbor
painting under **`if(!world_pixels)`**. Thus one margin could
remain empty regardless of the loaded original next-room atlas.

The other failure occurs when the mutable original NES PPU
nametable diverges from the immutable room-tile source enough
to fail `room_loaded()`'s >=75% vote. The old native host
kept using the last trusted room selector and extrapolated its
camera indefinitely with PPU scroll deltas until that source
was out of pixels, leaving both side margins black.

### JP0823 renderer-only correction

- Neighbor painting is now per side and **independent of
  overall world pixel count**. A learned, original-PPU-validated
  real room link always wins, and duplicate projection is
  avoided if the successor is already in the placed world.
- For the **two ROM-decoded BLK 1-03 subrooms only**, a
  presentational sibling camera projection is allowed
  where no PPU-observed room link has yet been learned:
  `(0,2,0)` camera X=512 projects `(0,2,1)`
  with camera -256 into the rightmost 85px;
  `(0,2,1)` camera X=0 projects `(0,2,0)`
  with camera +768 into the leftmost 85px.
  This never connects rooms in the physical world graph
  or claims original PPU transition authority.
- If a BLK 1-03 frame is in original gameplay state
  (`RAM $18=4`), retains the original CPU selector
  (`$34:$35:$36=00:02:00/01`), matches original
  `$54:$53` camera to original PPU X modulo 512
  within two pixels, uses a horizontal PPU Y near 120,
  valid PPU background pattern table and observed
  source width 768, three consecutive stable scene
  keys can recover the **presentation-only** room camera
  despite a failed immutable tile-map vote.
  It never calls the physical `join_accept` operation,
  cannot learn a new room connection and does not write
  RAM, PPU, mapper or OAM.
- The NES HUD and native central gameplay image remain
  pixel-identical, and side projections are strictly
  outside the 256-pixel native gameplay crop.

## Verification

A new native `jp0725_native_framebuffer` regression:
1. Original ROM-backed 1-03:0 right sibling appears in
   x341–425 even when neither room is in the world graph.
2. Original ROM-backed 1-03:1 left sibling appears in
   x0–84 even if disconnected.
3. The current world room can be placed and return
   nonzero pixels while its successor remains unplaced;
   the black right margin still receives original atlas
   tiles rather than being masked by the pixel-count gate.
4. Synthetic PPU nametable disagrees strongly with the
   decoded stage source, but three consecutive verified
   CPU/PPU phase samples recover **both** original
   Stage1-03 side columns.
5. An unverified PPU phase and changed selector never
   fabricate a source connection.
6. Original 256x240 picture pixels and HUD remain
   unmodified; no new actors or objects are created.
7. Invalid 1-03 source keys or camera outside original
   0–512-pixel range reject sibling projections.

The ROM-free local presenter regression passed normally
and with AddressSanitizer/UndefinedBehaviorSanitizer.
The Windows CI test of the new branch must be checked
before release acceptance.

## Distinct gameplay limitation

**Original-width-only enemies/objects are not fixed by
this renderer patch.** As established by JP0813–JP0822,
native stage source records and original actor snapshots
are observational. The real NES original allocator,
offscreen despawn logic, enemy simulation, damage,
object destruction and pickups still operate within the
historical 256-pixel camera. Rendering more sprite tiles
does not create reliable interactive offscreen actors.
An independent guest-compatible or native extended
object/actor scheduler with original $B727 and downstream
effect parity remains required. No false promise of
completed offscreen gameplay.

Strict PRG and VPP certification unchanged:
49,504/262,144 PRG; 31/100 VPP.
