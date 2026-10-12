# 0554 Phase 4C — opt-in VRC6a IRQ integrated with compiled CPU cycles

The ROM-free native `Cpu` optionally attaches a VRC6a IRQ device with
`enable_vrc6_irq()`. Every `advance_cycles` ticks the existing NTSC
PPU dot clock and VRC6's CPU-clock prescaler together. Direct
absolute/absolute-indexed STA/STX/STY writes to $F000–$F002 are timed
at the final instruction CPU cycle; unsupported indirect or unpositioned
IRQ-device writes fail closed. `service_interrupt_boundary()` now
ORs the VRC6 IRQ level with the existing explicit external IRQ, with
PPU NMI retaining priority. The mapper register original-address write
trace remains intact.

Opt-in and fail-closed: existing 0553 reset/NMI ROM replay and 1280-room
runner do **not** enable the VRC6 device or the boundary scheduler.
True bus micro-cycles, mapper revision A0/A1 variation, IRQ polling
edge cases, DMA, PPU rendering, APU and Mesen frame parity remain
unproven. No strict PRG credit awarded, and synthetic policy unchanged.

### Reproduce

```sh
cmake -S JP/native/boot -B build/jp-native-boot
cmake --build build/jp-native-boot --parallel 2
ctest --test-dir build/jp-native-boot --output-on-failure
```

`jp_vrc6_irq_integration_0554` tests latch, cycle-mode write
phase (control reload + one tick), overflow, IRQ entry vectors and
7-cycle clock continuation, acknowledge disable, indexed CPU-page
crossing stores, original write log, NMI priority, legacy isolation
and fail-closed indirect/unpositioned register writes.

References: https://www.nesdev.org/wiki/VRC_IRQ
VPP 27/100; strict PRG 49,504/262,144; 4,261 compiled instruction sites.
