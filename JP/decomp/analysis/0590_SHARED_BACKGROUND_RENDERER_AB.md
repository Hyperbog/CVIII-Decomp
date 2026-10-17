# JP 0590 — controlled background-renderer A/B build switch

Owner Beta reports suspect a **shared background-layer/scroll/priority
defect in several stages**, including ambiguous earlier Stage 3 and
Stage 4-0A purple-area graphics. It is not yet possible to conclude
that the culprit is sprite overflow or a specific PPU nametable fetch.

The pinned external NESRecomp cycle renderer has two compile-time
backends: hardware-style LLE and an experimental SIMD/HLE PPU. The
Original edition continues to default to **LLE**. For focused comparison
against the *same deterministic input route*, the private C11 build
now accepts `--ppu-impl HLE`:

```sh
# Keep separate build directories; never reuse an LLE CMake cache for HLE.
python3 JP/recomp/tools/build_retail_cycle_0575.py \
 --rom "/private/Akumajou Densetsu (Japan).nes" \
 --out /tmp/cviii-lle --frames 600 --ppu-impl LLE
python3 JP/recomp/tools/build_retail_cycle_0575.py \
 --rom "/private/Akumajou Densetsu (Japan).nes" \
 --out /tmp/cviii-hle --frames 600 --ppu-impl HLE
```

Pass an identical `--input-script FILE` in both commands to compare
observed per-frame CPU/PPU hashes and PNGs. This cannot currently
reproduce Stage 3/4 without reaching the same route; it is **not**
evidence of a graphics repair. Do not take different screenshots
alone as proof of correctness: LLE vs HLE differences may be accuracy
regressions. A game save state may be useful for reproduction, but
savestate portability across these backends is not assumed.

The mode is recorded in `jp_cycle_build.json` and
`jp_cycle_0568.json`; unsupported values fail before CMake. This
is a targeted renderer-diagnostic tool, not a whole-ROM
reconstruction test. Historical 27/100 VPP and strict PRG
49,504/262,144 remain unchanged.
