# JP 0564 — complete existing static-compiled opcode-site C11 code generation

The StarFox-style C transition now covers **all 4,261 previously existing
statically compiled opcode starts**, still requiring user-owned original ROM:

- **2,357** physical VRC6 raw0A source sites (992 audited,
  1,365 unproved candidates disabled by default) generated as C11.
- **1,904** original fixed31 plus scripted reset/first-NMI physical
  instruction starts, from original 8KiB source + existing recorded
  physical step execution, generated as C11. Historical 1,564 fixed
  source sites and 340 scripted-only sites are kept distinct.
- Both generators use existing original-JP evidence and source parsers;
  no copied StarFox source code or ROM images are committed.

`JP/decomp/tools/regen_c11_0564.py --rom "$ORIGINAL_JP_ROM"
--out /tmp/jp-c11-build` regenerates every original physical
source bank, C11 raw0A and fixed/boot code under `gen/`, plus a
typed C11 site census manifest. Output lives in a private build directory.
`JP/decomp/tools/static_recompile_boot_c_0564.py` validates physical PRG
offsets to avoid conflating banked CPU aliases.

`JP/recomp/native/c6502/cpu.c` now calls a compiled dispatcher for any
mapped original physical bank; the dispatcher itself is responsible for
physical-bank qualification. The C11 unit test checks a native fixed31
instruction call while bank14 is selected. An opt-in CPU interpreter
can execute paths outside any static dispatcher. Hardware access,
unknown opcodes, PPU, APU, VRC6 mapper IRQ and CPU cycles remain out of
scope or fail-closed. **No C game main loop or graphical/audio frontend
has been completed.**

CI compiles and tests C11 independently of the old C++ path.
Actual private original ROM code generation is local-only; full
original-JP game-state replay against C11 is not certified.
Strict 49,504/262,144; VPP27/100 unchanged.
