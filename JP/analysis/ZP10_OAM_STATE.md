# Zero-page `$10` lifetime at the PRG26 OAM renderer boundary

This checkpoint isolates one question: what state does the compressed sprite format use when a descriptor omits its attribute byte?

## Renderer-local facts

Within the entire active `PRG26/PRG27` 16 KiB window (`$8000-$BFFF` under VRC6 bank `$0D`), direct zero-page `$10` accesses in the `$8001/$8070` renderer are:

- `$8064`: `LDA $10` — non-mirrored compressed record reuses cached attribute
- `$80BF`: `STA $10` — non-mirrored full record caches final transformed attribute
- `$811B`: `STA $10` — mirrored full record caches final transformed attribute
- `$8166`: `LDA $10` — mirrored compressed record reuses cached attribute

There is no `STA/STX/STY $10` initialization in `$8001` before its object loop and no other zero-page `$10` store anywhere else in the `PRG26/PRG27` 16 KiB window.

Therefore `$10` is an **input/output state byte** of the renderer, not a descriptor-local temporary initialized by the renderer.

## NMI boundary

The top-level fixed-bank NMI code from vector entry `$E057` through the bank-$0D renderer call at `$E0C7` contains no direct `STA $10`, `STX $10`, or `STY $10` instruction.

This does not claim that every nested NMI helper is forbidden from using `$10`; it establishes that there is no dedicated top-level NMI initialization immediately before `$8001`.

## Proof that `$10` is shared scratch outside the renderer

A directly disassembled gameplay routine in VRC6 bank `$03` (`PRG06/PRG07`) uses `$10` for unrelated temporary state:

```asm
974F  B9 22 98  LDA $9822,Y
9752  85 10     STA $10
9754  B9 25 98  LDA $9825,Y
9757  85 11     STA $11
9759  B9 28 98  LDA $9828,Y
975C  20 74 94  JSR $9474
...
9769  A5 10     LDA $10
976B  9D 38 04  STA $0438,X
976E  A5 11     LDA $11
9770  9D 1C 04  STA $041C,X
```

Here `$10` temporarily carries a value later copied into the object's base-X array. This is not an OAM attribute initialization protocol.

Because NMI is non-maskable, a faithful whole-machine model cannot assume ordinary main-thread use of `$10` is invisible to NMI merely because the I flag is set. Exact scheduling/interruption remains machine state.

## `$9FA9` consequence

Descriptor `$9FA9` is the one currently proven referenced descriptor whose first sprite is compressed. Its first three sprite records omit attribute bytes and execute `LDA $10` before the descriptor supplies an explicit attribute.

Therefore a faithful translation must **not**:

- initialize `$10` at `$8001` entry,
- initialize `$10` at `$8070`/descriptor entry,
- derive an attribute default from the descriptor,
- cache attributes only in a host local that is reset per object.

It must consume the pre-existing RAM byte `$10` exactly as the original does, then update that byte whenever a later full record supplies a transformed attribute.

## What is and is not proved

Proved:

1. `$10` enters `$8001/$8070` as pre-existing shared RAM state.
2. Full OAM records overwrite `$10` with their final transformed attribute.
3. Compressed records consume the current `$10` unchanged.
4. `$9FA9` can consume `$10` before locally replacing it.
5. Main gameplay code also uses `$10` as unrelated scratch, so it is not renderer-private storage.

Not yet proved:

- which exact prior instruction/value is always observed by `$9FA9` on every reachable gameplay path,
- whether object-slot ordering guarantees a preceding full sprite record before every reachable `$9FA9` render,
- whether some NMI helper/IRQ path can change `$10` before `$8001` on particular frames.

Those are upstream scheduling/object-reachability questions. Until proved, the source model must expose `$10` through shared NES RAM rather than inventing a dedicated initializer.
