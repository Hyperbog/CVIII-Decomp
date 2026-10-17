# JP0661 — Native recompilation keyboard controls profiles

**Workstream:** the existing playable Windows C11 NESRecomp/SDL2 native
Enhanced Edition, **not** partial semantic decompilation. This feature
uses the pinned external NESRecomp (revision
`2b4fcdb98c9e702be3fb365cfc645003c50b5fc1`) host's real
`cyc_settings.c` sections `[Keyboard.Player1]` and
`[Input]` `Player1Source`, and its `cyc_input.c` physical
SDL scancode names. NESRecomp already supports persistent controller
binding editing through its upstream UI. This improvement adds **named
owner-local Player 1 keyboard profiles, conservative switching and
recovery** without duplicating that input system.

## Player-facing behavior

A freshly packaged build kit or the private owner-built
`AlphaCandidate` now contains:

- `Controls.bat` — menu for default NES keyboard keys, WASD
  keys, save the currently configured eight Player 1 keys into a
  named profile, select a saved profile or leave everything unchanged.
- `Controls.ps1` — direct noninteractive
  `-Action List|Show|Save|Apply -Profile NAME` support.
- `Control-Profiles.py` — original schema-checked INI/JSON editor;
  no SDL, original Japanese ROM, game art or CPU/PPU code.
- `Build-And-Play.bat -ControlsProfile wasd` — opt-in selection before
  NESRecomp loads `config.ini`. The normal Play-CVIII.bat and launcher
  path use **the user's existing settings unchanged**, with no hidden
  default remapping. Private `Launch-Alpha.ps1 -ControlsProfile NAME`
  is also supported.

Run **once** to let the native game generate the existing
`config.ini`, exit the game, then run `Controls.bat`. Apply changes
only while the game is closed. The profile manager selects keyboard
`Player1Source=1`; users can switch back to gamepad via the existing
NESRecomp launcher/input settings.

The built-in profiles:

| NES button | Original default | WASD |
| --- | --- | --- |
| A | Z | J |
| B | X | K |
| Select | Backslash | Right Shift |
| Start | Return | Return |
| Up | Up | W |
| Down | Down | S |
| Left | Left | A |
| Right | Right | D |

The manager only updates this eight-key section and the existing
`Player1Source` input key. It **never changes** Player 2, gamepad
bindings, host shortcuts, graphics/audio options, game volume, machine
save-state files, ROM bytes or the emulator's 6502/PPU/IRQ code.

## Error and recovery contract

- The user may capture a named active keyboard profile into
  `control-profiles/NAME.json`, versioned
  `cviii-native-keyboard-profile/v1`. Custom names use lowercase
  letters, digits, underscores or hyphens only; built-in names
  `default`/`wasd` are protected. Existing profile files are
  not overwritten.
- A successful change **first writes** the complete previous
  `config.ini` byte sequence to a uniquely named
  `control-backups/config-*.ini.bak` and **atomically replaces**
  only the settings file. Restore an earlier backup manually while
  the game is closed if any unwanted settings change occurs.
  The `default` profile restores stock Player 1 NES keys,
  but does **not** discard unrelated settings.
- Existing CRLF line endings, unrelated sections, keys and settings
  are retained. Exactly one of each input/binding source section
  is accepted; duplicate bindings or inconsistent/oversized/invalid
  settings fail **without** a settings rewrite.
- Duplicate mapped keys, unsupported SDL scancodes, and reserved
  menu/state/debug keys Escape/F4/F6/F8/F9/F10/F11/F12 are refused.
  Profiles are limited to existing engine-supported keyboard keys.
- There is **no in-game rebinding menu** created by this work, no
  gamepad-profile switcher, no arbitrary extended keyboard shortcuts,
  no running-game configuration reload, and no dependence on a
  commercial ROM. Owner Windows usability acceptance remains open.

## Native product verification

`JP/recomp/tools/test_control_profiles_0661.py` is an
**18-test actual-module regression** with entirely invented
`config.ini` content: canonical default and WASD states;
preservation of master volume, display preferences, Player 2
and F8/F9 shortcuts; exact original backup; original-key restore;
idempotence; unique custom save and profile reload; rejection of
invalid scancodes, menu keys, name traversal, duplicates,
source-section damage, oversized/unknown JSON and symlinks;
and missing-section reconstruction without losing nearby
settings. Strict Python module compilation and the ROM-free
Alpha builder packager also validate it.

Windows `jp_alpha_windows.yml` and Linux
`jp_nesrecomp_cycle_mapper24.yml` run the profile tests alongside
their existing synthetic-media C11 builds. `Build-Alpha.ps1`
copies all three profile tools to the **private executable's
directory**, and `package_alpha_builder_0580.py` includes
them in the **ROM-free** distributable builder kit.

Original-Japanese real Windows Owner keyboard UX remains to be
accepted; no synthetic CI run can certify user comfort or actual
controller-specific behavior. No semantic source VPP or strict
PRG credit: **31/100 VPP** and **49,504/262,144 strict PRG**
remain separate research metrics, unchanged by this product update.

## JP0661a — Windows coarse-clock collision correction

The first real Windows CI execution caught a defect not reproduced
by Linux: Windows `time.time_ns()` may return **identical
timestamps** on two immediately consecutive calls. Using only
the timestamp in a backup filename caused an `O_EXCL`
`FileExistsError` on the second profile change. **No existing
backup or owner config.ini was overwritten:** the fail-closed
operation aborted before atomic config replacement.

The corrected backup allocator uses an original timestamp plus
an **exclusive-create retry suffix** (0–99) and refuses to
change `config.ini` if no unique backup can be allocated.
The 18-test suite now deliberately forces `time.time_ns()` to
the **same fixed value on both sequential profile changes**,
asserting two preserved backups and successful WASD→default
restoration. The Windows product CI also parses all four
PowerShell entrypoint scripts before packaging acceptance.
Do not call the Windows build green until the corrected
workflow finishes successfully.
