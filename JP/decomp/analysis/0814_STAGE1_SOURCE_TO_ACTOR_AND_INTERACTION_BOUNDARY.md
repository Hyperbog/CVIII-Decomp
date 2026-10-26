# JP0814 — Original Stage 1 chapel source-to-actor identity and safe widescreen boundary

**Development head:** PR #16 on `jp0813-level1-source-world-lifetime`, stacking
on PR #13's existing native widescreen world and active-sprite projector.

## Original Japanese 6502 source, authenticated

Owner's retail Japanese VRC6 mapper-24 ROM SHA-256:
`958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`;
physical raw0A SHA-256:
`1460df577d44e114c64fdf34a8837629765f3f6a93d45796fdf81e5ffacb5ed8`.
The nine seven-byte records reside at `$AB1F-$AB5D` plus `$FF` at
`$AB5E`, inside owner-memory-only `00/01/01` room source payload.

This is **two separate original allocation types**. Source CPU
`$827D: LDA ($95),Y` reads field 2; `$827F: BMI $82AC`
selects type >= `$80`, otherwise falls through `$8281`.

| Source-record field 2 | Original call and slot domain | Verified 6502 RAM postcondition |
| --- | --- | --- |
| `$0D` (3 source records) | `$8281 JSR $835F`, source slots `X=0..5` | `$07C2+X=record[2]`, `$07DA+X=record[3]`, `$07E6+X=record[5]`, `$07CE+X=record[6]`, `$07D4+X=local axis`, `$07C8+X=$07E0+X=0` |
| `$80` (6 source records) | `$82AC JSR $8351`, direct object slots `X=13..18` | `$054E+X=record[2]`, `$0438+X=record[3]`, `$05D8+X=record[4]`, `$041C+X=local axis`, `$05EF+X=$30` from original `$8329` script byte |

Original range checks are `$8351: LDX #$0D` through the `$13`
exclusive limit for direct objects; `$835F: LDX #$00` through
`$06` exclusive limit for event source slots. The `$FF24` fixed
callee remains outside this local postcondition's identity claim.
The seven-byte records' first two bytes are the world-axis position.
The local axis uses original `$8205-$8254` admission math from
JP0813 with the **game CPU camera `$54:$53`** (not the potentially
lagged presentation-only PPU scroll). These identity matches
describe the *initial source installation*, not proof that coordinates
remain fixed after AI runs.

## Integrated code behavior

`cviii_stage1_source_link_0814.h` models the two distinct exact
original-RAM signatures; it rejects unsupported record types,
absent initial postconditions and any source matching multiple slots.
`cviii_world_link_chapel_0814` derives local coordinates per source
from original guest camera RAM and compares only authenticated
`$AB1F` source payloads. If multiple distinct sources could claim
one slot, it rejects **all** conflicting links. It makes no
proximity-only associations.

The existing host calls it after a source-verified vertical room
camera sample and the read-only JP0813 source update.
On a uniquely proven direct-object installation, an *already active*
`CviiiWorldActor0803` (same original room, slot and type) can gain
the original seven-byte record CPU address `source_cpu_0814`
and its current slot generation. Deactivating or recycling the actor
clears that provenance; it never causes a guest actor to appear.

The existing JP0807 world sprite renderer projects **only actual
active PRG26 actors** outside the original 256px picture, and the
original NES center/HUD is never repainted. JP0814 does not replace
that renderer, synthesize offscreen actors, enlarge the original
6502 collision domain, or mutate guest CPU/PPU/APU/OAM state.
Thus the new source tags are useful for future source-backed
widescreen presentation without incorrect, unearned interactions.

## Tests performed and remaining verification

- Original ROM, bank raw0A, opcode windows at
  `$827C/$8281/$829F/$82AC/$82B1/$8329/$8351/$835F`,
  and all nine source records were independently inspected locally.
- Local strict C11 and AddressSanitizer/UBSan direct/event matcher tests
  both **PASS**. Nine ROM-derived initial source/slot fixtures and
  nine altered-position rejections also **PASS** against the matcher.
  These are *postcondition fixtures*, not unmodified Mesen gameplay.
- The existing world C11 regression was extended to exercise:
  unambiguous direct type-`$80`, duplicate-source rejection,
  a separate type-`$0D` event slot, provenance tagging of an
  existing active actor, deactivation invalidation and wrong-room
  no-mutation. This full native target has **not** run in this tool
  session. The new standalone matcher executable was added to
  the NESRecomp CMake test targets; Windows build and original
  gameplay still need execution.

**Unresolved for the owner's unrestricted widescreen gameplay
goal:** natural-game Mesen source-to-slot lifetime trace and OAM
type-to-sprite identity, exact offscreen AI/collision/damage
scheduling, stage-wide world placements, cross-room actor migration,
and full Original-vs-Enhanced equivalence. A read-only source
association is not a license to spawn offscreen enemies or simulate
candle pickups. No new strict PRG credit or VPP increase.
