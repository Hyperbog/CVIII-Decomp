# JP0623 — Extensible Enhanced Start/Pause menu, original JP font

**Status:** native Start/Pause action registry, original-font renderer, C11
tests, five-stage pinned SDL integration overlay and CI gates **committed**.
The two independent ROM-free C11 tests **PASS locally using exact committed
source blobs**. The full pinned private SDL overlay and Windows Alpha
gameplay have **not** been compiled/executed locally; CI outcomes have not
been independently checked. Do not represent this as a certified player
release.

## Intended player interface

With the **Enhanced** windowed game and its authenticated owner-local
`CVIII-CHR-Index.dat` loaded, **F4** opens an independent paused
Start/Pause menu. **Up/Down** selects an action, **Enter** accepts and
**Escape/Backspace/F4** closes. Once open, controller D-pad Up/Down
navigates, A accepts and B/Start closes. Opening via a gamepad is **not
bound yet**, deliberately preserving the game's ordinary NES Start
control during gameplay. A configurable controller shortcut belongs to
a future integrated Controls menu.

Initial game-owned stable actions:

| ID | Display | Current host action |
|---|---|---|
| `core.save_state` | SAVE STATE | Call the pinned host's existing full-machine save-state handler, **current selected slot** |
| `core.load_state` | LOAD STATE | Call the pinned host's existing full-machine load-state handler, **current selected slot** |
| `core.audio` | AUDIO | Close Start/Pause; open the existing original-healthbar F6 audio panel |
| `core.quit` | QUIT | Require a second Accept while selected, then request normal host exit |

**Not yet built:** a graphical save-slot chooser, title-screen Start menu,
configurable menu-open controller binding, audio submenu Back-to-Start
navigation, public mod package loader, editor, new enemy/level resource
format, independent Music/SFX audio buses, exact original PPU palette
colors. Existing `Ctrl+0..9` slot selection and F8/F9 shortcuts remain
usable from gameplay and use the same full-machine serializer.

## Mod-forward architecture boundary

The [C11 Start/Pause registry](../native/enhanced/cviii_start_menu_0623.h)
uses symbolic namespaced IDs, typed action enums, optional enabled
predicates, a maximum of 32 entries with duplicate rejection,
lowercase-safe ID validation, and a sealed initialization boundary.
Only built-in default initialization installs the privileged
`core.save_state`, `core.load_state`, `core.audio`, `core.quit`
IDs. Future extensibility uses `CVIII_START_EXTENSION`; it cannot
silently impersonate privileged Save/Load/Quit by registering a different
name. The current game host initializes and seals four entries; external
mod resource loading and actual callable extension handlers are **not**
implemented. Renderer/navigation is **not fixed to four entries**;
the renderer scrolls a six-row viewport.

The [pure presentation renderer](../native/enhanced/cviii_start_ui_0623.c)
draws the 8x8 original JP CHR in-game font from the owner-authenticated
cache (numerals `$1041–$104A`, capitals `$1050–$1069`) onto a
256x240 frame copy. The panel and text drawing are clipped so a future
long mod label cannot leak onto pixels outside the panel; no emulated PPU
register, CPU frame, palette state or gameplay RAM is altered.
Orange/white RGB values are still *provisional* until certified against
the original in-game PPU palette.

The [game-owned adapter](../native/enhanced/cviii_start_host_0623.h)
exposes only open/close/navigate/accept and an action enum. It does **not**
know SDL paths or invoke file I/O, audio mixing or save serialization.
The existing [JP0620 audio state controller](../native/enhanced/cviii_audio_menu_state_0622.c)
continues to own all three 1% volume preferences. Master gain currently
works; Music and SFX remain stored-only until independently mixed.

## Pinned SDL integration

The new [JP0623 SDL overlay](../tools/patch_cyc_start_menu_0623.py)
adds a fifth private, staged patch to the pinned NESRecomp source:
0591 save slots → 0594 F10 stage/partner → 0596 original password
bootstrap → 0620 F6 audio → **0623 F4 Start/Pause**. The actual
SDL functions `save_state_slot` and `load_state_slot` are called
from host action dispatch. Those route to `save_state_to` /
`load_state_from`, which already refuse online save/load, validate
the whole-machine format and announce failures. Quit uses the normal
window exit flag; the registry requires two confirms.

**JP0632 source-order correction:** The earlier claim that the
CYC_DEV_UI handler ran before F6 and F10 in the four-layer JP0621
build was incorrect. The pinned SDL source and actual patch insertions
put F6 Audio → F10 password/debug → developer shortcuts in that order.
The fifth JP0623 overlay adds F4 Start/Pause ahead of these, resulting
in F4 → F6 → F10 → developer shortcuts. The original dev-first
JP0621 assertion was an audit error (C category), now corrected.
The [five-layer gate](../tools/jp_start_menu_pinned_gate_0623.py)
still checks final priority and original source identity.

The host's existing frame `open` predicate includes the new modal
and continues to gate CPU frames, controller input forwarding, and PCM
queueing. The original `was_open` / `hold_input` release barrier
remains intact. F4/Start/Pause and F6 cannot open over one another,
F10 debug is not hijacked, and save/load shortcut actions are guarded
while a modal owns input. Existing queued PCM is cleared at menu-open
via the JP0620 transition flag. Default core game frame timing is not
intentionally changed while menus are closed.

## Tests and evidence boundary

- **Actually run, PASS:** strict GCC C11 `-std=c11 -O2 -Wall -Wextra
  -Werror -pedantic` Start/Pause registry regression from
  `cviii_start_menu_0623.c` +
  `cviii_start_menu_test_0623.c`, **exact Git blob hashes match
  committed sources**. Covers core IDs, 32-entry capacity, extension
  registration, namespace and privilege spoof rejection, enabled
  predicates, select/wrap, save/load/audio action routing, quit
  confirmation, and closed-menu suppression.
- **Actually run, PASS:** strict GCC C11 original-font renderer
  regression from `cviii_start_menu_0623.c`,
  `cviii_start_ui_0623.c`, and
  `cviii_start_ui_test_0623.c`; **exact Git blob hashes match**.
  Checks missing authenticated CHR fallback, framebuffer size refusal,
  selected-row colors, quit confirmation text, and framebuffer canaries.
- **Committed, not executed here:** Linux and Windows CI test
  targets for both C11 cases, synthetic patcher smoke, and the
  five-layer *actual pinned SDL file* static gate. CMake generates
  the final private overlay on the existing windowed build path.
- **Not verified:** complete actual pinned 5-stage Python execution,
  native SDL C11/CMake link on owner Windows, precise gamepad input,
  pause/resume frame behavior in a running game, loading slots through
  the Start menu, save/load compatibility, automatic settings persistence
  between separate launches, and RGB PPU color fidelity. No original
  ROM or private upstream SDL source was committed to public Git.

## Next bounded phase

JP0624: validate or fix the full pinned Windows host build and playable
keyboard/controller Start/Pause; then replace the temporary F4 shortcut
with a configurable player-safe menu binding, add proper Save/Load slot
selection and Back-to-Start Audio navigation. Introduce externally
validated additive page registration only once a versioned mod data
loader and permissions policy exist. Do not change original gameplay
mechanics to implement UI.

**Certified decompilation ledger unchanged:** 49,504 / 262,144 strict
semantic PRG bytes (18.8843%), VPP 27/100, certified checkpoint 0508,
fixed frontier `$FB96`. No `JP/analysis/RESUME_STATE.json` update.
