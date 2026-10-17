# 0509 — Native C++ 2A03 CPU + VRC6 mapped headless machine, first independent source-PC check

**Purpose:** replace the previous separate Python interpreter and native mapper/IRQ demonstration with one **compiled** CPU+mapper+IRQ/controller/PPU-register bus. This is a source-ROM execution harness, **not a standalone rewritten/playable PC game**: it still requires a local original JP ROM. No copyrighted ROM material, screenshots or savestates are checked in.

## New native code

- `src/cpu_2a03.hpp/.cpp`: All 151 *official* NMOS-6502/2A03 opcodes; 2A03 ADC/SBC strictly **binary** even when decimal D is set, correct carry/overflow, 8-bit stack, JSR/RTS/RTI/BRK, zero-page index and JMP-indirect wrap, branch penalties and indexed page-cross read penalties, NMOS read-modify-write old/new stores. Unsupported unofficial opcodes raise a precise error; **not** an unofficial-opcode or per-cycle bus-transaction emulator.
- `src/native_machine_0509.hpp/.cpp`: integrates the already committed VRC6a PRG/CHR/RAM mapper and VRC6 IRQ counter with mirrored CPU RAM, controller `$4016/$4017` serial shifts, nametable CIRAM mirroring, palette, OAM register/DMA transfers, PPU `$2000–$2007` addresses and buffered reads, NTSC three-PPU-dot CPU clocks and modeled vblank NMI. **No raster pixel output, sprite zero, real APU sound, full open-bus/DMC, per-cycle CPU writes, or accurately synchronized CPU/IRQ edges.**
- `tools/native_probe_0509.cpp`: private original-JP-ROM headless CLI with bounded 20,000,000-instruction trace option. Its NES header check is **not a cryptographic identity check**; wrapper `tools/test_native_mesen_pc_0509.py` checks the exact original ROM SHA-256.
- `tests/cpu_2a03_test.cpp`: **262,144 exhaustive ADC/SBC arithmetic/flag cases** plus stack calls, BRK/RTI, NMI/IRQ flags, indirect-JMP page wrap, branching cycles, read-modify-write bus behavior and unsupported-opcode rejection. All passed with `g++ -std=c++20 -O2 -Wall -Wextra -Werror -pedantic` locally.
- `tests/native_machine_0509_test.cpp`: synthetic cartridge VRC6 PRG bank switching, controller serial reads, PPU nametable/palette buffering, and generated vblank/NMI → RAM update. This is a ROM-free **integration** test, not original-JP parity.

## Reference: exact original game PC prefix

Mesen2 v2.1.1 independently ran the original JP VRC6 retail ROM from RESET with `--frames 0 --step 16000 --trace` (private local original-ROM path); no `--set-pc`, memory mutation or fabricated interrupts. **Native C++ CPU observed the identical first 7,828 original-ROM PC addresses, one per original instruction** (hash of uppercase four-digit CPU PCs separated by newline):

| Prefix instruction count | Mesen PC SHA-256 = native PC SHA-256 |
|---:|---|
| 100 | `82ed21d964962ba4ed1a5e225f96f747d335b84c4d1135a6acfe4c2b816b32e9` |
| 3,000 | `01b4fc177cf759b44dd6b90685ae8a0600409044e1f613da0afcdac8f23318d8` |
| **7,828** | **`ac29c14add24b11f8ca4355dc2c2f0a6feb16723502ad9ee33f196d7842e8402`** |

**First divergence is instruction 7,829**: independent Mesen executes `$E012: LDA $2002` (first vblank-wait loop exit), while our approximate PPU timeline still executes `$E00D: LDA $2002` at the same ordinal. Mesen's 7,828-step CPU-cycle count is 27,401; the native loop modeled 27,402. This is **a measured 2A03/PPU initialization phase error**, not a match of CPU registers or proof of cycle-by-cycle parity. At 16,000 steps both execute in a later vblank waiting region but the phase and instruction sequence differ. The independent exact PC-prefix is intentionally limited to 7,828.

Reproduce locally:

```sh
c++ -std=c++20 -O2 -Wall -Wextra -Werror -pedantic -I JP/decomp/src \
 JP/decomp/src/cpu_2a03.cpp JP/decomp/src/native_machine_0509.cpp JP/decomp/src/vrc6_mapper.cpp \
 JP/decomp/src/vrc6_irq.cpp JP/decomp/tools/native_probe_0509.cpp -o /tmp/cviii-headless
python3 JP/decomp/tools/test_native_mesen_pc_0509.py /tmp/cviii-headless '/private/Akumajou Densetsu (Japan).nes'
# Independent original emulator (do not commit trace):
mesen-agent '/private/Akumajou Densetsu (Japan).nes' --frames 0 --step 16000 --trace /tmp/mesen-original.trace
```

**Completion ledger remains strict PRG `49,504/262,144 = 18.8843%`, VPP `26/100`, certified semantic checkpoint `0508`, pending research checkpoint `0509`, fixed physical frontier `$FB96`.** No native-runtime points awarded for an incomplete original-ROM interpreter. Required to claim a native playable port: replace original ROM source with reconstructed game routines/assets, emulate or natively implement full PPU raster/CHR/IRQ/audio behavior, and match independently recorded game frames and inputs.

## Further original-ROM NMI phase sensitivity (independent 100,000-step trace)

The above default startup (PPU dot 0) is not a calibrated reference machine state. An independent Mesen2 reset snapshot reports first frame scanline 0, dot **31**, while the native harness initialized scanline 0, dot 0. The native C++ machine now accepts an **explicit reference-test-only initial PPU dot** parameter (normal default stays 0); the private source-ROM probe accepts it as its optional fourth positional argument after trace output.

With that explicit Mesen reset-snapshot phase, the actual original-JP executable now matches **24,773 consecutive original-ROM program-counter addresses**. All ordinal 1–16,000 PCs also match. Exact normalized PC-sequence SHA-256 for the independent reference: **16,000:** `f800cb1c7067455869c102e96101ad51f81bfacac81cea3a14d7c9610b5ca19e`, **24,773:** `7f355f49db587c83c3477b15f3761c2d1317abdcadd33defcfcee30991e1a4ab`. At **step 24,774** the original Mesen2 enters `$E057` (NMI prologue) while the native model is one instruction ahead at `$E058`. This **does not** prove a generally correct PPU startup phase or true per-cycle NMI accuracy. It is a deliberately explicit, reproducible reference-fixture calibration, not a silent PPU constant modification. See `tools/test_native_mesen_pc_0509.py` for the SHA-locked 7,828 default / 24,773 phase-seeded acceptance limits; both compare PC alone rather than full registers.
