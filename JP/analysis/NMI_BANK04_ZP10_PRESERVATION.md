# Checkpoint 04F7 — raw bank `$04` alternate-parser ZP `$10` closure

This checkpoint audits the live raw-bank `$04` sound-stream path entered through fixed helper `$E1AF` and asks whether any reachable code can modify or alias shared ZP `$10` before OAM rendering.

All ROM claims use the exact Japanese target SHA-256:

```text
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
```

## Byte budget

Raw VRC6 bank `$04` maps CPU `$8000-$BFFF` to physical `PRG08/PRG09`.

The new checkpoint span is:

```text
physical PRG08 / CPU $8000-$91FF
4608 bytes
SHA-256 ee8b2de23022f715d3934907e7caaab91e824b4a9a31ccb75a69dae7d55c178b
```

This stays inside the agreed 500-5000-byte checkpoint budget. Raw bank `$05` and fixed `$E7FB` are deliberately not opened here.

## Parser code identity

Except for the bank-identifying byte at CPU `$8000` (`$04` here versus `$0C` in raw bank `$0C`), CPU `$8001-$87AD` is byte-identical to the alternate-parser code already audited in 04F5/04F6.

The bank-$04-specific stream/data region begins at `$87AE`.

## Exact bank-$04 metadata domain

The authoritative 125-entry sound metadata table in raw bank `$0C` contains:

```text
bank-$04 instrument references: 102
distinct bank-$04 stream roots: 96
sound IDs using bank $04:        17
```

The 17 sound IDs are:

```text
$5A $5D $5E $5F $60 $61 $62 $63 $64
$65 $66 $67 $68 $6A $6C $6D $6E
```

Each uses instruments `$00,$01,$02,$03,$04,$07`, for 17 references per instrument index.

Applying the parser-mode rule proven in 04F6:

```text
main parser:      first byte < $10, or instrument $05/$06
alternate parser: otherwise
```

all **102** bank-$04 references initialize alternate-parser mode. This makes raw bank `$04` a genuinely live alternate-parser bank, unlike the mostly main-parser bank `$0C` data domain.

The referenced stream-root range is `$87AE-$BE7D`; the final root `$BE7D` is `$FF`.

## `$842D` is not live in bank `$04`

The common alternate parser reaches indirect dispatch `$842D` only after command `$E7` sets bit 7 of `$018E,X` at `$8415`. `$844F` clears that bit after the parameter is consumed.

Across the referenced bank-$04 stream-storage range `$87AE-$BE7D`, there is exactly one raw byte `$E7`:

```text
$B818: FE FF E7 B7
```

It is not an `$E7` command.

The `FE` handler at `$8543` first advances to the next byte. When that byte is `$FF`, it advances again and reads two bytes into the stream pointer `$E0/$E1`:

```asm
8543  INY
8544  LDA ($E0),Y
8546  CMP #$FF
8548  BNE $856C
854A  INY
854B  LDA ($E0),Y    ; pointer low
854D  STA $012D,X
8550  STA $E2
8552  INY
8553  LDA ($E0),Y    ; pointer high
8555  STA $0136,X
8558  STA $E1
855A  LDA $E2
855C  STA $E0
855E  LDY #$00
```

Therefore bytes `$E7 $B7` at `$B81A-$B81B` are the little-endian pointer `$B7E7` consumed by `FE FF`; they never enter the command decoder as `$E7`.

A whole raw-bank census finds only one other `$E7` byte, at `$BFEB`. It is outside the referenced stream cluster and is the high byte of `JSR $E705` in unrelated PRG09 code:

```text
$BFE9: 20 05 E7  A6 69  60
       JSR $E705 ...    RTS
```

Thus bank `$04` has no live `$E7` command and cannot set the parser state that exposes the unbounded `$842D` table.

## Reachable write result

Starting at live entry `$8001` and adding only code-proven finite dispatch targets, the conservative parser graph contains **786 accepted instruction starts**.

Resolved indirect dispatch sites are:

```text
$802E  command high-nibble class table
$83E1  bounded E-command low-nibble table
$842D  E7 parameter table; not live for bank $04 data
$8641  active sound-channel dispatch
```

Within the graph:

- no direct `STA/STX/STY` or RMW instruction writes ZP `$10` / absolute `$0010`;
- no reachable `(zp,X)` or `(zp),Y` store can alias `$10`;
- no reachable zero-page-indexed store/RMW can wrap to `$10`;
- no reachable absolute-indexed write can reach `$0010` for any 8-bit index.

The only fixed-bank exits are the already-audited 04F3 helpers:

```text
calls: $E1B8 $E1C8 $E1D6 $E1F6 $E249
jumps: $E190 $E195 $E1E4 $E1EE
```

Those fixed helpers preserve `$10`.

## Result

**04F7 closes live raw bank `$04` alternate-parser execution as ZP `$10`-preserving.**

The remaining pre-render sound-side dependencies are raw instrument bank `$05` and fixed `$E7FB` / its inline dispatch. VPP remains **21/100** because transitive NMI helper closure is not yet complete.

Reproducible audit: `tools/audit_nmi_bank04_zp10.py`.
