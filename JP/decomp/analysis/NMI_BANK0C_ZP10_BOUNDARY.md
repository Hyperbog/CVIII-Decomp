# Checkpoint 04F5 — raw bank `$0C:$89E2` ZP `$10` boundary

This checkpoint audits the NMI-called raw-bank `$0C` helper beginning at CPU `$89E2` and asks only whether its reachable PRG24 code can modify the shared OAM attribute cache at ZP `$10`.

All ROM claims use the exact Japanese target SHA-256:

```text
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
```

## Byte budget

The initial 1 KiB window `$8800-$8BFF` exposed same-bank helper targets outside that sub-window, including `$87AE/$87DA`, `$8D06/$8DCD`, and `$8F55`.

To close those local edges without splitting one question across arbitrary boundaries, the checkpoint expanded within the agreed 500-5000 byte budget to:

```text
physical PRG24 / CPU $8000-$91FF
4608 bytes
SHA-256 2bd1badec12d9f68bf829c272105d85097966d6fb0419c206566eb54c7011734
```

Raw VRC6 bank `$0C` maps CPU `$8000-$9FFF` to physical PRG24.

## Reachable write result

Starting at `$89E2` and adding only code-proven finite indirect-dispatch targets, the audit reaches 1488 accepted instruction starts.

Within that graph:

- there is no direct `STA/STX/STY` or RMW write to ZP `$10` / absolute `$0010`;
- there is no reachable `(zp,X)` or `(zp),Y` store;
- there is no reachable zero-page-indexed store/RMW that could wrap to `$10`;
- all reachable absolute-indexed writes have bases whose full 8-bit index domain cannot wrap or add to `$0010`.

Therefore the closed portion of the `$89E2` helper graph preserves ZP `$10`.

## Fixed-bank exits are already covered

The statically resolved graph leaves PRG24 only through these fixed-bank calls/jumps:

```text
calls: $E1B8 $E1C8 $E1D6 $E1F6 $E249
jumps: $E190 $E195 $E1AF $E1E4 $E1EE
```

All are inside the fixed-bank `$E057-$E365` span already audited in checkpoint 04F3, which preserves `$10`. No new fixed-bank ROM span is introduced here.

## Finite indirect dispatches closed locally

The following indirect jumps have code-local domains:

- `$802E`: command class `$C0-$F0` selects four local targets from `$870B`;
- `$83E1`: low nibble `< $06` is handled directly; `$06-$0F` selects ten local targets from `$83E4`;
- `$8641`: channel-index dispatch uses the active sound-channel loop domain;
- `$8B10`: `$011B,X & $06` selects four local targets from `$8B14`;
- `$8E1D`: preceding comparisons prove the path sees command bytes `$E6-$EF`, selecting ten local targets from `$8DD6`.

These dispatch targets remain inside the audited PRG24 span and are included in the graph.

## Remaining boundary: `$842D`

One indirect jump cannot be closed from code-local bounds alone.

Command `$E7` reaches `$840F`, which advances to the next stream byte and then executes:

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

The local pointer block contains ten entries, all `$8444`, covering next-byte high nibbles `$0-$9`:

```text
$8430-$8443 = 44 84 repeated ten times
```

However, the code shown above does **not** bounds-check the next stream byte to `$00-$9F`. Under the project fidelity rules, the ten-entry table shape is not sufficient proof of the producer domain.

Therefore this checkpoint deliberately does **not** claim unconditional full closure of the raw-bank path. The remaining question is whether the ROM's actual sound-stream producers can ever supply command `$E7` followed by a byte with high nibble `$A-$F`.

## Result

**04F5 result:** the `$89E2` banked helper is proven `$10`-clean throughout the statically closed 4608-byte PRG24 graph, and every explicit fixed-bank exit is already `$10`-clean from 04F3. The only remaining bank-$0C control-flow uncertainty is the producer domain of the byte following stream command `$E7` at indirect dispatch `$842D`.

Do not infer that domain from the 10-entry table alone.

Reproducible audit: `tools/audit_nmi_bank0c_zp10.py`.
