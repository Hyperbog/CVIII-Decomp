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
- Added first instruction-level fixed-bank disassembly in `analysis/PRG31_boot_and_interrupts.asm`.
- Traced the first banked NMI frame routine through `PRG26:$8001..$817E` and classified `$817F+` as pointer/data space for that path.
- Traced the IRQ dispatch table in `PRG02` and discovered a real code/data overlap at `$9F60`.
- Added reproducible identity/bank analyzer `tools/analyze_rom.py`.

## Proven architecture from PRG31

### RESET

`PRG31:$E00B` waits on PPU status, initializes the stack, calls fixed-bank initialization helpers, clears CPU RAM `$0000-$07FF`, disables VRC6 frequency scaling at `$9003`, initializes additional state, configures `$B003`, selects the `$C000-$DFFF` bank, enables IRQs, and enters the fixed-bank idle loop at `$E04B`.

The boot path calls `PRG31:$E2C4`, which loads `$1E` and writes it to VRC6 `$C000`. Therefore physical `PRG30` is mapped at CPU `$C000-$DFFF` after this boot step.

### 16 KiB bank state

`PRG31:$E2D0` stores A to zero-page `$23`, then falls into `$E2D2`, which writes A to VRC6 `$8000`.

Thus `$23` is proven to be the software-tracked active 16 KiB PRG-bank value for normal bank changes. `$E2D2` is also callable directly when code intentionally changes the hardware bank without overwriting the tracked value.

`$E2CA` first saves `$23` into `$24`, then selects the new bank. The surrounding callers show `$24` participates in temporary-bank restoration.

### NMI and first frame/OAM path

NMI at `PRG31:$E057` saves A/X/Y, performs VRC6 IRQ-register writes, restores PPU banking state, and on its primary path performs OAM DMA from CPU page `$02` via `$4014`.

Later in that path it selects bank value `$0D` and calls CPU `$8001`. VRC6 bank `$0D` maps physical `PRG26/PRG27`, proving the call target is `PRG26:$8001`.

`PRG26:$8001`:

- iterates 28 object slots (`$00..$1B` indices into structure-of-arrays data at `$0400+`),
- skips inactive/suppressed entries,
- calls `$8070` to emit sprite records into `$0200-$02FF`,
- begins with 64 available sprite slots,
- then writes `$F4` to Y-coordinate bytes for every remaining slot so unused sprites are hidden before page-2 OAM DMA.

`$22` advances by `$44` modulo 256 each invocation and seeds the OAM destination offset. This is consistent with sprite-order rotation, but the exact gameplay intent remains provisional.

`$8070..$817E` performs two-level pointer lookup and emits OAM fields. `$8119` XORs the attribute byte with `$40`, proving a horizontal-flip path. `$817F+` is read as little-endian pointer-table data by this routine and must not be linearly disassembled as code without another proven entry.

Full notes: `analysis/PRG26_OAM_frame.md`.

### IRQ dispatch and overlap

IRQ at `PRG31:$E0F5` saves A/X/Y plus zero-page `$00/$01`, directly selects 16 KiB bank `$01` through `$E2D2`, and indexes a pointer table beginning at CPU `$9F01`. Bank `$01` maps physical `PRG02/PRG03`.

The table yields plausible handler pointers for indices `$00..$2F`. The next would-be entry overlaps sequential code and decodes to an implausible execution target, but the actual domain of `$6A` still needs producer-side proof.

Critical fidelity fact: table entry `$2F` uses bytes `$9F5F=$26` and `$9F60=$A5` to form target `$A526`, while `$9F60` is simultaneously the first opcode of a valid routine (`LDA $7A`). Therefore this ROM contains at least one proven **code/data-overlap byte**. Coverage/accounting must allow one physical byte to participate in more than one semantic role rather than forcing a disjoint partition.

Full notes: `analysis/PRG02_IRQ_dispatch.md`.

## Files that are authoritative for continuation

1. `docs/DECOMPILATION_CONTINUITY.md`
2. `docs/PROGRESS.md`
3. `docs/ROM_IDENTITY.md`
4. `analysis/PRG31_boot_and_interrupts.asm`
5. `analysis/PRG02_IRQ_dispatch.md`
6. `analysis/PRG26_OAM_frame.md`
7. `tools/analyze_rom.py`

## Unresolved / do not assume

- Exact semantic roles of zero-page variables other than those proven by direct use.
- Exact producer/domain of IRQ index `$6A`; do not yet hard-cap it in reconstructed logic solely from table appearance.
- Exact purpose of every VRC6 IRQ write in NMI until IRQ mode/latch paths are traced together.
- Complete extent and index semantics of the `$817F` pointer table.
- Complete object-record semantics for arrays `$0400/$041C/$0438/$0454/$0470/$048C/$04A8`.
- Full code/data/overlap classification of each physical PRG bank.
- Native runtime architecture and translated-source coverage denominator.

## Next batch

1. Trace all writes to `$6A` and reconcile the IRQ dispatch-index domain.
2. Disassemble/reconcile unique IRQ targets from the `$9F01` table, especially `$9F99`, `$9FA1`, `$9FD5`, `$9FE3`, `$A01C+`, and common return through fixed `$E118`.
3. Determine the valid index/stride and full extent of the `PRG26:$817F` sprite pointer table.
4. Trace producers of the 28-entry `$0400+` object structure-of-arrays fields.
5. Begin a machine-readable bank-aware symbol/call ledger once these relationships are stable.

The next coherent subsystem target remains **frame OAM construction + interrupt-driven bank context**, now with explicit overlapping-code/data support required by the original ROM.
