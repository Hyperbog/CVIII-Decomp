# JP 0569 — external cycle-accurate mapper24 VRC6 synthetic integration gate

**Purpose:** Test the real upstream C11 6502/PPU/APU/VRC6/DMA
recompiler without exposing the copyrighted retail Japanese game ROM.

`JP/tools/test_cycle_synthetic_rom_0569.py` generates an entirely
artificial 393,232-byte NES mapper24 (VRC6a) iNES ROM. Its short
independently written program runs from fixed $E000, updates the
switchable 16 KiB and 8 KiB PRG banking registers, enables WRAM,
performs $4014 sprite DMA, enables PPU NMI and rendering, arms and
acknowledges VRC6 IRQ, and spins in a loop. The generated images
are ephemeral CI artifacts, not committed to Git.

The `jp_nesrecomp_cycle_mapper24.yml` GitHub Actions job:
1. Fetches upstream `mstan/nesrecomp` at pinned commit
   `2b4fcdb98c9e702be3fb365cfc645003c50b5fc1` to a
   temporary **separate** checkout; checks its PolyForm Noncommercial
   1.0.0 license.
2. Generates the synthetic mapper24 VRC6 cartridge in runner.temp.
3. Invokes upstream official CMake
   `runner/cyc/project` with `NESRECOMP_HEADLESS=ON`,
   generating the game's C11 code and compiling it with its own
   VRC6-capable hardware model.
4. Runs the resulting native program for three frames; failing
   configuration, compilation or runtime returns nonzero CI.

The native user-original-ROM integration remains
`JP/tools/nesrecomp_cycle_0568.py`, which authenticates SHA-256 and
executes the same external runtime only under the user's ownership
and external license. The synthetic GitHub Actions run is *not* a
compatibility certificate for original Castlevania III and
**cannot increase VPP or strict PRG coverage.**

The older 0562–0567 independent C11 code generation and 0553 C++
trace tests are preserved and separately run by existing CI.

References: upstream [cycle PROJECTS.md]
(https://github.com/mstan/nesrecomp/blob/master/runner/cyc/PROJECTS.md)
and [MAPPERS.md]
(https://github.com/mstan/nesrecomp/blob/master/runner/cyc/MAPPERS.md).
