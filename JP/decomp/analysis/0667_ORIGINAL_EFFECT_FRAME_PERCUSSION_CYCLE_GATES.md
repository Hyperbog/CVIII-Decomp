# JP0667 — Japanese Beginning D/E state, frame gate, percussion/DPCM, register-cycle evidence

## Evidence boundaries

This is a **detached** original-source investigation for the owner-authenticated Japanese VRC6 Mapper24 Akumajō Densetsu ROM, SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`. It follows JP0664 song `$51`, JP0665 six-stream decoder and JP0666 bounded note-period register-plan oracle. It does **not** replace the original APU/VRC6 audio producer, feed the JP0647 mixer, modify game memory, claim independent Music/SFX sliders work, or imply an actual original-game reference recording has been captured.

## Original bank05 D/E handlers: read-only native C11 effects

`cviii_jp_effect_state_0667.h/.c` copies 2 KiB of synthetic/caller RAM into detached output (no original guest RAM mutation) and applies **supported local** original 6502 state changes for original melodic slot modes `0..4`. It refuses unknown commands, bad argument widths, bad slots, and the external-helper `ED/EF` paths without changing its output. It does not emit chip writes, sound samples or a song score.

The independently executed original ROM instruction paths are bounded by the SHA-authenticated raw05 `$837E–$8530` handler envelope (SHA-256 `ff148fe350183ed545f2bfb1ed546edc93686dfdc3bbd743da069677274701c8`), including the common parser core. The semantics validated *at the command handler boundary* are:

| Command | Original local RAM/state effect | Width in bytes |
| --- | --- | ---: |
| `D0–DF` | Set original `$0112` duration unit, `$017E/$0175` envelope/volume fields, `$01B7/$0187` per-note flags and `$03D9/$03DE` shape fields | 4 |
| `E0–E5` | Set `$01A3` octave and clear `$018E` bit 7 | 1 |
| `E6` | Set `$0112` duration unit to parameter, or its low nibble when `$018E` bit 7 is set | **2** |
| `E7` | Original bounded instrument-table dispatch updates `$01B7` and clears `$018E` bit 7; only known in-range parameter high nibble `0..9` admitted | 2 |
| `E8` | Update `$03D9/$03DE` low/high parameter nibble | 2 |
| `E9` | Clear/set `$018E` bit 5 or change `$017E/$03E8` modulation state depending on parameter | 2 |
| `EA` | Update `$01A8` signed encoded transpose | 2 |
| `EB` | Set/clear `$018E` bit 4 and configure `$06A5/$03ED/$03F7` phrase/envelope state | 2 when first parameter is zero; otherwise 3 |
| `EC` | Configure `$06B4/$06B9` control gating, with `$018E` mode-bit effects | 2 |
| `EE` | Update global `$01BE` | 2 |
| `ED/EF`, other F codes | Not yet safely isolated from fixed/helper interpreter; **rejected** | — |

**Original 6502 arithmetic detail:** `EB` at `$84C8–$84CE` performs repeated `ADC` without clearing carry at every iteration. Multiplying a duration unit by an integer loses original carry propagation for some inputs. The native code explicitly models the 8-bit ADC result and carry chain. For example, synthetic initial unit 169 repeated three times yields **252**, not 251. The earlier tentative `E6` one-byte concern was **disproved** after decoding instruction alignment at `$83F8`: this command consumes a parameter byte, consistent with the historical two-byte decoder.

A new original owner-ROM instruction-fetch oracle `jp0667_original_effect_compare.py` executes the actual bounded 6502 handlers until their entry-loop return `$8001`, comparing all relevant per-slot RAM state against compiled C11. **850/850 cases PASS** across original melodic modes and synthetic values. No frame scheduler was run in those cases.

### Voice frame gate (subset of scheduler, not absolute time)

Original raw0C:$8A7C–$8AA0 (SHA-256 `730a46288fbd1fd3f531a9a5c4e7fb540950c86fbce01d7d249931c7ce3885ed`) decrements `$0100,X` only when the original pause gate allows it. Countdown becomes zero exactly when a new stream parse is due (`$8DCD` dispatch). Nonzero—including decrement from zero wrapping to `$FF`—does not request a new note. Voice slot `$08` uses a different sound-ID-`$06` threshold on this path, instead of the normal `$011B` bit 0 shortcut. The native `cviii_jp_frame_gate_0667.h/.c` models only this **locally verified** countdown/pause/stream-due gate, not outer `$8A64` NMI scheduling, cycle offsets, dynamic channel ownership, `$8AAC` per-tick envelope subroutine, or complete note/effect cadence.

`jp0667_frame_gate_compare.py` executes 3,240 bounded original raw0C 6502 cases and compares the C11 outputs. **3,240/3,240 PASS:** 1,232 suppressed updates, 1,506 decremented-and-counting updates, and 502 stream-due decisions. These are artificial RAM states and bounded original instructions, **not** natural-gameplay frames.

### Source-backed percussion/DPCM *request* plans

Original raw05:$8072–$807D source-index mapping (SHA-256 `157833d861853f2e17a643fb6fcdc2999a9fcf03f53796bd51cee62c90307612`) contains **five low original sound IDs** and **seven high DPCM command IDs**. `cviii_jp_percussion_plan_0667.h/.c` reads this caller-authenticated source table on each mode7 percussion nibble. For high commands it delegates to **existing** `cviii_dmc_plan_0648` and source-authenticated original 15×4-byte DPCM descriptor table `$A957–$A992`. It returns the exact accepted/rejected six **abstract register-write intents** (`$4015/$4010/$4011/$4012/$4013/$4015`), including original `$019E` priority and `$06DD` counter effects, **not** DPCM sample DMA or waveform timing. Low noise requests stay as requests: assigning chip noise registers without the original low-ID dispatcher would be fabricated. 4,096 ROM-free synthetic event/priority cases PASS. Original 15 DMC programs were already proven by JP0648: no duplicate score credit.

`jp0667_owner_source_auth.py` additionally verifies the original-ROM SHA plus exactly four disjoint bounded source witnesses: raw05 D/E handler, raw05 percussion lookup, raw0C frame gate and raw0C 15-program DPCM table; no original bytes are published.

### Original gameplay CPU-cycle parity: **NOT ESTABLISHED**

`mesen_jp_register_cycles_0667.lua` is an **untested capture script** for an independently verified original MesenCE/Mesen2 build. It requests original CPU write callbacks at 2A03 `$4000-$4013/$4015/$4017` and VRC6 `$9000-$9003/$A000-$A002/$B000-$B002`, and prints original Mesen CPU cycle values and write addresses/bytes. It detects callback error and hard truncation. It does not observe missing preempted sounds, DMC DMA sample fetch bytes, effective DAC output or hardware APU internal edge timing.

`jp0667_cycle_trace_compare.py` is a fail-closed offline matcher for the original observer's `JP0667_...` log and the existing original-game native `CVIII-Audio-Registers.csv` (`cycle,chip,voice,register,value,previous,delta_cycles,rapid_rewrite`). It demands:

- Authenticated **original-JP ROM** and explicitly owner-attested matching power-on inputs/region/clock; no savestate transitions.
- One original reset boundary at the start, no truncation, both nonempty event sequences with legal register addresses, exact in-order address/value correspondence, and **identical recorded absolute CPU cycles**. It never automatically shifts the clock, drops events, fills in missing music or equates synthetic fixtures with real gameplay.
- Original emulator/core and native trace clock-origin correspondence must still be established independently; a reported conditional match is not a full APU/DMA/audio certificate.

Local **synthetic** proof: three invented aligned events accepted; nine deliberately malformed, missing, out-of-order, savestate/truncated or cycle/value/addr-mismatched conditions rejected. An actual independently executed original Mesen gameplay log and matched live native trace were **not** available in this environment. **Do not claim CPU-cycle original-game parity, full D/E envelope progression, or authentic sounding music at this checkpoint.**

### Owner-private reproduction

```sh
python3 JP/decomp/tools/jp0667_owner_source_auth.py --smoke
python3 JP/decomp/tools/jp0667_cycle_trace_compare.py --smoke
# GCC/Clang strict C11 ROM-free tests are included in run_native_regressions.sh.

python3 JP/decomp/tools/jp0667_owner_source_auth.py --rom /private/Akumajou.nes \
  --json /private/JP0667-source-metadata.json
# Compile shared objects from JP0667 source and the prior JP0666 Python reference.
python3 JP/decomp/tools/jp0667_original_effect_compare.py --rom /private/Akumajou.nes \
  --lib /private/libjp0667-effects.so --json /private/JP0667-effects-metadata.json
python3 JP/decomp/tools/jp0667_frame_gate_compare.py --rom /private/Akumajou.nes \
  --lib /private/libjp0667-frame.so --json /private/JP0667-frame-metadata.json
```

**Independent source observation still needed:** load the exact owner's Japanese ROM in MesenCE/Mesen2, load `mesen_jp_register_cycles_0667.lua`, reset after installing the script so the reset boundary is logged, play Beginning from power-on with a written reproducible controller-input sequence, quit cleanly and privately extract only `JP0667_` lines from the emulator log. Launch the native Alpha with the same inputs/region and `-AudioTrace` (see JP0610), collect `CVIII-Audio-Registers.csv`, then run:

```sh
python3 JP/decomp/tools/jp0667_cycle_trace_compare.py \
  --original-rom /private/Akumajou.nes \
  --mesen-log /private/JP0667-Mesen-lines.log \
  --native-csv /private/CVIII-Audio-Registers.csv \
  --matched-inputs-and-clock \
  --json /private/JP0667-live-parity-metadata.json
```

The `--matched-inputs-and-clock` declaration is a manual prerequisite, **not** automated proof of a match. Private logs may contain copyrighted sound-event sequences and should never be committed. Verify actual Mesen callback and cycle-counter semantics on the selected emulator build before relying on the comparison. Existing native timing tracing is unaffected. No new VPP/strict source coverage; R-007 remains open, music/SFX independent volume sliders remain pending.
