# Checkpoint 04F9 — raw bank `$04` PRG09 middle closure

This checkpoint continues the pre-render ZP `$10` provenance audit for raw VRC6 bank `$04`, beginning at the committed 04F8 frontier `$A012`.

Target ROM SHA-256:

```text
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
```

## Recovery / frontier verification

Before new analysis, the committed recovery invariants were rechecked against the authoritative ROM:

- 64-byte verification overlap `$9FD2-$A011`: matches;
- 32-byte frontier fingerprint `$A012-$A031`: matches;
- 04F8 dependency span `$920A-$A011`: matches;
- 04F8 recursive closure reproduces 3312 abstract states / 3025 unique command addresses with no `$E7` and no pointer escape.

The safe starting byte is therefore exactly `$A012`.

## Bounded dependency span

The handoff suggested `$A012-$B1FF`. The root at `$B1F0` does not close inside that suggested window, so 04F9 stops before that root rather than claiming partial closure.

Closed span:

```text
raw bank $04 / physical PRG09
CPU $A012-$B1EF
4574 contiguous bytes
SHA-256 796390314526db34b3a63e6abc838c06bebf1194456f98dda39f40743dd816d7
```

04F7 already counted one root-mode probe byte for every later bank-$04 root. Thirty-two such root bytes fall inside this span, so the exact 04F9 new-byte footprint is:

```text
4574 contiguous bytes - 32 previously counted root probes = 4542 new bytes
```

This remains inside the 500-5000-byte checkpoint budget.

## Metadata domain

The bank-$04 metadata census remains:

```text
instrument references: 102
distinct stream roots: 96
```

All bank-$04 references initialize alternate-parser mode under the ROM's first-byte/instrument rule.

04F9 closes 32 roots from sound IDs:

```text
$60 $61 $62 $63 $64 $66
```

The exact root set is verified by `tools/audit_nmi_bank04_prg09_mid.py`.

After this checkpoint:

```text
previously closed roots: 34
newly closed roots:      32
total closed:            66 / 96
remaining:               30
next root:               $B1F0
```

## Recursive stream result

The decoder carries the already-established alternate-parser stream state:

- `FB`: loop-anchor establishment;
- `FD`: call/return state;
- `FE xx`: counted loop using the current anchor;
- `FE FF lo hi`: absolute stream jump.

Across the 32 roots, the audit reaches:

```text
abstract parser states:          5869
unique decoded command addresses: 3776
lowest decoded command:          $A014
highest decoded command:         $B1EC
```

Resolved control edges:

```text
FD call:   9
FD return: 4
FE jump:  20
FE loop:  62
```

Every resolved `FD`/`FE` target remains within `$A012-$B1EF`. There are no missing loop anchors and no recursive paths escaping the closed span.

## `$E7` / `$842D` result

There are **zero raw `$E7` bytes** anywhere in `$A012-$B1EF`, and therefore zero decoded `$E7` commands.

Thus none of these 32 roots can reach the alternate-parser `$E7` handler at `$840F` or its indirect dispatch at `$842D`.

The executable alternate-parser core was already proved in 04F7 to contain no reachable write form capable of modifying or aliasing ZP `$10`. With no new parser-code path activated here, these 32 stream roots preserve `$10`.

## Result

**04F9 closes 32 additional raw-bank `$04` roots as ZP `$10`-safe.**

The remaining bank-$04 boundary is root `$B1F0`; 30 of 96 roots remain unresolved in the rest of physical PRG09.

No host-side bound may be added to `$842D`; this checkpoint proves non-reachability for the closed producer domain, not a local table bound.

**VPP remains 21/100.** This advances the transitive NMI-helper evidence but does not yet complete the rubric item because later bank `$04`, bank `$05`, and fixed `$E7FB` dependencies remain open.

Reproducible audit: `tools/audit_nmi_bank04_prg09_mid.py`.
