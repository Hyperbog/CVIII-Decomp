# JP0673 — First variable CPU-cycle offset: bracket, ROM-free contract and targeted witnesses

## Result from authentic owner-private traces (no ROM/events redistributed)

The corrected original JP0671 Mesen2 trace and retained JP0668 native C11 Alpha trace have **3,401/3,401 equal ordered register/value events**. JP0673's fail-closed audit identifies the **earliest offset change at audio write ordinal 13**:

| Observation | Mesen2 | Native C11 |
| :-- | --: | --: |
| Write 12 cycle | 80,414 | 80,413 |
| Write 13 cycle | 165,488 | 165,489 |
| Native minus Mesen write timestamp | −1 → +1 | — |
| CPU cycles elapsed between the writes | 85,074 | 85,076 |

Mesen end-frame boundaries **3, 4, 5** and three actual input polls fall strictly inside this gap. The first scripted player-one Start press occurs at frame 90; first logged DPCM descriptor write is event 117. The two extra native cycles accumulate before either, so a *button-input mismatch at frame 90* and DPCM *descriptor programming* cannot explain this **first** transition.

**Exact cause remains unknown.** Audio-only writes lack CPU read/instruction/NMI/DMA observations during 85,000+ intervening cycles. Do **not** infer whether two native CPU cycles were added, two Mesen CPU cycles omitted, or the same number of cycles have been accounted for against different power-up/frame epochs. Distinguish observed elapsed-count difference from actual executed extra bus cycles.

## Source-bound phase convention

- Native pinned engine `mstan/nesrecomp` `2b4fcdb98c9e702be3fb365cfc645003c50b5fc1`: `cpu6502.h` runs `hw_cycle_start` → `hw_write` → `hw_cycle_finish`; `hw_machine.c` increments `hw.cycles` in `hw_cycle_finish`. Project's JP0610 audio observer reads `hw.cycles` inside write handler **before** retirement.
- Mesen2 upstream `SourMesen/Mesen2` reviewed `b9fa69ddc6d0a331fb103fdb5eef6904305703c2`: `NesCpu.cpp` `MemoryWrite()` performs `StartCpuCycle(false)` → memory-manager write → `EndCpuCycle(false)`; `StartCpuCycle` increments CPU `CycleCount`, and the `NesMemoryManager.cpp` dispatcher calls the debugger's Lua write callback before hardware write.
- **Conditional prediction** on the same instruction/bus cycle stream and common counter epoch: native−Mesen **−1 on every write**. A fixed write-callback phase is not a mechanism for the changing −1→+1 offset.

## ROM-independent executable contract model: completed

`jp0673_rom_free_bus_contract.py` executes a deliberately synthetic *bus-cycle schedule*, not actual Mesen2 or NESRecomp code. It models 6502 `LDA #`, `STA abs`, `INC abs` (two writes), a taken branch, a seven-cycle NMI-entry fixture, and another `STA abs`. It verifies that **four writes and all six synthetic instruction starts** have a constant native−Mesen offset of **−1** under the two source-documented counter phases. In a controlled counterexample, inserting two synthetic read cycles after the first `STA` changes the four write offsets from `[-1,-1,-1,-1]` to `[-1,+1,+1,+1]` without changing addresses/values. This shows *how* a real gap difference would manifest; it **does not prove any two bus cycles were inserted in the owner build**.

Eleven isolated Python regression tests pass, including fail-closed event value/order checks and write-bracket inclusion. No licensed ROM or game-derived register content is part of the model.

## Next actual CPU instruction/bus witness (short, owner-private; no rebuild)

The pinned native `cyc_host.c` already supports `--trace-frame N --trace-out FILE` (single frame, forces headless), and `cyc_trace.c` emits `INSN PC=...` and per-cycle CPU/DMA bus records. The project's previously compiled **trace-capable native EXE** can be used; no source alteration or new build is necessary. Mesen's documented `emu.callbackType.exec` supplies CPU instruction start callbacks, plus read/write memory callbacks for the NMI vector, `$4014` OAM DMA, `$4016` controller, `$2002` PPU status, `$2000` PPU control, and stack page. Controller state stays neutral because the investigated interval precedes scripted presses.

The optional owner-private `JP0673-Run-CPU-Witness.ps1` kit captures just **7 Mesen frames** and native frames **2–5** as full upstream trace files. It verifies exact ROM/Mesen/executable SHA256 before running and stores *raw* CPU PC/bus/opcode traces **only** under `C:\Tools\Mesen2\Private\JP0673-CPU-Witness`. It is **not yet Windows-tested**. The local comparison program must confirm that all captured original Mesen audio writes within the study window match the earlier JP0671 log, and that the headless native first 13 writes match the earlier 1,100-frame native window capture. If not, **the witness is not comparable and should not be used for causal conclusions**.

After proving provenance, align actual CPU instruction PC sequences by absolute timestamp proximity without rebasing; find the **first change in the aligned instruction-interval difference** and inspect neighboring DMA and interrupt-vector bus entries. This can narrow the 85,074/85,076-cycle gap to an instruction/interrupt boundary. If Mesen/native instruction streams or trace-mode event sequences differ, record that discrepancy rather than asserting a timing defect.

The native source `--trace-frame` path switches to **headless** mode, unlike the existing window-mode Alpha reference; the 13-write exact-prefix gate is therefore essential. Also, Mesen `exec` callbacks and native `INSN` printouts need an independent opcode/bus-phase check before treating their *absolute* cycle numbers as the same phase. Neither this gate nor Windows execution is yet proved.

## Remaining gates

1. **Confirmed:** first changed write offset at ordinal 13 and 2-cycle interval disagreement across end-frame boundaries 3–5.
2. **Confirmed only in synthetic source-informed model:** fixed callback phase creates constant −1 offset; a two-cycle schedule discrepancy can make −1→+1.
3. **Not yet observed:** earliest mismatch in matched real CPU instruction PCs, branch/I/O reads, NMI stack/vector access, or DMA cycles.
4. **Not certified:** cycle-exact parity, full DMC DMA parity, PCM parity, or general complete-game behavior.

All output suitable for the public repo consists only of aggregate counts, evidence hashes, source references and synthetic fixtures. Owner-private raw CPU PC/audio event streams remain off GitHub.