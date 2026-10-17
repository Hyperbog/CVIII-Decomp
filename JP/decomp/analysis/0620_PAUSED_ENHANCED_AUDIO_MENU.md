# JP0620 — Paused, interactive Enhanced audio options using original tiles

**Status:** native C11/SDL implementation and ROM-free unit/patcher checks committed;
**not yet privately rebuilt and exercised on a real Windows AlphaCandidate**.
This is a bounded audio-options slice, **not** the planned expandable Start/Pause
screen, mod loader or editable level-system overhaul.

## User-visible contract

The **Enhanced** player can open the original-CHR audio screen with **F6**
in windowed builds using the JP0620 native host overlay. The authentic private
`CVIII-CHR-Index.dat` is required. It is extracted by the owner's private
build from the SHA-authenticated original Japanese ROM. No copyrighted ROM or
original CHR data is committed to the repository.

| Control | Keyboard | Gamepad |
|---|---|---|
| Open Audio | F6 (keyboard) | Not bound yet |
| Select Master/Music/SFX | Up / Down | D-pad Up / Down |
| Adjust by exactly 1% | Left / Right, including held-key repeat | D-pad Left / Right |
| Close and resume | F6, Escape, Backspace | B or Start |

**0–100%, step 1, defaults 100%.** Master attenuates the final native PCM;
Music and SFX still save preferences **without** independently attenuating
voices, because separate source buses do not yet exist. The original-art modal
displays **MUSIC SFX PENDING** to avoid misleading the player. The original
health-meter CHR tiles (filled `$1093`, empty `$1085`) and original in-game
font (`$1041–$104A` digits, `$1050–$1069` capitals) come from the
authenticated JP0619 asset cache. Palette RGBs are provisional and not yet
certified against a live original PPU-frame palette.

The original `--audio-ui-preview 1` developer-only, noninteractive render
remains available separately; no preview option is required to use F6.

### Why this is not another gameplay loop

The pinned NESRecomp SDL host already uses a Boolean `open` gate to pause
`cyc_run_frame()`, omit controller forwarding and drop newly generated PCM
when the runtime/debug menu is open. The owner-local
[JP0620 patcher](../../recomp/tools/patch_cyc_audio_menu_0620.py) extends the **existing**
Boolean with `cviii_audio_menu_active()` without patching any 6502 or
copyrighted ROM bytes. It layers after JP0591 save slots, JP0594 F10 stage
debug and JP0596 password bootstrap, and refuses missing or modified
source anchors. The upstream SDL library and its source are not vendored.
The generated C code lives only beside the privately pinned external build.

The input owner is the modal when active. F6 uses a nonrepeating toggle;
Up/Down selects one of three rows, Left/Right adjusts in ±1 steps,
the game-owned C11 control API updates the selected gain, and the SDL host
calls its normal `save_settings()` when a value changes. Game frames do
not advance while `open` is true; the host's preexisting `hold_input`
release barrier is reused after closing, preventing a held menu direction
or pad B from entering gameplay. Existing quick-save/quick-load keyboard
shortcuts are suppressed while F6 owns the menu. Queued SDL audio is
cleared at the opening event, preventing an old sound tail at pause.
F6 is blocked in netplay. If Enhanced or the authenticated private CHR
index is unavailable, the menu refuses to open.

The original graphic is composited into a **presentation framebuffer copy**;
no NES PPU, mapper, collision/physics, RAM, CPU cycle, audio register or
cartridge state changes. A successful native savestate load clears stale
modal ownership. The game-owned modal state is outside emulated savestates.

### Extension architecture

[JP0620 C11 registry](../../recomp/native/enhanced/cviii_menu_registry_0620.h)
defines a bounded, namespaced setting registration API with duplicate-key
rejection, range and step validation, stable labels/sections and a sealed
initialization boundary. When an optional `recomp-ui` host is present,
three interactive audio rows are added using this registry, along with
the host's existing Save State, Load State and Quit actions. The runtime
does **not** require recomp-ui for the **F6 original-art audio modal**:
the CMake-managed SDL patch applies when the game host extras are enabled,
even for `-DNESRECOMP_RECOMP_UI=OFF` (as in public Windows CI).

This registry is **not a general menu page/action registry yet**, and
there is **no data mod loader** or safe external mod registration API
implemented. Save/Load/Quit are still the host's own controls, not yet
presented together in a unified custom Start/Pause screen. Keep the
[universal mod-forward methodology](../../../MOD_FORWARD_METHODOLOGY.md)
and [game-specific architecture plan](../../recomp/docs/ENHANCED_MODDING_ARCHITECTURE.md)
as next-phase design contracts.

## Tested, untested and limits

1. **PASS, verified on local GCC C11:** exact committed JP0620
   registry source + exact committed test (matching Git blob hashes), with a
   compatible local JP0618 gain API implementation. Cases include valid
   1-percent values, bounds, duplicates, missing IDs, reserved namespaces,
   bad step values, sealed registration.
2. **PASS, verified on local Python:** exact committed
   `patch_cyc_audio_menu_0620.py --smoke` source (matching Git blob SHA).
   Verifies F6 interception, controller navigation, host pause predicates,
   menu-shortcut guard, save after gain adjustment, SDL queue clear, and
   rejection of corrupted or already-patched synthetic host inputs.
3. Existing JP0618/0619 ROM-free numeric/graphics tests are linked into
   Linux and Windows CI; JP0620 adds new smoke/test steps. The JP0619
   render test includes the interactive original-font pending-mixer warning
   and close hint.
4. **NOT tested in this environment:** actual generated JP0596→JP0620
   overlay against the pinned full upstream SDL source, Windows C11 window
   build/link, SDL keyboard/gamepad controls, visual game-frame pause,
   user settings round-trip across two real launches, exact palette colors,
   netplay behavior and full-game gameplay/sound parity. The real private
   Windows AlphaCandidate must be rebuilt and owner-tested.
5. The optional recomp-ui path is **not** exercised in CI, which explicitly
   passes `-DNESRECOMP_RECOMP_UI=OFF`. The independent F6 SDL modal path
   is compiled by the window CMake target and should be verified in actual
   Windows builds; do not infer an Actions result without checking runs.

**Decompilation accounting unchanged:** strict semantic PRG
**49,504/262,144 (18.8843%)**, VPP **27/100**, certified checkpoint
**0508**, fixed frontier **$FB96**. No changes to
`JP/decomp/analysis/RESUME_STATE.json`, original licensed media, reference
tests or goldens.

**Next bounded phase:** owner Windows F6 game-frame/keyboard/controller
QA; then the extensible combined Start/Pause menu with action/page IDs
(Save State, Load State, Audio, Quit) and authentic visual theming.
Independent Music/SFX source buses remain a separate audio architecture
project before their saved gains can affect playback.
