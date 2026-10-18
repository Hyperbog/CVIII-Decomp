# JP0678 — Mesen2 first-NMI source witness preflight

Status 2026-10-17: **owner has successfully rebuilt the complete pinned Mesen2 C++ solution** in Visual Studio 2022 Release | x64, with all 8 projects succeeding and 0 failures/skips. Native `MesenCore.dll`, `Core.lib`, `Windows.lib` and managed `Mesen.dll` are produced under the owner's independent `Mesen2-master\bin\win-x64\Release` directory. This confirms that owner-side source-level instrumentation is now feasible; it does **not** certify same-ROM replay equivalence or emulator timing parity.

## JP0678 second-stage bounded frame differential (owner aggregate, 2026-10-17)

Owner uploaded `JP0678-Mesen-frame-delta.json` (schema `JP0678-private-frame-marker-delta/v1`). The owner-side delta analyzer verified **both** the pinned original JP0673 seven-frame Mesen witness SHA-256 and the rebuilt/instrumented witness SHA-256 from the prior baseline report. It establishes:

- Seven `JP0673_FRAME` markers, ordered: **instrumented-minus-original CPU cycle deltas `[+1,+1,0,+1,+1,0,+1]`** (no constant offset).
- `JP0673_END`: `cycle` differs by **+1**; `frames`, `exec`, `bus`, and `audio` END fields each differ by **0**.
- Earlier baseline comparison already found **30,070/30,070 `JP0673_EXEC` records exact**, all selected `JP0673_BUS` records exact and **19/19 `JP0673_AUDIO` records exact**.
- No raw ROM bytes, PC/opcode data or full CPU witness have been publicly included.

**Interpretation:** The observed residual is confined to an alternating **0/1-cycle frame/end callback clock value**, with no recorded instruction/bus/audio stream divergence between the two Mesen2 builds. Its repeating `+1,+1,0` pattern is *consistent* with reporting a fractional NTSC PPU frame boundary in integer CPU clocks (the nominal NTSC frame spans about 29,780⅔ CPU cycles). This is a **clock API/callback-phase hypothesis**, not a proof that the frame engine or its NMI edge timing matches the authenticated original Mesen2 EXE. In upstream source `NesPpu::SendFrame` calls `ProcessEvent(EventType::EndFrame)` during PPU execution; the JP0678 compatibility Lua API directly exposes `NesCpu::GetCycleCount()`, whereas the original authenticated EXE's `emu.getCpuCycleCount` implementation has not been source-verified. That API semantic difference alone could explain a one-cycle callback discrepancy, but still needs a common-clock calibration to prove.

**Decision:** classify JP0678 Mesen stage A as **instruction/selected-bus/audio equivalence PASS; strict frame/end cycle equivalence FAIL, bounded ≤1 cycle**. Keep `eligible_for_nmi_edge_cycle_comparison=false` and `do_not_certify_native_cpu_parity=true`; do **not** massage frame values, modify CPU timing or declare original EXE physical NMI-edge equivalence. Do not repeat the full seven-frame capture merely to observe the same bounded frame delta. If strict cycle parity remains a required milestone, instrument and align the original/NESRecomp interrupt edge and poll signals on a demonstrably common CPU-cycle convention; otherwise archive this as an outstanding timing-fidelity item and resume modifiable native game system work.

## JP0678 post-hotfix baseline comparator: CPU/bus/audio exact; frame/end DIFFERENT (owner aggregate, 2026-10-17)

The owner submitted `JP0678-Mesen-baseline-equivalence.json` (schema `JP0678-mesen-build-baseline-equivalence/v1`), generated locally by the original-vs-rebuilt CPU witness comparator. This verifies original reference SHA-256 `a063546419c9c4c86a24cde00c19af4517f935cd5c6d9f3892f3f291f60791bc` and compares an instrumented witness SHA-256 `1f13d7d5f45e1eb319ced108d4faa96a1619b917fedc5311460f26444e64ee8f`.

| Measured stream | Original count | Instrumented count | Exact |
| --- | ---: | ---: | --- |
| `JP0673_EXEC` instructions | 30,070 | 30,070 | **true** |
| `JP0673_BUS` selected bus sequence | not included in aggregate | not included | **true** |
| `JP0673_AUDIO` events | 19 | 19 | **true** |
| `JP0673_FRAME` marker sequence | seven-frame test | seven-frame test | **false** |
| `JP0673_END` marker | — | — | **false** |

The owner's report explicitly sets `eligible_for_nmi_edge_cycle_comparison=false` and `do_not_certify_native_cpu_parity=true`. Do **not** relax these gates without further evidence. Matching instruction/bus/audio streams do not establish frame callback timing or internal NMI phase equivalence. The owner's uploaded report omits the differing FRAME/END values and therefore cannot distinguish a fixed endFrame callback phase offset, an API clock semantics discrepancy, or a genuine frame clock divergence.

To avoid rebuilding or recapturing, an owner-local `JP0678-Mesen-Frame-End-Delta-Audit-Kit.zip` reads only the two already captured CPU witnesses, requires the reference SHA-256, can verify the rebuilt witness against the prior report, and reports seven sanitized frame cycle offsets plus END marker field/count differences (no PC/opcode, bus values, ROM bytes or absolute CPU cycle series). Eight synthetic local tests passed; **the owner's actual offsets have not yet been measured**. The diagnostic ZIP and raw traces remain private/off Git. Await `JP0678-Mesen-frame-delta.json` before attributing cause or changing hardware timing code.

## Owner capture finding and Lua API hotfix (2026-10-17)

Owner privately uploaded three JP0678 files: `JP0678-Mesen-7frame-private.log`, `JP0678-Mesen-NMI-private.log`, and `JP0678-Mesen-NMI-status.txt`. The verified ROM and instrumented Windows Release x64 MesenCore hashes prove the instrumented core **launched**, but `MesenProcessExitCode: -1` and `INCOMPLETE_NOT_PROVEN` mean the seven-frame CPU witness did not finish. The CPU log contains `JP0673_READY v1` then immediately `JP0673_INVALID cycle_api_failed_or_regressed` before its BEGIN marker. The NMI instrumentation nonetheless emitted **two** assertion/CPU-edge/eligibility/acceptance groups. Those cycles are preliminary *instrumented-run-only* readings, not a verified match to the original reference; no parity inference from them.

**Verified cause of immediate witness failure:** The original JP0673 Lua witness begins with `local ok,c=pcall(emu.getCpuCycleCount)`. The uploaded pristine `Mesen2-master.zip` source's `Core/Debugger/LuaApi.cpp::GetLibrary` does not register `getCpuCycleCount` at all, although its `NesCpu::GetCycleCount()` C++ accessor exists. The original authenticated EXE accepted the API; this newly rebuilt **upstream source** does not. Earlier identification of the source checkout commit does **not** establish that it exposes the exact original EXE Lua API.

An owner-only diagnostic compatibility kit `JP0678-Mesen-Lua-Clock-API-Hotfix.zip` adds **only** a NES-only, read-only `emu.getCpuCycleCount()` LuaApi binding to the *existing instrumented copy*, returning `NesConsole::GetCpu()->GetCycleCount()`. No CPU/PPU timing or state is adjusted. Patch requires exact original SHA-256 for `Core/Debugger/LuaApi.cpp` and `.h`, JP0678 instrumentation markers, and no prior patch; it backs up both files and refuses editing `Mesen2-master`. Seven local source/patch tests pass. **Windows rebuild and replay remain pending**; the API semantics must still pass the exact original-vs-rebuilt JP0673 instruction/bus/audio/frame clock witness gate. If they differ, fail closed rather than realigning timestamps.

Owner action: run `jp0678_add_clock_api.py --root C:\Users\hyper\Downloads\Mesen2-JP0678-NMI`, rebuild its `Mesen.sln` Release | x64, rerun the existing `JP0678-Run-Mesen-NMI.ps1`, and run the baseline comparator **only if** JP0673_END frames=7 is present. Upload sanitized status/comparison and small NMI log privately; never publicize raw traces, ROM, or compiled binaries. This fix is **not** an NMI parity or root-cause fix.

## Rationale and scope

JP0676's private seven-frame native bus classification confirms **one additional completed native three-cycle instruction** before a valid **discarded NMI fetch**. JP0677's native `--align 0,1,2,3` sweep did not remove that completed instruction or change the first 13 audio event cycle offsets. The causal question is whether the PPU NMI output edge, CPU sample/edge latch or subsequent instruction-end poll happens on a different cycle in Mesen2 versus the pinned NESRecomp CPU. No runtime CPU timing, APU write timestamp or audio value adjustment is justified on the current evidence.

## Mesen2 stage A: owner-local isolated instrumentation

Package `JP0678-Mesen-NMI-Source-Instrumentation-Kit.zip` provides:

- `jp0678_patch_mesen.py`: requires SHA-256-exact original `Mesen2-master/Core/NES/NesCpu.cpp` and `NesPpu.cpp`, copies source to a **separate** `Mesen2-JP0678-NMI` tree, refuses existing destination, then injects a private read-only inline logger in exactly those files. It never touches the authenticated original binary or ROM.
- `JP0678-Run-Mesen-NMI.ps1`: executes the rebuilt source-copy testRunner for **7 original-JP neutral-input frames** with the unchanged `mesen_jp0673_cpu_witness.lua`, checks the original ROM SHA and full end marker, and writes source-NMI events only when the `JP0678_MESEN_NMI_LOG` environment variable is set. Files stay in `C:\Tools\Mesen2\Private\JP0678-Mesen-NMI`.
- `jp0678_check_mesen_baseline.py`: compares the rebuilt/instrumented Mesen witness with the previous original JP0673 Mesen CPU log (pinned SHA-256 `a063546419c9c4c86a24cde00c19af4517f935cd5c6d9f3892f3f291f60791bc`); requires exact instruction, selected bus, audio register and frame/end tuples. Only aggregate booleans/counts/hashes enter its output. Any mismatch **blocks causal inference** from the newly built emulator.
- 16 Python tests passed; a C++17 compile-and-run smoke test confirmed the local logger writes a single newline-delimited record to the environment-selected path. **No Windows C++ rebuild or owner runtime capture has yet run with the instrumented source copy.**

Logged Mesen events: PPU VBlank NMI assertion (including PPU scanline/cycle), NMI assertion by enabling $2000 during VBlank, CPU end-cycle NMI edge latch, one-cycle-later eligibility latch, and CPU decision to call IRQ() after an instruction. Capture is gated to CPU cycles 76,000..171,000; source and output retain private clock information but contain no ROM bytes or program counters in the small event trace. These are *not* physical motherboard oscilloscope timestamps: Mesen's `_state.CycleCount` and NESRecomp's `hw.cycles` have differing callback phases.

**Stage B still needed:** instrument pinned native NESRecomp `ppu_nmi_output` transition, `sample_nmi()/cpu_nmi_input()`, `cpu_poll()`, and rejected `cpu_fetch()` using an independently replay-verified native build. Only **after** Mesen stage A exact equivalence and native stage B matching event streams are observed can JP0678 distinguish PPU output timing from CPU polling timing. No C11 timing source patches or third-party cores have been published. Original ROM, private CPU witness and diagnostic DLL/EXE remain off public Git.

Owner Windows next action: use ZIP README, build `Mesen2-JP0678-NMI\Mesen.sln` Release | x64, run controlled testRunner, run original-vs-instrumented Mesen witness comparison, and upload only `JP0678-Mesen-NMI-status.txt`, `JP0678-Mesen-baseline-equivalence.json`, and the small `JP0678-Mesen-NMI-private.log` **to the private conversation**.

