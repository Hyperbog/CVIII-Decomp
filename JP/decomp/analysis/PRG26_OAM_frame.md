# PRG26 `$8001` — NMI-called OAM shadow construction path

## Proven call context

`PRG31:$E0C2` loads bank value `$0D`, calls the tracked VRC6 16 KiB bank selector, then executes `JSR $8001`.

VRC6 bank `$0D` maps physical PRG offsets `$34000-$37FFF`, so CPU `$8001` is physical `PRG26:+$0001`.

The same NMI path performs OAM DMA with `$4014 = $02`, proving CPU page `$0200-$02FF` is the shadow OAM page consumed by the PPU.

## Entry routine

```asm
8001  A9 00     LDA #$00
8003  85 05     STA $05
8005  A9 40     LDA #$40
8007  85 07     STA $07
8009  A5 22     LDA $22
800B  18        CLC
800C  69 44     ADC #$44
800E  85 22     STA $22
8010  85 04     STA $04
8012  A6 05     LDX $05
8014  E0 1C     CPX #$1C
8016  B0 20     BCS $8038
8018  BD 00 04  LDA $0400,X
801B  F0 17     BEQ $8034
801D  BD 70 04  LDA $0470,X
8020  30 12     BMI $8034
8022  BD 54 04  LDA $0454,X
8025  85 00     STA $00
8027  BD 1C 04  LDA $041C,X
802A  85 01     STA $01
802C  BD 38 04  LDA $0438,X
802F  85 02     STA $02
8031  20 70 80  JSR $8070
8034  E6 05     INC $05
8036  D0 DA     BNE $8012
8038  A6 04     LDX $04
803A  A4 07     LDY $07
803C  A9 F4     LDA #$F4
803E  9D 00 02  STA $0200,X
8041  8A        TXA
8042  18        CLC
8043  69 C4     ADC #$C4
8045  AA        TAX
8046  88        DEY
8047  D0 F3     BNE $803C
8049  60        RTS
```

## Directly established behavior

- `$05` iterates object indices `0..$1B` (28 entries).
- `$0400,X == 0` suppresses the object.
- A negative value in `$0470,X` also suppresses it.
- Three per-object bytes are copied to ZP `$00/$01/$02` before calling `$8070`.
- `$8070` writes 4-byte sprite/OAM records into `$0200+X`.
- `$07` begins at `$40` (64 sprite slots) and is decremented by `$8070` as records are emitted.
- After processing the 28 object records, `$8001` writes `$F4` into the Y-coordinate byte of every remaining OAM slot using the same rotating X sequence. This hides unused sprites before the subsequent page-2 OAM DMA.
- `$22` is advanced by `$44` modulo 256 each invocation and seeds the OAM destination offset through `$04`. This is consistent with deliberate sprite-order rotation; the precise gameplay reason/name is not yet promoted to a semantic invariant.

## `$8070` local renderer

`$8070` reads `$048C,X` and uses it to index a little-endian pointer table beginning at `$817F`:

```asm
8070  BC 8C 04  LDY $048C,X
8073  84 0F     STY $0F
8075  B9 7F 81  LDA $817F,Y
8078  85 08     STA $08
807A  B9 80 81  LDA $8180,Y
807D  85 09     STA $09
807F  BC 00 04  LDY $0400,X
8082  B1 08     LDA ($08),Y
8084  85 0A     STA $0A
8086  C8        INY
8087  B1 08     LDA ($08),Y
8089  85 0B     STA $0B
808B  A0 00     LDY #$00
808D  B1 0A     LDA ($0A),Y
808F  85 03     STA $03
```

This establishes two levels of pointer lookup before consuming a variable-length sprite description. The rest of `$8070..$817E` writes OAM Y/tile/attribute/X fields and handles an alternate horizontally transformed path; `$8119` XORs the attribute value with `$40`, which is the NES OAM horizontal-flip bit.

`$8172..$817E` conditionally fetches a byte and adds `$80`, returning carry set when `$0F >= $16`. Exact meaning of this special path remains unresolved.

## Data boundary

`$817F` is not sequential executable code for this path. It is read as table data by `$8075/$807A`. Its first bytes form plausible little-endian pointers:

```text
$817F: 9D 81 -> $819D
$8181: 0D 82 -> $820D
$8183: 65 82 -> $8265
$8185: AF 82 -> $82AF
$8187: B0 8A -> $8AB0
$8189: 45 95 -> $9545
$818B: A6 AA -> $AAA6
$818D: EA AB -> $ABEA
$818F: 6D 9E -> $9E6D
$8191: B0 8B -> $8BB0
$8193: A6 AB -> $ABA6
...
```

Do not linearly disassemble `$817F+` as code without following a proven control-flow entry.

## Next proof work

1. Determine valid values/stride of `$048C,X` and full extent of the `$817F` pointer table.
2. Reconcile sprite-description format consumed by `$8070..$817E` field by field.
3. Trace `$0400/$041C/$0438/$0454/$0470/$048C/$04A8` producers to identify the 28-entry object record structure.
4. Only after that, promote provisional names and produce the first native equivalent routine with byte/flag behavior tests.
