# Checkpoint 0502 — raw-bank $0B collision scratch / final-writer ordering

0502 turns the seven raw-bank `$0B` writes to shared ZP `$10` found in 0501 into a reusable collision-architecture result.

This checkpoint does **not** claim that every object/frame executes every writer. It proves:

- where the seven admitted `$10` writes live;
- what coordinate/probe value each writer constructs;
- the ordering of the writer families inside scheduler-called `$B1F8`;
- the ordering of repeated `$B1F8` calls across active object slots;
- the exact 8-bit distance primitives consuming the scratch pair;
- the two-byte ROM dependency at `$B394-$B395` that was intentionally outside the 0501 manifest.

Authoritative JP ROM SHA-256:

```text
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
```

## Scheduler ordering

Fixed PRG31 runs the active-object scheduler with:

```asm
FDEA  LDX #$01
...
FDF3  LDA #$0B
FDF5  JSR $E2D0
FDF8  JSR $80E3
FDFB  JSR $B1F8
...
FE6E  INX
FE6F  CPX #$13
FE71  BCS $FE76
FE73  JMP $FDEC
```

Therefore the ordinary active-object loop visits exactly `X = $01..$12` and invokes raw-bank `$0B:$B1F8` near the start of each active slot.

The later mapper-selected per-slot calls admitted in 0501 are locally `$10`-clean. Thus, among the currently admitted scheduler paths, the renderer-facing `$10` is the value from the highest/later outer slot whose `$B1F8` invocation executes one of the seven writers, or the previously inherited value if no admitted `$B1F8` path writes `$10`.

This is a writer-order statement, not a claim that a writer must execute on every frame.

## `$B1F8` collision-sweep ordering

The raw-bank `$0B` collision/object sweep reaches the writer-owning families in this order:

```text
early vertical/proximity checks -> $B634 / $B64B
normal object/player hitbox     -> $B339
active weapon/projectile probe  -> $B3EC
peer/object loop                -> $B447, repeated for $9B=$14,$15,$16
```

The peer loop is ROM-explicit:

```asm
B29D  LDA #$14
B29F  STA $9B
...
B2B0  JSR $B447
...
B317  INC $9B
B319  LDA $9B
B31B  CMP #$17
B31D  BCC $B2A1
```

Within one `$B1F8` invocation the symbolic last-writer precedence is therefore:

```text
last qualifying $B447 peer-loop writer
  > qualifying $B3EC weapon writer
  > qualifying $B339 object/player writer
  > qualifying early $B634/$B64B writer
  > inherited pre-$B1F8 value
```

Special offset-adjust paths can replace/adjust the base scratch value inside their owning family.

## Exact seven `$10` writers

### `$B3B6` — X probe from object position

```asm
LDY $07
LDA $BB40,Y
CLC
ADC $0438,X
STA $10
```

`$10 = object_X[X] + table_BB40[$07] (mod 256)`. It is immediately consumed by the absolute X-distance helper at `$B713`.

### `$B3D2` — Y probe from object position

```asm
LDY $07
LDA $BB50,Y
CLC
ADC $041C,X
STA $10
...
LDA $B394,Y
ADC $041C
STA $11
JSR $B707
```

```text
$10 = object_Y[X] + table_BB50[$07] (mod 256)
$11 = player_Y    + table_B394[Y]   (mod 256)
```

When this path is taken, `$B3D2` supersedes the earlier `$B3B6` value.

The selector for `$B394,Y` is locally proven exactly `Y=0 or 1` by `LDY #$00 / LDA $7F / CMP #$04 / BCC ... / INY`. The table bytes are exactly `$B394-$B395 = 00 05`.

Those two bytes were not part of 0501's `B323-B393` / `B396-B4D4` ranges, so 0502 promotes exactly **2 genuinely new PRG bytes**.

### `$B40E` — active weapon/projectile X probe

The `$B3EC` family derives an index from weapon/facing state, then constructs:

```text
$10 = player_X + weapon/facing X offset (mod 256)
$11 = weapon_Y + player-form Y offset   (mod 256)
```

The public US disassembly independently labels the relocation-equivalent routine as a close-enough weapon hit check. That is secondary naming evidence only; the JP byte/control-flow proof controls.

### `$B460` — peer-object coordinate probe

Inside the `$9B=$14..$16` peer loop:

```asm
LDX $9B
LDA $0438,X
STA $10
LDA $041C,X
STA $11
LDX $69
```

So `$10/$11 = peer_object[$9B].X/Y`, after which the current outer-object index is restored from `$69`.

### `$B65F` — vertical player/object probe

```asm
LDY $7F
LDA $B673,Y
CLC
ADC $041C
STA $10
LDY $054E,X
SEC
LDA $041C,X
SBC $BC08,Y
STA $11
JSR $B707
CMP #$0C
```

```text
$10 = player_Y    + table_B673[$7F]       (mod 256)
$11 = object_Y[X] - table_BC08[object_id] (mod 256)
```

The resulting absolute difference is compared against `$0C`.

### `$B740` — player-relative scratch probe

```asm
LDA $0438
CLC
ADC $0C
STA $10
LDA $041C
CLC
ADC $0D
STA $11
```

So `$10/$11 = player_X/Y + scratch offsets $0C/$0D (mod 256)`.

### `$B76C` — in-place scratch adjustment

```asm
LDA $10
CLC
ADC $0C
STA $10
LDA $11
CLC
ADC $0D
STA $11
```

So `$10/$11 += $0C/$0D (mod 256)`. This supersedes that family's earlier scratch value.

## Shared distance primitives

Raw bank `$0B` uses the same exact 8-bit absolute-difference idiom repeatedly:

```asm
B707  SEC
B708  LDA $11
B70A  SBC $10
B70C  BCS ...
B70E  EOR #$FF
B710  ADC #$01
B712  RTS
```

Equivalent arithmetic: `abs_delta8(a,b) = |a-b|` over unsigned 8-bit coordinates.

The same idiom is reused for `$B713` (`$10` vs player X), `$B71D` (`$10` vs player Y), `$80B3/$80B6` (object X vs player X), `$80C1/$80C4` (object Y vs scratch `$11`), `$80CB/$80CE` (object X vs scratch `$10`), and `$80D5` (object Y vs player Y).

This is now a reusable collision architecture rather than seven unrelated anonymous stores.

## Native lift

0502 adds:

```text
src/collision_math.hpp
src/collision_math.cpp
tests/collision_math_test.cpp
```

The native layer preserves 8-bit coordinate wrap, exact unsigned absolute difference, `$10/$11`-style pair construction, `$B76C`-style adjustment, and threshold semantics. The test exhaustively checks all 65,536 input pairs for the absolute-difference primitive and explicit wrap/adjust/threshold cases.

## External US correspondence

The normalized JP↔US matcher maps the corresponding US region into `Castlevania 3/bank_96.asm`. Useful US candidate labels include `sub_B377`, `sub_B42A`, `sub_B485`, and `sub_B64C/sub_B663`; they corroborate the collision interpretation but do not control JP semantics.

## Exact evidence footprint

Most 0502 code is already inside the 0501 semantic manifest. The only newly promoted ROM bytes are:

```text
$B394-$B395   2 bytes   00 05
SHA-256 9f1afa4dc124cba73134e82ff50f17c8f7164257c79fed9a13f5943a6acb8e3d
```

Therefore the strict tracked PRG floor advances from **48,821** to **48,823 bytes**, or from **18.6237%** to **18.6245%**.

The small byte delta is expected: 0502's value is architectural closure and native lifting over bytes already admitted by 0501.

## Remaining provenance edge

0502 proves symbolic last-writer ordering, but the actual final value still depends on live object/state predicates: which active outer slot is last to take a writer path, which writer family it takes, and what producer values feed the relevant object/weapon/hitbox indices.

Do not replace those runtime/state-domain questions with a constant default or clamp.

Reproducible audit: `tools/audit_nmi_bank0b_collision_zp10.py`.
