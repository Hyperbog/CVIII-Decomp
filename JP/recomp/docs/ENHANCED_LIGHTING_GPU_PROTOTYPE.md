# CVIII Enhanced: Experimental D3D11 GPU Lighting Mode

This branch contains a **first GPU lighting prototype**, not the final
Radiance Cascades implementation. The existing C11 **Standard** renderer
remains the default and remains usable on Windows without a suitable GPU,
on Linux, and in ROM-free/headless tests.

## Third mode: Radiance Cascades (experimental)

The new third mode runs a **true hierarchical directional-probe pass**:
each cascade holds 6,144 rays, but trades spatial density for angular
resolution as distance grows.

| Level | Probe grid | Directions per probe | Ray distance interval (NES pixels) |
| --- | --- | --- | --- |
| 0 | 32 × 24 | 8 | 0–8 |
| 1 | 16 × 12 | 32 | 8–40 |
| 2 | 8 × 6 | 128 | 40–168 |
| 3 | 4 × 3 | 512 | 168–680 |

These distances use the 256×192 gameplay world coordinate units.
Each interval traces against **the actual manually authored wall
rectangles**, preserving the existing persistent room IDs. At a hit,
the wall contributes its prelit face RGB while its opacity blocks
radiance arriving from higher cascades. Empty ray segments transmit
distant radiance. The GPU merges **far to near**, interpolating four
neighboring coarse probe locations and four finer angular children
per direction. Probe-zero radiance is integrated over eight
directions and blended into the **existing direct HDR lightmap**.
Rendering the finished 256×240 8-bit NES image still uses the
same native-resolution palette-preserving composite.

The editor's **Radiance Quality** setting chooses:
**Low** (2 cascades), **Medium** (3, the default), or
**High** (4). Both the quality and renderer selection are written to
owner-local `config.ini` as `LightingCascadeQuality` and
`LightingRenderer = RadianceCascades`.

It is an intentionally bounded first Radiance Cascades implementation,
**not** a full Path of Exile 2-style production GI solution. The wall
radiance is initialized from the previous GPU prototype's sample
of authored wall faces; this supports directional visibility-aware
indirect light but is not an iterated multi-bounce transport solver.
No sprite occlusion geometry, automatic tile collision export,
GPU-resident final display, linear color-managed lighting or
real-time 60-FPS acceptance is claimed. Scenes with no authored
occluders retain direct and sky light without mask-generated bounce.

**Compatibility:** Standard is the default. The third mode uses the
same Win64 hardware D3D11 and room-budget gate as GPU Prototype.
If either Radiance Cascades compute-shader initialization or dispatch
cannot proceed, the entire frame is rendered with Standard,
not a partially computed GPU image. Other platforms remain Standard.

ROM-free Windows CI gates include compilation of both new CS5.0
shader entry points, and an actual Direct3D WARP dispatch for each
quality tier (2/3/4). This verifies math execution and nonzero
indirect RGB on a synthetic wall scene; it does *not* substitute for
owner gameplay, visuals, camera, or performance checks.

References: [original Radiance Cascades research](https://github.com/Raikiri/RadianceCascadesPaper)
and [accessible cascade-merging explanation](https://mini.gmshaders.com/p/radiance-cascades).

## Selecting a renderer

Open **Enhanced → Lighting Studio → Settings → Renderer Backend** or the
genuine optional ReShade add-on's **GPU Lighting Prototype** section:

| Selection | Effect | Availability |
| --- | --- | --- |
| **Standard (CPU)** | Existing radial/cone/shaft lights, sky fill, masks, grading and editor handles | All existing supported systems |
| **GPU Prototype (D3D11, 1 bounce)** | GPU-traced direct visibility, authored wall occlusion and an approximate secondary diffuse bounce | Windows desktop, D3D11 feature level 11.0 hardware |
| **Radiance Cascades (D3D11, experimental)** | Directional hierarchical probe GI, far-to-near interval merging, Low/Medium/High quality | Windows desktop, D3D11 feature level 11.0 hardware |

The renderer choice is stored as `LightingRenderer = Standard`,
`LightingRenderer = GPUPrototype`, or
`LightingRenderer = RadianceCascades` in the owner's local `config.ini`.
`LightingCascadeQuality` is an integer from 2–4 (default 3).
**Original** mode never runs the GPU path.

No changes are made to guest NES CPU, mapper, PPU, audio or save-state
serialization. The result is applied only to an already copied, owner-side
RGBA presentation frame. While the lighting editor is open, Standard is
shown to preserve its scene handles and mask outlines. Close the editor
to preview GPU mode.

The GUI reports the GPU backend status. If the GPU is unsupported,
shader compilation/device creation fails, a frame has more than
**12 visible active emitters or 12 scene occluders**, or lightmap transfer
fails, that frame automatically uses the existing Standard renderer.
The saved choice is not silently rewritten.

## What the first GPU prototype actually traces

**Windows D3D11 CS5.0 compute shader** on a dedicated independent
device; it does not take over the SDL2 window/renderer.

- A **128×96** HDR floating-point lighting field is computed for the
  256×192-pixel gameplay area. The HUD above row 48 is not touched.
- Per-scanline host PPU scroll positions are used to track lights and
  masks in world coordinates; lights remain persistent in config.ini.
- Direct point/cone/shaft illumination traces 2D ray/rectangle
  visibility against **real numeric geometry for the manually
  authored shadow-mask rectangles**.
- A bounded **single indirect bounce** uses visible, author-defined
  wall faces as virtual emitters. Each face's original onscreen palette
  color estimates its diffuse albedo; for an offscreen surface the
  reference uses neutral albedo. A small reflected-light term is
  emitted toward visible points with a distance falloff and ray
  visibility checks. This is a **face-sampled approximation**, not a
  converged path tracer or physically calibrated BRDF.
- The GPU map is read back and bilinearly applied to a **full-native
  resolution NES image**, retaining palette pixel edges instead of
  upscaling a 128×96 screenshot.
- Existing scene ambient, sky fill and exposure/white-balance/saturation
  settings carry over. Global style links and flame animation are
  resolved before the GPU pass.

Because the existing SDL2 renderer does not expose portable compute
shaders and the original private Windows host should not be rewritten
in this phase, the compute device is standalone. **GPU→CPU readback
is a prototype limitation**, not the planned finished high-performance
renderer. Future direct GPU presentation should eliminate this stall
by sharing a display texture/graphics context once that API path is
validated against the pinned SDL2 backend.

### Geometry caveat

This prototype traces the **existing manually placed occluder geometry**.
It does **not** infer hard walls from arbitrary nonzero background pixels,
know which nametable tiles are actually solid, reconstruct depth from
Castlevania's flat art, or dynamically identify player/sprite occluders.
Those require evidence-based original-game scene collision/nametable
exports and proper foreground/background separation.

For a meaningful bounce-light test, place one or more wall masks near
a Torch or Window light and choose GPU Prototype *outside edit mode*.
Rooms with no authored occluders have no wall bounce; direct light
still operates. An over-budget room transparently falls back to Standard.

Radiance Cascades also **disables the former single-face bounce in
the direct shader**, so the legacy approximation is not double counted.
The directional probe pass supplies the indirect contribution instead.

## Build and validation

On Windows, the CMake `JP_CYCLE_HEADLESS=OFF` Enhanced target compiles
`cviii_gpu_rtgi_d3d11.cpp` and links the system `d3d11` and
`d3dcompiler` libraries. No external game ROM or GPU binary is
committed.

Windows builds have a separate **ROM-free D3DCompiler cs_5_0 smoke
executable**, using the *same* embedded HLSL as the actual game.
The game target depends on that executable's successful compile and
execution. The independent test checks HLSL syntax / shader compilation
but does not prove hardware-device creation, ray visual correctness, or
60-FPS gameplay in the owner's environment.

Linux and headless never build the D3D11 module. The mode is still
stored in the owner's config, and any missing backend must run Standard
without attempting graphics initialization.

## Acceptance matrix (Windows owner testing still required)

1. Start in Standard: check Original parity, HUD, scroll, light placement.
2. Select GPU Prototype; close lighting editor; check the reported
   backend becomes active and light output differs appropriately.
3. Use a single Wall Mask in front of Torch, then several masks.
   Look for physically wrong bleeding, sprite seam, overbright
   reflections and camera/world offset mistakes.
4. Move offscreen, return, die, load, change stage; ensure no stale
   lightmap, wrong room or lost persistent profiles.
5. Repeat with 0, 1, 4, 12, and 13 scene lights/masks to verify
   *fallback beyond the prototype cap* with no partial render.
6. Test an unsupported GPU / forced software SDL2 renderer;
   the desired behavior is Standard fallback, not a crash.
7. Profile GPU dispatch and CPU map/readback stalls against Standard,
   targeting a total frame time below 16.67 ms for 60 FPS.
8. Test genuine ReShade overlay editor ownership independently; ReShade
   is NOT the application's compute device or graphics driver.

## Next milestone: production-grade Radiance Cascades

The experimental third renderer now performs a **real three-stage
hierarchical-probe pipeline** (ray intervals, far-to-near merging and
GPU integration) with two to four levels. It is still an early
prototype and is not a finished physically convergent GI renderer.
The next production-quality phase should improve these areas:

- Evidence-verified collision/occlusion and emissive geometry from
  the original JP room/nametable and scrolling system.
- GPU-resident scene buffers and direct GPU image compositing (remove
  the current per-frame readback).
- Correct linear-light accumulation and a calibrated tonal operator.
- Separate static tile-geometry, animated sprites and foreground masks.
- A GPU reference/visual test comparing Standard, current one-bounce
  prototype, and Radiance Cascades, including moving characters.
- Hard performance caps, Standard fallback, no guest machine writes.

The experimental Radiance Cascades entry is available in the
mode dropdown and passes CS5.0 compilation and WARP execution.
Live Windows gameplay QA and measured GPU frame timing remain gates
before presenting it as production-ready.
See [lighting RTGI roadmap](ENHANCED_LIGHTING_RTGI_ROADMAP.md).
