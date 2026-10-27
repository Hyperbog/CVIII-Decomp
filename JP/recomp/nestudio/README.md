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

**Play:** after attaching a game, click **Play** or **Capture Keys**.
NEStudio captures arrows, Z/X, Enter and Backslash within its own WPF
window and publishes an eight-bit held-key mask through the authenticated
local native session bridge. The original NESRecomp SDL host merges
that mask with physical keyboard/gamepad state in `read_frame`, even if
Win32 focus cannot cross the embedded HWND boundary. Press **Escape**
to release input, or click **Release Keys**. Capture is cleared on
pause, stop, window deactivation and editor shutdown. External gamepad
support continues to use SDL. No ROM, guest CPU/PPU RAM or controller
serialization is edited by the bridge.

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

## True-dark interface

The editor uses near-black graphite backgrounds and bright foreground
labels, with custom dark ComboBox dropdowns, visible focus borders and
contrast-preserving selected items. The formerly dark-on-dark ComboBox
foreground is no longer inherited from the Windows system template.

## Original sprite-emission ownership and text-source discovery

NEStudio **v3** observes the original PRG26 sprite renderer, rather
than inferring sprite identity from color, proximity, or static OAM
indices. The pinned NESRecomp RAM-read policy provides the actual CPU
instruction PC. The observer accepts the bank-qualified `$8070`
`LDY $048C,X` read only when its mapped bytes match the original JP
opcode sequence `BC 8C 04`, recording current source object `$05`,
OAM cursor `$04` and free-slot counter `$07`.

The observer then requires an original renderer terminal read:
`$8038: A6 04` for a normal object pass or original
`$80ED: 68 68 60` at the 64-sprite non-local return. A missing
source call, invalid owner, conflicting physical slot, or unverified
terminal rejects ownership for that frame. Emitted OAM slot addresses
follow the original +`$C4` byte stride. The live bridge exposes
owner-by-OAM index, source-call and rejection counts. It never writes
CPU RAM, OAM, mapper, save states, or source ROM data.

In the **Sprites** tab, clicking a source-attributed visible sprite
selects its original CPU object. The viewport outlines all pieces
attributed to selected original objects in **gold**. Manually selected
OAM entries remain **cyan**. The Original Objects list, Ctrl/Shift
multiselection and Ctrl+G grouping follow the observed source identities.
If the hook cannot verify attribution for a particular frame, NEStudio
shows **Unattributed** rather than attaching the sprite to an invented
actor. The v3 bridge extends v2; both editor and private native game
must be rebuilt together.

**Original text printer research:** the private recomp now uses the
upstream passive PPU write callback to observe original writes to
nametable addresses `$2000-$2FFF`. The Dialogue inspector displays
the last observed source PC, PPU address, tile value, and total writes.
These are **source-side PPU access observations, NOT confirmed dialogue
events**. The address and tile alone do not identify the rendering
routine or originating script bank, and not all tile writes are text.
The original Japanese raw-bank 0A:$B8CC-$B908 room-message
selector also provides a verified source entry at $B8F4 (LDY $07A5).
The observer accepts that event only while the original mapped
instruction bytes AC A5 07, bounded $B921-$B936 message stream,
and 0..4 stage selector agree. For each authenticated source byte,
the v3 event record carries bank 0A, source PC $B8F4, original stage
and byte, and whether the value is the $FF terminator. A nonterminal
byte follows the game's JSR $EC47 at $B8FF. This is a **genuine
original message-source event**, not a proven text glyph or a
completed $EC47 printer hook. The editor lets authored Dialogue
entries bind to the last source-observed nonterminal byte.
Identify $EC47's actual text/PPU side effects before enabling
in-game text replacement or calling it a completed dialogue renderer.

For subsequent source tracing, run a repeatable real-game text scene
and save the local NEStudio acceptance log with location/timing.

## Original game-object identity and source-trigger milestone

The v2 bridge appends **28 actual original Japanese PRG26 object slots**
read from original game CPU RAM, with the seven verified renderer table
families (frame, Y, X, attributes, flags, sprite selector, mirror) plus
the original per-actor AI script byte at `$05EF+slot`. Source evidence
is in `JP/decomp/PreservationArchive/03_PPU_OAM_SPRITE_PIPELINE.md`,
`04_OBJECT_SCHEDULER_COLLISION_SCRATCH.md` and
`05_AI_SCRIPT_AND_ACTION_VM.md`. The native editor never writes this
guest state. Each active object obtains a host-only generation when
it first becomes active or its room changes; an inactive-to-active
transition also increments the generation. A slot reused without an
observed inactive frame cannot be distinguished and is explicitly
left uncertain.

In **Sprites**, the new **Original Game Objects** list shows raw
object slot, generation, position, selector and original AI-script ID.
Select multiple source objects (Ctrl-click) and choose **Group Original
Objects**, or press **Ctrl+G** while the object list has selection.
Room+slot+generation references are stored separately from the
older OAM snapshot groups. OAM pieces also display the original
phase-normalized emission index when `$22` is 4-byte aligned; that
emission order compensates for the proven `+$44` phase rotation but
**is not itself a proven object-to-piece owner lookup**. The newer v3 observer now identifies source-emitted OAM
ownership at original PRG26 instruction boundaries and highlights
attributed pieces. Failed or missing original boundary observations
remain unmapped instead of being assigned guessed owners.

**Dialogue trigger status:** No bank/PC-qualified original
text-print routine has yet been established. The v2 bridge reserves
an authenticated original dialogue-event record, initialized with
sequence zero; editor-authored screen markers never populate it.
The editor can now bind an authored dialogue to a **real observed
original actor AI-script byte transition** from `$05EF+slot`,
including original object generation and room. Select an original
game object in Sprites, select an authored dialogue in Dialogue,
and click **Bind selected original actor script**. The editor logs
and selects that entry if the observed AI-script byte later changes
into the bound value during the same object lifetime. **This is a
source-backed AI-script transition, not proof that the game printed
dialogue or that a script opcode is a text-rendering event.**
Automatic capture of original dialogue commands and replacement of
original guest text remain pending actual original-source proof.

These identifiers and trigger observations are ROM-free project data,
not semantic decompilation completeness claims.

## Restored full lighting and viewport tools

**Full Lighting Studio:** In the Lighting inspector, select **Full
Lighting Studio — all features**. This switches from NEStudio's compact
inspector to the existing game-owned Dear ImGui lighting editor. The
original implementation remains authoritative and includes emitter
types/shapes, range, intensity, direction, color, animation, global
styles, library presets and saved kits, ambient tint, independent
sky/hemisphere fill, exposure/temperature/saturation grading, particle
regions, weather and light-occlusion masks. The native game still
controls `config.ini` persistence, undo/redo and frame lighting. The
**Compact Lighting Inspector** button restores the simpler NEStudio
controls without resetting authored lighting data. The full panel draws
inside the SDL viewport, not as a separate operating-system window.

**Sprites:** Selecting the **Sprites** tab activates native OAM picker
mode and freezes the visible game frame through the existing host editor
session. Click the visible 8×8 portion of a sprite to select its current
OAM slot; Ctrl/Shift-click toggles additional selections. Selected
sprites receive cyan outlines inside the SDL viewport. **Ctrl+G** or
**Group Selected Sprites** adds a named group with the room, frame and
bounded slot/tile/attributes/coordinates captured. Editing names and
sort layers remains project authoring. Because the original game
rotates OAM indices, these saved members are **frame-local reference
snapshots**, not stable character IDs or live sprite overrides. Sprite
height may be 8×16 in other rendering contexts; this initial picker
only covers a conservative 8×8 hit area.

**Dialogue:** Selecting **Dialogue** switches away from OAM/light
picking. Add/select a dialogue record and choose **Bind region: click
viewport** to place an 80×24 authoring marker. The selected region is
outlined in amber; clicking any previously bound region selects its
dialogue entry. Region associations live in the `.nestudio` project
file and are bounded to a screen location and room. They are **not**
automatic extraction of the original NES dialogue script, or runtime
replacement of guest text. Actual textbox trigger identification
requires authenticated source hooks and guest-to-host event IDs.

All modes share one authenticated native session; no ROM or PPU RAM is
modified by these editor interactions.

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
- Native emitter handles can be dragged and selected and the OAM picker highlights frame-local slot snapshots. There is no stable guest-object identity/transform gizmo or arbitrary frame-step API yet. Debug mode cannot be equated with full game-engine simulation controls.
- Original/Enhanced parity and user data safety remain authoritative. Do not commit ROMs, locally built EXEs containing retail content, ripped CHR archives, or private saves.

## Acceptance milestones

1. **Current:** Build and open the Windows application, load a privately built game into the viewport, pause, select a torch, change its RGB/radius, save, restart and verify persistence.
2. Add read-only live sprite/OAM identities and background/foreground separation to the same scene inspector, then a data-only sprite asset replacement compiler with runtime consumption and override validation.
3. Add authentic dialogue trigger IDs, multilingual text resource loading, variable-size boxes, typewriter/page events, layout/glyph checks and deterministic gameplay-event execution.
4. Replace cross-process SDL HWND parenting with an explicit render-surface sharing API only if live owner QA exposes unacceptable focus/render/compositor behavior.
5. Implement a single transactional asset/project build and runtime hot-reload boundary; expand the timeline to actual scene triggers without altering original gameplay by default.
