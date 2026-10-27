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

Its initial `EnhancedProject.nestudio` points to the privately generated
`NEStudio-Preview\AlphaCandidate\Launch-NEStudio-Game.bat`.
The wrapper supplies the required Japanese ROM path, inherits NEStudio's
session token and starts the freshly built bridge-enabled native game.
The private `NEStudio-RomPath.txt` contains only the local ROM pathname,
not ROM data.

You can also build the editor independently without a ROM or running game:

```powershell
./JP/recomp/nestudio/Build-NEStudio.ps1 -Launch
```

Pass `-GameFolder "C:\path\to\AlphaCandidate"` to generate a starter
project referencing a compatible private native game plus its dedicated
`Launch-NEStudio-Game.bat`. **An old game build without the new NEStudio session bridge will embed the viewport but cannot provide live scene edits**; the recommended private builder rebuilds both halves.

Prerequisites: Windows x64, .NET **8 SDK** to build, and a private original-Japanese-ROM-authenticated native Enhanced build with SDL2.dll. The WPF published build targets the .NET 8 desktop runtime (not included in the editor-only GitHub artifact). No proprietary assets ship in the repository or CI artifact.

## Fixing a separate game window and "Bridge connecting"

The generic Alpha `Play-CVIII.bat` and `Build-And-Play.bat` launchers can
reuse an old `%USERPROFILE%\CVIII-Alpha\AlphaCandidate` executable
which has no NEStudio session bridge. This produces a separate game window
and leaves the editor at **Bridge connecting**. Selecting the bare native
EXE can also omit the mandatory positional Japanese ROM argument.

Use the private preview build and choose
`%USERPROFILE%\NEStudio-Preview\AlphaCandidate\Launch-NEStudio-Game.bat`
in **Set Game / Launcher**. The preview builder verifies that its fresh
native EXE contains the session bridge symbol before linking the project.
Do not use old alpha builds for live editor acceptance.

## Using an existing game .bat or .cmd launcher

NEStudio now accepts both an actual native `jp_akumajou_densetsu.exe`
and a Windows **.bat/.cmd game launcher**.

1. Open a project. Choose **Set Game .exe** (the file selector supports
   .exe/.bat/.cmd), point it at the existing launcher, then save the project.
2. Select **Run / Attach**. NEStudio starts that launcher under `cmd.exe`
   with an inherited private `CVIII_NESTUDIO_SESSION`.
3. When the actual Enhanced recomp process starts, its C11 bridge publishes
   **its native Windows process ID**. NEStudio embeds that process's SDL2
   window in the viewport, rather than trying to embed `cmd.exe`.
4. **Stop** terminates only NEStudio's own game/session.

A launcher script is **not** itself a game binary. If it only builds the
program and exits, then the native game still needs to compile and launch
successfully; this is not a workaround for errors in the private NESRecomp
build. An unmodified emulator or an older recomp lacking the unique
NEStudio native bridge will not publish the session/PID handshake and
therefore cannot supply live editor controls.

This update is available in new NEStudio Windows CI builds. A previously
downloaded `NEStudio.exe` from an older bundle must be **replaced with the
new editor binary**; changing only the starter project's JSON path cannot
retrofit BAT support into the original executable.

## Integrated workstation

- **Real native viewport:** Starts `jp_akumajou_densetsu.exe --edition Enhanced` with a private session environment variable and embeds its actual SDL2 Win32 child window. The viewport maintains the game's 256×240 presentation aspect ratio. NES frame timing, mouse mapping, gamepad, mapper and audio remain owned by the native process; no screenshot mirroring.
- **Live scene tree:** Reads the current resolved JP room and up to 128 persistent room lights from a bounded, versioned local shared memory bridge. Select a placed light in the tree to edit it.
- **Lighting inspector:** Place Candle/Torch in view center, select, duplicate, delete, change radius, power, RGB, flame animation, Standard/GPU Prototype/Radiance Cascades renderers, and undo/redo. The game SDL thread owns mutations and existing `config.ini` persistence. **Edit/Pause** opens the game's existing modal paused editor; **Play** resumes.
- **Sprite Studio integration:** Read-only snapshots of all 64 actual original PPU OAM sprite slots, alongside editable named sprite groups and display-layer organization. Original OAM slot rotation means these numeric slots are **not stable character identities**; grouping data is project-authoring metadata for the next validated sprite/asset importer, **not yet live OAM replacement**.
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

## Native game keyboard and lighting gizmo controls

**Play:** after attaching a game, click **Play** or **Focus Game** to
transfer Windows keyboard focus to the embedded SDL child HWND. Arrows
move the player; Z/X are A/B, Enter is Start, and Backslash is Select.
The editor attaches input threads only while setting cross-process focus,
then immediately detaches. Gamepad input remains native SDL2.

**Edit / Pause:** use **+ Torch** or **+ Candle** to place a light, then
click and hold the white light handle visible in the native game viewport,
drag it to the desired location, and release to commit/persist the move.
The engine uses the real room scroll and mouse mapping, creates one undo
checkpoint at drag start, and never adds a light when clicking empty
space. **Undo** reverses the change. Mouse editing is enabled only when
the authenticated session's editor is paused; normal gameplay uses the
original SDL event path. The native renderer supplies the ring/handle
visuals directly, not a WPF overlay across Win32 airspace.

These changes require **both** the updated NEStudio Windows editor and
a newly compiled owner-private game from the latest feature branch.
Prior native executables will not have the new editor drag router.

## Windows launcher and live viewport acceptance

Open the **Acceptance Log** button after starting the game. It opens a
local text file in `%LOCALAPPDATA%\\NEStudio\\Acceptance`. The editor
records the game's bridge-reported PID, whether native frames advance,
successful Win32 viewport parenting, the first live OAM/light snapshot,
and acknowledgements or rejections from native lighting commands.
The file is local to the Windows PC and is not uploaded automatically;
review it before sharing it.

Acceptance procedure for the real owner-private Windows build:

1. Use **Set Game / Launcher** to select the updated Enhanced `.exe`,
   `.bat` or `.cmd`. Click **Run / Attach** and confirm game video and
   audio appear inside the resizable NEStudio viewport.
2. Confirm the acceptance log contains both **frame counter is advancing**
   and **Win32 parent verified** (with the native game PID). Resize the
   editor and check that the native game stays in its viewport.
3. Click **Edit / Pause**, place a **Torch**, select it in the Scene
   Outliner, change its color and radius, and confirm an acknowledged
   native lighting property edit. Click **Play** and check controls.
4. Save the project, click **Stop**, reopen the game, and inspect the
   native lighting settings for persistence. A project save does not
   replace the native lighting `config.ini`.

**CI cannot certify the user's actual SDL/D3D11 rendering, mouse focus,
gamepad input, or persistence.** Mark those as accepted only after the
Windows gameplay exercise; an active bridge and parented HWND alone
are not proof of correct visual output.

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
