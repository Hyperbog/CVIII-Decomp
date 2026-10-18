# JP0677 — First NMI acceptance difference: test CPU/PPU alignment before patching the CPU

## JP0677 owner four-alignment result — COMPLETE, no alignment fixes NMI (2026-10-17)

The owner submitted `JP0677-NMI-alignment-sweep.json` (schema `JP0677-CPU-PPU-phase-sweep/v1`; safe aggregate SHA-256 `2e75c6bbba3ec218997ceff012b7dfe592a06620a541925346de704668ce6df2`). The assistant directly parsed the uploaded aggregate and independently checked the four rows' consistency; full raw Windows traces were **not** uploaded and hence have **not** been independently replayed here. All row-level tests below refer to gates reported by the owner's private local analyzer.

| Native alignment | Native extra completed instruction | Valid discarded NMI fetch | Native-Mesen first NMI push | Native-Mesen matched instruction interval | First 13 audio cycle offsets |
| --- | --- | --- | ---: | ---: | --- |
| `--align 0` | 1 | true | +2 CPU cycles | +3 CPU cycles | first 12 at −1, 13th +1 |
| `--align 1` | 1 | true | +2 CPU cycles | +3 CPU cycles | same |
| `--align 2` | 1 | true | +2 CPU cycles | +3 CPU cycles | same |
| `--align 3` | 1 | true | +2 CPU cycles | +3 CPU cycles | same |

All four runs preserve the first thirteen audio-register address/value pairs, and the `--align 0` native trace reproduces JP0673 exactly. The report sets `alignment_phase_sensitivity_observed=false`, `alignment_settings_without_extra_native_instruction=[]`, `NO_ALTERNATIVE_ALIGNMENT_REMOVED_EXTRA_INSTRUCTION`, and `CPU_timing_patch_authorized=false`.

**Inference:** The tested `--align` startup setting does not resolve or affect the first differing NMI acceptance boundary. The initial clock-phase-selector hypothesis is **rejected as a practical explanation or correction** for this specific case, though this does not establish that all PPU timing/phase implementations are identical. **The exact CPU cycle at which the PPU's NMI output changes and the CPU samples/promotes the NMI has not been observed on both engines**, so the causal choice remains open.

### JP0678 single discriminating test (not yet collected)

A conclusive differential witness must identify these events on the *same CPU-cycle convention*, over a very short bracket around the **first** NMI, not collect a new broad trace:

1. **PPU source edge:** PPU asserts the NMI output (with scanline/dot and CPU master-clock phase).
2. **CPU edge sample:** the CPU samples the PPU NMI signal and latches the rising edge.
3. **CPU poll / pending promotion:** the instruction-specific point where the pending NMI becomes eligible for the next opcode fetch/interrupt entry, with neighboring instruction-boundary ordinal.
4. **Discarded opcode fetch:** CPU fetch rejected because NMI is pending; next two preliminary reads, stack pushes and `$FFFA/$FFFB` vector reads can reuse JP0676 proven bus signature.

Pinned native source observation sites: `runner/cyc/hw_machine.c::sample_nmi` (`cpu_nmi_input(ppu_nmi_output())` at NTSC CPU master tick 4), `runner/cyc/cpu6502.c::cpu_nmi_input`, `runner/cyc/cpu6502.h::cpu_poll` and `cpu_fetch`/`cpu_fetch_rom`. Original Mesen2 source observation sites: `Core/NES/NesPpu.cpp::TriggerNmi`/`SetNmiFlag`, `Core/NES/NesCpu.cpp::EndCpuCycle` (`_state.NmiFlag`, `_needNmi`, `_prevNeedNmi`) and `Exec`/`IRQ`. Mesen2's existing Lua NMI callback occurs *after* interrupt delivery and cannot alone timestamp the assertion/sample/poll sequence. Either diagnostic source instrumentation of both cores or an independently calibrated equivalent witness is required. Compile diagnostics privately; never commit third-party modified cores, original ROM, raw traces or binaries. Instrumentation must **only observe**, never modify CPU/PPU execution or shift timestamps.

Decision gate: if PPU assertion/sample timestamp already differs, investigate PPU source/latch clock phase; if assertion/sample agree but pending-poll differs, investigate per-instruction `CYC_POLL` flags / Mesen `_prevNeedNmi` instruction-end sampling; if both agree, re-check trace PC pairing/callback phases before patching. Preserve 3,401/3,401 ordered audio address/value parity while addressing CPU-cycle parity.

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