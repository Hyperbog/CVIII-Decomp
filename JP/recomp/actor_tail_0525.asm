; Original JP VRC6 raw bank $0B, CPU $8000-$BFFF.
; Semantic 6502 mnemonics reassemble exactly to the source ROM.
.org $8193
ResetActorUnlessLinked:
    lda $054E,x
    cmp #$4D
    beq ResetLinkedActor
    lda #$00
    sta $054E,x
    sta $0470,x
    sta $0400,x
    sta $05EF,x
    rts

.org $81B2
ResetLinkedActor:
    lda $061D,x
    tax
    lda $0470,x
    and #$81
    beq ResetOwner
    jsr ClearActorFields
    sta $054E,x
ResetOwner:
    ldx $69
    jsr ClearActorFields
    sta $054E,x
    rts

.org $B56B
ClearActorFields:
    lda #$00
    sta $0657,x
    sta $0470,x
    sta $05C1,x
    sta $0400,x
    rts
