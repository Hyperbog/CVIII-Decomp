# Castlevania III for PC — one Enhanced edition

**Current product decision (owner, 2026-10-13):** Ship **one
player-facing Enhanced edition**, not separate Original and Enhanced
editions. Anyone wanting unmodified NES presentation can play the
original cartridge or ROM using an emulator. The native PC project
should provide meaningful PC-specific improvements.

**Internal reference is not a public edition.** Keep the existing
`--edition original` reference presentation path in developer builds
for frame/palette/PPU parity tests and bug isolation. Do not remove
original gameplay simulation, NES state semantics, or diagnostic
regressions: a separate "Original" menu choice or public batch
shortcut is unnecessary.

## Single Enhanced gameplay contract

| Area | Public Enhanced behavior |
|---|---|
| Core game | Preserve original enemy AI, physics, collisions, level structure, bosses, partner routes and passwords by default |
| Graphics | Fix the shared original PPU/mapper rendering defects first; offer improved sprites, flicker reduction, widescreen geometry and optional replacement art as each is verified |
| Audio | Support enhanced mixing and optional soundtracks once original cue/driver behavior is verified; avoid changing original event timing |
| Input | Configurable keyboard and gamepad bindings, including modern layouts |
| Progress | Compatible saves where technically possible; track gameplay-mod flags to protect state compatibility |
| Optional mods | New moves, changed difficulty, novel routes and expanded content are *opt-in*, never activated merely by starting Enhanced |
| Debugging | Private internal reference PPU path and F10 stage/password tools remain available for QA and verification |

**No false feature claim:** The current playable native build does not
yet provide widescreen, HD textures or independent music/SFX voices,
and sprite-limit removal remains experimental. Therefore the public
Enhanced default keeps unverified visual features **off** until their
scene-specific tests pass. The known Stage A-01 shared pixel corruption
is **not** fixed by switching edition labels. The goal is a
single Enhanced product with progressively validated improvements,
not simply relabeling the present original renderer.

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

**Enhanced UI / config:** One player-facing Enhanced preset with
separate advanced feature toggles and a clear "gameplay modified"
marker. Keep `--edition original` as an undocumented/internal
reference switch for parity diagnostics; no player-facing edition
picker. Disabling an optional mod restores original gameplay behavior
without corrupting progress.

## Release phases and acceptance

- **Alpha (existing owner-tested):** The original Japanese game
  launches as native C11 Windows x64 and progresses beyond Stage 1.
  The owner's ongoing natural playtest provides route coverage.
  Rendering defects are tracked independently, not confused with
  intentional NES constraints.
- **Beta — Core parity:** Validate an extended playthrough, alternate
  branches/partners, music and save/reset behavior, fix reproducible
  PPU/mapper priority defects. Compare against original reference mode
  internally, not as a second public product.
- **Beta — Enhanced foundation:** Expose optional feature/config selection,
  input remapping and reliable renderer/audio extension interfaces;
  implement enhancements incrementally behind feature flags. Provide
  builds whenever a feature is stable enough to test.
- **Enhanced release:** Widescreen and art packs, flicker-free
  sprites, per-channel audio and replacement soundtracks must be
  verified scene-by-scene or with focused natural playtests. Optional
  new moves are **not** prerequisites for a graphics/audio release
  and are tested separately.
- **Final:** One Enhanced edition, supported routes and endings, stable
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

## JP 0591 — save states, Original and Enhanced

Both editions use the **same whole-machine emulator save state**:
Original and Enhanced are runtime presentation/audio choices, not
separate emulated cartridges. The owner's existing Alpha has F8/F9
single-slot quick save/load. Next windowed builds add Ctrl+0..9
selection with F8/F9 to save/load selected slot, with legacy slot0
filename unchanged. The existing NESRecomp compiled-program/layout
compatibility checks remain authoritative; saves are not guaranteed
portable between independently rebuilt executables. See
[save-state implementation](../analysis/0591_SHARED_ORIGINAL_ENHANCED_SAVESTATES.md).


## JP0597 — ROM-authenticated private offline asset pack

The first asset-package slice extracts **complete physical CHR ROM**
(128 * 1 KiB pages; 8,192 planar NES tiles) and deterministic decoded
8x8 palette-index pixels. It also records all six original-JP password
tables at their authenticated physical 8 KiB PRG bank offsets.
Per-entry SHA256, per-page SHA256, a complete versioned manifest and
exact 2bpp-to-indices-to-2bpp reconstruction are checked. A later build
reuses a cache only after full verification; malformed or stale archives
fail closed. Private Windows Alpha builders create an owner-local
CVIII-Assets.bin, explicitly omitted from public CI artifacts.

This is **an offline cache**, not a rewritten graphics renderer, a
stage-data decompilation, or a substitute ROM for NESRecomp.
Background/sprite interpretation, metatiles, palettes, stage maps,
animation, music, and text extraction remain open; no strict semantic
PRG or VPP progress is claimed.
