# JP 0554 Phase 4F — bounded DMC sample-reader DMA

The opt-in `DmcDmaSampler` models **one explicitly requested sample
fetch** from $C000–$FFFF on an asserted CPU read boundary. It performs
a CPU read halt, dummy cycle, optional get/put alignment, and one
PRG sample read: three or four stalled CPU cycles. Caller supplies the
2A03 APU get/put parity. Each stalled cycle advances the PPU
dot scheduler and optional VRC6 IRQ counter. The sampled byte,
address, type (load/reload), CPU get cycle and stall length are recorded.

`Cpu::enable_dmc_dma(parity)` configures the unit and
`Cpu::service_dmc_dma_at_read_boundary()` performs one pending fetch.
The path is intentionally **not triggered automatically** by $4015 or
the 2A03 DMC output-unit buffer depletion. The caller must prove
a legal CPU read halt boundary and absence of competing OAM DMA;
any DMC/OAM overlap is rejected, including a pending DMC fetch before
an OAMDMA request. OAM and DMC get/put parity must agree.
No DMC playback rate, $4010–$4015 DMC registers, sample address
increment/wrap, loop, DMC IRQ or OAM/DMC cycle arbitration is modeled.

ROM-free `jp_dmc_dma_bounded_0554` CTest covers 3/4-cycle stalls,
sample bytes from both fixed PRG banks, trace timestamps,
VRC6 IRQ continuing to clock during DMC halts, duplicate requests,
unsupported addresses, source phase mismatch, fail-closed overlap,
and continued legacy default behavior.

References: https://www.nesdev.org/wiki/DMA
and https://www.nesdev.org/wiki/APU_DMC

Original 0553 reset/NMI script not modified and no Mesen-frame
parity awarded. Strict 49,504/262,144; VPP27/100, compiled starts4,261.
