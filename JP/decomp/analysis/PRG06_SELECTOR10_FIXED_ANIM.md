# Checkpoint 04E3 — PRG06 selector-`$10` transitive fixed animation path

This checkpoint is limited to fixed/shared routines that can mutate `$0400` after PRG06/07 has established selector `$10`.

## PRG06 chooses animation ID `$09`

The PRG06 path at `$823E-$8251` derives a Y animation ID from the current object's base Y `$041C,X`:

```asm
823E  A0 08     LDY #$08
8240  BD 1C 04  LDA $041C,X
8243  C9 A8     CMP #$A8
8245  B0 08     BCS $824F
8247  A0 09     LDY #$09
8249  C9 A0     CMP #$A0
824B  B0 02     BCS $824F
824D  A0 0A     LDY #$0A
824F  A9 10     LDA #$10
8251  4C 7F EF  JMP $EF7F
```

Therefore:

- base Y `>= $A8` -> animation ID `$08`
- base Y `$A0-$A7` -> animation ID `$09`
- base Y `< $A0` -> animation ID `$0A`

All three paths select renderer selector `$10`.

## `$EF7F` initializes shared animation state

Fixed helper `$EF7F` is:

```asm
EF7F  9D 8C 04  STA $048C,X
EF82  98        TYA
EF83  9D AA 05  STA $05AA,X
EF86  A9 00     LDA #$00
EF88  9D 93 05  STA $0593,X
EF8B  A9 01     LDA #$01
EF8D  9D 7C 05  STA $057C,X
EF90  60        RTS
```

For the middle PRG06 branch this establishes:

- `$048C,X = $10`
- `$05AA,X = $09`
- `$0593,X = $00`
- `$057C,X = $01`

`$05AA` is the animation-record index, `$0593` is the even frame-offset cursor, and `$057C` is the countdown consumed by the fixed animation updater.

## `$EF93` consumes that state and writes `$0400,X`

`$EF93` decrements `$057C,X`. When it reaches zero it falls into `$EF99`, which selects an animation table from `$048C,X`, chooses the 3-byte record indexed by `$05AA,X`, adds `$0593,X` to the record's base frame, and stores the result to `$0400,X` at `$EFB5`.

For selector `$10`, the pointer table at `$EFD2` resolves to `$F272`:

```text
selector $10 -> $F272
```

The selector-`$10` block is `$F272-$F37C`, exactly 267 bytes / 89 three-byte animation records.

Animation record `$09` is at:

```text
$F272 + 3*$09 = $F28D
$F28D: 14 08 02
```

With `$0593,X = 0`, the first `$EF93` update therefore performs:

```text
$0400,X = $14
```

The same record has limit `$02`, so its only frame is `$14`.

## Fixed object-loop scheduling evidence

The fixed-bank object loop at `$FDEC-$FE73` iterates X from `$01` through `$12`. After object-specific behavior returns, active objects whose `$0470` bit `$20` is clear execute:

```asm
FE54  BD 4E 05  LDA $054E,X
FE57  F0 15     BEQ $FE6E
FE59  BD 70 04  LDA $0470,X
FE5C  29 20     AND #$20
FE5E  D0 03     BNE $FE63
FE60  20 93 EF  JSR $EF93
```

Thus `$EF93` is the shared per-object animation tick for that active-object loop.

The PRG06 path that can reach `$823E` passes through `$81E0`, which writes `$40` to `$0470,X`. That value has bit `$20` clear, so this path does not itself suppress the `$FE60 -> $EF93` update.

## Result

Checkpoint 04E2 was correct that **direct PRG06 frame stores** never pair selector `$10` with frame `$14`, but the transitive fixed animation system does provide exactly that combination:

```text
PRG06 base Y $A0-$A7
  -> selector $10 + animation ID $09 via $EF7F
  -> shared $EF93 animation update
  -> selector-$10 record 9 at $F28D
  -> frame $14 in $0400,X
  -> renderer descriptor $9FA9
```

This identifies the missing machine mechanism for selector `$10` + frame `$14`.

### Scope limit

The remaining reachability question is narrower: prove the exact runtime ownership/slot path from the PRG06 `$823E` branch through the scheduler for the object(s) that can render `$9FA9`, and then determine the incoming cached attribute `$10` at that render ordering point. This checkpoint does not assign higher-level object/player semantics yet.

Reproducible audit: `tools/audit_prg06_fixed_animation.py`.
