# JP 0592 — Owner-only Original/Enhanced Alpha 0.2 Windows x64

The authenticated Japanese retail mapper24 ROM was compiled into a
Windows x86-64 PE32+ native C11 game using the independently obtained
pinned PolyForm Noncommercial NESRecomp runtime and Zig 0.13.0.
The executable links SDL2.dll and includes the previously implemented
JP0589 host-defined Original/Enhanced presentation layer.

A new private Alpha 0.2.0 Windows ZIP, delivered to the ROM owner,
contains CVIII_Alpha.exe, SDL2.dll, Original/Enhanced launchers,
legal notices, a build manifest and a visual reference screenshot.
It does not contain the original commercial ROM. Neither this
commercial-code-derived executable nor its generated source is
committed to the public repository.

Original launcher: faithful original game PPU presentation.
Enhanced launcher: experimental presentation-only recomposition
from all primary-OAM sprites. The hardware eight-slot sprite evaluation,
sprite-0 hit, PPU overflow, DMA, CPU, IRQ and collisions are unchanged.
It cannot recover sprites the original game never placed in OAM and
may misrender around mid-frame CHR bank changes. The Alpha 0.2 owner
Windows interactive acceptance is still pending.

Focused original-game test: one private compiled Linux C11 executable
ran 600 frames with --edition original and with --edition enhanced
--unlimited-sprites 1. The two generated per-frame CPU/PPU/memory
hash files were byte-for-byte identical, confirming no change in
observable machine state over that test. The intro presentation
images were also identical (no sprite overload at that point).
That is not evidence of flicker elimination during crowded play.
The Windows native EXE was confirmed as PE32+ x64 and linked to
SDL2.dll; archive integrity was verified. No reconstruction tests.

Release source JP/recomp/release/alpha/Launch-Alpha.ps1 now authenticates the
Japanese ROM and accepts Original or Enhanced explicitly. Play-Original,
Play-Enhanced, and legacy Play-Alpha alias are included in the public
ROM-free build kit. Its version is 0.2.0-alpha.1, and the Windows
synthetic SDL integration gate continues to test absence of ROM in CI.

The separate Stage 2/3?/4-0A background-layer defect is tracked as
GitHub issue #1 and has NOT been diagnosed or fixed. Enhanced full
widescreen, mixer channels, alternate audio, texture packs, and
optional multidirectional whipping remain planned, not included.

Historically certified PRG bytes 49,504/262,144, VPP27/100, and
the original recompilation site census remain unchanged.
