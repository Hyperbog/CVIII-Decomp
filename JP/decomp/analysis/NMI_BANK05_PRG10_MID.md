# Checkpoint 04FC — raw bank `$05` PRG10 middle closure

This checkpoint continues the pre-render sound-stream producer domain in raw VRC6 bank `$05` / physical PRG10-PRG11 from the committed frontier at CPU `$9A6B`.

Authoritative ROM SHA-256:

```text
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
```

## Recovery

The committed 04FB state was rechecked before forward work: ROM identity, the raw-bank `$05` overlap `$9A2B-$9A6A`, and the `$9A6B-$9A8A` frontier fingerprint all match the authoritative ROM.

The already-proven common parser result still applies: raw bank `$05:$8001-$87AD` is byte-identical to the audited bank-$04 core, so its resolved executable graph remains ZP `$10`-clean.

## Exact 04FC dependency span

The suggested initial window `$9A6B-$ACBC` reaches the root at `$AC55`, whose recursive dependency continues through `$AD96`. Extending to close that root remains inside the normal checkpoint budget.

The next root `$AD97` reaches through `$AE2D`; including it from the 04FC start would require 5059 genuinely new bytes and is therefore deferred.

Authoritative 04FC span:

```text
raw bank $05 / physical PRG10-PRG11
CPU $9A6B-$AD96
4908 dependency bytes
4908 genuinely new bytes
SHA-256 3d34329fd18b7c713f1fe35206868f1b6c0bdfb6127f664410a60fd54a8c46f0
```

04FC closes 31 metadata references sharing 25 distinct roots across sound IDs:

```text
$53 $54 $55 $56 $57 $5C
```

The 25 roots are:

```text
$9A6B $9B6A $9BD8 $9CF4 $9D21 $9D99 $9E36 $9F46
$A01E $A05B $A118 $A119 $A252 $A3BA $A506 $A658
$A6FB $A6FC $A7B3 $A86D $A918 $A9D6 $AA90 $AB65 $AC55
```

After 04FC:

```text
bank-$05 roots total       72
closed                     44
remaining                  28
next unresolved root       $AD97
```

## Hardened recursive result

The audit preserves the established alternate-parser state model: `FB` loop anchors, context-sensitive `FD` call/return, `FE nn` counted loops, `FE FF lo hi` absolute stream pointers, and the instrument-$07 non-`F?` rule. Every multi-byte command must have all operand bytes inside the claimed semantic span before any operand is read.

Across the 31 metadata references / 25 roots:

```text
abstract parser states:            7105
unique decoded command addresses:  4221
earliest decoded command:          $9A6B
latest decoded command:            $AD96
FD calls / returns:                22 / 22
FE jumps / loops:                  23 / 56
operand/path escapes:              0
pointer-target escapes:            0
```

The maximum byte read is exactly the exclusive endpoint `$AD97`, making `$AD96` a complete dependency boundary and `$AD97` a clean next-root frontier.

## Live `$E7` producer-domain proof

There are exactly three raw `$E7` bytes in the 04FC dependency span, and all three are decoded `$E7` commands:

```text
$9F5C -> parameter $09
$A950 -> parameter $0E
$AA13 -> parameter $0D
```

The producer high-nibble domain is therefore exactly:

```text
$0
```

At the common handler `$840F`, the following byte's high nibble is masked and doubled to index pointer pairs at `$8430-$8443`. High nibble `$0` indexes the first in-range pair, and the ROM table entry resolves to `$8444`.

`$8444` is already part of the audited common parser graph and is ZP `$10`-clean. Therefore every live 04FC `$E7` dispatch is closed from actual ROM producer values, with no invented host-side bounds check at `$842D`.

## Result

**04FC closes the next 25 raw-bank `$05` roots as preserving shared ZP `$10`. Cumulative bank-$05 closure is 44/72 roots.**

The next root is `$AD97`; its dependency reaches through `$AE2D`, which would make this checkpoint 5059 genuinely new bytes, so it is deliberately deferred.

Fixed `$E7FB` / inline dispatch remains unresolved and is not opened here.

VPP remains **21/100** because the remaining 28 bank-$05 roots and fixed `$E7FB` still block transitive NMI-helper closure.

Reproducible audit: `tools/audit_nmi_bank05_prg10_mid.py`.
