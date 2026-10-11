; Original Akumajou Densetsu JP, VRC6 raw 16 KiB bank $0B.
; Maps PRG +$2C000 into CPU $8000-$BFFF via bank select $0B.
; Sources $8161-$8192 and $826C-$8281, 72 original bytes.
.org $8161
ActorApplyAttributes:
    lda $0470,x
    and #$01
    bne ActorSetFlag80
    lda $0470,x
    and #$08
    beq $81A9
ActorSetFlag80:
    lda $0470,x
    ora #$80
    sta $0470,x
    cpx #$0D
    bcs $81B1
    and #$01
    beq $81B1
    lda $054E,x
    bmi $8193
    jsr $81CC
    bcc $81B1
    lda $0470,x
    and #$04
    beq $8193
    jsr $8253
; $8193 falls into already reassembled actor_tail_0525.asm.
.org $826C
ActorCheckBounds:
    lda $054E,x
    cmp #$30
    bcc ActorBoundsDone
    cmp #$66
    bcs ActorBoundsDone
    lda $041C,x
    cmp #$F8
    bcc ActorBoundsDone
    jmp $8193
ActorBoundsDone:
    rts
