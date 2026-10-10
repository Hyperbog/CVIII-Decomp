# 0514 — Original actor delta producer and bank-$0B postprocessing gate

**Evidence:** faithful original-ROM native state transitions, directly observed live Stage 1 entry, and explicitly synthetic original-CPU differential for otherwise unobserved branches. This is NOT whole-frame actor collision/scheduling parity or new certified PRG coverage.

## Original-ROM source provenance

The authenticated unmodified Japanese Mapper24 VRC6 ROM has SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`. The independent Mesen2 2.1.1 code/data mapping, not merely game RAM `$23`, identifies these original physical locations:

| Original mapped CPU source | Physical PRG | Semantics | SHA-256 for bounded original source window |
|---|---|---|---|
| Bank 30 `$D2FE–$D30C` | `$03D2FE–$03D30C` | `$62>=2` camera/object delta producer writes `$6B=$53-$08` | `7694f4922335fb8e25f4639f983714ea86112971811c3bc8afc6dc6a9aef5553` |
| Raw bank `$0B:$B1F8–$B215` | `$02F1F8–$02F216` | Postprocessing eligibility through `$B1F7`, `$B217`, `$B258` | `481d2cfaaa53fe9b2a40e1bf20577fd83d871386a1037d28acfb36e5147c035f` |
| Bank 30 `$D062–$D068` sample window | `$03D062–$03D068` | Original `$D064: LDA ($0A),Y` and `$D066: STA $65` room-data producer | `dca5f4c4fce297a90fe38a9a1df6ad646cfb424832bc039b2f7aab5e0b1a5039` |

**Important:** `$D062–$D068` is a seven-byte authentication window and ends on the first opcode byte of the next `JSR`; it is NOT a certified instruction-complete contiguous source slice. `$D066` is an identified *direct zero-page* writer, not a proof that no other indirect/aliased writes to `$65` exist. Its preceding `$D03C–$D064` logic selects pointer records through `$34/$35/$36`, `$D953,Y`, and `($0A),Y`. The real original gameplay domain of those descriptors and the `$65` high-bit condition for the vertical branch remain **OPEN**.

## Native semantic lift

[Native header](../src/actor_preflight_0514.hpp) and [C++ implementation](../src/actor_preflight_0514.cpp) expose two **bounded** source-semantic routines:

- `produce_delta6b_d2fe`: authentic `LDY $62`, conditional `DEY`, `LDA $53`, `SEC; SBC $08`, `STA $6B`, and RTS-boundary return A/X/Y/P when `$62>=2`. The distinct `$62=0/1` scrolling/coordinate-update branches are rejected, **not silently approximated**.
- `actor_postprocess_b1f8_gate`: starting at mapped `$0B:$B1F8`, checks `($0470,X & $11)`, `$0400,X`, then original type thresholds `$83`, `$80`, `$58`, `$61`; returns the exact next original CPU boundary (`$B1F7` immediate RTS, `$B258` bypass or `$B217` collision precheck) and A/X/Y/P. It performs **zero RAM stores**. Observed scheduler indices 1, 2, 14–17 are within the native gate's 1–17 scope; the separate fixed `$FF06` *actor allocation* domain of 1–12 must not be substituted.

These two structured routines do **not** implement or execute source `$B217` onward, collision helpers `$B339/$B3EC`, later `$B258/$B29D` paths, or the entire caller `$FDFB` frame continuation. The explicit branch result prevents incorrect fallthrough.

## Real Mesen gameplay observations

In genuine original-JP Stage 1 from the previously independently obtained natural frame-2604 state, Mesen reaches raw-$0B `$B1F8` for actor type `$3D`, X=1, `$0401=$92`, `$0471=$44`, and naturally reaches `$B217` after 12 original instructions. The verified return boundary is A=`$3D`, X=1, Y=0, P=`$80`. Mesen's physical mapped source offset is `$02F1F8`. Natural Stage 1 also runs the same `$B1F8` entry for X=2 and 14–17. A 60-frame observer recorded **360** bank-qualified `$B1F8` entries, not proof that all scheduler types/routes were processed identically.

At subsequent frame 2605, the authentic original ROM enters physical bank-30 `$D2FE`, CPU X=16, RAM `$62=$02`, `$53=0`, `$08=0`. Original `$D30A` writes `$6B=0`; after 9 original instructions including RTS, returned A/X/Y/P=`00/10/01/03` hex. The 60-frame observer saw **59** direct physical-$03D30A `$6B` stores, all `$00`. It saw **no** `$65` writer during those 60 frames. A separate natural frame-1503 to frame-1703 run likewise observed no direct `$65` writes. These are bounded negative observations; they do not establish that `$65` is constant or unused.

## Independent 6502 and native differential validation

Public [native original-ROM-free tests](../tests/actor_preflight_0514_test.cpp) cover **65,538** delta-producer cases (all 65,536 `$53/$08` byte pairs plus two invalid `$62` branch rejections) and **34,819** actor eligibility gate configurations over every 8-bit type, eight gate-mask/liveness scenarios, all 17 original scheduler indices and three invalid-X rejections. **100,357 cases** pass with strict C++20 builds and AddressSanitizer/UndefinedBehaviorSanitizer.

The [authenticated original-Mesen replay script](../tools/audit_actor_preflight_0514.py) runs **38** independent original-ROM instruction-step comparisons anchored to two *natural, private* Mesen states. Two input rows retain actual game-produced RAM; **36 cases explicitly inject RAM** to test the branches; they are **NOT new original-gameplay reachability**. Native C++ matches **68,096/68,096 non-stack Mesen RAM bytes** (1,792 per case), return A/X/Y/P, and all `$B1F8` branch destinations. The [compact machine report](0514_actor_preflight_report.json) carries original source hashes, private savestate hashes and outcome digest `4c8b821561085060437249f22bf0f78c22269951d8e2caf186aeaabceadf6394`, without committing retail ROM, emulator binary, savestates or raw RAM traces.

To reproduce locally (matching Mesen-agent 2.1.1 and the two original source-input savestates are required):

```sh
cmake -S JP/standalone0509 -B build/standalone0509 -DCMAKE_BUILD_TYPE=Release
cmake --build build/standalone0509 --parallel
ctest --test-dir build/standalone0509 --output-on-failure
python3 JP/tools/audit_actor_preflight_0514.py "$ORIGINAL_JP_ROM" \
  --mesen /path/to/mesen-agent \
  --native-replay build/standalone0509/native_preflight_replay_0514 \
  --producer-state /private/natural_D2FE_frame2605.mss \
  --postprocess-state /private/natural_B1F8_frame2604.mss \
  --report /tmp/0514_actor_preflight_report.json
```

GitHub Actions runs ROM-free C++ regression/CTest, script `py_compile`, and archive integrity. **It does not run private-ROM emulator replay.** Outstanding work: trace actual `$65` stage/room inputs, `$62=0/1` producer variants, and the `$B217/$B258` original collision gate continuation. A true source-equivalent native actor *frame* is not yet demonstrated. **Strict PRG +0; floor 49,504/262,144 (18.8843%); VPP 26/100; last certified checkpoint 0508; fixed frontier FB96 unchanged.** `RESUME_STATE.json` is not promoted.
