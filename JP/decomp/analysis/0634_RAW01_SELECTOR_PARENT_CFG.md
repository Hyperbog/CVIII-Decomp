# JP0634 — Original raw01 B87A-to-BB57 parent route and table bounds

**Status:** source-ROM-authenticated, no-interrupt conditional route only.

The original physical VRC6 raw01 source has an in-bank route:

- B87A: JSR B8F8; B87D: STA $078A; B880: JSR B919; B883: JMP BAEF.
- B919 helper directly clamps unsigned RAM $30 to at most $11 using
  LDA $30; CMP #$11; BCC +2; LDA #$11; STA $30.
- B94E calls B955, whose original physical code was audited separately.
- BAEF–BB61 is a contiguous opcode-decoded original tail containing
  BB57: LDA $30; LSR A; TAY; LDA $BB62,Y; STA $07A0; RTS.

Four complete original code windows (B87A–B885, B919–B954,
B955–B980, BAEF–BB61) and the nine-cell table are pinned by SHA-256
in the JP0634 script. 256 incoming byte values are stepped through
the authentic B91E–B927 clamp instructions. The range at BB57 on
this particular no-interrupt B87A→B919→BAEF route is $30=$00..$11
and thus table indexes 0..8. This is a conditional source-bound
finding; it does **not** prove this route was ever executed in a real
playthrough, that alternate entry points are absent, or that no NMI
or IRQ writes RAM $30 between the clamp and BB57.

Nor does it prove that raw01 STA $07A0 is a predecessor to the
independent raw0A B7F7 room-loader. R-002 remains OPEN.

Run the committed ROM-free smoke, then the private original-ROM audit:

    python3 JP/decomp/tools/audit_room_selector_parent_0634.py --smoke
    python3 JP/decomp/tools/audit_room_selector_parent_0634.py --rom /private/Akumajou-Densetsu-JP.nes

Strict PRG unchanged: 49,504/262,144 (18.8843%). VPP27/100,
certified checkpoint 0508, fixed frontier FB96.
