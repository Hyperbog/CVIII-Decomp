# Checkpoint 04E6 — primary type `$08` root `$0645` producer domain

This checkpoint closes the remaining root-construction question from 04E5: whether a normal primary-type `$08` object can enter state `$00` with a nonzero `$0645,X` large enough to invalidate the `$0633+$0645` table bound.

All claims below are verified against the exact Japanese ROM SHA-256:

```text
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
```

## Fixed full-object reset clears `$0645`

The authoritative fixed-bank helper `$FF24` begins by clearing movement state through `$FF15`, then clears the object work fields.

Its tail is:

```asm
FF42  STA $05D8,X
FF45  STA $05EF,X
FF48  STA $0606,X
FF4B  STA $061D,X
FF4E  STA $0633,X
FF51  STA $0645,X
FF54  RTS
```

Therefore any constructor that routes through `$FF24` establishes:

```text
$0606 = $00
$061D = $00
$0633 = $00
$0645 = $00
```

before object-specific state begins.

## Standard low-slot allocator also zeroes `$0645`

The common low-slot allocator in physical PRG18 starts at CPU `$86E3`.

It:

1. preserves the requested primary type in ZP `$11`;
2. searches for a free ordinary object slot;
3. invokes `$86D1`;
4. `$86D1` invokes the `$8692/$869D` reset block;
5. that reset block clears `$0606/$061D/$0633/$0645`;
6. only then does `$86E3` store the caller-supplied primary type into `$054E,X`.

The relevant reset tail is:

```asm
86A3  STA $05EF,X
86A6  STA $0606,X
86A9  STA $061D,X
86AC  STA $0633,X
86AF  STA $0645,X
```

Thus a caller-supplied type `$08` created through the standard allocator also begins with `$0645=$00`.

## PRG20's `$73 -> $0645` path cannot create type `$08`

During the investigation a superficially dangerous path was found in physical PRG20.

The Japanese ROM path at `$81AF` does:

```asm
81AF  JSR $FF24
81B2  LDY #$00
81B4  LDA ($00),Y
81B6  STA $054E,X
...
81D7  LDA $054E,X
81DA  SEC
81DB  SBC #$80
81DD  TAY
81DE  LDA $8329,Y
81E1  STA $05EF,X
81E4  LDA $73
81E6  STA $0645,X
81E9  RTS
```

This is the high-type room/spawner construction path, not the primary-type `$08` path.

The two record-pointer tables consumed immediately before `$81AF` are at CPU `$A56B` and `$A66B` in the same 16 KiB PRG window. A ROM-backed audit enumerates every even selector slot that resolves to an address inside `$8000-$BFFF`.

Result:

```text
valid pointed records checked: 251
records beginning with type $08: 0
low first-byte values present: $00 only
all nonempty record first bytes: $80 or greater
```

So the one constructor that deliberately writes room-position byte `$73` into `$0645` cannot instantiate primary type `$08`.

This is important because the public US disassembly uses different addresses/constants in this area; the committed audit uses only the Japanese ROM bytes.

## No literal direct type-`$08` constructor

The complete 256 KiB PRG contains no byte sequence:

```asm
LDA #$08
STA $054E,X
```

That does not by itself prove constructor closure, but it rules out a separate simple literal bypass.

The dynamic low-type constructors examined during 04E6 either:

- route through `$FF24` / the PRG18 reset allocator before storing the requested type;
- draw from finite tables that do not contain `$08`; or
- are transformations that do not leave the slot dispatchable as primary type `$08`.

The ROM-backed audit locks the reusable constructor facts rather than relying on those navigation observations alone.

## Consequence for the 04E5 trajectory

The normal root contract for primary type `$08` is now:

```text
before state $00:
$0606 = $00
$0633 = $00
$0645 = $00
```

Checkpoint 04E5 already proved state `$00` performs:

```text
$041C = $C0
$0520 = $FE
$0537 = $00
$0633 := ($0633 + 1) & $07
$0606 := $01
```

Therefore the first state-`$01` target index is not merely bounded by `$00-$0E`; it is exactly:

```text
$0633 + $0645 = $01 + $00 = $01
```

and the target is:

```text
$840F[$01] = $90
```

With exact `-2` vertical motion, the authoritative behavior-call trajectory necessarily includes:

```text
$A6, $A4, $A2, $A0
```

Each lies in the `$A0-$A7` window selecting animation ID `$09`.

Combined with checkpoints 04E3 and 04E4:

```text
normal root type $08
 -> state $00 reset/initialization
 -> state $01 target $90
 -> Y passes through $A6/$A4/$A2/$A0
 -> selector $10 / animation $09
 -> fixed $EF93 writes frame $14
 -> selector $10 + frame $14
 -> PRG26 descriptor $9FA9
```

So `$9FA9` is now proven reachable through a normal root-construction/state-machine path in the Japanese ROM.

## Scope limit

This checkpoint closes the **root constructor / `$0645` provenance needed for the type-`$08` `$9FA9` path**.

It does not claim that every transient write to `$054E` anywhere in the 256 KiB PRG has been semantically classified. That broader whole-ROM type-transition census is separate work.

The next renderer question is no longer descriptor reachability. It is the incoming persistent OAM attribute-cache value in ZP `$10` when reachable `$9FA9` begins with compressed records.

Reproducible audit: `tools/audit_prg06_type08_0645.py`.
