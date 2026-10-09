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

## Provisional 0508 local room evidence (NOT live certification)

The committed [0508 Phase 5 findings](../analysis/0508_PHASE5_FINDINGS.md) exercise B7F7 under explicitly assumed room indices $07A0=00..04 and map five complete bank-$0E data streams at $BE8B-$BF39 (175 physical bytes, 30 five-byte object records) through actual FB96 stack/mapper transactions. These are **conditional parser input bytes**, not additional semantic PRG coverage. Phase 4 shows a separate raw-bank-$01:$BB57 routine *can* write $07A0 values larger than $04, so the pointer-table width is not a proven global bound.

The [Phase 6 IRQ audit](../analysis/0508_PHASE6_FINDINGS.md) closes a different bounded question: the verified IRQ handler graph preserves the loader pointer $08/$09, room indices $07A0/$07A6 and state selectors $18/$19/$68. This does **not** establish that the five-input loader executes from reset, or exclude NMI re-entry and other ordinary-frame writers. Research tasks R-001/R-002 remain OPEN; fixed PRG31 $FB96 remains an unclaimed semantic frontier.


## Provisional 0508 — bounded original room-state transitions

The [Phase 5 mapped-bus loader audit](../analysis/0508_PHASE5_FINDINGS.md) parses five conditional raw-bank-$0E room streams (175 bytes, 30 object records) through fixed `$FB96`, restoring bank `$0A` after each read. Phase 6's [IRQ preservation](../analysis/0508_PHASE6_FINDINGS.md) rules out overwrites to its pointer/selector inputs within the verified IRQ handler graph, but does not prove frame liveness.

[Phase 7](../analysis/0508_PHASE7_FINDINGS.md) runs the exact first-level inline-tail dispatch twice under **conditional** seed `$18=$0C, $19=$13`: raw-`$0A:$B36B` updates `$18=$0D, $19=0`; if no other writer intervenes, the next NMI entry dispatches to raw-`$0A:$B570`. 65,536 saved-Y/field combinations pass. Because the initial pair's live producer and the subsequent handler execution are not proved, this remains a local two-entry witness, **not a verified stage progression or semantic-byte coverage addition**. R-001 and R-002 remain OPEN.

## Provisional 0508 Phase 8 — room-index initialization rather than global clamp

[Phase 8's original-instruction audit](../analysis/0508_PHASE8_FINDINGS.md) proves the **conditional state-zero prefix** at raw `$0A:$B570` invokes fixed `$E7B6`, clearing `$07A0`, `$07A6`, `$0789` and `$68` to zero while preserving `$0781` by `PHA/PLA`. It halts at fixed `$EB82` before that callee executes. This is a concrete room-index **initialization point**, not a global `$07A0=0..4` producer bound or proof of live reset-to-frame execution. Later writer ordering, bank-$01 `$BB57`, and `$B7DE` progression still require correlation. Tests: 768 partial CPU executions; zero new strict bytes.

## 0508 Phase 9 — conditional state zero completes and advances to state one

[Phase 9](../analysis/0508_PHASE9_FINDINGS.md) now executes the `$EB82` PPU initialization that [Phase 8](../analysis/0508_PHASE8_FINDINGS.md) left open, including the first data pointer `$EBF7→$EC1D`, the 42-byte two-block PPU-clear stream, helper `$E827` source-pointer advancement, and fixed `$ED89` return. Raw bank `$0A:$B589` then increments `$19` from zero to **one** and RTS returns to the synthetic caller. Local `$07A0/$07A6/$68` remain zero and `$0781` is restored; 512 ROM-backed instruction tests pass with two PPU address-increment settings. The following state-one routine `$B58C`, any external helper, live start-state provenance and later room-index producers remain UNKNOWN; no global `$07A0=0..4` bound, no completed stage behavior, no strict byte increase.

## Provisional 0508 Phase 10 — state-one sound reset and conditional state two

[Phase 10](../analysis/0508_PHASE10_FINDINGS.md) runs the actual raw $0A:$B58C state-one prefix through fixed $E249 and raw $0C:$8850. Sound command $6B selects the $87AE reset path; 256 initial-X cases execute through reset and stop at $8860. **Only if the remaining unexecuted sound interpreter returns without corrupting saved $25** does fixed E249 restore $0A, B4E9 clear $68, and B594 advance $19 from 1 to 2. That suffix is tested with an injected synthetic return, not full original audio execution. R-001/R-002 stay OPEN; no strict PRG byte increase.


## Provisional 0508 Phase 11 — state one reaches state two after a real sound return

[Phase 11's ROM-fetched execution audit](../analysis/0508_PHASE11_FINDINGS.md) extends Phase 10 beyond raw-$0C:$8860, completes the command-$6B metadata installer and all six fixed-$E19F temporary raw-$05 reads, and observes a **real RTS** from $8850. Fixed $E249 restores bank $0A before raw-$0A:$B591 resets $68 and $B594 increments room $19=1→2. The conditional start at $B58C is not yet established from reset; the state-two $B597/B689→B6A4 carry gate and global $07A0 source domain remain OPEN. This is zero new strict byte coverage.
