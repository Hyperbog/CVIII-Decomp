# JP0680 — Native NMI edge sampling and CPU interrupt polling (diagnostic preflight)

Status: **source review complete; privately instrumented native seven-frame run still pending** (2026-10-18). This analysis and public commit include NO ROM, ROM-derived generated source, diagnostic native EXE, CPU program-counter trace, bus traffic or original audio raw log. Private owner ZIP `JP0680-Native-NMI-Poll-Kit.zip`, SHA-256 `cd78d616b6b99517901e104688a079958d625e69b0f285b9b3514d1cec3139b7`, is delivered in chat, not checked into the public repository.

## Established input evidence

- JP0676 owner-private CPU/bus audit establishes an additional **fully completed three-cycle native instruction** followed by a discarded NMI opcode fetch and correct seven-cycle NMI entry. Original Mesen2 does not complete that extra instruction before the matched NMI handler entry. First aligned instruction-timing transition is at matched ordinal **3,300**. The first native minus original stack-push timing offset is **+2** cycles, while the relative matched instruction interval differs by **+3** cycles. Callback timestamps are not yet independently calibrated to identical physical CPU-cycle phases.
- JP0677 tested all NTSC `--align 0,1,2,3` settings: one extra native instruction on every setting, unchanged first 13 ordered audio register values, and identical `[-1] × 12, [+1]` native-minus-Mesen write time offsets.
- JP0678 instrumented Mesen2 reported a first NMI PPU assertion and CPU edge observation near original Mesen CPU cycle **86,954**. The JP0679 verified comparison demonstrates exact original-versus-rebuilt Mesen PPU frame clocks, scanline, dot and frame indices on all seven samples, plus a bounded `[+1,+1,0,+1,+1,0,+1]` CPU callback counter difference. **Do not assume Mesen and native CPU cycles share a timestamp phase.**

## Pinned source path and specific possible explanation

External `mstan/nesrecomp`, pinned commit `2b4fcdb98c9e702be3fb365cfc645003c50b5fc1`:

1. `runner/cyc/hw_internal.h::ppu_nmi_output` returns `ppu.nmi_enable && ppu.vblank`.
2. `runner/cyc/hw_machine.c::sample_nmi` calls `cpu_nmi_input(ppu_nmi_output())` at **NTSC master tick 4**. This call exists in both the ordinary tick loop and optimized `run_ticks_1_to_11` cases. DMA cycles also sample the pin.
3. `runner/cyc/cpu6502.c::cpu_nmi_input` latches `cpu.nmi_edge=1` on a new asserted edge, with `nmi_input` retaining the sampled level.
4. `runner/cyc/cpu6502.h::cpu_poll` promotes any latched `cpu.nmi_edge` to `cpu.do_nmi=1`; instruction templates call it only when they set `CYC_POLL` or `CYC_POLL_BRANCH` on the relevant cycle. Thus a newly latched edge not yet promoted before the next fetch could cause another instruction to execute. **That conditional possibility has NOT been observed in the private native core yet.**
5. `cpu6502.h::cpu_fetch` and `cpu_fetch_rom` record the opcode instruction start and perform the bus read, then return the interrupt pending bit; `cpu_interrupt(false)` processes the correct vector and seven-cycle entry contract from JP0676.

The first extra native instruction is consistent with an edge **arriving after the pertinent CPU poll**, a delayed source /NMI assertion, or a mismatch between the native and Mesen polling conventions. No source-only reasoning proves which.

## Owner-private JP0680 instrumentation protocol

The owner-only ZIP contains `jp0680_patch_native.py` (anchored patches to the four pinned source blobs in an **isolated local Git clone**), `JP0680-Run-Native-NMI.ps1` (verified ROM/ref hash, local clone, separate private headless CMake Release build, seven-frame replay and trace/audit), `jp0680_analyze.py` (privacy-safe summary of relative CPU cycles from first PPU pin rise through CPU asserted sample, latched edge, promoting `CYC_POLL`, dropped fetch, NMI entry and vector), 20 synthetic local unit tests and README. A standalone GCC C11 event logger smoke test also compiled and ran. Exact four-source anchor occurrence checks were independently verified against pinned GitHub source via GitHub API; source-file Git blobs are verified again by the owner-side patcher before modifying the clone. The owner-side Windows C11 recompile is **not yet verified**.

The source logger is dormant unless `JP0680_NATIVE_NMI_LOG` is set, and even then logs only between CPU cycles 85,000 and 90,000. A read-only diagnostic may affect **wall-clock speed**, but may not change simulated clocks, CPU/PPU registers, ROM memory or source-level timing gates. `hw.tick` is the next scheduler tick, not an independent physical time signal in optimized fast paths, and its numeric value must not be used uncritically for cross-engine cycle equality.

**Strict replay gates:** same original JP ROM SHA `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`; original JP0671 Mesen audio SHA `5aba434cc9bed36908ef97f63aecf0cd8a4c30b35db2aa4060e367553c3bf5f5`; native 7-frame frame-3 trace SHA equals JP0673 `acc54fd4d8567dd2ba7e16017dd1b5e71632f1c73f5a74f5f33870db324065e3`; first 13 ordered native audio register address/value pairs equal the original reference. If any fails, reject the timing report. Private trace and executable must NEVER be committed publicly.

**Expected owner output:** `C:\Tools\Mesen2\Private\JP0680-Native-NMI\JP0680-native-NMI-poll-audit.json`; on failure `JP0680-status.txt`. The sanitized report shows event-relative CPU cycle offsets, counts of intervening polls/fetches, relevant PPU scanline/dot and source/audio/replay provenance; it does not include ROM bytes, opcode, raw PC or full bus traces. This demonstrates native event order, but **does not alone certify the causal original-versus-native NMI mismatch**, which also requires consistent cross-core timestamp conventions and validated Mesen NMI event observation.

## Decision

If native PPU /NMI assertion precedes the extra instruction but native `cpu.do_nmi` is not promoted until its subsequent poll, investigate instruction template polling or edge scheduling, not PPU rendering. If assertion or CPU sample is late against calibrated Mesen evidence, investigate PPU output timing or the sample phase first. If the trace lacks first NMI events or native baseline replay differs, fix observation setup, not emulation. **Do not patch CPU/PPU timing or claim exact 1,100-frame CPU-cycle parity before the new owner-side evidence arrives.**
