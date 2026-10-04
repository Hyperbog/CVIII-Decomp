# Checkpoint 04F7 — raw bank `$04` alternate-parser boundary

This checkpoint continues the pre-render shared-ZP `$10` provenance audit after 04F6. It examines raw VRC6 bank `$04`, which maps CPU `$8000-$BFFF` to physical `PRG08/PRG09`, but deliberately limits new ROM coverage to physical `PRG08:$8000-$91FF`.

Target ROM SHA-256:

```text
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
```

New ROM span:

```text
raw bank $04 / physical PRG08
CPU $8000-$91FF
4608 bytes
SHA-256 ee8b2de23022f715d3934907e7caaab91e824b4a9a31ccb75a69dae7d55c178b
```

## Parser core identity

Fixed helper `$E1AF` banks the current instrument-data bank and jumps to CPU `$8001`. For raw bank `$04`, bytes `$8001-$87AD` are byte-identical to the already-audited bank `$0C` parser core. The only earlier difference is the bank-identifying byte at `$8000` (`$04` versus `$0C`); bank-specific data begins at `$87AE`.

The four alternate-parser indirect dispatch sites in this common core are:

```text
$802E  $83E1  $842D  $8641
```

The locally bounded tables for `$802E`, `$83E1`, and `$8641` match the bank `$0C` copies exactly. `$842D` still uses the ten-entry `$8430-$8443` table whose valid entries all target `$8444`; no new host-side bound is invented.

A conservative graph rooted at `$8001` plus the locally demonstrated table targets accepts **786 instruction starts**. Its only external fixed-bank calls/jumps are the same helpers already covered by 04F3:

```text
calls: $E1B8 $E1C8 $E1D6 $E1F6 $E249
jumps: $E190 $E195 $E1E4 $E1EE
```

Across that resolved executable graph, there is no direct, zero-page-indexed, indirect-store, absolute `$0010`, or absolute-indexed write form capable of modifying/aliasing ZP `$10`.

## Bank `$04` metadata domain

Reusing the exact 125-entry sound metadata table established in 04F6 gives:

```text
bank-$04 instrument references  102
distinct bank-$04 roots          96
```

Every bank-$04 reference initializes **alternate-parser mode** under the ROM's own rule: its first stream byte is `>= $10`, and none uses instrument `$05/$06`.

Inside the current `$8000-$91FF` span there are **23 referenced roots**, all distinct, belonging to sound IDs:

```text
$5A $5D $65 $67
```

Most importantly, the complete 4608-byte checkpoint span contains **zero raw `$E7` bytes**. Therefore `$E7` cannot be consumed as a command while the stream cursor is inside this bounded span, and the producer edge into `$840F/$842D` is absent for in-span bytes.

## Boundary

04F7 does **not** claim that raw bank `$04` is globally closed. The metadata domain contains roots beyond `$91FF`, and the final in-span root begins at `$9133`; later stream bytes are deliberately outside this checkpoint. Those bytes must be audited before bank `$04` can be declared fully `$10`-preserving.

What is now established is narrower and durable:

- the bank `$04` alternate-parser executable core `$8001-$87AD` is the proven bank `$0C` core;
- its resolved graph is `$10`-clean;
- all 102 bank-$04 metadata references select alternate-parser mode;
- the first bounded PRG08 data window contains no `$E7` byte at all;
- any remaining `$842D` producer-domain question lies in later bank `$04` stream data, not in the parser core or current span.

**VPP remains 21/100.** No rubric point is earned by this boundary closure alone.

Reproducible audit: `tools/audit_nmi_bank04_alt_parser.py`.

## Next checkpoint

04F8 should continue raw bank `$04` only, beginning at physical `PRG08` / CPU `$9200`, and close as much of the remaining PRG08 stream domain as fits the 500-5000-byte budget. Do not open raw bank `$05` or `$E7FB` in the same checkpoint.
