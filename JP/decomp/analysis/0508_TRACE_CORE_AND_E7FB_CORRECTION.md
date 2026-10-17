# JP 0508 — Reusable official-6502/VRC6 partial trace core and corrected E7FB indexed-pointer wrap

**Status:** Newly ROM-tested CPU/bus **infrastructure** plus a real partial-native reconstruction correction. This is **NOT** cycle-accurate NES emulation, a reset-to-frame reference trace, a completed 0508 checkpoint, or a new strict byte/VPP award. Authoritative ROM SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.

## Reusable executable rather than another one-handler interpreter

`JP/decomp/tools/trace_6502_vrc6_0508.py` supports the 151 official NMOS 6502 instruction opcodes from the repository opcode inventory, preserving 8-bit A/X/Y/stack/flags and 16-bit PC, zero-page indirect wrap, the JMP-indirect page-wrap anomaly, 2A03 binary ADC/SBC even with D set, stack JSR/RTS/BRK/RTI, mapped PRG reads, Mapper 24 `$8000` raw 16 KiB PRG writes, `$C000` 8 KiB PRG-bank writes, mirroring of 2 KiB internal RAM, PRG RAM, and event capture for common PPU/APU/VRC6 writes. Unsupported/unofficial instructions stop rather than silently approximating. RMW memory operations perform old-then-new bus writes. This is a reusable **partial synchronous instruction/bus stepper**, not a parity-certified emulator: no CPU-cycle counts, PPU scanlines/sprites, DMA stalls, IRQ generation/latency, VRC6 audio synthesis, or console open-bus/IO model.

The `test_trace_6502_vrc6_0508.py` regression initializes from **prior independently tested Phase 9/11 RAM and stack fixtures** but now executes *one single general CPU implementation* for both distinct game subsystems instead of bespoke instruction classes. It passes **272 conditional cases, 334,912 ROM-fetched 6502 instructions**:

| Path | Cases | ROM instructions/case | Independent effects compared |
|---|---:|---:|---|
| Raw `$0A:$B570`, fixed `$E7B6/$EB82`, PPU stream, exit `$B589` | 8 initial RAM seeds × 2 PPU increment modes = **16** | 10,532 | Exactly 2,048 PPU `$2007` writes per run and their increment-1/32 PPU addresses; restored `$0781`, `$19=1`, `$07A0/$07A6=0`, stack return |
| Raw `$0A:$B58C`, fixed `$E249`, raw `$0C` sound command `$6B`, temporary bank `$05`, natural return to `$B596` | **256** | 650 | Six bank-$05 instrument pointers; bank writes and sound reset; `$23=$25=$0A`, `$19=2`, `$68=0`, stack return |

**Measured local runtimes** on the provided container: 1.69 seconds for the 272-case cross-subsystem test; 1.05 seconds for the separate microtest. These measured test runtimes **are not** ChatGPT per-response wall-time allowances.

## Correction C-003: E7FB Y wrap at selector 7F/FF

Previously `JP/decomp/src/room_state_dispatch.hpp` read its second inline pointer byte at `pointer_entry+1` for every selector, as did its previous exhaustive address-lift test. Actual fixed PRG31 `$E7FB-$E813` implements:

- `ASL A` (8-bit), `STY $03`, `TAY`, `INY`;
- `PLA; STA $00; PLA; STA $01` (save original *JSR return* address, which is `$B4D0` for raw `$0A:$B4CE`);
- `LDA ($00),Y; STA $02; INY; LDA ($00),Y; LDY $03; STA $03; JMP ($0002)`.

The indexed reads share an **8-bit Y register**. For selectors `$7F` and `$FF`, doubled offset `$FE` becomes first Y=`$FF`; the following `INY` wraps to `$00` for the second byte. The first pointer byte is read from raw `$0A:$B5CF`, but the high byte comes from **`$B4D0`**, the last opcode operand of the caller's `JSR $E7FB`, *not* from `$B5D0`.

- Old incomplete C++ result: `read(B5CF) | (read(B5D0)<<8)` = `$20FB`.
- ROM-instruction result: `read(B5CF) | (read(B4D0)<<8)` = **`$E7FB`**.
- The corrected native model uses `high_addr = $B4D0 + uint8_t((selector<<1) + 2)` instead of `low_addr + 1`. First byte still uses `$B4D1 + uint8_t(selector<<1)`.

Both $7F and $FF cause this *conditional* behavior because bit 7 of selector is discarded by ASL. **Neither selector has a proved actual gameplay producer.** This is a modern code-lift correction, not a claim of a shipped original glitch or an added strict PRG dependency. `JP/decomp/tests/room_state_dispatch_test.cpp` changes its expected high-byte read and pins `$7F/$FF` to `$E7FB`; rebuilt `-std=c++17 -Wall -Wextra -Werror -pedantic`, **65,536 tests PASS**.

`test_trace_6502_micro_0508.py` independently proves the dispatcher ABI across **256 selectors × 8 saved-Y values = 2,048 ROM-fetched E7FB cases**, explicitly covering selectors `$7F/$FF`, with correct final C/Z/N and preserved synthetic parent return frame. It also checks **40,960** 2A03 binary ADC/SBC cases with decimal flag set, four indirect JMP page-wrap cases and BRK/manual NMI stack/vector examples. **75,781 CPU instructions** total under this microtest. This is not exhaustive testing of all instruction/flag combinations.

## Verification and conservative completion ledger

Run from repository root, with immutable JP ROM locally supplied (not committed):

```sh
python3 JP/decomp/tools/test_trace_6502_vrc6_0508.py 'Akumajou Densetsu (Japan).nes' JP/decomp/analysis/0508_trace_core_report.json
python3 JP/decomp/tools/test_trace_6502_micro_0508.py 'Akumajou Densetsu (Japan).nes' JP/decomp/analysis/0508_trace_core_micro_report.json
g++ -std=c++17 -O2 -Wall -Wextra -Werror -pedantic JP/decomp/tests/room_state_dispatch_test.cpp -o /tmp/room_state_dispatch_test
/tmp/room_state_dispatch_test 'Akumajou Densetsu (Japan).nes'
```

The general harness should be compared with a trusted reference-emulator CPU/mapper/PPU trace before reference parity can be claimed or VPP increased. Use it next to trace RESET through the *live* first-level NMI progression and the state-two carry gate, rather than performing more custom partial CPU snippets. The earlier 0508 bulk 32-KiB scan independently proves the reset clear `$18=$19=$68=$07A0=$07A6=0`; the **complete** reset-to-selector-$0C progression remains OPEN.

**New strict PRG bytes: 0**; authoritative **49,404/262,144 (18.8461%)**, **VPP 24/100**; last completed checkpoint **0507**, fixed PRG31 frontier `$FB96`. Do not rewrite RESUME_STATE for research-only code or its correction. Source of truth is original JP ROM, not the older address-lift model.
