# Actual ReShade Lighting Overlay (experimental integration)

This is an optional **real ReShade add-on** using ReShade's
`reshade::register_overlay("CVIII Lighting", ...)` interface.
Its controls appear inside ReShade's own existing overlay, not in a
second themed Dear ImGui window. The built-in CVIII Dear ImGui editor
continues to work without ReShade. This integration is **not** bundled
with the public Alpha kit or certified by a Windows gameplay test.

## Requirements

- Private CVIII Enhanced Windows x64 game build from the
  `feature/enhanced-lighting-foundation` branch.
- Official ReShade **with full add-on support**, installed specifically
  for your private CVIII executable's detected D3D/OpenGL backend.
- Matching ReShade SDK source checkout with submodules initialized
  (including `deps/imgui`). See
  https://github.com/crosire/reshade and
  https://crosire.github.io/reshade-docs/ .
- Visual Studio C++ tools, CMake, and the normal private Japanese ROM
  build process. No ReShade or game ROM binaries are committed here.

## Build this *separate* add-on

Example PowerShell, adapting the directories to your own checkout:

```powershell
git clone --recurse-submodules https://github.com/crosire/reshade.git C:\src\reshade
cmake -S JP/recomp/reshade -B C:\temp\cviii-reshade-build -A x64 -DCVIII_RESHADE_SDK_ROOT=C:\src\reshade
cmake --build C:\temp\cviii-reshade-build --config Release
```

Build with an SDK version that matches the installed ReShade API and
Dear ImGui function table, rather than assuming that the current
ReShade GitHub branch is always binary compatible. Output is a
`CVIII_Lighting.addon64` file. Place that file in the add-on search
directory configured in ReShade, typically near its loaded DLL.
Enable third-party add-ons only in your own trusted single-player
environment. The ReShade add-on is **not** a graphics-driver rewrite.

## Usage

1. In the game's `config.ini` set
   `LightingEditorKey = End`, keeping **Home** available for
   ReShade itself. (The native editor remains available via End.)
2. Install and open the **actual ReShade overlay** with Home.
   Select **CVIII Lighting** in ReShade's add-on/effect interface.
3. Rename/group lights, copy/paste them, duplicate, edit precise
   world X/Y positions, choose radial/cone/shaft shapes, color,
   range, brightness, mute, flicker and scene ambient settings.
   The add-on writes via the game's exported editor C API and calls
   the game's existing `config.ini` serializer.
4. When the ReShade panel is no longer drawn, a short presentation
   watchdog closes the external editing session and resumes the NES
   simulation. ReShade itself owns mouse input while its overlay
   is open; the native lighting studio does not render simultaneously.

**Limitations pending actual end-to-end validation:**
The add-on provides **Add Light: Click Level** for placing lights
in the visible game area. It passes ReShade's window-space pointer
through the native SDL2 video geometry converter; **Add at Center**
and exact world X/Y editing remain available if capture/scale
compatibility is uncertain. This ReShade mouse path has not yet
received an owner's interactive DPI/resize acceptance test. The add-on **compiled successfully** against the official
pinned ReShade v6.8.0 SDK in the independent Windows CI
[run 40267293019](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/40267293019),
which produced a ROM-free artifact named
`CVIII-ReShade-Lighting-Addon-Experimental`. That proves C++
compile/link only, **not** dynamic API registration, injected graphics
backend compatibility, actual Windows game mouse alignment, stage
transitions or visual acceptance. Keep it experimental until those
in-game checks pass.

ReShade can postprocess the SDL renderer's D3D/OpenGL output,
but the native CVIII 2D lighting model continues to own actual
level coordinates and pixel illumination. No depth map, collision
mask, occluder detection or geometry-based cast shadows exist yet.
