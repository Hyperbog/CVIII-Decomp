# JP0742 — Working ROM-private original/native replay environment

**Scope:** establish runnable original Japanese MesenCE and the current opt-in
NESRecomp engine, without owner retesting, private media uploads to GitHub,
new game logic, or source-certification credit.

## Executable availability: RESOLVED

The container cannot resolve github.com directly, so source cloning and
ordinary release downloads fail here. Authenticated GitHub Actions connector
artifact retrieval was successful:

| Component | Evidence / provenance | Result |
| --- | --- | --- |
| MesenCE original emulator | nesdev-org/MesenCE 2026-10-07 "Build Mesen" run `37624076912`, Linux clang **NativeAOT** artifact `11483797471`; local executable SHA-256 `f02685dafe559addf8dd8d769621a89777137d0c4592436aed65694a7e740676` | Linux ELF starts, ROM recognized as NES Mapper24/KONAMI-VRC-6, headless Lua works |
| Previous native uninstrumented engine | GitHub Actions run `40078515139`, artifact `12554585870` | 64-frame and 9,610-frame original-mode replay complete, using archived JP0719 button file |
| Current trace-enabled native engine | ROM-free PR workflow `.github/workflows/jp0742_private_replay_engines.yml`, first successful run `40079499511`, artifact `12554975419`; local ELF SHA-256 `8113593fcef28382b096883acbb5a4df0dc9afcc944ac803876eb8d82d59e865` | COMPLETE native CPU bus-write trace, zero exit |

The standard MesenCE Linux x64 artifact requires .NET 10 (not installed);
the **NativeAOT** artifact has no separate .NET runtime dependency.
The MesenCE GUI requires an X display, but its built-in `--testRunner`
executes ROM and Lua headlessly.

**Correct unattended MesenCE invocation**, using the existing owner ROM
locally and the canonical trace Lua:

```sh
JP0740_INPUT_TSV=/private/JP0718-original-input.tsv \
JP0740_ANCHORS_TSV=/private/JP0740-verified-anchors.tsv \
JP0740_TRACE_TSV=/private/JP0742-mesen-original-writes.tsv \
  /private/Mesen --testRunner --testRunnerTimeout=240 \
    --debug.scriptWindow.allowIoOsAccess=true \
    /private/mesen_jp0740_original_write_trace.lua \
    "/private/Akumajou Densetsu (Japan).nes"
```

The current MesenCE core exposes **`emu.stop(0)`**, not `emu.exit(0)`
(despite outdated command-line help text). The canonical JP0740 Lua
recorder was updated to `emu.stop` with exit code 0 only for COMPLETE;
failed anchors stop with exit code 1.

## Native original-mode replay: ACTUALLY EXECUTED

Ran the installed CI-built opt-in native tracer with the original
SHA-256-verified Japanese ROM and the owner-recorded JP0719 input
schedule SHA-256 `27b502aaeca9f5d5381f9f9a812cc188043d083d8ac8b3a89bc40c70f3c30196`:

```sh
JP0740_NATIVE_TRACE_TSV=/private/jp0742_native_writes.tsv \
  /private/jp0742_native_trace_engine \
    "/private/Akumajou Densetsu (Japan).nes" \
    --headless --frames 9610 --edition original \
    --input /private/JP0719-original-controller-input.input
```

Result: exit **0**; `END\tCOMPLETE\t9901`; **9,901**
physically mapped original-JP native CPU-bus records (events from frames
9,370–9,600). Saved output local SHA-256
`f7ef7c1855f5cc6828666749f122b770fa9f14c1aada68f8d4958235cb762f0c`.

Actual native mapped producer PCs:
- $62 mode **2**, bank $0E:$936E, physical PRG offset $3936E:
  231 writes in this window;
- $62 mode **1**, bank $0E:$8748, physical offset $38748:
  66 writes;
- $62 mode **0**, bank $0E:$877D, physical offset $3877D:
  8 writes;
- player action $0565: 20 writes, spread across 11 physical PC sites;
- player Y $041C: 236 writes, mainly $0E:$870F, some fixed $FEFE;
- vertical speed $0520: 201 writes;
- coarse scroll $63: one write at fixed $D348, PRG $3D348.

These are **new authentic native runtime instruction observations**, not
yet first-*incorrect*-write findings. Do not conflate this JP0742 executable
with the older owner-played JP0719 native build.

## Original MesenCE replay: RUNNABLE, ARCHIVE EQUIVALENCE FAILED

The original MesenCE build successfully loads and executes the original
Japanese ROM via CLI. Its Lua testRunner and restricted filesystem I/O
were independently verified; its initial recorded controller polls
at absolute frames 2–8 reproduce the archived CPU-cycle values exactly.
A historical input-cycle audit found the first detected poll-cycle
difference at **absolute frame 618 / archived local frame 617**:
new replay 18,372,181 versus original 18,372,182 (**-1 CPU cycle**).

For a separate comparison at real archived RAM snapshots, the replay
matched **both original RAM and original CPU cycle** at local frames
**24** and **264**. By local frame **416** (after historical first START
hold at about absolute frames 394–400), the replay differed:
original cycle 12,415,968 vs replay 12,415,967, and watched RAM
state different. At local frame **664** and **832**, further RAM and
cycle differences appeared.

A complete 9,600-local-frame *attempt* with the JP0740 source CPU-write
observer correctly **refused the historical original anchor at frame
9,376**, exiting code 1:
- recorded original source CPU cycle **279,249,268**;
- new source replay CPU cycle **279,249,248** (-20);
- mode $62 original $02, replay $00;
- player Y $041C original $4F (79), replay $34 (52);
- first recorded source `ANCHOR_FAIL`, then
  `END\tANCHOR_MISMATCH\t999\t9376\t0`.

**IMPORTANT:** A failed original replay is not an authenticated source
CPU-write trace, even though its observed writes are physically mapped.
The prior ROM state is reproduced through at least frame 264, but not
through frame 416. Do not auto-shift the controller schedule to obtain
a favorable state match. Original archive event recording used
`emu.getInput()` during `InputPolled`; the new runner injects with
`emu.setInput()`. These have different data paths and the full
sampled 8-bit $4016 serial read phases were not recorded historically.
Investigate actual MesenCE polling/latching, platform settings,
initial controller configuration, and deterministic emulation options.

## Current status and next proof gate

1. **Executable acquisition blocker is solved for both emulators.**
   A native runtime and original MesenCE headless Lua can run on this host.
2. The original Mesen replay **has not** reached all historical RAM/cycle
   anchors. The first known failing RAM checkpoint is frame 416,
   rather than an unwarranted inference at frame 9,576.
3. Fix original input replay equivalence using verified emulator
   input-poll mechanics and exact CPU/PPU state, not an arbitrary
   one-frame schedule adjustment.
4. Re-run original JP0740 CPU-write capture to completion, compare it with
   completed native JP0742 write trace, align mapped PCs and bus
   phases in `jp0741_first_write_compare.py`.
5. Only then certify the first actual incorrect store to $0565, $0520,
   $041C or $62 and consider a bounded game-code correction.

Last personally tested owner checkpoint **JP0722**.
**No gameplay patch, no source byte admission. VPP 31/100; strict
PRG 49,504 / 262,144 bytes; baseline 0508.**
