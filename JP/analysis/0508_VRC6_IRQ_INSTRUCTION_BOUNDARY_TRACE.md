# 0508 bulk: VRC6 IRQ source integrated into ROM-fetched RESET/NMI execution

**Evidence grade:** bounded experimental 2A03 + VRC6 source + vblank CPU-instruction emulator test, **NOT** cycle-accurate original-console/reference-emulator trace parity and **NOT** a completed 0508 semantic-coverage checkpoint. Source ROM SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.

## Original hardware/code contract

The existing native source `JP/src/vrc6_irq.cpp` implements mapper-24 latch/control/acknowledge register writes and the scanline 341/3 prescaler, already validated by `tests/vrc6_irq_test.cpp`. New `tools/trace_vrc6_irq_frames_0508.py` mirrors that same mapper component in the ROM-fetched 6502 execution harness and enters **original ROM fixed IRQ vector `$E0F5`** at instruction boundaries when IRQ is asserted and I=0. NMI is prioritized if both are pending; the CPU pushes the interrupt context and executes the ROM handler, including `$E100` temporary raw-bank `$01` mapping and `$E118/$E11D` mapper control/acknowledge distinction, restoring `$23`/bank on exit. `RTI` is attributed to the entry type, not spuriously counted as an NMI return.

The test `tools/test_vrc6_irq_frames_0508.py` performs **267** checks: one-shot and repeating acknowledgment, cycle mode, control/enable changes, the native 114/114/113 CPU scanline prescaler pattern, mapper-register mirror encoding, vector priority and batched-vs-stepwise counter equivalence across 240 combinations. All pass. The previous 151-opcode cycle-class and 43,008 CPU micro-case tests also pass.

## Large multi-scenario results

| Synthetic input and duration | Original instructions | Modeled NMI entries | Modeled IRQ entries = returns | Observed first-level `$18` states |
|---|---:|---:|---:|---|
| Start each 30 frames, 480 frames | 4,437,108 | 475 | 99 | `$00,$02,$03,$04,$09,$0A` |
| None, 240 frames | 2,207,098 | 237 | 234 | `$00` |
| A/B/Start alternation, 240 frames | 2,216,850 | 236 | 17 | `$00,$02,$0A` |
| **Total, 960 frames** | **8,861,056** | **948** | **350** | no trace reaches `$0C/$0D` |

IRQ source generated 393 counter-overflow assertions across these scenarios. Some assertions are masked or cleared without becoming distinct handler entries, so **assertions are not interchangeable with CPU vector entries**. All **350 recorded IRQ entries returned via RTI**. The run checks that all logged vector addresses equal `$E0F5`. The identical first-level state sets and NMI counts in earlier IRQ-disabled synthetic runs are a **local differential sanity check**, not hardware-level parity. Exact full traces and SHA fingerprints are in `0508_irq_frames_start30_480.json`, `0508_irq_frames_none_240.json`, `0508_irq_frames_abstart_240.json`, and `0508_vrc6_irq_batch_summary.json`.

## Bounds and next action

- Mapper VRC6 IRQ source is modeled with existing native semantics. **CPU write timing is still instruction-boundary, not per memory-bus-cycle**. NES PPU timing is a vblank proxy without rendering, odd-frame skip or full OAM/DMA effects. CPU interrupt latency, APU and raster IRQ interleaving remain approximate.
- The model does **not** prove actual gameplay reachability of `$18=$0C/$0D`, $19/$68 producer domains, room loader/live `$07A0` pointer bounds, native reference-emulator equivalence or VPP rubric trace-parity credit. A negative observed trace is not a global impossibility proof.
- High-value next batch: compare CPU/mapper/RAM/PPU event traces against an independent authoritative NES emulator with correct timing; use that reference to drive raw bank `$0A` and `$0E` state/domain promotion, then derive exact non-overlapping physical byte manifests. No additional micro-phase selector speculation without a new runtime witness.

**Progress:** 0 newly admitted strict PRG bytes; **49,404/262,144 (18.8461%)** remains official; **VPP 24/100**; `RESUME_STATE.json` remains completed 0507, frontier fixed `$FB96`. This committed batch is provisional tooling/research, not a semantic checkpoint.

## Reproduce

```sh
python3 JP/tools/test_vrc6_irq_frames_0508.py 'Akumajou Densetsu (Japan).nes' JP/analysis/0508_vrc6_irq_component_report.json
python3 JP/tools/trace_vrc6_irq_frames_0508.py 'Akumajou Densetsu (Japan).nes' JP/analysis/0508_irq_frames_start30_480.json --frames 480 --policy start30 --max-steps 6500000
python3 JP/tools/trace_vrc6_irq_frames_0508.py 'Akumajou Densetsu (Japan).nes' JP/analysis/0508_irq_frames_none_240.json --frames 240 --policy none --max-steps 3200000
python3 JP/tools/trace_vrc6_irq_frames_0508.py 'Akumajou Densetsu (Japan).nes' JP/analysis/0508_irq_frames_abstart_240.json --frames 240 --policy abstart --max-steps 3200000
python3 JP/tools/assemble_0508_irq_batch.py
```

The tools import the existing 0508 ROM-fingerprinted trace core/cycle scheduler in `JP/tools/`, and the summary assembler expects the previously committed IRQ-disabled `JP/analysis/0508_cycle_vblank_480_report.json` and `JP/analysis/0508_cycle_vblank_batch_summary.json`.
