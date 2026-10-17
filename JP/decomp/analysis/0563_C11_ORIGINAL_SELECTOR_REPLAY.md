# JP 0563 — original Japanese bank0A → generated C11 → real CPU parity

New ROM-backed `JP/recomp/native/c6502/raw0a_driver_0563.c` can execute
`bank0a_compiled.c` regenerated locally by the 0562 C11 source emitter.
The C runner reads a user-owned original cartridge, maps the original
physical VRC6 bank raw0A at CPU $8000–$BFFF, initializes original
zero-page stage selectors, sets up an authentic RTS return stack,
and executes the $801E–$8046 selector *through statically emitted C*.
It rejects an unresolved PC, unsupported hardware access, missing RTS
return, or **any interpreter fallback** during this bounded test.

`test_c6502_regen_0563.py --rom "$ORIGINAL_JP_ROM"`:
1. Authenticates 393232-byte original Japanese ROM SHA-256.
2. Regenerates all 25 whole-original-cartridge source modules and checks
   exact bank reconstruction.
3. Emits C11 for 2357 bank0A opcode sites (candidate execution enabled
   ONLY within bounded 135-case local selector test).
4. Compiles generated C together with 2A03 C11 CPU core into an executable.
5. Runs all original 135 stage/middle/leaf selectors.
6. Compares C results to source-typed tables **and independently executed
   original 6502 opcodes**.
7. Uses a temporary directory. Neither ROM nor generated commercial
   source code is checked into Git.

Public CI runs `--smoke` instead, which compiles the source emitter
against artificial test rows and rejects malformed evidence classes
and unsorted instruction starts. The authenticated original-run test
requires the user-owned ROM and is not run by ROM-free GitHub CI.

**This provides a compiled C11 proof-of-concept for an existing
source routine, not a playable native game.** Unproved candidate code,
unmodeled 2C02/APU/VRC6 behavior, real IRQ timing and full-bank
gameplay reachability remain open. Strict PRG 49,504/262,144, VPP
27/100, existing 4,261 C++ opcode starts unchanged.
