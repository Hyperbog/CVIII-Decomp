# PRG22 `$8745` owner checkpoint

Checkpoint 04D asks whether the frame-`$14` write at `PRG22:$8745` can be the missing path to sprite descriptor `$9FA9`, which requires selector `$10` plus frame `$14`.

## Dispatcher ownership

The PRG22/23 object dispatcher at `PRG23:$BD11` reads object type from `$05EF,X`, uses the type to fetch a state-table pointer from `$BEA3`, then indexes the current state `$05C1,X` as a four-byte record. Record byte 0 is an action ID dispatched through the action-pointer tables beginning at `$BD67/$BE67`.

For object type `$26`, `$BEA3 + 2*$26` points to state table `$AE6A`.

The next distinct packed state-table boundary is `$AF2A`, so type `$26` owns exactly 48 four-byte state records at `$AE6A-$AF29`.

## Actions that reach `$8745`

Two action entries can reach the shared tail containing `$8745`:

- action `$5C` -> `PRG22:$871E`
- action `$8A` -> `PRG22:$86F2`

Direct state-table reconciliation finds both action IDs only in the type-`$26` state table for this ownership path:

- state `$08`: action `$5C`
- state `$14`: action `$5C`
- state `$2B`: action `$8A`

`$871E` reaches `$8734` on its active path. `$86F2` can also jump to `$8734`. The shared tail then executes:

```asm
8734  CLC
8735  LDA $041C,X
8738  AND #$F0
873A  ADC #$08
873C  STA $041C,X
873F  INC $05C1,X
8742  INC $05C1,X
8745  LDA #$14
8747  STA $0400,X
874A  JSR $8309
874D  JMP $FF15
```

Thus `$8745` is a shared type-`$26` frame transition, not a standalone generic frame setter.

## Selector setup immediately before action `$5C`

Type `$26` state `$07` is:

```text
0B 12 12 00
```

Action `$0B` resolves to `PRG22:$8519`, which loads record byte 1 into `$048C,X` and record byte 2 into `$0400,X`:

```asm
8519  LDY #$01
851B  LDA ($02),Y
851D  STA $048C,X
8520  INY
8521  LDA ($02),Y
8523  STA $0400,X
8526  JMP $8357
```

Therefore state `$07` explicitly sets:

- selector `$048C,X = $12`
- frame `$0400,X = $12`

and advances to state `$08`, whose action is `$5C -> $871E`.

The same pair occurs again at states `$13/$14`:

- state `$13`: `0B 12 12 00`
- state `$14`: `5C 00 00 00`

So both ordinary `$5C` entries reach `$8745` from a directly proven selector-`$12` setup, not selector `$10`.

## Full explicit selector domain inside type `$26`

Every state record in the 48-state type-`$26` table whose action is `$0B` was enumerated. Its selector parameter is always either:

- `$12`, or
- `$08`

There is no explicit selector `$10` setup anywhere in the type-`$26` state table.

This is enough to reject `PRG22:$8745` as the previously hypothesized selector-`$10` + frame-`$14` route to descriptor `$9FA9` within the authoritative type-`$26` object state machine.

## Scope limit

This checkpoint does **not** claim that arbitrary external code could never mutate `$048C,X` for a type-`$26` object. It proves the narrower decompilation fact needed here:

- `$8745` is owned by type `$26` action/state flow,
- its normal `$5C` entries are explicitly preceded by selector `$12`, and
- type `$26`'s own explicit selector-setting records contain only `$12/$08`, never `$10`.

Therefore `$8745` does not establish `$9FA9` reachability. The missing selector-`$10` / frame-`$14` combination must come from another transition mechanism if `$9FA9` is reachable in normal gameplay.

Reproducible audit: `tools/audit_prg22_8745_owner.py`.
