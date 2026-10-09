# 02 — CPU Boot, NMI, IRQ and Inline Control Dispatch

**Status:** PARTIAL. A/B-level ROM code; F covers only mapper/IRQ unit tests. Core evidence: [fixed first-level dispatcher](../analysis/NMI_FIXED_E7FB_DISPATCH.md), [scheduler](../analysis/NMI_FIXED_SCHEDULER_BANKED_0501.md), [IRQ states](../analysis/PRG02_IRQ_dispatch.md), [native IRQ](../analysis/NATIVE_VRC6_IRQ.md).

## Interrupt roots

PRG31 vectors: RESET $E00B, NMI $E057, IRQ/BRK $E0F5. NMI handles PPU DMA and banked helpers; IRQ uses the fixed handler and banked 45-state table in PRG02. These are ROM-specific facts, not a generic NES initialization recipe. [Fixed NMI audit](../analysis/NMI_FIXED_ZP10_PRESERVATION.md) tracks a part of the pre-render graph.

At fixed $E118 the program clears mapper control register $F001 **before** acknowledging via $F002 at $E11D. The native VRC6 IRQ scheduler models latch at $F000, control at $F001, ack at $F002, 8-bit counter and the **114,114,113 CPU-cycle** repeating scanline-mode prescaler cadence; exact CPU interrupt latency, PPU/frame trace parity and complete active IRQ transitions remain broader runtime tasks.

## $E7FB is not an ordinary returning JSR

The 25-byte inline tail-dispatch routine at fixed $E7FB:

1. `ASL A` doubles the selector in **8 bits**; `STY $03` preserves the caller's Y.
2. `PLA/STA $00; PLA/STA $01` pops the original JSR return address.
3. `LDA ($00),Y; ...` reads two bytes at return-address + 1 + 2*A and +2 + 2*A, then restores Y.
4. `STA $03; JMP ($0002)` tail jumps to the selected pointer, **without returning to the inline data**.

The call therefore consumes a caller-owned little-endian word table immediately after `JSR $E7FB`. A linear disassembler that treats those bytes as fallthrough instructions is wrong. The routine writes scratch $00–$03, **not $10**. Final CPU Z/N from its last `LDY $03` reflect restored Y, not target high byte (see [0507 partial ABI test](../analysis/NMI_BANK0A_ROOM_DISPATCH_0507.md)).

## First-level NMI $18 and nested state $2C/$68

Fixed $E35E loads selector $18, $E360 calls E7FB; the 16 encoded first-level pointer pairs include index $0D → **$E526**, where code selects raw bank $0A then jumps $B4CC. The table's 16 words alone **do not prove live $18=0..15**. Fixed $F39A contains another E7FB dispatch over encoded $2C state pointers; producer bounds remain open. [Nested dispatch analysis](../analysis/NMI_FIXED_2C_PREFIX.md), [$68 secondary](../analysis/NMI_FIXED_68_DISPATCH.md).

## Bank-switch entry and scheduling

[0507](../analysis/NMI_BANK0A_ROOM_DISPATCH_0507.md) newly verifies *only* raw-$0A:$B4CC-$B4D0 as mapper-resolved executable instruction bytes via fixed $E526. The 12 subsequent state words and a 281-start graph are structural until $19 liveness is proved.

The fixed $FDE4 object scheduler selects raw $0B, invokes $80E3/$B1F8 and visits ordinary object slots X=$01..$12. The per-slot banked calls and their actual $10 writers need cross-call provenance; see [04](04_OBJECT_SCHEDULER_COLLISION_SCRATCH.md).

## Recompilation rules

Correctly implement interrupt priority, 6502 8-bit/16-bit wrap, JSR stack semantics and tail dispatch side effects. NES 2A03 is 6502-like **without decimal arithmetic**; CPU flags, memory mirroring and PPU/mapper IRQ timing should be checked against hardware docs but validated in the game with trace tests. **No complete CPU/NMI/IRQ frame-trace parity is currently certified.**

## Provisional 0508 IRQ preservation result (R-001 / R-002)

The [Phase 6 JP-ROM static audit](../analysis/0508_PHASE6_FINDINGS.md) re-traverses all 38 unique 04F2 IRQ handler entrypoints (45 encoded states), covering 558 handler instruction starts, the $9F5B helper including its $9F87 cursor-wrap branch, and fixed IRQ helper bodies. It proves the admitted IRQ graph leaves ZP $08/$09/$10/$18/$19/$23/$54/$68 and RAM $07A0/$07A6 untouched. The two indexed writes at $A328 and $A4A5 have locally bounded X=0..2 and X=0..7, excluding $07A0. The IRQ maps bank $01 through E2D2 without changing $23 and restores the tracked bank using E2D0 before RTI. This supports temporary bank-$0E source reads inside fixed $FB96 against ordinary IRQ interleaving, but does not prove NMI re-entry, reset-to-room reachability, cycle timing, or complete frame parity. No newly verified PRG bytes or VPP points are credited.


## Provisional 0508 Phase 7 — two-entry inline-dispatch witness

A ROM-backed 6502 instruction executor tests conditional `$18=$0C, $19=$13` through fixed `$E51E`, raw `$0A:$AFA4`, the exact `$E7FB` stack-consuming ABI and `$B36B`. The last routine assigns `$18=$0D` and `$19=0`. Under the explicit *no intervening selector writer* condition, a later fixed `$E526` dispatch reaches raw `$0A:$B4CC` and selects handler `$B570`. All 65,536 `$0789 × saved-Y` tests pass with byte/stack/mapper/flag assertions. This is **not** proof the initial predecessor state is reachable after RESET or a native NMI/IRQ timing trace; retain R-001 OPEN. [0508 Phase 7](../analysis/0508_PHASE7_FINDINGS.md).
