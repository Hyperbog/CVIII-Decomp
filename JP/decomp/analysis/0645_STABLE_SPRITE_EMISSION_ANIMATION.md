# JP0645 — Enhanced stable-sprite OAM rotation and animation hardening

## Owner-visible scope

This checkpoint improves **only** the already optional PC-native
`-StableSprites` presentation pass. It does not modify game CPU/PPU/APU
simulation, original OAM bytes, movement, hitboxes, VRAM registers, IRQ
timing, save-state serialization, the stock renderer, audio, or any
gameplay resource. The playable Japanese original and Enhanced default
path are unchanged. Graphics issue #1 remains **owner-resolved and
closed**; JP0645 is not an attempt to reopen that problem.

## Original game sprite identity

JP0609 authenticated the PRG26 original sprite emitter:
- Each frame shifts start byte offset `$22` by `+$44` (17 OAM slots).
- Each consecutive logical sprite is emitted `+$C4` bytes later
  (minus 15 slots modulo 64).
- NES primary OAM slot priority therefore rotates even if the same
  game-side objects remain present.

Original physical OAM sprite indices are **not actor identities**.
JP0609 already uses the emission order for drawing; JP0608 history
association still relied on tile equality and short physical-slot
coincidences. An animation can change tile number while the game's
phase simultaneously moves the exact same logical sprite to a new
physical slot. The history code then treats it as a vanished sprite
and rescues an old pixel piece for one unnecessary frame.

For word-aligned offsets, the reversible permutation is:

```
emission = ((physical_slot - (phase >> 2)) * 17) & 63
physical_slot = ((phase >> 2) + emission * 49) & 63
```

17 and 49 are multiplicative inverses modulo 64 because
`49 * 17 = 833 = 13 * 64 + 1`.
The algorithm first matches unique old/new emission identities,
accepting tile/flip animation when position (within 4 pixels),
sprite height and palette grouping agree. Every new sprite can
consume **at most one** previous sprite. Any unmatched prior
sprite then tries the existing conservative tile/attribute/proximity
matching, now also one-to-one and nearest-first within each old
candidate. Unpaired old sprites can still be held for **at most
one frame**, subject to the existing scene-change suppression.

If the offset is not OAM-word-aligned the logical-association pass is
disabled rather than inventing an identity. All phase arithmetic is
unsigned/modulo 64; no original CPU RAM or PPU state is written.

## Reproducible tests

Existing JP0608 suite still covers behind-background priority,
transparency, sprite left-edge clipping, one-frame rescue, original
OAM rotation compositing and reset.

New `cviii_sprite_identity_test_0645.c` links the **same production C11
sprite-layer implementation**, with synthetic OAM and pattern bytes:

1. Phase 00 to 44: animated tile 1→3, flip and small motion,
   second overlapping sprite retained, no rescued ghost.
2. Two same-palette lookalikes, one absent: the single live sprite
   cannot consume two previous logical identities.
3. All 64 logical emissions rotate, with all 64 tiles animating
   together: no ghosts or out-of-bounds placement.
4. Non-word-aligned phase disables untrusted identity tracking.
5. Phase FC→40 wrap preserves emission 0.
6. Mass OAM removal suppresses scene-transition ghosts.
7. Power/reset clears history; sprite-disable masks never paint.

Both Windows CMake SDL2 owner-kit builds and Linux external NESRecomp
integration compile the production renderer and execute this additional
strict C11 suite. Public CI uses **synthetic** invented ROM data, not
real Japanese game playthrough evidence.

### Private owner spot-check

Use an **up-to-date separately rebuilt private candidate**, retaining
the previous working build for fallback. Run the same known playable
Stage 1/doorway and Stage 4-0A scenes with StableSprites OFF and ON,
looking for one-frame doubled outlines during Trevor/partner turn,
jump, sprite overlap and room transitions. Leave the default OFF
unless the optional enhancement looks better. If a new regression
appears, report the stage, companion, action and setting rather than
reopening historical issue #1 without evidence.

## Evidence boundaries

A successful synthetic C11 suite and cross-platform compiler establish
the host's structural behavior, not original-vs-native pixel-perfect
graphics across stages or real owner Windows sprite visual acceptance.
Original game semantic source counts remain exactly
49,504/262,144 bytes (18.8843%), VPP27/100, certified checkpoint0508,
fixed frontier $FB96 and R-002 OPEN. All modding features remain
deferred until Enhanced Edition completion.

## Authenticated Japanese source-byte corroboration

The optional owner-local `JP/decomp/tools/jp_sprite_emission_source_0645.py`
identifies the exact original PRG26 bank-26 byte windows at physical
PRG offset `0x34019` (`A5 22 18 69 44 85 22 85 04`) and
`0x34051` (`8A 18 69 C4 AA 88 D0 F3`). The former contains
`LDA $22; CLC; ADC #$44; STA $22`; the latter contains
`TXA; CLC; ADC #$C4; TAX`, supporting the static emitter-rotation
interpretation. It checks the exact supplied owner Japanese ROM hash,
iNES mapper24 and both byte windows; no ROM is copied to Git.
The ROM-free synthetic bank/tamper fixtures plus 4,096 inverse-permutation
cases run in Windows/Linux CI. Authenticated retail ROM audit was
actually run locally and passed. These are **original source bytes**,
not proof of runtime liveness or gameplay-layer pixel parity.

```sh
python3 JP/decomp/tools/jp_sprite_emission_source_0645.py --smoke
python3 JP/decomp/tools/jp_sprite_emission_source_0645.py --rom "/private/Akumajou Densetsu (Japan).nes"
```
