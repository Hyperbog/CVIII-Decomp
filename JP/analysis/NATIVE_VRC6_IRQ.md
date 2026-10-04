# Native VRC6 IRQ timing/scheduler

This native subsystem implements the Mapper 24 VRC IRQ source used by Akumajou Densetsu. It models the mapper-side latch, control, acknowledge, counter and CPU-cycle timing. CPU core interrupt polling/latency remains a separate runtime concern.

Implementation:

```text
src/vrc6_irq.hpp
src/vrc6_irq.cpp
tests/vrc6_irq_test.cpp
```

Hardware behavior implemented from the VRC IRQ model:

- `$F000`: 8-bit IRQ latch;
- `$F001`: control bits `M/E/A`, pending-IRQ acknowledge, prescaler reset, and latch-to-counter reload when E is set;
- `$F002`: pending-IRQ acknowledge and A-to-E enable transfer without counter/prescaler reload;
- cycle mode clocks the 8-bit IRQ counter every CPU cycle;
- scanline mode uses a 341-dot prescaler subtracting 3 per CPU cycle, producing the repeating 114,114,113 CPU-cycle cadence;
- when the counter is `$FF`, the next clock reloads the latch and asserts the mapper IRQ source;
- when disabled, the counter/prescaler do not advance.

The regression test verifies one-shot and repeating acknowledge behavior, exact scanline prescaler cadence, cycle mode, control-disable semantics and Mapper-24 register mirroring. With the authoritative JP ROM, it also verifies the established IRQ-handler bytes:

```text
$E118  LDA #$00
$E11A  STA $F001   ; IRQ Control clear
$E11D  STA $F002   ; IRQ Acknowledge
```

Local verification:

```sh
g++ -std=c++20 -Wall -Wextra -Werror \
  -Isrc src/vrc6_irq.cpp tests/vrc6_irq_test.cpp \
  -o /tmp/vrc6_irq_test
/tmp/vrc6_irq_test /path/to/Akumajou\ Densetsu\ \(Japan\).nes
```

This source+test pair satisfies CPU/mapper/interrupts VPP rubric item 9, **native IRQ timing/scheduler implementation**. It does not satisfy CPU/interrupt trace parity and does not model CPU-side IRQ polling quirks.
