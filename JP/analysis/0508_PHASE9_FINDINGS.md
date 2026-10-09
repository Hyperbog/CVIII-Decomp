# CVIII JP — Checkpoint 0508 Phase 9: bounded `$EB82` PPU-clear return into room state 1

**Status:** PROVISIONAL ROM-backed local 6502/PPU-register execution. **Not** a reset-to-NMI witness, original-emulator trace, complete 0508 checkpoint, or semantic PRG-byte promotion. The source ROM is Japan iNES (393,232 bytes), SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`, mapper 24 VRC6a.

## Exact conditional handoff

[Phase 7](0508_PHASE7_FINDINGS.md) proves the local `$18=$0C,$19=$13` predecessor dispatch can select state `$18=$0D,$19=$00` and next enter raw VRC6 bank `$0A:$B570` **if** the original selectors attain those values and no intervening writer changes them. [Phase 8](0508_PHASE8_FINDINGS.md) executes `$B570` through `$B586: JSR $EB82`, proving fixed `$E7B6` zeroes `$07A0/$07A6/$68` and that `$0781` is restored. Phase 9 resumes the *same conditional local machine* and executes the entire fixed `$EB82` callee through its return to `$B589: INC $19; RTS`.

| JP physical/mapped location | Original instruction or data | Consequence |
|---|---|---|
| Fixed PRG31 `$EB82-$EB8D` | X=0; load pointer bytes from `$EBF7,X/$EBF8,X` | Pointer `$00/$01 = $EC1D` |
| Fixed PRG31 `$EB8E-$EBAB` | Calls `$E16C`, sets `$FC/$FD=0`, configures `$2006`, advances the data pointer with `$E827` | Sets initial PPU target `$2000`, data pointer `$EC1F` |
| Fixed PRG31 `$EC1D-$EC46` | **42 ROM-data bytes**, including two little-endian PPU addresses, pairs of `$78,$00`, two `$40,$00` counts, `$7F` address switch, terminal `$FF` | 1,024 zero-valued `$2007` writes for each of two nominal blocks, **2,048 port writes total** |
| Fixed PRG31 `$EBEC-$EBF3` | `$7F` re-reads next PPU target address `$2400` | Starts second block at `$2400` |
| Fixed PRG31 `$EBF4-$EBF6` | `$FF` dispatches to `$ED89` | `$ED89: LDA $FF; STA $2000; RTS` returns to `$B589` |
| Raw VRC6 bank `$0A` / physical PRG21 `$B589-$B58B` | `INC $19; RTS` | End state `$19=$01`, `$07A0=$00`, `$07A6=$00`, `$68=$00` |

**Address distinction:** With PPUCTRL bit 2 clear, 1-byte VRAM increment, the write addresses run `$2000-$23FF` and `$2400-$27FF`, totaling 2,048 distinct addresses. With bit 2 set, the PPU increment is 32 bytes; 2,048 **port writes** still occur, but the VRAM addresses repeat/alias. The audit explicitly tests both settings and does **not** falsely infer 2,048 distinct VRAM cells for the second case. PPUSTATUS `$2002` is modeled as fixed zero on the tested path; PPU cycles, rendering side effects and hardware-reference parity are not simulated.

## Independent original-stream/CPU assertions

`JP/tools/audit_0508_phase9.py` imports the prior ROM-fingerprinted Phase 8 CPU, adds only the needed original 6502 opcodes (`LDA abs,X`, `LDA (zp),Y`, `ADC`, `CPY`, `INC zp`, branches etc.), models writes to `$2000/$2001/$2006/$2007`, and independently parses the 42-byte ROM data stream into an expected output sequence. Original low/high PPU address words are little-endian in the stream; the ROM code sends their high byte then low byte to `$2006`. A mismatch in either direction fails the audit.

For **256 different RAM seeds × 2 PPUCTRL increment settings = 512 cases**, each executes **10,532 actual JP instructions** from raw `$0A:$B570` through fixed `$E7B6`, `$EB82`, `$E16C`, `$E827`, `$ED89`, and back to the synthetic parent RTS destination `$9000`. Every case checks: ROM identity and exact helper byte witnesses; CPU stack restored to its original depth; 2,048 zero-valued PPUDATA writes at the independently calculated addresses; `$00/$01=$EC46` at sentinel; `$FC/$FD=0`; `$0781` preservation; `$19` increment to 1; `$07A0/$07A6/$68=0`; and `$23=$0A` maintained. A fixed-status PPU read is the bounded test condition, **not** a claim about arbitrary PPU status or NMI scheduling.

The source stream fingerprint is SHA-256 `7500a17666fbd773b53c9d784e06ab1b1b12ffaa817c2d1ccae99a6c7a53054f` over **PRG31 `$EC1D-$EC46` (42 bytes)**. This is previously covered fixed PRG31 territory (`$EC00-$EFFF`), never 42 newly credited bytes.

## Unresolved and excluded

1. **R-001 stays OPEN:** no independent reset-to-first-NMI proof that `$18=$0C,$19=$13` occurs. This is a conditional instruction-level test, not an observation of live gameplay.
2. **R-002 stays OPEN:** local post-state-zero `$07A0=$07A6=0` is now tested through `$EB82`; later `$B7DE`, bank-$01 `$BB57`, alternate setters, and all intervening NMI/helper paths are not globally closed. The state-one handler `$B58C` and subsequent room-loader state `$19=2` remain separate proof obligations.
3. **R-004 stays OPEN:** `$10` last writer at sprite renderer entry is not resolved by these PPU zero writes.
4. **No promotion:** all fixed instructions and the 42 stream bytes used here overlap prior strictly tracked fixed-bank ranges; newly decoded raw `$0A` instructions remain conditional on unproved producer liveness. Strict new PRG bytes **0**, cumulative **49,404 / 262,144 (18.8461%)**, VPP **24/100**; machine `RESUME_STATE.json` remains at completed 0507 and fixed frontier `$FB96`.
5. No IRQ scheduling, nested interrupts, PPU DMA, sprite rendering, console frame timing or reference-emulator equality is claimed. Raw ROM is not committed.

## Reproduce

```sh
python3 JP/tools/audit_0508_phase9.py 'Akumajou Densetsu (Japan).nes' 0508_phase9_report.json
```

The JSON records all bounded assertions and expected byte/stream fingerprints. The test has no external runtime or non-Python dependencies, beyond the committed Phase 8 audit module.
