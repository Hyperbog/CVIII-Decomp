# JP0678 — Mesen2 first-NMI source witness preflight

Status 2026-10-17: **owner has successfully rebuilt the complete pinned Mesen2 C++ solution** in Visual Studio 2022 Release | x64, with all 8 projects succeeding and 0 failures/skips. Native `MesenCore.dll`, `Core.lib`, `Windows.lib` and managed `Mesen.dll` are produced under the owner's independent `Mesen2-master\bin\win-x64\Release` directory. This confirms that owner-side source-level instrumentation is now feasible; it does **not** certify same-ROM replay equivalence or emulator timing parity.

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

