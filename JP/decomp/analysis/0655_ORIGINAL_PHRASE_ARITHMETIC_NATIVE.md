# JP0655 — Authentic original-JP sound phrase arithmetic, compiled native C11

## Whole-subsystem context and exact physical scope

This continues the **original Japanese raw PRG0C sound interpreter** initiated
by JP0533, JP0534 and JP0652–JP0654. It is **one completed bounded arithmetic
branch** within that ongoing whole-subsystem work, **not** a completed bank or
native music engine. Original Japanese Mapper24 VRC6 ROM SHA-256 is
`958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.

This pass decodes the original bank-qualified CPU address range
**physical raw16 PRG bank 0C, conditional CPU $8D15–$8D8F**: 123 source
bytes, each authenticated against the original retail ROM. The first routine
is in physical 8KiB PRG24; source phrase data $A42C–$A956 is in PRG25.
The code executes only when the cartridge bank mapper selects raw0C in
$8000–$BFFF; this is a **conditional local execution proof**, not
a matched original Mesen gameplay callback.

| CPU half-open address range (physical raw0C) | Source bytes | SHA-256 |
| --- | ---: | --- |
| $8D15–$8D4B caller/ordinary byte dispatch | 55 | `30d0ef2f537e579ce47ef71afc54b7ac83fc966a9248c82f22e0890527cbfc74` |
| $8D4C–$8D5F 8-bit repeat-add multiplier | 20 | `9898cc613eff3a85d480d3a908efd9c7b13a2f265cccfd5a05eecb3f8182d47e` |
| $8D60–$8D75 16-bit add with carry | 22 | `c5c81eeb8623764bde0889a6e6d1070166ff9f3e9e78c115205d4bf74cf7773c` |
| $8D76–$8D8F 16-bit subtract with borrow | 26 | `b10cf22a11e99bfce83df2b964f72faf986fc4d199eb0def04c01ceaee4eb8ba` |
| **Total $8D15–$8D8F** | **123** | `feaba31c42beb226b70c9bc3f4551c4f3a2d1f75ac6c7874c4537f11249a8151` |

The source instructions are not a guessed stream grammar:

1. Original `LDA $06AA,X; TAY; LDA ($E2),Y; CMP #$FB` reads
   one byte from the bank-qualified source stream. **$FB–$FF** branch
   to original $8D90, outside this lift and intentionally rejected.
2. For byte $00–$FA, `CMP #$10` selects whether four `LSR A`
   shifts update channel field `$03F2,X`. The original
   `INC $06AA,X` increments the source cursor with 8-bit wrap.
3. `AND #$0F` selects a low-nibble magnitude. For $0–$7,
   `$8D4C` performs a repeated add of nibble × original RAM
   `$03F7,X`. For $8–$F, it first replaces the nibble with
   $10–nibble. The **multiplier zero case executes 256 loop iterations**
   due to the original `DEX; BEQ` sequence, producing zero modulo 256
   but with different CPU cost from an immediate no-op.
4. `LDX $EE` restores X from original shared state. The original
   $8D60 add or $8D76 subtract uses prior two-byte RAM value
   `$01AD,X/$01B2,X`, returns result in `$EC/$ED`, and leaves
   scratch `$E2` holding the calculated magnitude. The native lift
   records final A, X, Y and **C/Z/N/V flags**. It preserves the original
   conditional Z/N overwrite by `INC/DEC $ED` when the low byte
   carries or borrows.

This is **not** proof of the musical note, duration, pitch, volume, player
voice, or playback effect of any input nibble. Those meanings depend on
the greater stateful interpreter and mapper/hardware semantics.

## Verified source-data domain

The complete earlier JP0653 phrase stream pool at physical raw0C
$A42C–$A956 is 1,323 original ROM bytes, SHA-256
`a35de62be83954e53e65ef149ee74d5e1f95e3d1999009bcf90221bd47e7e7b5`.
Across all original **byte positions**, not just proved live command starts:

- **1,122** values are below $FB and are candidates for isolated
  ordinary-byte replay.
- **201** values are control tokens (141 × $FF, 30 × $FB, 30 × $FE).
  They are **excluded** from ordinary-byte replay; no claim that
  all those bytes represent executed parser commands.
- All 1,122 ordinary byte *positions* are conditionally replayed
  with five distinct RAM/register seeds = **5,610 original-6502
  instruction paths**. The reference emulator fetches the **actual
  original opcodes**, performs stack-backed JSR/RTS, 8-bit RAM updates
  and CPU arithmetic. The independent compiled C11 translation
  matches final A/X/Y, C/Z/N/V, cursor, nibble state, scratch and the
  low/high 16-bit result, with the exact allowed non-stack RAM
  write footprint. **5,610/5,610 PASS**, including 1,122
  factor-zero scenarios and up to 1,316 stepped instructions.
- OriginalROM, original raw0C bank, four subroutine and whole
  123-byte block hashes are pinned. Nine owner-ROM/physical-bank
  corruption or identity checks rejected changed source. The
  original recorded PRG31 overlap/frontier hashes all still match.

These are synthetic **input RAM states applied to authentic source code
and media**. They do not establish natural game execution of every
source byte, all callsites, DMA cycles, IRQ or APU event parity.

## Dormant native implementation and regression gates

New code:

- `JP/recomp/native/enhanced/cviii_phrase_delta_0655.h/.c`: pure C11
  ROM-supplied, read-only *semantic result* helper. It never mutates
  guest RAM, mapper state, PCM/audio, save files or the original game.
  It returns 1 only for byte <$FB, 0 for excluded $FB–$FF tokens
  and -1 for invalid buffers/unmapped source. In both non-success
  cases it leaves the caller's output struct unchanged.
- `JP/decomp/tools/jp_phrase_delta_0655.py`: originalROM SHA, four
  subroutine SHA, whole-code, complete raw bank and pool checks;
  instruction-fetched bounded original CPU reference; first-divergence
  refusal and aggregate metadata only. No retail phrase bytes
  are committed or emitted.
- `JP/recomp/native/enhanced/cviii_phrase_delta_test_0655.c`: ROM-free
  independent **385,536 synthetic cases** covering every ordinary
  byte $00–$FA, every 8-bit multiplier and six low/high boundary-value
  seeds. Its slow repeated-add oracle is distinct from the production
  multiplication formula. Tests exercise fail-closed control tokens,
  invalid mapper windows, bad buffer sizes and mutation-safe return.
  C11 assertions are forced active even with Release `-DNDEBUG`.
- The synthetic Python smoke checks 4,096 nibble/multiplier
  combinations. GCC and Clang `-Wall -Wextra -Werror -pedantic`,
  Clang AddressSanitizer/UndefinedBehaviorSanitizer passed locally.
  Linux/Windows native CI builds and regressions are tracked separately.

Private reproduction (retail ROM never uploaded to Actions):

```sh
python3 JP/decomp/tools/jp_phrase_delta_0655.py --smoke
cc -std=c11 -O2 -Wall -Wextra -Werror -pedantic -DNDEBUG \
  JP/recomp/native/enhanced/cviii_phrase_delta_0655.c \
  JP/recomp/native/enhanced/cviii_phrase_delta_test_0655.c \
  -o /tmp/jp0655-test
/tmp/jp0655-test
cc -std=c11 -O2 -fPIC -shared \
  JP/recomp/native/enhanced/cviii_phrase_delta_0655.c \
  -o /tmp/libjp0655.so
python3 JP/decomp/tools/jp_phrase_delta_0655.py \
  --rom "/private/Akumajou Densetsu (Japan).nes" \
  --native-lib /tmp/libjp0655.so \
  --json /tmp/jp0655-metadata-only.json
```

**Boundary:** The header/output describes scalar postconditions, **not
full RAM/bus event mutations**, 6502 CPU cycle accounting, full
hardware flag-state contract or the $FB/$FE/$FF control interpreter.
The compiled helper has **no live call site**; original audio and
Enhanced output stay unchanged. The earlier independent MesenCE
owner-playthrough parity boundary remains open, as do R-002 and
audio R-007. All 123 code bytes were previously structurally
source-authenticated in bank0C; strict newly admitted PRG bytes
**0**, global strict PRG **49,504/262,144 (18.8843%)**, VPP
**27/100**, certified **0508**, fixed PRG31 frontier **$FB96**
unchanged. No full-bank completion or new mod API is claimed.
