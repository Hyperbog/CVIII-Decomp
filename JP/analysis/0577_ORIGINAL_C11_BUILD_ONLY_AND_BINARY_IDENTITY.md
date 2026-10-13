# JP 0577 — separate original-ROM native C11 compilation from guest execution

The original NESRecomp cycle runner treated a native C11 executable
as complete only after a successful bounded guest execution. A genuine
original-ROM **compiler/build success** could be lost when an
unsupported guest opcode, stuck NMI or PPU error halted first boot.

`tools/nesrecomp_cycle_0568.py` now writes
`jp_cycle_build.json` **immediately after** external CMake
generation and compilation, recording the authenticated Japanese
ROM identity, native executable path, native executable SHA-256,
build logs and explicit `build_completed=true` with
`gameplay_parity_verified=false`. This report survives a
subsequent guest crash, frame-count mismatch, or timeout.

`--build-only` is supported by both the lower-level cycle
script and the pinned one-command `build_retail_cycle_0575.py`.
It stops after original-ROM C11 compilation and returns the binary
fingerprint without claiming frame execution. The default
still attempts 120 bounded headless frames and, on success,
records actual original game CPU native/interpreted fractions
separately in `jp_cycle_0568.json`.

The focused ROM-free
`tools/test_cycle_build_stages_0577.py` simulates only external
configure/build/execution and verifies the report and SHA:
build-only, successful bounded guest, and failing bounded guest
return independent truthful evidence. This is a **build-lifecycle
test**, not a ROM reconstruction, video, emulator or game-parity test.

To build the original Japanese VRC6 native C11 executable privately:

```sh
python3 JP/tools/build_retail_cycle_0575.py \
 --rom "/private/Akumajou Densetsu (Japan).nes" \
 --out /tmp/jp-retail-c11 --build-only
```

Upstream is still an external pinned PolyForm Noncommercial dependency,
and original commercial ROM/game-derived C remains outside Git. The
network-isolated sandbox cannot download upstream source, so this
step itself does not certify that retail C11 compilation succeeded.
VPP 27/100; strict PRG 49,504/262,144; compiled original sites
4,261 unchanged.
