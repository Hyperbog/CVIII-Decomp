# `$9FA9` reachability checkpoint

This file records a deliberately narrow reachability pass for sprite descriptor `$9FA9`. It does **not** attempt to reconstruct the full object system.

## Required renderer state

Selector `$10` points to master frame table `$9E6D`. Frame offset `$14` indexes pointer bytes `$9E81/$9E82`, which resolve to descriptor `$9FA9`.

Therefore an object reaches `$9FA9` only when, at render time:

- `$048C[slot] == $10`
- `$0400[slot] == $14`

The descriptor then begins with three compressed sprites and consumes the incoming cached OAM attribute in zero-page `$10`.

## Direct selector-`$10` producer families checked

### PRG06 `$8E9A..$8F0E`

The spawn loop at `$8EB7` stores selector `$10` to `$048C,Y`. Its frame byte comes from `$9158,Y`; the six values used by the loop are:

`$F4,$F6,$F8,$FA,$FC,$FE`.

The parent/current object at `$8EF4/$8EF7` receives frame `$F0` and selector `$10`.

None of these direct assignments uses frame `$14`.

### PRG06 helper `$9474/$947D`

The helpers are:

```asm
9474  STA $0400,X
9477  LDA #$10
9479  STA $048C,X
947C  RTS

947D  STA $0400,Y
9480  LDA #$10
9482  STA $048C,Y
9485  RTS
```

Thus they atomically pair an incoming frame byte with selector `$10`.

All direct call sites in this physical bank were reconciled. Their immediate/table-derived frame values include `$F0`, `$D2`, `$C0`, `$C6`, `$CC`, `$E4`, and `$E0`; no checked call supplies `$14`.

The dynamic return helper `$9559` reads its frame byte from `$95F1,Y`; the six-byte table is:

`D2 C0 C6 CC C0 C6`.

The `$975C -> $9474` path uses `$9828,Y`, whose reachable three values are:

`E4 E0 E0`.

### PRG18 `$9DDE..$9E1E`

This path writes selector `$10` at `$9DFB`. Immediately before it, frame is chosen as `$EC` or `$E8` and stored at `$9DF8`.

Again, direct initialization is not frame `$14`.

## Separate frame-`$14` transition

A distinct object-state routine in physical PRG22 contains:

```asm
873F  INC $05C1,X
8742  INC $05C1,X
8745  LDA #$14
8747  STA $0400,X
874A  JSR $8309
874D  JMP $FF15
```

This transition writes frame offset `$14` but does **not** write `$048C,X` in the local path. Therefore it can preserve a pre-existing sprite-set selector while moving the object to frame `$14`.

This is the first direct evidence explaining how `$9FA9` can be a later animation/state frame rather than a creation-time frame.

## What is proved

- `$9FA9` requires selector `$10` plus frame `$14`.
- The checked direct selector-`$10` creation/setup paths do not initialize frame `$14`.
- A separate executable state transition writes frame `$14` without changing the selector in that path.
- Consequently, a faithful analysis must treat selector and frame as independently persistent object fields; it is unsafe to infer frame domain solely from selector-setup call sites.

## What is not yet proved

This checkpoint does **not** yet prove that the PRG22 `$8745` transition is reachable for an object whose selector is `$10`. That requires tracing the owning object-handler/state dispatch far enough backward to its creation/setup path.

It also does not prove which object slot numbers can reach `$9FA9`, nor whether a lower-numbered rendered slot always establishes cached attribute `$10` before such an object is processed.

## Next narrow question

Trace only the owner/entry path of the PRG22 routine containing `$8745` and connect it to the object's creation/setup routine. The target proof is binary: either establish that this handler can operate on a selector-`$10` object, or prove it belongs to a different selector family. Do not expand into unrelated object types.
