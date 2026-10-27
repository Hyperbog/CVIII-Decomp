# JP0828 — Original type-$3D virtual movement, source detachment, B447 inputs and E249 prelude

## Scope

The owner requested original per-frame type-$3D AI, persistent
virtual actor state after original CPU-slot deallocation, wider
weapon/projectile collision input, and complete $E249/$B525
defeat effects. This checkpoint implements the **authenticated
movement subroutine and isolated persistence**, plus **original
collision-input geometry** and a **bounded E249 prelude**.
It does **NOT** yet reproduce the entire original AI,
original damage/defeat/drop/score paths, or enable any
independent gameplay-authoritative hit.

All actual code is sourced from the SHA-256-authenticated
Japanese VRC6 ROM `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.
Private physical bank raw0B SHA:
`17b216088d12ac7b6a4a68bbea3434dbdba317865bd6cf4d11646a3d4efaf64a`;
private fixed bank raw0F SHA:
`96990dfb1b859cfbcebed583ac100cc49aefe235ab61220fafa365dabba88964`.
No ROM bytes or Mesen savestates are committed.

## First real Mesen original actor update entry

The Mesen 2.1.1 controller-reached owner ROM (Stage1-02,
frame **3094**, type3D original actor slot **X=1**) executes:

- Fixed `$FE4E JSR $E2D0`: select physical original
  16KiB raw0B at CPU $8000–$BFFF.
- Fixed `$FE51 JSR $8001`: enter original actor
  fractional-position/movement routine, **CPU
  $8001–$804A**, returning to fixed `$FE54`.
- Original code updates `$04C4,X` fractional X,
  `$0438,X` integer X with carry from the fraction,
  9-bit source-page bit `$0470,X & 1`,
  `$04DB,X` fractional Y, and `$041C,X`
  integer Y; speed inputs `$04F2,X/$0509,X`
  and `$0520,X/$0537,X`.
- Subsequent fixed `$FE60 JSR $EF93` animation,
  `$FE68 JSR $8161` offscreen OAM visibility and
  `$FE6B JSR $826C` lifetime check are separately
  identifiable but **not** yet run inside the
  private actor VM. Hence this is a correct per-frame
  **movement** entry, not full type3D AI.

Authenticated 74-byte window CPU $8001–$804A hash
`4f8acdadcc27a00278b799ca271122d46c05473d92f19e1f01ee505113fccef9`.

## Actual 6502 movement inside isolated native CPU

`cviii_actor_vm_0827.h` extends its original read-only
PRG mapping to allow exactly $8001–$804A. It executes
original 2A03 binary ADC, zero-page ORA/ADC,
LDY/STY/DEY, original fractional carry, absolute-X
reads/writes and private JSR/RTS. It still rejects all
unmapped PPU/APU/mapper calls.

`cviii_virtual_3d_0828.h` creates a **separate
persistent 2KiB private CPU RAM image per source**.
For authenticated sources phases 3 and 4, when the
corresponding actual CPU actor is alive, its existing
guest poststate is copied into the private image.
If the original slot goes away, its old private state
is retained and can change from LINKED to DETACHED
**only when the last original CPU flags contain
both adjacent-page bit $01 and OAM-cull bit $80,
and its world X lies outside the original 256px
gameplay strip**. Otherwise the instance fails
closed as FAULTED: a type-zero original slot may
represent a defeated enemy or normal room cleanup,
and must NEVER become an artificial offscreen survivor.
For eligible offscreen witnesses, the virtual actor
resumes authentic $8001 movement from saved private
RAM on new PPU/source-verified room frames.
It maps both original +256/-256 page candidates
to the nearest historically observed 32px-continuous
world coordinate **before** detachment, rather than
teleporting an adjacent-page sprite back to screen X.
It then computes X delta from the original 9-bit page
and 8-bit integer position with 512px rollover; Y applies
original signed modulo-256 increment. Impossible
>32-pixel per-frame shifts, unknown instructions, and
untrusted source/room keys mark the instance FAULTED
rather than fabricate an actor result.
New objects with a recycled original numeric slot do
not reclaim the detached virtual identity.

This new native instance update is **actually called**
in `cviii_stage1_host_0725.c` after original guest
source observation and the bounded $B486 probe.
It runs exclusively in private RAM and does not
change the user's original cartridge engine, original
256px physics, original-mode OAM or savestate bytes.
The current world reset intentionally **invalidates
unserialized private timelines** on savestate load;
full save/restore of independent virtual actor state
remains unresolved. Room discontinuity also stops its
clock; world-wide offroom scheduling is not implemented.

## Real original Mesen comparison

From the existing genuine controller-only original
frame3092 creation savestate, Mesen 2.1.1 ran two
frames to fixed CPU `$FE51` with **X=1** at original
frame **3094**. Captured original CPU RAM before
the `$8001` call and after its exact instruction
trace returned through `$8036 RTS`.

The independently compiled native source CPU VM,
started from **the identical private Mesen CPU-RAM
snapshots** and original authenticated physical raw0B
ROM bytes, matched **both source-born type3D actors**:

| Original source actor | Scratch $00/$01 | Integer X / page flags | Fraction X/Y | Integer Y |
|---|---|---|---|---|
| X=1, parent source3 | $44/$FF | $0439=$9F, $0471=$44 | $04C5=$A0, $04DC=$00 | $041D=$50 |
| X=2, parent source4 | $44/$FF | $043A=$BF, $0472=$44 | $04C6=$A0, $04DD=$00 | $041E=$B0 |

Both stopped at original **$8036 RTS**.
Original Mesen RAM was never modified by either
private native comparator. These controller-reached
per-frame witnesses support movement for two original
actors, not full AI, hits or defeat.

A second **4,096-case** original ROM differential
confirmed signed velocity, 9-bit page carry,
both integer coordinates, fractional X/Y and
guest RAM isolation against independently computed
C11 arithmetic. A separate synthetic test verifies
an adjacent-page/OAM-culled actor survives type-zero
disappearance, advances X across multiple private 6502
ticks, and is not reassigned when the original CPU
reuses slot1. The regression also asserts that an
actor disappearing INSIDE the normal 4:3 gameplay
strip is rejected rather than being revived.

**Natural caveat:** the controlled original ROM
trace proves the movement implementation on a
normally allocated actor. It is NOT natural evidence
of a detached actor surviving indefinitely or
experiencing correct external enemy AI, damage,
pickup and drops. It is also not a controller-reached
proof of death at $B525.

## Wider B447 collision input

`cviii_virtual_collision_0828.h` checks source-linked
detached type3D against actual original partner slots
20–22 and original 8-bit ROM radius tables
`$BB80/$BC08/$BB60/$BB6B`, but uses world-space
signed X distance to prevent false 8-bit wrap
across the 426px viewport. It observes original
per-partner $068D mask bits $02/$04/$08 and
fails closed on original $B7 alternatives and special
partner type05 $0593 handling.
This yields **candidate proximity only**, not permission
to change $068D, hit actors, play sound, consume weapon,
apply $B486 damage or execute $B525 defeat.
Both interaction authorization flags remain zero.

## E249/B525 sound and defeat boundary

The original fixed-bank code is authenticated:
- `$E249–$E263` SHA-256:
  `5a5d7b8a0f857c8062faee305b4d752522f281bda0271e402cd4c66759b37324`.
- `$E2D0–$E2D5` SHA-256:
  `8d1a2898917458f00a455757ee9471327e1d4f51bee3d841d98e23055fb51380`.

Actual `$E249` pushes original sound A, stores
`$26=$FF`, saves previous PRG page `$23`
in `$25`, selects PRG bank `$0C` using
`$E2D0`, then restores the saved A and calls
bank0C **`$8850`**. Only **after that call**
does it clear $26 and restore the prior bank.

The pure `cviii_e249_prelude_0828` captures the
original sound ID, previous PRG bank and proposed
$25/$26/bank0C setup, stopping at `$E258
JSR $8850`. The live actor VM records that
would-call context when $B486/B525 reaches E249,
but **does not actually switch the native mapper,
write APU or simulate subsequent defeat/loot**.

**The requested complete E249/B525 continuation is
not implemented.** It requires bank0C $8850 sound
code, the rest of original B525–B5DE object
replacement/score/drop logic and the other banked
effect helpers, and original-versus-sandbox state
comparisons on natural damage/defeat events.

## Verification

`JP0828_DetachedOriginalMovement` native C11
and Windows CTest checks independent two-frame
virtual actor stepping, source ID reuse rejection,
collision candidate dimensions/unknown branches,
E249 bank setup and savestate reset.
Linux strict GCC and Clang ASan/UBSan fixtures pass.
The owner-private CLI:
```sh
python3 JP/decomp/tools/jp0828_original_movement_sound_audit.py \
  --smoke --rom '/private/Akumajou Densetsu (Japan).nes'
```
checks complete ROM identity and four authentic
code-window SHA-256 fingerprints.
Full Windows and external NESRecomp CI must be
checked on the latest commit separately.

**No playable claim of independently interacting
widescreen enemies** until original animation/AI,
collision and full defeat effects are matched.
Strict PRG 49,504/262,144, VPP 31/100 unchanged.
