# 0522 — Provisional original-JP $FE63 bank0B actor-tail foundation

Original ROM SHA-256: `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28` (Mapper 24; 256 KiB PRG). ROM bytes are private and never committed. Physical PRG offsets are relative to the PRG block after the 16-byte iNES header.

| Source | PRG span | SHA-256 |
|---|---|---|
| fixed E2D0-E2D5 | 03E2D0-03E2D5 | 8d1a2898917458f00a455757ee9471327e1d4f51bee3d841d98e23055fb51380 |
| fixed FE63-FE75 | 03FE63-03FE75 | bfe287c26149b305403019d54a537ab15137c4a46933803ddc82e8e6f291631e |
| raw0B 8161-81B1 | 02C161-02C1B1 | ea381a34b2fe3df6c5b2c4fc40f89aaab3fe421de3d49a6852f00663195b5728 |
| raw0B 826C-8281 | 02C26C-02C281 | 210667cf666f4bec07e356c74ee535bdb1303568600aadf9c4bcad7d215511e2 |

The implementation starts at the original fixed FE63 boundary after the 0521 EF93 RTS. It supports actor indices X=0D..12, writes $23=$0B and models the PRG16 mapper bank as $0B, updates $0470,X bit 7 through raw0B 8161, then processes early RTS outcomes from raw0B 826C (type <$30, type >=$66, or type $30..$65 with $041C,X<$F8). FE6E advances X and returns boundary $FDEC or $FE75 with exact N/Z/C and preserved V. The $826C->$8193 tail callback is rejected before RAM mutation. Actor X<0D and whole-actor-frame continuation remain unlifted.

The native unit suite covers 110,592 supported cases, 18,432 rejected callback states, and 5 invalid actor-index guards. Release-mode assertions are forced on and local C++20 -Wall -Wextra -Werror -pedantic and ASan/UBSan checks passed. These tests are source-derived, not Mesen parity. The `native_fe63_replay_0522` executable accepts independent original Mesen pre/post 2KiB RAM dumps and expected PC/A/X/Y/P/bank, comparing 1,792 nonstack bytes due to the unmodeled hardware JSR/RTS stack.

Reproduction: `python3 JP/tools/audit_fe63_0522_rom.py "$ORIGINAL_JP_ROM"`; `bash JP/tools/run_native_regressions.sh "$ORIGINAL_JP_ROM"`; `cmake -S JP/standalone0509 -B build/standalone0509 && cmake --build build/standalone0509 && ctest --test-dir build/standalone0509 --output-on-failure`.

**Verification limit:** no independent original-Mesen FE63 replay has been run in this integration; the required private Mesen executable/agent and SHA-locked natural actor-15 savestate are not available here. Do not add evidence-ledger counts or claim certified gameplay equivalence. Previous strict PRG 49,504/262,144 bytes, VPP 27/100, semantic checkpoint 0508 and fixed frontier FB96 are unchanged.
