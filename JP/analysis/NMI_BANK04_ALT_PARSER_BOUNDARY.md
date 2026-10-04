# Checkpoint 04F7 — raw bank `$04` alternate-parser boundary

This checkpoint continues the pre-render shared-ZP `$10` provenance audit after 04F6. Raw VRC6 bank `$04` maps CPU `$8000-$BFFF` to physical `PRG08/PRG09`.

Target ROM SHA-256:

```text
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
```

## Exact byte budget

The planned contiguous span was `$8000-$91FF` (4608 bytes). The final in-window root begins at `$9133`; 04F7 extended the contiguous span by 10 bytes through `$9209` to include its first raw `$FF` control marker:

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

The bank-specific stream-data region `$87AE-$9209` contains **zero raw `$E7` bytes**.

## 04F8 correction to first-`$FF` wording

The original 04F7 write-up called the first raw `$FF` after each of these roots a terminator. That was too strong: **11 of the 23 recorded first-`$FF` positions are the `$FF` marker inside `FE FF lo hi` absolute-pointer commands**, not stop commands.

Checkpoint 04F8 adds a recursive command/pointer decoder that rechecks all 23 04F7 roots using the actual alternate-parser grammar (`FB` loop anchors, `FD` call/return, and `FE` counted/absolute-pointer control). That decoder proves:

- no reachable `$E7` command occurs in any of the 23 roots;
- every resolved `FD`/`FE` pointer target remains inside `$87AE-$9209`;
- no counted `FE` loop lacks a preceding `FB` loop anchor;
- the latest reachable command byte is `$9208`.

Therefore the 04F7 safety result remains valid, but the correct basis is **recursive command/pointer closure**, not first-raw-`$FF` termination.

Evidence for the correction: `analysis/NMI_BANK04_PRG08_TAIL.md`, `tools/audit_nmi_bank04_prg08_tail.py`.

## Boundary at completion of 04F7

As of the end of 04F7:

- bank `$04` parser core `$8001-$87AD` was byte-identical to the proven bank `$0C` alternate-parser core;
- its resolved graph was `$10`-clean;
- all 102 bank-$04 references selected alternate-parser mode;
- the first 23 bank-$04 roots were closed through `$9209` with no live `$E7` producer;
- 73 later stream bodies remained unresolved.

**VPP remained 21/100.** No rubric point was earned by this boundary closure alone.

Reproducible 04F7 audit: `tools/audit_nmi_bank04_alt_parser.py`. Its first-raw-`$FF` list is retained as a byte-level checkpoint, while 04F8 supersedes the old terminator interpretation.
