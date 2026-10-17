# JP 0554 Phase 3 — opt-in final-cycle PPU register bus scheduling

A bounded C++20 CPU/PPU integration now timestamps direct absolute
and absolute-indexed 6502 CPU reads and writes of the 2C02 register
window ($2000–$3FFF) on the final CPU instruction bus cycle.
For supported direct source operations, `Cpu::exec` advances all
preceding instruction cycles before the register access and advances
the last cycle afterwards. Indexed read page-crossing penalties
are included. Only actual `$2000` (PPUCTRL), `$2001` (PPUMASK)
writes and `$2002` (status bit 7 read/clear) have modeled effects;
other PPU operations fail closed. The register address is mirrored
every eight bytes. Each accepted transaction records original CPU
address, canonical register, value, read/write, CPU-cycle number,
and PPU frame scanline/dot.

## Verification

ROM-free CTest `jp_timed_ppu_bus_0554` checks that a status read
positioned just before the scanline-241 dot-1 transition returns
the old status, a later read observes/clears VBlank, $2008/$2009
mirrors write the correct registers, indexed reads with page cross
take one additional cycle, stores do not, real VBlank NMI edges latch,
and unsupported/unpositioned PPU accesses reject. It also tests
that the default 0553 scripted mode remains unchanged.

Run:
```sh
cmake -S JP/recomp/native/boot -B build/jp-native-boot
cmake --build build/jp-native-boot --parallel 2
ctest --test-dir build/jp-native-boot --output-on-failure
```

## Explicit boundaries

Opt-in only via `Cpu::enable_timed_ppu_registers()`.
The shipped 0553 ROM-authenticated reset/NMI driver continues
to use scripted $2002 reads and injected NMI until a reference
Mesen full-system trace validates a replacement. This does NOT
model an entire 2A03 bus, dummy read/RMW subcycles, open-bus
bits, VBlank/NMI suppression race windows, $2005/$2006 scrolling,
$2007 VRAM access, OAM DMA, DMC DMA, rendering, VRC6 IRQ or APU.
Only direct absolute and absolute-indexed LDA/LDX/LDY/BIT
and STA/STX/STY addressed at PPU registers are supported for
the final-access timestamp. All other register paths fail closed.

No original JP gameplay-frame equivalence or playable-runtime claim.
4,261 statically compiled instruction starts unchanged.
Strict PRG 49,504/262,144, VPP 27/100, semantic frontier 0508/$FB96.
