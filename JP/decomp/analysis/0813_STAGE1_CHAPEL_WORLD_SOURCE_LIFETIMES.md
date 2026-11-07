# JP0813 — Stage 1 chapel original world-axis admission and resident source lifetime

**Implementation branch:** `jp0813-level1-source-world-lifetime`, based on the
existing **PR #13** resident-world/native widescreen runtime. This is not a
parallel simulation or a replacement for NESRecomp.

## Source proof and new product behavior

Owner-supplied Japanese Mapper24 ROM SHA-256:
`958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.
Original physical raw PRG0A SHA-256:
`1460df577d44e114c64fdf34a8837629765f3f6a93d45796fdf81e5ffacb5ed8`.

The three-tier `$801E-$8046` hierarchy distinguishes **two stage-zero
1-02 sources**, rather than treating them as one byte stream:

| Original selector ($34/$35/$36) | Root | Actual consumer |
| --- | --- | --- |
| `00/01/00` | `$93E8` | Original `$8106` six-slot source/auxiliary-cell installer (JP0664) |
| `00/01/01` | `$AB1F` | Original `$8205/$8275` seven-byte **vertical scrolling world objects** |

The second root contains **nine 7-byte records plus one `$FF`**
(`$AB1F-$AB5E`, 64 bytes), not 30 earlier raw0E records.
Six third-field values are `$80` and three are `$0D`.
The types are **not** presently certified as candles or named enemies.
The first two source bytes form a big-endian 16-bit world-axis
position (loaded into `$09` high and `$0A` low by original
`$8321`); field three supplies the orthogonal X position.
The physical source-window SHA-256 is
`dd742e7f329382fed658e0b2d6847cc3b55965b55380a2c8fd057b75cc15917e`.

Original CPU `$8213-$8248` performs two chained 6502 `SBC`
operations against the **16-bit camera `$54:$53`**, checks negative
high byte and optional `$10` correction, admits only the original
bounded local interval (`$02 < $B9`), and writes local vertical
placement `($02+$37)&$FF`. The implemented
`cviii_stage1_admit_0813` retains the exact byte wrap and borrow
behavior. It is not a signed-host `abs(world-camera)` approximation.

**Integrated runtime:** when the already-authenticated
`chapel_camera_0808()` succeeds, the live presenter updates the
persistent world registry's nine original seven-byte source identities.
Each record retains original source CPU offset, world-axis coordinate,
orthogonal source X, raw actor type, original eligibility,
projected axis and saturated entry/exit counters. Once the independently
verified room graph places this chapel, original source XY is projected to
global world XY as (room.x+record[3], room.y+16-bit axis). Unknown room
connections leave world_placed=0 and NO guessed global position. An object leaving
the original activation window remains **resident as source geometry**
and can re-enter without a fresh ROM extraction. This tracking is
independent of PRG26's original 28 *active* sprite/actor slots.
State-load/reset clears the observer epochs but retains the already
authenticated room payloads and source-layout graph.

No guest RAM, mapper registers, virtual actors, hitboxes, collision
decisions or AI timers are changed. An eligible source is **not**
declared spawned or rendered, and an expired active actor is **not**
kept alive in emulation. The native game still controls original
activation/culling. This is the **resident source and lifetime
foundation**, not complete offscreen AI or widescreen gameplay parity.

## Validation and remaining acceptance

- Uploaded original JP ROM SHA and raw0A source SHA **PASS** locally;
  the documented 9-record chapel span/source hierarchy are checked.
- A **262,144-case C11** synthetic independent byte/borrow oracle
  (world 0..511 × camera 0..511) matched every returned admission
  and projected-axis byte under strict GCC with ASan+UBSan, locally.
- Existing `cviii_level1_world_test_0803.c` now exercises nine
  invented seven-byte sources, original activation, exit while still
  resident, reentry, wrong-selector rejection, and reset.
- `jp_stage1_source_window_test_0813` is registered as a C11
  native test target. Entire NESRecomp host CI and original gameplay
  acceptance are **not claimed** by the local isolated test.

**Open causal requirements:** verify the chapel's real camera and
`$8205` event frames with Mesen, correlate individual source records
to actor slots and rendered sprites, resolve types `$80/$0D`,
then present extended-view actors from original rules while preserving
a reversible vanilla mode. No new VPP/strict PRG percentage is claimed.
