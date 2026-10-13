# Japanese Castlevania III — Original and Enhanced editions

**Product decision (owner, 2026-10-12):** One native C11 game engine
with two selectable editions: **Original** and **Enhanced**.
The goal is a playable PC game that is not constrained by the NES's
sprite and audio channel limits. Do NOT turn these PC enhancements
into NES ROM patches, and do not change original game mechanics unless
the player explicitly selects a gameplay modification in Enhanced.

## Edition contracts

| Feature | Original | Enhanced |
|---|---|---|
| Game logic, enemy AI, physics, damage, collision, stages, routes | Original | **Identical by default** |
| Display | Faithful 4:3 NES viewport | Optional true widescreen (extra scenery, not stretch); graceful 4:3 fallback |
| Sprite evaluation | Original hardware behavior | Optional flicker-free compositing beyond 8 visible sprites per scanline |
| Graphics | Original CHR/palettes | Optional high-resolution sprite / background texture packs |
| Music / effects | Original 2A03 + VRC6 arbitration | Per-generator mixer, independent music/SFX virtual voices, remastered/alternate soundtracks |
| Input | Original game inputs / reference mapping | Rebindable keyboard / controller profiles, conflicts and reset |
| New mechanics | **Never enabled** | Explicit opt-in gameplay modules such as SCIV-inspired multidirectional whipping |
| Save/profile configuration | Base-game-compatible state | Store edition and game-mod flags separately; preserve original saves where possible |

**Do not use the word 'Enhanced' to imply all gameplay mods are enabled.**
Enhanced presentation and audio must work with completely original
attacks, health, character movement and enemy behavior.

## Technical boundaries

**Authoritative game core:** The original code's 6502 CPU state,
RAM/mapper24 VRC6 bank switching, interrupts, simulation clock,
scroll/script events and OAM/register writes remain authoritative.
Generated C and the original-game interpreter fallback use the same
core. Rendering and audio must not alter CPU-visible PPU/APU status,
IRQ timing, sprite-0 hit, input sampling or collisions.

**Native renderer:** Render the standard original 256×240 plane for
reference. Enhanced optionally composites more objects from primary OAM,
without fabricating additional hardware sprite units. Distinguish
game-side dropped sprites (never written to OAM) from the PPU eight
per-line visibility limitation. True widescreen requires recovering
additional valid room/metatile/CHR geometry with appropriate scrolling,
rather than stretching an existing frame or exposing junk nametables.
Preserve original viewport bounds for enemy activation and gameplay.
Back off to pillarboxed reference output where a room cannot be
rendered safely. HD asset pack IDs should account for CHR bank, tile,
palette, flip, sprite composition and frame animation, with fallbacks.

**Native audio:** Pinned NESRecomp currently mixes 2A03 pulse 1/2,
triangle, noise, DMC and VRC6 pulse 1/2, saw into its synthesized PCM.
Channel level/mute/solo controls are a distinct first feature from
fixing music cut-outs. When sound effects overwrite game music
registers, the mixed hardware PCM no longer includes missing notes.
Independent music and SFX require tracing the game's **logical music
and effects events before channel allocation**, using additional
virtual synthesizer voices or substitute cue playback. Preserve
the original timing-facing registers. Soundtrack packs need stable
cue IDs, start/stop/transition synchronization, explicit loops/fades,
and legal rights for user-provided audio.

**Host inputs:** Key/controller remapping translates to original
button states at the same game frame; multiple controllers,
disconnect behavior, conflicts, dead zones and reset-to-default must
be handled. Future optional multidirectional attacks use separate
mod-owned inputs/collision/animation state and **cannot** silently
change original input semantics. If gameplay modifications affect
save compatibility or replay parity, mark them in save/profile metadata.

**Edition UI / config:** Original and Enhanced presets, separately
toggled advanced features, per-feature versioned settings, and a
clear "gameplay modified" marker. Switching back to Original restores
the reference presentation and disables any new gameplay move without
corrupting progress. Original should remain available for diagnosing
any Enhanced-specific artifact.

## Release phases and acceptance

- **Alpha (existing owner-tested):** The original Japanese game
  launches as native C11 Windows x64 and progresses beyond Stage 1.
  The owner's ongoing natural playtest provides route coverage.
  Rendering defects are tracked independently, not confused with
  intentional NES constraints.
- **Beta — Original:** Validate an extended playthrough, alternate
  branches/partners, music and save/reset behavior, fix reproducible
  gameplay and priority bugs. No need for whole-ROM reconstruction
  tests unless a specific failure requires them.
- **Beta — Enhanced foundation:** Expose edition/config selection,
  input remapping and reliable renderer/audio extension interfaces;
  implement enhancements incrementally behind feature flags. Provide
  builds whenever a feature is stable enough to test.
- **Enhanced release:** Widescreen and art packs, flicker-free
  sprites, per-channel audio and replacement soundtracks must be
  verified scene-by-scene or with focused natural playtests. Optional
  new moves are **not** prerequisites for a graphics/audio release
  and are tested separately.
- **Final:** Both editions, supported routes and endings, stable
  controller/sound/video behavior, legal distribution, repeatable
  builds and release documentation.

No game art, ROM-derived generated code, remastered/alternate commercial
music, user saves, or unlicensed third-party engine source may be
published without distribution permission. NESRecomp upstream is
PolyForm Noncommercial 1.0.0 and requires license review.

## Work items

- [Edition presets, gameplay invariant and feature flags](https://github.com/Hyperbog/CVIII-Decomp/issues/4)
- [True widescreen camera and extended room rendering](https://github.com/Hyperbog/CVIII-Decomp/issues/5)
- [Per-channel audio mixing and user-provided soundtrack packs](https://github.com/Hyperbog/CVIII-Decomp/issues/6)
- [Persistent keyboard/controller mapping](https://github.com/Hyperbog/CVIII-Decomp/issues/7)
- [HD sprite/background texture packs](https://github.com/Hyperbog/CVIII-Decomp/issues/8)
- [Opt-in SCIV-style multidirectional whipping](https://github.com/Hyperbog/CVIII-Decomp/issues/9)
- [Flicker-free enhanced sprites](https://github.com/Hyperbog/CVIII-Decomp/issues/2)
- [Prevent SFX from stealing music notes](https://github.com/Hyperbog/CVIII-Decomp/issues/3)
- [Existing Stage 2/4-0A priority/rendering bugs](https://github.com/Hyperbog/CVIII-Decomp/issues/1)

Phase 0589 implements the **initial edition selection and presentation extension**:
`[Game] Edition = Original/Enhanced` and optional
`UnlimitedSprites = 1`, with a runtime native host hook and mock
C11 test. The compositor is experimental and not yet validated on
the owner's Windows build or on Stage 3/4. All other proposed Enhanced
features remain unimplemented; do not treat this extension as a
widescreen or completed flicker-removal release.
