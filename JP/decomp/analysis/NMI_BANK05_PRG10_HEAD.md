# Checkpoint 04FB — raw bank `$05` PRG10 head closure

This checkpoint begins the remaining pre-render sound-stream producer domain in raw VRC6 bank `$05` / physical PRG10-PRG11 from CPU `$87AE`.

Authoritative ROM SHA-256:

```text
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
```

## Recovery and parser-core identity

The schema-v5 recovery transition from raw bank `$04` to raw bank `$05` was rechecked against the ROM before forward work: the bank-$04 overlap `$BE3E-$BE7D` and bank-$05 fingerprint `$87AE-$87CD` both match.

Raw bank `$05:$8001-$87AD` is byte-identical to the already-audited raw bank `$04` alternate-parser executable core:

```text
1965 bytes
SHA-256 e2c3ff3d7e9f96b598610a8028f5b92a606fac7f9acb2977811146fa145fdb67
```

Therefore the prior executable-code proof is reusable: its resolved graph has 786 accepted instruction starts and no write form capable of modifying or aliasing shared ZP `$10`.

## Exact metadata domain

Re-reading the authoritative metadata table gives:

```text
bank-$05 instrument references: 84
distinct stream roots:          72
first root:                     $87AE
last root:                      $BEE8
```

Every bank-$05 reference initializes alternate-parser mode under the ROM-proven rule: its first stream byte is `>= $10`, and no reference uses the instrument `$05/$06` main-parser exception.

## Exact 04FB dependency span

The initial suggested window was `$87AE-$99FF`. The root at `$995F` remains live beyond `$99FF` but closes through `$9A6A`, still inside the normal 5000-new-byte budget. The next root `$9A6B` requires dependency through `$9B69`, which would make the checkpoint 5052 genuinely new bytes and is therefore deferred.

Authoritative 04FB span:

```text
raw bank $05 / physical PRG10
CPU $87AE-$9A6A
4797 dependency bytes
4797 genuinely new bytes
SHA-256 58f4a24e41ba95766529e1eaa531c63fc666ca51abc668ec4eb3ba3f4e50eb6b
```

04FB closes 19 metadata references / 19 distinct roots from sound IDs `$50-$53`:

```text
$87AE $87C8 $87E1 $87F9 $8811 $882A $8842
$8ACD $8CCB $8E17 $8FE0 $91B9 $9387 $94B1
$95E6 $9644 $9773 $97FC $995F
```

After 04FB:

```text
bank-$05 roots total       72
closed                     19
remaining                  53
next unresolved root       $9A6B
```

## Hardened recursive result

The audit carries the established alternate-parser stream state for `FB` loop anchors, context-sensitive `FD` call/return, `FE nn` counted loops, `FE FF lo hi` absolute stream pointers, and the instrument-$07 non-`F?` rule. Every variable-width command must have all operand bytes inside the accounted span before they are read.

Across the 19 roots:

```text
abstract parser states:            6437
unique decoded command addresses:  3992
earliest decoded command:          $87AE
latest decoded command:            $9A67
FD calls / returns:                26 / 26
FE jumps / loops:                  13 / 38
operand/path escapes:              0
pointer-target escapes:            0
```

The maximum byte read is exactly the exclusive endpoint `$9A6B`, so `$9A6A` is fully accounted and `$9A6B` is a clean next-root boundary.

## Live `$E7` producer-domain proof

Unlike raw bank `$04`, bank `$05` contains reachable alternate-parser command `$E7`. This is resolved from the actual producer bytes rather than by adding a host-side bound.

The nine unique decoded `$E7` command/parameter pairs are:

```text
$8A39 -> $50
$8BDC -> $50
$8E2C -> $58
$8EFE -> $50
$911F -> $50
$9126 -> $55
$924A -> $80
$9260 -> $80
$928C -> $02
```

At the common parser handler `$840F`, the byte following `$E7` is transformed as:

```asm
8418  LDA ($E0),Y
841A  AND #$F0
841C  LSR A
841D  LSR A
841E  LSR A
841F  TAX
8421  LDA $8430,X
8424  STA $E2
8426  LDA $8431,X
8429  STA $E3
842B  LDX $EE
842D  JMP ($00E2)
```

Thus the relevant producer domain is the high nibble of the parameter byte. For every decoded `$E7` in 04FB, that domain is exactly:

```text
$0 $5 $8
```

All are within the ROM's ten-entry `$0-$9` pointer block `$8430-$8443`. The bank-$05 core is byte-identical to the audited bank-$04 core, and all ten entries are `$8444`; every live 04FB `$E7` therefore dispatches to `$8444`, which is already part of the resolved ZP-`$10`-clean executable graph.

This is a ROM-proven producer-domain bound. It does **not** justify adding a generic host-side bounds check to `$842D`.

## Result

**04FB closes the first 19 of 72 raw-bank `$05` roots as preserving shared ZP `$10`, including the first live `$E7` producer-domain proof.**

The next root is `$9A6B`. Including it in this checkpoint would require 5052 new bytes through `$9B69`, so it is deliberately deferred.

Fixed `$E7FB` / inline dispatch remains unresolved and is not opened here.

VPP remains **21/100** because transitive NMI-helper closure is still incomplete.

Reproducible audit: `tools/audit_nmi_bank05_prg10_head.py`.
