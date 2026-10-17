# Native 2A03/VRC6 CPU integration — checkpoint 0509 work in progress

This directory builds a **headless native C++ CPU/bus integration program**. It is **not a playable native Castlevania III port** and **still uses the private original JP NES ROM** as code and asset input. It produces only machine diagnostics and optional CPU trace files; it does not render an interactive game.

Requirements: CMake 3.16+, a C++20 compiler and **a locally supplied** SHA-pinned Japanese `Akumajou Densetsu` cartridge image (not in Git). No retail ROM or PRG/CHR/savestate/trace payload is bundled.

```sh
cmake -S JP/decomp/legacy/native0509 -B /tmp/cviii-native -DCMAKE_BUILD_TYPE=Release
cmake --build /tmp/cviii-native --parallel
ctest --test-dir /tmp/cviii-native --output-on-failure
/tmp/cviii-native/cviii-headless-0509 '/private/Akumajou Densetsu (Japan).nes' 10000
python3 JP/tools/test_native_mesen_pc_0509.py /tmp/cviii-native/cviii-headless-0509 '/private/Akumajou Densetsu (Japan).nes'
```

The Python verifier checks SHA-256 for the exact JP ROM and the first **7,828** original-ROM PC addresses against an independent Mesen2 v2.1.1 golden digest. The same original machine's PPU vblank wait diverges at ordinal 7,829, **not** an instruction-semantic victory across 7,828 arbitrary opcodes; many of these instructions are repeated PPU polling. Cycle/PPU/mapper/IRQ and native game-frame parity remain **unproved**. The executable validates iNES shape and mapper but **does not check SHA-256 itself**; use the wrapper for authenticated ROM-locked evidence.

Source port: `../../../src/cpu_2a03.*` (all official CPU opcodes) and `../../../src/native_machine_0509.*` (VRC6 mapper, IRQ and partial PPU registers). These are the first actual native CPU-execution integration pieces; the port is not independent of original PRG and has no working raster rendering or APU audio. Full technical and proof-limits note: `../../../docs/0509_NATIVE_CPU_HEADLESS.md`.

### Controlled reference-emulator PPU phase option

The headless CLI optionally accepts `REFERENCE_PPU_START_DOT` as its fourth argument after `ORIGINAL_JP_ROM`, `MAX_STEPS`, and `TRACE_FILE`. For the reproducible independent Mesen2 reset snapshot, `31` is an explicit *fixture seed* (Mesen scanline 0/cycle 31), **not** the native machine default and **not** a generally certified hardware startup phase. With this seed, the first **24,773** original CPU PC addresses agree with independently emulated Mesen2; divergence at **24,774** happens at NMI entry. The automated Python verifier covers both the no-seed **7,828** and explicit-seed **24,773** boundaries. There is no full CPU cycle/PPU/render/IRQ reference parity.
