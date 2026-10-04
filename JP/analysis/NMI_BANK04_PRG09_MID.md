# Checkpoint 04F9 — raw bank `$04` PRG09 middle closure

This checkpoint continues the pre-render shared-ZP `$10` provenance audit from the repaired 04F8 frontier at CPU `$A014`.

Target ROM SHA-256:

```text
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
```

## Recovery gate

Before new analysis, the committed restart invariants were rechecked against the authoritative ROM:

- full ROM SHA-256 matches;
- 64-byte overlap `$9FD4-$A013` matches;
- frontier fingerprint `$A014-$A033` matches;
- reconciled 04F8 span `$920A-$A013` matches;
- the hardened 04F8 recursive audit reproduces the prior root-state counts and both repaired `FE FF lo hi` cycles.

The safe starting point is therefore exactly `$A014`.

## Exact bounded span

The handoff suggested `$A014-$B1FF`. The root at `$B1F0` cannot be closed inside the 5000-new-byte checkpoint budget: its recursive dependency reaches through `$B3CB`. Including that root would require:

```text
CPU $A014-$B3CB      5048 dependency bytes
33 prior root probes
5015 genuinely new bytes
```

Therefore 04F9 stops at the largest clean boundary before that root:

```text
raw bank $04 / physical PRG09
CPU $A014-$B1EF
4572 dependency bytes
SHA-256 55e35f223091a0c50beaf7ba0561445cc5c07d11ae83bfe827abcc22aa2d5a5b
```

04F7 already counted one first-byte mode probe for each later bank-$04 root. Thirty-two such root bytes lie inside this span:

```text
4572 dependency bytes
-  32 prior root probes
=4540 genuinely new bytes
```

This stays inside the 500-5000-byte checkpoint budget.

## Metadata domain

The established bank-$04 metadata census remains:

```text
instrument references: 102
distinct stream roots:  96
```

Every bank-$04 reference initializes alternate-parser mode under the ROM's first-byte/instrument rule.

04F9 closes 32 roots from sound IDs:

```text
$60 $61 $62 $63 $64 $66
```

The exact `(sound, instrument, root)` set is asserted by `tools/audit_nmi_bank04_prg09_mid.py`.

After this checkpoint:

```text
previously closed roots: 34
newly closed roots:      32
closed cumulative:       66 / 96
remaining:               30
next unresolved root:    $B1F0
```

## Hardened recursive stream result

The audit carries the established alternate-parser stream state:

- `FB`: loop-anchor establishment;
- `FD`: call/return state;
- `FE nn`: counted loop using the saved anchor;
- `FE FF lo hi`: absolute stream-pointer load;
- `FF`: actual stop command;
- instrument `$07`: its distinct parser rule before the shared `F?` handlers.

Every variable-width command is checked for complete operand containment **before** any operand byte is read.

Across the 32 roots:

```text
abstract parser states:           5869
unique decoded command addresses: 3776
earliest decoded command:         $A014
latest decoded command:           $B1EC
```

Resolved control edges:

```text
FD call:    9
FD return:  4
FE jump:   20
FE loop:   62
```

There are no missing loop anchors, operand escapes, recursive path escapes, or pointer targets outside `$A014-$B1EF`.

## `$E7` / `$842D` result

There are **zero raw `$E7` bytes** in `$A014-$B1EF`, and therefore zero decoded `$E7` commands in the closed producer domain.

None of these 32 roots can activate alternate-parser handler `$840F` or its unbounded indirect dispatch `$842D`.

The executable alternate-parser core `$8001-$87AD` was already proved ZP `$10`-clean in 04F7. Since 04F9 introduces no new parser-code path and no live `$E7`, these 32 roots preserve shared ZP `$10`.

This is producer-domain non-reachability, not proof of a local bound. Do not add a host-side bounds check to `$842D`.

## Result

**04F9 closes 32 additional bank-$04 roots as ZP `$10`-safe.**

```text
bank-$04 roots total       96
closed after 04F9          66
remaining                  30
next unresolved root       $B1F0
```

The remaining 30 roots occupy the rest of physical PRG09. Raw bank `$05` and fixed `$E7FB` remain untouched.

VPP remains **21/100** because transitive NMI-helper closure is still incomplete.

Reproducible audit: `tools/audit_nmi_bank04_prg09_mid.py`.
