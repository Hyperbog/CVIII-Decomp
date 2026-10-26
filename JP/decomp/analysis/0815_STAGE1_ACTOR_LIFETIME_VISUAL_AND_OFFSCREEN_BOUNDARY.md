# JP0815 — Original actor lifetime and visual-reference evidence; offscreen interaction dry-run

**Scope:** Part 21 stacked on [PR #16](https://github.com/Hyperbog/CVIII-Decomp/pull/16)
and PR #13's resident Level 1 world / original-PRG26 sprite renderer.
Authenticated user-provided Japanese Mapper24 iNES ROM SHA-256:
`958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.
No ROM, extracted sprite art, raw RAM or savestate is committed.

## Genuine original-game actor lifetime evidence

Older independent Mesen2 controller-input original-game captures already prove
that **actor X=15, type `$80`, attribute `$81`** is *active* on Stage 1
frame 2603. Its fixed `$FDFE→$FE31` scheduler gate is independently
stepped in [JP0519](0519_FIXED_SCHEDULER_NATIVE_FINDINGS.md), the
`$BD11→$FE60` continuation in [JP0520](0520_SCHEDULER_BD11_FE34_NATIVE_FINDINGS.md),
and `$EF93→$FE63` animation update in
[JP0521](0521_ORIGINAL_ANIMATION_NATIVE_FINDINGS.md).
**These are overlapping windows from one actor**, not three separate
objects or an independently witnessed removal. Natural RAM `$05EF,X=0`
in JP0520 also shows why JP0814's original installation signature
(`$30` on the initial type-`$80` write) must NOT be required
forever after animation/script processing begins.
Neither the actor's exact originating `$AB1F` record nor the
frame of its original despawn is proved by those stored reports.
**Important allocation/visibility split:** this naturally observed
type-`$80` actor has original `$0470,X=$81`, whose high bit makes
the existing JP0803 visual-sprite shadow mark it non-rendered even while
original `$054E,X=$80` proves the scheduler slot is allocated.
JP0815 now separately reports an original *guest installation witness*
from JP0814's exact CPU RAM fields. Hidden actors are never drawn,
yet the genuine installed slot must not be mislabeled a despawn.
JP0814 retains an initial unique source tag only while the same
original actor slot and its generation remain active.

## New source-to-visual proof

PRG26 original 16KiB bank SHA-256:
`042d91a4fe2be444465b4ebdac1ee419ed58f74976bc1e9edbb92995a7fb6959`.
The owner-local [visual provenance auditor](../tools/jp_stage1_visual_identity_0815.py)
authenticates original ROM, raw0A, PRG26, and all nine `$AB1F`
seven-byte records (3 source rows `$0D`, 6 direct types `$80`).
From the actual original PRG26 sprite table `$817F`,
selector byte offset `$0E` and *frame-table offset* `$00`
resolve to set `$ABEA`, compressed sprite descriptor `$AC5C`,
**four sprite pieces**. This proves a specific original graphics
reference, **not** that live actor X15 used this exact frame, nor
a human name such as candle, torch or enemy. Live PPU CHR/palette and
sprite/OAM capture are needed for visible identity.

`cviii_source_visual_0815()` recreates the pointer/size checks of
existing PRG26 `cviii_world_sprites_draw_0807()` and fails closed on
absent bank, escaped pointers or more than 27 compressed pieces.
The resident-world `chapel_projection` registry holds descriptor
CPU address/piece count only for a **confirmed still-active original
actor** with a unique JP0814 source address and generation.
Source records without a verified *visible* live actor receive no
visual descriptor and never draw ghosts. Original allocated-but-hidden
slots remain separate from this visual condition.

## Offscreen source simulation: precise scope and guard

`cviii_world_probe_chapel_0815()` runs after authenticated
vertical chapel camera and original guest-slot capture. It converts
original source positions to extended-world point coordinates using
the original `$37` local Y offset and, **when source-admitted**, the
exact JP0813 original 6502 local-position computation. It classifies
each source as native 256px point, extra-wide margin point, or
outside picture (also clips the fixed first 48 HUD scanlines).
If the **guest** already has a uniquely tagged active type-`$80`
actor, the probe uses its *live* world coordinates, frame, mirror,
palette and original descriptor; otherwise it reports a **non-rendered
source-only candidate**. The existing JP0807 renderer continues to
paint only original game actors. No machine-state writes occur.

The interaction policy is deliberately fail-closed:
source row `$0D` is **not directly an actor**; an unspawned
type `$80` has **no simulated contact**; a real type `$80`
has `MAY_ROUTE_B162`, NOT a hitbox or pickup.
Original raw0B `$B217` first checks `$7E & $F0` and can bypass via
`$B258`; only on the alternative path does type `$80 >= $69`
branch to **`$B162`** rather than the ordinary `$B339`
radius measurement. Its downstream special collision/interaction
effects have **not** been reconstructed. Neither source-only candidates nor
installed-but-hidden slots grant any offscreen interaction; a false
hit/damage/pickup
implementation here would be incorrect.

**Geographic bound:** all nine original chapel record X coordinates
are within `$20..$D8` (32..216 pixels). With actual chapel horizontal
camera X=0, these sources are *already inside* the native 256px
gameplay image. Synthetic camera X=80 tests validate a prospective
extra-wide margin, but **do not** prove offscreen enemy placement
for the wider horizontal Level 1-01/02 world. Other source producers
and room/activation chains remain to be recovered.

## Reproducibility and delivery grade

```sh
python3 JP/decomp/tools/jp_stage1_visual_identity_0815.py --smoke
python3 JP/decomp/tools/jp_stage1_visual_identity_0815.py \
  --rom "/private/Akumajou Densetsu (Japan).nes"
# Owner native project, requires external NESRecomp root and original ROM:
cmake --build <owner-native-build-dir> --target jp_source_offscreen_test_0815
ctest --test-dir <owner-native-build-dir> --output-on-failure -R JP08
```

The isolated C11 source-projection test passed **262,144**
synthetic world/camera point comparisons and 13 guards with
strict GCC and ASan/UBSan locally. The Python owner-ROM fingerprint
audit, Python compilation and ROM-free smoke also passed locally.
The existing integrated world C11 test is extended and the four
JP0803/JP0813/JP0814/JP0815 tests are registered in CTest, but the
whole owner native project / Windows build and a fresh original Mesen
capture **have NOT been executed** in this environment.
No gameplay-wide offscreen AI, collision, pickups or verified
candle identity is delivered or claimed; strict PRG and VPP unchanged.

**Next causal proof:** fresh natural Mesen hardware capture of
source record `$AB1F`→actual X13..18 slot write, original
`$048C/$0400` sprite frame and CHR at output, observed actor
removal/respawn, and the `$B162` special interaction path;
then a separate horizontal-world actor source census.
