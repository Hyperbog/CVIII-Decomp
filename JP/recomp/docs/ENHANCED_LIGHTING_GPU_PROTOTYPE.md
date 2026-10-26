# CVIII Enhanced: Experimental D3D11 GPU Lighting Mode

This branch contains a **first GPU lighting prototype**, not the final
Radiance Cascades implementation. The existing C11 **Standard** renderer
remains the default and remains usable on Windows without a suitable GPU,
on Linux, and in ROM-free/headless tests.

## Selecting a renderer

Open **Enhanced → Lighting Studio → Settings → Renderer Backend** or the
genuine optional ReShade add-on's **GPU Lighting Prototype** section:

| Selection | Effect | Availability |
| --- | --- | --- |
| **Standard (CPU)** | Existing radial/cone/shaft lights, sky fill, masks, grading and editor handles | All existing supported systems |
| **GPU Prototype (D3D11, 1 bounce)** | GPU-traced direct visibility, authored wall occlusion and an approximate secondary diffuse bounce | Windows desktop, D3D11 feature level 11.0 hardware |

The choice is stored as `LightingRenderer = Standard` or
`LightingRenderer = GPUPrototype` in the owner's local `config.ini`.
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

## Next milestone: Radiance Cascades (not implemented here)

A higher-quality **2D Radiance Cascades** backend should replace the
single face-sampled bounce with multi-scale directional radiance probes,
with quality choices for cascade count, base probe spacing, angular
resolution and denoising. Prerequisites:

- Evidence-verified collision/occlusion and emissive geometry from
  the original JP room/nametable and scrolling system.
- GPU-resident scene buffers and direct GPU image compositing (remove
  the current per-frame readback).
- Correct linear-light accumulation and a calibrated tonal operator.
- Separate static tile-geometry, animated sprites and foreground masks.
- A GPU reference/visual test comparing Standard, current one-bounce
  prototype, and Radiance Cascades, including moving characters.
- Hard performance caps, Standard fallback, no guest machine writes.

A future Radiance Cascades mode is not added to the mode dropdown
until it exists and has passed both shader tests and live gameplay QA.
See [lighting RTGI roadmap](ENHANCED_LIGHTING_RTGI_ROADMAP.md).
