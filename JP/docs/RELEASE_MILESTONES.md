# Japanese Castlevania III — Release milestones

The project now prioritizes **playable deliverables**, not arbitrary
counts of reconstructed ROM bytes. Retain original ROM authentication,
the C11 native cycle compiler, and the proven C++ implementation as a
reference. No copyrighted ROM, generated commercial game code or
user saves go into public GitHub releases.

## Alpha — Windows x64, actual game boots and responds to the player

**Release candidate label:** `0.1.0-alpha.1`.
**Current status: BLOCKED — original retail-JP cycle game has not
been built and played in a Windows SDL window.**

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

**Do not ask the user to playtest before these conditions pass.**
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
