# JP0677 — First NMI acceptance difference: test CPU/PPU alignment before patching the CPU

## Owner v3 PowerShell Python-launcher fix (2026-10-17)

Owner's next `JP0677-status.txt` again returned `INCOMPLETE_NOT_PROVEN`: the v2 PowerShell runner resolved **two** `py.exe` `ApplicationInfo` objects (Python Launcher plus a WindowsApps alias). Using `(Get-Command 'py.exe' -CommandType Application).Source` yielded a list that PowerShell interpolated into one malformed command string (`path1 path2`), so the phase sweep still never ran. The file hashes in the status remain the expected private ROM, native EXE and original Mesen witness; they do not establish a timing result.

**v3 fix:** select exactly one existing launcher executable using `Get-Command 'py.exe' -All -CommandType Application` piped through `Test-Path -PathType Leaf` and `Select-Object -First 1`; require one candidate, then use the selected object's `Source` converted to a single string. The wrapper remains `Invoke-JP0677Python`, never a function named `Py`. No CPU/PPU code, native binary, ROM, trace parsing, emulator command flags, frame replay or parity thresholds changed. Local tests passed: **11 ROM-independent JP0677 analyzer tests plus 7 static launcher checks** (18 total). This is **not** an end-to-end Windows PowerShell test. Owner rerun with private `JP0677-NMI-Alignment-Phase-Sweep-Kit-v3.zip` remains pending.

## Owner JP0677 launcher failure and hotfix v2 (2026-10-17)

The owner supplied `JP0677-status.txt` (schema `JP0677-private-alignment-sweep-status/v1`) reporting `INCOMPLETE_NOT_PROVEN` / `The script failed due to call depth overflow.` The status verified the expected private original ROM, native executable and original Mesen witness SHA-256, but **does not report any successful alignment runs**. Do not interpret this as support for or against the CPU/PPU phase hypothesis.

The local PowerShell runner's wrapper was defined `function Py([string[]]$arguments)` and executed `& py -3 @arguments` from inside the wrapper. PowerShell command resolution is case-insensitive, so `py` resolved back to the `Py` function, recursively invoking itself until call-depth overflow; the Python analysis did not execute. The correction **renames the wrapper** to `Invoke-JP0677Python` and resolves `py.exe` explicitly with `Get-Command py.exe -CommandType Application`, executing its absolute path. The four-alignment native commands, input ROM/executable SHA checks, CPU traces, audio-prefix gates, and Python analysis are unchanged. The owner should extract `JP0677-NMI-Alignment-Phase-Sweep-Kit-v2.zip` and rerun the same PowerShell command.

**Verification:** eleven existing ROM-independent JP0677 analyzer tests and five new static PowerShell launcher regression checks passed (16/16). These are local tests; the corrected Windows PowerShell runner and native four-phase sweep have **not** yet been executed by the owner. The only conclusion supported remains the earlier JP0676 completed extra instruction, followed by a discarded native NMI fetch. No CPU timing change is warranted.

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