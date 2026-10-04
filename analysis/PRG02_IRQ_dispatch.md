# PRG02 IRQ dispatch analysis

## Context

`PRG31:$E0F5` is the IRQ vector. At `$E100` it loads bank value `$01` and calls the raw VRC6 16 KiB bank selector at `$E2D2`. Therefore CPU `$8000-$9FFF` maps physical `PRG02` and `$A000-$BFFF` maps physical `PRG03` for the banked IRQ dispatch.

The handler doubles zero-page `$6A` and reads a 16-bit target from `$9F01,Y` / `$9F02,Y`, stores it in `$00/$01`, then executes `JMP ($0000)`.

## Candidate pointer entries

The bytes beginning at CPU `$9F01` decode into the following plausible handler targets through index `$2F`:

| index | target |
|---:|---:|
| 00 | `E118` |
| 01 | `A078` |
| 02 | `A0A8` |
| 03 | `A0CF` |
| 04 | `A102` |
| 05 | `A10D` |
| 06 | `A120` |
| 07 | `A14B` |
| 08 | `A16F` |
| 09 | `A1D5` |
| 0A | `A1FA` |
| 0B | `A10D` |
| 0C | `A120` |
| 0D | `A18B` |
| 0E | `A1B1` |
| 0F | `A1FA` |
| 10 | `A235` |
| 11 | `A243` |
| 12 | `A249` |
| 13 | `A293` |
| 14 | `A2E2` |
| 15 | `A310` |
| 16 | `A01C` |
| 17 | `9FD5` |
| 18 | `9FE3` |
| 19 | `9FA1` |
| 1A | `A323` |
| 1B | `A340` |
| 1C | `A357` |
| 1D | `A36B` |
| 1E | `A3A8` |
| 1F | `A3ED` |
| 20 | `A405` |
| 21 | `A3A8` |
| 22 | `A420` |
| 23 | `9F99` |
| 24 | `A293` |
| 25 | `A2DD` |
| 26 | `A316` |
| 27 | `A2EA` |
| 28 | `A310` |
| 29 | `A497` |
| 2A | `A4B2` |
| 2B | `A4DF` |
| 2C | `A4EC` |
| 2D | `81CE` |
| 2E | `D007` |
| 2F | `A526` |

The next two bytes interpreted as another pointer would yield `$297A`, which is not a plausible PRG execution address. Do **not** yet convert this observation into a proven `$6A <= $2F` invariant; the producer/domain of `$6A` still needs to be traced.

## Critical code/data overlap at `$9F60`

Entry `$2F` uses:

- low byte at `$9F5F` = `$26`
- high byte at `$9F60` = `$A5`
- target = `$A526`

But `$9F60` is also the first opcode byte of a valid routine:

```asm
9F60  A5 7A     LDA $7A
9F62  29 0F     AND #$0F
9F64  0A        ASL A
9F65  A8        TAY
9F66  B9 8B 9F  LDA $9F8B,Y
9F69  85 00     STA $00
9F6B  B9 8C 9F  LDA $9F8C,Y
9F6E  85 01     STA $01
9F70  A0 00     LDY #$00
9F72  B1 00     LDA ($00),Y
9F74  8D 81 07  STA $0781
9F77  AC 80 07  LDY $0780
9F7A  C8        INY
9F7B  B1 00     LDA ($00),Y
9F7D  C9 FF     CMP #$FF
9F7F  F0 06     BEQ $9F87
9F81  85 3D     STA $3D
9F83  8C 80 07  STY $0780
9F86  60        RTS
9F87  A0 01     LDY #$01
9F89  D0 F0     BNE $9F7B
```

Therefore physical PRG byte `PRG02:+$1F60` must be represented as **both table data and executable code** in any exact reconstruction/accounting system. A simplistic disjoint code-vs-data partition is insufficient for this ROM.

## Additional local facts

`$9F8B+` is itself used as a pointer table by the `$9F60` routine, followed by short byte sequences terminated by `$FF`. `$9F99` begins a separate IRQ-target routine:

```asm
9F99  A9 7F     LDA #$7F
9F9B  8D 02 D0  STA $D002
9F9E  4C 18 E1  JMP $E118
```

`$E118` is the fixed-bank IRQ common restore/acknowledge path.

## Next required proof

1. Trace every write to zero-page `$6A` to establish the actual IRQ-dispatch index domain.
2. Disassemble and reconcile all unique targets in the candidate table.
3. Identify which targets return via `$E118` and which perform intermediate VRC6/PPU work.
4. Preserve the `$9F60` overlapping byte in any source representation and coverage ledger.
