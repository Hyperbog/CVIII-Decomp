# Checkpoint 0500 — fixed PRG31 secondary `$68` dispatchers

0500 continues the nested gameplay-state analysis from the raw fixed-bank frontier at `PRG31:$F800`. It uses the whole-PRG atlas as a discovery accelerator, but promotes only JP-ROM-backed control flow and explicitly consumed table/data bytes.

Authoritative JP ROM SHA-256:

```text
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
```

## Recovery / raw window

```text
04FF overlap     $F7E0-$F7FF  32 bytes
SHA-256          6966c228f397fb1a390562bc871d382f624397bd65f06bb301774b085e7759d1

0500 fingerprint $F800-$F81F  32 bytes
SHA-256          322b459da91a43e13712821aba143184801a6b9e6c91e0047f9826846a957f24

raw window        $F800-$FBFF  1024 bytes
SHA-256          f3090b53f174f15eeacad0d9e042efd95ff93ed6b4bfd706ba233ee5f588c86a
```

The four 04FF gaps remained unclaimed entering this checkpoint:

```text
F706-F712   13
F724-F738   21
F782-F791   16
F7B7-F7CE   24
```

## Deferred primary `$2C` entries

04FF carried six encoded primary states forward:

```text
$08 -> $F965
$0B -> $F831
$0C -> $F839
$0D -> $F841
$0E -> $F841
$10 -> $F849
```

`$F831/$F839/$F841` are small banked-tail states. `$F849` and `$F965` each load `$68` and invoke the already-audited stack-consuming `$E7FB` dispatcher.

## Secondary dispatcher #1 — `$F849`

```asm
F849  A5 68     LDA $68
F84B  20 FB E7  JSR $E7FB
```

The following 32 bytes `$F84E-$F86D` encode 16 pointers:

```text
00 F86E   01 F883   02 F88F   03 F899
04 F8B1   05 F8E9   06 F919   07 F95A
08 F86E   09 F877   0A F88F   0B F899
0C F706   0D F724   0E F782   0F F7B7
```

Table SHA-256:

```text
88065baa658136181547132c1ee61481724cba01f76f0f5aed837a91aa06e549
```

This is the missing semantic admission for **all four 04FF gaps**. They are no longer merely physically adjacent bytes; they are encoded secondary-dispatch targets.

The 16-entry shape is **not** promoted to a live `$68 <= $0F` proof. `$E7FB` performs no bounds check.

## Secondary dispatcher #2 — `$F965`

```asm
F965  A5 68     LDA $68
F967  20 FB E7  JSR $E7FB
```

The following 20 bytes `$F96A-$F97D` encode 10 pointers:

```text
00 F97E   01 F9C2   02 F9D7   03 F9FF   04 FAAA
05 FACA   06 FAF2   07 F9C2   08 F9D7   09 FB37
```

Table SHA-256:

```text
9db34975a37e416e832cc543ae63858c0fa17e5a7b0b5f6f6070a96974838aea
```

Again, ten encoded pointers do **not** establish `$68 <= $09`.

## Strict bounded graph

Conservative decoding starts from the three simple deferred primary roots, both dispatcher sites, and every encoded secondary target. Conditional branches follow both sides. Calls/jumps outside the admitted fixed regions are recorded as dependencies instead of being traversed under guessed mapper state.

Result:

```text
official instruction starts        395
instruction/operand bytes          875
explicit table/data bytes           58
  F84E-F86D pointer data             32
  F96A-F97D pointer data             20
  FB31-FB36 bounded local table       6
---------------------------------------
genuinely new semantic bytes       933
```

`$FB31-$FB36` is explicitly justified by the local loop at `$FB20`: `LDY #$00`, `LDA $FB31,Y`, `INY`, `CPY #$06`, `BNE`, so exactly six data bytes are consumed.

Boundary/control edges from the strict graph:

```text
fallthrough -> new          359
branch      -> new           29
JSR         -> fixed-out     45
JSR         -> banked        32
JMP         -> banked         5
JMP         -> fixed-out      3
E7FB tail dispatch            2
JSR         -> prior          2
JMP         -> prior          2
JSR         -> new            2
JMP         -> new            2
branch      -> prior          1
```

## Exact new-byte manifest

```text
F706-F712    13   8745c6e3d3acdd90bf3b1cafaf32f9e981a606070ba5d2b365cace8f56fa3025
F724-F738    21   41cad7c7b722c299f4111083f871fd996a0cfa517bd990d3b37ddce6ac30072e
F782-F791    16   17bbb4663de8e617686c27ab5ad5554a69c0062d9c8bff1d353fd6487028546b
F7B7-F7CE    24   0d93fcf865fdae96f01a0640e3769924b558f1cb0aaa0dbe7d2fedfdf17462be
F831-FA9F   623   eb0859ea4906556aa18192c14d446c9968b56eda1d0d27ad70138f292d9cd9fe
FAAA-FB95   236   5d32479e3af38c5477b4a3c076b3c3d0a0bd07f4c572a35a115bd6e347720402
```

Total: **933 genuinely new bytes**.

Ordered-manifest SHA-256:

```text
a4ae2796d32ef639940c58f0160af79b8eab8cf80347a998af0ae9c4bab3e44a
```

Within the original `$F800-$FBFF` raw window, 859 bytes are now semantically admitted. The still-unclaimed raw gaps are:

```text
F800-F830    49
FAA0-FAA9    10
FB96-FBFF   106
```

`$FAA0-$FAA9` are visible as indexed ROM data dependencies in the `$F9FF` path, but their complete index domains (`$62`, `$054E`) are not yet proven, so these bytes remain unclaimed rather than being swept in by proximity.

## Shared ZP `$10`

The admitted graph contains 82 reachable store/RMW instructions.

- no direct ZP/absolute store/RMW targets `$10`;
- no reachable `zpx`, `zpy`, `(zp,X)`, or `(zp),Y` store/RMW form;
- the nine reachable absolute-indexed writes use bases only in `$0300-$057C`, so an 8-bit X/Y cannot wrap them to `$0010`.

Therefore the **bounded 0500 fixed graph preserves shared ZP `$10`**. This does not assert that unresolved banked/fixed callees preserve it.

## `$2C` and `$68` local mutations

Reachable `$2C` mutations in newly admitted code are:

```text
F736  STA $2C   restore saved pre-call state
F78F  STA $2C   restore saved pre-call state
F7CC  STA $2C   <- $16
F962  STA $2C   <- $03
FB77  STA $2C   <- $03
```

Reachable `$68` mutations are exactly 16 `INC $68` sites:

```text
F706 F72F F78D F874 F896 F8AE F8E6 F916
F957 F9B4 F9D0 F9FC F9FF FAB7 FAD7 FB04
```

The local structure is consistent with bounded state machines, and earlier verified fixed code initializes `$68` to values including `$00` and `$08`. However, external callees may return before these transitions, so this checkpoint deliberately does **not** claim complete live `$68` producer bounds.

## Result

**0500 closes the deferred fixed-bank primary roots and both visible secondary `$68` dispatch structures as a bounded local graph, promotes all four formerly-unclaimed 04FF gaps, and adds 933 genuinely new bytes while proving the admitted graph itself is ZP `$10`-safe.**

Still open:

1. complete `$68` producer/alias domains for both secondary dispatchers;
2. complete `$2C` producer/alias domain;
3. mapper-state resolution for the 32 JSR + 5 JMP banked exits in this graph and the earlier fixed graph;
4. first-level `$18` producer-domain closure;
5. `$FAA0-$FAA9` indexed-data domains;
6. remaining fixed tail beginning at `$FB96`.

Reproducible audit: `tools/audit_nmi_fixed_68_dispatch.py`.

VPP remains **21/100** until transitive NMI helper/bank-context closure is complete.
