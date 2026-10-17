# 0513 — Original JP raw-bank $0B vertical actor displacement and $8843

**Evidence class: source-faithful C++ + synthetic original-Mesen instruction equivalence. NOT verified original gameplay reachability for `$810F`.** This distinction is essential. The source ROM is the authenticated Japanese mapper-24 game (SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`), mapped to raw 16-KiB PRG bank `$0B` (physical offsets `$02C0E3-$02C15E` and `$02C843-$02C86B`).

## Actual original ROM control flow

At `$80E3`, the fixed-bank `$FDF8` actor caller enters mapped raw bank `$0B`. The previous [0512 horizontal lift](0512_ACTOR_DISPLACEMENT_NATIVE_FINDINGS.md) covers `$65 & $80 == 0`. This tranche reconstructs **the opposite path `$65 & $80 != 0`**: `$810F` selects two Y-coordinate continuations depending on `$65 & 1`. Both sign-extend displacement `$6B` to `$00`, preserve original `$0470,X & $FE` to `$01`, then add `$6B` to `$041C,X`, propagate the carry into coordinate high bit0 of `$0470,X`, and preserve the 6502 accumulator, Y and N/Z/C/V flags.

The `$65` **even** branch at `$8113` gates on new `$0470,X` bit0: if 0, `$815E` jumps to `$8843`; otherwise `$812E` tests `$054E,X` (type). The `$65` **odd** branch at `$8140` gates on the new `$041C,X >= $30`: if true, jump `$8843`; otherwise use the same `$812E` actor-type gate. For that gate, types `<$68` or negative (`$80-$FF`) are deleted by writing zero to **both** `$054E,X` and `$0400,X`; types `$68-$7F` return intact. The condition is from original 6502 BMI/CMP/BCS instructions, not inferred gameplay conventions.

The actual branch continuation at **`$8843-$886B`** returns immediately if `$6B=0` or type `$054E,X != $3B`. For type `$3B` with nonzero displacement, it writes `$04` from the low bit of `$65` (zero or `$FF`) and uses original two ADC instructions to update the separate 16-bit coordinate `$0606,X`/`$061D,X`, preserving both carry and final A/Y/P semantics. Original continuation returns through its RTS to fixed-bank `$FDFB`; the C++ entry `apply_prg0b_actor_displacement_80e3_vertical_complete` models the bounded entire branch, not the downstream `$B1F8` actor postprocess. The separate `apply_prg0b_actor_displacement_80e3_vertical` exposes the pre-`$8843` boundary explicitly.

## Regressions and independent original-ROM CPU oracle

Native C++ [vertical source module](../src/actor_displacement_vertical_prg0b_0513.cpp), [header](../src/actor_displacement_vertical_prg0b_0513.hpp), [139,279-case vertical tests](../tests/actor_displacement_vertical_prg0b_0513_test.cpp), [131,072-case post-$8843 tests](../tests/actor_post8843_0513_test.cpp), and a [RAM/CPU-state replay executable](../tools/native_vertical_replay_0513.cpp) build cleanly with strict GCC warnings and pass independently with AddressSanitizer and UndefinedBehaviorSanitizer. Combined **270,351 ROM-free mathematical/unit cases**.

The [ROM-locked Mesen differential replay](../tools/audit_vertical_synthetic_0513.py) uses an original natural Stage 1 frame-2604 actor-X=1 source savestate (private SHA-256 `9250a09c03b5ea2d56157ddfa5a857a8fddab305dd17aad74490e0d8eac797aa`) with mapper bank `$0B` actually mapped. **It then forcibly sets CPU PC to `$80E3` and edits six individual RAM fields for each synthetic test**: `$65`, `$6B`, `$041D`, `$0471`, `$054F` and `$0401`. These edits are not a naturally executed game-state producer. The original unmodified ROM instructions run in Mesen 2.1.1 until the fixed caller return `$FDFB` (or a bounded `$8843` prefix breakpoint).

An original-Mesen *injected-state* matrix of **54 configurations** covers every combination of even/odd vertical route, positive/negative delta class and cleared/retained/transfer behavior (12 branch classes), including type `$3B` two-word continuation. For each case, native C++ matches **1,792/1,792 physical system-RAM bytes excluding only the 6502 hardware stack**, plus returned A/Y/P, X=1 and PC `$FDFB`: **96,768/96,768** RAM comparisons in total. [Compact report](0513_vertical_synthetic_report.json) lists the 12 branch-class counts, source block hashes and outcome digest `346cb04072a6ec025fa153441a7cff2cf43708ef3f1d6ce6fa81a2843c5d4871`. Physical raw-bank `$0B:$80E3-$815E` hash `84af7cef133ae428a931360513ff77918ebcc6ff1861439799493fb69d2e71b0`, and `$8843-$886B` hash `c79cb2d2295368c2034f93615d0acf4aca20a24c3a338c9f3be0f7d54854d8eb`.

To reproduce with private original JP ROM, matching Mesen-agent binary and the original naturally reached state:

```sh
cmake -S JP/decomp/legacy/standalone0509 -B build/standalone0509 -DCMAKE_BUILD_TYPE=Release
cmake --build build/standalone0509 --parallel
ctest --test-dir build/standalone0509 --output-on-failure
python3 JP/tools/audit_vertical_synthetic_0513.py "$ORIGINAL_JP_ROM" \
  --mesen /path/to/mesen-agent \
  --natural-original-state /private/natural_bank0B_80E3.mss \
  --native-replay build/standalone0509/native_vertical_replay_0513 \
  --complete --report /tmp/0513_vertical_report.json
```

## Bounded natural observation and remaining obligations

Separately, 300 consecutive *natural unmodified-input* original Mesen frames from the verified Stage 1 actor snapshot (frame 2603 to 2903) executed raw-bank `$0B:$80E3` but did **not** execute `$0B:$810F` in that interval; an initial 60-frame sample recorded 354 `$80E3` callbacks, zero `$810F` callbacks. This is a **bounded negative observation**, not proof the vertical branch is unused in the game. Native vertical branch parity therefore has **synthetic source-ROM instruction evidence**, not genuine vertical-gameplay liveness.

**Still open:** genuine `$65` producer and `$65`-negative gameplay inputs, fixed `$B1F8` post-processing, complete actor update scheduling and actual PPU/OAM/audio parity. Neither source hash nor synthetic Mesen agreement constitutes an overlap-deduplicated semantic byte certification. New strict PRG **0**, verified floor **49,504/262,144 (18.8843%)**, **VPP 26/100**, last certified checkpoint **0508**, fixed frontier **FB96**. No `RESUME_STATE.json` update.
