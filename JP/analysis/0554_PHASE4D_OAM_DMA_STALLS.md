# JP 0554 Phase 4D — opt-in 513/514-cycle internal-RAM OAM DMA

The opt-in native `Cpu::enable_ram_oam_dma(get_cycle_parity)`
models $4014 writes by supported directly addressed 6502 stores
and the ensuing CPU read halt, optional alignment and 256
get/put pairs. A test-defined get/put CPU-cycle phase is mandatory:
NTSC 2A03 power-on alignment is not deterministic. The DMA device
uses the 2KiB internal CPU RAM and its $0800–$1FFF mirrors only;
non-RAM source pages fail closed. It copies 256 bytes into a
private OAM array and supports an explicitly seeded OAMADDR for
unit tests. Each of the 256 bytes records the source address,
destination OAM index, byte, and get/put CPU cycle.

Elapsed stall cycles are **513 or 514 in addition to the writing
instruction**. Each stalled CPU cycle drives the PPU dot clock and
opt-in VRC6 IRQ counter. PPU NMI edges can become latched during
DMA and are consumed only by the existing opt-in instruction-boundary
scheduler after the CPU resumes.

## Tests

`jp_ram_oam_dma_0554` verifies:
- Both 513/514 alignment paths and per-byte cycle timestamps
- 2KiB RAM mirroring, complete 256-byte copy and 8-bit OAMADDR wrap
- VRC6 level IRQ and PPU NMI evolving during a CPU DMA halt
- NMI priority over an IRQ after DMA completion
- Unsupported pages, indirect or unpositioned $4014 writes rejected
- Opt-in isolation of the legacy original-ROM scripted boot driver

Run ROM-free CI via:
```sh
cmake -S JP/native/boot -B build/jp-native-boot
cmake --build build/jp-native-boot --parallel 2
ctest --test-dir build/jp-native-boot --output-on-failure
```

## Important exclusions

This is not complete OAMDMA or sprite emulation. It does not
handle $2003 OAMADDR or $2004 OAMDATA writes, arbitrary PRG/PRG-RAM
or I/O source pages, DMC DMA overlap and arbitration, DMA CPU
halt-read bus side effects, or $4014 multiple-write RMW behavior.
The assumed source RAM contents are unchanged by DMA, which is valid
only for the supported internal-RAM subset. CPU/PPU power-on
alignment, register read suppression races and whole-game Mesen
frame equivalence remain unverified.

Reference: https://www.nesdev.org/wiki/DMA
Existing synthetic 0553 driver never enables this DMA module.
**No strict PRG/verified-parity credit awarded:** VPP 27/100,
49,504/262,144 strict PRG, 4,261 compiled instruction sites.
