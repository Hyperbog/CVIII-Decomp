# JP0677 — First NMI acceptance difference: test CPU/PPU alignment before patching the CPU

## What is proven from the prior private witnesses

The JP0673–JP0676 owner-local audits validate the corrected 1,100-frame Japanese original/native ordered audio-write address/value stream (**3,401/3,401**) and isolate the first *instruction* difference at matched instruction ordinal **3,300**: native completed one additional three-cycle instruction, then discarded the next opcode fetch due to pending NMI. Native's seven-cycle interrupt entry then performs the correct two preliminary reads, three stack pushes, and two `$FFFA/$FFFB` vector reads. Native minus Mesen vector and stack bus cycles are **+2**, while the next matched instruction-start offset is **+3**, partly due to differing callback timestamp phases.

The direct *reason* for the additional instruction is that the native CPU had not accepted the NMI at the instruction boundary where Mesen took it. That alone does **not** establish whether the NMI pin was asserted later in native PPU time or the native CPU sampled/polled a timely pin edge too late. The JP0676 capture has no timestamped NMI pin/CPU polling markers. Do not assign that root cause without an experiment.

## Newly identified configuration-level candidate

**Pinned NESRecomp** `mstan/nesrecomp` commit `2b4fcdb98c9e702be3fb365cfc645003c50b5fc1`:

- `runner/cyc/cyc_host.c` documents `--align N` for CPU/PPU phase **0–3**, *default 0*, parses `--align`, and passes it to `cyc_power_on((uint8_t)align)`.
- `runner/cyc/hw_machine.c` sets `hw.align = ppu_alignment & 3`; in NTSC `run_tick()` samples `ppu_nmi_output()` at **master tick 4** into `cpu_nmi_input()`. In `runner/cyc/cpu6502.h`, `cpu_poll()` promotes the latched `nmi_edge` to `do_nmi` and `cpu_fetch()` subsequently tests that flag after the potentially discarded fetch.
- `runner/cyc/hw_internal.h` defines PPU NMI output as `ppu.nmi_enable && ppu.vblank`; the precise vblank latch is modeled in `hw_ppu.c`.

**Upstream Mesen2** source baseline `b9fa69ddc6d0a331fb103fdb5eef6904305703c2`:

- `Core/NES/NesCpu.cpp` `Reset()` uses `_ppuOffset = 1` by default when randomized CPU/PPU alignment is off; `StartCpuCycle()` advances the PPU with this offset, and `EndCpuCycle()` observes the NMI flag into `_needNmi`/`_prevNeedNmi`.
- `Core/NES/NesPpu.cpp` `TriggerNmi()` asserts the CPU NMI flag if NMI is enabled. `NesCpu::Exec()` enters `IRQ()` at an instruction boundary when the prior interrupt state is pending.

**Crucial caveat:** NESRecomp's numeric alignment 0 and Mesen's `_ppuOffset=1` are not automatically equivalent origin conventions. A difference is visible at the *configuration/source* level; whether it caused the actual initial NMI divergence is only a **testable hypothesis**.

## JP0677 A/B test — no new Mesen session or build

The distributed `JP0677-NMI-Alignment-Sweep-Kit.zip` runs the same authenticated diagnostic native executable on the same ROM/input-neutral opening for **7 frames** in **four native CPU/PPU alignment modes** (`--align 0,1,2,3`). Per-frame native bus traces for frames 2–5 cover the first NMI discrepancy, even when an interrupt straddles a frame boundary. An owner-local Python matcher authenticates prior JP0673/JP0676 aggregate/witness hashes, requires the **entire `--align 0` bus trace to hash-match** the already validated baseline and the 7-frame audio hash to match, and requires all four phase variants to preserve the **first thirteen original 2A03/VRC6 register addresses/values in order**. The matcher then counts actual completed native opcode instructions between matched pre-/post-NMI PCs and checks the continuous discarded-fetch bus signature.

**If any phase removes the extra completed instruction while keeping the required value and provenance gates:** the first divergence is experimentally **sensitive to CPU/PPU clock alignment**; inspect that phase and subsequent audio-cycle offsets to assess whether mismatched phase initialization is the causal explanation. **Do not** silently change the default, assert that a particular alignment is hardware-correct, or claim full cycle parity from one NMI alone.

**If no valid phase removes it:** a targeted internal edge/poll witness (native `ppu_nmi_output()`, `cpu_nmi_input`, `cpu_poll` and Mesen NMI flag/end-cycle latch) is required. A private diagnostic build may be needed. A source-level CPU timing patch is still unjustified.

The 11 synthetic ROM-free tests pass; **owner Windows sweep pending**. No private ROM, raw full CPU trace, raw audio events or compiled binaries on GitHub.