# JP 0578 — source-free, frame-hash and screenshot evidence for native C11

The upstream pinned cycle runner supports `--hash-out FILE`,
`--screenshot FILE`, and `--input FILE`. Frame hashes include
the observable CPU bus trace, RAM/picture hash, PC/register state,
cycle count and internal hardware-state hash. These are deterministic
**per-frame emulator observations**, not compiled instruction sites
or proof of pixel/sound parity against Mesen.

The private authenticated original Japanese-ROM headless runner now:
1. Builds the real game as native C11 and writes the executable SHA256
   **before** attempting emulated frames (0577).
2. Runs bounded frames with automatic per-frame hashes and a final-frame
   256x240 PNG. `--input-script` optionally replays a plain text
   controller schedule with no gameplay video or movie recording.
3. Validates exactly the requested number of well-formed per-frame
   entries with sequential frame indices and increasing CPU cycles,
   plus a valid 256x240 PNG IHDR.
4. Records SHA256 fingerprints and final PC/cycle values in
   `jp_cycle_0568.json` under `frame_artifacts`. The screenshot,
   hash lines, audio and commercial game bytes remain local.
5. Rejects malformed, absent or truncated frame evidence even if
   the guest process returned zero.

Usage:
```sh
python3 JP/tools/build_retail_cycle_0575.py \
 --rom "/private/Akumajou Densetsu (Japan).nes" \
 --out /tmp/jp-retail-c11 --frames 600 \
 --input-script "/private/cviii_start_route.txt"
```

Input script example (manually chosen, not proven to start the real
game): `180 START` then `181 -`. It is optional, and run details
remain separated from genuine Mesen parity certification.

The pinned external CI independently exercises the exact 0576
synthetic mapper24 CMake target with actual `--hash-out` and
`--screenshot`, plus a focused ROM-free invalid-artifact test. No
retail ROM, unlicensed source, or commercial generated C is included.
The CI therefore proves **the diagnostics interface works with the
synthetic test** but does not claim that the real game boots.

VPP27/100, strict49,504/262144, 4,261 historical instruction starts
unchanged. No reconstruction tests were requested or run here.
