# 06 — Room State, Bank-Switched Resource Reads and World/Stage Model

**Status:** EARLY PARTIAL. First verified mapper-dispatch entry, conditional room-loader graph; **full stage/world gameplay is not reconstructed**. Evidence: [0506](../analysis/CROSSBANK_AI_ATLAS_0506.md), [0507](../analysis/NMI_BANK0A_ROOM_DISPATCH_0507.md).

## Bank-state entry: proven, selector liveness: unproven

The fixed NMI first-level inline table includes selector entry $0D → fixed $E526. The ROM executes:

```asm
E526  LDA #$0A
E528  JSR $E2D0
E52B  JMP $B4CC
```

This establishes raw bank **$0A** for CPU $8000-$BFFF on that branch. In checkpoint 0507, **physical PRG21:$B4CC-$B4D0** (5 bytes `LDA $19; JSR $E7FB`) is newly admitted verified code. This mapper-context proof does **not** show the global live $18 value $0D or bound all $19 values.

## Encoded room-state table and conditional graph

Twelve encoded words $B4D1-$B4E8 contain target addresses:

```text
00 B570  01 B58C  02 B597  03 B5A3
04 B5CC  05 B5DA  06 B614  07 B622
08 B64E  09 B5CC  0A B5DA  0B B662
```

Official-opcode traversal of the candidate handler roots yields 281 instruction starts and 582 candidate consumed code/operand bytes across noncontiguous intervals. **Only the five bytes $B4CC-$B4D0 are new strict verified coverage in 0507**. A pointer table's 12 entries are not evidence of the live $19 producer domain.

Conditional state index 1 → $B58C calls $B4E9 (sets $68=$00) and increments $19; index 2 → $B597 calls $B689 (nested $68 tail dispatch). Index 0 in that nested table points to $B6A4, but its carry gate must pass to invoke $B7F7. Cross-frame $19/$68 mutations and mapper restoration through helpers remain open.

## Candidate room loader and temporary source bank

When selected under raw bank $0A, $B7F7–$B872 has eleven `JSR $FB96` instructions. Fixed PRG31:$FB96 temporarily maps raw bank **$0E** with $E2D0, reads `LDA ($08),Y`, stores original A on the 6502 stack, restores raw bank **$0A**, and returns that read value. The bus-aware [native partial lift](../src/temporary_prg_bank_read.hpp) tests 65,537 read/index combinations and restoration order, **not the loader's full liveness**.

The candidate loader populates room/object data and includes `AND #$0F; STA $54`: **$54=0..15 on this specific branch**, not globally. The source pointer system at $B8C2/$07A0, room record ownership, stage IDs, scrolling and progression remain unproved. Do not invent a room format from nearby bytes alone.

## Not yet characterized

The chapter will eventually cover stage/room graph, camera bounds, level tilemaps/collision, stage transitions/branching, characters and alternate routes, doors, bosses, title/menu/password/game over/endgame persistence. Today those are **research targets**, not claimed established behavior. Preserve unknown stage data and ROM physical location in the atlas rather than labeling it executable from visual similarity.

Next: close $18/$19/$68 live sources, B6A4 carry branch, $07A0-indexed pointer extents, and confirm the room/source-to-consumer bytes before native world implementation.
