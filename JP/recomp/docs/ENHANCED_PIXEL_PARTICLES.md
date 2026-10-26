# Enhanced Pixel FX — World-Scoped Native-Resolution Atmosphere

Experimental C11 host-presentation effects (no ROM, machine or save-state changes).

## Presets and look

| Preset | Pixel-art appearance |
| --- | --- |
| Floating Dust | Slow drifting specks in corridors |
| Rising Embers | Orange upward-moving 1–2px particles by fires |
| Pixel Fog | Stippled low-opacity native-pixel cloudlets without HD blur |
| Falling Ash | Muted drifting gray flecks |
| Snow | Gentle bright falling pixels |
| Rain | Fast downward pixel streaks |
| Fireflies | Flickering colored pixel specks |

## Editor

Native Lighting Studio > Particles, or genuine ReShade CVIII Lighting > Pixel FX. Choose an effect and Create at View Center or Place on Level; the latter uses the established SDL2 mouse-to-game mapping. Each persistent region has an editable name, preset, X/Y world coordinates, width/height, density (1–96), speed (0–300%), wind (-100..100), opacity (0–100%), native pixel size (1–4) and RGB color. Duplicate and Delete are available. Region boundaries show cyan 1-pixel outlines only in edit mode. Editor operations participate in the host-only undo/redo history.

## Persistence and rendering

Up to 32 regions are scoped to the existing resolved JP room ID; particles are placed using the same per-scanline PPU scroll mapping as world lights. Their positions are deterministic functions of the authoring profile and render-frame counter, without random-number state or game RAM writes. Offscreen particles disappear and reappear as the camera returns. All settings persist in the owner's config.ini as Particles, ParticleXX and ParticleNameXX entries; older configs remain valid with no effects.

Particle drawing occurs at the existing 256x240 NES resolution, after Standard/GPU Prototype/Radiance Cascades lighting but before host pause UI. All RGB blending is quantized to 16 increments and pixel fog is sparse dither rather than a blurry filtered effect. HUD rows 0–47 are protected. Particles remain independently active when lighting is disabled. The maximum is 32 x 96 = 3072 sample particles per frame.

## Scope and owner QA

The first version does not extract true geometry/collision from tiles, occlude against moving Trevor sprites, emit actual lighting into GPU radiance probes, or simulate volumetric atmospheric scattering. Pixel FX are placed above the already composited background and sprite frame. Those limitations and CPU performance with many overlapping fog regions need Windows gameplay screenshots/tests.

Owner checklist: place embers at a torch, dust in a hall, fog in a window; adjust speed/wind/opacity; scroll away/back, die/load/revisit, restart, test all three lighting modes, check HUD and 60 FPS. Draft PR #14 remains unmerged pending acceptance.