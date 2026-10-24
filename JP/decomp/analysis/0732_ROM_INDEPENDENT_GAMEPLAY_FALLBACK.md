# JP0732 — ROM-independent 6502 gameplay fallback with native dispatch preserved

## Discovery: the fallback already exists upstream

The pinned separately licensed NESRecomp commit `2b4fcdb98c9e702be3fb365cfc645003c50b5fc1` already provides a *complete interpreter*, rather than merely a generated translator. Source: `runner/cyc/cpu6502_interp.c` (`cpu_interp_step`), `cpu6502.c` (interrupt/reset), `cyc_run.c` (instruction-boundary scheduler), `hw_machine.c`, `hw_mapper.c`, `hw_ppu.c`, `hw_apu.c`, and `cyc_native_none.c` (empty compiled-instruction dispatch).

This interpreter models NMOS 6502/2A03 instructions including the undocumented instruction forms, ordered memory accesses, DMA stalls, IRQ/NMI polling and mapper registers. NESRecomp's `hw_mapper.c` has explicit Mapper 24/26 (VRC6) reset and writes. Its dispatcher already selects `cyc_native_has(cpu.pc)` / `cyc_native_run()` only when native code is available and PRG is not modified; all other instructions use `cpu_interp_step()`. Its compiled RAM-view tier also dynamically validates a ROM-independent image rather than running stale RAM instructions.

## Actual implementation

`JP/recomp/native/rom_runtime_0732/CMakeLists.txt` builds a **full native executable** `jp_akumajou_runtime_0732` from the upstream `NESRECOMP_CYC_SOURCES` + `cyc_native_none.c` + all thirty-eight original-JP **Enhanced presentation and resource** C11 modules. It accepts original Mapper24 ROM **only at process launch**, not CMake configure or compile time. It invokes neither ROM-dependent `NESRecomp` code generator nor `tools/cyc/prepare_project.py` and does not compile any retail-ROM-specific `game_cyc*.c` files. It may optionally enable the pinned upstream SDL2 user window/audio host and the existing game-owned widescreen presenter. It does **not** vendor external NESRecomp code.

In this first backend, no unproven native instruction replacement is dispatched: `cyc_native_none.c` makes `cyc_native_has()` return false and `cyc_native_run()` inert. Every opcode executes on the interpreter with the same Mapper24 PPU/APU and CPU bus as the native recompilation. This is a **native executable running the game's original 6502 code via a 2A03 interpreter**, not a claim that those bytes have already been converted to independent native C. Existing retail-ROM recompilation and verified native block generation remain available on the separate developer-only build path; eventual verified handler injection must be designed with bank/image identity and cycle-level parity tests.

## Reproducible ROM-free developer build

```sh
cmake -S JP/recomp/native/rom_runtime_0732 -B build/rom-runtime \
  -DNESRECOMP_EXTERNAL_ROOT=/path/to/pinned/nesrecomp \
  -DJP0732_WINDOWED=OFF -DJP0732_ENHANCED=ON
cmake --build build/rom-runtime --parallel 4
# The following ROM argument is provided at execution time, NOT build time:
build/rom-runtime/jp_akumajou_runtime_0732 original-japanese.nes \
  --frames 20 --edition original --hash-out /tmp/frames.txt
```

**The original ROM remains locally owned; never add it, generated source, ROM-derived art, input logs, executable game content, or cache files to the public repository.**

## Regression gates

The Linux synthetic mapper24 workflow now builds both the ROM-specialized compiler-generated executable and the independent JP0732 interpreter without a build-time ROM argument for the latter. It compares **every observable hash field on 20 frame-by-frame snapshots** for three paths: generated code, generated executable `--interp-only`, and the new ROM-independent interpreter. It runs only on an invented VRC6 cartridge constructed by the existing JP0569 synthetic fixture tool. This is a complete instruction/hardware *integration equivalence test on that fixture*, not retail JP0718 Stage 1 parity.

Windows MSVC CI builds the same standalone executable with no ROM or code-generator input. Windowed SDL support is optional at build time; release packaging, original-game visual certification and performance remain open.

## Separation still required

- Import the authenticated original ROM from the final native install's first-launch picker and preserve the path in per-user settings. The existing Windows Alpha PowerShell launcher already supports picker and source validation; a standalone GUI installation/picker without PowerShell is later work.
- Allow **only authenticated, independently proved** native semantic handlers to replace interpreter instruction ranges, with mapper bank identity and opcode content guards, correct CPU cycle/bus timing, and explicit fallback on mismatch. **Zero handlers are wired in JP0732**; no semantic PRG coverage uplift is claimed.
- Verify original retail JP frame/dump/timing equivalence against the already supplied JP0718 MesenCE and JP0719 native full replay; the synthetic fixture does not prove it.
- Merge runtime content decoder/cache, vertical rooms and offscreen renderer fidelity; keep original mode authoritative.

This provides the first ROM-at-launch **full gameplay executable**, while leaving the interpreter-to-proven-native substitution a separately testable optimization rather than claiming fully recompiled gameplay.
VPP remains 31/100; strict original semantic PRG 49,504/262,144 bytes (18.8843%).
