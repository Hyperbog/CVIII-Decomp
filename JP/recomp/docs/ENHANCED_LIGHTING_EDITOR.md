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
new ReShade-side lights support Add Light: Click Level via the
native SDL2 coordinate mapping, with Add at Center and numeric X/Y
as alternatives. Genuine overlay click placement is not owner-verified. ReShade Home may conflict with the
native Home editor shortcut: set `LightingEditorKey = End` for
ReShade testing.

## Global Lighting Library and Sky Fill

The **Library** tab in the embedded Dear ImGui studio now contains seven
reusable, named lighting archetypes. They are **not** tied to the
screen, and each invocation allocates fresh emitters in the current
candidate room:

| Template | Emitters | Suggested use |
| --- | --- | --- |
| Candle | 1 small warm radial source | Candlesticks, sconces |
| Torch | 2 (flame core + wider spill) | Castle wall torches |
| Lantern | 2 (glass glow + bounce) | Enclosed hand lamps |
| Window | 2 (cool shaft + diffuse bounce) | Dungeon windows |
| Moonlight | 2 (blue shaft + cool bounce) | Night exteriors |
| Sunbeam | 2 (warm cone + diffuse bounce) | Daytime shafts |
| Magic | 2 (colored core + halo) | Spells, altars |

**Apply Here** inserts the rig at camera center. **Place...** enables
one-click placement at an exposed scene position. Each placed rig is
an ordinary group of independently editable lights; colors, shapes
and intensities can be customized after placement. Placement fails
atomically if there are insufficient free slots or the rig extends
outside the supported 0..65535 horizontal / 0..479 vertical world
coordinate domain.

To create a reusable **custom global group**, select a light in a
named group, choose one of 12 library slots, supply a kit name, and
click **Save Selected Group as Global Kit**. The entire set (up to
eight emitters) is captured relative to the selected light's world
position. Reapplying the kit to another scene restores individual
names, colors, geometry, flicker modes, and relative spacing, but
assigns the new scene room ID. This is *not* an active link: editing
one placed instance doesn't silently change every other room.

**Persistence:** custom kits are stored in `config.ini` as
`LightKitXX` and `LightKitPartXX_N`. They complement, rather
than replace, the old `LightXX` entries. The existing maximum
of 128 actual placed emitters remains global across saved scenes.

### Ambient versus sky illumination

The **Scene** tab separates the previous ambient multiplier from a
new **Sky Brightness** source. Old colored ambient continues to
work for compatibility, but **Neutral white ambient** removes the
subtractive color-filter behavior. The new sky fill adds a soft
scene-wide illumination shoulder with adjustable RGB color and
strength, plus three projected directions: upper sky, uniform fill,
or lower bounce. **Daylight**, **Moonlight**, and **No Sky**
give quick starting points. Each scene's sky is saved to a
`RoomSkyXX` record, independent from its `RoomAmbientXX`
entry, including a user-selected sky color when strength is zero.

This is a **stylized 2D sky/hemisphere approximation**. It is
not global illumination, real light bouncing, depth-buffer-based
skylight occlusion, or geometry-resolved cast shadows. For those
effects, the native renderer must first expose reliable scene
geometry and occluder masks.

The experimental real ReShade panel has equivalent global-rig
and sky controls. It builds as a separate add-on and still needs
an end-to-end injected Windows UI/placement acceptance test.

## Global Styles, authored shadows, grading and edit history

### Live shared global settings

**Global Styles** is separate from **Global Kits**:

- **Global Kit** is a reusable group of independent lights that you
  place again in another scene. Applying the kit does not link its
  photometry to other instances.
- **Global Style** is a named, reusable *live appearance*. Capture
  the selected light into any of 16 style slots, then **Link Selected**
  or **Link Current Group**. Edit Global Range, Strength, RGB, Shape,
  Angle and related photometric values once; the renderer resolves
  each linked light through its shared style in real time, even if
  it resides in another room. Individual positions, room ownership,
  light names, groups and mute switches remain local. **Unlink**
  restores the light's retained local appearance.
- Links are stored as `LightLinkXX` and styles as
  `GlobalStyleXX` in the existing `config.ini`.
  This also works through the independently built real ReShade add-on.

### Scene masks and soft shadow occlusion

The **Masks** tab lets you **Draw Rectangle on Level** with two clicks
(or start a rectangle near a selected light). In the ReShade panel,
**Draw Mask (2 clicks)** does the same via the established SDL2
window-to-game coordinate transform. An authored rectangle has editable
world X, world Y, width, height, 0–100% shadow opacity and 0–16 pixel
penumbra softness. Mask outlines are visible in edit mode only.

Only positioned emitters behind an authored wall mask are darkened.
Each mask uses deterministic five-ray segment/rectangle shadow tests,
not a guessed tile solidity attribute or a scene-depth texture. Sky
fill and ambient remain unaffected. Masks are room-scoped and saved
to `OccluderXX` records; up to 64 are supported globally.

**Important:** masks are a *manual geometry proxy*, not automatic
Castlevania collision geometry. Exact tile- and sprite-respecting
occlusion requires a separate verified collision/nametable geometry
export, and many live shadow-casting emitters may need GPU or cached
shadow maps for reliable 60 FPS.

### Scene exposure and grading

The **Scene** tab includes an independent post-light grading stage:
Exposure from -2.00 to +2.00 stops, a relative warm/cool white-balance
control (-100 to +100), and saturation from 0–200%. A one-click
**Neutral Grade** reset restores 0 EV, neutral white and 100%
saturation. The real ReShade panel exposes the same properties.
These are simple artistic RGB gains, not a calibrated ACES color
pipeline. Changes affect rows 48–239, never the top NES HUD.
Scene grades persist as `SceneGradeXX`.

### Preset management and undo

The **Library** tab now includes saved-kit **Rename**, **Duplicate to
Empty Slot** and **Delete**. These operations preserve the other
saved kits and can be undone. All lighting authoring edits share a
bounded 16-step host-only history. Native UI uses **Ctrl+Z / Ctrl+Y**
or Undo/Redo buttons. The real ReShade panel exposes Undo/Redo
buttons as well. No emulator quick-save slot or original guest
memory is altered.

### Across a level, including deaths and returns

Placed lights, style links, sky/grade overrides, masks and global
kits live in host `config.ini`, rather than the emulated game's
savestate. Game power/reset or savestate load dismisses the
editor but does not erase these settings.

The original-Japanese room source uses the `$34/$35/$36` selector
triple and the `$07A0` room-resource selector (known bounded
values 0–4). The host currently identifies a room with the **full
four-field selector**. This avoids inadvertently merging distinct
rooms. If returning to an area yields a *different* raw selector,
**Settings → Persistent Scene Identity** shows both the raw and
resolved IDs. Enter the old **Saved Scene ID** to map this new raw
selector back to the already-authored room. Mapping is saved as
`SceneAliasXX`, with up to 32 mappings; old light positions are
not discarded or migrated. Default mapping is identity.

**Actual Windows return-trip QA remains required.** Synthetic
tests prove model persistence, alias resolution and room isolation;
they do not prove every genuine route has stable selectors, nor
full vertical world-coordinate unwrapping above the 480-pixel
PPU domain. Do not merge until Stage 1 and multiple vertical room
transitions and death/reload loops visibly retain all authored lights.

## Animated candles, feathered shadows and GPU GI

### Flame animation in the editor

Each light now has five animation modes: **Candle Flicker**,
**Steady**, **Torch Turbulence**, **Soft Pulse**, and **Ember Dips**.
The native studio and genuine ReShade add-on expose **Flame Speed**
(1–400%) and **Flame Strength** (1–100%). Choosing 0 for either
restores the existing automatic value, preserving legacy settings.
Intensity and a very small amount of source radius breathe together
using continuous deterministic functions instead of per-frame random
flashes; each source has an independent stable phase.

New animation data persists as optional `LightAnimXX`,
`GlobalAnimXX` (shared linked global styles), and
`LightKitMotionXX_N` (captured reusable multi-light kits).
Steady sources remain steady across gameplay frames. Candles, torches
and magic lights can have distinct rhythms.

These frequencies are artistic choices. Experiments on *coupled*
candle flames report approximately 10 Hz oscillations, but that
finding should not be treated as a precise rule for isolated candle
light or torches. The animator exposes pace and amplitude rather
than pretending the RGB modulation is a measured photometric model.

### Soft shadow seam refinement

The old mask occlusion used **five horizontally separated binary
visibility rays**. It could leave narrow vertical and diagonal
terminator steps, particularly noticeable on moving sprite art.
The updated renderer uses a deterministic **3×3, binomial-weighted
area-source visibility filter along both X and Y**, with a larger
available 0–32 pixel mask softness range. New masks start at a
softer 10-pixel setting with moderate opacity; previously authored
mask values are retained for backwards compatibility.

This improves spatial edge smoothness, but not every possible seam:
the present CPU renderer lights the already-composited NES frame,
so a moving sprite crossing a shadow can still reveal how the
shadow boundary affects foreground and background together. The
next compositor upgrade should separate sprite/background layers
and then apply distinct shadow interaction before recombining them.
Nine shadow-visibility rays also increase CPU cost in affected
regions versus five; FPS must be checked on the owner's PC.

### GPU lighting modes and Radiance Cascades

**Settings → Renderer Backend** now offers three choices:
**Standard** (C11 CPU default), **GPU Prototype** (D3D11 direct
visibility with sampled one-bounce light), and **Radiance Cascades**
(D3D11 hierarchical directional radiance merging across two to four
probe levels). For Radiance Cascades, select Low, Medium or High quality
in the same Settings tab. The genuine ReShade add-on exposes the same
controls. Unsupported hardware, GPU failure and excess per-scene
geometry fall back automatically to Standard.

The Radiance Cascades implementation has passed ROM-free Windows
CS5.0 shader compilation and multi-level WARP dispatch tests, but it
is **not gameplay- or performance-verified** on an owner's system.
All GPU modes currently use manually authored wall masks, not the
game's automatically decoded solid-tile collision map. The existing
CPU-staging lightmap transfer is a prototype bottleneck. See
[**GPU Prototype and Radiance Cascades guide**](ENHANCED_LIGHTING_GPU_PROTOTYPE.md)
and [**Production RTGI roadmap**](ENHANCED_LIGHTING_RTGI_ROADMAP.md)
for implementation, limits, room/scroll QA and future multibounce
and GPU-resident compositing work.

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
