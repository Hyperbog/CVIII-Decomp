# 0552: whole-bank static native 6502 translation (actual code, limited scope)

## Why this is different from previous source classification

The source in `JP/native/bank0a/generated/bank0a_compiled.cpp` is a **real compiled
C++ statement for each decoded original instruction start** in the Japanese
16-KiB physical VRC6 PRG bank `$0A`. It is not an iNES byte dump; no opcode
is decoded from program ROM at runtime. A compiler turns each static PC case
into host machine code.

Every source instruction site has an explicit **evidence gate**. The default
mode allows 992 previously audited 6502 instructions (2,162 original bytes)
only. It rejects the 1,365 further *candidate* instruction sites (2,910
original bytes) unless an explicitly bounded test opts in. Non-code, tables,
and unknown positions **fail closed**. The remaining 11,312 bytes of the bank
are **not** represented as executable host instructions and are *not* proof of
recovered semantics. The prior 3,684 fully unknown bytes are not solved by
this work. This does NOT make the bank fully decompiled or the game playable.

The compiled C++ uses the platform-independent 6502 semantics in
`static_6502.hpp` and an explicit RAM/banked-ROM bus. Decimal-mode behavior
uses the Ricoh 2A03 binary ADC/SBC convention; PPU/APU and CPU cycle timing
are not implemented. Each opcode/site is compiled ahead of time through C++
`switch` specialization, rather than interpreting runtime 6502 opcodes.

## Independently verified original behavior

Original-JP ROM SHA-256:
`958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`

Physical bank 0A SHA-256:
`1460df577d44e114c64fdf34a8837629765f3f6a93d45796fdf81e5ffacb5ed8`

1. A real **original-6502 opcode interpreter** executes original `$B7F7`
   room-loader bytes and the original `$FB96` and `$E2D0` bank-switch helper.
   Independently statically compiled C++ executes the bank's corresponding
   original instructions and a bounded native translation of the original
   helper; no ROM-byte decoding occurs in the native CPU hot path.
2. All **five original indexed room streams × 256 varying register/flag
   initializations = 1,280 cases** pass full **2,048-byte RAM equality**,
   final A/X/Y/SP, tested C/Z/N flags, ordered physical-bank-0E reads and
   values, and mapper-write counts. This includes real 6502 stack memory
   side effects of nested JSR/RTS in `$FB96`.
3. The original `$801E` three-level selector, currently a *candidate* in
   the 0538 atlas, is explicitly opted in **only for 135 bounded, structurally
   verified selector paths**. Each leaf pointer matches the original 6502
   interpreter and independently decoded pointer hierarchy. This is local,
   conditional proof, not gameplay reachability or unconditional certification.
4. GCC and Clang compile the entire 2,357-case native bank module and both
   pass the authenticated-ROM comparisons. CTest and ROM-free tests require
   neither original game bytes nor external emulator software.
5. The generator verifies that the original source **reassembles to exactly
   the original 16,384-byte bank**, and rejects wrong original-ROM hashes,
   non-matching code widths, overlapping sites, and unknown opcodes.

### Reproduction

```
# CI and developer machines without commercial ROM:
cmake -S JP/native/bank0a -B build/bank0a -DCMAKE_BUILD_TYPE=Release
cmake --build build/bank0a --parallel 2
ctest --test-dir build/bank0a --output-on-failure
python3 JP/tools/test_static_bank0a_0552.py --smoke

# Optional developer-supplied authenticated original Japanese ROM:
python3 JP/tools/build_fullbank_0a_source.py --rom "$JP_ROM" --out /tmp/jp-original-source
python3 JP/tools/static_recompile_bank0a.py --rom "$JP_ROM" \
  --source /tmp/jp-original-source/banked/prg_raw0a.asm --output /tmp/jp-native-generated
cmp JP/native/bank0a/generated/bank0a_compiled.cpp /tmp/jp-native-generated/bank0a_compiled.cpp
python3 JP/tools/test_static_bank0a_0552.py --rom "$JP_ROM" \
  --source /tmp/jp-original-source/banked/prg_raw0a.asm --compiler g++
python3 JP/tools/test_static_bank0a_0552.py --rom "$JP_ROM" \
  --source /tmp/jp-original-source/banked/prg_raw0a.asm --compiler clang++
```

No retail-ROM, raw physical bank binary, CHR, Mesen savestate, or ROM-sized
byte payload is distributed in this source package.

## Completion status / next integrated milestone

- **Achieved:** native C++ translation of all 2,357 existing structurally
  decoded bank0A instruction starts, evidence-gated. Entire audited executable
  room-loader path passes 1,280 full-RAM CPU and mapper comparisons.
- **Not achieved:** execution parity for every instruction/start in the static
  map; 1,365 candidates still unproven; 3,684 original bytes still unknown;
  cross-bank original scheduler/IRQ/PPU/APU frame behavior; playable game.
- **Next:** extend the *same* static translator to the fixed scheduler and
  bank00/bank0E dependencies, replace bounded helper intrinsics with
  translated CPU machine code where possible, then compare genuine Mesen2
  frame traces from reset through gameplay. The current byte classification
  and strict certification percentages are unchanged.
