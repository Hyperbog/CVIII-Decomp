# Native Mapper 24 / VRC6 PRG+CHR mapper

This checkpoint adds a native target-game Mapper 24 memory-mapper lift for Akumajou Densetsu.

Authoritative JP ROM identity remains:

```text
SHA-256 958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
PRG     256 KiB
CHR     128 KiB
mapper  24 / Konami VRC6a
```

Implementation:

```text
src/vrc6_mapper.hpp
src/vrc6_mapper.cpp
tests/vrc6_mapper_test.cpp
```

The lift implements the memory-mapping behavior needed by the target cartridge:

- `$6000-$7FFF` PRG RAM gated by `$B003` bit 7;
- `$8000-$BFFF` switchable 16 KiB PRG using the lower four bank bits;
- `$C000-$DFFF` switchable 8 KiB PRG using the lower five bank bits;
- `$E000-$FFFF` fixed physical PRG31;
- VRC6a mapper-register mirrors using decoded CPU A0/A1/A12-A15 (`address & $F003`);
- eight CHR registers at `$D000-$D003/$E000-$E003`;
- VRC6 pattern-table banking modes 0, 1, 2 and 3, including 2 KiB-pair behavior under `$B003` bit 5;
- target-game CIRAM vertical/horizontal/one-screen A/one-screen B selection from `$B003` bits 2-3;
- PPU pattern-table reads through the selected 1 KiB CHR slots.

VRC6 pulse/saw audio and IRQ latch/control/ack/timing are intentionally outside this class and remain separate open subsystems.

## Regression coverage

`tests/vrc6_mapper_test.cpp` validates synthetic bank identity across all PRG windows, mapper-register mirrors, WRAM enable/disable, CHR modes, and the target game's normal `$20/$24/$28/$2C` mirroring values.

When passed the authoritative JP ROM, the same test also verifies:

- iNES dimensions and mapper 24 identity;
- raw bank `$0B` mapping to physical PRG22/23 and the checkpoint-0501 `$B3B6: STA $10` byte;
- raw bank `$09:$8001` and raw bank `$0A:$84EA` mapping;
- fixed PRG31 NMI/RESET/IRQ vector bytes for `$E057/$E00B/$E0F5`.

Local verification command:

```sh
g++ -std=c++20 -Wall -Wextra -Werror \
  -Isrc src/vrc6_mapper.cpp tests/vrc6_mapper_test.cpp \
  -o /tmp/vrc6_mapper_test
/tmp/vrc6_mapper_test /path/to/Akumajou\ Densetsu\ \(Japan\).nes
```

This source+test pair satisfies VPP CPU/mapper/interrupts rubric item 8, **native VRC6 PRG/CHR mapper implementation**. It does not satisfy the separate IRQ timing/scheduler or trace-parity items.
