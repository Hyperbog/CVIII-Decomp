# Checkpoint 0508 — bounded controller-origin state transitions from original RESET

**Status: PROVISIONAL, not an original console frame trace or completed checkpoint.** Japanese Akumajou Densetsu ROM SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`, mapper 24 / VRC6a, exact original ROM instructions, zero strict-new PRG bytes and unchanged VPP **24/100**. Last completed machine recovery checkpoint **0507** and fixed-bank frontier **$FB96** remain unchanged.

## What this adds to the 32-KiB and RESET/NMI bulk work

The first bulk pass captured a real reset-to-idle instruction path and 450 manually injected, zero-input NMIs. Those runs stopped at `$18=$00,$19=$01`, which did **not** prove room-state `$0C/$0D` liveness. This extension adds a reusable **NES controller `$4016/$4017` serial-bit bus model** to the same `JP/decomp/tools/trace_6502_vrc6_0508.py` generic 151-official-opcode ROM instruction interpreter. At `$4016` writes, the strobe is latched/reset; later `$4016/$4017` reads shift A, B, Select, Start, Up, Down, Left and Right in that order (bits 0–7), then return the modeled post-eight-bit 1. This is a **deterministic CPU-visible input model**, not an electrical open-bus/timing implementation.

The new `JP/decomp/tools/test_controller_start_nmi_0508.py` executes genuine JP ROM RESET instructions from `$E00B` to idle `$E04B` under synthetic `$2002=$80` during the two reset wait phases. It then supplies `$2002=$00`, injects 300 NMIs at the ROM's NMI vector `$E057` under each of **three artificial main-loop spacing policies** (0, 12 or 384 genuine instructions per NMI), disables IRQ and supplies a one-button Start press to controller one **only for artificial NMIs 2–4**. The game itself reads the input through its original fixed-controller helper; the test does not assign `$18`, `$19`, `$68` or `$F8` manually.

### Reproducible exact observation in each schedule

| Manual NMI index | Controller state | Original RAM `$18` | Original RAM `$19` | Original `$F8` |
|---:|---|---:|---:|---:|
| RESET end | released | `$00` | `$00` | reset zero |
| 1 | released | `$00` | `$01` | `$00` |
| 2 | Start pressed | `$00` | `$02` | `$10` |
| 3 | Start held | `$00` | `$03` | `$00` |
| 4 | Start held | `$00` | `$04` | `$00` |
| 261 | released | `$00` | `$00` | `$00` |
| 262 | released | `$00` | `$01` | `$00` |

All intermediate tested NMIs leave `$18=$00` and `$68=$07A0=$07A6=$00`. The source instruction trace distinguishes a new Start press `$F8=$10` at NMI2 from the held repeat `$F8=$00` at NMI3. At artificial NMI261, the observed selector returns to 0, and NMI262 increments it to 1. **No tested schedule reaches `$18=$0C` or `$18=$0D`.** This observation is not a global impossibility proof; the artificial runtime lacks real graphical/gameplay scheduling and other controller behaviors.

### Measurement

| Idle instructions/NMI | Manual NMI count | Exact original instructions including reset |
|---:|---:|---:|
| 0 | 300 | 529,829 |
| 12 | 300 | 533,429 |
| 384 | 300 | 645,029 |
| **Total** | **900** | **1,708,287** |

32KiB raw bank-$0A/$0E + full 256KiB direct-writer encoding census were earlier discovery, not represented by this 1.7M instruction total. The trace intentionally leaves VRC6 audio/IRQ, PPU scanline/timing, true NMI scheduling, rendering, open bus and game-play inputs beyond the Start pulse unsupported. An instruction count is **not** a count of different verified PRG bytes.

**Regressions rerun against the exact original ROM with the new bus model:** `test_trace_6502_vrc6_0508.py` 272 cases / 334,912 instructions; `test_trace_6502_micro_0508.py` 2,048 E7FB cases + 40,960 2A03 binary ADC/SBC arithmetic cases; `test_reset_nmi_trace_0508.py` 450 synthetic NMIs / 1,599,939 instructions. These are repeated reference tests of the same audit tools, not additional PRG/VPP credit. The 65,536-case corrected native E7FB C++ address regression is already committed separately.

## Unclosed dependency and next work

The real remaining gate is **R-001**: an actual input/PPU/IRQ game-state trace that produces the first-level `$18=$0C` and a valid `$19=$13` predecessor, and subsequently the `$0D` room-state loader, with intervening RAM producers/mapper writes preserved. The tested Start button only establishes a reachable *synthetic* `$18=0` title-state chain; it does **not** validate game-world live room-index `$07A0=0..4` or the bank-$0A state-two `$B597/$B6A4` carry gate (**R-002**). Nor does the partial mapped CPU input bus establish native CPU/PPU/audio frame parity (**R-006**).

Improved next M1 capability should be hardware-timed PPU/NMI/IRQ and authentic captured controller stream or reference emulator trace, then apply existing 0508 room loader structural manifest and corrected E7FB source to the whole bank-$0A/$0E semantic ledger. No speculative byte promotions.

Reproduce:

```sh
python3 JP/decomp/tools/test_controller_start_nmi_0508.py '/path/Akumajou Densetsu (Japan).nes' JP/decomp/analysis/0508_controller_start_nmi_report.json
python3 JP/decomp/tools/test_trace_6502_vrc6_0508.py '/path/Akumajou Densetsu (Japan).nes' /tmp/trace_regression.json
python3 JP/decomp/tools/test_trace_6502_micro_0508.py '/path/Akumajou Densetsu (Japan).nes' /tmp/trace_micro.json
python3 JP/decomp/tools/test_reset_nmi_trace_0508.py '/path/Akumajou Densetsu (Japan).nes' /tmp/reset_regression.json
```

**Accounting: 0 new strictly verified PRG bytes (cumulative 49,404 / 262,144 = 18.8461%); VPP still 24/100; machine recovery checkpoint remains 0507; fixed PRG31 frontier $FB96.** Research scripts, report and notes are safe to commit; do not commit the raw ROM.
