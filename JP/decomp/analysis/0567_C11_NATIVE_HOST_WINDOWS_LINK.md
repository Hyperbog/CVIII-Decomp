# JP 0567 — Windows/Linux cross-link of pure-C native host

Public ROM-free native boot CMake now builds
`jp_c6502_host_link_0567` from:
- C11 `native/c6502/main.c`, the actual private-original-ROM bounded
  native host entrypoint;
- C11 `native/c6502/cpu.c` and `opcode_table.c`;
- `native/c6502/host_link_fixture_0567.c`, an explicitly
  **synthetic** stand-in for the generator outputs.

The goal is to ensure the new host executable compiles and
links with the default Windows MSVC toolchain as well as Linux
C11 toolchains, independently of copyrighted game code.

The old C++ NES hardware and ROM-free tests remain in the same CMake.
The Linux source-level smoke separately compiles/executes the native
host with generated synthetic C units and verifies instruction limits,
physical fixed31 dispatch, RAM changes, unsupported-PC rejection
and cartridge CRC safeguard.

**Not claimed:** source-authenticated C11 original gameplay,
VRC6 game runtime, PPU/APU frames or full code provenance.
Existing 4,261 compiled C++ sites, historical 49,504/262,144
strict PRG and VPP27/100 remain unchanged.
