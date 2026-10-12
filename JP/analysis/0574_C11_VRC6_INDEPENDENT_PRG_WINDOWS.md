# JP 0574 — correct VRC6a independent 8 KiB PRG window in C11

Reviewing the C11 runtime after the 0573 original-ROM selector build
revealed an architectural correctness defect: `jp_bus_read()` and
fixed-physical codegen **incorrectly fixed $C000–$DFFF to physical
PRG bank30**. Mapper24 VRC6a uses a 16 KiB switchable
$8000–$BFFF, an independently switchable 8 KiB
$C000–$DFFF, and only the last 8 KiB $E000–$FFFF fixed.

The C11 bus now implements VRC6a $8000–$8003 select (4 bits)
and $C000–$C003 select (5 bits), including documented
`address & 0xF003` register mirroring and ignored upper data bits.
A single `jp_bus_physical_offset` function maps CPU addresses
into 256 KiB PRG offsets. Both interpreter reads and
**generated fixed/scripted compiled C** use this resolver, so
the same bank-switching rules apply to either execution backend.

The rest of the VRC6 hardware is explicitly not implemented by this
lightweight C bus: $B003 WRAM enable, VRC6 audio,
CHR/nametable pins, IRQ, CPU/PPU timing and DMA still
require the external cycle-accurate backend. Unsupported
registers fail closed, as before.

A focused ROM-free C11 test checks 16 KiB and 8 KiB registers,
their address mirrors, the independence of the $C000 slot, fixed
$E000 mapping, physical offset identity and unsupported WRAM
registers. A Python generator smoke additionally verifies
physically eligible $C000 original sites.

No new original PRG bytes are claimed. Native 4,261 compiled sites,
strict 49,504/262,144, VPP27/100 remain unchanged.
Reference: https://www.nesdev.org/wiki/VRC6
