# 0515 — Original Stage 1 actor collision admission through bank-$0B:$B231

**Evidence grade:** bounded faithful C++ semantic lift of original JP PRG, plus original Mesen2 instructions and exact RAM/register/branch comparison. The collision resolution routine itself has **not** been lifted; this checkpoint stops at its call site `$B232: JSR $B339`.

## Original mapped source and live boundary

The authenticated original Japanese ROM (SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`) maps VRC6 raw bank `$0B` to CPU `$8000-$BFFF` on the observed Stage 1 frame 2604. Mesen's independent disassembler reports `$B217` as **physical PRG `$02F217`**, not just game RAM bank metadata. Original physical source `$0B:$B217-$B231` comprises **27 bytes** with SHA-256 `07704dd27ecdf3bdc4b0780dd5c0a00acf1bf3dc396fa0e7c93b28a790623587`; the longer bounded `$B1F8-$B231` slice hashes to `1a3b482dca0425a679df117a9330247c727042eb6d4b71fae32092b837956356` (58 physical bytes, not overlap-subtracted certification).

The original natural actor is type `$3D`, source X=1, with `$0401=$92`, `$0471=$44`, `$7E=$00`, `$7D=$00` at the mapped `$B1F8` entry. Mesen executes **12** original instructions to `$B217`, then **11** instructions to `$B232` where the original collision JSR begins. Original CPU at `$B217`: A=`$3D`, X=1, Y=0, P=`$80`, cycle 77,522,038. At `$B232`: A=0, X=1, Y=0, P=`$02`, cycle 77,522,071.

## Source-faithful native decision and branch priority

Native [C++ implementation](../src/actor_collision_precheck_0515.cpp) and [header](../src/actor_collision_precheck_0515.hpp) lift `$B217-$B231` directly, preserving accumulator, indexed register values, C/N/Z/V flag semantics and all branch-priority decisions. This source performs **no RAM stores**:

| Original CPU condition in order | Branch boundary |
|---|---|
| `$7E & $F0` nonzero (`$B217-$B21B`) | `$B258` bypass |
| Actor `$054E,X >= $69` (`$B21D-$B224`) | `$B162` actor-type continuation |
| `$0470,X & $02` nonzero (`$B227-$B22C`) | `$B1D8` attribute continuation |
| `$7D` nonzero (`$B22E-$B230`) | `$B258` bypass |
| Otherwise | `$B232` — stop before `JSR $B339` |

The public `actor_pre_collision_b1f8_through_b231` **composes** this new original source function with the already source-verified 0514 `$B1F8` actor eligibility gate. It retains the gate's other exits `$B1F7/$B258` and only invokes the `$B217` path when the original `$B1F8` gate selects `$B217`. Both entry points operate on scheduler actor indices **X=1..17**, distinct from original `$FF06` actor-allocation index 1..12. The header and implementation do not emulate a 6502 stack or execute collision logic.

## Test matrix with explicit evidence classes

The [C++ native test](../tests/actor_collision_precheck_0515_test.cpp) passes **82,947** cases: 65,536 combinations of 256 `$7E` values × 256 actor types; 16,384 branch-precedence/type/attribute/mask combinations; 1,024 integrated `$B1F8→$B231` gate combinations; three rejected actor indices. Optimized strict GCC and ASan/UBSan test builds passed. The module is linked into the existing `standalone0509` native library and both native test and [standalone original-Mesen replay executable](../tools/native_collision_precheck_replay_0515.cpp) are built by CMake and the project regression runner.

The independent [ROM-locked Mesen regression](../tools/audit_b217_original_mesen_0515.py) reuses the **unmodified controller-produced frame-2604 `$B1F8` input state**, exact SHA-256 `0fd7256466e3e952402858ecaa3034eda6774ab2acbf16ad4e2d00c99e1b442c`. It derives `$B217` by stepping 12 instructions in Mesen and authenticates the resulting CPU PC/A/X/Y/P/cycle, RAM SHA-256 `07b0cbc2d94013a219276945e568bcd5b06c661da61f36cafeae1b7f1d8ec6b0` and physical PRG. Identical CPU/RAM snapshots may serialize into different `.mss` hashes; the derived state is therefore validated by actual original RAM and CPU evidence, not the incidental compressed savestate hash.

**58 original-Mesen differential comparisons passed**: **two windows in the SAME naturally reached actor X=1 event**, one standalone `$B217→$B232` (11 instructions), one composed `$B1F8→$B232` (23 instructions); and **56 deliberately RAM-injected cases** exploring seven actor-type values × eight masks. This is **not** two independently reached actors, and the 56 edited cases do **not** establish natural branch liveness. Each native output matches 1,792/1,792 Mesen RAM bytes excluding only hardware stack `$0100–$01FF`, as well as A/X/Y/P and next PC: **103,936/103,936 matched bytes total**. Original source return destinations are `$B258`, `$B162`, `$B1D8`, `$B232`. [Compact machine report](0515_collision_precheck_mesen_report.json) records per-class counts and result digest `af0f7510525e432cfbbed55e630a9bab05be1aa672dce9cacd9450dfb16b4e7d`, without raw RAM or savestates.

Local reproduction (the separately supplied original ROM, matching Mesen 2.1.1 agent/core, private natural original state and native replay executable are required):

```sh
cmake -S JP/decomp/legacy/standalone0509 -B build/standalone0509 -DCMAKE_BUILD_TYPE=Release
cmake --build build/standalone0509 --parallel
ctest --test-dir build/standalone0509 --output-on-failure
python3 JP/tools/audit_b217_original_mesen_0515.py "$ORIGINAL_JP_ROM" \
  --mesen /path/to/mesen-agent \
  --native-replay build/standalone0509/native_collision_precheck_replay_0515 \
  --natural-B1F8-state /private/natural_0514_B1F8.mss \
  --report /tmp/0515_collision_precheck_mesen.json
```

GitHub CI exercises the ROM-free C++ tests and Python syntax check; **it cannot replay private original-ROM input states**. Do not commit source ROM, Mesen savestates or debugger RAM/trace files.

## Next physical original-code frontier and certification exclusions

An additional, genuinely game-reached Mesen 48-instruction trace (from the exact frame-2604 actor-$B1F8 source state) continues **`$B232 JSR $B339`, `$B339` initializes `$00/$01` from ROM tables `$BB05/$BB0E` using `$7F`, then `$B362-$B36B` computes `$02`, before `$B36D JSR $80B3` and the `$80B3` source begins signed position comparison.** This is a mapping/tracing result only; no native equivalence is claimed for `$B339`, `$80B3`, `$80C1`, `$B162`, `$B1D8` or `$B258` continuation. The original `$B7` and type `$048C` conditions in `$B339` still require branch analyses.

**Certification remains unchanged:** no newly overlap-deduplicated PRG instruction/data extent; new strict PRG bytes **0**, verified **49,504/262,144 (18.8843%)**, **VPP 26/100**, last completed certified semantic checkpoint **0508**, fixed CPU frontier **`$FB96`**. The active research checkpoint is 0515; `RESUME_STATE.json` remains unchanged. R-004/$10 final renderer writer and full native frame/PPU/APU/scroll/input parity remain OPEN.
