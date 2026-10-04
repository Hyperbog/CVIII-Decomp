# Checkpoint 04E1 — PRG18 type `$E1` selector-`$10` frame domain

This checkpoint deliberately covers only one proven selector-`$10` family: the PRG18 object created as type `$E1` at `$9E0F`. It asks whether that family can mutate its frame byte to `$14`, which would select descriptor `$9FA9` under selector `$10`.

## Creation/setup path

The creation loop at `PRG18:$9DDE` writes a new object through Y. Its render setup is:

```asm
9DE7  STA $0565,Y
9DEA  CMP #$0E
9DEC  BCC $9DF2
9DEE  CMP #$12
9DF0  BCC $9DF6
9DF2  LDA #$EC
9DF4  BNE $9DF8
9DF6  LDA #$E8
9DF8  STA $0400,Y
9DFB  LDA #$10
9DFD  STA $048C,Y
...
9E0F  LDA #$E1
9E11  STA $05EF,Y
9E14  LDA #$00
9E16  STA $05C1,Y
```

Therefore a type-`$E1` object begins with:

- selector `$048C = $10`
- frame `$0400 = $E8` when the preceding value is `$0E..$11`
- otherwise frame `$0400 = $EC`
- state `$05C1 = 0`

## Dispatcher ownership

The PRG18/19 object dispatcher masks `$05EF,X` with `$7F`, subtracts one, and indexes the type-state pointer table at `$8928`.

For type `$E1`:

- `(E1 & 7F) - 1 = $60`
- pointer entry `$8928 + 2*$60 = $89E8`
- `$89E8` contains `$8FC4`
- the next type (`$E2`) points to `$8FD0`

Thus type `$E1` owns exactly six two-byte state records at `$8FC4-$8FCF`:

| state | action | parameter index |
|---:|---:|---:|
| `$00` | `$3A` | `$69` |
| `$01` | `$0B` | `$0F` |
| `$02` | `$05` | `$00` |
| `$03` | `$22` | `$22` |
| `$04` | `$46` | `$58` |
| `$05` | `$21` | `$01` |

The action pointer table at `$85CC` resolves these to:

- `$3A -> $9C68`
- `$0B -> $9482`
- `$05 -> $9623`
- `$22 -> $9897`
- `$46 -> $9B3F`
- `$21 -> $8662`

## Only frame mutation in this six-state path

Actions `$3A`, `$0B`, `$05`, `$22`, and `$21` do not write/increment/decrement `$0400,X` on their reconciled action bodies.

State `$04` executes action `$46` with parameter index `$58`. The three parameter bytes at `$8FE2 + 3*$58 = $90EA` are:

```text
FF 00 FF
```

Action `$46` at `$9B3F` first advances state. Its first parameter (`$13`, record byte 1) controls selector/frame behavior:

```asm
9B4D  LDY #$01
9B4F  LDA ($02),Y      ; parameter 1
9B51  CMP #$FF
9B53  BEQ $9B6A
...
9B63  DEC $0400,X
9B66  DEC $0400,X
9B69  RTS
9B6A  INC $0400,X
9B6D  INC $0400,X
9B70  RTS
```

Because type `$E1` supplies parameter 1 = `$FF`, its state-4 transition adds exactly two to the existing frame and does not replace the selector.

Therefore the complete proven type-`$E1` frame evolution is:

```text
$E8 -> $EA
or
$EC -> $EE
```

State `$05` resolves to `$8662`, which is `RTS`, so there is no subsequent type-`$E1` state-table frame mutation.

## Result

**Type `$E1` cannot reach selector `$10` + frame `$14` through its authoritative six-state PRG18 state machine.** It therefore does not establish normal-game reachability of descriptor `$9FA9`.

This is a narrow result. It does not yet close the selector-`$10` families created/managed in PRG06, nor arbitrary external mutation of a type-`$E1` object's render fields.

Reproducible audit: `tools/audit_prg18_e1_frame.py`.
