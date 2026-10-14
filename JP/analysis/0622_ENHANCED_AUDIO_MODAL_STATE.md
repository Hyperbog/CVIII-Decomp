# JP0622 — Testable native Enhanced F6 menu controller

**Goal:** remove the F6 Audio menu's open/close/selection/volume logic from a
large host callback implementation, while retaining the original Japanese
gameplay baseline, the authentic private CHR renderer and the existing
JP0620 SDL pause/input shell. This is a **bounded refactor with behavior
tests**, not the future unified Start/Pause menu.

## Implemented

The independent [C11 audio-menu controller](../native/enhanced/cviii_audio_menu_state_0622.c)
takes two explicit, presentation-only inputs: whether Enhanced is active and
whether the authenticated original CHR asset index is present. A closed menu
opens only if both are true; an already-open menu may always close. Opening
resets selection to the Master row for consistent navigation. Selected row
order is Master → Music → SFX, Up/Down wraps and Left/Right adjusts exactly 1%
with no change outside 0–100. Row selection alone does not require a settings
write. An invalid input command, invalid selected row, null object or closed
menu cannot change any volume. Music and SFX still only store preferences:
**independent sound-source mixing remains unimplemented**.

The actual [Enhanced edition host](../native/enhanced/cviii_edition.c)
delegates its exported `cviii_audio_menu_active/toggle/close/move` API to
this tested module. The public SDL-adapter ABI and its original-art rendering
remain the same. We additionally close the modal when a new machine power-on
occurs, an emulated state is loaded, or the engineering-only Original mode is
selected. This prevents modal selection state surviving a gameplay reset
without altering any CPU/PPU/APU state.

CMake includes the controller in the playable Enhanced host target. It also
adds the standalone `jp_audio_menu_state_test_0622` target. The Linux
NESRecomp CI host source compilation now links the controller, and both Linux
and Windows CI run the standalone regression (ROM-free).

## Local execution evidence

**PASS — actually compiled and executed in this environment:** strict
GCC C11 `-std=c11 -O2 -Wall -Wextra -Werror -pedantic` of the
**exact committed** JP0622 controller and test plus the **exact committed**
JP0618 volume-level implementation and header. Confirmed the Git blob hashes
of all five locally compiled source files matched the authoritative remote
`decompilation` branch. Command:

```sh
cc -std=c11 -O2 -Wall -Wextra -Werror -pedantic \
  JP/native/enhanced/cviii_audio_levels_0618.c \
  JP/native/enhanced/cviii_audio_menu_state_0622.c \
  JP/native/enhanced/cviii_audio_menu_state_test_0622.c \
  -o /tmp/jp_audio_menu_state_test_0622
/tmp/jp_audio_menu_state_test_0622
```

The regression covers refusal to open without Enhanced or authenticated CHR,
null-state safety, Master/SFX cyclic row navigation, 1% Music/SFX/Master
adjustments, held/closed-menu suppression at the controller API boundary,
deterministic re-entry, 0/100 clamp, invalid command/row rejection and
closed-menu reset during gameplay load/edition changes.

**Not executed/verified:** complete private pinned-NESRecomp CMake build,
Windows SDL runtime and controller hardware, real frame pause/release
behavior, old save-state compatibility replay, current Actions results,
original PPU palette identity and native gameplay/audio recording. The
JP0621 source-chain gate remains required for these integration checks.
No claim of a fully functioning shipping UI or independent Music/SFX mixer
follows merely from an isolated passing controller test.

## Remaining integrated-menu work

The user-requested **expandable Start/Pause menu** eventually groups
Save State, Load State, Audio and Quit through stable action IDs with
future mod registration. Existing F6 Audio remains independent; the
current numeric-setting registry is not a complete menu page registry.
Do not introduce arbitrary mod executable loading or break baseline
gameplay while designing the unified UI. The master sound gain remains
functional in source; separate Music/SFX voice buses remain necessary.

**Certified source-ledger unchanged:** semantic PRG **49,504 / 262,144**
(18.8843%); VPP **27/100**; checkpoint **0508**; frontier **$FB96**;
`JP/analysis/RESUME_STATE.json` unchanged.
