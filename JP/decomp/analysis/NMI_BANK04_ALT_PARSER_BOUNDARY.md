# Checkpoint 04F7 — raw bank `$04` alternate-parser boundary

This checkpoint continues the pre-render shared-ZP `$10` provenance audit after 04F6. Raw VRC6 bank `$04` maps CPU `$8000-$BFFF` to physical `PRG08/PRG09`.

Target ROM SHA-256:

```text
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
```

## Exact byte budget

The planned contiguous span was `$8000-$91FF` (4608 bytes). The final in-window root begins at `$9133`; 04F7 extended the contiguous span by 10 bytes through `$9209`:

```text
raw bank $04 / physical PRG08
CPU $8000-$9209
4618 bytes
SHA-256 cfdd27fa72b9e990c31bb12e1511fa7229ffe2c898dcc361586c77b71543caa6
```

The metadata audit also reads the first byte of the 73 distinct bank-$04 roots that begin after `$9209` to apply the already-proved parser-mode rule. Those are 73 one-byte probes outside the contiguous span.

Therefore the exact 04F7 new-byte footprint remains:

```text
4618 contiguous bytes + 73 isolated root bytes = 4691 bytes
```

The later 04F8 repair does **not** reassign byte coverage to 04F7. It only supplies semantic operand overlap at `$920A-$920B` needed to prove the final 04F7 stream cycle.

## Parser core identity

Fixed helper `$E1AF` banks the current instrument-data bank and jumps to CPU `$8001`. For raw bank `$04`, bytes `$8001-$87AD` are byte-identical to the already-audited bank `$0C` alternate-parser core. The bank-identifying byte at `$8000` is `$04` rather than `$0C`; bank-specific data begins at `$87AE`.

The four alternate-parser indirect dispatch sites in the common core are:

```text
$802E  $83E1  $842D  $8641
```

The locally bounded tables for `$802E`, `$83E1`, and `$8641` match the bank `$0C` copies. `$842D` still uses the ten-entry `$8430-$8443` table; no host-side bound is invented.

A conservative graph rooted at `$8001` plus locally demonstrated dispatch targets accepts **786 instruction starts**. Its fixed-bank dependencies are already covered by 04F3. Across the resolved bank-$04 executable graph there is no write form capable of modifying or aliasing ZP `$10`.

## Bank `$04` metadata domain

Reusing the exact sound metadata table established in 04F6 gives:

```text
bank-$04 instrument references  102
distinct bank-$04 roots          96
```

Every bank-$04 reference initializes **alternate-parser mode** under the ROM's own rule: each probed first byte is `>= $10`, and none uses instrument `$05/$06`.

Exactly **23 distinct roots** begin inside the contiguous 04F7 coverage range. They belong to sound IDs:

```text
$5A $5D $65 $67
```

The bank-specific stream-data region `$87AE-$9209` contains zero raw `$E7` bytes.

## Reconciled stream-control correction

The original 04F7 write-up treated the first raw `$FF` after each root as a terminator. 04F8 corrected this: 11 of those positions are the `$FF` marker inside `FE FF lo hi` absolute-pointer commands.

The hardened 04F8 decoder rechecks all 23 04F7 roots using the actual `FB`/`FD`/`FE` grammar and strict operand-in-span assertions.

One boundary cycle matters:

```text
9208: FE FF 33 91 -> $9133
```

The command begins inside 04F7's contiguous coverage, but its final two pointer operands are `$920A-$920B`. Those two bytes are assigned to 04F8's byte coverage while serving as semantic overlap for the 04F7 closure.

Strict revalidation proves:

```text
prior roots:                23
abstract parser states:     2819
unique command addresses:   2169
latest command address:     $9208
decoded E7 commands:        0
operand escapes:            0
pointer-target escapes:     0
```

All resolved pointer **targets** remain in the prior stream domain; the semantic read boundary extends through `$920B` solely because the `$9208` command is four bytes long.

Therefore the 04F7 safety result remains valid. The correct basis is recursive command/pointer closure with explicit operand accounting, not first-raw-`$FF` termination.

Evidence: `analysis/NMI_BANK04_PRG08_TAIL.md`, `tools/audit_nmi_bank04_prg08_tail.py`.

## Boundary at completion of 04F7

The stable 04F7 result is:

- parser core `$8001-$87AD` is byte-identical to the proven bank `$0C` alternate-parser core;
- its resolved graph is ZP `$10`-clean;
- all 102 bank-$04 references select alternate-parser mode;
- the first 23 bank-$04 roots are recursively closed with no live `$E7`;
- byte coverage remains exactly the original 4691-byte footprint;
- semantic closure of root `$9133` uses the 04F8-owned operand overlap `$920A-$920B`;
- 73 later stream bodies remained unresolved at this checkpoint.

**VPP remained 21/100.**

Reproducible 04F7 audit: `tools/audit_nmi_bank04_alt_parser.py`. The hardened recursive boundary proof is in `tools/audit_nmi_bank04_prg08_tail.py`.
