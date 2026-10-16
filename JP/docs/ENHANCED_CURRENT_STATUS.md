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
| Save states | F8/F9 and Ctrl+0..9 native slots; current GUI Save/Load chooser still needs owner round-trip validation |
| Enhanced F4 Start/Pause | Source-implemented Save, Load, Audio and two-step Quit, game-authentic pixel font, modal pause and input release; source/C11 tests pass; F4 opens by keyboard, gamepad operates menu after opening |
| Enhanced F4 Save/Load chooser | Original font, 0–9 slot picker, uses existing whole-machine serializer; new GUI/real save-load acceptance pending |
| Enhanced F6 Audio | Health-bar and original-font menu with 1% Master/Music/SFX sliders; nested Audio returns to parent Pause; latest owner UI acceptance pending |
| Master volume | **Working**, applied to final mixed PCM in Enhanced mode |
| Music/SFX sliders | Stored settings only; **not** independent sound gains or voices |
| Experimental sprite enhancement | Opt-in extra-OAM compositor and stable sprite history/priority; default off, independent owner acceptance needed; not required to close already-resolved issue #1 |
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
2. **One functional cosmetic mod:** implement a versioned manifest,
   a symbolic asset ID, validated override, and safe original fallback.
   Make it installable/removable with unchanged gameplay semantics.
3. **First actual independent Music/SFX voice prototype:** one song
   plus competing effects, isolated original hardware emulation, and
   working separate output gains before claiming a full audio system.
4. Continue other larger Enhanced targets in priority order after
   regression baselines exist: player remapping, texture packs,
   audio replacement and widescreen.

## Independent historical decompilation metrics

Strict semantic PRG **49,504 / 262,144 (18.8843%)**;
VPP **27/100**; certified checkpoint **0508**;
fixed PRG31 frontier **$FB96**; room-loader R-002 **OPEN**.
None measures the percentage of the playable game that works.
