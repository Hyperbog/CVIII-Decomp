; Original Akumajou Densetsu JP, VRC6 physical PRG bank 31.
; Bank-qualified 6502 code for $FDE4-$FE62 (127 original bytes).
; Calls to raw $8000-$BFFF depend on the preceding VRC6 mapper state.
; These are source instructions, not emulated runtime coverage claims.
.org $FDE4
ActorSchedulerStart:
    inc $A0
    lda #$FF
    sta $8F
    ldx #$01
ActorSchedulerNext:
    lda $054E,x
    beq ActorSchedulerIncrement
    stx $69
    lda #$0B
    jsr $E2D0
    jsr $80E3
    jsr $B1F8
ActorPostCollision:
    ldx $69
    lda $054E,x
    beq ActorSchedulerIncrement
    cmp #$30
    bcs ActorType30Plus
    lda #$09
    jsr $E2D0
    jsr $8001
    ldx $69
    jmp AfterTypeMotion
ActorType30Plus:
    lda $0470,x
    and #$02
    beq ActorNoForcedUpdate
    jsr $FE8C
    jmp $FE63
ActorNoForcedUpdate:
    lda $054E,x
    bmi ActorRunFollowup
    cmp #$69
    bcs ActorAfterFollowup
    jsr $FF56
    bcs $FE63
ActorRunFollowup:
    jsr $BD11
AfterTypeMotion:
    ldx $69
ActorAfterFollowup:
    lda $054E,x
    cmp #$58
    bcs ActorCheckFlag40
    cmp #$30
    bcc ActorCheckFlag40
    lda $A8
    bne $FE63
ActorCheckFlag40:
    lda $0470,x
    and #$40
    beq ActorCheckAlive
    lda #$0B
    jsr $E2D0
    jsr $8001
ActorCheckAlive:
    lda $054E,x
    beq ActorSchedulerIncrement
    lda $0470,x
    and #$20
    bne $FE63
    jsr $EF93
; The next instruction at $FE63 is in fixed_tail_0525.asm.
; The branch destination $FE6E is already reassembled in 0525.
.org $FE6E
ActorSchedulerIncrement:
; External label lives in the 0525 source. No duplicated byte emitted.
.org $FE76
ActorSchedulerExit:
    lda #$0A
    jsr $E2D0
    jsr $84EA
    lda $89
    bmi ActorSchedulerReturn
    dec $89
    bpl ActorSchedulerReturn
    lda #$00
    sta $0417
ActorSchedulerReturn:
    rts

.org $FE8C
ActorDispatchDescriptor:
    lda $0565,x
    lsr a
    lsr a
    lsr a
    lsr a
    lsr a
    lsr a
    jsr $E7FB
; E7FB consumes inline return-address-relative pointer words (three entries).
.org $FE98
ActorDescriptorPointers:
    .word ActorDescriptor0,ActorDescriptor1,ActorDescriptor2

.org $FE9E
ActorDescriptor0:
    lda #$80
    sta $05D8,x
    lda #$04
    sta $0454,x
    lda $0565,x
    ora #$40
    sta $0565,x
    rts

.org $FEB1
ActorDescriptor1:
    dec $05D8,x
    bne ActorDescriptorExit
    lda #$08
    sta $05D8,x
    lda $0565,x
    and #$BF
    ora #$80
    sta $0565,x
ActorDescriptorExit:
    rts

.org $FEC6
ActorDescriptor2:
    lda $1B
    and #$03
    bne ActorDescriptorExit
    lda $0454,x
    eor #$04
    sta $0454,x
    dec $05D8,x
    bne ActorDescriptorExit
    lda $0470,x
    and #$FD
    sta $0470,x
    lda $0454,x
    and #$FB
    sta $0454,x
    rts
