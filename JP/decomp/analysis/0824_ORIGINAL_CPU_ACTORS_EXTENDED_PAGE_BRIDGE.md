# JP0824 — Stage 1 original-CPU-owned actors in the 426px viewport

## What is implemented (and what is not)

A **real original game actor** is an allocated slot in original CPU
`$054E,X`, with actual sprite data `$0400,X/$048C,X`,
original `$0470,X` flags, positions `$0438,X/$041C,X`,
and an original source record. It is **not** a native object spawned
from the background atlas. The ROM-authenticated 6502 engine
continues controlling animation, movement, game-state lifetime and
collisions. The native renderer reads state after each frame.

The Stage 1 Enhanced sprite bridge previously discarded **all**
original actors when `$0470,X & $80`, even though
original raw PRG0B `$8161-$81B1` may set that offscreen
sprite/OAM-cull flag while the actor remains allocated and its CPU
AI continues running. Additionally `cviii_world_capture_live_0803`
required a globally placed room, even though BLK 1-03 source
selectors `(0,2,0)` and `(0,2,1)` are independently known from
an authenticated owner-ROM atlas without a proven global adjacency.

The new **original CPU adjacent-page bridge** fixes both gaps:

- Only original actor slots **1–12** with
  `$054E,X=$3D` (natural JP0509 row32 type),
  `$0470,X & $05 == $05` (original source flag bit2
  and adjacent-page bit0), original valid source-parent index
  `$0645,X<6`, and nonzero original `$0400,X`
  qualify. **No source record alone creates an actor.**
- It reads original `$0438,X` and the original page bit.
  When raw X is near 0, the candidate real sprite lies
  **+256px** into the original right-neighbor page; when
  raw X is near 255, the candidate lies **−256px** into
  the left page. Middle-page candidates are rejected because
  they cannot intersect either 85px extension.
- If the original actor also has OAM-cull bit `$80`,
  it is still eligible for **margin-only** PRG26 sprite
  projection with the original recorded frame/palette/
  mirror and CHR data. The central 256x240 original PPU
  picture remains pixel-identical; the native renderer
  does not alter original OAM.
- In an original ROM-authenticated horizontal source room
  whose global topology is not yet proven, original
  actors are represented in that room's **local** frame
  and projected against its verified CPU/PPU camera.
  Unplaced rooms do not gain fabricated global links.
- Original `$054E,X=0`, loss of source provenance,
  page-bit removal or a zero sprite frame remove the
  offscreen projection. No native event resurrects a
  deallocated game actor.
- Original `$B1F8` collision dispatcher returns early
  when source page bit0 is set; **the original CPU**
  processes normal `$B339` / response code when it
  legitimately brings the actor back into page0.
  Thus player-facing interaction stays original rather
  than a second, approximate native hitbox engine.

## Real original Mesen test for page-1 CPU survival

Using Mesen 2.1.1 with authenticated Japanese ROM
SHA256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`,
the existing **natural** Stage1-02 frame3122
type3D actor source snapshot was used as a **private
controlled CPU-oracle**:

1. Load a genuine owner-original frame3122 saved state
   from the independent controller-only JP0509 natural
   actor creation replay.
2. Write just actor1 original `$0471=$C5` (source
   provenance, one-bit adjacent page, OAM cull) and
   `$0439=$0C` (right-neighbor X=12).
3. Execute one complete **original** Mesen CPU frame.
4. Verify original `$054F=$3D`, frame `$0401=$94`,
   original `$0471=$C5` and `$0646=$03`
   are retained. The original actor remains allocated
   through that offscreen frame; no synthetic CPU code
   or separate scheduler is required to keep it alive.

### Three independently executed original-page variants

From the same genuine natural Mesen frame3122 snapshot,
the test reset the original CPU state for each variant and
ran **one complete original 6502 gameplay frame**:

| Original input page1 | Original frame postcondition | Native gate |
| --- | --- | --- |
| actor X=`$0C`, flags=`$C5` | original actor type`$3D`, frame`$94`, flags`$C5`, parent source3 survived | project right |
| actor X=`$F0`, flags=`$C5` | original actor type`$3D`, frame`$94`, flags`$C5`, parent source3 survived | project left |
| actor X=`$81`, flags=`$C5` | original `$054F=0`, `$0401=0` (CPU deallocated) | reject middle page |

The new reproducible private owner oracle
`JP/decomp/tools/jp0824_mesen_original_actor_page_oracle.py`
validates both authorized core hashes, the original ROM,
the original natural type3D input state and **all three**
actual 6502 postconditions. It never includes the original
state or ROM in Git.

This is an original **controlled-state test**, **NOT**
proof of natural wide source spawning, natural offscreen
AI motion for every actor type, or contact/parity against
an extra-wide native projectile. Original ROM raw0B
`$80E3-$815E` SHA256 is
`84af7cef133ae428a931360513ff77918ebcc6ff1861439799493fb69d2e71b0`
(camera/flag state); original raw0B
`$8161-$81B1` SHA256 is
`ea381a34b2fe3df6c5b2c4fc40f89aaab3fe421de3d49a6852f00663195b5728`
(OAM/visibility gate). The original sprite data
are loaded and authenticated at runtime from the
owner's private ROM and not committed.

## Native regression and acceptance boundary

`jp_extended_actor_test_0824` builds an artificial,
ROM-free `(0,2,0)` room that has **not** been
placed in global world coordinates. It installs
**a synthetic representation of authentic guest RAM
fields** (not a virtual source) for one type3D
slot and tests original right-side and left-side
page1 projections, an offscreen OAM flag, actual
PRG26 sprite pointer decoding, and central pixel
preservation. It explicitly tests rejection for
missing original source page, invalid parent index,
allocator type0, untrusted original room, and
unsupported actor slots. It also checks original
`$B1F8` early return when page1 and subsequent
normal in-page handler eligibility.

The source is wired into native CMake CTest and
Windows CI. Test outcomes must be read for the
current commit before reporting success.

**Important unimplemented portion of the user's request:**
The original game continues spawning sources
according to its 256px camera. A room's unspawned
offscreen records remain **source records**, not
interactive enemies. Original weapon/projectile
ranges, candles and unspawned enemies are NOT
simulated beyond the original viewport; no
offscreen collision, damage or pickup is granted
by this patch. A genuinely separate wide actor
scheduler must reproduce **original per-type
spawn, AI, collision, defeat, loot and savestate
behavior** before those additional objects can
be enabled. The first CPU-owned actor bridge
does not claim complete user-requested parity.

No additional PRG/VPP certification is credited:
**49,504/262,144 PRG, 31/100 VPP**.
