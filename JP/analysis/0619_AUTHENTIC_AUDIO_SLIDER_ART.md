# JP0619 — Authentic health-meter graphics and numeric font for Enhanced audio options

**Product contract:** Ship Enhanced only, retain the original Japanese game's gameplay/physics/enemy/level timing as the baseline, allow deliberate tested enhancements. Confirmed UI: Master, Music and Sound Effects, 0–100% by 1%, original health-bar art as the slider and original in-game font for numbers. JP0618 persists three gain values and implements **only Master** postmix attenuation; music/SFX buses remain unsplit.

## Original ROM visual evidence

The uploaded owner-local Akumajou Densetsu ROM is 393,232 bytes, Mapper24, SHA-256
`958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`. Its CHR starts at file offset `$40010` and is a contiguous 131,072-byte archive of 8,192 planar 8×8 tiles. The [JP0619 source audit](../tools/jp_audio_ui_chr_0619.py) authenticates the whole ROM and four original raw-CHR tile-group SHA256 digests before emitting *only derived tile ID metadata*.

| Physical CHR tile indices | Authentication | Confirmed original visual function |
|---|---|---|
| `$1041–$104A` | `2738bea62342332fba08fff03f7d746f7de25dd93b5aac86d1cfac65a0a12a8c` | In-game pixel numerals `0–9` in ascending sequence |
| `$1050–$1069` | `a80bdb980cdf813ae757a6e354dde1f9b07c28828b09911afd98117f06d66e13` | In-game Latin capitals `A–Z` |
| `$1083–$1085` | `e4cf4857bc8e144726c4ef3d8732ea07798d7ed08820f831b06b61b46bcf576f` | Health-meter outline family, including empty double-cell tile `$1085` |
| `$1093–$1095` | `166f548ca0cdacfb9efd94cd6cc360cc995630c22262c073e432f990ed48fb40` | Health-meter filled family, including filled double-cell tile `$1093` |

Planar-source check: filled tile `$1093` first active row is color-index `2,2,2,0,2,2,2,0`; empty outline `$1085` is `3,3,3,0,3,3,3,0`. Both are exactly original tiles, *not* AI-generated, redrawn or substituted graphics. The current display RGBs (orange `#FF882C`, off-white `#F1EEEA`) are selected for preview and **have not been verified against a live original PPU palette at a captured frame**.

## JP0619 implementation

The [C11 pure presentation renderer](../native/enhanced/cviii_audio_ui_0619.c) overlays an 8-pixel-tile original-font panel on a copy of the already rendered 256×240 gameplay framebuffer. Three rows read `MASTER`, `MUSIC`, `SFX`, with an 18-tile-wide track of original empty double-segment health-bar graphics, filled left-to-right with the exact original filled tile pixels clipped to `round(144*value/100)` pixels. Right-aligned original-font numbers read 0–100; selected text is orange. The renderer leaves pixels outside the panel unchanged and never writes emulated memory, palette, PPU, sound hardware, timing or CPU state.

The native [Enhanced presentation hook](../native/enhanced/cviii_edition.c) exposes an **explicit developer-only, noninteractive** `--audio-ui-preview 1` option. It has no effect unless the owner-private, authentic `CVIII-CHR-Index.dat` has been loaded through JP0598's existing full-cache identity/planar check. If no authenticated CHR index exists, the presentation path is unchanged. The preview is **off by default**; it does **not** pause game execution, intercept controls, or alter audio gain.

The owner-private launcher optionally enables this static visual with `Launch-Alpha.ps1 -Edition Enhanced -AudioUiPreview`; it refuses missing CHR assets or the engineering-only Original diagnostic mode. The renderer is packaged in the native host build and tested in ROM-free Linux/Windows CI.

## Verification actually performed

- The JP0619 CHR audit PASS on the exact uploaded original Japanese ROM. ROM-free `--smoke` checks 2bpp planar decoding and rejection of invalid/short/wrong-ROM inputs.
- A strict GCC C11 test `-std=c11 -O2 -Wall -Wextra -Werror -pedantic` PASS using synthetic glyph/health-meter tiles: empty asset fail-closed, invalid framebuffer width/selection, 100/50/1/0 percent fill, color-highlight selection, authentic tile-ID mapping, preserved outside pixels and canary bounds.
- An independent private local preview image was rendered from the actual uploaded original ROM's decoded CHR pixels (example values 78/52/91), visually reviewed for letter alignment and health-meter tracks. Neither original image nor licensed CHR payload was committed.
- **Not executed here:** latest GitHub Actions CI run, rebuilt private Windows AlphaCandidate/GUI, in-game menu input controls, pause during menus, live original-HUD palette, and independent music/SFX attenuation.

### Next bounded component

JP0620: integrate a safely paused player-facing audio menu, Up/Down selection and Left/Right 1%-step controls, reliable controller/keyboard input isolation, persisted settings and no accidental gameplay movement while menu is open. Avoid shipping the preview as the final menu. Independent Music/SFX host buses remain an additional separate prerequisite for functional non-Master gains.

**Accounting:** No new strict semantic PRG bytes, no VPP points, no ROM or PCM mixer modifications. Strict total **49,504/262,144 (18.8843%)**; VPP **27/100**; certified semantic checkpoint **0508**, fixed frontier **$FB96**, `JP/analysis/RESUME_STATE.json` unchanged.
