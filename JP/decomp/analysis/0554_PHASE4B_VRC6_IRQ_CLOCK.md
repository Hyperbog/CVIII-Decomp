# JP 0554 Phase 4B — isolated Konami VRC6a CPU-cycle IRQ counter

The ROM-free `native/boot/vrc6_irq_0554.hpp` C++20 device models the
Japanese Akumajou Densetsu mapper-24 VRC6a interrupt registers:
`$F000` reload latch, `$F001` control (mode M, enable E, enable-on-ack
A), and `$F002` acknowledge (copy A to E). Control acknowledges IRQ,
resets the CPU-cycle prescaler, and reloads counter only when E is set.
Acknowledge does not reset prescaler or counter. Disabled counters freeze.
Counter overflows at $FF, reloads the latch and asserts a level IRQ.

In scanline-approximation mode, the prescaler subtracts 3 per CPU cycle
from 341, producing 114/114/113 CPU-cycle IRQ-counter ticks; in cycle
mode the counter ticks on every CPU cycle. This continues during VBlank
or PPU rendering-off, as VRC IRQs are CPU-clocked.

Reference: [NESdev VRC IRQ](https://www.nesdev.org/wiki/VRC_IRQ),
[NESdev VRC6](https://www.nesdev.org/wiki/VRC6).
The VRC IRQ generalization follows the published NESdev model; subtle
chip-revision behavior still needs observed hardware/emulator traces.

## Verification

The ROM-free `jp_vrc6_irq_counter_0554` CTest covers two cycle-mode
overflows, IRQ level and acknowledgment, enable-on-ack, one-shot after
ack, disabled-counter freeze, exact prescaler phases 114/114/113,
control reset, latch update/reload, and rejection of invalid registers.

```sh
cmake -S JP/recomp/native/boot -B build/jp-boot
cmake --build build/jp-boot --parallel 2
ctest --test-dir build/jp-boot --output-on-failure
```

**Not connected to the native CPU/bus** yet. The earlier 4A pre-dispatch
interrupt scheduler accepts an external IRQ level, but no driver wires
this VRC6 counter to that input. No instruction-level mapper register
write phase, OAM/DMC DMA, IRQ sampling accuracy, or frame parity is
asserted. The original-ROM 0553 CPU replay remains scripted and
unmodified.

VPP 27/100, strict PRG 49,504/262,144, 4,261 compiled starts; last
semantic checkpoint 0508/$FB96. No ROM content is committed.

Next: opt-in clock wiring from CPU `advance_cycles`, precise direct
mapper register-write phase, CPU IRQ arbitration connection, bounded
tests under the source-authenticated JP ROM, Mesen trace comparison.
