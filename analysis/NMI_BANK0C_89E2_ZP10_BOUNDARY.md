# Checkpoint 04F5 — raw bank `$0C:$89E2` ZP `$10` boundary

This checkpoint follows the NMI-called raw-bank `$0C` helper starting at CPU `$89E2`. Raw VRC6 bank `$0C` maps CPU `$8000-$9FFF` to physical PRG24.

All claims are verified against Japanese ROM SHA-256:

```text
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
```

The initial 1 KiB window was expanded, within the agreed checkpoint budget, to absorb local control-flow edges.

Primary span:

```text
physical PRG24 / CPU $8000-$91FF
4608 bytes
SHA-256 2bd1badec12d9f68bf829c272105d85097966d6fb0419c206566eb54c7011734
entry: $89E2
```

## Direct ZP `$10` writes

The complete 4608-byte span contains no direct official-6502 store/RMW encoding targeting ZP `$10` or absolute `$0010`.

On the currently closed reachable graph, every dynamic write is absolute-indexed (`abs,X` / `abs,Y`) with base address at least `$0100`. No reachable `zp,X`, `zp,Y`, `(zp,X)`, or `(zp),Y` store/RMW form exists. Therefore the resolved portion of the graph cannot alias `$10` through indexing.

## Indirect dispatches closed in this checkpoint

The sound/update parser uses ZP `$E2/$E3` as a temporary jump pointer. Five indirect dispatches are now bounded by local masks/guards and finite pointer tables.

### `$802E`

The high command bits are reduced with `AND #$30` and three `LSR`s, so the table index is exactly `$00/$02/$04/$06`.

`$870B` targets:

```text
833D 837E 83B7 85B3
```

### `$83E1`

This path receives the command low nibble from `$802A-$802C`. Values `< $06` exit without indirect dispatch. Values `$06-$0F` subtract `$06`, double, and index the 10-entry table `$83E4-$83F7`.

Targets:

```text
83F8 840F 8456 845A 848C 849F 84ED 851D 852A 851D
```

### `$8641`

The root `$89E2` update loop iterates channel X from `$00` through `$08`. `$8628` uses that channel X, doubles it, and indexes the 9-entry table at `$86F9`.

Targets:

```text
86A9 86B4 86BF 8644 8644 8668 8668 869E 8644
```

### `$8B10`

`$011B,X & $06` yields only `$00/$02/$04/$06`, indexing `$8B14`.

Targets:

```text
8B2C 8C16 8C2A 8C83
```

### `$8E1D`

The local guards admit only command bytes `$E6-$EF` to this dispatch. Their low nibbles `$6-$F` subtract `$06`, double, and index the 10-entry table at `$8DD6`.

Targets:

```text
8E20 8E2A 8E34 8E3D 8E45 851D 851D 851D 851D 8E4B
```

Fixed-bank targets called/jumped to by these resolved paths are inside the already-audited 04F3 fixed span `$E057-$E365`, which preserves `$10`.

## Remaining indirect dispatch: `$842D`

`$842D` remains intentionally unresolved.

The code is:

```asm
8418  LDA ($E0),Y
841A  AND #$F0
841C  LSR A
841D  LSR A
841E  LSR A
841F  TAX
8420  DEY
8421  LDA $8430,X
8424  STA $E2
8426  LDA $8431,X
8429  STA $E3
842B  LDX $EE
842D  JMP ($00E2)
```

The physically demonstrated pointer table is exactly ten entries at `$8430-$8443`; all ten point to `$8444`:

```text
8444 8444 8444 8444 8444 8444 8444 8444 8444 8444
```

`$8444` is executable code immediately after the table. Extending the table beyond `$8443` would reinterpret executable bytes as pointers and repeats the class of table-boundary error already corrected in the IRQ work.

However, `AND #$F0` followed by three `LSR`s can mathematically produce byte offsets `$00,$02,...,$1E`. The local `$8418-$842D` code does **not** prove that the source command high nibble is limited to `$0-$9`.

Therefore this checkpoint does not invent that producer bound.

## Result

04F5 proves:

- the 4608-byte PRG24 span has no direct `$10` writer;
- all currently closed paths from `$89E2` have no indexed/indirect store capable of aliasing `$10`;
- five indirect dispatch families are fully bounded;
- only the command-domain proof feeding `$842D` remains before the complete `$89E2` helper graph can be declared to preserve `$10`.

The next checkpoint should trace only the producer/data domain of the byte consumed at `$8418` when the `$018E,X` high-bit path is active. Do not broaden into `$E7FB` yet.

Reproducible audit: `tools/audit_nmi_bank0c_zp10_boundary.py`.
