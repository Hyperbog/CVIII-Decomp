# Checkpoint 04F2 — IRQ-side ZP `$10` interference

This checkpoint answers one narrow question: after NMI executes `CLI` and before `PRG26:$8001` renders OAM, can any **verified IRQ handler** modify the persistent OAM attribute cache at ZP `$10`?

All claims are verified against the Japanese target ROM SHA-256:

```text
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
```

Primary new ROM span:

```text
PRG02/PRG03 CPU $9F99-$A526
size: 0x58E = 1,422 bytes
SHA-256: fb0f709699ad64b6cb49fa4eaeb2de8e1a260e23745341fc2f48b38fedd8ded3
```

The already-proven IRQ table remains `PRG02:$9F01-$9F5A`, 45 states `$00-$2C`.

## Direct handler writes

The complete `$9F99-$A526` span contains no direct official-6502 write/RMW encoding that names ZP `$10` or absolute `$0010` as its destination.

Manual instruction-boundary reconciliation of the verified handler entries also finds no indexed/indirect store on a reachable IRQ path that can alias ZP `$10`.

Reachable zero-page writes in this handler set are instead to locations such as:

```text
$00
$3C-$3F
$42
$6A
$6C/$6D
$79
$D2/$D3
```

There is no accepted handler instruction storing to `$10`.

## Local helper `$9F5B`

Handlers `$A078` and `$A16F` can call local helper `$9F5B`.

`$9F5B-$9F8A` manipulates `$0780/$0781`, pointer scratch `$00/$01`, and ZP `$3D`; it does not write `$10`.

## Fixed helper call set

Disassembly of all verified handler entrypoints reduces external fixed-bank calls to:

```text
$E001
$E005
$E2FA
$E30B
$E316
$E32B
$E331
$E33C
$E347
$E351
```

These are delay/register/mapper restore helpers already mapped in the fixed bank. Their bodies contain no write to ZP `$10`.

The fixed IRQ prologue/epilogue `$E0F5-$E130` also does not touch `$10`; it saves/restores `$00/$01`, A/X/Y, switches the IRQ bank, dispatches, acknowledges/disables IRQ state, restores the tracked PRG bank, then returns with `RTI`.

## NMI consequence

NMI executes:

```asm
E072  CLI
...
E0C2  LDA #$0D
E0C4  JSR $E2D0
E0C7  JSR $8001
```

IRQ service can therefore occur during the pre-render interval. However, within the currently verified IRQ dispatch/state-machine implementation, such an IRQ **preserves ZP `$10`**.

This removes the interrupt-side caveat left by 04F1 for the verified IRQ handler set.

The incoming `$10` observed by `PRG26:$8001/$8070` is therefore not altered by the mapped IRQ machinery. Its variability comes from ordinary shared-RAM/render history established in 04F1, not from these IRQ handlers.

## Fidelity rule

A native IRQ implementation must not invent save/restore or initialization of `$10`.

Correct behavior is simpler:

```text
IRQ entry: leave $10 alone
IRQ handlers: leave $10 alone
IRQ exit: leave $10 alone
```

The renderer must still consume whatever shared-RAM value is present when it begins.

## Scope limit

This checkpoint does **not** prove that no code anywhere in the whole ROM can write ZP `$10`.

It proves only that the verified IRQ entry, 45-state handler set, their local `$9F5B` helper, and their known fixed helper calls do not write it.

Reproducible audit: `tools/audit_irq_zp10.py`.
