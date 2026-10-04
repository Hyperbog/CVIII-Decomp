# Checkpoint 04FE — fixed PRG31 inline dispatcher / main-script table

This checkpoint begins from the committed fixed-bank frontier at `PRG31:$E7FB` and resolves the calling convention plus the two inline pointer tables directly exposed by the pre-render NMI path. It deliberately does **not** claim transitive closure of every dispatched handler.

Authoritative JP ROM SHA-256:

```text
958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
```

## Recovery

The schema-v6 04FD handoff was rechecked before analysis:

- raw bank `$05:$BEC6-$BF05` overlap matches;
- fixed `PRG31:$E7FB-$E81A` fingerprint matches;
- the 04FD bank-$05 audit reproduces;
- bank `$05` remains 72/72 roots closed and ZP `$10`-safe.

## Exact dependency accounting

04FE uses three fixed-PRG31 spans:

```text
A  $E35C-$E558   509 dependency bytes
   SHA-256 b22290e667392d25d75176c8685f9263794c20b9ce7e951b089dc09c4a1620bf
   prior 04F3 overlap $E35C-$E365 = 10 bytes
   genuinely new bytes = 499
   new-only $E366-$E558 SHA-256
   abf6303fbc6aaffd176abb96abb4e9a7150e4420498ccf438da6b2f4156baea0

B  $E7FB-$E826    44 genuinely new bytes
   SHA-256 1475029da3717f4674b4ed14f88cd238ef0612744133cfcbaad593722b37ff99

C  $F390-$F3DC    77 genuinely new bytes
   SHA-256 534f1b3ff2e7b25348a1a4c66479018ec9153d63b3e9f9b964f9e07483905b15
```

Total:

```text
630 dependency bytes
- 10 prior bytes
= 620 genuinely new ROM bytes
```

## `$E7FB`: A-indexed stack-consuming inline dispatcher

Exact JP code:

```asm
E7FB  0A        ASL A
E7FC  84 03     STY $03
E7FE  A8        TAY
E7FF  C8        INY
E800  68        PLA
E801  85 00     STA $00
E803  68        PLA
E804  85 01     STA $01
E806  B1 00     LDA ($00),Y
E808  85 02     STA $02
E80A  C8        INY
E80B  B1 00     LDA ($00),Y
E80D  A4 03     LDY $03
E80F  85 03     STA $03
E811  6C 02 00  JMP ($0002)
```

This is not an ordinary returning helper.

On entry from `JSR $E7FB`, the stack contains the caller return address, which points to the final operand byte of the `JSR`. `$E7FB`:

1. doubles A to a word-table byte offset;
2. saves caller Y in `$03`;
3. pops the JSR return address into `$00/$01`;
4. uses `Y = 2*A + 1`, so `($00),Y` addresses the first byte of the word table immediately following the JSR;
5. loads the selected word into `$02/$03`;
6. restores caller Y;
7. executes `JMP ($0002)`.

Because `$E7FB` consumes the JSR return address, the selected target's eventual `RTS` returns to the caller *above* the routine that invoked `$E7FB`. A native lift must preserve this non-local calling convention; it must not model `$E7FB` as a conventional C function returning to the bytes after the inline table.

## `$E814`: Y-indexed sibling dispatcher

The 19 bytes immediately following `$E7FB` form a related helper:

```asm
E814  C8        INY
E815  68        PLA
E816  85 00     STA $00
E818  68        PLA
E819  85 01     STA $01
E81B  B1 00     LDA ($00),Y
E81D  85 02     STA $02
E81F  C8        INY
E820  B1 00     LDA ($00),Y
E822  85 03     STA $03
E824  6C 02 00  JMP ($0002)
```

This variant also consumes the JSR return address but uses caller Y directly as the inline-table byte offset. It does not preserve Y.

## NMI call site and JP `$18` table

The 04F3 NMI helper reaches:

```asm
E35C  INC $1B
E35E  LDA $18
E360  JSR $E7FB
```

The 32 bytes immediately following the JSR, `$E363-$E382`, are a 16-entry word table. The exact JP targets are:

```text
$00 -> $E383
$01 -> $E436
$02 -> $E437
$03 -> $E449
$04 -> $F390
$05 -> $E459
$06 -> $E49B
$07 -> $E539
$08 -> $E50E
$09 -> $E516
$0A -> $E541
$0B -> $E549
$0C -> $E51E
$0D -> $E526
$0E -> $E52E
$0F -> $E531
```

The existing US Castlevania III disassembly labels the analogous `$18` field as a main-script state and likewise describes a 00-0F state family. That is useful naming evidence only; the table, targets, and calling convention above are independently verified from the JP ROM.

**Important:** the JP table has 16 entries but `$E7FB` performs no bounds check. This checkpoint does not infer `A <= $0F` merely from table size. Exhaustive JP `$18` producer-domain closure remains open.

## State `$04`: nested gameplay dispatcher

JP table entry `$04` reaches fixed `$F390`:

```asm
F390  JSR $F6AE
F393  LDA $2D
F395  BEQ $F398
F397  RTS
F398  LDA $2C
F39A  JSR $E7FB
```

`$F39D-$F3DC` is a 32-entry inline word table:

```text
00 F3FC   01 F402   02 F48D   03 F531
04 F5A8   05 F5D2   06 F61D   07 F62C
08 F965   09 F638   0A F511   0B F831
0C F839   0D F841   0E F841   0F F4E7
10 F849   11 F65B   12 F652   13 F713
14 F739   15 F792   16 F7CF   17 F653
18 F6EC   19 F3F4   1A F6E4   1B F4FA
1C F6F4   1D F6FE   1E F3EC   1F F3DD
```

Again, table size is not treated as a producer bound. The JP `$2C` producer domain and the 32 target graphs remain open.

## ZP `$10` result at this boundary

Across the three 04FE dependency spans there is no raw encoding for a direct ZP `$10` store/RMW (`STA/STX/STY`, `INC/DEC`, `ASL/LSR/ROL/ROR`).

That statement is intentionally narrow. It does **not** prove:

- indexed/indirect writes in every selected handler cannot alias `$10`;
- banked helpers called by those handlers preserve `$10`;
- state `$04`'s `$2C` target graph preserves `$10`.

Earlier project evidence already establishes that ordinary gameplay code can use `$10` as unrelated scratch. Therefore transitive pre-render preservation cannot be promoted from the local no-direct-write result alone.

## Result

**04FE closes the exact ABI and JP inline-table structure of fixed `$E7FB/$E814`, the 16-entry NMI `$18` dispatch table, and the 32-entry nested gameplay `$2C` table.**

It does **not** yet close the full pre-render dependency. Remaining semantic edges are:

1. prove the JP `$18` producer domain before treating the 16-entry table as bounded;
2. reconcile the selected top-level handler graphs and their banked exits;
3. prove the JP `$2C` producer domain and the 32 gameplay targets;
4. audit any resulting fixed/gameplay scratch paths that can modify shared ZP `$10`.

VPP remains **21/100**. The CPU/mapper/interrupt rubric point for transitive NMI helper/bank-context closure is still open.

Reproducible audit: `tools/audit_nmi_main_script_dispatch.py`.

## Next checkpoint

**04FF — JP `$18` main-script producer domain and top-level target-edge classification.**

Use the external US disassembly aggressively to locate candidate equivalent writers/state transitions, but promote only JP-ROM-backed producer values and control-flow evidence. Do not infer table bounds from the US labels or from table length.
