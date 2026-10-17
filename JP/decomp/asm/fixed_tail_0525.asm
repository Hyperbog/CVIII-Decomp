; Original JP fixed bank31, CPU $E000-$FFFF.
; Source 6502 instructions with original absolute and banked targets.
.org $E2D0
SetPrgBank16:
    sta $23
    sta $8000
    rts

.org $FE63
AfterActorAnimation:
    lda #$0B
    jsr SetPrgBank16
    jsr $8161
    jsr $826C
    inx
    cpx #$13
    bcs AfterActorLoop
    jmp $FDEC
AfterActorLoop:
