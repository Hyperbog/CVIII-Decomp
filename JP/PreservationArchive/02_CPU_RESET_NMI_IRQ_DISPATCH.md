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

## Provisional 0508 Phase 8 — state-zero clear and preserved room field

The [ROM-locked bounded execution audit](../analysis/0508_PHASE8_FINDINGS.md) follows raw bank `$0A:$B570` through fixed `$E2C4`, `$E616`, and `$E7B6` to the **entry** of `$EB82`. It executes 768 synthetic-entry cases, not complete NMI frames. `$E7B6` clears 1,297 distinct RAM destinations; caller `$B57B-$B583` saves/restores `$0781`. The tested entry consequently clears `$07A0/$07A6/$0789/$68`, retains `$0781`, and preserves `$18=$0D/$19=0`. State-zero entry and post-`$EB82` effects remain conditional/unclosed. No semantic PRG or VPP increment.

## Provisional 0508 Phase 9 — fixed PPU stream returns to state one

The [Phase 9 ROM-locked audit](../analysis/0508_PHASE9_FINDINGS.md) extends the *conditional* raw `$0A:$B570` state-zero prefix through fixed `$EB82` (and `$E16C/$E827/$ED89`), then executes raw `$0A:$B589 INC $19; RTS`. Its 512 bounded cases preserve `$0781`, leave `$07A0/$07A6/$68=0` and advance `$19=0→1`. The fixed `$EC1D-$EC46` data stream issues 2,048 zero-valued `$2007` writes. This is **not a full NMI trace**: PPUSTATUS is held at zero; reset-to-selector liveness, interrupt timing, other writers, and native PPU parity remain unresolved. The stream is previously counted fixed PRG data; no new strict coverage or VPP.

## Provisional 0508 Phase 10 — banked state-one audio call

[Phase 10](../analysis/0508_PHASE10_FINDINGS.md) executes conditional raw bank $0A:$B58C through fixed PRG31 $E249 into raw bank $0C:$8850 and its $87AE sound reset. Fixed $E249 saves $0A in ZP $25 and selects $0C via tracked $23/$8000. The test stops at $8860 after the reset. A separate explicitly *injected hypothetical return* tests the fixed $E249 bank-restoring suffix. No entire music parser, continuous NMI path, or strict PRG byte promotion is claimed.


## Provisional 0508 Phase 11 — state-one sound call returns naturally

[ROM-executed local proof](../analysis/0508_PHASE11_FINDINGS.md) resumes conditional raw-$0A:$B58C with $19=1 and executes the full $E249→raw-$0C:$8850 command $6B metadata installation through its **actual** RTS, including six $E19F raw-$05 reads and matching bank restores. It returns with $23=$0A, $19=2 and $68=0 in 256 cases; no synthetic sound-parser return is needed. The initial $18/$19 seed, contiguous frame reachability and NMI/IRQ interleaving are not certified. Strict PRG accounting remains unchanged.


## 0508 bulk trace infrastructure and reset seeding

The [32-KiB source/producer sweep](../analysis/0508_BULK_0A0E_FINDINGS.md) executes fixed RESET `$E020–E034`'s indirect RAM clear across 32 incoming RAM seeds (6,174 original instructions/case), proving `$18=$19=$68=$07A0=$07A6=0` immediately after that loop while `$00/$01` end as a working pointer `$0800`. This is a bounded initial state, **not** a reset-to-NMI frame witness or proof of later `$18=$0C` liveness. The new [reusable partial 2A03/VRC6 stepper](../analysis/0508_TRACE_CORE_AND_E7FB_CORRECTION.md) replays two independent ROM path regressions and detects E7FB's native index-wrap reconstruction error. No CPU-cycle timing or reference-emulator parity certificate exists.


## 0508 bulk first-NMI synthetic execution witness

The [generic ROM-fetched RESET→NMI experiment](../analysis/0508_RESET_NMI_SYNTHETIC_TRACE.md) runs the original RESET from fixed `$E00B` to `$E04B` under two fixed VBlank-ready `$2002` reads, then manually injects 150 NMIs for each of three idle-instruction budgets (0/12/384). Its **450 synthetic NMIs/1,599,939 executed original instruction steps** demonstrate conditional first-NMI `$18=0,$19:0→1` and subsequent no-input `$18=0,$19=1`. No controller interface, frame timing, PPU pipeline, or IRQ scheduling is implemented; this is **not** reference hardware/gameplay liveness or full CPU trace parity. R-001 and R-006 remain OPEN; no PRG/VPP increase.


## 0508 bulk dynamic CPU writer coverage (synthetic evidence only)

The [mapped multi-bank original-ROM instruction audit](../analysis/0508_BULK_DYNAMIC_PRODUCER_TRACE.md) records all fetched opcode/operand physical bytes and exact RAM write PCs, including fixed `$E551: INC $18` and fixed `$E558: STA $18` plus a raw-bank-$01 write at `$A627`. Across three artificial controller schedules it executes 4,669,348 instructions / 1,800 manual NMIs. A subsequent fork of artificial NMI392 (`$18=$04`) tests 19 separate controller policies for 120 injections each and executes 7,132,248 more original instructions; every branch remains `$18=$04` under these simplified PPU and no-IRQ conditions. Fixed `$F6AE` checks `$1F|$2E|$1D|$A8` before its Start `$F8 & $10` predicate. **Neither original gameplay liveness nor permanent inaccessibility of `$0C/$0D` is implied**. R-001/R-006 remain OPEN; no VPP or strict byte change.


## 0508 experimental vblank-generated NMI execution — no reference parity

[Original-ROM modeled CPU-cycle/vblank trials](../analysis/0508_EXPERIMENTAL_VBLANK_CYCLE_TRACE.md) run 960 synthetic PPU frames and 948 NMI entries across three controller policies, **8,864,752 ROM instruction executions**, from an NTSC-shaped PPU vblank edge scheduler instead of manual NMI injections. The first-level `$18` chain reaches `00→02→0A→09→03→04`, but does not establish `$0C/$0D`. A 151-official-opcode timing-class self-test and 27 representative cases pass. **PPU/IRQ/input are not hardware-accurate; no authentic playthrough, CPU trace parity, R-001/R-006 closure, PRG or VPP score change** follows.
