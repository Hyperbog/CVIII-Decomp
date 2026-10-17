# Checkpoint 04F8 — raw bank `$04` PRG08-tail closure (reconciled)

This checkpoint continues the pre-render shared-ZP `$10` provenance audit from 04F7 and records the repaired dependency accounting required by the interruption/restart integrity check.

Target ROM SHA-256:

```text
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
```

## Repaired byte accounting

The original 04F8 write-up ended the dependency span at `$A011`. The hardened decoder proves that the command at `$A010` is:

```text
A010: FE FF 85 9E
```

and therefore reads operand bytes through `$A013`.

The authoritative 04F8 dependency span is now:

```text
raw bank $04 / CPU $920A-$A013
half-open [$920A,$A014)
3594 bytes
SHA-256 728c86cd808e178821f7f72d1f0371eb16a5bde3a1dda495543338391a5e7b3c
```

Eleven root-mode probe bytes in this span were already counted by 04F7:

```text
3594 dependency bytes
-  11 prior probe bytes
=3583 genuinely new bytes for 04F8
```

This remains inside the checkpoint budget.

## 04F7 boundary repair

The restart audit also exposed that prior root `$9133` reaches:

```text
9208: FE FF 33 91
```

The command byte `$9208` was inside the old 04F7 contiguous span ending at `$9209`, but its low/high pointer operands at `$920A-$920B` were not.

This does not require redoing the parser core or the earlier root graph. The strict decoder revalidates the 23 prior roots using semantic span `$87AE-$920B` while leaving 04F7's byte-coverage accounting unchanged. Bytes `$920A-$920B` are assigned to 04F8's new-byte coverage but are also the operand overlap needed to prove the `$9133` cycle.

Strict revalidation result:

```text
prior roots:                23
abstract parser states:     2819
unique command addresses:   2169
latest command address:     $9208
decoded E7 commands:        0
affected edge:              $9208 FE FF 33 91 -> $9133
pointer/operand escapes:    0
```

Thus the substantive 04F7 safety result remains valid.

## 04F8 metadata domain

Exactly 11 distinct bank-$04 roots are closed by this checkpoint:

```text
sound $5D, instrument $07 -> $920C
sound $5E, instrument $03 -> $92DB
sound $5E, instrument $04 -> $93FA
sound $5E, instrument $07 -> $95E3
sound $5E, instrument $00 -> $967E
sound $5E, instrument $01 -> $974D
sound $5E, instrument $02 -> $9900
sound $60, instrument $03 -> $99E9
sound $60, instrument $04 -> $9BAF
sound $60, instrument $07 -> $9D21
sound $60, instrument $00 -> $9E85
```

All were already proven by 04F7's root probes to initialize alternate-parser mode.

## Hardened recursive stream result

`tools/audit_nmi_bank04_prg08_tail.py` now asserts that every multi-byte decoded command has all parameter bytes inside the claimed semantic span before reading them.

The decoder carries the established alternate-parser stream grammar:

- `FB`: loop-anchor establishment;
- `FD`: call/return;
- `FE nn`: counted loop;
- `FE FF lo hi`: absolute stream pointer load;
- `FF`: stop command;
- instrument `$07`: its distinct `$8031` rule before shared `F?` handlers.

For the 11 04F8 roots:

```text
abstract parser states:      3312
unique command addresses:    3025
earliest command:            $920C
latest command:              $A010
decoded E7 commands:         0
operand escapes:             0
pointer-target escapes:      0
```

The final cross-bank cycle is:

```text
A010: FE FF 85 9E -> $9E85
```

with all four bytes `$A010-$A013` inside the repaired dependency span.

There are zero raw `$E7` bytes in `$920A-$A013`, so none of these 11 roots can activate alternate-parser handler `$840F` or indirect dispatch `$842D`.

Because the executable alternate-parser core was already proven ZP `$10`-clean, these roots preserve shared `$10`.

## Reconciled result

**04F8 is now fully reconciled and no longer provisional.**

After the repair:

```text
bank-$04 roots total          96
closed in corrected 04F7      23
closed in 04F8                11
closed cumulative             34
remaining                     62
first unresolved root         $A014
```

Raw bank `$05` and fixed `$E7FB` remain untouched.

VPP remains **21/100** because the transitive NMI-helper closure is still incomplete.

Reproducible audit: `tools/audit_nmi_bank04_prg08_tail.py`.
