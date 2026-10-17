# JP0624 — F4 Start/Pause native action-shell regression gate

**Bounded result:** New ROM-free integration test for the **actual source
fragment produced by the JP0623 pinned SDL patcher**, not a second
Start/Pause implementation. The goal is to catch bugs in Save State,
Load State, Audio, Quit confirmation, input ownership and netplay
opening restrictions **before** claiming a playable Windows alpha.

## Implementation

[JP0624 executable harness](../tools/jp_start_pause_shell_test_0624.py)
imports the real `JP/recomp/tools/patch_cyc_start_menu_0623.py` module and
extracts its `SHELL` string without rewriting it. It creates one small
private temporary C11 translation unit around this exact source,
compiles it against the **actual game-owned
`cviii_start_menu_0623.c` action-registry module**, and executes
two variants:

- Offline: authenticated asset/Enhanced gating, F4 key-repeat suppression,
  unchanged gameplay-key ownership outside the modal, Up/Down navigation,
  keyboard Enter and gamepad A acceptance, current-slot Save/Load callback
  dispatch, Audio submenu delegation, two-step Quit confirmation,
  cancelling Quit confirmation by navigation, Escape/gamepad Start close
  and restored input ownership.
- Netplay compile flag `-DNESRECOMP_NET`: same checks plus a fake active
  match in which F4 **must not open** the menu.

The fixture uses minimal SDL type and key/button constants, plus
instrumented mock save/load/audio and Quit callbacks. There is **no
original ROM, original game graphics, upstream SDL source, actual window
or emulated CPU** inside the test. The real private host build remains
separate.

A `--smoke` mode verifies import of the exact committed patcher,
presence of C source action handlers and the ability to build a valid
fixture **without** invoking a compiler, so Windows CI can verify the
source setup even when the Microsoft `cl` environment is not loaded.

Run from repository root:

```sh
python3 JP/decomp/tools/jp_start_pause_shell_test_0624.py --smoke
python3 JP/decomp/tools/jp_start_pause_shell_test_0624.py
```

The default `cc` can be overridden with `--cc clang` or `CC=clang`.
The harness builds both modes using `-std=c11 -O2 -Wall -Wextra
-Werror -pedantic`; it deletes the temporary C source and executables
after a successful run. Use `--emit-c /tmp/start_shell.c` for inspection
without a build.

## Verification and CI

- **PASS locally:** A separately assembled C11 mock of the JP0623
  Pause shell compiled with strict GCC flags and executed in both
  offline and `NESRECOMP_NET` variants, using the locally mirrored
  JP0623 action registry. It confirmed Save/Load/Audio/confirmed Quit
  flow, close/input-return and netplay-open refusal.
- **Committed, not yet run locally:** The script's exact-patcher
  `SHELL` extraction, its `--smoke` run, and compilation/execution
  of the source-generated fixture. Both checks are now CI-gated on
  Linux (one smoke plus two compilation/execution variants); Windows
  CI gets the extractor smoke. **No new CI run result has been checked.**
- **Still unverified:** five-layer generated *full* pinned upstream
  SDL source compiles/links, private Windows GUI execution, real
  keyboard/gamepad event propagation, pause/resume cycles, configured
  quick-save slot semantics during a live game, independent Music/SFX
  mixer operation and byte-exact original PPU palette matching.

## Architecture impact

The original gameplay, 6502/mappers/APU/PPU timing, level data and
progression remain untouched. The Start/Pause registry retains four
built-in stable action IDs and space for more, but a public mod package
loader, editor, save-slot picker and customizable gamepad open binding
are **still not implemented**. Do not describe this isolated harness as
proof that the complete Windows build is playable. The existing
[universal mod-forward methodology](../../../MOD_FORWARD_METHODOLOGY.md)
continues to govern future extensibility.

**Certification unchanged:** semantic PRG **49,504/262,144**,
VPP **27/100**, checkpoint **0508**, frontier **$FB96**.
`JP/decomp/analysis/RESUME_STATE.json` remains unmodified.
