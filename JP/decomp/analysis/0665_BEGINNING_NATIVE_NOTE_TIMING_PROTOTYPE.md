# JP0665 — Original-Japanese Beginning note/timing C11 proof, detached

The exact Japanese original ROM, imported VRC6 NSF track 1 and owner-confirmed FamiStudio 4.5.1 TXT were inspected privately. No original game ROM, NSF, tracker TXT, DPCM payloads or note-by-note licensed score is bundled.

## Proven from original retail 6502 opcodes

- The original ripped NSF's **track 0 -> sound ID $51** is separately SHA-locked; the original cartridge's **$51** descriptor installs **six raw bank05 streams**, descriptor modes `0,1,2,3,4,7`.
- Raw05 `$800D–$8015` accepts upper-nibble `$0–$B` as ordinary notes, dispatches `$C–$F` to control; `$837E–$83B4` consumes D-prefixed four-byte voice-configuration; `$833D–$837C` computes `C` rest/mute countdowns.
- Raw05 `$82A0–$82B8` writes to original `$0100,X` the eight-bit `(low_nibble+1)*$0112,X` duration countdown for ordinary notes, rests and mode7 hit requests. This integer's conversion to exact CPU cycle deadlines is **not independently validated**.
- Raw05 `$811F–$8171` uses note high nibble for the original 16-bit `$872B` pitch-table lookup, which is then modified by octave and per-voice state. The included native sequencer exposes **unscaled table periods only**, not fabricated final register values.
- Register routing in `$81A9–$822D` and `$8314`: original modes 0,1,2 program VRC6 periods `$9001/$9002`, `$A001/$A002`, `$B001/$B002`, while modes 3,4 program APU pulses `$4002/$4003`, `$4006/$4007`. Original mode7 runs the distinct `$8052–$807D` percussion lookup; its sound program IDs above/equal `$6F` go through the original indexed DPCM branch. Original noise programs <=`$05` run a separate sound dispatcher.
- Sound `$51` contains *all six* raw05 source-control graphs bounded to the prior 04FB source window; the C11 code handles original `FB`, context-sensitive `FD`, counted `FE nn`, absolute `FE FF lo hi`, `FF`, `D`/`E` width and bounded source addresses. It does **not** yet apply every original effect (`E6–EF`, D timing/envelope operands) to hardware.

## Source-vs-FamiStudio timing tests

Private, SHA-locked original input compared to FamiStudio note-trigger positions. Original stream output is event candidates (including muted/retrigger state), not proof all sounded:

| First 1,024 exported tick positions | Native source candidates | FamiStudio note triggers | Shared tick positions |
|---|---:|---:|---:|
| VRC6 pulse1 | 117 | 188 | 113 |
| VRC6 pulse2 | 123 | 190 | 39 |
| VRC6 saw | 96 | 61 | 61 |
| 2A03 pulse1 | 116 | 98 | 98 |
| 2A03 pulse2 | 122 | 206 | 114 |
| DPCM | **117** | **117** | **117** |
| Noise requests/notes | 87 | 335 | 87 |

Over **all 7,424 exported tick positions**, DPCM had **717/717 FamiStudio positions present** in native source output, but the source output also had **19 additional candidates**. Other channels have substantial errors, especially VRC6 pulse 2. This demonstrates that the original source grammar + naive controller replay is not yet a faithful scheduler/envelope/player. The DPCM counts must **not** be read as DAC/audio parity, DMA correctness or gameplay liveness.

## Files and running locally

- `cviii_jp_music_0665.h/.c`: native C11 *source-driven* event decoder, six static original-chip destinations; does not touch game hardware or play any audio.
- `cviii_jp_music_test_0665.c`: synthetic ROM-free success and corruption smoke.
- `jp0665_owner_compare.py`: private original ROM+FamiStudio TXT authentication and detached C11 library tick comparison (does not emit music events).
- `cviii_jp_chip_0665.h/.c`: six **preview** oscillators (APU pulses/noise; VRC6 pulses/saw) driven by *externally supplied register writes*. The callback signature is compatible with JP0647's `CviiiVirtualSample`, allowing later independent buses. **No actual original `$51` music-register write program is wired to it yet**, no DMC PCM voice, no volume/pitch/sweep envelopes, no analog filtering parity, no exact CPU clock.
- `cviii_jp_chip_test_0665.c`: ROM-free wave generation/invalid-reg smoke.
- `metadata-timing-1024.json` and `metadata-timing-7424.json`: private-source-derived **aggregate only** results (not copyrighted song data).

Compile:

```sh
cc -std=c11 -O2 -Wall -Wextra -Werror -pedantic -DNDEBUG cviii_jp_music_0665.c cviii_jp_music_test_0665.c -o /tmp/jp0665-test
/tmp/jp0665-test
cc -std=c11 -O2 -Wall -Wextra -Werror -pedantic -DNDEBUG cviii_jp_chip_0665.c cviii_jp_chip_test_0665.c -o /tmp/jp0665-chip-test
/tmp/jp0665-chip-test
cc -std=c11 -O2 -fPIC -shared cviii_jp_music_0665.c -o /tmp/libjp0665.so
python jp0665_owner_compare.py --rom '/private/Japan.nes' --famistudio-txt '/private/CV3JP.txt' --lib /tmp/libjp0665.so --ticks 1024 --json '/private/JP0665-reference-summary.json'
```

Tested: GCC/Clang C11 strict `-Wall -Wextra -Werror -pedantic -DNDEBUG`, Clang ASan+UBSan, private ROM vs native C11 comparison for first 1024 and all 7424 tracker positions. **None of these tests proves original gameplay/audio parity or native build integration.**

**Release gate:** Do not bypass/suppress the original NESRecomp APU/VRC6 PCM or activate Music/SFX sliders using this prototype. The original game and Enhanced edition's existing combined audio remain authoritative. Complete the E-commands, original `F` scheduler special cases, original `D` instrument envelopes, raw0C timer advancement, noise and DMA sample voices, source-owner classification and MesenCE comparison *before* connecting this to game audio.
