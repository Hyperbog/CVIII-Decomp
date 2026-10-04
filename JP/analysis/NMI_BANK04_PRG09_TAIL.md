# Checkpoint 04FA — raw bank `$04` PRG09 tail closure

This checkpoint finishes the remaining pre-render sound-stream producer domain in raw VRC6 bank `$04` / physical PRG09, beginning from the committed 04F9 frontier at CPU `$B1F0`.

Authoritative ROM SHA-256:

```text
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
```

## Exact dependency span

All 30 remaining distinct bank-`$04` roots close before the physical bank tail ends. The final reachable command is the one-byte stop at `$BE7D`, so bytes `$BE7E-$BFFF` are not consumed as commands or operands by any bank-`$04` metadata root.

```text
raw bank $04 / physical PRG09
CPU $B1F0-$BE7D
3214 dependency bytes
SHA-256 a7f0a8308ed9335b27de8eaf3df440f0d28cd6f57fb97e4123222e3116fc5f55
30 root bytes already counted as 04F7 mode probes
3184 genuinely new bytes
```

This remains inside the normal 500-5000-new-byte checkpoint budget.

## Metadata closure

The established census remains 102 bank-`$04` instrument references / 96 distinct roots. 04F7-04F9 closed the first 66 roots. The remaining tail contains 36 metadata references sharing 30 distinct roots across sound IDs:

```text
$5F $68 $6A $6C $6D $6E
```

After 04FA:

```text
bank-$04 roots total       96
closed                     96
remaining                   0
```

Every bank-`$04` reference still satisfies the ROM-proven alternate-parser initialization rule: first byte `>= $10`, with no instrument `$05/$06` exception.

## Hardened recursive result

The audit carries the established parser state for:

- `FB`: loop-anchor establishment;
- `FD`: call/return state;
- `FE nn`: counted loop using the saved anchor;
- `FE FF lo hi`: absolute stream-pointer load;
- `FF`: stop;
- instrument `$07`: its distinct non-`F?` parser rule.

Every variable-width command requires complete operand containment before operand bytes are read.

Across the 36 metadata references / 30 roots:

```text
abstract parser states:            3426
unique decoded command addresses:  2595
earliest decoded command:          $B1F0
latest decoded command:            $BE7D
FD calls / returns:                20 / 20
FE jumps / loops:                  17 / 16
decoded E7:                        0
operand/path escapes:              0
pointer-target escapes:            0
```

## Raw `$E7` bytes

There is one raw byte `$E7` inside the semantic dependency span, at `$B81A`, but it is not a command:

```text
$B818: FE FF E7 B7  -> absolute stream pointer $B7E7
             ^
             pointer-low operand
```

The only other raw `$E7` byte in the remaining physical PRG09 tail is at `$BFEB`; it lies beyond every reachable bank-`$04` command and operand and is not in the closed dependency span.

Therefore none of the remaining roots can activate alternate-parser handler `$840F` / indirect dispatch `$842D`.

## ZP `$10` consequence

04F7 already proved the shared alternate-parser executable core `$8001-$87AD` is ZP `$10`-clean on its resolved graph. 04F8-04FA now prove that every one of the 96 bank-`$04` stream roots avoids live `$E7` dispatch and remains inside the audited parser behavior.

**Result: the entire raw-bank `$04` producer domain preserves shared ZP `$10`.**

This is a producer-domain reachability proof, not a guessed local bound on `$842D`; no host-side bounds check should be introduced there.

## Next sound-side domain

The remaining sound-side pre-render dependency is the other instrument-data bank selected through `$06D3,X`: raw VRC6 bank `$05` / physical PRG10-PRG11. The metadata table contains 84 bank-`$05` references / 72 distinct roots, with the first root at CPU `$87AE`.

Fixed `$E7FB` / inline dispatch also remains unresolved and is deliberately not opened in 04FA.

VPP remains **21/100** because transitive NMI-helper closure is not yet complete.

Reproducible audit: `tools/audit_nmi_bank04_prg09_tail.py`.
