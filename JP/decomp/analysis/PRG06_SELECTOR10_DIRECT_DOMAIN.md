# Checkpoint 04E2 — PRG06/07 direct selector-`$10` frame domain

This checkpoint is intentionally narrower than a full object-family closure. It inventories every **direct bank-resident indexed write** to the renderer selector `$048C` and frame `$0400` in the VRC6 16 KiB bank value `$03` (`PRG06/PRG07`, CPU `$8000-$BFFF`), then resolves the values used by the direct selector-`$10` setup helpers.

The question is whether any directly encoded PRG06/07 setup path can establish selector `$10` with frame `$14`, which would address descriptor `$9FA9`.

## Complete direct selector-store inventory in PRG06/07

Direct indexed stores to `$048C` in this 16 KiB bank pair occur only at:

- `$8D4F`: `STA $048C,Y`
- `$8EB9`: `STA $048C,Y`
- `$8EF9`: `STA $048C,X`
- `$9479`: `STA $048C,X`
- `$9482`: `STA $048C,Y`

The `$8D4F` site stores selector `$0E`.

The other four selector stores explicitly store `$10`:

```asm
8EB7  LDA #$10
8EB9  STA $048C,Y

8EF7  LDA #$10
8EF9  STA $048C,X

9474  STA $0400,X
9477  LDA #$10
9479  STA $048C,X
947C  RTS

947D  STA $0400,Y
9480  LDA #$10
9482  STA $048C,Y
9485  RTS
```

Thus `$9474/$947D` are the canonical bank-local helpers that pair an A-supplied frame with selector `$10`.

## Complete direct frame-store inventory in PRG06/07

Direct indexed stores to `$0400` in the same bank pair occur only at:

### X-indexed

- `$8E34`
- `$8EF4`
- `$9474`
- `$9ADB`
- `$9C58`
- `$9D19`

### Y-indexed

- `$8D4A`
- `$8DFA`
- `$8ED5`
- `$947D`

There are no direct `INC $0400,X` or `DEC $0400,X` instructions in this bank pair.

This does **not** prove that no external fixed-bank/shared helper can ever modify the same object field. That transitive question is deliberately left for a later checkpoint.

## The only literal frame `$14` setter forces selector `$0E`

The only bank-resident literal `$14` frame setup is:

```asm
8D48  LDA #$14
8D4A  STA $0400,Y
8D4D  LDA #$0E
8D4F  STA $048C,Y
```

Therefore this direct setup creates frame `$14` under selector `$0E`, not selector `$10`.

## Direct selector-`$10` spawn/setup values

### `$8EA3` spawn loop

The loop stores selector `$10` at `$8EB9`. Its frame comes from `$9158,Y`, with Y explicitly covering indices `0..5`:

```text
$F4,$F6,$F8,$FA,$FC,$FE
```

### `$8EF2` root setup

```asm
8EF2  LDA #$F0
8EF4  STA $0400,X
8EF7  LDA #$10
8EF9  STA $048C,X
```

So this direct setup is selector `$10`, frame `$F0`.

## `$9474/$947D` helper call domain

All absolute calls/jumps to `$9474` in this bank pair are:

- `JSR`: `$9262,$92C7,$93FB,$975C`
- `JMP`: `$9383,$93ED,$9432,$943E,$9492`

The only absolute call to `$947D` is `$9279`.

Direct reconciliation gives the following frame sources:

- `$9262`: `$F0`
- `$9279`: `$F0`
- `$92C7`: `$D2`
- `$9383`: `$D2`
- `$93FB/$943E`: table `$95F1,Y`
- `$93ED`: table `$95F1,Y` + `$04`
- `$9432`: table `$95F1,Y` + `$02`
- `$9492`: either `$F0` or the incoming Y; its only callers supply `$D2` or a value loaded by `$9559`
- `$975C`: table `$9828,Y`

The reconciled `$9559` frame table is:

```text
$95F1: D2 C0 C6 CC C0 C6
```

The `$975C` frame table is:

```text
$9828: E4 E0 E0
```

Combining the directly proven helper inputs gives this selector-`$10` helper frame set:

```text
$C0,$C2,$C4,$C6,$C8,$CA,$CC,$CE,
$D0,$D2,$D4,$D6,$E0,$E4,$F0
```

Adding the direct `$8EA3` spawn frames yields the full currently proved **direct PRG06/07 selector-`$10` setup domain**:

```text
$C0,$C2,$C4,$C6,$C8,$CA,$CC,$CE,
$D0,$D2,$D4,$D6,$E0,$E4,$F0,
$F4,$F6,$F8,$FA,$FC,$FE
```

Frame `$14` is absent.

## Other direct frame stores do not introduce `$14`

The remaining direct bank-local frame stores are fixed to values other than `$14`, except the `$8D4A` selector-`$0E` setup already covered.

In particular, `$9ADB` stores the return value of fixed-bank helper `$FF24`. `$FF24` loads A=`$00`, performs only `STA` operations afterward, and returns with A still zero, so `$9ADB` stores frame `$00`.

## Result

**No direct indexed PRG06/07 selector-`$10` setup path produces frame `$14`.** The bank pair's only literal frame `$14` setup explicitly selects `$0E`.

This eliminates direct PRG06/07 selector setup as the route to `$9FA9`, but it does **not** yet prove that a selector-`$10` object cannot later receive frame `$14` through a transitive fixed-bank/shared helper or code in another PRG bank.

That transitive mutation question is the next checkpoint.

Reproducible audit: `tools/audit_prg06_selector10_direct.py`.
