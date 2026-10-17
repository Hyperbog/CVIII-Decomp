# Checkpoint 04FD — raw bank `$05` PRG11 tail closure

This checkpoint finishes the remaining pre-render sound-stream producer domain in raw VRC6 bank `$05` / physical PRG11 from the committed frontier at CPU `$AD97`.

Authoritative ROM SHA-256:

```text
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
```

## Recovery

Before forward work, the committed 04FC state was rechecked against the ROM. The raw-bank `$05` overlap `$AD57-$AD96`, frontier fingerprint `$AD97-$ADB6`, prior 04FC dependency hash, and parser-core identity all matched.

A stale paragraph in `docs/INTERRUPTION_RECOVERY.md` still described the old resolved 04F7/04F8 repair as an active hold. That documentation inconsistency was corrected before 04FD evidence was promoted; the historical repair remains recorded, but current forward work is governed by the committed ready `RESUME_STATE.json` frontier.

## Exact 04FD dependency span

All 28 remaining bank-`$05` roots close inside the remaining physical PRG11 tail. The last reachable command/operand byte is `$BF05`.

```text
raw bank $05 / physical PRG11
CPU $AD97-$BF05
4463 dependency bytes
4463 genuinely new bytes
SHA-256 30f4e1640f97c342886a4d5f1a652cbfda41102abbd4760501bcd2915b474a72
```

The 34 metadata references share 28 distinct roots across sound IDs:

```text
$57 $58 $59 $5B $69 $6B
```

After 04FD:

```text
bank-$05 roots total       72
closed                     72
remaining                   0
```

## Hardened recursive result

The audit preserves the established alternate-parser model for `FB` loop anchors, context-sensitive `FD` call/return, `FE nn` counted loops, `FE FF lo hi` absolute stream pointers, and the instrument-$07 non-`F?` rule. Every variable-width command must have all consumed operand bytes inside the accounted dependency before they are read.

Across the final 34 metadata references / 28 roots:

```text
abstract parser states:            5346
unique decoded command addresses:  3433
earliest decoded command:          $AD97
latest decoded command:            $BF05
FD calls / returns:                28 / 28
FE jumps / loops:                  15 / 43
operand/path escapes:              0
pointer-target escapes:            0
```

The maximum byte read is exactly the exclusive endpoint `$BF06`, so the dependency is closed through `$BF05` without consuming unused bytes after it.

## Live `$E7` producer-domain proof

There are 21 raw `$E7` bytes in the dependency span, of which 13 are decoded `$E7` commands. The unique decoded command/parameter pairs are:

```text
$AE6D -> $05
$B18A -> $85
$B34E -> $84
$B355 -> $85
$B470 -> $84
$B679 -> $24
$B69D -> $24
$B724 -> $24
$B73A -> $24
$B7D5 -> $24
$B7F9 -> $24
$B876 -> $24
$B88C -> $24
```

Their producer high-nibble domain is exactly:

```text
$0 $2 $8
```

The common `$840F` handler masks the following byte's high nibble and doubles it to index pointer pairs at `$8430-$8443`. High nibbles `$0`, `$2`, and `$8` are all inside the ROM's ten-entry `$0-$9` domain, and every selected table entry resolves to `$8444`.

`$8444` is already part of the audited common parser graph and is ZP `$10`-clean. Therefore every live 04FD `$E7` path is closed from actual JP-ROM producer values. No generic host-side bounds check is added at `$842D`.

## Bank `$05` conclusion

Raw bank `$05:$8001-$87AD` is byte-identical to the already-audited bank-`$04` common parser core, whose resolved graph contains no write form capable of modifying or aliasing shared ZP `$10`.

04FB, 04FC, and 04FD now close all 72 metadata roots, including every live `$E7` producer domain encountered across bank `$05`.

**Result: the entire raw-bank `$05` producer domain preserves shared ZP `$10`.**

## Next pre-render dependency

The remaining unresolved pre-render dependency is fixed-bank `PRG31:$E7FB` and its inline dispatch. This is deliberately not opened in 04FD.

The fixed-bank range `$E7FB-$EBFF` is 1029 bytes of not-yet-accounted PRG31 territory before the already-audited 04F4 `$EC00-$EFFF` helper span. The next checkpoint should begin at `$E7FB`, following only the actual fixed-bank control/data dependencies and treating any edges into prior audited fixed-bank spans as overlap rather than new coverage.

VPP remains **21/100** because fixed `$E7FB` / inline-dispatch closure is still required before the transitive pre-render NMI-helper item can be reconsidered.

Reproducible audit: `tools/audit_nmi_bank05_prg11_tail.py`.
