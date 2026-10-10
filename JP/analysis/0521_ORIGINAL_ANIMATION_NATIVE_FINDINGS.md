# 0521 — Original Japanese fixed-bank `$EF93` animation state update

**Evidence:** source-bounded native C++ reproduces the original ROM's `$EF93–$EFD1` animation countdown and ROM-table frame/phase advancement. One genuine original Stage 1 actor-15/type-`$80` event naturally follows **`$FDFE→$FE60 JSR $EF93→$FE63`**. This is **57 original 6502 instructions**, not a completed whole-actor frame.

## Original physical source

Original JP VRC6 mapper-24 ROM SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`; independent Mesen2.1.1 agent/core SHA-256 `95bcda9d4ff6428937183093386d993649c2d740273871ced78217d3d8f234d0` / `d2831c26d42aba675ed5d2cf392b2e12a67cb25274d981ef2c7741e552b72040`. CPU `$EF93` is fixed physical PRG `$03EF93`. Source `$EF93–$EFD1` (63 bytes) SHA-256 `bda4aad82a26f52a5f5fcefdedf647987d8e49ae4afb7b150b2d20f4903b3da5`; original pointer words at `$EFD2,Y` / `$EFD3,Y` with Y=`$0E` are physical `$03EFE0–$03EFE1`, source bytes `59 F3`, SHA `54819e9401d0371fa1f2ef00f1dba2a218bbcaa82af5ee3b2d0a0ee046409dda`. Original indexed descriptor triplets at `$F359–$F388` (48 bytes) SHA `948eeb0adfde8a3316c4c0e72aef51d6132b6276f287767ebdca411c2a633283`.

[C++ animation source](../src/actor_animation_ef93_0521.cpp) and [original source descriptor bytes](../src/original_ef93_tables_0521.hpp) model original ZP `$08/$09` pointer, original `$05AA,X` 3-byte-index math, `$057C,X` timer (DEC and reload), `$0400,X` animation frame, `$0593,X` phase increments and comparison/reset. Accumulator/Y and 6502 N/Z/C/V are preserved at original `$FE63` return. **Bounded support:** when timer refreshes, only descriptor `$048C,X=$0E` and frame index `$05AA,X≤15` are supported; all other descriptor families are rejected without partial RAM writes. When DEC leaves the timer nonzero, source skips descriptor handling and the native function supports any descriptor/index without reading them. Index X=1–18. This is structured native C++, not a 6502 emulator.

## Exact Mesen feedback

Using the private naturally controller-reached Mesen Stage 1 `$FDFE` state SHA `403e0819d38124abbc5156aae63f86566873c64719536eef9721d2fb40dc3a47`, independent original Mesen runs **29 source CPU instructions** to naturally enter `$EF93` with A/X/Y/P `00/0F/00/03`. The **28-instruction** direct `$EF93→$FE63` natural source call matches **2,048/2,048 internal RAM bytes** including the hardware stack plus original A/X/Y/P `00/0F/02/03`. The composed **57-instruction `$FDFE→$FE63`** original source path matches **1,792/1,792 non-stack RAM bytes**, A/X/Y/P and next PC; the original JSR changes the stack. The two natural windows are **overlapping views of ONE actor**, not two distinct gameplay events.

The [reproducible original-ROM differential](../tools/audit_animation_ef93_0521.py) checks **38 original CPU instruction windows**: two overlapping natural ones and **36 deliberately RAM-injected synthetic** cases—two CMP/phase outcomes for each of sixteen descriptor triplets plus four non-expiring timer inputs. Every tested source/native comparison matches CPU A/X/Y/P and exit PC `$FE63`; across tests **77,568/77,568 compared original internal RAM bytes** are exact. [Compact machine report](0521_original_mesen_animation_report.json) preserves source SHA-256 hashes, natural/synthetic counts and result digest `9f06575a0b8d250d9ad6e59ba0d9817cbbc0531ab40a9c3b85d74bf7060cfe0b`. Comparison bytes are not independent original ROM coverage.

[Native unit suite](../tests/actor_animation_ef93_0521_test.cpp) passes **65,547 cases** covering 16 indexed entries × 256 phase values × four timer modes and 11 unsupported/invalid-domain guards. Strict C++20 compilation and AddressSanitizer/UndefinedBehaviorSanitizer passed. [Native replay CLI](../tools/native_animation_replay_0521.cpp) compares full original RAM and CPU registers; the existing native source composition links directly to the original 0520 scheduler gate. Original ROM, Mesen binaries, proprietary assets, RAM snapshots and savestates remain private.

To reproduce with the matching private natural state, original Japanese ROM and Mesen agent/core:

```sh
cmake -S JP/standalone0509 -B build/standalone0509 -DCMAKE_BUILD_TYPE=Release
cmake --build build/standalone0509 --parallel
ctest --test-dir build/standalone0509 --output-on-failure
python3 JP/tools/audit_animation_ef93_0521.py "$ORIGINAL_JP_ROM" \
  --mesen /path/to/mesen-agent \
  --natural-FDFE-state /private/natural_FDFE_actor15.mss \
  --native-replay build/standalone0509/native_animation_replay_0521 \
  --report /tmp/0521_animation_source_report.json
```

**Remaining original code:** `$FE63 LDA #$0B → $FE65 JSR $E2D0` bank switch, `$FE68 JSR $8161` actor attribute callback, `$FE6B JSR $826C` and later scheduler completion; other animation descriptor pointers are not yet lifted. Whole-frame native/game parity remains open. 0521 adds no strict certified PRG bytes, no new VPP points. Strict PRG **49,504/262,144 (18.8843%)**, VPP **27/100**, last completed semantic certificate **0508**, fixed frontier `$FB96`.
