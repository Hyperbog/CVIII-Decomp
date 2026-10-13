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
