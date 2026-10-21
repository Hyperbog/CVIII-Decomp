# JP0672 — Native vs Mesen2 audio write-cycle phase (source review + owner-private paired trace)

**Verdict:** the JP0671 original and JP0668 native 1,100-frame traces agree in **all 3,401 ordered audio register addresses and values**, but **not** in absolute CPU-cycle timestamps (only 76 equal). No changes to CPU timing, native sound engine, or equality comparator are authorized by this audit. Do not infer PCM/DMA/audio-output parity.

## Source-level observation: both taps occur before the hardware write; their counters update at different points

Pinned native external engine: `mstan/nesrecomp` at `2b4fcdb98c9e702be3fb365cfc645003c50b5fc1` (the owner's captured C11 build). The project instruments the raw bus writes via [`JP/recomp/tools/patch_cyc_audio_bus_0610.py`](../../recomp/tools/patch_cyc_audio_bus_0610.py). In its APU `apu_write` and mapper `hw_cart_cpu_write` handlers, the injected tap calls `cviii_audio_bus_observe(hw.cycles, addr, value)` **before** the write is dispatched to the chip. The upstream [`cpu6502.h`](https://github.com/mstan/nesrecomp/blob/2b4fcdb98c9e702be3fb365cfc645003c50b5fc1/runner/cyc/cpu6502.h) `cpu_write()` executes `hw_cycle_start(...)` → `hw_write(...)` → `hw_cycle_finish(...)`; upstream [`hw_machine.c`](https://github.com/mstan/nesrecomp/blob/2b4fcdb98c9e702be3fb365cfc645003c50b5fc1/runner/cyc/hw_machine.c) increments `hw.cycles++` in `hw_cycle_finish()`. The observer samples the counter **before the current CPU write cycle is retired**.

In upstream Mesen2, [`NesCpu.cpp`](https://github.com/SourMesen/Mesen2/blob/b9fa69ddc6d0a331fb103fdb5eef6904305703c2/Core/NES/NesCpu.cpp) `MemoryWrite()` performs `StartCpuCycle(false)` → `_memoryManager->Write()` → `EndCpuCycle(false)`. `StartCpuCycle()` increments `_state.CycleCount` **before** the memory-manager write. [`NesMemoryManager.cpp`](https://github.com/SourMesen/Mesen2/blob/b9fa69ddc6d0a331fb103fdb5eef6904305703c2/Core/NES/NesMemoryManager.cpp) invokes debugger `ProcessMemoryWrite` **before** dispatching the write to the hardware handler. [`Debugger.cpp`](https://github.com/SourMesen/Mesen2/blob/b9fa69ddc6d0a331fb103fdb5eef6904305703c2/Core/Debugger/Debugger.cpp) invokes Lua memory callbacks inside this prewrite processing. `emu.getCpuCycleCount()` and the flat `state['cpu.cycleCount']` agreed in the earlier owner probe. The Mesen callback therefore sees the counter **after incrementing for the current write cycle**.

For matching machine-origin conventions and execution, this phase distinction predicts `native_hw.cycles = mesen_cycle_count - 1` at the same bus write. It is a *conditional convention prediction*, **not proof that the machines have matching reset epochs, full instruction traces, PPU/NMI boundaries, or DMA stalls**. Instrumentation placement is correct for both: a destructive global offset or wholesale sound-code change would obscure evidence.

## Owner-private real-pair audit — aggregates only

Both input traces are owner-private and remain off GitHub. The audit was executed locally with Python stdlib on the existing complete JP0671 Mesen log SHA-256 `5aba434cc9bed36908ef97f63aecf0cd8a4c30b35db2aa4060e367553c3bf5f5`, the retained native CSV SHA-256 `3d4a32dd8c507119960f17e7a8104d17b492a6ff23eda4c11688eeec38b3eac3`, and the pinned JP0668 input replay SHA-256 `1ae01d6032847d2e37e151e09398c1f6f6765ed1915fe0623069d5d96d40ab3c`. It checks the native manifest SHA files and **one** power-on epoch; the original 1,100 frames/1,099 polls, frame/poll input-mask schedule, and JP0671 physical CPU Start witness were also checked.

| Test | Private real-pair result | Interpretation |
| --- | ---: | --- |
| Equal ordered register address/value writes | **3,401/3,401** | Proven for this one scripted session |
| Exact absolute CPU cycles, *no correction* | **76/3,401** | Strict timestamp parity fails |
| Offset (`native − Mesen`) min / max | **−7 / +9** cycles | Not a single fixed offset |
| Exact adjacent write intervals | **2,710/3,400** | Most local instruction-to-write timing intervals agree |
| Mesen adjacent write gaps ≤ 10 cycles | **265/265** equal native intervals | Short register-write sequences have matching cadence |
| Mesen adjacent write gaps ≤ 100 cycles | **987/1,014** equal native intervals | Changes can occur within a short multiwrite run |
| Observed offsets before first DPCM descriptor write | **−3..+3** cycles | Variable offset exists *before* DPCM descriptor programming |
| Hypothetical “native +1” matching count | **988/3,401** | Diagnostic only; not accepted as cycle parity |

The first original DPCM descriptor write in this run occurs at write **117**, after early offset variation had already appeared. This alone cannot exclude earlier DMC activity triggered by a different mechanism, nor identify what causes the offsets. Periodic 2-/4-cycle jumps and short constant-offset runs are **consistent with**, but do **not prove**, CPU/PPU/NMI boundary or DMA timing differences. Do not claim a specific interrupt, miscount or DMC bug from register traces alone.

## Reproduce without publishing licensed events

The repo adds [`JP/recomp/tools/jp0672_audio_cycle_audit.py`](../../recomp/tools/jp0672_audio_cycle_audit.py) and its synthetic-data regression tests. Locally supply the owner-private files using paths on the machine holding them:

```powershell
py -3 JP/recomp/tools/jp0672_audio_cycle_audit.py `
  --mesen-log C:\Tools\Mesen2\Private\JP0671-Mesen-original-fixed.log `
  --native-dir C:\Tools\Mesen2\Private\JP0668-Native-StderrFix-20261017-205325-9e1573 `
  --replay C:\Tools\Mesen2\Private\JP0668NativeKit\JP0668-window-input.txt `
  --out C:\Tools\Mesen2\Private\JP0672-timing-report.json

py -3 -m unittest discover -s JP/recomp/tools -p "test_jp0672_audio_cycle_audit.py" -v
```

The command outputs only aggregate counts, histogram and evidence hashes; **never copies register events/values, ROMs, audio assets, or CSV contents to the public repository**. The strict original/native comparison always uses raw, unshifted event clocks. A source-phase +1 diagnostic is deliberately excluded from the verdict and never rewrites any trace.

## Next precise engineering question

To determine whether the remaining ±9 cycles come from the native CPU core, scheduler, PPU/NMI alignment or DMC DMA, obtain a **matched CPU-side instruction/bus witness near the first divergence** in a separate, minimally intrusive session (for example, `PC`, CPU-cycle, $4016 strobe/read, NMI entry and OAM/DMC DMA stall counters on both machines). Input masks alone or audio register callbacks cannot reveal which non-audio CPU cycles account for jumps. Before requesting another Windows capture, instrument a deterministic non-ROM synthetic CPU bus test in the upstream-compatible native core and compare its cycle-start/write/finish sequence with Mesen's documented phase. Even an exact convention correction would **not** certify PCM waveform, DPCM DMA, or general game parity.