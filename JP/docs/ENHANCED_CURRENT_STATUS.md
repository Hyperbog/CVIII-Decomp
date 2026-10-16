# Enhanced Edition — Current status (JP0643)

Reconciled with the owner's October 2026 gameplay feedback.
This is the **current product status**, not a replacement for the
chronological decompilation notes.

## The working player-facing baseline

- **One public Enhanced Edition**, with faithful original Japanese
  Akumajou Densetsu gameplay as the default. The internal `Original`
  runtime mode is retained for engineering A/B checks, not a separate
  public product.
- The owner reports that the native Windows game runs correctly.
  The earlier rendering artifact (Stage 2/3?/4-0A/A-01 discussion)
  is **resolved by owner confirmation**. [Issue #1](https://github.com/Hyperbog/CVIII-Decomp/issues/1)
  has been closed as completed. This is not a technical pixel-parity
  certificate or an identification of a particular fix commit.
- The current published public kit is documented as
  **0.2.0-alpha.1**: an owner-ROM-authenticated local Windows build kit,
  **not** a downloadable copyrighted game executable.
  Historical owner validation extends through Stage 4-0A, including
  character switching with Sypha. Later host/menu features may not
  yet have undergone an owner gameplay pass.

## Implemented source, with remaining acceptance limits

| Component | State and limitations |
|---|---|
| Native Japanese game and public Windows launcher | Playable owner-tested baseline; user supplies authenticated original JP ROM |
| Save states | F8/F9 and Ctrl+0..9 native slots; JP0644 now rolls back the chosen quick slot on failed I/O and keeps the picker open for retry; real owner-file round-trip still pending |
| Enhanced F4 Start/Pause | Source-implemented Save, Load, Audio and two-step Quit, game-authentic pixel font, modal pause and input release; source/C11 tests pass; F4 opens by keyboard, gamepad operates menu after opening |
| Enhanced F4 Save/Load chooser | Original font, 0–9 slot picker, uses existing whole-machine serializer; new GUI/real save-load acceptance pending |
| Enhanced F6 Audio | Health-bar and original-font menu with 1% Master/Music/SFX sliders; nested Audio returns to parent Pause; latest owner UI acceptance pending |
| Master volume | **Working**, applied to final mixed PCM in Enhanced mode |
| Music/SFX sliders | Stored settings only; **not** independent sound gains or voices |
| Experimental sprite enhancement | Opt-in extra-OAM compositor and stable sprite history/priority; JP0645 now uses original PRG26 OAM-rotation emission identity to prevent duplicated animation ghosts, with 64-sprite synthetic CI; default off, owner gameplay acceptance pending; issue #1 stays closed |
| Original ROM asset package | Authentic private CHR/package/index and read-only tracing are implemented, **not** an installable texture override |
| F10 stage/companion tools | Debug-only checkpoint/password bootstrap, not public game progression |
| JP0641/JP0642 scenario/replay tools | Versioned preflight and private reference/native frame-budget orchestration; synthetic CI passed, genuine per-frame parity not demonstrated |

The pinned seven-stage native SDL chain successfully passed Windows
Alpha builder and Linux NESRecomp integration GitHub Actions at JP0639
(runs 38829146730 and 38829147219). The independent scenario
contract passed Windows and Linux at JP0642 (run 38833423691).
Those results validate build/instrumentation, not all new UI features
on the owner's actual Windows desktop.

## Not yet delivered as Enhanced player features

- Independent music and sound-effects voice pools, mixing, and true
  Music/SFX volume gains (issues #3 and #6).
- Player-installable, versioned symbolic-ID texture/resource override
  packs with deterministic fallback (issue #8).
- True extended-world widescreen camera/view (issue #5).
- Player-facing control-rebinding UI and persistent profiles (issue #7).
- Optional multidirectional whip/new mechanics (issue #9), not part of
  faithful baseline behavior.
- Full mod/plugin SDK, mod loader, editor and alternate soundtrack packs.
- Owner QA of newly added F4/F6 menus, actual Save/Load slot files,
  input suppression, UI pause/resume, and keyboard/controller focus.

## Recommended next product milestones

1. **Current native Enhanced release candidate QA:** rebuild privately
   and verify F4/F6/Save-Load/Audio-to-Pause input, save persistence,
   real state round-trip and controller interactions. Accept the
   graphics issue closure; do not invent a new renderer defect.
2. **Complete optional Enhanced sprite presentation:** compare
   actual rendered scenes in owner builds, keep original mechanics
   unchanged, and fix only observed sprite regressions. This is
   independent of the already-closed graphics issue #1.
3. **Independent Music/SFX engine:** prototype one song and a few
   competing effects with independent virtual voices and working
   Music/SFX gains, then expand while preserving original sound
   hardware for CPU/gameplay state.
4. **Custom controls:** complete player-facing keyboard/controller
   rebinding and persistent profiles with a recoverable default.
5. **True widescreen:** render additional verified scene geometry;
   never stretch the 256x240 original bitmap as a substitute.
6. **Full Enhanced Beta acceptance:** exercise stage routes,
   companions, bosses, audio, saves and menus in actual gameplay,
   then release a stable Enhanced Edition.
7. **After release only:** modding infrastructure, user-installed
   texture/resource packs, soundtrack swaps, editors and optional
   gameplay modules. Do not put these on the active pre-release queue.

## Latest integration — JP0644

The seventh-layer generated SDL shell now passes compiled offline and
netplay tests with the real menu/slot/audio-controller C models, covering
transactional failed Save/Load, retry/cancel, nested Audio parent return,
modal input ownership and double-confirm Quit. The Windows SDL2 native
candidate builder and Linux external NESRecomp integration CI both passed
at commit `279da91c` (runs 38836167641 and 38836167331). These are
**synthetic-media integration results**, not real controller/save-file owner
acceptance. See [JP0644 evidence](../analysis/0644_ENHANCED_MODAL_TRANSACTION_AND_SDL_HARNESS.md)
and [owner menu QA](../release/alpha/QA_ENHANCED_MENUS_0644.md).

**Product scope reminder:** all modding features are explicitly deferred
until the Enhanced Edition is complete and stable.

## Latest gameplay-facing Enhanced work — JP0645

The optional StableSprites compositor now pairs animated sprite pieces
by logical PRG26 emission identity despite rotating physical OAM slots,
with one-to-one matching and conservative fallback. The original Japanese
PRG26 `$22 += $44` and OAM `X += $C4` opcode windows were checked on the
actual owner cartridge, not inferred from an invented ROM. A ROM-free
4,096-case phase/slot inverse audit is included. Both the Windows SDL2
candidate and Linux NESRecomp native integration passed, including the
new 64-piece animation and one-frame ghost tests (runs 38838450762 and
38838450730). **StableSprites remains opt-in/off by default** until owner
stage-specific visual QA; original gameplay and issue #1 resolution are
unchanged. Modding remains outside pre-release scope. See [JP0645](../analysis/0645_STABLE_SPRITE_EMISSION_ANIMATION.md).

## Independent historical decompilation metrics

Strict semantic PRG **49,504 / 262,144 (18.8843%)**;
VPP **27/100**; certified checkpoint **0508**;
fixed PRG31 frontier **$FB96**; room-loader R-002 **OPEN**.
None measures the percentage of the playable game that works.
