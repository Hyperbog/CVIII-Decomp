# Checkpoint 04FF partial — fixed PRG31 `$2C` nested-dispatch head

This is a **bounded partial 04FF evidence checkpoint**, not a completed 04FF closure. The repository recovery state must remain `blocked` until the full live `$2C` producer domain and all admitted nested targets are reconciled.

Authoritative JP ROM SHA-256:

```text
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
```

## Recovery boundary

04FE established the nested `$E7FB` table at fixed `PRG31:$F39D-$F3DC`. The 64-byte table and next-code fingerprint reproduce exactly:

```text
$F39D-$F3DC  SHA-256 81d06cd79d64c3d4cfe14bbefa851e74e748536f723636abaf82870ec065d22f
$F3DD-$F3FC  SHA-256 65d47f163ffad5ca20903cece8606c76416ceb5cb8edba99780be720730f08aa
```

The initial 04FF raw window is fixed `PRG31:$F3DD-$F7FF` (1059 bytes), SHA-256:

```text
72918e40813310fe3f967790d9b77e344a0f2ede92d12942d95c23849084b1b6
```

Prior 04FE coverage `$F6AE-$F6E3` remains verification/prior coverage only and is never counted again.

## Primary nested-table roots inside this window

The 32-entry `$2C` table encoded by 04FE contains 26 distinct targets inside `$F3DD-$F7FF`. Six entries are deliberately deferred because they start beyond this bounded window:

```text
$08 -> $F965
$0B -> $F831
$0C -> $F839
$0D -> $F841
$0E -> $F841
$10 -> $F849
```

The 26 in-window roots are decoded conservatively: both sides of conditional branches are followed; fixed calls/jumps outside the bounded window and CPU `$8000-$DFFF` exits are recorded as dependencies rather than guessed through an unknown mapper state.

## Strict fixed-window graph

Result:

```text
official instruction starts       401
unknown opcodes                      0
unique decoded instruction bytes   931
04FE $F6AE-$F6E3 overlap             0
```

Exact genuinely-new byte manifest:

```text
F3DD-F6AD   721   SHA-256 371c27c08f71624463d2c63097938a30fa57253bd073d2554d454111708f6852
F6E4-F705    34   SHA-256 cd2f26e03fcfab69f12aec4fbe3ff9571f8a2633b3c84eb4365a0d8e777378c5
F713-F723    17   SHA-256 4bc45df46fbab59efc9b70eb7d577001b8474818f921b86e618b43c4653c8300
F739-F781    73   SHA-256 b8cc2cdf6b04eb86ff7693b53c006afb6710098252d7a921e199c22355d462ac
F792-F7B6    37   SHA-256 b564a74ff4c6ba3a55b76472c1462ff1b915f0c333c8dc54ccae3b9a76d1e5e1
F7CF-F7FF    49   SHA-256 13b6de6ba1671ce00afec40ee8b7886d6ed9126a6261b5a090a15f0cc73b1574
```

Ordered-manifest SHA-256:

```text
2e8b703b970ca2f1eae61f5fd1a4850da6b8e5d4af1a894fb8075657299ae0d4
```

The 128 raw bytes in the bounded window not claimed by this graph are exactly:

```text
F6AE-F6E3   54 bytes   prior 04FE coverage
F706-F712   13 bytes   not reached by these 26 roots
F724-F738   21 bytes   not reached
F782-F791   16 bytes   not reached
F7B7-F7CE   24 bytes   not reached
```

The last four gaps are not silently treated as code/data coverage; later secondary-dispatch evidence may admit them.

## Dependency boundary

The strict bounded graph records these exits without assigning guessed bank state:

```text
JSR -> CPU $8000-$DFFF       64
JMP -> CPU $8000-$DFFF        8
JSR -> fixed outside window   60
JMP -> fixed outside window    1
branch -> fixed outside         2
fallthrough -> fixed outside    1
```

These are semantic dependencies, not coverage escapes hidden by the audit.

## Shared ZP `$10`

Within the decoded fixed-window graph:

- 46 reachable store/RMW instructions exist;
- there is no direct ZP/absolute write to `$10`;
- there is no reachable indexed or indirect store/RMW addressing form at all.

Therefore the **bounded fixed `$F3DD-$F7FF` graph itself preserves shared ZP `$10`**. This does not prove that its external mapper-dependent callees preserve `$10`.

## `$2C` producer information learned here

Reachable fixed-side mutations of `$2C` are exactly:

```text
F3FF INC $2C
F443 INC $2C
F486 STA $2C
F4BF INC $2C
F4CF STA $2C
F4DC STA $2C
F4F3 STA $2C
F5CF INC $2C
F629 STA $2C
F635 STA $2C
F64F STA $2C
F6FB INC $2C
F716 INC $2C
F775 INC $2C
F7B4 INC $2C
F7DB STA $2C
```

ROM-local constant stores are bounded:

```text
$F486 <- $04 / $09 / $13, selected by local predecessors
$F4CF <- $0F
$F4DC <- $0A
$F4F3 <- $10
$F629 <- $07
$F635 <- $01
$F64F <- $02
$F7DB <- $10
```

Conservative root reachability for the INC sites is:

```text
F3FF <- primary entry $00
F443 <- $01
F4BF <- $01,$02
F5CF <- $04
F6FB <- $1C
F716 <- $13
F775 <- $14
F7B4 <- $15
```

Thus the highest in-window primary entry that can conservatively reach an increment is `$1C`, which would yield at most `$1D` **if no intervening external callee changes `$2C`**.

That qualification is controlling. This partial checkpoint does **not** claim `$2C <= $1F` because:

1. fixed callees outside `$F3DD-$F7FF` may mutate `$2C`;
2. mapper-dependent `$8000-$DFFF` callees may mutate `$2C`;
3. six primary table entries lie beyond `$F7FF`;
4. those deferred states expose additional `$68`-indexed inline dispatchers.

A subsequent probe already confirms why those domains must stay separate: `$F849` and `$F965` each execute `LDA $68 / JSR $E7FB` with their own inline pointer data. Their table shapes are not producer-domain bounds and are not closed here.

## Result

**04FF partial result:** 931 genuinely new fixed PRG31 bytes are strictly decoded and ZP `$10`-safe; the fixed-side `$2C` transitions are sharply bounded, but the live `$2C` producer domain is not yet closed. Keep `RESUME_STATE.json` blocked at `$F3DD` until the deferred states, secondary `$68` dispatches, and mapper-selected callees are reconciled.

Reproducible audit: `tools/audit_nmi_fixed_2c_head.py`.
