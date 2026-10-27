# NEStudio — native Windows Enhanced NES development environment

**Status: first integrated Windows application under development; live gameplay QA pending.** This is not an image mockup. It is a WPF desktop executable that starts the existing private C11/SDL2 Japanese recomp and hosts the actual game HWND in a resizable NEStudio viewport. The original game executable, SDL2, NES CPU/PPU and audio remain unchanged.

## Build and run (owner Windows PC)

The recommended one-click private route is:

```bat
JP\recomp\nestudio\Preview-NEStudio.bat
```

The script checks the authentic owner-supplied JP ROM, checks out **feature/nestudio-foundation** in the isolated `%USERPROFILE%\NEStudio-Preview\_cviisource` folder, builds the owner-private Enhanced executable through the existing Alpha process, and builds NEStudio with the .NET 8 SDK. It leaves `CVIII-Alpha` and `CVIII-Lighting-Preview` unchanged. On completion, the editor is at:

```text
%USERPROFILE%\NEStudio-Preview\NEStudio\NEStudio.exe
```

Its initial `EnhancedProject.nestudio` points to the privately compiled game in `NEStudio-Preview\AlphaCandidate`, without embedding ROM assets in the project.

You can also build the editor independently without a ROM or running game:

```powershell
./JP/recomp/nestudio/Build-NEStudio.ps1 -Launch
```

Pass `-GameFolder "C:\path\to\AlphaCandidate"` to generate a starter project referencing a compatible freshly built native Enhanced game. **An old game build without the new NEStudio session bridge will embed the viewport but cannot provide live scene edits**; the recommended private builder rebuilds both halves.

Prerequisites: Windows x64, .NET **8 SDK** to build, and a private original-Japanese-ROM-authenticated native Enhanced build with SDL2.dll. The WPF published build targets the .NET 8 desktop runtime (not included in the editor-only GitHub artifact). No proprietary assets ship in the repository or CI artifact.

## Integrated workstation

- **Real native viewport:** Starts `jp_akumajou_densetsu.exe --edition Enhanced` with a private session environment variable and embeds its actual SDL2 Win32 child window. The viewport maintains the game's 256×240 presentation aspect ratio. NES frame timing, mouse mapping, gamepad, mapper and audio remain owned by the native process; no screenshot mirroring.
- **Live scene tree:** Reads the current resolved JP room and up to 128 persistent room lights from a bounded, versioned local shared memory bridge. Select a placed light in the tree to edit it.
- **Lighting inspector:** Place Candle/Torch in view center, select, duplicate, delete, change radius, power, RGB, flame animation, Standard/GPU Prototype/Radiance Cascades renderers, and undo/redo. The game SDL thread owns mutations and existing `config.ini` persistence. **Edit/Pause** opens the game's existing modal paused editor; **Play** resumes.
- **Sprite Studio authoring foundation:** Editable named sprite groups and display-layer organization in NEStudio project files. These are data-only project annotations for the next enhanced sprite/asset importer, **not yet live OAM replacement**.
- **Dialogue & translations foundation:** Per-event stable ID, Japanese/English/French/Spanish/German source, explicit manual line breaks, `[page]` page delimiters, configurable automatic line width, deterministic local layout preview. Stored in the project file, **not yet hooked into original game dialogue triggers**.
- **Timeline & asset browser foundation:** Authored event records and referenced user-local assets, with no ROM byte inclusion, and a persistent project tree.
- **Project save/open:** Versioned `.nestudio` JSON schema with atomic replacement, bounded validation, and a separate game executable path. Current lights remain in the live game's `config.ini`; NEStudio does not fork a second copy of lighting state.
- **Resizable layout:** Scene tree, actual viewport, timeline/console and inspector with adjustable pane splits. WPF desktop fonts and controls are intentionally independent from the NES bitmap.

## Integration architecture

```text
NEStudio.exe (.NET 8/WPF editor)
    ├── WinFormsHost parent HWND ── real SDL2 native game child window
    ├── NEStudio v1 project (sprite groups, localizations, timeline, assets)
    └── Local\NEStudio-<session> memory map (bounded v1 commands/snapshots)
            └── owner-private SDL show() tick
                  └── existing cviii_lighting_editor_* host APIs
                         └── existing C11/SDL2 NESRecomp Enhanced runtime
```

The fixed-layout bridge has compile-time C size assertions and is never created when the game is launched normally without `CVIII_NESTUDIO_SESSION`. The session token prevents accidentally talking to a different game window. The bridge exposes **presentation/light authoring only**, not game memory, mapper/PPU state or save-state serialization.

## Important limitations and next production steps

- WPF application and ROM-free schema tests can run in GitHub Actions, but **actual native game embedding, focus, SDL2/D3D11 behavior and owner Windows gameplay** still require user acceptance.
- The first editor does **not** make sprite group order affect NES OAM, import custom sprites into the live engine, patch original dialogue triggers, change textbox runtime geometry, or rebuild stages. These need one shared versioned resource compiler and source-authenticated runtime adapters, rather than writing speculative guest RAM.
- There is no draggable viewport-object gizmo or arbitrary frame-step API yet; pause and lighting operations work through existing host exports. Debug mode cannot be equated with full game-engine simulation controls.
- Original/Enhanced parity and user data safety remain authoritative. Do not commit ROMs, locally built EXEs containing retail content, ripped CHR archives, or private saves.

## Acceptance milestones

1. **Current:** Build and open the Windows application, load a privately built game into the viewport, pause, select a torch, change its RGB/radius, save, restart and verify persistence.
2. Add read-only live sprite/OAM identities and background/foreground separation to the same scene inspector, then a data-only sprite asset replacement compiler with runtime consumption and override validation.
3. Add authentic dialogue trigger IDs, multilingual text resource loading, variable-size boxes, typewriter/page events, layout/glyph checks and deterministic gameplay-event execution.
4. Replace cross-process SDL HWND parenting with an explicit render-surface sharing API only if live owner QA exposes unacceptable focus/render/compositor behavior.
5. Implement a single transactional asset/project build and runtime hot-reload boundary; expand the timeline to actual scene triggers without altering original gameplay by default.
