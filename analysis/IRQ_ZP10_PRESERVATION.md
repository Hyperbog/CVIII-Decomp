# Checkpoint 04F2 — IRQ-side ZP `$10` preservation

This checkpoint answers one question only: after NMI executes `CLI` and before `PRG26:$8001` renders, can any verified IRQ handler mutate the OAM attribute cache in zero-page `$10`?

Authoritative ROM SHA-256:

```text
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
```

Primary new ROM span:

```text
PRG02/PRG03 CPU $9F99-$A526
size 1422 bytes
SHA-256 fb0f709699ad64b6cb49fa4eaeb2de8e1a260e23745341fc2f48b38fedd8ded3
```

The previously mapped fixed IRQ prologue/exit and already-known called helper signatures are used only to close the same question.

## Direct write census

The complete 1422-byte handler span contains no direct encoding that can write `$10` via:

- `STA/STX/STY $10`
- `INC/DEC/ASL/LSR/ROL/ROR $10`
- absolute `$0010` equivalents

The audit also walks the 38 unique dispatch entrypoints from the proven states `$00-$2C` whose targets lie in this span. On all visited instruction boundaries it finds no reachable indexed-zero-page or indirect write form that can alias `$10`, and no absolute-indexed write whose base can reach `$0010`.

## Called helper closure

Reachable IRQ code in this span calls only the following targets outside the primary span:

```text
$9F5B
$E001 $E005
$E2FA
$E30B $E316 $E32B $E331 $E33C $E347 $E351
```

The external jump set is only the established fixed exits:

```text
$E118 $E11D
```

### Local `$9F5B`

The referenced helper at `$9F5B` mutates `$0781`, `$00`, `$01`, `$3D`, and `$0780`. It does not write `$10`.

### Fixed helper set

`$E001/$E005` are delay loops. `$E2FA` and `$E30B-$E351` form the known CHR/VRC6 register helper set, writing mapper registers from constants or ZP `$38-$3F`. None writes `$10`.

### IRQ prologue/exit

The fixed IRQ path `$E0F5-$E130` saves/restores A/X/Y and ZP `$00/$01`, bank-switches to raw bank `$01`, dispatches, acknowledges/restores mapper state, and returns with `RTI`. It does not write `$10`.

## Consequence for the NMI-before-renderer window

NMI executes `CLI` at `$E072`, so an IRQ may interrupt before the later `JSR $8001` renderer call at `$E0C7`.

For the currently proven IRQ state domain and handler graph, such an IRQ **preserves ZP `$10`**. Therefore IRQ-side execution does not introduce a hidden attribute-cache initializer or modifier between the pre-render NMI state and `PRG26:$8001`.

Combined with 04F1, the renderer contract is now stronger:

```text
incoming $10 at PRG26:$8001
= shared RAM value produced before/within NMI helper work
  and not modified by the verified IRQ handler graph

then during rendering:
full sprite record       -> final transformed attribute stored to $10
compressed sprite record -> current $10 consumed unchanged
```

This does not yet prove that every pre-render NMI helper preserves `$10`; that is a separate checkpoint.

## Result

**04F2 result: all verified IRQ handlers and their called helper closure preserve ZP `$10`.**

Reproducible audit:

```text
tools/audit_irq_zp10.py
```
