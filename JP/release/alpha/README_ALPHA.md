# CVIII Japanese Castlevania III — private Original/Enhanced Alpha 0.2

Version 0.2.0-alpha.1. The original C11 Windows Alpha 0.1 was
owner-tested through Stage 4-0A, including Sypha and character switching.
The NEW experimental extra-sprite Enhanced renderer requires owner QA.

Build privately on Windows (CMake, Visual Studio, Git, Python and the
unmodified original Japanese Akumajou Densetsu ROM required):

    powershell -ExecutionPolicy Bypass -File .\Build-Alpha.ps1 -Rom "C:\Games\Akumajou Densetsu (Japan).nes"

The build kit downloads pinned NESRecomp PolyForm Noncommercial source
to a separate private directory and compiles the original owner ROM into
a local executable. The public build kit contains no ROM or game code.

After build, double-click Play-Original.bat or Play-Enhanced.bat in the
private AlphaCandidate directory. Play-Alpha.bat remains an Original alias.
The launchers authenticate original Japanese mapper24 ROM SHA256 and
prompt for the cartridge when not supplied.

Original: faithful PPU presentation and original gameplay.
Enhanced: experimental all-primary-OAM sprite compositor intended to
remove eight-sprites-per-scanline flicker. CPU/PPU-visible gameplay,
sprite-0 hit, IRQ, DMA and collisions remain original. Sprite art can
misrender if CHR banks switch mid-frame; fall back to Original as needed.

Default input: arrows=movement; Z=A; X=B; Enter=Start;
Backslash=Select. The NESRecomp SDL host supports configurable
keyboard/controller bindings. Builds with the 0591 slot extension
support Ctrl+0..9 slot selection plus F8/F9 save/load.

Not yet supported: true widescreen level geometry, individual channel
gain, independent soundtrack/SFX voices, remastered audio or texture
replacement, and optional new moves. The Stage 2/3?/4-0A shared
background-layer artifacts remain an unresolved Original issue.

Focused authentic-ROM validation: Original and Enhanced 600-frame
headless CPU/PPU/memory hashes match byte-for-byte. This is not
full-game/Windows Enhanced GUI certification. Do not distribute the
copyrighted game EXE, ROM or third-party sound/assets publicly.

## Private Windows stage and companion debug picker

New AlphaCandidate private builds include Debug-Stage-Companion.bat.
Double-click it (Python 3 with Tkinter required); choose a stage/checkpoint,
None, Alucard, Sypha or Grant, and the same name used at game name-entry.
Copy the displayed 4x4 password grid and enter its symbols manually
on the game's password screen. Password symbol keys: W=whip,
R=rosary/cross, H=heart, .=blank.

The original game's Normal difficulty only supports some partners
on each route. The picker rejects unavailable combinations. Hard mode
may allow the combination but changes the game difficulty. This is
an external test aid, not an in-game F10 debug menu, not mid-game warp
or RAM-based companion injection. The Japanese live password path
still needs acceptance testing on the original compiled game.

## JP0594 F10 stage and companion checkpoint warp (new private build)

Inside either Original or Enhanced gameplay, press **F10**. The game
pauses. Up/Down chooses one of 18 stage checkpoints; Left/Right chooses
None, Alucard, Sypha or Grant. **Enter** loads a previously captured
whole-machine checkpoint for the selected stage and companion (true
instant stage warp). **F5** captures the *currently running game*
as the selected stage/companion checkpoint; **Esc/F10** resumes.

Each checkpoint is a separate `saves/<ROM>.debug.stageNN.partnerN.cycstate`,
compatible with the original full-machine F8/F9 serializer. Saving a
checkpoint does NOT create or add a companion: capture when the selected
companion is already actually in the game. Likewise, **a stage cannot
warp before its compatible checkpoint exists.** One can reach it naturally
or start with a valid password and capture once; subsequent stage jumps
are immediate. Checkpoints are specific to the native executable build
and may need recapturing after recompilation. Slot 0..9 saves are separate.
No ROM patching, unproved RAM writes or gameplay state fabrication.
The separate password picker still helps seed a stage from the title.
This initial F10 implementation requires a new private Windows build
and has not been owner-playtested.

## JP0595 password clipboard controls

The external `Debug-Stage-Companion.bat` window now has **Paste
password** as well as Copy. Paste a 4x4 grid of W/R/H/. marks;
the tool checks the original player name, checksum and companion-route
legality before selecting its stage, companion and difficulty. This
does not yet type a password into the NES game automatically.

## JP0595 in-game password clipboard shortcut

Open F10 and press Ctrl+V to paste a 4x4 W/R/H/. password grid.
The ROM-authenticated checksum and stage selector are decoded,
and the current F10 stage and companion are selected accordingly.
Press Enter to load the corresponding PREVIOUSLY CAPTURED checkpoint.
No game CPU RAM, password entry or stage initialization is changed.
F10 cannot yet start an uncaptured stage; the external Python
password tool checks the name as well and can help seed it manually.

## JP0596 one-time password-screen bootstrap (Windows private Alpha)

This is a substantial improvement for testing multiple unvisited stages.
Preserve the original Japanese password system and ordinary New Game paths.

**Once per compatible native executable:** From the original title menu,
open the game's Password feature, enter your test player name and reach
the 4x4 password-entry screen. Press **F10**, then **F6** to capture that
original screen as a reusable whole-machine bootstrap checkpoint. F6
refuses to capture when the original game's $0019 menu state is not $08.

After that, at any point in gameplay press **F10**, use Up/Down for the
18 checkpoints, Left/Right for None/Alucard/Sypha/Grant, and **Tab** to
select Normal/Hard difficulty. Press **Enter**:
- If the corresponding stage/partner/difficulty snapshot already exists,
  it loads instantly (unchanged 0594 behavior).
- Otherwise the engine loads the single original password-screen snapshot,
  encodes a new stage password using the name in that actual saved screen,
  and fills original Japanese password RAM $0790..$079F. **Confirm the
  password using the game's normal confirm control** to begin the level.

The original JP password decoder performs the real game-state and route
initialization; F10 does not pretend it can jump directly to arbitrary
stage code. Normal mode still rejects route-impossible companions; Hard
can admit additional combinations but changes game difficulty. Ctrl+V
inside F10 still selects a checkpoint from a pasted password, and the
external Python picker still supports full password copy/paste.

The bootstrap loading path backs up the current entire machine and rolls
back on a wrong menu state or any RAM-write failure. The existing saves
are preserved; Hard-mode checkpoints use a distinct file suffix. Both
Original and Enhanced can use the **development-only** F10 tool.

**Validation status:** GitHub Windows synthetic UI/C11 compilation does
not establish real JP password acceptance or the first successful
transition. The exact $0019 state, active password UI and subsequent
stage initialization require owner/private Windows or independent Mesen
frame tracing. Treat this as a development test feature until confirmed.


## JP0597 private versioned ROM asset package

Build-Alpha.ps1 now generates or verifies a local **CVIII-Assets.bin**
under AlphaCandidate. It is derived from your authenticated Japanese
mapper24 ROM and included ONLY in the private output/ZIP. The package
is a deterministic ZIP-format archive with a JSON manifest, SHA256 of
every entry, all **128 physical 1 KiB CHR pages (8,192 tiles)**,
all 524,288 decoded CHR palette-index pixels, and the six ROM-confirmed
password tables with physical bank addresses. These are raw physical
CHR tile indices, not final colored sprites or decoded room backgrounds.
The archive preserves every raw CHR byte and tests lossless re-encoding.

To regenerate independently, run (from an up-to-date repo checkout):

    python JP/tools/jp_asset_pack_0597.py --build --rom "C:\Games\Akumajou Densetsu (Japan).nes" --out "C:\Games\CVIII-Assets.bin"

To validate a cached package without reopening the retail ROM:

    python JP/tools/jp_asset_pack_0597.py --verify --out "C:\Games\CVIII-Assets.bin"

A repeated private build reuses an intact package. On a corrupt,
outdated or incompatible archive it fails closed: run the same
--build command with --rebuild to regenerate it from the authenticated
original cartridge. Original-JP assets remain copyrighted and local;
never publish or attach CVIII-Assets.bin to public Git or CI.

**Phase boundary:** The current Original/Enhanced native executable
still executes the original game's ROM-derived native code and requires
the authenticated ROM at private compilation/launch. Neither edition
reads CVIII-Assets.bin yet. Substituting it for the ROM or claiming
renderer parity would be premature. Future stages will identify CHR
bank/register changes and game level/animation structures, then
switch only verified Enhanced presentation reads to the package.
