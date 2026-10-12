# JP 0554 phase 4E — bounded PPU OAMADDR/OAMDATA register integration

When the existing timed PPU register path and the bounded internal-RAM
OAM DMA device are both enabled, direct CPU $2003 (OAMADDR) writes,
$2004 (OAMDATA) writes and $2004 reads operate on the SAME OAM
address and 256-byte backing array as $4014 DMA. Register mirrors
($200B/$200C) retain the canonical $2003/$2004 mapping. OAMDATA writes
auto-increment OAMADDR modulo 256; reads do not. Each direct
supported PPU instruction records its final-cycle transaction.

OAM register accesses fail closed if no backing device is present or
if the PPU clock currently has rendering enabled on visible/prerender
scanlines. This deliberately excludes actual rendering-time OAM
evaluation/increment corruption and OAMADDR corruption peculiar to
older 2C02 revisions. OAM attribute-bit write masking and sprite
rendering are also not modeled. Byte-level OAM is a bounded state
buffer, NOT an original console framebuffer parity claim.

Tests verify mirrored address/data writes, direct readback after DMA,
OAMADDR wrap, shared memory, register timestamps, rendering-time
rejection, absent-device rejection, and unchanged scripted 0553 mode.
Reference: https://www.nesdev.org/wiki/PPU_registers

Strict coverage 49,504/262,144; VPP 27/100; native starts 4,261.
