# CVIII Enhanced — Lighting Quality and Optional 2D RTGI Roadmap

**Scope:** Japanese Castlevania III's host-side presentation, isolated from
original CPU/PPU/IRQ state, Original edition, owner ROM and machine save states.
This is a technical plan, **not** a claim that a ray-traced backend ships today.

## What works on the current feature branch

- Native CPU 256×240 presenter: room-based radial/cone/shaft emitters, global
  light styles and kits, sky fill, area-source-style occlusion over explicitly
  drawn world-space rectangles, per-scene grading, persistent lighting config.
- Scene pixels in rows 48–239 are shaded after the original NES renderer.
  HUD rows 0–47 are never modified.
- GUI: native Dear ImGui + optional independently built real ReShade add-on.
  Neither GUI is itself a shader-backed GI pass.
- Candle/torch animation: per-light phase, smooth multi-frequency flame
  modulation, Torch/Pulse/Ember modes, adjustable speed/depth and gentle
  radius breathing. Modes are deterministic under host frame time. Global
  styles and saved kits carry the animation settings.
- Overlapping light sources add per-channel contributions and pass through a
  Reinhard-inspired highlight shoulder. Bright areas preserve some palette
  detail; this is **not** yet energy-conserving linear-light transport.

## Near-term acceptance: shadow seams and sprite compositing

The previous occlusion algorithm used five horizontally displaced binary
visibility rays. Shadow transitions could look stair-stepped and terminate
sharply at vertical boundaries; entire finished NES image (including sprite
pixels) was darkened at once.

- Current patch changes the penumbra to **3×3, Gaussian-weighted area-source
  visibility samples on both axes**, with longer softness sliders.
- Game-world occluders have editable strength and softness and remain hidden
  except while authoring. On completed scenes, no debug rectangle should
  overlay sprite art.
- Pixel-accurate test: a walking character crossing a shadow terminator
  should not create a noticeable one-pixel light/dark stripe.
- **Further work:** distinguish background from sprite layers before applying
  the shadow and combine them afterward with separate contact-light rules.
  This may require exposing original host-owned background/sprite buffers
  rather than lighting the already composited 256×240 screenshot.
- Profile CPU time with 1, 8, 32 visible lights, 0–16 masks, moving sprites
  and a stage transition. Avoid silent regressions to game simulation timing.
  Current area-light sampling increases CPU work per affected pixel.

## Global moonlight / daylight environments

Separate the following material controls instead of tinting the whole
scene: (1) neutral ambient energy; (2) additive sky/hemisphere illumination;
(3) moon/sun world direction and color; (4) local window-shaft emitter color
and intensity; and (5) per-scene exposure / white balance.

The current built-in Moonlight sky setting plus linked global Window/Moonlight
light styles already support manual authoring. The **next model extension**
should add globally named Environment Profiles (Moonlight, Overcast,
Sunrise, Dungeon Night) and a scene link. All rooms linked to that environment
would inherit sky RGB, skylight strength and global shaft photometry,
while preserving local mask geometry, window positions and optional
per-room overrides. Do not silently share world positions across rooms.

**Off-screen light:** the sky/hemisphere term is camera-independent and
covers the full gameplay viewport; individual moon shafts attach to world
coordinates and clip naturally when scrolled away.

## Selectable renderer modes

- **Original:** no Enhanced presentation changes (existing parity).
- **Enhanced / Standard:** current artist-directed CPU renderer with smooth
  flame animation, low-cost soft shadows, additive sky fill and grading.
- **Enhanced / GPU Prototype (implemented, Windows experimental):** an
  independent D3D11 CS5.0 compute pass traces direct visibility against
  authored world-rectangle masks, accumulates a sampled diffuse wall-face
  bounce, interpolates an HDR 128×96 lightmap over the NES's full 256×240
  source frame, and automatically falls back to Standard. It compiles only
  in private Windows GUI builds. This is NOT automatic collision geometry
  or the future Radiance Cascades transport solver.
- **Enhanced / Radiance Cascades (future opt-in):** a higher-quality GPU
  renderer with hierarchical directional radiance probes, verified room
  geometry, proper GPU-resident compositing and a Standard fallback.
  This mode is not offered in the UI until genuinely implemented.

### RTGI prototype: technically viable in 2D, not free

1. **Scene geometry export.** Build a room-scoped occluder/emissive mask from
   verified room/nametable/world tile and stage metadata. Do not assume
   nonzero backdrop pixels are solid walls. Merge the author's mask edits.
2. **GPU light input.** Upload emissive RGB, named light attributes,
   camera offsets and static/dynamic occluders as dedicated textures.
   Separate sprite and foreground lighting from background transport.
3. **Visibility / signed distance field.** Use jump flooding (JFA) or
   an offline/baked static distance field plus a small dynamic update
   for moving objects.
4. **Direct and indirect illumination.** Prototype a low-resolution
   ray-march for direct visibility and a *single indirect bounce* first.
   Compare against small offline CPU reference images.
5. **Higher-quality mode.** Investigate Radiance Cascades 2D, which
   accumulates directional radiance in hierarchical probes, rather than
   firing independent rays from every 256×192 pixel per light every
   frame. This is a sensible route to real-time multi-source GI.
6. **Temporal stability:** stable seeded sampling or deterministic
   cascades, optional denoising, lighting history reset when room identity
   or scrolling viewport changes, and no light smearing after death/load.
7. **Composite:** grade in a consistent light/color space (prefer linear
   RGB during accumulation), then use a bounded tone-mapping shoulder
   and restore the 8-bit NES output at final display size.
8. **Backend:** SDL2's current `SDL_Renderer` acceleration does **not**
   expose custom shader execution as a cross-platform contract. Provide
   an explicit render-backend interface (likely D3D11 on Windows plus
   an OpenGL or Vulkan backend if desired). ReShade's installed overlay
   is not the game's compute renderer, though its API may be useful
   for postprocessing. Retain a CPU/SDL Standard fallback.

Prototype at half-native light resolution (128×96 for 256×192 gameplay)
before attempting full-native RTGI. Measure the complete present-frame
budget, not just shader time. 60 fps allows 16.67 ms for **everything**,
including emulation, audio and UI, so lighting must stay well under
that on tested machines. Use low/medium/high presets and hard caps.

### Sources guiding design

- *Holographic Radiance Cascades for 2D Global Illumination*
  (Freeman, Sannikov & Margel, 2025):
  https://arxiv.org/abs/2505.02041
- A reference 2D Radiance Cascades / distance-field implementation:
  https://github.com/Hybrid46/RadianceCascade2DGlobalIllumination
- Sannikov / Xor tutorial on the multi-scale radiance cascade concept:
  https://mini.gmshaders.com/p/radiance-cascades
- *Synchronization in flickering of three-coupled candle flames*
  (2016): https://pmc.ncbi.nlm.nih.gov/articles/PMC5080605/
  Experimentally observed ~10 Hz is a *coupled flame* result, not a
  universal frequency for isolated candles. Game flame rhythm remains
  deliberately tunable rather than misrepresented as measured photometry.
- NVIDIA GPU Gems on percentage-closer filtering of shadow visibility:
  https://developer.nvidia.com/gpugems/gpugems3/part-ii-light-and-shadows/chapter-8-summed-area-variance-shadow-maps

## GPU Prototype implementation status (October 2026)

The first D3D11 compute-lighting prototype is now in
[`cviii_gpu_rtgi_d3d11.cpp`](../native/enhanced/cviii_gpu_rtgi_d3d11.cpp),
with the actual CS5.0 kernel shared by the ROM-free Windows
[`shader compile fixture`](../native/enhanced/cviii_gpu_rtgi_shader_test.cpp)
and
[`WARP execution fixture`](../native/enhanced/cviii_gpu_rtgi_warp_test.cpp).

Choose **Standard** or **GPU Prototype** in Lighting Studio / Settings
or the genuine ReShade add-on UI. Config persists `LightingRenderer =
Standard` or `LightingRenderer = GPUPrototype`. GPU init failure or
prototype light/occluder capacity exhaustion transparently falls back
on that frame without affecting Original mode, game hardware state or
the user's config. The editor previews Standard while open to preserve
the placement/occluder authoring handles.

The GPU pass currently uses **explicit author-created masks**, not
automatically reconstructed solid tiles. Its indirect light is a
single per-face virtual-emitter bounce, informed by sampled visible
NES RGB or a neutral unknown-wall albedo. It is intentionally not
presented as converged path-traced lighting or Radiance Cascades.
The dedicated D3D11 device uses a GPU-to-CPU staging readback and
bilinear lightmap compositing; replacing that stall with a shared
display texture remains the first performance upgrade.

See [**GPU Prototype setup and acceptance**](ENHANCED_LIGHTING_GPU_PROTOTYPE.md)
for exact bounds, quality expectations, compatibility and fallback.

## Owner testing checklist for the next Windows session

1. Candle vs Torch vs Pulse vs Ember with moving, pause, reload and scroll.
2. Shadow mask near a wall where Trevor crosses the boundary: center, top,
   bottom, and across scene scrolling; inspect aliasing and FPS.
3. Multiple Torch and Window emitters overlapping, with high/low exposure,
   warm/cool white balance, and flicker occurring out of phase.
4. Moonlight sky plus linked window shafts; verify camera scroll does not
   change offscreen sky, while world-mounted shafts leave/re-enter view.
5. Exit and return to each room, die, restore a save state and restart.
   Check that room-scoped profiles, aliases and global style links persist.
6. Compare against Original edition for gameplay timing and renderer parity.
