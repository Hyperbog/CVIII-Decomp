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
The initial add-on places new lights at the center of the visible
game area, then offers precise X/Y editing. Native mouse placement
remains available via the built-in editor; direct click-to-place in
the true ReShade overlay is not implemented yet. The add-on is
separately built and **has not passed** Windows SDK compilation,
API-function-table compatibility, gameplay input, shader-hook, or
interactive UI tests in the owner's environment. Do not present
this as a released or plug-and-play package.

ReShade can postprocess the SDL renderer's D3D/OpenGL output,
but the native CVIII 2D lighting model continues to own actual
level coordinates and pixel illumination. No depth map, collision
mask, occluder detection or geometry-based cast shadows exist yet.
