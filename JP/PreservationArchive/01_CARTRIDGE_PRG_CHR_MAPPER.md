# 01 — Cartridge Image, Physical PRG/CHR and Konami VRC6a Mapper

**Status:** PARTIAL. Evidence: A/B (original header/boot) plus scoped native tests F. Read [ROM identity and 32-bank hash table](../docs/ROM_IDENTITY.md), [native mapper audit](../analysis/NATIVE_VRC6_MAPPER.md).

## Immutable geometry

iNES header `4E 45 53 1A 10 10 80 10 00 00 00 00 00 00 00 00`. File size **0x60010** = 16-byte header + **0x40000 PRG (256 KiB)** + **0x20000 CHR (128 KiB)**. Mapper **24** = Konami VRC6a (JP; the US mapper is different). Fixed physical PRG31 is 8 KiB at PRG offset `0x3E000` and CPU `$E000-$FFFF`; RESET/NMI/IRQ vectors point to **$E00B/$E057/$E0F5**. ROM checksum is in chapter 00.

## CPU-to-ROM mapping

| CPU window | Original mapping | Physical PRG |
|---|---|---|
| $6000-$7FFF | PRG-RAM, gated by $B003 bit 7 | writable RAM, not ROM |
| $8000-$BFFF | 16-KiB raw switch bank `r`; written at $8000 | physical 8-KiB banks `2r,2r+1` |
| $C000-$DFFF | independent switchable 8-KiB bank | selected physical 8-KiB bank |
| $E000-$FFFF | fixed 8 KiB | PRG31 |

Raw bank $0B therefore means physical PRG22 and PRG23 in the $8000-$BFFF window; raw $0A means PRG20/PRG21. **A CPU address like $B4CC has no unique physical identity without mapper state.** For 0507, fixed NMI $E526 explicitly selects raw bank $0A and jumps to $B4CC; see [06](06_ROOMS_STAGE_WORLD_STATE.md).

Fixed PRG31:$E2D0 executes `STA $23; STA $8000; RTS` as the game's 16-KiB selector. $23 is actual RAM state; the mapper write is also an external machine side effect. The [temporary read](../src/temporary_prg_bank_read.hpp) selects raw $0E for `LDA ($08),Y` then explicitly restores $0A. See [0506](../analysis/CROSSBANK_AI_ATLAS_0506.md); nested mapper state/interrupt context still matters.

## PPU/CHR and mirroring

The [native VRC6 mapper](../src/vrc6_mapper.hpp) models eight CHR registers in $D000-$D003/$E000-$E003, pattern table mode 0–3, pair mode, and CIRAM mirroring controlled by $B003 bits 2–3. [Tests](../tests/vrc6_mapper_test.cpp) exercise synthetic bank identities, register mirrors, WRAM and target JP-ROM window identities. These **component tests are not complete frame rendering or sprite/video parity**.

## Recompilation contract and unknowns

Implement mapped reads/writes as an explicit CPU/PPU bus with mapper state. Preserve $23 writes, $8000/$C000 selectors, CHR slots, IRQ and audio register ownership. The *complete game-specific mapper-write and frame-timing inventory* remains open; [VRC6 IRQ](../analysis/NATIVE_VRC6_IRQ.md) is a distinct component, and VRC6 pulse/saw sound is a separate unimplemented parity target. Never merge JP mapper and US MMC5 semantics.
