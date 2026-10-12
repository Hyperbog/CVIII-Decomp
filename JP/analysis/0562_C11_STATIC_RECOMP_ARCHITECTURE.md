# JP 0562 — StarFox-style C11 static recompiler pivot

**Decision:** The new native recompilation ABI is C11. Legacy tested
C++ code is retained until independently matched, not deleted. This
copies the **methodology** from mstan/StarFoxSNESRecomp, not third-party
licensed source code.

1. `JP/native/c6502/cpu.h` defines a portable 2A03 `JpCpu` and
   `JpBus` ABI. CPU registers, 2 KiB mirrored RAM, physical VRC6 bank
   ($8000-$BFFF) and fixed banks30/31 ($C000-$FFFF) are explicit.
2. `cpu.c` implements official 6502 opcode semantics in C11
   and one interpreter-step fallback for instructions reached dynamically
   but not known to the static compiler. Unsupported I/O/PPU/APU/
   DMA/mapper writes and unofficial opcodes fail closed.
3. `opcode_table.c` comes from the project's existing 6502 instruction
   definitions (151 official instructions, not scraped raw game code).
4. `static_recompile_c_0562.py` reuses the authenticated, whole-bank
   0538 source, byte-exact reassembly, and `source_cases` historical
   evidence labels to emit C11 ahead-of-time `switch(pc)` code for
   raw0A **2357 instruction starts**.
5. Generated C, manifests, original ROM and assets remain local,
   not committed. C candidates remain marked and **blocked by
   default**; an opt-in interpreter can execute runtime-reached
   unresolved/candidate instructions, tracked separately.
6. ROM-free CTest and Python generator smoke protect the C11 path.
   Both Win/MSVC and Linux gates continue to test the existing
   C++ runtime, so the migration is incremental.

## Reproduce with privately owned authenticated JP ROM

```sh
python3 JP/tools/build_fullbank_0a_source.py \
 --rom "$ORIGINAL_JP_ROM" --out /tmp/jp-original-sources
python3 JP/tools/static_recompile_c_0562.py \
 --rom "$ORIGINAL_JP_ROM" \
 --source /tmp/jp-original-sources/banked/prg_raw0a.asm \
 --out /tmp/jp-c11-generation
cmake -S JP/native/boot -B /tmp/jp-c11-test
cmake --build /tmp/jp-c11-test
ctest --test-dir /tmp/jp-c11-test --output-on-failure
```

**Unfinished before full C migration:** integrate C codegen output
with the runtime/loader, add a hardware bus callback/interface compatible
with original VRC6/2C02 and APU events, implement authentic timer/interrupt
phasing and DMA, produce first C-generated-vs-original-CPU replay, then
port all 16 raw and two fixed banks. The initial C CPU
does not yet model cycles, PPU, APU, DMA, mapper IRQ or BRK.
Its interpreter fallback is opt-in, not a certification of guessed code.
Original source/output validation and gameplay parity remain separate.

VPP 27/100; strict PRG 49,504/262,144; existing 4,261
C++ compiled opcode sites, of which 2,357 correspond to raw0A.
No extra semantic byte claims.
