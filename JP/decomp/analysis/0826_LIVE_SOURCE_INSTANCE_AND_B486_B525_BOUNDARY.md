# JP0826 — First native source-instance lifecycle integration, B486/B525 boundary

## Delivered implementation (draft PR #16)

The previous JP0825 source-admission header existed but was not called
from the game. JP0826 adds a running native instance registry to the
live Stage 1 world, attached to the already SHA-authenticated owner-ROM
physical raw0A room source table. The implementation is limited to
original JP room selector **(0,1,0)** and its two natural row32 actor
sources. No original ROM bytes are committed.

During `cviii_world_preload_horizontal_0816`, the real owner-ROM
room1 6-pair descriptor and script/type lookup admit source
phases **3** and **4**, types `$3D` at room positions
**(160,80)** and **(192,176)**. If a synthetic/unsupported
bank does not prove these source records, the registry remains
dormant while the rest of the original world initializes.

On every **verified** frame in that room,
`cviii_world_observe_children_0818` now calls
`cviii_wide_runtime_tick_0826`:

- Two persistent, source-keyed *native instance records* maintain
  their own time counters, source positions, last guest position,
  original sprite frame/flags, and lifecycle state.
- Only a real original guest CPU actor (`$054E,X=$3D`,
  `$0470,X & $04`, original `$0645,X` parent phase
  and a unique plausible position) can change a resident
  instance into live. It is **not** sufficient that a source
  exists in the ROM atlas.
- Once bound, the native copy updates on new original CPU frames
  with a 32-pixel continuity bound and unchanged guest actor slot.
  It **does not** run a separate inferred skeleton AI.
- If the original guest allocation disappears, the native
  instance enters `LOST` and is **not** resurrected when
  another guest object appears in the same numeric slot.
  Savestate/reset clears transient associations while leaving
  the authenticated source directory resident.
- The game continues owning all emulated CPU, PPU, OAM,
  actor movement, contacts, sound, score and pickups.

### Original Mesen source evidence

A fresh read of the owner-original Mesen 2.1.1 saved state from
natural Stage 1-02 frame **3092**, after the prior verified
600-instruction creation sequence, confirms original:
source-parent slots `$0646=$03`, `$0647=$04`;
actor X `$0439=$A0` (160), `$043A=$C0` (192);
actor types `$054F/$0550=$3D`; camera `$53/$54=0`.
This is proof of **source attachment at creation**, not
proof of offscreen-generated enemies.

### $B486 and $B525

Existing `cviii_effect_b486_prefix_0821` faithfully predicts
the original 6502 high-nibble accumulator and 8-bit
`$067B,X` subtraction, including the branch to
`$B525` on zero/negative result. The new
`cviii_b525_prefix_0826` additionally models the
first original `$B525-$B53B` decision: type `$3D`,
`$3E`, `$4B`, or `$47` selects sound `$27`,
and other type IDs select `$32`, before original
`$B53C JSR $E249`.

**The model stops before $E249.** Original downstream
`$B53F-$B5DE` includes event/actor replacements, sound,
score and other game-visible effects. This branch has NOT
been recompiled and validated for an independent offscreen
combat actor. It is not used to write emulator RAM or
authorize offscreen hits.

The native C11 `JP0826_OriginalSourceInstance` test
checks two resident source identities, independent frame
counters, authenticated original allocation links,
position continuity, loss/reuse refusal, wrong-room
rejection, B486-to-B525 transition, and B525 sound choice
across all 256 actor IDs. The Windows workflow executes
the test explicitly and builds the full playable native
target; the same commit passes the external NESRecomp
smoke and JP Native Regression Gate.

## Explicit remaining limitation

**No independently updated original-type $3D combat AI
or wider weapon/projectile interaction is functioning
yet.** These source instances maintain independent
native *lifecycle records* and *clocks*, but still
obtain actual movement, animation and gameplay changes
from the original CPU. The original 4:3 spawn and
collision restrictions remain.

Next release-changing work needs a reentrant original
6502 actor execution context or exact compiled native
actor behavior, first for row32/$3D, then authentic
projectile and pickup slots; plus original-vs-compiled
contact, B486 damage, E249/B525 defeat, drop, lifecycle
and savestate parity. No guessed source hitboxes,
independently awarded drops or fake persistent enemies
are enabled. Strict PRG **49,504/262,144**; VPP **31/100**.
