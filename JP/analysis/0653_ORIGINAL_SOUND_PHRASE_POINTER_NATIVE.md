# JP0653 — Original sound phrase indexing, bounded native 6502 parity

## Physical source and exact boundaries

Original retail Japanese Mapper24/VRC6 ROM SHA-256:
`958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.
All addresses below are **CPU addresses conditional on physical raw16 bank `0C`**
(PRG byte offset `0C*0x4000 + (CPU-$8000)`). They are not evidence of
observed live mapper state.

Original instruction sequences independently authenticated from ROM bytes:

- `$8B2C-$8B3A` inclusive, 15 bytes, SHA-256
  `7b5d76bfa7b74521769c25f33258af5d2929461695e80c78ae3769274c4fc350`.
  Original instructions are `LDA $01B7,X; ASL A; TAY; LDA $A304,Y;
  STA $E2; LDA $A305,Y; STA $E3`. The selector source is **RAM
  `$01B7,X`**, not an inferred musical track ID.
- `$8D07-$8D14` inclusive, 14 bytes, SHA-256
  `cb9975a69bde783bc881ed8c2e9ee35a97f755d28913653a278cbbbeb9d28941`.
  Original instructions are `LDA $06; ASL A; TAY; LDA $A404,Y;
  STA $E2; LDA $A405,Y; STA $E3`. The selector source is **ZP `$06`**.

Both execute original 8-bit `ASL A`, so the table byte index is
`(2 * selector) & $FF`: values `$80-$FF` alias `$00-$7F`.
The first consumer's entire 128-index domain reads within `$A304-$A403`;
the second consumer has only **20 structurally indexed pointers** at
`$A404-$A42B` (selector indices 0..19, with high-bit aliases 128..147).
For the other 108 distinct second-consumer selector indices, authentic
6502 reads still happen, but **the source words are phrase-data bytes,
not certified pointer table entries**. The native model records those
raw bus words with an unverified classification and must not treat them
as valid phrase roots or proof of an original game error.

## Whole phrase-pool classification

The 296-byte pointer region `$A304-$A42B` is SHA-256
`2c2b1d4a4f59c39c8ad46ad4b2c103055cf61911fdd3e68e104b1a5d2cfd8945`;
the 1,323-byte source pool `$A42C-$A956` is SHA-256
`a35de62be83954e53e65ef149ee74d5e1f95e3d1999009bcf90221bd47e7e7b5`.
The 148 sorted indexed words have **140 distinct roots** and exactly eight
repeat-pointer excess entries (one root repeated eight times and one twice).
A full, nonoverlapping root-to-next-root physical partition covers all 1,323
bytes. Each structural interval ends in `$FF`.

**Important exception:** the last indexed interval `$A945-$A956`
contains **two** `$FF` bytes, at `$A94F` and `$A956`. It is **not** correct
to claim its entire 18-byte span is one original executed phrase with a
single terminal instruction. The model reports the complete *source interval*
without inventing what follows its first `$FF` or implying runtime liveness.

## Implemented native source lift

- `JP/native/enhanced/cviii_phrase_lookup_0653.h/.c` — dormant, read-only
  C11 source-pointer resolution, including original A/Y and final Z/N flags,
  8-bit wrap, CPU read address, raw returned pointer word and distinct
  verified table-membership status. It validates the complete source
  pointer ordering and interval terminals before using a record. Out-of-table
  original reads return unverified source status with no certified span.
- `JP/tools/jp_phrase_lookup_0653.py` — private original-JP full ROM,
  exact opcode/table/pool SHA audit and small **instruction-fetched**
  NMOS-6502 reference execution of both real opcode sequences, not a
  pointer-formula-only emulator. Optional `--native-lib` compares original
  stepped A/Y, Z/N, `$E2/$E3` pointer bytes against compiled C11.
- `cviii_phrase_lookup_test_0653.c` — independent artificial bank and C11
  rejection tests; no copyrighted source media or reconstructed phrases.

Authenticated private execution **PASS**: 2 routines × 256 byte selector
values × 6 initial X seeds = **3,072/3,072** original-opcode-versus-compiled-C11
local cases. ROM-free Python smoke tests 512 artificial opcode paths, all
148 structural pointers, 140 artificial intervals and corruption cases;
strict C11 synthetic tests include both complete 256-selector domains,
invalid input, bad pointer and damaged terminal with unchanged output on
hard failure. Both GCC and Clang C11 compiles passed; sanitizer build passed.

```sh
python3 JP/tools/jp_phrase_lookup_0653.py --smoke
cc -std=c11 -O2 -Wall -Wextra -Werror -pedantic -DNDEBUG \
  JP/native/enhanced/cviii_phrase_lookup_0653.c \
  JP/native/enhanced/cviii_phrase_lookup_test_0653.c -o /tmp/jp0653-test
/tmp/jp0653-test
# Private ROM only, optional C11 shared library built locally:
cc -std=c11 -O2 -fPIC -shared \
  JP/native/enhanced/cviii_phrase_lookup_0653.c -o /tmp/libjp0653.so
python3 JP/tools/jp_phrase_lookup_0653.py \
  --rom "/private/Akumajou Densetsu (Japan).nes" \
  --native-lib /tmp/libjp0653.so --json /tmp/jp0653-summary.json
```

The JSON contains **aggregate metadata and no ROM/source-pool bytes**.
Both GitHub build gates operate on ROM-free fixtures; MesenCE and original
retail gameplay are **not** executed in CI. Original sound selector liveness,
true note/phrase command grammar, voice assignment, APU/VRC6 timing,
DMC DMA timing and original-vs-native full game/audio parity remain open.
There is **no actual playback change** and no public mod API introduced;
the JP0647 virtual voice mixer remains dormant. Strict semantic PRG remains
**49,504/262,144 (18.8843%)**, VPP **27/100**, certified checkpoint
**0508**, fixed frontier **$FB96**, R-002/R-007 **OPEN**. All these source
bytes were structurally accounted in JP0534, so **no new strict credit**.
