# Decompilation progress ledger

## Current status

Project initialized on 2026-10-03 from the verified Japanese `Akumajou Densetsu` Mapper-24 ROM. The first bank-aware control-flow pass is committed. No source-level translated-byte percentage is claimed yet: code/data classification and a defensible coverage denominator have not been established across all 256 KiB PRG.

### Completed foundation

- Verified immutable ROM identity and iNES header.
- Split PRG conceptually into 32 physical 8 KiB banks (`PRG00..PRG31`).
- Recorded CRC32/SHA-1 prefix for every physical PRG bank in `docs/ROM_IDENTITY.md`.
- Established fixed-bank vectors:
  - RESET `$E00B`
  - NMI `$E057`
  - IRQ `$E0F5`
- Added first instruction-level disassembly in `analysis/PRG31_boot_and_interrupts.asm`.
- Added reproducible identity/bank analyzer `tools/analyze_rom.py`.

## Proven architecture from PRG31

### RESET

`PRG31:$E00B` waits on PPU status, initializes the stack, calls fixed-bank initialization helpers, clears CPU RAM `$0000-$07FF`, disables VRC6 frequency scaling at `$9003`, initializes additional state, configures `$B003`, selects the `$C000-$DFFF` bank, enables IRQs, and enters the fixed-bank idle loop at `$E04B`.

The boot path calls `PRG31:$E2C4`, which loads `$1E` and writes it to VRC6 `$C000`. Therefore physical `PRG30` is mapped at CPU `$C000-$DFFF` after this boot step.

### 16 KiB bank state

`PRG31:$E2D0` stores A to zero-page `$23`, then falls into `$E2D2`, which writes A to VRC6 `$8000`.

Thus `$23` is proven to be the software-tracked active 16 KiB PRG-bank value for normal bank changes. `$E2D2` is also callable directly when code intentionally changes the hardware bank without overwriting the tracked value.

`$E2CA` first saves `$23` into `$24`, then selects the new bank. The surrounding callers show `$24` participates in temporary-bank restoration.

### NMI

NMI at `PRG31:$E057` saves A/X/Y, performs VRC6 IRQ-register writes, restores PPU banking state, and on its primary path performs OAM DMA from CPU page `$02` via `$4014`.

Later in that path:

- loads bank value `$0D`
- calls `$E2D0`
- calls CPU `$8001`

VRC6 16 KiB bank `$0D` maps PRG offsets `$34000-$37FFF`, i.e. physical `PRG26/PRG27`. Therefore the `$8001` call is proven to target **`PRG26:$8001`**.

Initial disassembly of `PRG26:$8001` shows it iterates object/state arrays in `$0400+`, writes sprite records into shadow OAM page `$0200-$02FF`, and fills remaining OAM Y bytes with `$F4`. Combined with the NMI `$4014 = $02` DMA, this strongly establishes `$8001` as part of the frame's OAM/sprite-shadow construction path. Semantic naming beyond that remains provisional until `$8070+` is fully reconciled.

### IRQ

IRQ at `PRG31:$E0F5` saves A/X/Y plus zero-page `$00/$01`, directly selects 16 KiB bank `$01` through `$E2D2`, and indexes a pointer table beginning at CPU `$9F01`. Bank `$01` maps physical `PRG02/PRG03`; therefore this dispatch table resides in that physical 16 KiB pair.

The handler jumps indirectly through `$0000`, allowing banked IRQ subhandlers, and the common restoration path restores the hardware bank from tracked value `$23` before RTI.

This direct-vs-tracked bank-select distinction must be preserved in the native model.

## Files that are authoritative for continuation

1. `docs/DECOMPILATION_CONTINUITY.md`
2. `docs/PROGRESS.md`
3. `docs/ROM_IDENTITY.md`
4. `analysis/PRG31_boot_and_interrupts.asm`
5. `tools/analyze_rom.py`

## Unresolved / do not assume

- Exact semantic roles of zero-page variables other than those proven by direct use.
- Exact IRQ table length and meaning of `$6A` values.
- Exact purpose of every VRC6 IRQ write in NMI until the IRQ mode/latch paths are traced together.
- Full boundaries and data tables around `PRG26:$8001`.
- Full code/data partition of each physical PRG bank.
- Native runtime architecture and translated-source coverage denominator.

## Next batch

1. Fully disassemble/reconcile `PRG26:$8001` and its local helpers through at least `$817E`, classifying embedded pointer/data tables separately.
2. Trace the `PRG02/PRG03` IRQ pointer table at CPU `$9F01`, enumerate reachable IRQ handlers, and record physical targets.
3. Trace all callers of `$E2C0/$E2C4/$E2CA/$E2D0/$E2D2` to establish bank-state invariants.
4. Begin a machine-readable bank-aware symbol/call ledger once those relationships are stable.

The goal of the next batch is not merely more disassembly; it is the first coherent subsystem boundary: **frame OAM construction + interrupt-driven bank context**.
