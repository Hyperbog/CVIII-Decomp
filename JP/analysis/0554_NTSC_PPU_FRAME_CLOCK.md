# JP 0554 — standalone NTSC 2C02 clock for native frame scheduling

**Evidence scope: new hardware timing primitive, not a gameplay/frame parity certificate.**

The C++20 `NtscPpuClock` module models 341 dots × 262 scanlines, the NTSC
2A03-to-2C02 1:3 clock ratio, VBlank entering at scanline 241/dot 1 and
clearing at pre-render scanline 261/dot 1, and the odd-frame skipped
pre-render dot when background or sprites are enabled. It models PPUCTRL
NMI-enable rising edges, PPUSTATUS bit-7 read-to-clear and a CPU-consumable
latched NMI edge. A deliberately defined epoch of scanline 0/dot 0/even frame
makes the tests reproducible but does **not** claim actual power-on PPU phase.

Evidence: [NESdev PPU frame timing](https://www.nesdev.org/wiki/PPU_frame_timing),
[PPU rendering](https://www.nesdev.org/wiki/PPU_rendering),
[PPU registers](https://www.nesdev.org/wiki/PPU_registers), and
[NMI](https://www.nesdev.org/wiki/NMI).

## Checks

```sh
cmake -S JP/native/boot -B build/jp-native-boot
cmake --build build/jp-native-boot --parallel
ctest --test-dir build/jp-native-boot --output-on-failure
```

GCC and Clang standalone C++20 tests pass for CPU/PPU ratio, scanline
crossings, two-frame VBlank, read-to-clear behavior, enabling NMI mid-VBlank,
multiple NMI-output edges, pre-render clearing, and exact odd/even dot counts.
The existing 0553 driver and scripted ROM replay are intentionally unchanged.

## Excluded/unverified behavior

The clock is **not connected** to the currently statically compiled 6502
instruction runner or the VRC6 mapper/IRQ scheduler. CPU instruction
cycle counts, bus-access phase, DMC/OAM DMA stalls, real PPUSTATUS low bits,
VBlank read races/NMI suppression, renderer, VRAM/CHR, audio, scanline IRQ,
controller input and real frame parity are still unimplemented. It is
incorrect to replace the 0553 scripted `$2002` responses or injected NMI
without these additional CPU/bus timing and original-Mesen comparison gates.

Next: add official NMOS 6502 per-instruction cycles (including branch/page
penalties), wire PPU register reads/writes at well-defined CPU cycle offsets,
hook NMI acknowledgement and mapper IRQ; then compare real Mesen NTSC traces.
No original ROM data is committed, and the strict PRG count stays
49,504/262,144; **VPP remains 27/100**. Semantic checkpoint 0508 and
fixed-$FB96 frontier are unchanged.
