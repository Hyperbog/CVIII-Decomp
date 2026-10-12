# JP 0553 — combined fixed-bank reset/NMI and bank0A native static recompilation

## Executable milestone

A **single** C++20 native executable now links physical-PRG instruction-site
translators for the verified Japanese fixed bank 31 and bank 0A, sharing one
explicitly modeled NES 2A03 semantics core. The compiler emits templated
6502 operations with literal operands; it does **not** execute a generic
fetch/decode loop and does **not** ship proprietary original ROM data.

The original-JP ROM is supplied privately when the native executable runs.
Both the original interpreter and compiled C++ read data and pointers from
that authenticated image. No original PRG, CHR, savestate or graphics are
committed by this work.

| Property | Original-ROM checked result |
| --- | ---: |
| Fixed bank 31 historically source-audited instruction sites | 1,564 |
| Physical instructions observed in **scripted** reset/NMI CPU trace | 403 |
| Overlap between the above two sets | 63 |
| Union of fixed-bank source and scripted-reset instruction sites | **1,904** |
| Previously compiled bank0A instruction sites | **2,357** |
| Combined statically native-compiled instruction sites | **4,261** |
| Original CPU instruction boundaries reset → first injected NMI RTI | **11,740** |
| Native/original PC, registers, flags, mapper and per-step RAM hash comparisons | **11,740 / 11,740** |
| Independent bounded bank0A room-object cases | **1,280 / 1,280** |
| Bytes of complete RAM checked per native room case | **2,048** |
| Earlier bank0A three-level pointer cases | **135 / 135** |
| Original-ROM whole-image source rebuild | **393,232 / 393,232 bytes** |
| Newly promoted strict semantic PRG bytes | **0** |

For the reset/NMI path, the original-vs-native checker also compares every
*ordered* PPU/APU/MMIO write and the final complete 2KiB RAM contents.
Passes were observed independently with GCC and Clang. The source is regenerated
from the authenticated original ROM plus the repository's original physical
`prg_fixed31.asm`; its SHA and physical instruction boundaries must agree.

## What actually executes

The C++ entry begins at the original reset-vector `$E00B`, reaches the idle
loop `$E04B`, injects one NMI, executes the original NMI vector and scheduler
through its real branch for game state `$18=0`, and finishes on the original
`RTI` return to `$E04B`. It crosses physical fixed PRG bank31 and mapper-
selected PRG bank12/13. Unlike prior Python-only boot tracing, every CPU
instruction on this bounded path is a statically generated native C++ call.

The same `jp_native_boot` binary also has a `--room` mode that executes
bank0A `$B7F7` native instructions and the original fixed `$FB96` helper,
under the five original room streams and 256 initial-state seeds. This shares
**the same C++ CPU/Bus declarations** with the reset/NMI mode. It does not
claim that reset naturally reaches the room loader.

## Strict limitations (no hidden promotion)

- The PPU status gate still uses the original checkpoint 0548 scripted model:
  first `$2002` read returns zero, subsequent reads return vblank; `$2007`
  reads and unmodeled registers return zero.
- **One NMI is deliberately injected at `$E04B`**. This does not prove that
  real hardware naturally produces the precise same interrupt boundary.
- Controller inputs are neutral, and the CPU is not cycle-accurate. APU, PPU,
  IRQ, VRC6 hardware effects, rendering, audio and gameplay frames are NOT
  equivalence-tested by this pipeline.
- A source-audited instruction is not necessarily live in gameplay. The 340
  additional scripted-trace sites do not establish natural gameplay reachability.
- The bank0A 1,365 *candidate* instruction sites remain explicitly uncertified,
  although opt-in bounded selector tests exercise a subset. The original
  3,684 unknown bytes in bank0A are still unknown.
- The generator rejects any instruction/operand overlap, bad original image,
  inconsistent source, or unsupported unmapped address. Compiled candidate
  code does not automatically increase the project's 49,504-byte strict
  certified PRG baseline or VPP 27/100.
- This is neither a complete fixed-bank semantic decompilation nor a
  boot-to-playable native game. It does not implement frame scheduling,
  dynamic input, graphics, sound, or all game states.

## Reproduction

Original commercial files are not present in public CI:

```sh
python3 JP/tools/test_native_boot_0553.py --smoke
python3 JP/tools/test_native_boot_0553.py --rom "$JP_ROM" --compiler g++
python3 JP/tools/test_native_boot_0553.py --rom "$JP_ROM" --compiler clang++
cmake -S JP/native/boot -B build/jp-native-boot
cmake --build build/jp-native-boot --parallel
ctest --test-dir build/jp-native-boot --output-on-failure
```

`test_native_boot_0553.py --rom` regenerates the original 25-bank cartridge
source, validates the fixed31 static compiler source/manifest, compiles the
combined program, checks all 11,740 individual reset/NMI instructions
including per-step 2KiB RAM digests, and checks all 1,280 bank0A room streams.
The standalone bank0A pointer/room tests remain independent regressions.

## Next completion target

Add real time/cycle/PPU scheduling to the native 2A03 platform, and apply the
same physical-bank static compilation to the remaining original game states.
Then compare a real Mesen gameplay savestate and controller sequence without
scripted PPU status or a manually injected game-state 13.
