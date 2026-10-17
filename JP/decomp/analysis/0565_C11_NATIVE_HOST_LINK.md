# JP 0565 — C-only native executable with ROM-derived ahead-of-time generation

The C11 migration now offers a standalone original-ROM-linked executable
instead of only a C semantics library:

```sh
python3 JP/decomp/tools/regen_c11_0564.py --rom "$ORIGINAL_JP_ROM" --out /tmp/jp-c11
cmake -S JP/recomp/native/c6502 -B /tmp/jp-c11-build \
 -DJP_C6502_GEN_DIR=/tmp/jp-c11/gen
cmake --build /tmp/jp-c11-build
/tmp/jp-c11-build/jp_c6502 "$ORIGINAL_JP_ROM" --steps 10000
```

The C host `native/c6502/main.c` loads the original Japanese user-supplied
ROM, checks its iNES shape and expected CRC32 $2E93CE72 as a **secondary
accidental-mismatch guard** (the Python codegen requires full SHA-256),
reads the original reset vector, routes each guest instruction through
the physical-bank-qualified original raw0A and fixed/boot compiled C
dispatchers, and optionally interprets dynamically reached but uncompiled
instructions when `--fallback` is explicitly set.

The C runner outputs a bounded CPU-state/compiled/interpreted count
or terminates with a nonzero status on the first unresolved PC, invalid
opcode or unavailable NES hardware operation. **It does not emulate
PPU/APU/VRC6 peripherals, CPU/PPU cycle timing, display frames, input
or audio**, and is not claimed to run complete gameplay.

The independent ROM-free test
`tools/test_c6502_native_host_0565.py --smoke` links C-generated
synthetic bank code + synthetic fixed31 instructions and checks:
real instruction execution, reset vector, bounded completion, correct
RAM effects, explicit unsupported-PC rejection and ROM CRC32 guard.
CMake supports explicit `-DJP_C6502_HOST_ONLY=ON` when the user
has no original ROM, matching StarFox's host-only versus local game
code separation.

The existing C++ NES hardware/runtime tests remain intact; the C
native runner is a **parallel replacement path under migration**, not
a silent deletion of established tests.

VPP27/100, strict 49,504/262,144, existing 4,261 static
instruction sites; no new gameplay/parity credit.
