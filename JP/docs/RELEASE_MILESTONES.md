# Japanese Castlevania III — Release milestones

The project now prioritizes **playable deliverables**, not arbitrary
counts of reconstructed ROM bytes. Retain original ROM authentication,
the C11 native cycle compiler, and the proven C++ implementation as a
reference. No copyrighted ROM, generated commercial game code or
user saves go into public GitHub releases.

## Alpha — Windows x64, actual game boots and responds to the player

**Release candidate label:** `0.1.0-alpha.1`.
**Current status: PRIVATE ALPHA CANDIDATE BUILT — original Japanese C11
Windows x64 SDL2 executable now exists, and headless guest execution reaches
Stage 1. Actual Windows window/audio/interactive controls remain unverified.**

Required before labeling an artifact "playable alpha":

- A Windows x64 `jp_akumajou_densetsu.exe` is generated from the
  authenticated original Japanese VRC6a ROM with NESRecomp's
  cycle-accurate C11 backend, the pinned external license reviewed.
- The actual **SDL2 window** opens (not a headless frame-counter process),
  with audio, keyboard/gamepad input, and the title screen visible.
- Start transitions to controllable Trevor movement in Stage 1;
  walking, jumping, whipping and pause work without crashing.
- Original game's VRC6 mapper24, PPU and audio remain active. Known
  issues are written down. Saves and longer routes are not prerequisites.
- A ROM-free packaging/rebuild kit and private reproducible hash
  exist; the actual native game executable derived from the user-owned
  ROM stays local unless distribution rights are established.

**A private candidate is now available for the owner's Windows interactive
verification, but it is NOT yet a publicly qualified playable Alpha.**
An artificial-ROM VRC6 CI test, a successful C11 compiler,
an interpreted CPU fallback, or a command-line loop alone is not
a playable release.

## Beta — Stage 1 and route/playability coverage

- Stage 1 boss, exit and route transition through original input.
- Selected additional stages and character recruit/switch behavior.
- ROM-backed native CPU cycle share and fallback counts reported.
- Frame/sprite/audio/IRQ correctness compared to original where needed,
  including at least one authentic Mesen reference path.
- Packaging and save-state behavior checked on clean Windows systems.

## Final — complete game release

- Entire game (multiple partner/route choices and endings) playable.
- Major visual/audio and VRC6 IRQ/memory parity independently verified.
- Controllers, saves, region handling, packaging, licenses and
  deterministic regressions pass on release binaries.
- Public distribution consists only of legally distributable binaries
  and components. Original ROM and derivative generated game code
  require an appropriate distribution-rights assessment.
- A reproducible signed/versioned build and changelog are available.

## Immediate alpha engineering sequence

1. Enforce windowed SDL availability at CMake configuration (**0579**).
2. Build a **real windowed binary** with a public wholly synthetic
   mapper24 fixture in Windows CI (validates build plumbing only).
3. Provide a private-ROM alpha build/launch kit for Windows x64
   with pinned engine checkout and bundled third-party notices.
4. Build and open the genuine Japanese game in a Windows window,
   fix the first blockers. **Only then invite user testing.**

Independent C11 compiler tests should be rerun only when relevant
source, mapper or release-toolchain changes require them.

## Phase 0584 — authenticated original-game native Alpha candidate

The owner-supplied original Japanese ROM was compiled with the pinned
NESRecomp 2A03/VRC6 C11 cycle backend and a windowed **Windows x64 SDL2
executable** was cross-linked using Zig 0.13.0. The owner's private alpha
ZIP includes the PE32+ executable, SDL2.dll, launcher, PolyForm-NC/SDL2
license notices, alpha metadata, and a Stage 1 PNG. It excludes the ROM
and is not committed or published as a public release.

Real-original-ROM checkpoints (different from synthetic CI):

- Unseeded 600 frames: 17,865,917 CPU cycles; 62.3% native.
- Seeded 600 frames: **17,865,910/17,865,917 native cycles**,
  **zero ROM/RAM interpreter fallbacks**. All 600 frame hashes and the
  final screenshot are **byte-for-byte identical** to the unseeded run.
- 1800 frames without input: title screen, opening castle and intro text
  were rendered.
- 2100 frames with deterministic Start input: original 'ENTER YOUR NAME'
  screen displayed.
- 3000 frames with scripted Start/A/right/B input: original **Stage 1**
  visible (SCORE/TIME/BLK, Trevor sprite and enemies), 86,450,376 /
  89,339,119 native CPU cycles (96.8%). Later stages have not been tested.
- Windows native executable: SHA-256
  `1ad5fdd6d7ed05ea9abb47c50c5b489392899405492db69d1682441b221e3024`.
  PE32+ x86-64, links SDL2.dll; GUI run/audio/controller verification
  still **pending**. The cross-linked binary is not evidence by itself
  of an interactive Windows pass.

This supplies the owner a real-ROM Alpha candidate to test. The Stage 1
CPU/scripted-input proof is headless on Linux, not a hands-on Windows QA
result. No independent Mesen frame parity claim and no update to the
historical 27/100 VPP or 49,504/262,144 strict PRG certificate.
