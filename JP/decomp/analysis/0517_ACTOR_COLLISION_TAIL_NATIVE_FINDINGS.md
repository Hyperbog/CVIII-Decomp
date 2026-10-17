# 0517 — Original JP actor collision result through fixed-bank $FDFE

**Status:** Source-faithful, bounded native C++ and independent original-Japanese-ROM Mesen2 CPU/RAM comparisons. This is **one actor's collision tail, not a whole actor frame**, and not an overlap-deduplicated certified PRG extent. No changes to the earlier PC demo.

## Connected original gameplay execution

At Stage 1 original frame **2604**, normal original controller input reaches raw PRG bank **$0B**, original CPU **$B1F8** with actor X=1, type **$3D**. Original Mesen2.1.1 follows:

`$B1F8 → $B217 → $B232 JSR $B339 → $80B3 → $B393 RTS → $B235 → $B258 → $B29D → $B31F RTS → $FDFE`.

The original path executes **91 original CPU instructions** before returning to fixed-bank **$FDFE**. On this naturally reached state the last collision comparison has carry **set** (no overlap), bypassing the positive-collision setup. Actor follower slots **20, 21 and 22** are all empty, so original `$9B` scans `$14..$16`, ends at `$17`, and returns to the fixed scheduler. The completed structured native C++ composition [`actor_collision_b1f8_through_tail_0517`](../src/actor_collision_result_0517.cpp) is **1,792/1,792 non-stack internal-RAM bytes exact** with original Mesen at `$FDFE`, returning original A/X/Y/P `17/01/16/03` hexadecimal. Original CPU stack `$0100–$01FF` is excluded, because native functions do not model JSR/RTS hardware pushes.

A second, shorter natural tail witness from original `$B235 → $FDFE` executes **37 original instructions**, matching the same source actor and destination. The two naturally reached windows **overlap**: they are not two independent game actor events.

## Original source, native branches and explicit limits

The lifted mapped original-ROM source consists of three bounded physical bank-$0B windows, independently hash-checked by the [Mesen audit](../tools/audit_actor_collision_tail_0517.py):

| CPU window | Physical PRG start | Original source SHA-256 |
|---|---|---|
| `$B235–$B27B` (71 bytes) | `$02F235` | `c574b40977c2792490272d71441d622dec6f29b3db1eed2709c69e979001e294` |
| `$B29D–$B2A7` (11 bytes) | `$02F29D` | `dcb6ae9933347084a3403bd972b16568c780e350fef83be5e715618e615e2661` |
| `$B317–$B31F` (9 bytes) | `$02F317` | `76e769e52e5abe16461f696c487ef5e5edc1ec6aaf8565b543334b8d7230326c` |

[Native source](../src/actor_collision_result_0517.cpp) reconstructs:

- **`$B235` carry decision**: carry set skips response setup; carry clear writes the source attribute `$0657,X` into `$7E`, stores actor X in `$8E`, and writes left/right comparison direction to `$8D`. Actor type `$39` transfers to unlifted `$B243` special helpers.
- **`$B258–$B27B`**: type `$16/$37` short return, type `$61–$7E` short return, or `$068D,X&1` / `$0630` / `$0413` flags steering to the attachment scan or the unlifted `$B27C JSR $B3EC`.
- **`$B29D–$B2A7` and `$B317–$B31F`**: source-equivalent scan of follower types `$054E,Y` at indices **20–22**, incrementing zero-page `$9B`. Encountering a nonzero type stops at original `$B2A8`, instead of fabricating the unlifted attachment operation; if all empty, the routine returns via `$B31F RTS` to fixed `$FDFE`.

The actor scheduler's **X=1..17** index range is preserved; follower slots **20..22** are a separate scan domain, not the original actor allocator's X=1..12 domain. Native APIs explicitly return first unsupported PC `$B243`, `$B27C` or `$B2A8`. No PPU, frame, collision reaction for arbitrary actors, or game completion is asserted.

## Automated original-ROM feedback / regression results

[Native test](../tests/actor_collision_tail_0517_test.cpp) passes **65,539** bounded cases: 65,536 varied type/carry/attribute/follower configurations and three rejected indices. Strict C++20 compilation, AddressSanitizer and UndefinedBehaviorSanitizer pass. The [tail replay executable](../tools/native_tail_replay_0517.cpp) and [connected-path replay executable](../tools/native_composed_replay_0517.cpp) compare original ROM state snapshots with native C++ and CPU registers.

The independently executed [original Mesen audit](../tools/audit_actor_collision_tail_0517.py) verifies the original ROM SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`, Mesen agent/core hashes and immutable original controller-reached `$B1F8` savestate (SHA-256 `0fd7256466e3e952402858ecaa3034eda6774ab2acbf16ad4e2d00c99e1b442c`). It itself derives the naturally reached `$B235` breakpoint and a **deliberately coordinate-injected overlap** branch from the original `$B339` breakpoint.

**16 original-ROM CPU comparison windows passed: 2 overlapping natural and 14 synthetic** (including the injected overlap). Total **28,672/28,672** compared original Mesen **non-stack RAM bytes**, with exact original A/X/Y/P and destination PC. Synthetic probes cover positive collision setup `$7E/$8D/$8E`, type `$16/$37/$61/$7E/$7F`, `$068D` bit gate, `$0630/$0413` path to `$B27C`, occupied follower slot `$B2A8`, and type-$39 special helper. These injected cases **are not naturally observed gameplay**. [Compact machine report](0517_actor_collision_tail_report.json) preserves 16 per-window stop PCs and source instruction counts, ROM source hashes, result digest `e2223bed31eadea37c45a94ca8b60928f8e4fd69df930be54278241d26dc70d6`, and no raw retail-ROM, Mesen savestate or RAM data.

Reproduce using a locally obtained original JP ROM, qualified Mesen agent/core and the original natural private Stage 1 `$B1F8` state:

```sh
cmake -S JP/decomp/legacy/standalone0509 -B build/standalone0509 -DCMAKE_BUILD_TYPE=Release
cmake --build build/standalone0509 --parallel
ctest --test-dir build/standalone0509 --output-on-failure
python3 JP/decomp/tools/audit_actor_collision_tail_0517.py "$ORIGINAL_JP_ROM" \
  --mesen /path/to/mesen-agent \
  --natural-B1F8-state /private/natural_0514_B1F8.mss \
  --native-replay build/standalone0509/native_tail_replay_0517 \
  --native-composed build/standalone0509/native_composed_replay_0517 \
  --report /tmp/0517_original_collision_tail.json
```

GitHub CI runs ROM-free C++ tests and Python syntax checks, **not the original copyrighted ROM-dependent emulator audit**. Do not commit or distribute ROM, savestates, raw emulator RAM/trace/CDL or emulator binary.

**Next original-source frontier:** unlifted `$B243→$FF15/$B568` special type-$39, `$B27C→$B3EC` follower/contact helper, and nonempty follower `$B2A8` through `$B447/$B727`. Then reconstruct fixed `$FDFE→$FE00` actor continuation for an actual native actor-update step. Shared R-004 `$10` renderer writer and native PPU/OAM/APU/frame parity remain unresolved. **Strict PRG newly certified 0; floor 49,504/262,144 (18.8843%), VPP26/100, last completed semantic checkpoint 0508, fixed frontier FB96 unchanged.** No `RESUME_STATE.json` promotion.
