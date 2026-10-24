# JP0725 — Live original-ROM Stage 1 widescreen presentation

**Implementation:** `cviii_stage1_host_0725.c/.h` now connects the JP0724 ROM-only atlas to the *actual* `cviii_edition.c` `CycHostExtras.present` callback. It returns 426×240 only for Enhanced with an authentic owner's original Japanese cartridge. Original returns exactly the original 256×240 pointer. The PPU/core still renders the authoritative game image; the host copies that image unchanged into native X=85..340 and paints ROM-derived background only in side columns.

**Build source:** the existing `JP_ORIGINAL_JP_ROM` input is independently SHA256-authenticated by the retail-only CMake media validator. JP0725 privately embeds only its filesystem path in the compiled owner's binary; it does NOT embed original game bytes in public C source. A full-file FNV64 identity cross-check `76615b120049ad3f` is required when opening the ROM in the shipping presenter. The standalone tests explicitly compile `CVIII_STAGE1_TEST_SYNTHETIC_ROM` to permit wholly invented layouts. The optional `--stage1-world-rom FILE` changes the private source path, but never bypasses the production identity gate. `Stage1World = 0` or `--stage1-world 0` disables extended background. Default is enabled *for Enhanced* if the authentic private ROM path exists. Absent or wrong media fails closed to the original dimensions.

## Camera/orientation evidence

Original Japanese CPU RAM `$53/$54` is the view's 16-bit **room-local** position: horizontal X for `$65 < $80`, vertical Y for `$65 >= $80`. Original MesenCE and native replay independently record this at normal Stage 1 gameplay. The actual PPU scanline horizontal scroll from the pinned NESRecomp `cyc_render_line_scroll_x(120)` is modulo 512; the presenter combines the ROM-local high-page position with the PPU's observed fractional phase and **requires ±2px agreement**. It checks real gameplay `$18=04`, original Stage 1 metatile source pointers `$5A/$5B=$8441` and `$5C/$5D=$8D51`, visible background enabled and CHR pattern table `$1000`, and stable scanline Y. Selector values alone are not game-mode identifiers.

Examples from the existing owner-provided JP0719 native replay:

| Native sample | room selector | RAM $53/$54 | PPU scanline X | Interpretation |
| --- | --- | ---: | ---: | --- |
| 19 | 00/00/00 | 21 | 21 | Exact room-local scroll |
| 24 | 00/00/00 | 142 | 142 | Exact room-local scroll |
| 29 | 00/00/00 | 218 | 219 | One-pixel phase difference |
| 35 | 00/00/00 | 417 | 416 | One-pixel phase difference |
| 39 | 00/00/00 | 512 | 0 | Exact when reduced modulo 512 |
| 43 | 00/01/00 | 0 | 256 | **Transition:** deliberately suppress extended scenery |

Original Stage 1 chapel selector `00/01/01` has `$65=$80`; its static ROM room is **only 256px wide** and extends vertically. The compositor deliberately shows no horizontal extension there; the center remains the original hardware image, and a future vertical expanded view needs different room-Y world geometry. Preloaded atlas data for the vertical room remains available but is not wrongly painted using the horizontal camera.

## Tests and acceptance boundary

- Native host regression checks **all 61,440 pixels** in the center of a 426×240 output, positive right-margin imagery **before gameplay traversal**, original mode fallback, game-over suppression, scrolling phase mismatch, and vertical-room exclusion.
- Independent C11 original-JP room map and atlas regression tests exercise the entire eight-room source layout without embedding any retail assets.
- The ROM-free **Windows 2022/MSVC host compositor test** builds the same production presenter using an explicitly invented synthetic room fixture and checks the returned 426×240 framebuffer in Windows memory.
- The existing Windows native Alpha candidate build compiles the complete SDL-linked NESRecomp game against *synthetic test media* and runs its short test frames. These are build/ABI checks, not original-Japanese stage play screenshots.
- The final **authentic original-ROM Windows SDL gameplay screenshot and subjective offscreen graphics inspection are not yet verified**. Neither automated CI nor a non-Windows container may claim that test. No user replay is requested at this checkpoint; the offline capture and deterministic input schedule remain available for a later consolidated validation if genuinely needed.

**Known visual limits:** Static room tile IDs + palette quadrants are original-ROM source-authenticated, but cached areas use the currently mapped CHR banks and live palette. Offscreen sprite simulation, raster splits, offscreen bank differences and deliberately animated/metatile changes remain outside this background-only compositor. The ongoing JP0720–JP0722 owner's local pixel-cache prototypes have not been silently merged into this publicly committed implementation. No new semantic-PRG or VPP credit is claimed.

VPP remains **31/100** and original semantically certified PRG remains **49,504 / 262,144 bytes (18.8843%)**. This is renderer functionality, not a new proof of original 6502 semantic coverage.
