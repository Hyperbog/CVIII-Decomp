# 0511 — Faithful original JP bank-$0B actor fixed-point movement in native C++

**Validated native semantic lift; not a complete emulated frame or strict byte certificate.** Source: authenticated original 393,232-byte JP VRC6 Mapper24 ROM, SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`. Source raw bank `$0B:$8001-$804A` contains **74 bytes**, SHA-256 `4f8acdadcc27a00278b799ca271122d46c05473d92f19e1f01ee505113fccef9`. Mesen physically maps PC `$8037/$803E/$8047/$8020/$8033` to PRG offsets `$02C037/$02C03E/$02C047/$02C020/$02C033` respectively, not merely using a ZP bank tracker.

## Source math and integrated native interface

The previous [row-$32 live actor creation](0510_ROW32_NATIVE_LIFT_FINDINGS.md) yields two real type-`$3D` actors. During subsequent gameplay frames Mesen sees both active with script `$13` and RAM `$0657,X=$20`, advancing X through raw bank `$0B` movement code. Mesen `STA $0438,X` sources are `$8047` and `$80FD` (Lua callback reports the *next* CPU PC `$804A/$8100`); the latter is an **additional movement path, not reconstructed here**.

The new `src/actor_motion_prg0b_0511.{hpp,cpp}` is a structured native C++ lift of the **actual original `$8001-$8036` routine with nested `$8037-$804A` call**. It is not a 6502 interpreter. It preserves `$00=$0470,X&FE`, `$01=$FF` when integer X velocity `$04F2,X` is negative (otherwise zero), `$04C4,X += $0509,X` with carry into `$0438,X += $04F2,X`, and ninth X coordinate bit0 stored in `$0470,X` with carry/sign extension. Original `$04DB,X + $0537,X` and `$041C,X + $0520,X` form the Y fraction/integer update. All seven source RAM writes are retained, including unchanged-value stores; no other RAM fields are changed except original JSR/RTS stack bytes which the structured native lift never creates. Final returned 2A03 A/Y/P semantics are reproduced, including C/Z/N/V flags.

The ROM-free [native original-math oracle test](../tests/actor_motion_prg0b_0511_test.cpp) passes **69,646** inputs: 65,536 full 256×256 fractional-X and fractional-velocity combinations (varying integer signed velocity and high-bit state), 4,096 additional mixed cases, 13 actor indices and one invalid-index rejection. Optimized GCC strict-warning builds and ASan/UBSan both pass. Integrated into `standalone0509` CMake native library and mandatory `run_native_regressions.sh`; generic preview movement controls are NOT changed or given parity credit.

## Genuine original emulator RAM and register comparisons

An **independently original-Mesen-produced controller-only state** after two naturally reached raw-$0A row-$32 type-$3D spawns is privately hash-pinned (`c54060fc64196d750c79f222c22325d8ae1829a32f6da96c0fe93d808907a872`). The event was reached in an alternate naturally input-driven **100-frame checkpoint/reload** schedule at frame 2603; it must not be conflated with the earlier 0509 continuous branch's frame-3092 event. No RAM/PC/bank changes were injected to create it. The initial state remains private and is NOT in Git.

Original Mesen2 2.1.1 with authenticated agent/core independently steps both active actor slot X=1 and X=2 into `$0B:$8001` at **frame 2604**. Each call executes exactly **30 original 6502 instructions**, including `$8037-$804A` and both RTS instructions. [Native replay driver](../tools/native_actor_motion_replay_0511.cpp) passes all **1,792 nonstack RAM bytes** per call, plus exact returned A/Y/P (slot1 `50/00/00`, slot2 `B0/00/80` hexadecimal). Mesen original final CPU cycles: 77,523,380 and 77,525,243. **3,584/3,584** source RAM bytes match across two calls; [compact report](0511_actor_motion_live_report.json) locks before/after nonstack RAM hashes without redistributing original game RAM.

Replay on the authenticated private state and original Japanese ROM:

```sh
cmake -S JP/standalone0509 -B build/standalone0509 -DCMAKE_BUILD_TYPE=Release
cmake --build build/standalone0509 --parallel
ctest --test-dir build/standalone0509 --output-on-failure
python3 JP/tools/audit_mesen_actor_motion_0511.py "$ORIGINAL_JP_ROM" \
  --mesen /path/to/mesen-agent --private-state /private/natural_postspawn.mss \
  --native-replay build/standalone0509/native_actor_motion_replay_0511 \
  --report /tmp/actor_motion_live.json
```

The original private-state replay **passed**. A separate fully clean-boot one-command attempt reproduced the ROM and original stage states but intermittently stalled during the multi-invocation Mesen state bootstrap; that end-to-end driver is **not claimed as passed**. The native motion replay itself has been run successfully after the naturally produced private state. Do not merge those evidence grades. Actual 45-frame original Mesen observation keeps both type-$3D actor scripts stable and shows an X increment roughly one pixel per two to three frames, with no claimed full-frame native parity.

**Remaining:** raw `$0B:$80E3-$810F` second observed position writer, actor script dispatcher/AI continuation, full frame PPU/OAM, real game input, global $10 final-writer and pixel/audio parity. No complete global actor or timing model. Native progress does NOT promote semantic PRG bytes or VPP. Strict floor remains **49,504/262,144 (18.8843%)**, **VPP 26/100**, certified checkpoint 0508, fixed-bank frontier FB96. RESUME_STATE unchanged.
