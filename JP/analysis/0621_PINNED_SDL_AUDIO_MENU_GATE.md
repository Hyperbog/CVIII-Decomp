# JP0621 — Actual pinned SDL source / F6 audio menu integrity gate

**Bounded objective:** Validate the JP0591 → JP0594 → JP0596 → JP0620
Enhanced F6 audio menu source-generation path **against the exact upstream
NESRecomp SDL file**, rather than treating earlier synthetic overlay
fixtures as complete evidence. Original gameplay remains the default;
Enhanced is the only shipping edition. All mod-forward architecture
policies remain in force.

## Verified upstream source identity and statically checked prerequisites

Pinned external dependency: `mstan/nesrecomp` commit
`2b4fcdb98c9e702be3fb365cfc645003c50b5fc1`,
`runner/cyc/cyc_sdl.c`, Git blob SHA-1
`a10d0fce1d1e568a2ef672738cbee7eded323fdb`.

Read-only GitHub inspection of that actual source confirms **exactly one**
occurrence of each key original upstream anchor: window save-path
constructor, save/load UI toast, SDL_KEYDOWN event branch, standalone
`save_state_slot`, `cyc_ui_render`, frame-loop `bool open` and
`open = menu_open()`, Quick Save/Load guards, gamepad-menu nav,
frame execution gate `online || (!open && !inactive)`, and host
audio output call `cyc_session_audio_mix(pcm,n)`.
This proves the **first-layer source compatibility prerequisites**,
not a completed compiled four-overlay build.

## Added source-chain contract

[JP0621 verifier](../tools/jp_audio_menu_pinned_gate_0621.py):

- Reads only a user-supplied copy of the **pinned, unmodified** upstream SDL
  source. Applies **only** Git's reversible Windows checkout CRLF→LF
  normalization, rejects unexpected bare CR, and checks the exact committed
  Git blob identity. Any other altered upstream content fails even if the
  patch anchors still match.
- Imports the **actual committed** 0591/0594/0596/0620 Python patchers and
  calls their real `generate` functions in order, without writing source
  output, and invokes JP0591's original validator.
- Requires exactly one final modal adapter include/keyboard handler/D-pad
  handler, presence of the 0591 save-slot and 0594 stage/password layers,
  and preservation of all expected host frame gating and PCM pathways.
- Inspects **event interception order**: the F6 audio handler must receive
  the event before the F10/debug password handler, which must precede
  `CYC_DEV_UI`'s `dev_key` handler. When F10 stage debug is open,
  the F6 audio handler explicitly defers so the original password
  checkpoint capture shortcut still works.
- Checks that the final `open` frame gate includes `cviii_audio_menu_active`,
  the upstream `was_open`/held-key input-release barrier remains intact,
  save/load shortcuts are suppressed while the modal is active, queued
  audio clears at pause and Left/Right changes are saved.
- Has a ROM-free `--smoke` fixture, plus a separate required **actual
  pinned-source** run. The smoke fixture is not used as a substitute
  for the real source file.

### Reproduction

From the repository root, after obtaining the pinned external checkout:

```sh
python3 JP/tools/jp_audio_menu_pinned_gate_0621.py --smoke
python3 JP/tools/jp_audio_menu_pinned_gate_0621.py \
  --source _external_nesrecomp/runner/cyc/cyc_sdl.c
```

Both the Linux mapper24 and Windows Alpha CI workflows now run these
commands **before** the build. The gate fails closed if an upstream
revision changes, if any intermediate patch cannot apply, or if the
pause/interception checks fail. It neither copies the external SDL
implementation into Git nor distributes original JP ROM contents.

## Honest execution limits

**Verified in this phase:** exact upstream source Git blob identity and
presence/uniqueness of expected original anchor strings via connected
GitHub source inspection; Python gate source and Windows/Linux workflow
steps committed. Previous JP0620 C11 registry and standalone patcher
synthetic tests exist.

**Not verified here:** local execution of the **complete** Python chain on
the actual external file, new GitHub Actions run result, compiled generated
SDL host, gamepad/keyboard interactions in a real window, the visible
paused 256×240 CHR menu in the actual PC executable, two-launch preference
persistence, game-frame freeze and state-load behavior on actual hardware.
These checks remain required before a playable alpha is declared
validated.

No player-facing features were added in JP0621. JP0620 F6 audio options
remain the last implementation; original Master PCM gain works by code
inspection and prior synthetic tests, while Music/SFX remain persisted
but **not** independently mixed. Start/Pause Save/Load/Quit and general
mod-content loader/editor remain planned, not implemented.

**No certification advancement:** strict semantic PRG
**49,504/262,144 (18.8843%)**; VPP **27/100**; checkpoint **0508**,
fixed frontier **$FB96**; `JP/analysis/RESUME_STATE.json` unchanged.

## JP0623 correction — Intermediate developer-key precedence

The historical JP0621 description above called the four-stage SDL keyboard
priority validated. Inspection in JP0623 showed that the **pinned
`CYC_DEV_UI` handler actually runs first in the JP0620 four-stage
intermediate source**. This is a real integration issue, not a gameplay
claim: `jp_audio_menu_pinned_gate_0621.py` now verifies and exposes that
intermediate order rather than incorrectly asserting the intended one.
The [JP0623 fifth-layer overlay and source gate](0623_MOD_FORWARD_START_PAUSE_MENU.md)
move the developer handler behind F4 Pause, F6 Audio and F10
password/debug dispatch. Native Windows gameplay acceptance still
requires the actual five-layer SDL build/test.
