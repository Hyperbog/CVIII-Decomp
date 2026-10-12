# JP 0554 Phase 4A — opt-in native instruction-boundary NMI/IRQ delivery

The native static-6502 CPU can now deliver latched PPU NMI and an
externally asserted level IRQ at instruction boundaries, when explicitly
enabled by `Cpu::enable_boundary_interrupts()`. The public
`Cpu::service_interrupt_boundary()` must be called once BEFORE each
dispatched native instruction; it returns `InterruptKind` so callers do
not wrongly count an interrupt as an executed compiled opcode. It
honors priority (NMI before IRQ), IRQ masking by P.I, saved PC/status
(B=0, bit5=1), hardware vectors FFFA/FFFE, seven-cycle entry, and RTI.
CLI/SEI/PLP temporarily sample the previous I value at the following
instruction boundary; RTI applies its restored I immediately. An
interrupt-entry guard requires at least one handler instruction before
another interrupt can be delivered.

**Boundaries:** The 0553 original-JP ROM reset/NMI driver is intentionally
unchanged, uses scripted `$2002` polling and manually injected first NMI.
The new scheduler is opt-in and does not magically make the CPU bus,
NMI race windows, branch/IRQ polling phases, DMA stalls, APU IRQ,
VRC6 IRQ counter or original gameplay frames cycle-accurate.
The external level IRQ input is a test/source integration point,
**not a claim that VRC6 IRQ hardware has been implemented**.
No CPU opcode instruction sites were added, and the semantic
checkpoint / PRG metrics remain unchanged.

## Reproduce ROM-free regressions

```sh
cmake -S JP/native/boot -B build/jp-native-boot
cmake --build build/jp-native-boot --parallel 2
ctest --test-dir build/jp-native-boot --output-on-failure
```

Tests cover opt-in isolation, NMI latch priority over IRQ,
interrupt flags and PC push, exact vector/stack/entry cost,
IRQ I masking, CLI delay, SEI prior-I sampling, level reentry
after RTI, and deassertion.

Primary timing references:
[NESdev interrupts](https://www.nesdev.org/wiki/Interrupts),
[NESdev NMI](https://www.nesdev.org/wiki/NMI),
[NESdev VRC IRQ](https://www.nesdev.org/wiki/VRC_IRQ).

Next: authentic VRC6 $F000/$F001/$F002 latch/control/ack
and IRQ prescaler, access-phase and IRQ sampling audits,
APU/DMA, and Mesen frame-trace parity before native gameplay
validation. Strict PRG: 49,504/262,144; VPP: 27/100;
native compiled starts: 4,261.
