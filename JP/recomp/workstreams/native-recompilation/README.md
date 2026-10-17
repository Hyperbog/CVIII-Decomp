# Native recompilation — existing playable Enhanced Edition

**This is the functioning game/product workstream, not an unplayable prototype waiting for all PRG bytes to be semantically decompiled.**

The project already provides an owner-tested Windows **C11 NESRecomp/SDL2** build of Japanese *Akumajou Densetsu* (VRC6 Mapper 24), built privately from the authenticated original cartridge. The public `0.2.0-alpha.1` artifact is a ROM-free **builder/launcher kit**; it does not distribute the compiled commercial game or game ROM. The single public player-facing direction is **Enhanced Edition**; an Original rendering mode remains available as an internal baseline.

## Product implementation and acceptance

| Capability | Repository-backed state |
| --- | --- |
| Native original gameplay | **Playable owner-tested Windows baseline.** Repository specifically records gameplay through Stage 4-0A, Sypha and character switching. It does not include an independently recorded complete end-credits acceptance test. |
| Original graphics correction | Owner confirmed the prior defect resolved; GitHub issue #1 closed. This is distinct from the optional enhanced sprite compositor. |
| Extra sprite/flicker presentation | Optional 64-OAM compositor and stable sprite emission history; source and synthetic tests exist; **off by default**, latest owner scene-specific acceptance still pending. |
| Save states | Original full-machine serializer, F8/F9 and Ctrl+0..9 ten-slot selection; F4 Save/Load GUI implemented. Real owner save/load file-compatibility and latest GUI QA are separately tracked. |
| Stage and companion selection | F10 debug overlay lists 18 checkpoint labels and None/Alucard/Sypha/Grant. Previously captured compatible snapshots can be loaded; the password-screen bootstrap assists first entry. Selection is **not** arbitrary fabricated game state, and latest owner's first-visit QA is still pending. |
| PC menus and audio | F4/F6 presentation menus, a working master PCM gain and other host features; separate Music/SFX sliders are settings until original voice producers are integrated. |

**Product status source:** [Enhanced Edition current status](../../docs/ENHANCED_CURRENT_STATUS.md), [Alpha builder/controls](../../release/alpha/README_ALPHA.md), [release milestones](../../docs/RELEASE_MILESTONES.md), and [machine-readable product feature registry](PRODUCT_STATE.json).

## JP0661 — Persistent keyboard controls

An opt-in **Controls.bat** front end is now part of the
ROM-free build kit and private native AlphaCandidate. It
saves/restores named Player 1 keyboard profiles, offers
original and WASD/J/K presets, maintains recoverable
`config.ini` backups, and integrates with the existing
build-and-play launcher via `-ControlsProfile NAME`.
Gamepad mappings, player 2, audio, save states and original
game execution are unaffected. This is not an in-game
rebind UI. [Full product implementation evidence](0661_NATIVE_KEYBOARD_PROFILE_MANAGER.md).

## Relevant production code and validation

- [Native original-ROM cycle build](../../native/nesrecomp_cycle/CMakeLists.txt) — linked external pinned NESRecomp C11 machine and authenticated private ROM.
- [Enhanced host presentation](../../native/enhanced/cviii_edition.c) — product graphics, optional presentation and host-extension integration.
- [Save-state slot patch](../../tools/patch_cyc_savestates_0591.py), [stage/partner UI](../../tools/patch_cyc_stage_menu_0594.py) and [password bootstrap](../../tools/patch_cyc_stage_bootstrap_0596.py).
- [Windows Alpha compilation](../../../../.github/workflows/jp_alpha_windows.yml) and [Linux Mapper24 native runtime compilation](../../../../.github/workflows/jp_nesrecomp_cycle_mapper24.yml) — public CI uses **synthetic media**, not the user's retail ROM or a complete real-game playthrough.
- [Native release kit](../../release/alpha/README_ALPHA.md); private original-ROM build via the owner's `Build-And-Play.bat`.

## Explicitly not this stream's completion percentage

The [semantic VPP rubric](../../../decomp/workstreams/semantic-decompilation/README.md) and its historically certified unique PRG byte count measure **separate reverse-engineering research**. The Native runtime portion of that research rubric is **not** an assertion that this NESRecomp game lacks a CPU, PPU, frame loop, audio backend or playable executable.

This product's outstanding work is real-game release QA, optional enhancements, mod tooling and compatibility—not recreating an already functioning title screen, Stage 1, save-state serializer or NES execution engine.
