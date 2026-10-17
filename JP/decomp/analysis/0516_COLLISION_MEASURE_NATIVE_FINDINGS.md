# 0516 — Native original bank-$0B actor collision distances, B339/B393

**Evidence classification:** source-bounded original-ROM semantic lift, real one-actor Stage 1 reachability, and ROM-authenticated Mesen synthetic branch testing. No complete actor collision-response, source renderer, gameplay frame or certified PRG-byte promotion.

## Original physical PRG source and bounded entry

An authenticated unmodified Japanese Mapper24 (VRC6) ROM (SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`) executed in original Mesen2 2.1.1. On the naturally reached original Stage 1 type-`$3D` actor X=1, CPU `$B339` maps to **physical PRG offset `$02F339` in raw bank `$0B`**. The original instruction flow is **`$B1F8 → $B217 → $B232: JSR $B339 → $B36D: JSR $80B3`**. For nearby X coordinates, the original branch also executes `$B38E: JSR $80C1`. Both measurement paths arrive at **`$B393`**, immediately before the original `RTS` to `$B235`.

[Source C++](../src/actor_collision_measure_0516.cpp), [interface](../src/actor_collision_measure_0516.hpp), and [ROM-derived constant tables](../src/actor_collision_tables_0516.hpp) reconstruct this bounded source. Original source code/data hashes, established by [ROM-locked Mesen audit](../tools/audit_collision_measure_0516.py):

| Physical bank `$0B` CPU addresses | Original function or indexed bytes | SHA-256 |
|---|---|---|
| `$B339–$B393` | 91-byte measurement control-flow window | `63ffaae0dcfa49c59976f908028c5d479b7a5a322c98fbe2a7c651e416f421e3` |
| `$80B3–$80C9` | 23-byte horizontal/vertical absolute-difference helpers, shared subtraction and RTS | `30502fd79ec1b4a003445edee0f5d14b7d5abcd6bdf3ba006172ebf9bd316230` |
| `$BB05` (9 entries) | Original base X clearance | `bb77fce75faf9aa9c3114ffd5effec0eb52d21675d52553fdad025b057a4d809` |
| `$BB0E` (9 entries) | Original base Y clearance | `9573f03f87b039a49537447dedc25de80f6d8b6b46118a5e60ce5153f4a2c84f` |
| `$BB80` (105 entries) | Actor-type-indexed X radius | `1c80668c09c86baa24651b7ca05fa608627aaa83065974fbb5b6bf2ab00c3972` |
| `$BC08` (105 entries) | Actor-type-indexed Y radius | `dec7dfc688067be375a4f1a158dc2c9b46f00518dbc21209ef74886d2a79288c` |
| `$B394` (2 entries) | Original room-group player vertical offset `00 05` | `9f1afa4dc124cba73134e82ff50f17c8f7164257c79fed9a13f5943a6acb8e3d` |

**Important source correction:** the original vertical player offset at `$B395` is `$05` (five pixels), not `$01`. This was found by the mathematical unit test and validated by the original-Mesen vertical paths.

Native **supported preconditions** are deliberately narrower than the entire game: actor scheduler index X=1..17; original room index `$7F` 0..8; actor type `$054E,X` 0..`$68`; `$B7=0`; and *exclude* `$048C,X=$08` with `$0400,X≥$EE`. The latter enters a separate `$B396` source handler; nonzero `$B7` calls `$E5BE`. Both are **rejected**, not modeled approximately.

## Native behavior and real connected game event

Original `$B339` loads two room clearances into ZP `$00/$01` and actor-type radius into `$02`. The original `$80B3` computes absolute horizontal 8-bit displacement between `$0438,X` and player `$0438` with authentic 2A03 carry/overflow behavior. If distance is **at least** radius, it returns to `$B393` without vertical work. Otherwise it writes vertical radius `$03`, selects player room offset `$00/$05`, writes ZP `$11`, computes absolute vertical distance by original `$80C1`, and compares it to `$03`. Native return includes full A/X/Y/P and comparison carry. RAM stores are restricted to original scratch `$00/$01/$02` and, on the vertical branch, `$03/$11`.

The new `actor_collision_measure_b1f8_to_b393` **composes** the already verified [0514 actor gate](0514_ACTOR_PREFLIGHT_NATIVE_FINDINGS.md) and [0515 collision admission](0515_COLLISION_ADMISSION_NATIVE_FINDINGS.md) with this measurement. For a naturally reached Stage 1 actor, the actual original Mesen executes **53 CPU instructions** from `$B1F8` to `$B393`; composed native matches its 1,792 nonstack RAM bytes, A/X/Y/P and final PC. The shorter original `$B339→$B393` naturally executed **29 CPU instructions** and is also exact. **These are two overlapping windows on the same original actor**, not two independently reached events. Live X distance is `$2F` (47) and exceeds the actor's horizontal radius, so the authentic game takes the *horizontal early exit*. Artificial coordinate modifications are needed to exercise vertical evaluation.

## Test results and reproducibility

The [ROM-free C++ oracle suite](../tests/actor_collision_measure_0516_test.cpp) passes **139,343** cases: 65,536 fully enumerated X-coordinate pairs, 65,536 enumerated Y-coordinate pairs, 7,560 indexed actor/room/coordinate samples, 704 composed precheck/measurement scenarios and seven invalid-entry rejections. Optimized C++20 GCC with warnings-as-errors and AddressSanitizer/UndefinedBehaviorSanitizer pass. Source is linked into the existing native `standalone0509` CMake pipeline, with an additional [native RAM-replay tool](../tools/native_collision_measure_replay_0516.cpp).

The authenticated [Mesen differential audit](../tools/audit_collision_measure_0516.py) starts from the SHA-locked, naturally controller-reached **private original `$B1F8` state** (SHA-256 `0fd7256466e3e952402858ecaa3034eda6774ab2acbf16ad4e2d00c99e1b442c`). It derives `$B339` via **24 original CPU steps**, checks exact original CPU cycle **77,522,077**, natural 2-KiB RAM SHA `938ba9d9775a9544da06f666802f34f4b4ee20096eb396c8480ade73fb7fdc67`, and Mesen's *physical* `$02F339` mapping. It compares **50 instruction windows**: two overlapping natural windows and **48 explicitly RAM-modified synthetic windows**, all executing the authenticated original ROM code. Across those snapshots, native C++ matches **89,600/89,600 non-stack RAM bytes** (1,792 per window), end PC `$B393`, and original A/Y/P. 12 windows take horizontal early exit and 38 enter vertical comparison. [Compact report](0516_collision_measure_mesen_report.json) locks original ROM/table hashes, branch counts, sample hashes and outcome digest `88c500ebb8350e4a15393220f9f33a55529c1d7a8a5147d97cb975b9020de6af`. The 256 bytes `$0100–$01FF` of the original JSR/RTS hardware stack are excluded.

Reproduce with the original authenticated Japanese ROM and independent Mesen 2.1.1 executable/core:

```sh
cmake -S JP/decomp/legacy/standalone0509 -B build/standalone0509 -DCMAKE_BUILD_TYPE=Release
cmake --build build/standalone0509 --parallel
ctest --test-dir build/standalone0509 --output-on-failure
python3 JP/decomp/tools/audit_collision_measure_0516.py "$ORIGINAL_JP_ROM" \
  --mesen /path/to/mesen-agent \
  --private-state /private/natural_JP_stage1_B1F8.mss \
  --native-replay build/standalone0509/native_collision_measure_replay_0516 \
  --report /tmp/0516_original_collision_report.json
```

Private ROM, Mesen binaries, savestates, RAM, and raw trace dumps are **not** committed. CI executes the ROM-free native tests, Python syntax compilation and preservation/archive gate; it cannot run the private-ROM differential.

**Next original-source obligations:** `$B7!=0` → `$E5BE` / `$B73A`, `$048C=8` and `$0400≥$EE` → `$B396`, post-`$B393` return and `$B235` result-handling, source `$B1D8/$B162/$B258` branches, whole-frame actor scheduler and real PPU/OAM/APU parity. No native full-game/whole-frame claim. **Strict PRG bytes added: 0**; certified floor **49,504/262,144 (18.8843%)**, **VPP26/100**, last completed certified checkpoint **0508**, fixed-bank frontier `$FB96`; no promotion of `RESUME_STATE.json`.
