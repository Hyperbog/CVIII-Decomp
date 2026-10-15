# JP0625 — Authentic-font Save/Load slot picker (Enhanced Start/Pause)

**Target:** Enhance the existing JP0623 F4 Start/Pause menu with a graphical
0–9 Save State / Load State slot selector, instead of immediately operating
on the previously selected slot. Keep the default Japanese-game physics,
enemy timing, camera, controller gameplay and ROM machine state unchanged.
This is an owner-local Enhanced presentation feature. It is **not**
a new serializer, level editor, mod package loader or public plugin API.

## Player interaction (source committed, Windows playtest pending)

- Open Enhanced **Start/Pause with F4** (the authenticated private CHR
  index must be available). Choose **Save State** or **Load State**.
- The corresponding **SAVE SLOT** or **LOAD SLOT** page displays the
  currently selected host quick-save slot, **0–9**, using authenticated
  original Japanese in-game digit glyphs $1041–$104A, capitals
  $1050–$1069, and the existing original-font/panel renderer.
- **Left/Right or Up/Down** changes the selected slot by exactly one.
  Slots wrap (0 ↔ 9). Gamepad D-pad also adjusts it.
- **Enter / gamepad A** confirms the selected slot, calling the
  **original pinned NESRecomp full-machine** `save_state_slot()` or
  `load_state_slot()` via JP0591's host `cviii_save_slot` variable.
  Original validation, netplay restrictions, save-path convention,
  success/failure notifications and state-loaded callback are kept.
- **Escape / Backspace / gamepad B** cancels only the slot chooser,
  returning to the paused Start/Pause action list **without touching
  any slot file or changing the current host slot**.
  **F4 / gamepad Start** closes the whole menu. A successful
  save/load closes the parent menu; on I/O failure the original host
  reports the failure and the player returns to the action list.
- The existing gameplay `Ctrl+0..9` quick-slot selection and F8/F9
  shortcuts remain unchanged; the chooser uses their same slot number
  mapping. The main menu still does not steal the gameplay Start key.

## Architecture and source changes

- [State component](../native/enhanced/cviii_slot_picker_0625.h) and
  [implementation](../native/enhanced/cviii_slot_picker_0625.c):
  `CviiiSlotPicker`, `cviii_slot_begin/step/cancel/accept`. Independent
  of SDL, operating system, filesystem, CPU/mappers/PPU/APU, and
  game-input timing. Rejects invalid actions, stale/invalid slots,
  movement while closed and null confirmation pointers.
- [Game adapter](../native/enhanced/cviii_edition.c) exposes
  `cviii_pause_slot_*` to the pinned native host, retaining the existing
  register-based four core action IDs and mod-forward action seams.
  The slot state is separate from savestates, cancels on Original
  diagnostic selection, power-on, load-state and parent menu close.
- [Original font renderer](../native/enhanced/cviii_start_ui_0623.c)
  draws the slot number, page title, adjust/confirm/back prompts using
  the JP0619 owner-authenticated private CHR index. It writes only to
  a copy of the 256×240 presented framebuffer, never NES VRAM or game RAM.
  Colors are preview approximations pending exact live original palette
  matching. Missing authenticated CHR fails closed.
- [Sixth private SDL source overlay](../tools/patch_cyc_slot_picker_0625.py)
  operates on the **already pinned/generated fifth** JP0623 overlay:
  JP0591 → JP0594 → JP0596 → JP0620 → JP0623 → **JP0625**.
  It replaces immediate Save/Load actions with a slot submenu, intercepts
  child keys/gamepad buttons before parent controls, and calls the
  **unchanged original host** Save/Load functions only on confirmation.
  The untouched pinned NESRecomp source and original copyrighted ROM
  are not committed to public Git.
- [Six-layer source gate](../tools/jp_slot_picker_pinned_gate_0625.py)
  authenticates the original pinned SDL Git blob and applies all six
  patchers in memory; checks the original serializer, slot number
  integration, modal precedence and pause/hold-input predicates.
- [Generated SDL shell regression](../tools/jp_slot_shell_test_0625.py)
  imports the actual sixth-layer patch source and builds a ROM-free C11
  simulation in offline and netplay compilation modes to test child
  selection, 0/9 wrap, cancellation, no immediate save/load and modal
  input isolation.
- CMake and both Linux/Windows workflows now compile/run the isolated
  slot-state and original-font renderer tests, plus Python smoke and
  six-stage pinned SDL source checks. Linux additionally invokes the
  generated SDL shell C11 integration test.

## Evidence actually verified in this phase

**PASS, executed locally in strict GCC C11**, with exact committed
Git blob SHA matching all authored files:
1. `cviii_slot_picker_0625.c` + `cviii_slot_picker_test_0625.c`
   (`-std=c11 -O2 -Wall -Wextra -Werror -pedantic`):
   valid Save and Load, 0 ↔ 9 wrap, invalid actions/slots,
   null-pointer safety, cancel/back and closed-menu suppression.
2. `cviii_start_menu_0623.c` + `cviii_start_ui_0623.c` +
   `cviii_slot_picker_0625.c` +
   `cviii_start_ui_test_0623.c` with the same strict flags:
   original glyph mapping for SAVE/LOAD title and slot numerals,
   panel bounds, foreground color and presentation-only behavior.

**Committed but NOT executed/confirmed locally:**
- Exact sixth-layer Python `--smoke` and real upstream pinned SDL
  six-stage patch generation.
- Exact generated-shell C11 integration script offline/netplay.
- GitHub Actions results and a rebuilt real Windows SDL executable.
- Gameplay pause/resume, physical controller events, actual native
  ten-slot save/load I/O, and host config/asset round-trips.

**Open design work:** audio submenu Back-to-Start, configurable menu-open
controller binding (without stealing NES Start), mod data-pack loader,
editor/level schemas and independent Music/SFX audio mixing. The user’s
[universal mod-forward standard](../../MOD_FORWARD_METHODOLOGY.md)
remains governing policy; JP0625 deliberately adds no fixed global
slot file format or new game-state serialization path.

**Certification accounting unchanged:** verified strict semantic PRG
49,504/262,144 bytes (18.8843%), VPP 27/100, certified checkpoint
0508, fixed frontier $FB96; `JP/analysis/RESUME_STATE.json` untouched.

**Next bounded phase JP0626:** authenticate/compile the full private
six-stage SDL overlay on the pinned NESRecomp Windows build, validate
real pause/input/slot I/O and then complete Audio→Start/Pause Back
navigation and configurable gamepad opening without gameplay leakage.
