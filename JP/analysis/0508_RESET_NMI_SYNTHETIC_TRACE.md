# 0508 bulk M1 — Original RESET and 450 manually injected NMI CPU traces under a declared synthetic bus

**Status:** PROVISIONAL reference-INSTRUCTION execution only, **not** real console/reference-emulator parity, natural VBlank/NMI timing, calibrated controller input, or verified live state `$18=$0C`. JP ROM SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.

## What is actually executed

`JP/tools/test_reset_nmi_trace_0508.py` uses the generic 151-official-opcode 2A03/mapped-Mapper24 stepper [published previously](0508_TRACE_CORE_AND_E7FB_CORRECTION.md). Unlike earlier Phase 8/9 local synthetic entry snapshots, this test begins at **the authentic RESET vector CPU `$E00B`**, reads original opcodes including the entire `$E020-$E034` indirect 2KiB RAM clear, executes the fixed sound reset, and stops when the original RESET reaches the idle loop at `$E04B`.

A well-defined synthetic bus supplies PPUSTATUS `$2002=$80` for the two VBlank-ready polling reads during reset. The test then sets PPUSTATUS reads to `$00` and injects 150 NMIs using the actual `$FFFA` vector (`$E057`) without scheduling IRQs, without modeling actual CPU cycles/PPU scanlines or VRC6 IRQ, and with synthetic controller `$4016/$4017` reads returning zero. Each NMI follows ROM code and returns to the caller's idle-loop PC via original `RTI` stack semantics. The three scenarios execute respectively **0, 12 or 384 ordinary idle-loop instructions between artificial NMIs**; these counts are not claimed to be real frame cycle budgets.

## Measured bounded results

| Idle instructions per NMI | NMIs executed | Total ROM-fetched CPU instruction steps, including reset | Observed state pair after each NMI |
|---:|---:|---:|---|
| 0 | 150 | **513,513** | `$18=$00 / $19=$01` |
| 12 | 150 | **515,313** | `$18=$00 / $19=$01` |
| 384 | 150 | **571,113** | `$18=$00 / $19=$01` |
| **Total** | **450** | **1,599,939** | Three different synthetic schedules |

In each run, original RESET executes **6,417 instructions** to `$E04B`; RAM `$18/$19/$68/$07A0/$07A6` is zero, SP=$FF, initial tracked raw bank=$00. The very first synthetic NMI runs **5,321** ROM instructions and advances subordinate `$19=0→1` via the fixed `$E383` handler while keeping `$18=0`. Later no-input scenarios do not advance the tested pair. Each NMI restores stack to SP=$FF, leaves `$1C=0`, and updates the `$1B` counter; the fixed path ultimately maps raw bank `$0D` by its ordinary OAM-render call.

The deterministic JSON report records the SHA-256 of each 150-entry state/instruction trace, all three pre-NMI idle budgets, first/last frame counters and mapper-bank observations. This is a **negative under stated inputs**, not a proof that the game cannot reach `$18=$0C` when a real controller is used.

## Interpretation and certification limit

- **R-001 partially narrowed but OPEN:** the original RESET-side starting state `$18=0,$19=0` and a 0→1 local first NMI transition are now independently executed from the RESET vector. The chain to `$18=$0C/$19=$13`, input events and bank-$0A room-state liveness remain unproven; the 150 synthetic no-input frames cannot establish global absence of those states.
- **R-006 OPEN:** the interpreter does not model the PPU's VBlank edge semantics, scanline/CPU cycle synchronization, `$4014` DMA stalls, controller serial protocol, APU sample generation, or VRC6 IRQ schedule. No comparison against a real emulator trace, frame image, or console has occurred. Manually injecting NMIs is *not* observation of real hardware.
- The ROM's fixed IRQ/PPU register writes are recorded, not validated against actual original-video or audio timing. SRAM and mapper memory window semantics remain the known partial VRC6 implementation.
- **Progress credit:** 0 newly certified strict PRG bytes, authoritative 49,404/262,144 (18.8461%), VPP 24/100; completed recovery state remains 0507 and fixed PRG31 `$FB96`. This is tooling/provenance evidence toward M1, not the completed M1 acceptance gate.

## Reproduction

```sh
python3 JP/tools/test_reset_nmi_trace_0508.py '/path/to/Akumajou Densetsu (Japan).nes' JP/analysis/0508_reset_nmi_trace_report.json
```

Next action: add a real PPU/mapper/IRQ/controller timing/input layer or import a trusted emulator CDL/CPU trace, then replay reset-to-NMI/room progression under grounded inputs. Do not infer a `$07A0≤4` room bound or promote raw `$0A/$0E` conditional byte ranges merely from this no-input trace.
