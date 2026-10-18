# JP0679 — Dual-clock, seven-frame Mesen2 EndFrame diagnostic (preflight)

Status: **owner run pending**. The completed JP0678 report finds exact selected CPU instruction/bus/audio streams between original Mesen2 and rebuilt JP0678 Mesen2, but frame callback CPU timestamps differ `[+1,+1,0,+1,+1,0,+1]`; final END differs only `cycle:+1`. This is a bounded observational difference, **not a certified frame-timing source bug**. The separate native NESRecomp one-additional-instruction-before-NMI discrepancy remains open.

## JP0679 owner result — PPU frame clock exact, CPU callback count differs by 0/1 (2026-10-18)

The owner supplied the sanitized local analyzer report `JP0679-dual-clock-audit.json` (schema `JP0679-sanitized-dual-clock-frame-audit/v1`; SHA-256 of uploaded JSON `c4185a0c93426d0c119b0cc946424fe13cb61af89ec765a0c24e3b1d7e129bb5`). The report affirms exact original and rebuilt provenance checks, 7 frame pairs, strict reproduction of the previously verified JP0678 frame deltas, and recognized post-hotfix rebuilt managed DLL provenance.

| Owner-side aggregate | Frame positions 1–7 |
| --- | --- |
| Rebuilt − original `ppu.masterClock` | `[0,0,0,0,0,0,0]` |
| Rebuilt − original PPU scanline | `[0,0,0,0,0,0,0]` |
| Rebuilt − original PPU dot | `[0,0,0,0,0,0,0]` |
| Rebuilt − original PPU frame index | `[0,0,0,0,0,0,0]` |
| Rebuilt − original `cpu.cycleCount` | `[+1,+1,0,+1,+1,0,+1]` |
| Rebuilt − original `emu.getCpuCycleCount()` | `[+1,+1,0,+1,+1,0,+1]` |
| API − `cpu.cycleCount` (original and rebuilt) | `[0,0,0,0,0,0,0]` each |
| `getState().masterClock` − CPU counter (original and rebuilt) | `[0,0,0,0,0,0,0]` each |
| `ppu.masterClock % 12` (original and rebuilt) | `[0,8,4,0,8,4,0]` each |
| Current probe API − respective earlier JP0673/JP0678 witness marker | `[0,0,0,0,0,0,0]` each |

**Revised conclusion:** **Exact PPU-based frame-boundary timing gate PASSES (all seven frame ticks and positions agree).** The original stricter **CPU-cycle-at-EndFrame gate still FAILS** and must not be silently re-labeled as exact. The finding **disproves the narrow conjecture that a difference between Lua's exposed CPU API and the internal `cpu.cycleCount` value caused the residual**: those fields are identical in both builds. A difference in CPU-cycle accounting or CPU↔PPU execution/callback phase remains; it may be a clock-origin/convention mismatch rather than a change in executed program behavior, but that root cause is **not directly determined**. Previous JP0678 30,070/30,070 exact instruction, selected bus and 19/19 audio event comparisons remain intact. No CPU code/hardware timing patch authorized.

The seven PPU clock residues repeat `0,8,4` on the 12-master-tick NTSC CPU cycle grid; this is consistent with fractional frame/CPU-clock alignment but does not *by itself* prove a particular floor/ceil formula or clock offset. The original and rebuilt Mesen2 builds may have different callback timing conventions or effective CPU/PPU sync. Direct original-versus-NESRecomp NMI pin equivalence and exact native CPU-cycle parity remain unproven. Avoid conflating Mesen-vs-Mesen frame-clock agreement with native-vs-original NMI parity.

**Engineering gate recommendation:** Preserve two separately labeled validations in the project: (A) `EndFrame_PPU_time_exact: PASS` (meaningfully relevant to rendered frame timing) and (B) `EndFrame_CPU_cycle_exact: FAIL_bounded_0_or_1`, with actual sample offsets and provenance. If changing the engine to achieve hardware CPU-cycle exactness later, independently calibrate CPU endFrame callback phase and NMI edge/poll signals; do **not** adjust event timestamps just to satisfy the comparison. This bounded Mesen-only validation investigation can now close without another Mesen2 rebuild, freeing effort for native gameplay/modifiability. If a user explicitly wants the stricter CPU-count gate resolved too, a narrow next diagnostic is to log the CPU `StartCpuCycle`/ `EndCpuCycle` phase as `EndFrame` fires, in a private rebuilt diagnostic, rather than recapturing long bus traces.

## Owner JP0679 preflight: changed managed DLL SHA; v2 narrow allowlist (2026-10-18)

The owner uploaded `JP0679-status.txt` (schema `JP0679-private-dual-clock-status/v1`) reporting `INCOMPLETE_NOT_PROVEN` before either new dual-clock probe ran. The runner rejected `C:\Users\hyper\Downloads\Mesen2-JP0678-NMI\bin\win-x64\Release\Mesen.dll` because its observed SHA-256 was `4311442e1bc94096d36890f6af9e3d5666eed24a5f9295f79272eb31b146fc6f`, not the earlier JP0678-captured `65e6105611ffe809ad31ceb5a49458f482e845c507b428284f598f809202c6b8`. The reason the managed app DLL changed has **not** been established; do not claim bitwise executable equivalence.

V2 owner-local `JP0679-Mesen-Dual-Clock-Frame-Audit-Kit-v2.zip` updates both PowerShell capture runner and Python sanitizer to allow **exactly these two observed Mesen.dll digests** and to record whether the app artifact matches the earlier JP0678 capture or the subsequently observed Release DLL. The original ROM SHA, original authenticated Mesen EXE SHA, instrumented `MesenCore.dll` SHA, prior original+instrumented CPU witness hashes, seven-frame READY/BEGIN/END checks, and all private clock comparison gates remain strictly enforced. New unknown app digests still fail closed. The Lua dual-clock probe and emulator source are **unchanged**, and no native binary was rebuilt for v2.

Verification: **18 local ROM-independent tests** passed (15 original plus three regression checks for accepting the one new observed app hash while rejecting all other digests and preserving hard ROM/core/original guards). No new Windows capture or NMI clock result is yet available. Owner should replace the JP0679 kit files in `C:\Tools\Mesen2\JP0673Kit`, rerun the identical `JP0679-Run-Dual-Clock.ps1` command, then run `jp0679_analyze.py` only on `CAPTURED_NEEDS_SANITIZED_ANALYSIS`. All raw logs remain owner-local.

## Source-grounded correction to proposed dual-clock comparison

The top-level `emu.getState().masterClock` is **not** an independent PPU clock for NES in pinned Mesen2. `Core/Debugger/LuaApi.cpp::GetState` reads `Emulator::GetMasterClock()`, which calls `NesConsole::GetMasterClock()`, which returns `_cpu->GetCycleCount()`. The JP0678 compatibility API `emu.getCpuCycleCount()` also reads `NesCpu::GetCycleCount()`. Therefore comparing just those two values in the rebuilt app is circular.

Mesen2's `NesPpu::Serialize` explicitly makes the *nested PPU* `_masterClock`, `_scanline`, `_cycle`, and `_frameCount` visible under `SerializeFormat::Map`. Through `NesConsole::Serialize`, `Serializer::NormalizeName`, and Lua `getState`, their keys are `ppu.masterClock`, `ppu.scanline`, `ppu.cycle`, and `ppu.frameCount`; the CPU's `_state.CycleCount` is `cpu.cycleCount`. The PPU clock runs on the PPU timing grid (`Core/NES/NesPpu.h::Run` advances `_masterClock` by `_masterClockDivider` per PPU cycle); `EndFrame` is called within `NesPpu::SendFrame` during that PPU stepping.

## Delivered owner-private experiment

Owner ZIP: `JP0679-Mesen-Dual-Clock-Frame-Audit-Kit.zip`, SHA-256 `4cd7b06ce5982faac0f73996e3efdc5951a713f4fdd7e75de77fe794f7709f80` (private download via chat; not committed). Contains:

- `mesen_jp0679_dual_clock.lua`, a seven-frame-only read-only `EndFrame` snapshot with both CPU counters, PPU clock and scanline/dot/frame position; same Lua file run against **both** original authenticated Mesen2 EXE and already-built instrumented JP0678 DLL, with neutral input injection matching the original witness.
- `JP0679-Run-Dual-Clock.ps1`, a SHA-256-gated owner runner; refuses changed original ROM/EXE or rebuilt instrumented `MesenCore.dll`/`Mesen.dll`. Accepts Mesen2 process exit `-1` only if seven valid `JP0679_FRAME` records and `JP0679_END frames=7` exist in each private log. No recompiles, patches, source edits, or full CPU/bus traces.
- `jp0679_analyze.py`, sanitizes per-frame original vs instrumented differences for the independent PPU clock, PPU scanline/dot/frame index, both CPU clocks, the two API-minus-state offsets and CPU-clock vs PPU-clock sub-cycle residues (mod 12). Requires exact original JP0673 and rebuilt JP0678 seven-frame witness hashes plus previous verified `[1,1,0,1,1,0,1]` frame delta gate. Reports no raw CPU cycle or PPU absolute clock, PC/opcode, bus address or ROM bytes.
- `test_jp0679.py` (15 local ROM-independent tests passed) and README.

Owner extraction target: `C:\Tools\Mesen2\JP0673Kit`. Execute `powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Tools\Mesen2\JP0673Kit\JP0679-Run-Dual-Clock.ps1"`, then run the packaged `jp0679_analyze.py` with the arguments in the private README. Upload **only** `C:\Tools\Mesen2\Private\JP0679-Dual-Clock\JP0679-dual-clock-audit.json` (or sanitized status on failure).

## Interpretation gate

If the independent `ppu.masterClock` and PPU frame positions agree across both builds while the exposed Lua CPU-cycle APIs disagree, report a **frame clock API convention discrepancy**. The earlier observed frame deltas have exactly this possibility, but it is **not yet observed**. If PPU clock/scanline/dot disagree, investigate actual PPU clock origins and event timing; do not attribute it to rounding. If new captures conflict with old frame markers, do not normalize the earlier witness silently. Any SHA/key/end-marker mismatch fails closed. Neither diagnostic outcome establishes native NESRecomp physical-clock CPU/PPU or NMI-poll parity.

**No hardware behavior change authorized** by JP0679 alone. After bounded frame counter discrepancy is resolved or documented, return to native gameplay/modifiability milestones.
