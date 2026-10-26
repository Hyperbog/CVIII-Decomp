# Enhanced lighting editor — JP0662

**State:** SDL2 integration compiled in Linux and Windows Alpha builder CI.
Owner gameplay / interactive Windows acceptance is not yet certified.

## Player controls

Press **F7** during Enhanced gameplay to enter or leave the paused editor.
Changes are reflected in the presented picture immediately.

| Input | Function |
| --- | --- |
| Left click / drag | Place or move a light |
| Right click | Select nearby light (within 10 world pixels) |
| Wheel / +/- | Change radius |
| Shift+wheel / PageUp/PageDown | Change intensity |
| Ctrl+wheel / [ and ] | Adjust ambient darkness |
| C | Cycle warm, cool, red, green, neutral |
| Delete or Backspace | Delete selected light |
| F7 or Escape | Close editor |

Maximum 24 lights per saved profile. Default warm color RGB (255,167,74),
radius 56, intensity 85 and ambient 78%. The native host stores Lighting,
LightAmbient and Light00..23 in the existing [Game] config.ini. These
are presentation settings and do not enter the original NES save state.

## Rendering and scrolling design

- The lighting module operates on 256x240 ARGB output after Enhanced sprite
  composition and before Enhanced Start/Audio menu overlays.
- Rows 0..47 are excluded so score and health UI stay readable.
- Game CPU, PPU timing, sprite-0, mapper, enemy collisions, game input and
  reference Original presentation are unmodified.
- NESRecomp provides line-by-line PPU scroll data from the actual frame.
- Japanese ROM RAM $53/$54 is used as the camera reference to unwrap the
  NES's 512-pixel horizontal PPU coordinate repeat.
- RAM $34/$35/$36 and $07A0 generate a candidate stage/room identifier.
  Verify that key in real game scenes before asserting cross-room stability.
- Vertical world coordinates currently retain the PPU 0..479 wrap domain.
  Full vertically extended levels need additional unwrapping and QA.

## Windows owner visual acceptance — Stage 1

This is a reproducible manual test, **not a claim of completed gameplay QA**.

1. Download the branch's Windows Alpha *build-kit* artifact from its successful
   GitHub Actions Windows Alpha builder job and privately rebuild the game
   using your own authenticated Japanese ROM (the ZIP is not a game binary).
   An existing previously built AlphaCandidate EXE does **not** automatically
   update; use the documented forced Rebuild flow.
2. Launch Enhanced, enter Stage 1, and press F7. The game should stop moving
   and the LIGHT EDITOR help toast should appear. Click near an existing
   torch/candle in the playable area, below the top 48 HUD scanlines.
3. While still paused, change radius with the wheel and intensity with
   Shift+wheel. Ctrl+wheel changes ambient. Select with right-click,
   cycle color with C. The numeric status toast should display the selected
   light's R (radius), POWER, RGB and AMB values. Check for smooth illumination
   without white clipped outlines or obvious color banding.
4. Press F7 to resume; walk until the light is completely outside the viewport
   (and beyond its radius), then walk back. It should disappear, return, and
   continue illuminating its original level location. When the center is just
   offscreen but the radius overlaps the image, some edge illumination is
   physically expected. Try crossing a 256-pixel nametable boundary.
5. Walk into another room/stage; a light from Stage 1 should not appear in
   a different room. Return and confirm it is still present. If it blinks,
   the candidate ROM stage/room key requires correction; do not merge.
6. Exit and restart without resetting config.ini; placed lights, RGB, radius,
   intensity and ambient should survive. F4, F6, F8/F9 and F10 should
   retain their native behavior before and after F7.
7. With F7 closed, press F12 to capture a picture without editor markers.
   Capture a matched Original reference and Enhanced lighting image at
   the same stage/frame if possible. The original reference must be unchanged.

Suggested evidence: one lit room screenshot, one dark-area screenshot,
one image after returning from a scroll, plus a note of stage, camera direction,
whether loading and restarting preserved placement, and any light flicker/jump.
Do not share or commit your private ROM or proprietary generated game sources.

## Visual restraint

Lighting uses a soft highlight shoulder to prevent additive flame colors
from clipping already-bright NES palette pixels to white. Full black stays
black, ambient shadow is present only in Enhanced lighting mode, and the
game HUD is not darkened. This is 2D illumination: no 3D surface normals
or geometry-based cast shadows have been synthesized.

## Research-informed flicker

The implemented light modulator combines gentle smooth oscillations at
0.73 and 1.71 Hz (aesthetic choices) with a very small 10.2 Hz term
for high-intensity warm lights. Independent phases prevent obvious
synchronization. The exact coefficients are deliberately artistic,
not experimental amplitude-fit measurements. Isolated candles generally
flicker less than close groups of candles.

1. Chen et al., *Frequency and Phase Characteristics of Candle Flame
   Oscillation* (2019): coupled candle bundles show approximately
   10–12 Hz oscillations, with single candles comparatively stable.
   https://doi.org/10.1038/s41598-018-36754-w
2. Gergely et al., *Flickering candle flames and their collective behavior*
   (2020): measured frequency depends on bundle geometry and oxygen.
   https://doi.org/10.1038/s41598-020-78229-x
3. Syouichi & Akashi, *Measuring Fluctuation of Japanese Candle and
   Consideration* (2009): decreasing spectral power with frequency.
   https://doi.org/10.11515/ieijac.42.0.30.0
4. **Future shadows only:** Tan et al., *RTSDF: Real-time Signed Distance
   Fields for Soft Shadow Approximation in Games* (2022).
   https://doi.org/10.5220/0010996200003124
   The SDF occlusion technique is not implemented in this phase.

## Acceptance gates

- Strict C11 synthetic scroll, room exclusion, persistence and HUD tests.
- Original/Enhanced host adapter fallback regression tests.
- Final pinned-source Python SDL overlay smoke tests.
- Linux + Windows Alpha source compilation.
- **Pending owner QA:** Stage 1 light placement; scroll away and back,
  nametable-wrap, vertical-room and alternate stage transitions, save/relaunch,
  F4/F6/F10 menu compatibility and controller input suppression.
- **Not implemented yet:** geometry-based shadows, automatic light emitters,
  GPU bloom, exact vertically unwrapped stage geometry.

Keep as draft until the real Japanese Windows gameplay tests pass.
