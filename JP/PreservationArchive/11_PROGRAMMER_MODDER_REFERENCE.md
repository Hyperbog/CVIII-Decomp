# 11 — Programmer and Modder Quick Reference

**Status:** PRELIMINARY; only currently verified field boundaries and machine constraints. [Evidence rules](00_SCOPE_EVIDENCE_AND_SOURCE_BASELINE.md) always take precedence over convenience labels.

## Physical and CPU address notation

`PRG31:$E526` = fixed physical 8-KiB bank 31; `raw0A:$B4CC` = one of the raw 16-KiB mapper bank $0A CPU addresses, which falls in physical PRG21. Raw bank r maps physical 8KiB 2r and 2r+1. A CPU address **without** bank state is not a stable ROM pointer in $8000-$DFFF.

For any extracted field retain original ROM SHA-256, original raw bytes, physical offsets, inferred semantic view, whether it was an instruction operand, and whether its producer index range is proved. Native IDs/extensions should never steal unproven original action or object IDs.

## CPU/RAM contracts demonstrated so far

| Address/field | Demonstrated role | Critical scope |
|---|---|---|
| $0200-$02FF | shadow OAM before DMA via $4014=$02 | 64×4-byte PPU sprites |
| $0400,X | active object visibility/descriptor field in renderer | renderer X=0..$1B |
| $041C,X / $0438,X | object Y / X coordinate inputs | 8-bit wrap |
| $0454,X | object attribute/variant input | attribute masking at transform |
| $048C,X | sprite descriptor-set pointer selection | JP double indirection |
| ZP $10/$11 | shared transient coordinate/attribute state | no automatic renderer-entry zero |
| $05EF,X | object AI script ID | live ID domain partially known |
| $05C1,X | object AI four-byte record index | 8-bit `index*4` |
| ZP $19 | raw-$0A room-state selector | global live domain unproved |
| ZP $68 | nested room-state selector | may change inter-frame |
| ZP $23 | bank-select shadow written by $E2D0 | observable RAM + $8000 write |

These names describe proved consumers/selected writers, **not globally unique exclusive ownership**. Consult [03](03_PPU_OAM_SPRITE_PIPELINE.md), [04](04_OBJECT_SCHEDULER_COLLISION_SCRATCH.md), [05](05_AI_SCRIPT_AND_ACTION_VM.md), [06](06_ROOMS_STAGE_WORLD_STATE.md).

## Three modding modes

1. **Inspect/round-trip:** preserve original byte image and all unknown/slack/aliased bytes; require binary identity after no-op conversion.
2. **Legacy-compatible edit:** change only original documented fields and indices with proven capacities, re-run code/data producer bounds and emulator traces.
3. **Native extension:** allow larger script IDs, new assets, QoL, save formats etc through explicit *new* versioned structures and translation adapters. Never label a new native format as shipped 1989-era ROM serialization.

Examples: do not edit all 256 action table words believing they are live; mechanical $9E aliases script data. Do not clamp the FD62,Y ROM lookup to 12 entries: the modulo-12 bound belongs only to the *other* FD4D table. Do not carry US MMC5 mapper semantics into JP Mapper 24.

## Implementation assistance

[ROM identity](../docs/ROM_IDENTITY.md), [whole PRG atlas](../docs/WHOLE_PRG_ATLAS.md), [progress rubric](../docs/PROGRESS_METRIC.md), [native components](08_NATIVE_RECOMP_AND_PARITY_CONTRACTS.md). Report any observed discrepancy as a new UNKNOWN or C-type correction and check the ROM before altering original semantics.
