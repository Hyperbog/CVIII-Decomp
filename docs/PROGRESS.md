# Decompilation progress ledger

## Current status

Project initialized on 2026-10-03 from the verified Japanese `Akumajou Densetsu` Mapper-24 ROM. Two bank-aware analysis batches are committed. No source-level translated-byte percentage is claimed yet: code/data classification and a defensible coverage denominator have not been established across all 256 KiB PRG.

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
- Correctly bounded the IRQ dispatch table to states `$00-$2C` and mapped every table target/state transition.
- Added machine-readable `analysis/IRQ_STATE_MACHINE.csv`.
- Added reproducible ROM and IRQ audits in `tools/analyze_rom.py` and `tools/audit_irq_dispatch.py`.

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

`$8070..$817E` performs two-level pointer lookup and emits OAM fields. `$8119` XORs the attribute byte with `$40`, proving a horizontal-flip path. `$817F+` is read as pointer-table data by this routine and must not be linearly disassembled as code without another proven entry.

Full notes: `analysis/PRG26_OAM_frame.md`.

## Batch 02 — IRQ state-machine closure and correction

### Corrected table boundary

The initial pass incorrectly extended the IRQ pointer table through candidate states `$2D-$2F` and claimed `$9F60` was an overlapping code/data byte. Fresh direct disassembly corrected this.

The actual table is exactly:

- `PRG02:$9F01-$9F5A`
- 90 bytes
- 45 entries
- states `$00-$2C`

`$9F5B` begins executable `CE 81 07` (`DEC $0781`) and is directly called by `$A090` and `$A185`. Therefore `$9F5B+` is code, not additional dispatch-table data. The old `$9F60` overlap claim is retired and must not be reintroduced.

### State transitions

Every table target is now mapped in `analysis/IRQ_STATE_MACHINE.csv`.

Important closure facts:

- normal table states are `$00-$2C`
- the highest explicit chain is `29 -> 2A -> 2B -> 2C`
- state `$2C` does not increment
- states `$1A/$1B` assign from small local tables rather than simply incrementing
- several states intentionally remain active across IRQs until a RAM countdown/condition completes
- bit-7-set `$6A` values bypass the table entirely at the fixed IRQ dispatcher

### `$43` seed / `$6A` active-state contract

NMI copies `$43 -> $6A` at `$E073-$E075`.

`$E616` clears both `$6A` and `$43`.

Whole-PRG producer-pattern auditing plus direct instruction-boundary reconciliation establishes:

- accepted direct immediate `$43` seeds observed in code: `01,05,0B,10,12,13,16,17,19,1A,1E,21,23,29,80`
- helper `$8E97` supplies additional proven seeds `02`, `09`, and `24` (plus `13` on another branch)
- `$94D9` restores `$43` from `$A3`, while `$B55A` proves `$A3` is a snapshot of the previous `$43`
- `$9A67` stores only `01`, because it executes after equality with `CMP #$01`
- apparent non-STA `$43` mutations and apparent extra `$6A` stores found by raw pattern search fall inside tables/graphics/inline dispatch data and are not accepted as executable writes

The currently proven state domain is therefore table states `$00-$2C` plus `$80` as a high-bit bypass sentinel.

### VRC6 IRQ exit distinction

The two fixed exits are not interchangeable:

- `$E118`: `LDA #0; STA $F001` then falls through `$E11D`
- `$E11D`: writes to `$F002` and restores the tracked PRG bank

NESdev documents `$F001` as IRQ Control and `$F002` as IRQ Acknowledge. A write to Acknowledge applies the stored A-bit enable-after-ack behavior; a Control write also changes/reloads IRQ state. Preserve this difference in the eventual native VRC6 implementation.

References:

- https://www.nesdev.org/wiki/VRC6
- https://www.nesdev.org/wiki/VRC_IRQ

## Files authoritative for continuation

1. `docs/DECOMPILATION_CONTINUITY.md`
2. `docs/PROGRESS.md`
3. `docs/ROM_IDENTITY.md`
4. `analysis/PRG31_boot_and_interrupts.asm`
5. `analysis/PRG02_IRQ_dispatch.md`
6. `analysis/IRQ_STATE_MACHINE.csv`
7. `analysis/PRG26_OAM_frame.md`
8. `tools/analyze_rom.py`
9. `tools/audit_irq_dispatch.py`

## Unresolved / do not assume

- Exact gameplay/render meaning of each `$43/$6A` IRQ program state.
- Exact producer/valid domains of `$0780/$0781/$0782/$0789-$0794` used by multi-step IRQ handlers.
- Exact purpose of every VRC6 IRQ latch value until the visual split/scroll programs are connected to frame-side setup.
- Complete extent and index semantics of the `PRG26:$817F` sprite pointer hierarchy.
- Complete object-record semantics for arrays `$0400/$041C/$0438/$0454/$0470/$048C/$04A8`.
- Full code/data classification of each physical PRG bank.
- Native runtime architecture and translated-source coverage denominator.

## Next batch

1. Return to `PRG26:$8070` and determine the valid `$048C` selector domain and exact first-level `$817F` pointer-table extent.
2. Decode the second-level sprite-description pointer format and field stream consumed by `$8070..$817E`.
3. Trace producers of the 28-entry object structure-of-arrays fields around `$0400-$04A8`.
4. Connect the `$43` IRQ seed setters to the visual/game states that select each raster program.
5. Once those RAM contracts are stable, begin the first native mapper/IRQ/OAM subsystem source with regression checks against ROM-derived traces.

No translated-byte percentage is being reported yet. That remains intentionally deferred until the project has a conservative, overlap-safe PRG accounting model rather than an invented early denominator.
