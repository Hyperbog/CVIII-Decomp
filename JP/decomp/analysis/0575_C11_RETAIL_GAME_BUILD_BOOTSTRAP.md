# JP 0575 — single-command pinned external C11 retail-game build

The standalone C11 instruction compiler and authentic selector test
already exist. Full graphical/audio/CPU-cycle execution uses external
`mstan/nesrecomp` (PolyForm Noncommercial 1.0.0). The earlier pinned
external C11 engine compiled a wholly synthetic VRC6 mapper24 ROM with
86,951/86,958 CPU cycles native and zero fallbacks over three frames;
that is **not** original retail-game parity.

`tools/build_retail_cycle_0575.py` now runs the necessary **private**
setup and authentic C11 compilation from one command:

```sh
python3 JP/recomp/tools/build_retail_cycle_0575.py \
 --rom "/private/Akumajou Densetsu (Japan).nes" \
 --out "/tmp/jp-retail-c11" --frames 120
```

This authenticates the original SHA-256, byte size and mapper24 header,
checks out external NESRecomp at exact commit
`2b4fcdb98c9e702be3fb365cfc645003c50b5fc1`, checks the
upstream noncommercial LICENSE, calls the existing 0568 cycle
configure/compile/run pipeline, requires parseable completed frames
and CPU compiled-vs-interpreted counters, and writes
`/tmp/jp-retail-c11/jp0575_build_report.json`.
Private engine source, original ROM and generated original game C
remain outside the public CVIII repository.

`--plan` authenticates media and shows output paths without cloning;
`--offline` uses only an existing exactly pinned upstream checkout;
`--windowed` requests GUI builds. The targeted Windows/Linux C11 CI
checks this bootstrap policy without rebuilding copyrighted ROM source.

**Limitations:** this environment has no outbound GitHub DNS, so a
complete external-engine retail-JP executable has **not** been built
here. This is reproducible build infrastructure, not newly verified
gameplay. C11 hardware PRG bank mapping was fixed in 0574. Strict
49,504/262,144, VPP27/100 and existing 4,261 compiled sites unchanged.
