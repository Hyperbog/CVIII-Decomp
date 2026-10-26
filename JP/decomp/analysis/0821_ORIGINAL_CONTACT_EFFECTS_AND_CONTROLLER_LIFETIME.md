# JP0821 — Original B6CE/B5DF/B486 effect semantics, effect23 projection and controller-only Mesen capture

**Target:** Japanese Castlevania III / Akumajou Densetsu, original VRC6 Mapper24
ROM SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.
Physical raw PRG0B SHA-256
`17b216088d12ac7b6a4a68bbea3434dbdba317865bd6cf4d11646a3d4efaf64a`.
All ROM/code-window signatures are tied to that physical bank; no original
retail data, binary savestates, sprites or private unabridged traces are shipped.

## Original CPU actor effect semantics

The owner-local `jp_stage1_contact_effects_0821.py --rom ORIGINAL_JP_ROM`
authenticates the original `$B6CE-$B706`,
`$B5DF-$B628` and `$B486-$B4D4` code ranges, dispatch
bytes and effect-field writer instructions.

**`$B6CE` — original actor response:**
- If original `$054E,X` is outside types `$30–$57`, return.
- For an ordinary eligible type other than `$49`, if
  `$0470,X & $02` is clear, original `$B6E4` sets bit `$02`
  and masks original `$0565,X &= $3F`. If bit already set, return.
- For type `$49`, original branch at `$B6DB` enters
  `$B6F5` and iterates **slots X=1..8**. It checks each
  slot's `$0470` bit `$02` and invokes `$B6E4`
  for every unmarked slot, **without rechecking their types**.
  This path exits at `$B706 RTS` with CPU X=`$09`.

**`$B5DF` — original visual effect, not an allocator spawn:**
- The availability gate checks **`$0400+$17`**, *not*
  `$054E+$17`. If occupied, return without creating an effect.
- Otherwise original CPU obtains Y from partner `$041C,$9B`
  and X from original actor `$0438,X`.
- Original sprite/effect **slot 23** receives
  `$0470=20`, `$0400=12`, `$048C=0E`,
  X/Y positions and `$89=08`; the CPU restores X
  from original zero-page `$69`.
- Crucially, `$054E+23` is **not written** by the
  routine. The original PRG26 margin sprite renderer
  already accepts authentic nonzero-frame visuals even
  when an enemy allocator type is zero.
- New `cviii_effect23_witness_0821` checks the exact
  original sprite-postcondition *on real game RAM*, without
  claiming that a static snapshot proves `$B5DF` was
  invoked. The resident world records only observed
  effect23 signature entries; it neither spawns an effect
  nor treats slot23 as an enemy.

**`$B486` — original actor reaction-state consumption:**
- Types below `$30` return; types `$58+` route
  to external `$B47B`.
- Within types `$30–$57`, if high nibble
  `$0669,X & $F0` is zero, return. Otherwise shift that
  nibble right by 4 into scratch `$01` and store
  `$0669,X &= $0F`.
- When original `$0470,X & $02` is set, continue at
  `$B4D7`, beginning with `JSR $E75A` and other
  unproven downstream effects.
- Otherwise decrement `$067B,X` by the original
  high nibble, modulo 256. Zero or negative (N flag)
  results enter **`$B525`** defeat/response path.
  Positive nonzero enters `$B4BC`, beginning with
  `JSR $E249`. The native model **stops before** both.
- The full `$B4D7–$B524`, `$B525–$B5DE`
  and `$E249/$E75A/$B5C4/$8282` subpaths
  have external sound, actor change, map and event
  side effects that have not been proven equivalent.
  Do not infer hitbox, damage, pickup or native offscreen
  NPC lifetime from this routine prefix.

The new C11 `cviii_contact_effects_0821.h` returns **predicted
original writes and first unsupported PC**, never applies them
to NESRecomp RAM/PPU/mapper, never manufactures native enemies
and never inserts a second effect sprite.

## Actual native product wiring

`cviii_world_capture_live_0803` now records the original
slot23 `frame=$12 / selector=$0E / flags=$20`
signature after an independently attested source-room
CPU frame. It preserves the separate facts that
`$054E+23` may be zero and the original sprite is
nevertheless eligible for existing PRG26 rendering.
The entry counter counts **signature appearances**,
not independently witnessed `$B5DF` game-code calls.
A zero frame removes the visual witness; savestate
reinitialization clears volatile observation epochs while
preserving the authentic resident world/room sources.

## Natural controller-reached Mesen: precise evidence grade

[JP0509](0509_MESEN_ACTOR_LIVE_FINDINGS.md) independently
proved **natural type-`$3D` actor creation**, using the
owner-original Japanese ROM and unmodified Mesen 2.1.1:
frame **3092**, original `$84F3` bank0A source
X=`$03`, row `$32`, then an original
**600-instruction CPU trace** with original
slots **1 and 2** newly type `$3D`.
The original trace hash is
`dce02d6ce15c65a4b2dbdeea880b3171206514eeb7d35bb9168fcff56db48d93`.
Its natural creation witness is **not** a natural contact
or eventual deallocation witness. It does not establish
that source-parent `$0645` stayed unchanged across frames.

For a full controller-reached lifecycle, the new
`jp0821_mesen_original_lifecycle_probe.py` reuses
the same JP0509 cold-boot controller schedule and
checks that authentic frame3092/600-step actor creation
still exactly reproduces; then from the **same unmodified
post-creation save-state** it probes:
- Bank-qualified original `$B727` instruction execution,
  checking that original CPU X is *one of those same two*
  original child slots, type `$3D`, flagged by
  `$0470` bit `$04`, and source index `$0645=$03`.
- First natural **writes** to original actor type
  `$054F` and `$0550`; independently steps each
  writer to determine whether type changed to zero.
- Only chronological **same-child**
  contact-before-type-zero writer from that
  same replay baseline may count as a complete candidate
  lifecycle; all unrelated actors, nonzero writes,
  timeouts or missing breakpoints report incomplete
  evidence. The driver never edits the original
  CPU PC, register, mapper or RAM. Private savestates
  and full traces exist only in a temporary directory,
  with compact event status reported separately.

**Execution blocker:** the Mesen headless agent and
matching core are not installed in this session;
container DNS does not resolve GitHub. The new capture
driver is **not yet executed** here. It is provided
for a deterministic, bounded original-game replay,
not as claimed proof of contact/deallocation.

```sh
python3 JP/decomp/tools/jp_stage1_contact_effects_0821.py \
  --smoke --rom "/private/Akumajou Densetsu (Japan).nes"
python3 JP/decomp/tools/jp0821_mesen_original_lifecycle_probe.py \
  --rom "/private/Akumajou Densetsu (Japan).nes" \
  --mesen "/private/mesen-agent" --frames 1200 \
  --report "/private/jp0821_lifecycle.json"
```

## Regression evidence and further boundary

New `jp_contact_effects_test_0821` covers original
type-`$49` 8-slot sweep, guarded bit2 updates,
slot23 effect acceptance using frame not actor type,
`$B486` nibble consumption/8-bit depletion and
unsupported downstream callback stops; strict C11
and sanitizer validation are local.
The world integration test asserts a real guest
slot23 sprite can be visible with original actor type
zero, will not count repeated identical frames as
new effects, and disappears when original frame clears.
The Windows builder explicitly executes the new
`JP0821_` CTest and the previously existing JP0803
resident-world test. Current CI status must be read
from the latest PR16 head before marking passes.

**Not implemented:** a new Mesen contact/despawn
event capture, original-vs-compiled original
`$E75A/$E249/B525` effect parity, extra-wide
independently scheduled AI/hitboxes, pickups, or
full-world game behavior.

**Certification unchanged:** strict PRG
**49,504/262,144 (18.8843%)**, VPP **31/100**.
