# JP 0554 Phase 2 — 2A03 static-instruction CPU cycle accounting

The shared native `Cpu::exec<Op,Mode>` now accumulates the documented
NMOS 6502 base cycle count for each supported original instruction and
advances the standalone NTSC PPU dot clock by exactly three dots per
counted CPU cycle. It applies the original taken-branch (+1) and
page-cross (+1) penalties and extra indexed page-cross timing for
`abs,X`, `abs,Y`, and `(zp),Y` **read** instructions, not stores/RMW.
Indirect indexed addressing uses the single effective-pointer read already
performed by the CPU semantic core, preventing additional $2002 polling,
mapper reads, or memory side effects. NMI entry adds 7 CPU cycles.
Unsupported opcode/address-mode combinations fail at compile time.

The ROM-free unit tests check read/store/RMW differences, both branch
penalties, JSR/RTS, NMI/RTI, and exact 3:1 clock advancement.
Existing 0553 original-ROM trace output formats and scripted I/O
remain unchanged. This is **instruction-level accounting only**;
it is not bus-cycle-accurate, and the PPU clock does not yet
drive $2002 status, PPUCTRL writes, IRQ arbitration, or NMI delivery.

Unmodeled timing includes 513/514-cycle OAM DMA, DMC DMA stalls, VRC6 IRQ
CPU sampling, memory bus half-cycle phases, transient NMI read-race
behavior, and the bank0A `bounded_external()` helper path (which is still
a bounded intrinsic, not statically compiled instructions). In
particular, calling the PPU clock independent of script I/O must not
be construed as authentic JP gameplay/interrupt timing.

Reproduction (public ROM-free CI):
```sh
cmake -S JP/native/boot -B build/jp-native-boot
cmake --build build/jp-native-boot --parallel
ctest --test-dir build/jp-native-boot --output-on-failure
```

The original JP ROM is SHA-locked as before and remains private.
VPP stays 27/100; strict PRG 49,504/262,144; no new native
instruction-site promotion. Next: instrument precise PPU register
read/write phases and NMI delivery, include OAM/DMC DMA/mapper IRQ,
then compare natural Mesen original-frame traces.
