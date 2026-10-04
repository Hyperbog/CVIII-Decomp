# Checkpoint 04F3 — fixed-bank pre-render NMI ZP `$10` preservation

This checkpoint asks one bounded question: within the fixed-bank NMI code and helpers in `PRG31:$E057-$E365`, can execution before `PRG26:$8001` modify the persistent OAM attribute cache at ZP `$10`?

Authoritative ROM SHA-256:

```text
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
```

## Byte budget

Primary new ROM span:

```text
PRG31 CPU $E057-$E365
size 0x30F = 783 bytes
SHA-256 b0e367bb5971310da3bbd066f54cc3def543e82134f4df6b7b82feef06166176
```

No external helper body is followed beyond this span in 04F3.

## Renderer-reaching NMI path

The relevant fixed NMI sequence begins at `$E057`. It executes `CLI` at `$E072`, performs the frame/NMI helper work, then selects raw bank `$0D` and calls the renderer:

```asm
E072  CLI
...
E08C  JSR $E16C
E08F  JSR $ED46          ; external dependency
...
E0A1  JSR $E131
E0A4  JSR $E2D6
...
E0B9  JSR $E238
E0BC  JSR $E264
E0BF  JSR $E35C
E0C2  LDA #$0D
E0C4  JSR $E2D0
E0C7  JSR $8001          ; PRG26 renderer
```

The NMI body itself contains no direct store/RMW to `$10`.

## In-span helper closure

The renderer-reaching path calls these helpers whose bodies are fully inside the 783-byte span:

```text
$E16C
$E131
$E2D6
$E238
$E264
$E2D0
$E35C
```

Their in-span code contains no direct `STA/STX/STY`, `INC/DEC`, or shift/rotate destination at ZP `$10` or absolute `$0010`.

### Indexed-write alias audit

The only in-span indexed writes/RMWs that need alias reconciliation are:

```asm
E287  STA $28,X
E289  STA $F8,X
E28B  STY $2A,X
E28D  STY $FA,X

E2AF  ROL $00,X
E2BA  ROL $01,X
```

The caller controls X:

- `$E264` calls `$E29B` with X=`$00`, then X=`$02`; therefore `$E2AF/$E2BA` can touch only `$00-$03`.
- `$E27A` calls `$E280` with X=`$00`, then increments X to `$01` and falls through `$E280`; therefore `$E287-$E28D` can touch only `$28/$29`, `$F8/$F9`, `$2A/$2B`, `$FA/$FB`.

None can alias `$10`.

## External dependencies deliberately left open

04F3 finds three pre-render calls that leave the primary byte span.

### `$ED46`

NMI directly executes:

```asm
E08F  JSR $ED46
```

`$ED46` is outside this checkpoint and is not assumed to preserve `$10` yet.

### Banked `$89E2`

`$E238` explicitly selects raw bank `$0C` and then calls CPU `$89E2`:

```asm
E238  LDA #$FF
E23A  STA $26
E23C  LDA #$0C
E23E  JSR $E2D0
E241  JSR $89E2
...
```

The called banked routine is outside this fixed-bank checkpoint. Its `$10` behavior remains open.

### `$E7FB` inline dispatcher

`$E35C` executes:

```asm
E35C  INC $1B
E35E  LDA $18
E360  JSR $E7FB
```

`$E7FB` is outside the primary span and uses inline dispatch data beginning after the call. Its reachable targets are intentionally deferred.

## Consequence

Within `PRG31:$E057-$E365` itself, the fixed-bank NMI path preserves ZP `$10`.

04F3 does **not** yet prove complete pre-render NMI preservation, because `$ED46`, banked `$89E2`, and `$E7FB`/its dispatched targets remain unresolved.

Combined state after 04F2/04F3:

```text
verified IRQ graph        -> preserves $10
fixed NMI span E057-E365 -> preserves $10
external NMI dependencies -> still open
```

## Result

**04F3 result: the fixed-bank pre-render NMI span does not modify ZP `$10`; three external helper dependencies remain.**

Reproducible audit: `tools/audit_nmi_fixed_zp10.py`.
