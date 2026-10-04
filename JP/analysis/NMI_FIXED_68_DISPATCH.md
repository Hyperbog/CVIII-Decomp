# Checkpoint 0500 — fixed PRG31 secondary `$68` dispatchers

0500 is a completed bounded checkpoint. It closes the six primary `$2C` entries deferred by 04FF, the explicit `$F800` fallthrough boundary handed forward by 04FF, and the encoded target graphs of the two secondary `$68` dispatchers at `$F849` and `$F965`. It does not claim a complete live `$68` or `$2C` producer-domain proof.

Authoritative JP ROM SHA-256:

```text
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
```

## Recovery boundary

```text
$F7E0-$F7FF overlap SHA-256
6966c228f397fb1a390562bc871d382f624397bd65f06bb301774b085e7759d1

$F800-$F81F fingerprint SHA-256
322b459da91a43e13712821aba143184801a6b9e6c91e0047f9826846a957f24

$F800-$FBFF raw investigation window SHA-256
f3090b53f174f15eeacad0d9e042efd95ff93ed6b4bfd706ba233ee5f588c86a
```

04FF also carried four unreached gaps: `$F706-$F712`, `$F724-$F738`, `$F782-$F791`, `$F7B7-$F7CE`.

## Deferred primary roots and the repaired `$F800` seed

The six encoded primary states deferred by 04FF are:

```text
$08 -> $F965
$0B -> $F831
$0C -> $F839
$0D -> $F841
$0E -> $F841
$10 -> $F849
```

04FF also recorded an explicit fallthrough boundary at `$F800`. Therefore `$F800` is a required 0500 root. The earlier 933-byte 0500 draft omitted this root and incorrectly left `$F800-$F830` unclaimed; that accounting is superseded by this corrected checkpoint.

## Secondary dispatcher at `$F849`

```asm
F849  LDA $68
F84B  JSR $E7FB
```

Inline table `$F84E-$F86D` is 16 pointers:

```text
00 F86E
01 F883
02 F88F
03 F899
04 F8B1
05 F8E9
06 F919
07 F95A
08 F86E
09 F877
0A F88F
0B F899
0C F706
0D F724
0E F782
0F F7B7
```

SHA-256:

```text
88065baa658136181547132c1ee61481724cba01f76f0f5aed837a91aa06e549
```

This structurally admits all four former 04FF gaps through actual pointer-table control flow.

Two already-proven primary transitions initialize this state family at different `$68` values:

```asm
F4F1  LDA #$10
F4F3  STA $2C
F4F5  LDA #$00
F4F7  STA $68

F7D9  LDA #$10
F7DB  STA $2C
F7DD  LDA #$08
F7DF  STA $68
```

Those facts are producer evidence, not a proof that every live path entering primary state `$10` has `$68 <= $0F`.

## Secondary dispatcher at `$F965`

```asm
F965  LDA $68
F967  JSR $E7FB
```

Inline table `$F96A-$F97D` is 10 pointers:

```text
00 F97E
01 F9C2
02 F9D7
03 F9FF
04 FAAA
05 FACA
06 FAF2
07 F9C2
08 F9D7
09 FB37
```

SHA-256:

```text
9db34975a37e416e832cc543ae63858c0fa17e5a7b0b5f6f6070a96974838aea
```

Neither table length is promoted to a live `$68` bound.

## Strict bounded graph

Roots:

```text
F800 F831 F839 F841 F849 F965
```

The two `JSR $E7FB` sites are tail-dispatch boundaries; their inline bytes are data, not fallthrough instructions. Both sides of conditional branches are followed. Fixed targets outside the bounded domain and CPU `$8000-$DFFF` targets are dependencies rather than guessed traversals.

Result:

```text
official instruction starts          414
unknown opcodes                         0
reachable store/RMW instructions       82
indexed write/RMW forms                 9
```

All nine indexed writes are absolute-indexed stores with bases in `$0300-$057C`; none can alias zero page. There is no direct write/RMW to `$10`. Therefore the admitted fixed 0500 graph preserves shared ZP `$10`.

Boundary dependencies:

```text
JSR -> fixed outside domain   50
JSR -> banked                  38
JMP -> banked                   5
JSR -> prior verified           3
JMP -> fixed outside domain     3
JMP -> prior verified           2
branch -> prior verified        1
```

## Local selector mutations

Reachable `$2C` mutations:

```text
F736 F78F F7CC F962 FB77
```

Reachable `$68` mutations:

```text
F706 F72F F78D
F874 F896 F8AE F8E6 F916 F957
F9B4 F9D0 F9FC F9FF
FAB7 FAD7 FB04
```

These sites are verified, but complete transitive producer closure remains open because unresolved external callees may also mutate the selectors.

## Semantic ROM data

`$FB20-$FB2C` bounds Y to `0..5` while reading `$FB31,Y`, so `$FB31-$FB36` is admitted as exactly six bytes of ROM data:

```text
3C 3A 3C 3B 3A 3C
```

The apparent `$FAA0-$FAA9` ROM data referenced by the `$FAxx` body remains unclaimed because the relevant `$62/$054E` index domains are not yet proven.

## Exact genuinely-new coverage

```text
F706-F712    13   8745c6e3d3acdd90bf3b1cafaf32f9e981a606070ba5d2b365cace8f56fa3025
F724-F738    21   41cad7c7b722c299f4111083f871fd996a0cfa517bd990d3b37ddce6ac30072e
F782-F791    16   17bbb4663de8e617686c27ab5ad5554a69c0062d9c8bff1d353fd6487028546b
F7B7-F7CE    24   0d93fcf865fdae96f01a0640e3769924b558f1cb0aaa0dbe7d2fedfdf17462be
F800-FA9F   672   6dea651f93c64d59355c4180907677d367bb705ed84cbfa6ec59da79009028a8
FAAA-FB95   236   5d32479e3af38c5477b4a3c076b3c3d0a0bd07f4c572a35a115bd6e347720402
------------------------------------------------
TOTAL       982
```

Ordered-manifest SHA-256:

```text
fdc1a53db0ee18ca5e70188d2c8b31d1b350c91d011f72fddb4b6fcb7434984e
```

The only still-unclaimed byte range below the raw `$FB96` frontier is `$FAA0-$FAA9` (10 bytes).

## Result

0500 promotes **982 genuinely new PRG31 bytes** and proves the admitted fixed graph itself is `$10`-safe. It does not yet prove complete `$68`, `$2C`, or `$18` producer domains or preservation across mapper-dependent callees.

Reproducible audit: `tools/audit_nmi_fixed_68_dispatch.py`.

## Next checkpoint — 0501

Continue from raw fixed-bank frontier `$FB96`. The complete remaining fixed tail is `$FB96-$FFFF` (1130 bytes), SHA-256 `0cbfd0aa79f3c7d1db7a756c08c47bfe01cba321900fb8955e77ec8525d38d44`. Carry `$FAA0-$FAA9` as an explicit unresolved indexed-data dependency and classify the raw `$FE95: JSR $E7FB` atlas candidate only through actual control flow.