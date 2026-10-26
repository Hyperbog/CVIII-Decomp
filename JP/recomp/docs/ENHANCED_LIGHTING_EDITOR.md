# Enhanced lighting editor — JP0662

**State:** SDL2 integration compiled in Linux and Windows Alpha builder CI.
Owner gameplay / interactive Windows acceptance is not yet certified.

## Player controls

Press **Home** during Enhanced gameplay to enter or leave the paused editor.
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
| Home or Escape | Close editor |
| Ctrl+Home | Change the editor shortcut (press the new key; Escape cancels) |

**Keybinding:** Home opens or closes the editor by default. To remap it
without leaving the game, press Ctrl+Home, then the replacement key.
The new key takes effect immediately and is saved to [Game] as
`LightingEditorKey = Home` (or the chosen SDL scancode name) in
`config.ini`. You can also edit that value with the game closed.
Escape cancels capture; F4/F6/F8/F9/F10/F11/F12 and other reserved
system keys cannot be assigned. Avoid choosing a key currently used
for NES controls. The Ctrl+Home remapping gesture remains available
even if the editor key itself changes.

Maximum 128 lights per saved profile. Default warm color RGB (255,167,74),
radius 56, intensity 85 and ambient 78%. The native host stores Lighting,
LightAmbient and Light00..127 in the existing [Game] config.ini. These
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

## Dear ImGui lighting studio — genuine modern in-game editor

This is now an **actual Dear ImGui UI**, not a hand-drawn 256×240
pixel-art dock. Press Home (or your mappable shortcut) in Enhanced
gameplay to pause and open the resizable, movable
**CVIII | LIGHTING STUDIO** window. The UI is drawn at desktop/window
resolution *over* the pixel-perfect NES image. The menu does not write
to the emulated CPU, PPU, OAM, or game save states.

The UI uses Dear ImGui v1.93.0 (MIT), fetched and built at its pinned
tag, with the official SDL2 SDL_Renderer backend. OpenGL is **not**
assumed: SDL2 selects the system's accelerated renderer (often D3D
on Windows, sometimes OpenGL), and the bridge works either way.
No ReShade injection, Windows graphics driver hooks or extra runtime
graphics DLL are required.

- **Scene Lights**: genuine scrollable selectable list for the current
  candidate room. Click any row to select a light, even if its center
  lies behind the window.
- **Add Light**: click the button, then click any exposed part of the
  scene. Drag the existing light handle (20 game-pixel grab radius).
- **Radius / Intensity**: full mouse sliders with numeric values.
- **Light Color**: full color-edit control with hue wheel, RGB numerical
  editing, and warm candle/cold blue/white presets.
- **Enable Lighting / Ambient**: checkbox and adjustable ambient slider.
- **Delete Selected / Resume Game**: explicit buttons; Home/Escape
  also close the editor.
- **Persistence**: changes use the existing config.ini lighting keys.
  UI placement is not written to imgui.ini in the working directory.

The rendering bridge is
`JP/recomp/native/enhanced/cviii_imgui_editor.cpp` (C++17) and is
built **only for windowed Enhanced-host builds**. The original game
remains C11. The public build kit still contains no ROM or game binary;
the private Windows Alpha includes the pinned Dear ImGui MIT license.

**Mouse tracking fix:** SDL2's game renderer sets a 256x240 logical
size, which automatically scales SDL2 mouse events to game pixels.
The Dear ImGui SDL2 backend expects coordinates in *window* pixels.
The editor now reverses that scaling with
`SDL_RenderLogicalToWindow()` before forwarding mouse-motion and
button events, including panel hit testing. Scene placement converts
those same window pixels back through the original game's coordinate
conversion once (not twice). This handles integer scaling, resize,
and letterboxing without modifying game renderer output.

**QA pending:** Although CI can compile the actual SDL window renderer,
mouse capture, HiDPI scaling, sliders and screenshot legibility still
need an owner's Windows visual acceptance pass. Do not treat a
successful build as proof of interaction or lighting fidelity.

## Expanded editing — groups, shapes, ambient and real ReShade

**Native studio:** The revised Dear ImGui workspace now uses Home, Scene,
Settings, Statistics and About tabs, inspired by ReShade's preset/effect
list layout. This is the existing embedded UI, not an add-on DLL.

- **Light names and groups** can be assigned independently and viewed
  under collapsible group headings; the light list can be searched by
  name or group. Lights can be muted or enabled without deleting them.
- **Copy, Paste and Duplicate** operate on complete light properties,
  including source room-independent metadata. Ctrl+C/V/D are supported
  when the cursor is not editing text. Paste inserts into the current
  room near the visible camera center. Duplicate offsets 12×8 pixels.
- **Shapes:** point/radial (original soft glow), **cone** (direction +
  adjustable half-angle), and **shaft** (direction + beam width).
  These are physically *illustrative 2D masks*, not 3D light transport
  or occlusion-aware volumetric shadows. Existing radial light
  profiles load unchanged.
- **Flicker:** Subtle, Steady and Torch controls are per light.
- **Exact coordinates:** X and Y can be entered numerically to move
  lights, including those hidden under the editor.
- **Scene ambient:** the Scene tab defines brightness 0–100 and RGB
  tint for a particular candidate stage/room; rooms without an
  explicit override inherit the original global ambient setting.
- **Settings serialization** retains the old `Light00` entries and
  adds `LightStyle00`, hex-encoded `LightName00` /
  `LightGroup00` (UTF-8) and `RoomAmbient00`. Old configs remain
  readable. Invalid labels are rejected rather than partially loaded.
  A maximum of 128 lights and 32 ambient overrides are supported.

**Actual ReShade overlay:** An independent optional add-on project is
now under [`JP/recomp/reshade/`](../reshade/README.md).
It uses ReShade's `register_overlay("CVIII Lighting", ...)`, so when
installed against the full-add-on-enabled ReShade runtime, the
controls are intended to appear within **ReShade itself**. It must
be compiled and installed separately, and is **not yet owner-tested**
or included with the standard private Alpha. Its first iteration
supports named lights, groups, clipboard, shape and scene controls;
new ReShade-side lights are created at the visible scene center
and then moved using exact X/Y. Direct scene-click placement in the
ReShade add-on is still pending. ReShade Home may conflict with the
native Home editor shortcut: set `LightingEditorKey = End` for
ReShade testing.

## Windows owner visual acceptance — Stage 1

This is a reproducible manual test, **not a claim of completed gameplay QA**.

1. Download the branch's Windows Alpha *build-kit* artifact from its successful
   GitHub Actions Windows Alpha builder job and privately rebuild the game
   using your own authenticated Japanese ROM (the ZIP is not a game binary).
   An existing previously built AlphaCandidate EXE does **not** automatically
   update; use the documented forced Rebuild flow.
2. Launch Enhanced, enter Stage 1, and press Home. The game should stop moving
   and the translucent LIGHTING WORKBENCH should open on the right. Click near an existing
   torch/candle in the playable area, below the top 48 HUD scanlines.
3. While still paused, change radius with the wheel and intensity with
   Shift+wheel, or drag the RADIUS and POWER sliders. Select a
   light from the SCENE LIGHTS list and adjust RED, GREEN and BLUE sliders. The numeric status toast should display the selected
   light's R (radius), POWER, RGB and AMB values. Check for smooth illumination
   without white clipped outlines or obvious color banding.
4. Press Home to resume; walk until the light is completely outside the viewport
   (and beyond its radius), then walk back. It should disappear, return, and
   continue illuminating its original level location. When the center is just
   offscreen but the radius overlaps the image, some edge illumination is
   physically expected. Try crossing a 256-pixel nametable boundary.
5. Walk into another room/stage; a light from Stage 1 should not appear in
   a different room. Return and confirm it is still present. If it blinks,
   the candidate ROM stage/room key requires correction; do not merge.
6. Exit and restart without resetting config.ini; placed lights, RGB, radius,
   intensity and ambient should survive. F4, F6, F8/F9 and F10 should
   retain their native behavior before and after Home.
7. With Home closed, press F12 to capture a picture without editor markers.
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
