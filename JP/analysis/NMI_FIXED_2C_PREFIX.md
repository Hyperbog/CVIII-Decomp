# Checkpoint 04FF — fixed PRG31 nested `$2C` prefix

This checkpoint continues the nested `$E7FB` gameplay dispatch from the 04FE frontier at fixed `PRG31:$F3DD`. It deliberately separates **local fixed-bank producer facts** from still-open transitive callees: table shape and local writes are proven from the JP ROM, while no external caller/callee is assumed to preserve `$2C` or shared ZP `$10` without its own mapper/context proof.

Authoritative JP ROM SHA-256:

```text
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
```

## Recovery / prior overlap

04FE established the nested 32-entry inline pointer table at `$F39D-$F3DC`; that 64-byte table is verification-only in 04FF and is not recounted.

The initial 04FF dependency prefix is:

```text
PRG31 CPU $F3DD-$F7FF
1059 dependency bytes
SHA-256 72918e40813310fe3f967790d9b77e344a0f2ede92d12942d95c23849084b1b6
```

04FE already counted `$F6AE-$F6E3` (54 bytes), SHA-256:

```text
d79b617b7e27190b6556464a37cc024a1837e949ebe9446d12815da908233dfb
```

Therefore 04FF contributes exactly **1005 genuinely new bytes** in two ordered ranges:

```text
$F3DD-$F6AD   721 bytes   SHA-256 371c27c08f71624463d2c63097938a30fa57253bd073d2554d454111708f6852
$F6E4-$F7FF   284 bytes   SHA-256 6f3c519ae6a1965fc20722535001e4c08a84dfde4245cfa79b78a463c8df0ce6
```

Ordered new-manifest SHA-256:

```text
257dfb57d710e3eb4ea9e4ff1d4d168901e65dc3afc7c1c6054c1c5d2548e51a
```

## Nested targets physically entering this prefix

The 04FE table contains 32 entries / 31 unique target addresses. Twenty-six unique targets begin inside `$F3DD-$F7FF`:

```text
F3DD F3EC F3F4 F3FC F402 F48D F4E7 F4FA
F511 F531 F5A8 F5D2 F61D F62C F638 F652
F653 F65B F6E4 F6EC F6F4 F6FE F713 F739
F792 F7CF
```

The remaining entries begin at `$F831/$F839/$F841/$F849/$F965` and are deferred beyond this byte frontier.

A conservative recursive decode from all 26 in-prefix roots follows only control flow whose instruction start remains inside `$F3DD-$F7FF`; fixed/banked calls, branches, or jumps leaving the interval are recorded as exits rather than guessed.

Result:

```text
verified in-prefix instruction starts   401
unknown official opcodes                  0
reachable indexed/indirect ZP writes      0
reachable direct $2C writers             16
deferred exits                           136
  JSR                                     124
  JMP                                       9
  branch                                    2
  fallthrough                               1
```

The absence of indexed/indirect zero-page stores/RMWs is important: within this local graph there is no hidden indexed alias to `$2C`; every local mutation of `$2C` is an explicit `STA $2C` or `INC $2C`.

## Explicit local `$2C` writers

The reachable writers and the nested table roots whose local graph can reach them are:

```text
F3FF  INC $2C       root 00
F443  INC $2C       root 01
F486  STA $2C       root 01        immediate $09 or $13
F4BF  INC $2C       roots 01,02
F4CF  STA $2C       roots 01,02    immediate $0F
F4DC  STA $2C       roots 01,02    immediate $0A
F4F3  STA $2C       root 0F        immediate $10
F5CF  INC $2C       root 04
F629  STA $2C       root 06        immediate $07
F635  STA $2C       root 07        immediate $01
F64F  STA $2C       root 09        immediate $02
F6FB  INC $2C       root 1C
F716  INC $2C       root 13
F775  INC $2C       root 14
F7B4  INC $2C       root 15
F7DB  STA $2C       root 16        immediate $10
```

`$F486` has two ROM-visible immediate producers: `LDA #$09` falls into the store, while `$F489: LDA #$13 / BNE $F486` reaches the same store.

All constant `STA $2C` values are within `$00-$1F`. If only the local root-associated state is considered, the INC sites also nominally remain in-range, producing the set:

```text
$01 $02 $03 $05 $07 $09 $0A $0F $10 $13 $14 $15 $16 $1D
```

That set is **not promoted to a complete JP producer-domain proof** because many paths call helpers outside this prefix before returning. Until those callees are reconciled under their actual fixed/banked context, they are allowed to be potential `$2C` producers.

## Initialization evidence already visible above the nested dispatcher

The first-level fixed graph contains explicit zero initialization when entering relevant main-script paths:

```asm
E449  LDA #$00
E44B  STA $2C
...
E489  ...
E48D  LDA #$04
E48F  STA $18
E491  LDA #$00
E493  STA $2C
```

This strongly anchors the nested state machine at zero on those transitions, but it still does not eliminate later external writes.

## External reference used only as an accelerator

The existing US Castlevania III disassembly labels an analogous gameplay script byte as `ram_002A_script` and enumerates a `$00-$1F` state family. That is useful semantic/naming evidence, but it is **not** used as the JP bound proof: the JP build uses different zero-page layout and mapper/audio architecture, and the local JP audit above remains controlling.

## Result

**04FF closes the fixed `$F3DD-$F7FF` prefix and enumerates every local `$2C` write reachable from the 26 nested targets entering that interval. All constant local producers are in-range and no indexed/indirect ZP alias exists. Full `$2C` producer closure remains open across the 136 deferred exits.**

The next byte frontier is fixed `PRG31:$F800`. The next checkpoint should continue through the out-of-prefix targets at `$F831/$F839/$F841/$F849/$F965`, while resolving mapper state before traversing `$8000-$BFFF` callees. `$18` producer closure remains separately open.

Reproducible audit: `tools/audit_nmi_fixed_nested_prefix.py`.

VPP remains **21/100**; transitive NMI helper/bank-context closure is not yet earned.
