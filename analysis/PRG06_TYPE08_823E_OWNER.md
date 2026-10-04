# Checkpoint 04E4 — owner/scheduler link for PRG06 `$823E`

This checkpoint closes the runtime ownership and scheduler link around the PRG06 branch that can select animation ID `$09` under renderer selector `$10`.

It intentionally does **not** yet prove that the required base-Y window `$A0-$A7` occurs in normal gameplay. That value-provenance question is the next checkpoint.

## Fixed object-loop slot range

The fixed object loop starts with:

```asm
FDEA  LDX #$01
FDEC  LDA $054E,X
...
FE6E  INX
FE6F  CPX #$13
FE71  BCS $FE76
FE73  JMP $FDEC
```

Therefore the ordinary active-object loop processes exactly:

```text
X = $01..$12
```

These are renderer/object slots 1 through 18.

## Primary type `$08` dispatches to PRG06 `$8021`

For primary types below `$30`, the fixed loop selects VRC6 16 KiB bank `$09` and calls its common object entry `$8001`:

```asm
FE05  CMP #$30
FE07  BCS $FE16
FE09  LDA #$09
FE0B  JSR $E2D0
FE0E  JSR $8001
```

Inside bank `$09`, the common dispatcher uses `$054E,X` as the primary type. Its bank-selector table is at `$8163` and its behavior-pointer table is at `$81E9`.

For primary type `$08`:

```text
bank selector: $8163 + $08 = $03
behavior ptr:  $81E9 + 2*($08-1) = $8021
```

`$8155` routes nonzero bank-selector entries through fixed helper `$E5DA`, which temporarily selects that bank and invokes the pointer in `$0000/$0001`.

Therefore an active primary-type `$08` object in the fixed loop executes:

```text
VRC6 bank $03 -> PRG06:$8021
```

with the same X slot from `$01..$12`.

## Internal state path to `$823E`

`PRG06:$8021` reads internal byte `$0606,X`. The state-machine branch at `$8143` is:

```asm
8143  LDY $0606,X
8146  BEQ $814D
8148  JMP $81DD
...
81DD  DEY
81DE  BNE $8254
81E0  LDA #$40
81E2  STA $0470,X
```

Thus internal state `$0606,X = $01` selects the `$81E0` path.

That path can reach `$823E` through the directly encoded branches at `$8206` and `$8210`. At `$823E`, base Y selects animation ID `$08/$09/$0A`:

```asm
823E  LDY #$08
8240  LDA $041C,X
8243  CMP #$A8
8245  BCS $824F
8247  LDY #$09
8249  CMP #$A0
824B  BCS $824F
824D  LDY #$0A
824F  LDA #$10
8251  JMP $EF7F
```

Therefore the exact middle branch is:

```text
primary type $08
internal state $0606 = $01
base Y $041C = $A0..$A7
  -> selector $10
  -> animation ID $09
```

## Same fixed-loop iteration reaches the animation tick

`$81E0` writes `$0470,X = $40` before the animation selection. Consequently:

- bit `$40` is set;
- bit `$20` is clear.

After bank-$09` common dispatch returns, the same fixed object-loop iteration executes:

```asm
FE45  LDA $0470,X
FE48  AND #$40
FE4A  BEQ $FE54
FE4C  LDA #$0B
FE4E  JSR $E2D0
FE51  JSR $8001       ; bank-$0B movement integrator

FE54  LDA $054E,X
FE57  BEQ $FE6E
FE59  LDA $0470,X
FE5C  AND #$20
FE5E  BNE $FE63
FE60  JSR $EF93       ; shared animation tick
```

So the type-$08 `$823E` path is not detached from the fixed scheduler: the same X slot is subsequently eligible for `$EF93` in the same object-loop iteration.

## Connection to descriptor `$9FA9`

Checkpoint 04E3 proved:

```text
selector $10
animation ID $09
cursor 0
  -> fixed animation record $F28D = 14 08 02
  -> $EF93 writes frame $14 to $0400,X
```

The renderer's first-level selector table gives:

```text
selector $10 -> frame-pointer table $9E6D
```

and frame offset `$14` in that table is:

```text
$9E6D + $14 -> pointer $9FA9
```

Therefore the complete machine path is now reconciled as:

```text
fixed object slot X=$01..$12
primary type $08
  -> bank-$09 common dispatcher
  -> bank-$03 PRG06:$8021
  -> internal state $01
  -> base Y $A0..$A7
  -> PRG06:$823E selects selector $10 / animation $09
  -> same fixed-loop iteration reaches $EF93
  -> frame $14
  -> PRG26 descriptor $9FA9
```

## What this proves and what remains open

This proves the **owner, slot range, dispatch chain, scheduler chain, and descriptor resolution** for the `$823E` route.

The remaining reachability issue is now only the value provenance of `$041C,X`:

- does a primary-type `$08`, internal-state `$01` object actually attain base Y `$A0-$A7` on an authoritative gameplay path?

Until that is proved, `$9FA9` is machine-reachable under an exact state predicate, but normal-gameplay reachability is not yet claimed.

Reproducible audit: `tools/audit_prg06_type08_owner.py`.
