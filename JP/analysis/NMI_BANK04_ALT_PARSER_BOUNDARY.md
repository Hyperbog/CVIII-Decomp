# Checkpoint 04F7 — raw bank `$04` alternate-parser boundary

This checkpoint continues the pre-render shared-ZP `$10` provenance audit after 04F6. Raw VRC6 bank `$04` maps CPU `$8000-$BFFF` to physical `PRG08/PRG09`.

Target ROM SHA-256:

```text
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
```

## Exact byte budget

The planned contiguous span was `$8000-$91FF` (4608 bytes). The final root inside that window begins at `$9133` and reaches its `$FF` terminator at `$9209`, so the contiguous span was expanded by 10 bytes to close that same root:

```text
raw bank $04 / physical PRG08
CPU $8000-$9209
4618 bytes
SHA-256 cfdd27fa72b9e990c31bb12e1511fa7229ffe2c898dcc361586c77b71543caa6
```

The metadata audit also reads the first byte of the 73 distinct bank-$04 roots that begin after `$9209` in order to apply the already-proved parser-mode rule. Those are 73 one-byte probes outside the contiguous span.

Therefore the exact 04F7 new-byte footprint is:

```text
4618 contiguous bytes + 73 isolated root bytes = 4691 bytes
```

This remains inside the 500-5000-byte checkpoint limit.

## Parser core identity

Fixed helper `$E1AF` banks the current instrument-data bank and jumps to CPU `$8001`. For raw bank `$04`, bytes `$8001-$87AD` are byte-identical to the already-audited bank `$0C` alternate-parser core. The bank-identifying byte at `$8000` is `$04` rather than `$0C`; bank-specific data begins at `$87AE`.

The four alternate-parser indirect dispatch sites in the common core are:

```text
$802E  $83E1  $842D  $8641
```

The locally bounded tables for `$802E`, `$83E1`, and `$8641` match the bank `$0C` copies. `$842D` still uses the ten-entry `$8430-$8443` table whose valid entries all target `$8444`; no host-side bound is invented.

A conservative graph rooted at `$8001` plus the locally demonstrated dispatch targets accepts **786 instruction starts**. Its external fixed-bank dependencies are exactly:

```text
calls: $E1B8 $E1C8 $E1D6 $E1F6 $E249
jumps: $E190 $E195 $E1E4 $E1EE
```

These fixed helpers were already covered by 04F3. Across the resolved bank-$04 executable graph there is no direct, zero-page-indexed, indirect-store, absolute `$0010`, or absolute-indexed write form capable of modifying or aliasing ZP `$10`.

## Bank `$04` metadata domain

Reusing the exact 125-entry sound metadata table established in 04F6 gives:

```text
bank-$04 instrument references  102
distinct bank-$04 roots          96
```

Every bank-$04 reference initializes **alternate-parser mode** under the ROM's own rule: each probed first byte is `>= $10`, and none uses instrument `$05/$06`.

Exactly **23 distinct roots** begin inside the contiguous 04F7 span. They belong to sound IDs:

```text
$5A $5D $65 $67
```

All 23 reach their `$FF` terminator by `$9209`. The bank-specific stream-data region `$87AE-$9209` contains **zero raw `$E7` bytes**. Therefore `$E7` cannot be consumed from any of these bounded stream bodies, and the producer edge into `$840F/$842D` is absent for this closed data subset.

## Boundary

04F7 does **not** claim raw bank `$04` is globally closed. Seventy-three distinct roots begin after `$9209`; only their first mode-selection byte was probed here. Their stream bodies remain unresolved and may still contain a live `$E7` producer for `$842D`.

Established after 04F7:

- bank `$04` parser core `$8001-$87AD` is byte-identical to the proven bank `$0C` alternate-parser core;
- its resolved graph is `$10`-clean;
- all 102 bank-$04 references select alternate-parser mode;
- the first 23 bank-$04 roots terminate by `$9209` and contain no raw `$E7` in their bounded data region;
- remaining `$842D` producer-domain work lies in the 73 later stream bodies.

**VPP remains 21/100.** No rubric point is earned by this boundary closure alone.

Reproducible audit: `tools/audit_nmi_bank04_alt_parser.py`.

## Next checkpoint

04F8 should continue raw bank `$04` from CPU `$920A` through the remaining PRG08 tail, carrying the established alternate-parser/current-bank state. Do not open raw bank `$05` or `$E7FB` in the same checkpoint.
