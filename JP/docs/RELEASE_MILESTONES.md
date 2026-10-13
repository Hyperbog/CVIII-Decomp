# Japanese Castlevania III — Release milestones

The project now prioritizes **playable deliverables**, not arbitrary
counts of reconstructed ROM bytes. Retain original ROM authentication,
the C11 native cycle compiler, and the proven C++ implementation as a
reference. No copyrighted ROM, generated commercial game code or
user saves go into public GitHub releases.

## Alpha — Windows x64, actual game boots and responds to the player

**Release candidate label:** `0.1.0-alpha.1`.
**Current status: OWNER-TESTED WINDOWS ALPHA — the owner reports that the
original Japanese native C11 Windows build is playing flawlessly, with no
issues reported in their initial interactive test. Full-game completion,
all controls/audio/saves and individual routes remain unverified.**

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

**The private Alpha candidate has now passed an initial owner-reported Windows
playability check.** This is sufficient to proceed to Beta validation, but
is **not** evidence that the entire game or every route has been completed.
No public redistributable executable is authorized by this observation.
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

## Phase 0585 — first owner-reported live Windows Alpha playtest

On 2026-10-12, after launching the private Windows x64 original-Japanese
C11 Alpha candidate, the owner reported: "The game is playing flawlessly
and it looks like I can probably play the whole game."

**Verified by user report:** Native Windows build launches into playable
game content and no defect was reported in the initial interactive session.
This is distinct from the previously completed scripted/headless Stage 1
checks and is the first reported real-machine interactive acceptance.

**Not yet established:** Exactly which stages, endings, partners, save/load,
controllers, audio devices, frame rates or alternative routes were tested.
"Probably play the whole game" is a reasonable expectation, not a full
playthrough result. Do not label Beta or Final complete yet.

### Next release gate: Beta

Use **natural playtests**, not wholesale reconstruction testing:

1. Complete Stage 1 boss and its exit/route transition, if not already done.
2. Continue into at least one later level, documenting the first abnormality.
3. Test partner recruitment/switching when encountered, plus pause and audio.
4. Verify any supported save/reset or resume workflow before claiming it.
5. Keep a short list of reproducible Windows-specific issues and collect
   logs/screenshots only if a defect occurs. No gameplay recording required.

Full-game Final acceptance still requires multiple routes/endings, stable
session behavior, visual/audio fidelity, packaging and legal review.
These owner observations **do not change** independent Mesen parity/VPP
metrics: 27/100 VPP, 49,504/262,144 strictly certified PRG bytes.

## Phase 0586 — owner confirms Stage 1 boss and lower Stage 2 entry

Owner Windows x64 original-Japanese C11 Alpha follow-up on 2026-10-12:
**Stage 1 boss defeated, Stage 1 exit and branch transition succeeded,
and the owner has just started Stage 2 on the bottom/lower route.**
The owner previously reported flawless interactive gameplay and has not
reported a new fault in this follow-up.

This satisfies the *first Beta route-progression gate* through Stage 1
and entry into the lower Stage 2 branch. It **does not** verify that
Stage 2 is complete, that upper route or alternate partners function,
or that any later boss, ending, save operation or audio implementation
has been exhaustively tested. Continue natural gameplay; ask for
screenshots/logs/reconstruction tests only in response to a concrete
problem. No user gameplay recordings are required.

Alpha remains a private, user-tested build. Beta validation in progress;
no Beta/Final release is claimed. Existing VPP27/100, strict PRG
49,504/262,144 and prior compiled-site census remain unchanged.

## Phase 0587 — owner reaches Stage 4-0A, recruits Sypha, switching works

On 2026-10-12, the owner reported that the private original-Japanese
native C11 Windows Alpha reached **Stage 4-0A** following the lower
route. **Sypha was recruited and switching player characters works.**
The owner described the overall game as playing very well, with
**minor sprite glitches in the purple area** of Stage 4-0A. A screenshot
was supplied; the exact rendering/timing root cause has not been
established. The earlier Stage 2 lower-route background pixels
occluding Trevor remain separately described under the expanded
[graphics issue #1](https://github.com/Hyperbog/CVIII-Decomp/issues/1).

**Beta acceptance newly supported by owner report:** real-game
multi-stage progression, Sypha recruitment and character switching.
**Unverified:** successful Stage 4-0A boss/exit, other partners,
alternate routes, endings, complete audio, saves and full enhanced
features. Avoid unnecessary decomp/reconstruction/testing while the
user plays normally.

## Phase 0588 — dual-edition product specification

The owner has defined **Original** and **Enhanced** builds on the same
native C11 engine. Enhanced aims for true widescreen, separate sound
channels and independent SFX/music, optional remastered/alternate
soundtracks, freely remappable controls, sprite/texture packs and
flicker-free graphics. **Underlying original gameplay is the default
for both editions.** Optional new moves (e.g. SCIV-style directional
whipping) require separately enabled Enhanced-only gameplay modules.
The architecture, acceptance criteria and issue links are recorded in
[Original and Enhanced editions](ORIGINAL_ENHANCED_EDITIONS.md).
These enhancements are **not implemented** in the current Alpha.
