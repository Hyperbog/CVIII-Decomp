# JP0626 — Nested Audio screen returns to Start/Pause without resuming gameplay

**Status:** JP0626 parent/child menu ownership and seventh private SDL overlay
implemented and committed; exact source C11 unit and Python patch smoke
**PASS locally**. Authentic seven-layer pinned-source generation, GitHub
Actions outcomes, Windows SDL compile/link and real gameplay remain
**unverified**. This phase does **not** claim a fully certified PC Alpha.

## Player-facing behavior

In Enhanced with the owner-authenticated private Japanese CHR index:

1. Press **F4** to open Start/Pause, navigate to **Audio**, press Enter
   (or gamepad A if already in the Start/Pause menu).
2. The authentic health-meter/font Audio screen opens **without discarding
   the parent menu state**. Keyboard/controller Up/Down and 1% Left/Right
   remain exclusive to Audio, and gameplay remains frame-paused.
3. Press **F6**, **Escape**, **Backspace**, gamepad **B** or **Start** to
   close the Audio child. The original-font **Start/Pause menu returns
   on the Audio row**, and the host continues to hold gameplay paused.
4. Exit Start/Pause with **F4**, **Escape** or gamepad **B/Start** to
   restore normal gameplay after the host's held-key release barrier.
5. **Direct F6 Audio from gameplay** still closes directly to gameplay.
   The main Start/Pause page is not fabricated in that case.

The prior graphical Save/Load 0–9 slot selector, confirmation flow,
double-confirm Quit and gamepad navigation remain as implemented at JP0625.
The F4 keyboard open binding remains temporary; ordinary gamepad Start is
still an original-game input during gameplay. Master volume affects PCM,
Music/SFX remain **saved preferences only** pending separate voice buses.

## Runtime design

The pure C11 [menu-stack interface](../../recomp/native/enhanced/cviii_menu_stack_0626.h)
and [implementation](../../recomp/native/enhanced/cviii_menu_stack_0626.c)
accept a resident `CviiiStartMenu` and an independent
`CviiiAudioMenuState`. They report the **focused** parent only while
the parent is open and the Audio child is closed. Entering Audio via the
parent sets only the Audio state and leaves the parent selection unchanged;
a standalone F6 Audio session does not create a parent. Entry requires
Enhanced plus authenticated private CHR, with no guest CPU/PPU/APU/RAM
mutations.

The actual Enhanced [host adapter](../../recomp/native/enhanced/cviii_edition.c)
now delegates `cviii_pause_active` and
`cviii_pause_audio_enter` to those functions, stops parent
navigation/actions while the child owns focus, guards the slot
submenu against Audio ownership and prefers **the active child
renderer** to the parent original-font presentation. Reset/edition
switch/savestate load continue to close both pages. Existing original
Japanese-font and health-meter tiles are used; no copyrighted asset
bytes are committed.

The [seventh generated SDL overlay](../../recomp/tools/patch_cyc_audio_return_0626.py)
runs after JP0591 slots → JP0594 F10 debug → JP0596 password →
JP0620 F6 Audio → JP0623 F4 Start/Pause → JP0625 slot picker.
It replaces the Start/Pause Audio action's old `cviii_pause_close()`
with `cviii_pause_audio_enter()`. It also fixes the **inline F6
event-batch `open` recomputation** to include
`cviii_pause_active()` immediately after the Audio child closes:
that prevents an intermediate `open=false` from leaking subsequent
controller/window events into gameplay before the end-of-loop pause
predicate recomputes. The original upstream host's CPU frame pause,
PCM suppression, queued-audio drain and held-button release barriers
remain the only simulation control; no parallel emulator loop exists.

The source patch refuses drifted/missing/duplicate prior-layer anchors.
[JP0626 full-source gate](../tools/jp_audio_return_pinned_gate_0626.py)
authenticates the pinned unmodified NESRecomp SDL Git blob and actually
runs all seven ordered Python patchers in memory, requiring final parent
ownership, original slot menu/save/load actions and intact host pause
predicates. Both Linux and Windows workflows now invoke its smoke and
pinned-source modes before the native build. CMake selects the
**seventh** generated source as the final private SDL overlay.

## Actual tests versus unverified checks

**PASS locally**, `gcc -std=c11 -O2 -Wall -Wextra -Werror -pedantic`:

```sh
cc -std=c11 -O2 -Wall -Wextra -Werror -pedantic \
 JP/recomp/native/enhanced/cviii_start_menu_0623.c \
 JP/recomp/native/enhanced/cviii_audio_levels_0618.c \
 JP/recomp/native/enhanced/cviii_audio_menu_state_0622.c \
 JP/recomp/native/enhanced/cviii_menu_stack_0626.c \
 JP/recomp/native/enhanced/cviii_menu_stack_test_0626.c \
 -o /tmp/jp0626_stack_test
/tmp/jp0626_stack_test
```

Original Japanese source-specific and synthetic cases exercised:
normal F6 Audio open and close with no parent; F4 parent selection
persistence across nested Audio; disabled Enhanced/missing CHR rejection;
independent Music volume stored in 1% steps (not mixer parity); parent
not receiving focus while Audio is open; 1% state continuity after Back;
null, duplicate-entry and return-to-gameplay cases.

All **nine locally compiled header/C files** were checked with Git blob
identity, including new JP0626 header/implementation/test matching the
current committed Git sources. No original ROM input was required.

**PASS locally**:

```sh
python3 JP/recomp/tools/patch_cyc_audio_return_0626.py --smoke
```

The patcher's exact bytes matched the committed Git blob. It checks
child entry replacement, recompute of same-event `open`, and refusal
to apply twice or with changed anchors.

**Committed but not actually executed here:** seven-layer whole-upstream
`jp_audio_return_pinned_gate_0626.py --source`, CMake/SDL compiled
full native Windows target, Linux and Windows CI steps. Exact runtime
real keyboard/controller event ordering, pause/resume, saved settings
across launches, ten-slot file I/O and VRC6 game audio recording still
require owner/runner QA. Static and isolated tests are not gameplay
parity certificates.

**Next bounded work:** authentic pinned SDL full-source compilation and
Windows Alpha F4→Audio→Back→F4 gameplay verification; then configurable
gamepad opening shortcut and mod-data extensibility. Keep all new
source-specific adapters behind the shared
[mod-forward standard](../../../MOD_FORWARD_METHODOLOGY.md).

**No certification change:** strict semantic PRG
**49,504/262,144 (18.8843%)**, VPP **27/100**, checkpoint **0508**,
fixed frontier **$FB96**; `JP/decomp/analysis/RESUME_STATE.json` unchanged.
