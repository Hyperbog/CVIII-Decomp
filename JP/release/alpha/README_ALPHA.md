# CVIII Japanese Castlevania III — Windows Alpha Candidate

Version **0.1.0-alpha.1 (BUILD KIT)**. This is NOT a qualified playable
release until the original game has been opened and controlled in Stage 1.

### Windows x64 prerequisites

Windows 10/11, Visual Studio 2022 Build Tools with **Desktop development
with C++**, CMake 3.20+, Python 3.11+, Git and a privately owned
unmodified "Akumajou Densetsu (Japan).nes".

The external NESRecomp runtime is subject to PolyForm Noncommercial 1.0.0.
Review this license before building or distributing a game.

### Build a private native game

Extract the builder ZIP and open PowerShell there. Run:

    powershell -ExecutionPolicy Bypass -File .\Build-Alpha.ps1 -Rom "C:\Games\Akumajou Densetsu (Japan).nes"

The script downloads CVIII and pinned NESRecomp, authenticates the ROM,
generates original game instructions as C11, compiles the entire
windowed VRC6 cycle runtime with SDL2 and creates a local private ZIP
under %USERPROFILE%\CVIII-Alpha. Neither ROM nor compiled game code is
included in this public build kit.

### Launch the candidate

    powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\CVIII-Alpha\AlphaCandidate\Launch-Alpha.ps1" -Rom "C:\Games\Akumajou Densetsu (Japan).nes"

Controls: arrows = D-pad, Z = A, X = B, Enter = Start,
Backslash = Select. Gamepad mapping is available through NESRecomp.

### Alpha release gate

This is a *candidate build*. Before the first PLAYABLE ALPHA is published
we must verify the actual original Japanese game displays its title
screen, accepts Start, and allows movement, jump, whip and pause in
Stage 1 without crashing. Synthetic-VRC6 frame tests are not enough.

Beta will expand Stage/character/route coverage. Final will require
complete-game routes/endings, sound, graphics, input, save behavior
and distribution-rights review. No commercial ROM is redistributed.
