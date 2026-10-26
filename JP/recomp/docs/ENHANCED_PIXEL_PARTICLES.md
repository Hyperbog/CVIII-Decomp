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

## Shared Randomized Weather

Choose a Global Weather Slot 0–7 and create a Rain Showers, Thunderstorm, Winter Snow, Drifting Mist, Volcanic Ash, or Night Fireflies template. Apply it to the current room. The same named profile can be linked to many rooms; changing the profile updates all linked scenes without copying local particles. Unlinking one room does not erase its global profile.

Global controls: particle type, color, count, speed, wind, opacity, native pixel size, chance of active weather (0–100%), period between weather fronts (1–120 seconds), seed (0–65535) and foreground/background depth. The host uses seeded adjacent weather-front strengths and smooth interpolation rather than independent random numbers every frame. A fixed room/profile/frame reproduces the same effect; a different time can produce clear spells, showers, gusts or stronger snow.

Weather is generated in fixed 128-world-pixel horizontal chunks and two 240-pixel vertical pages, so movement follows world geometry during scrolling rather than appearing attached to the window. Up to eight nearby cells are considered per frame. The weather RNG is entirely outside the NES CPU/PPU state.

## Attachments, Layers and GPU Sparks

Select a particle region and **Attach to Light** to pick a named torch/candle in the scene. The region stores a signed offset from its parent light, follows the light's changing world X/Y, and disappears when the parent is muted. Unlinking to World Coordinates leaves the region at its last world location. The link and offset persist in optional ParticleAttachXX config records.

Each region and weather profile can be **Foreground** or **Behind Sprites**. The background layer is drawn before scene lighting and uses a read-only NES background reconstruction to protect pixels belonging to visible sprites. Where this reconstruction is unavailable, the renderer falls back to foreground effects, not an invented depth map. This is a pixel-difference approximation rather than a complete PPU sprite-depth export.

Embers and Fireflies expose **GPU Particle Glow** (0–100%). Up to four visible spark positions may enter the actual D3D11 direct-light array for ray/rectangle visibility and Radiance Cascades wall illumination, within the existing 12-light scene budget. Standard CPU lighting still displays the particle sprites without this extra GPU glow. Fog, dust, snow and rain are not automatically luminous.

Configuration adds WeatherXX, WeatherNameXX, WeatherRoomXX and ParticleAttachXX. Older profiles lacking these records load normally; the new behavior is opt-in.

## Persistence and rendering

Up to 32 regions are scoped to the existing resolved JP room ID; particles are placed using the same per-scanline PPU scroll mapping as world lights. Their positions are deterministic functions of the authoring profile and render-frame counter, without random-number state or game RAM writes. Offscreen particles disappear and reappear as the camera returns. All settings persist in the owner's config.ini as Particles, ParticleXX and ParticleNameXX entries; older configs remain valid with no effects.

Particle drawing occurs at the existing 256x240 NES resolution, after Standard/GPU Prototype/Radiance Cascades lighting but before host pause UI. All RGB blending is quantized to 16 increments and pixel fog is sparse dither rather than a blurry filtered effect. HUD rows 0–47 are protected. Particles remain independently active when lighting is disabled. The maximum is 32 x 96 = 3072 sample particles per frame.

## Scope and owner QA

The current version does not extract collision geometry from tiles or simulate physical volumetric scattering. Sprite occlusion uses a visual background-difference mask; optional GPU sparks are deliberately capped, rather than full physical emissive-particle transport. Pixel FX are placed above the already composited background and sprite frame. Those limitations and CPU performance with many overlapping fog regions need Windows gameplay screenshots/tests.

Owner checklist: place embers at a torch, dust in a hall, fog in a window; adjust speed/wind/opacity; scroll away/back, die/load/revisit, restart, test all three lighting modes, check HUD and 60 FPS. Draft PR #14 remains unmerged pending acceptance.