# Checkpoint 04E5 — primary type `$08` vertical path toward `$A0-$A7`

This checkpoint traces only the base-Y/velocity path for the already-proven primary-type `$08`, internal-state `$01` route to `PRG06:$823E`.

## State `$00` initializes Y and velocity

The type-`$08` behavior enters state `$00` when `$0606,X == 0`.

At `PRG06:$816C` it performs:

```asm
816C  LDA #$C0
816E  STA $041C,X
8171  JSR $FF15
8174  LDA #$FE
8176  STA $0520,X
...
817E  INC $0606,X
```

Fixed helper `$FF15` clears all four movement bytes:

```asm
FF15  LDA #$00
FF17  STA $04F2,X
FF1A  STA $0509,X
FF1D  STA $0520,X
FF20  STA $0537,X
FF23  RTS
```

Therefore state `$00` leaves the object with:

```text
base Y       $041C = $C0
vertical low $0537 = $00
vertical high $0520 = $FE
next state   $0606 = $01
```

For the fixed movement integrator, `$FE` is the signed high-byte contribution `-2`.

## Fixed bank-$0B movement is exactly -2 pixels per tick

The post-behavior movement path in VRC6 bank `$0B` contains:

```asm
8024  CLC
8025  LDA $04DB,X
8028  ADC $0537,X
802B  STA $04DB,X
802E  LDA $041C,X
8031  ADC $0520,X
8034  STA $041C,X
8037  RTS
```

With `$0537=$00` and `$0520=$FE`, and with no state-`$01` write to either velocity byte before this integrator, each scheduled movement tick changes base Y by exactly `-2`.

Thus the state-`$01` trajectory begins:

```text
$C0, $BE, $BC, ... $AA, $A8, $A6, $A4, $A2, $A0, $9E, ...
```

## State `$01` target gate

At `PRG06:$81E5`, state `$01` computes an index from `$0633+$0645` and compares the corresponding target-Y byte against current `$041C,X`:

```asm
81E5  LDA $0633,X
81E8  CLC
81E9  ADC $0645,X
81EC  TAY
81ED  LDA $840F,Y
81F0  CMP $041C,X
81F3  BCC $8201
81F5  STA $041C,X
81F8  INC $0606,X
...
8200  RTS
```

If target Y is below current Y, execution branches to `$8201` and state `$01` continues. Otherwise the object is clamped to the target and advances state.

State `$00` also uses the same sum as an index into the 15-byte block `$81CE-$81DC`; `$81DD` is independently proven executable because `$8148` jumps directly to it. The consumer-valid table domain therefore currently established for that state-0 lookup is indices `$00-$0E`.

For those same indices, target bytes `$840F[0..14]` are:

```text
70 90 70 98 78 98 70 90 70 60 50 60 70 60 50
```

The maximum is `$98`.

Therefore, **for every currently table-valid index `$00-$0E`, state `$01` cannot terminate before passing below `$A8`**.

## `$A0-$A7` is then deterministic

At current Y `$A8`, every established target is `<= $98`, so state `$01` continues and the fixed movement step changes Y to `$A6`.

On the next behavior call, `$823E` sees `$A6`, which lies in `$A0-$A7`:

```asm
823E  LDY #$08
8240  LDA $041C,X
8243  CMP #$A8
8245  BCS $824F
8247  LDY #$09
8249  CMP #$A0
824B  BCS $824F
824D  LDY #$0A
```

So any type-`$08`, state-`$01` object operating with the established index domain necessarily selects animation ID `$09` at least once. Checkpoints 04E3/04E4 already prove that this installs selector `$10`, is ticked by `$EF93`, writes frame `$14`, and resolves to descriptor `$9FA9`.

## Remaining producer-bound caveat

This checkpoint does **not** yet close the producer domain of `$0645,X` for root primary-type `$08` objects.

The bytes prove:

- `$0633` is incremented and masked to three bits in state `$00`;
- `$0645` participates in the state-0 and state-1 table indices;
- indices `$00-$0E` are the currently established consumer-valid state-0 table domain;
- within that domain, traversal through `$A0-$A7` is mathematically unavoidable.

They do **not yet prove** that every normal root type-`$08` producer supplies `$0645` such that `$0633+$0645` remains in `$00-$0E`.

Accordingly, normal-gameplay `$9FA9` reachability is now reduced to one producer-domain question: prove the root/creation values of `$0645` for primary type `$08`. Do not infer that bound merely from the table shape.

Reproducible audit: `tools/audit_prg06_type08_vertical_path.py`.
