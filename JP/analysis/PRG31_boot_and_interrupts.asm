; Akumajou Densetsu (Japan) — physical PRG31 fixed bank
; Derived from verified ROM SHA-256:
; 958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
;
; CPU mapping: PRG31 is fixed at $E000-$FFFF.
; This is evidence-oriented disassembly, not yet reconstructed source.

; ---------------------------------------------------------------------------
; RESET vector -> $E00B
; ---------------------------------------------------------------------------
RESET_E00B:
E00B  D8        CLD
E00C  78        SEI
E00D  AD 02 20  LDA $2002
E010  10 FB     BPL $E00D
E012  AD 02 20  LDA $2002
E015  10 FB     BPL $E012
E017  A2 FF     LDX #$FF
E019  9A        TXS
E01A  20 6C E1  JSR $E16C
E01D  20 51 E1  JSR $E151
E020  E8        INX
E021  8A        TXA
E022  85 00     STA $00
E024  85 01     STA $01
E026  A0 00     LDY #$00
E028  A2 08     LDX #$08
E02A  91 00     STA ($00),Y
E02C  C8        INY
E02D  D0 FB     BNE $E02A
E02F  E6 01     INC $01
E031  E4 01     CPX $01
E033  D0 F5     BNE $E02A
E035  A9 00     LDA #$00
E037  8D 03 90  STA $9003       ; VRC6 frequency control
E03A  20 11 E2  JSR $E211
E03D  20 5C E1  JSR $E15C
E040  A9 20     LDA #$20
E042  85 21     STA $21
E044  8D 03 B0  STA $B003       ; VRC6 PPU banking/mirroring/WRAM control
E047  20 C4 E2  JSR $E2C4       ; selects $1E at $C000 (physical PRG30)
E04A  58        CLI
E04B  E6 20     INC $20
E04D  18        CLC
E04E  A5 20     LDA $20
E050  65 1B     ADC $1B
E052  85 20     STA $20
E054  4C 4B E0  JMP $E04B

; ---------------------------------------------------------------------------
; NMI vector -> $E057
; ---------------------------------------------------------------------------
NMI_E057:
E057  48        PHA
E058  8A        TXA
E059  48        PHA
E05A  98        TYA
E05B  48        PHA
E05C  AD 02 20  LDA $2002
E05F  A5 41     LDA $41
E061  49 FF     EOR #$FF
E063  8D 00 F0  STA $F000
E066  A5 40     LDA $40
E068  8D 01 F0  STA $F001
E06B  A5 42     LDA $42
E06D  49 FF     EOR #$FF
E06F  8D 00 F0  STA $F000
E072  58        CLI
E073  A5 43     LDA $43
E075  85 6A     STA $6A
E077  A5 21     LDA $21
E079  8D 03 B0  STA $B003
E07C  A4 1C     LDY $1C
E07E  D0 57     BNE $E0D7
E080  E6 1C     INC $1C
E082  A9 00     LDA #$00
E084  8D 03 20  STA $2003
E087  A0 02     LDY #$02
E089  8C 14 40  STY $4014       ; OAM DMA from page $02
E08C  20 6C E1  JSR $E16C
E08F  20 46 ED  JSR $ED46
E092  A5 FE     LDA $FE
E094  A6 1D     LDX $1D
E096  F0 06     BEQ $E09E
E098  C6 1D     DEC $1D
E09A  F0 02     BEQ $E09E
E09C  29 E7     AND #$E7
E09E  8D 01 20  STA $2001
E0A1  20 31 E1  JSR $E131
E0A4  20 D6 E2  JSR $E2D6
E0A7  A5 72     LDA $72
E0A9  10 06     BPL $E0B1
E0AB  4A        LSR A
E0AC  4A        LSR A
E0AD  4A        LSR A
E0AE  4A        LSR A
E0AF  85 72     STA $72
E0B1  A5 53     LDA $53
E0B3  85 6C     STA $6C
E0B5  A5 54     LDA $54
E0B7  85 6D     STA $6D
E0B9  20 38 E2  JSR $E238
E0BC  20 64 E2  JSR $E264
E0BF  20 5C E3  JSR $E35C
E0C2  A9 0D     LDA #$0D
E0C4  20 D0 E2  JSR $E2D0       ; 16 KiB bank select -> bank value $0D
E0C7  20 01 80  JSR $8001       ; physical target depends on bank $0D
E0CA  A9 00     LDA #$00
E0CC  20 72 EC  JSR $EC72
E0CF  85 1C     STA $1C
E0D1  68        PLA
E0D2  A8        TAY
E0D3  68        PLA
E0D4  AA        TAX
E0D5  68        PLA
E0D6  40        RTI

NMI_ALT_E0D7:
E0D7  20 31 E1  JSR $E131
E0DA  20 D6 E2  JSR $E2D6
E0DD  A5 72     LDA $72
E0DF  10 06     BPL $E0E7
E0E1  4A        LSR A
E0E2  4A        LSR A
E0E3  4A        LSR A
E0E4  4A        LSR A
E0E5  85 72     STA $72
E0E7  A5 53     LDA $53
E0E9  85 6C     STA $6C
E0EB  A5 54     LDA $54
E0ED  85 6D     STA $6D
E0EF  20 24 E2  JSR $E224
E0F2  4C D1 E0  JMP $E0D1

; ---------------------------------------------------------------------------
; IRQ/BRK vector -> $E0F5
; ---------------------------------------------------------------------------
IRQ_E0F5:
E0F5  48        PHA
E0F6  8A        TXA
E0F7  48        PHA
E0F8  98        TYA
E0F9  48        PHA
E0FA  A5 00     LDA $00
E0FC  48        PHA
E0FD  A5 01     LDA $01
E0FF  48        PHA
E100  A9 01     LDA #$01
E102  20 D2 E2  JSR $E2D2       ; direct 16 KiB bank select, does not update $23 here
E105  A5 6A     LDA $6A
E107  0A        ASL A
E108  B0 0E     BCS $E118
E10A  A8        TAY
E10B  B9 01 9F  LDA $9F01,Y
E10E  85 00     STA $00
E110  B9 02 9F  LDA $9F02,Y
E113  85 01     STA $01
E115  6C 00 00  JMP ($0000)     ; IRQ dispatch through banked table
E118  A9 00     LDA #$00
E11A  8D 01 F0  STA $F001
E11D  8D 02 F0  STA $F002
E120  A5 23     LDA $23
E122  20 D0 E2  JSR $E2D0       ; restore tracked 16 KiB bank
E125  68        PLA
E126  85 01     STA $01
E128  68        PLA
E129  85 00     STA $00
E12B  68        PLA
E12C  A8        TAY
E12D  68        PLA
E12E  AA        TAX
E12F  68        PLA
E130  40        RTI

; ---------------------------------------------------------------------------
; VRC6 PRG-bank helpers
; ---------------------------------------------------------------------------
sub_E2C0_select_prg8_07:
E2C0  A9 07     LDA #$07
E2C2  D0 02     BNE $E2C6

sub_E2C4_select_prg8_1E:
E2C4  A9 1E     LDA #$1E
E2C6  8D 00 C0  STA $C000       ; VRC6 8 KiB PRG select
E2C9  60        RTS

sub_E2CA_save_then_select_prg16:
E2CA  48        PHA
E2CB  A5 23     LDA $23
E2CD  85 24     STA $24
E2CF  68        PLA

sub_E2D0_track_and_select_prg16:
E2D0  85 23     STA $23

sub_E2D2_select_prg16_raw:
E2D2  8D 00 80  STA $8000       ; VRC6 16 KiB PRG select
E2D5  60        RTS

; NOTE: Address-stable labels above describe only behavior directly visible in bytes.
; Further semantic naming is deferred until callers and RAM roles are proven.
