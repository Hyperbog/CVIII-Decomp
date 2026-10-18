# JP0679 — Dual-clock, seven-frame Mesen2 EndFrame diagnostic (preflight)

Status: **owner run pending**. The completed JP0678 report finds exact selected CPU instruction/bus/audio streams between original Mesen2 and rebuilt JP0678 Mesen2, but frame callback CPU timestamps differ `[+1,+1,0,+1,+1,0,+1]`; final END differs only `cycle:+1`. This is a bounded observational difference, **not a certified frame-timing source bug**. The separate native NESRecomp one-additional-instruction-before-NMI discrepancy remains open.

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
