# Checkpoint 04F1 — incoming ZP `$10` for reachable `$9FA9`

This checkpoint answers one question only: when the now-proven type-`$08` path reaches PRG26 descriptor `$9FA9`, what supplies the attribute byte consumed by its first compressed sprite records?

All ROM claims are verified against the Japanese target SHA-256:

```text
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
```

Primary byte span examined in this checkpoint is PRG26 `$8001-$81FF` (renderer core), with isolated verification of descriptor `$9FA9` and slot-0 mirror-state stores in PRG28.

## Renderer order and cache lifetime

PRG26 `$8001` starts the object index at zero and processes objects in strictly ascending slot order until `$1C`:

```asm
8001  A9 00       LDA #$00
8003  85 05       STA $05
...
8012  A6 05       LDX $05
8014  E0 1C       CPX #$1C
8016  B0 20       BCS $8038
...
8034  E6 05       INC $05
8036  D0 DA       BNE $8012
```

It does not initialize ZP `$10` before the loop or before calling `$8070`.

Inside the renderer:

```asm
8064  A5 10       LDA $10      ; compressed record, non-mirrored
80BF  85 10       STA $10      ; explicit attribute, non-mirrored
811B  85 10       STA $10      ; explicit attribute, mirrored
8166  A5 10       LDA $10      ; compressed record, mirrored
```

Therefore `$10` is a persistent input/output byte across records and across object calls.

## `$9FA9` begins by consuming inherited state

The authoritative descriptor bytes are:

```text
9FA9: 04 DF 8A F0  E1 8C F8  E5 8E 00  04 E4 90 03
```

Count is four sprites. The first three Y/control bytes are odd (`DF`, `E1`, `E5`), so all three records omit an attribute byte and consume the pre-existing `$10`. Only the fourth record supplies an explicit attribute (`03`).

Thus `$9FA9` does not define its first three attributes locally.

## The incoming value is not a single game constant

Because the outer renderer walks slots upward, the value seen by `$9FA9` is determined by render history earlier in the same frame:

1. if a lower-index object rendered and completed at least one explicit-attribute record, `$10` is the final transformed attribute emitted by the last such lower object;
2. if no lower-index object emitted an explicit attribute, `$10` remains whatever shared-RAM value entered the renderer.

The descriptor census already established that referenced descriptors do contain explicit-attribute records, but there is no fixed lower-slot object tied to the type-`$08` allocation path. The ordinary allocator uses the first free slot in `$01-$12`, so the preceding rendered slot is frame-state dependent rather than a dedicated `$9FA9` initializer.

A concrete JP-ROM source of variation exists even at slot zero. Physical PRG28 contains executable immediate writes of both mirror states to the slot-0 `$04A8` field:

```asm
823E  A9 01       LDA #$01
8240  8D A8 04    STA $04A8
...
8249  A9 00       LDA #$00
824B  8D A8 04    STA $04A8
```

PRG26 uses `$04A8 == 0` for the mirrored path. On an explicit attribute, that path XORs `$40` before caching the final value in `$10`. Therefore otherwise-identical descriptor attributes can leave different cached values solely because the earlier slot's mirror state differs.

This directly disproves any host-side rule such as "`$9FA9` always begins with attribute X" or "initialize `$10` to a default before rendering `$9FA9`."

## Faithful native contract

The native renderer must preserve exactly this contract:

```text
incoming $10 = shared NES RAM state
for each object in ascending slot order:
    full record       -> transform attribute, store result to $10
    compressed record -> read current $10 unchanged
```

For reachable `$9FA9`, its first three sprites therefore intentionally inherit cross-object/shared-frame state.

## Interrupt caveat

NMI re-enables IRQs before the PRG26 renderer. The verified IRQ table/state-machine remains the authority for interrupt-side effects. This checkpoint does not introduce a separate `$10` initializer for IRQ handling, and no such initializer is assumed. If future IRQ-reachable code is proven to write `$10` during this window, it must be modeled as another legitimate shared-RAM source rather than normalized away.

## Result

**04F1 result: the incoming `$10` value for `$9FA9` is intentionally variable inherited state, not a constant.**

The correct translation boundary is therefore shared NES RAM plus exact ascending object order—not a per-object attribute local.

Reproducible audit: `tools/audit_prg26_9fa9_cache.py`.
