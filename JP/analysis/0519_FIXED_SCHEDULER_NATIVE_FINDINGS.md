# 0519 — Source-faithful fixed-bank actor scheduler continuation gate

**Evidence:** original unmodified Japanese Castlevania III Stage 1 naturally reaches CPU `$FDFE` and executes ten source instructions to `$FE31`; a structured native C++ source lift matches **2,048/2,048 internal RAM bytes**, A/X/Y/P and destination PC. The code stops **before** `$FE31: JSR $BD11`. It does **not** implement the remainder of the actor scheduler, a full game frame, or the original collision response.

## Original physical source

ROM SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`; original Mesen2 agent SHA-256 `95bcda9d4ff6428937183093386d993649c2d740273871ced78217d3d8f234d0`, core SHA-256 `d2831c26d42aba675ed5d2cf392b2e12a67cb25274d981ef2c7741e552b72040`. CPU `$FDFE` maps to physical PRG31 offset `$03FDFE`. Original source window `$FDFE–$FE38` (59 bytes) SHA-256 `914d07f4eb94ca66311acca1f86e24ce20e46f53ee72ec0e5a07c489864fe343`. The shorter source decision window `$FDFE–$FE2B` hashes to `173c20666fe116cb35c9b167201111b9960d435d7ce685e8fb94225578a31c15`. Neither window is credited as novel PRG: this project already has earlier fixed-bank semantic evidence, and 0518 established that the full historical union must be checked.

## Actual natural Mesen source event

Original controller inputs alone advance the retail ROM from cold boot through a frame-1503 state to frame 2603. At **frame 2603**, the original CPU naturally reaches `$FDFE` with actor slot X=15, actor type `$054E,X=$80`, attribute `$0470,X=$81`, scratch `$69=$0F`. The original PC/A/X/Y/P/cycle at entry are `FDFE/01/0F/00/01/77497061`; ten original CPU steps execute at:

`FDFE → FE00 → FE03 → FE05 → FE07 → FE16 → FE19 → FE1B → FE23 → FE26`

and stop at **PC `FE31`**, with A/X/Y/P/cycle `80/0F/00/81/77497091`. The full 2 KiB Mesen internal RAM SHA-256 is the same before and after: `11f46dd23d37ae7caafa50ddd89e0ab9736b1c0b0a37de7ea6cc2c9f8708292f`. No original RAM, CPU PC, or ROM bytes were patched for this natural observation. Because no JSR has yet executed, the 256-byte stack may be compared too.

The [native C++ routine](../src/scheduler_postcollision_0519.cpp) exactly reproduces that natural original execution boundary: **2,048/2,048 physical RAM bytes unchanged and returned A/X/Y/P and terminal PC equal to Mesen**. [Native replay CLI](../tools/native_scheduler_replay_0519.cpp) checks the complete 2 KiB original RAM snapshots and register values.

## Bounded source behavior and non-natural test paths

Starting at original `$FDFE LDX $69`, the native routine selects **original first-call stop boundaries** based on actor type and `$0470,X & $02`, without executing any of these unresolved helpers:

| Original predicate | First stop PC | Not yet executed |
|---|---|---|
| Type `$054E,X == 0` | `$FE6E` | actor-loop advance |
| Type `$01–$2F` | `$FE0B` | bank switch `JSR $E2D0` after `LDA #$09` |
| Type `≥$30` with attribute bit 1 set | `$FE1D` | `JSR $FE8C` |
| Bit 1 clear, signed type `$80–$FF` | `$FE31` | `JSR $BD11` (**naturally observed**) |
| Bit 1 clear, type `$30–$68` | `$FE2C` | `JSR $FF56` |
| Bit 1 clear, type `$69–$7F` | `$FE36` | `JSR $BD11` |

All branches preserve 6502 `LDX/LDA/AND/CMP` N/Z/C status, old I/D/B/V flags, and original register X selection from `$69`; no RAM writes occur in this prefix. Native rejects X outside **1–18**, the observed fixed actor scheduler range. This is *not* the original allocator's **1–12** destination slot domain, nor the follower scan's **20–22** domain.

[Native test](../tests/scheduler_postcollision_0519_test.cpp) passes **73,731** configurations (18 indices × 256 actor types × 16 attributes plus three invalid-X cases) in strict C++20 optimized and AddressSanitizer/UndefinedBehaviorSanitizer builds. Tests for the five other first-call paths use **synthetic native states**, not independently reached game inputs; natural Mesen state parity is established only for slot 15/type `$80` terminating at `$FE31`. The project [native CI regression gate](../tools/run_native_regressions.sh) compiles and executes this ROM-free unit test. An optional attempted all-in-one cold-boot Mesen replay wrapper stalled intermittently during savestate preparation and is **not claimed to pass**; original Mesen input/cold-boot steps and the ten-instruction source replay were verified separately, as described above.

## Next original source boundary and accounting

Reconstruct `$FE31 → JSR $BD11` and the subsequent `$FE34` actor-type checks using real original Mesen source states; alternatively trace `$FE2C JSR $FF56` for live type `$3D` actors. This is still not an end-of-actor-frame native result. **Zero** additional strict PRG bytes/VPP points; current VPP **27/100** from the independent 0518 gameplay rubric review, strict floor **49,504/262,144**, last completed semantic certificate **0508**, frontier **$FB96** unchanged.
