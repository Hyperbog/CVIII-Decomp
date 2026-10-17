# JP0656 — Complete bounded raw0C phrase control-byte format, native parity

**Target:** Authentic original Japanese VRC6 Mapper24 retail ROM SHA-256
`958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.
**Physical identity:** PRG raw 16KiB bank `0C` mapped conditionally at
CPU `$8000-$BFFF`, not an observed gameplay mapper trace.
**Whole subsystem:** source-indexed 125-program Japanese sound engine
and its secondary 148-entry phrase-index subsystem; sound interpreter
is **not** yet fully integrated or replayed during natural gameplay.

## Newly closed source-authenticated executable branch

The entire **61-byte original PRG0C:$8D90–$8DCC** instruction interval
has source SHA-256
`b483a567561def4d16207dc526ed89c53bf69e673651fc06b637d970f31cb315`.
The branch entrance `$8D15-$8D1F` is separately authenticated:
SHA-256 `cee4cc1f5bfa0852bbb7ba9ac6c56d841d19cb1218009570b0383b9bd507f4c3`.
The raw bank SHA-256
`f52c62b3c01fb10e9d727b9e983a2d0c1fc78ef502c5f972f9b28a349b2a9a42`
and 1,323-byte original raw0C `$A42C–$A956` stream pool SHA-256
`a35de62be83954e53e65ef149ee74d5e1f95e3d1999009bcf90221bd47e7e7b5`
also remain pinned. The previous JP0655 strictly bounded
`$8D15-$8D8F` ordinary-byte branch is preserved without modification.

Read directly from the **original opcode control flow**, the complete
one-byte classification at conditional `$8D15` is:

| Token | Exact original branch and state result | Output boundary |
| --- | --- | --- |
| `$00–$FA` | Original JP0655 8-bit nibble + two-byte arithmetic | $8D3D/$8D4B RTS |
| `$FB–$FD` | INC `$06AA,X`; copy cursor to `$06A0,X` | JMP `$8D06` |
| `$FE`, parameter equals incremented `$06AF,X` | Increment 8-bit `$06AF,X`, compare at `($E2),Y+1`; reset `$06AF,X` and `$06A0,X` to zero, increment cursor twice | JMP `$8D06` |
| `$FE`, parameter differs | Increment `$06AF,X`; copy `$06A0,X` to cursor | JMP `$8D06` |
| `$FF` | Set `$03F2,X=$FF` | RTS at $8DCC (caller return not modeled) |

Every control branch preserves the **final original A/X/Y and C/Z/N/V
register flag postconditions**, including the carry left by its
last compare; the `$FE` parameter address uses wrapped **8-bit Y**
and can legitimately reference the beginning of the phrase pointer
base when Y wraps. Native output also records precise RAM write
footprint (writes even if a value is unchanged).

The original 1,323-byte phrase pool contains 1,122 positions valued
`$00–$FA` and **201 control-valued positions**:
30 `$FB`, 0 `$FC`, 0 `$FD`, 30 `$FE`,
and 141 `$FF`. The occurrence count refers to *raw source byte
positions*, **not independently observed executed command instances**.
`$FC/$FD` are verified authentic **code-path possibilities** with
separate artificial-data tests, not claimed original music usages.

## Independent original CPU vs compiled native verification

- `JP/decomp/tools/jp_phrase_control_0656.py`: fetches and executes actual
  original opcode bytes starting at `$8D15` through the exact
  `$8D06` or `$8DCC` exit, with 6502 memory writes, indexed addressing,
  CMP/branches, actual PC, register/flags and bounded source bus.
  It requires the authenticated owner's original-ROM SHA and four
  independent original-span checks.
- `JP/recomp/native/enhanced/cviii_phrase_control_0656.h/.c`:
  dormant, read-only compiled C11 structural return contract with
  original register/flag results, four source-command outcomes and
  precise RAM effect flags. No audio, ROM, guest RAM or save mutation.
- `JP/recomp/native/enhanced/cviii_phrase_control_test_0656.c`:
  **327,680 ROM-free** control-domain cases (all five input bytes ×
  all 256 cursor values × 256 repeat-count values), independent
  expected-state oracle, explicit match/rewind coverage,
  invalid-source and unchanged-output rejection gates.
- **1,827/1,827 genuine original-ROM opcode vs C11 cases PASS**:
  every one of 201 original control-valued source positions,
  seven synthetic RAM state seeds, and both `$FE` branches.
  Original branch-hit counts: cursor transfer 210; `$FE` match 210;
  `$FE` mismatch 420; channel end 987. A further **42**
  opcode-vs-native cases with *synthetically altered private phrase
  data only* exercise `$FC/$FD` and all five token possibilities;
  these are excluded from authentic-source statistics.
- GCC and Clang C11 `-Wall -Wextra -Werror -pedantic` and Clang
  ASan/UBSan passed locally. Both native Windows and Linux CI
  build/test targets are added, using **only synthetic invented data**.
  The Japanese/US original-ROM bytes, copyrighted sound script
  payload, and private per-source JSON are never committed.

**Reproduce locally:**

```sh
python3 JP/decomp/tools/jp_phrase_control_0656.py --smoke
cc -std=c11 -O2 -Wall -Wextra -Werror -pedantic -DNDEBUG \
  JP/recomp/native/enhanced/cviii_phrase_control_0656.c \
  JP/recomp/native/enhanced/cviii_phrase_control_test_0656.c -o /tmp/jp0656-test
/tmp/jp0656-test
cc -std=c11 -O2 -fPIC -shared \
  JP/recomp/native/enhanced/cviii_phrase_control_0656.c -o /tmp/libjp0656.so
python3 JP/decomp/tools/jp_phrase_control_0656.py \
  --rom "/private/Akumajou Densetsu (Japan).nes" \
  --native-lib /tmp/libjp0656.so
```

## Fixed VPP scoring decision

**VPP Audio +1**, strictly the **first of two**
`Audio → music/SFX data formats` rubric subpoints.
JP0652 authenticated the complete **125-record / 325-reference**
primary sound directory; JP0653 authenticated both 128/20-word
secondary pointer tables and the complete bounded phrase pool;
JP0655 proved ordinary byte arithmetic; this checkpoint resolves
the **remaining $FB–$FF phrase control token format and all its
locally branched state effects** against actual original 6502
instructions and compiled C11. Together these form a reusable typed
source decoder contract, rather than opaque metadata-only pointers.
The **second data-format subpoint remains open** for the raw04/raw05
stream grammar, dynamic source/selector proof and remaining mode
handling. No credit is taken for driver architecture, APU/VRC6
register output, Music/SFX independent routing or original gameplay
trace parity.

**Global VPP: 27 → 28 / 100** (Audio: 1 → 2 / 12).
**Strict verified PRG: stays 49,504/262,144 (18.8843%)**:
the 61 source code bytes were already structurally represented and
there is **no new independent Mesen actual-gameplay liveness witness**
under the historical strict 0508 admission standard.
The independent fixed PRG31 frontier fingerprints
`$FB76-$FB95` and `$FB96-$FBB5` also remain byte-identical.
Original-JP gameplay, CPU cycle, IRQ, PPU, DMC DMA and PCM
parity, and R-002/R-007 remain **OPEN**. No original sound-engine
output changes and no playable-native audio claim.
