# 0520 — Source-faithful original BD11 early return and fixed FE34 scheduler decisions

**Scope:** connected native C++ reconstruction of raw bank `$0B:$BD11–$BD1E` and fixed bank 31 `$FE34–$FE5F`; original Mesen2 naturally follows `$FDFE → $FE31 JSR $BD11 → $BD10 RTS → $FE34 → $FE60`. The result is a bounded source-equivalent gate and **not** a full actor-frame update.

## Authenticated original mapped source

The source is the unmodified Japanese VRC6 mapper-24 ROM SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`. Original Mesen2.1.1 (agent SHA `95bcda9d4ff6428937183093386d993649c2d740273871ced78217d3d8f234d0`, core SHA `d2831c26d42aba675ed5d2cf392b2e12a67cb25274d981ef2c7741e552b72040`) disassembles original CPU `$BD11` from mapped physical PRG `$02FD11` and fixed `$FE34` from `$03FE34`: 

| Original physical source window | Length | SHA-256 |
|---|---:|---|
| raw `$0B:$BD10–$BD1E` (physical `$02FD10–$02FD1E`) | 15 | `3b41c6d64f49c352ac47a80b050cd525e06b87f1f167bfdeddff57d274732484` |
| fixed PRG31 `$FE34–$FE5F` (physical `$03FE34–$03FE5F`) | 44 | `babee7df6116c8cdf20ee322f3ae4d3e9cef79a60399d2dfbb061cf5cbe4730c` |

These are physical-source fingerprints, **not a newly overlap-deduplicated PRG certificate**; the historical strict-byte ledger still needs complete reconciliation.

## Naturally reached original execution

The same private controller-reached original Stage 1 actor-15/type-`$80` source savestate as 0519 is used (SHA-256 `403e0819d38124abbc5156aae63f86566873c64719536eef9721d2fb40dc3a47`). Mesen independently steps **11 original instructions** from `$FDFE`, reaching `$BD11` with CPU A/X/Y/P `80/0F/00/81`; CPU JSR stack bytes have been pushed. Original RAM `$A8=0` and `$05EF,X=0`, so `$BD13 BEQ $BD1A`, `$BD1D BEQ $BD10` and `$BD10 RTS` return to original fixed `$FE34` without running optional `$E744` or actor-table helper. The next fixed source actor gates check type `$054E,X`, attribute `$0470,X & $40`, `$0470,X & $20`, and `$A8` before continuation.

**Natural isolated window:** `$BD11→$FE60` takes **17 original CPU instructions**, ending with A/X/Y/P `00/0F/00/03`, **2,048/2,048 exact original internal-RAM bytes**, including the hardware stack (the window itself pushes no bytes; RTS only adjusts SP). Original BD11-derived RAM snapshot SHA `b3f29f02c3503f4e963fc4690b4f0323ef1c37012f9bf9d4b8be9a86e7d0e5d6`.

**Natural composed window:** `$FDFE→$FE60` takes **28 original CPU instructions** on the *same actor event*, ending with identical A/X/Y/P and destination. [Native composition](../src/scheduler_bd11_followup_0520.cpp) matches **1,792/1,792 original Mesen non-stack RAM bytes**; the original source executed `JSR $BD11` and changed its hardware stack. The two natural windows **overlap**, not two separate live gameplay events.

Original CPU path suffix after `$BD11` (17 instructions): `$BD11, $BD13, $BD1A, $BD1D, $BD10, $FE34, $FE36, $FE39, $FE3B, $FE45, $FE48, $FE4A, $FE54, $FE57, $FE59, $FE5C, $FE5E`, stopping **before** `$FE60 JSR $EF93`.

## Reconstructed decisions and explicit stops

[C++ source](../src/scheduler_bd11_followup_0520.cpp) and [header](../src/scheduler_bd11_followup_0520.hpp) expose `scheduler_bd11_and_fe34_0520` and a compositional `scheduler_fdfe_to_followup_0520` that reuses the authenticated 0519 `$FDFE` gate. They preserve the original source A/X/Y/P arithmetic and **do not modify RAM**.

| Source decision | Next original PC (stop) | Reason |
|---|---|---|
| `$BD11 LDA $A8` nonzero | `$BD15` | Before `JSR $E744`, not lifted |
| `$A8=0`, `$BD1A LDA $05EF,X` nonzero | `$BD1F` | Original actor descriptor/table path, not lifted |
| Fixed `$0470,X & $40` nonzero | `$FE4E` | Before `JSR $E2D0`, not lifted |
| Fixed `$054E,X=0` | `$FE6E` | Actor-loop advance, not lifted |
| Fixed `$0470,X & $20` nonzero | `$FE63` | Later fixed scheduler continuation, not lifted |
| Otherwise | `$FE60` | Before `JSR $EF93` (**naturally reached**) |

Native actor scheduler X domain is **1..18**. The source entry guards this domain and `$69` actor index. Source helpers beyond these transfer PCs are explicitly unimplemented, not approximated.

## Test results and evidence classes

- [Native unit regression](../tests/scheduler_followup_0520_test.cpp): **77,827** cases, consisting of 18×256×16 actor/attribute seed combinations, 4,096 connected natural-shape cases and three rejected actor index cases. Strict GCC C++20 optimized and AddressSanitizer/UndefinedBehaviorSanitizer builds passed.
- [Independent original-ROM differential](../tools/audit_scheduler_followup_0520.py): **14 CPU comparison windows**, two overlapping natural windows on one actual actor, and **12 RAM-injected synthetic cases** exercising unobserved branch alternatives. Exactly **28,416/28,416 compared RAM bytes** match; A/X/Y/P and original terminal PC match in every window.
- [Machine report](0520_original_mesen_followup_report.json) preserves case-specific original CPU counts, exit PCs, register results, source SHA hashes and outcome digest `a03c1b658acb5c8a05d18cfe27226cfafce6538ec21cdf6326e4603320b4a058`. Original commercial ROM, emulator binary, savestate and RAM snapshots are not committed.
- [Native replay executable](../tools/native_followup_replay_0520.cpp) compares original system RAM and terminal registers, excluding only the original JSR stack for the composed `$FDFE` path.

Reproduction requires the user's private original ROM, matching independent Mesen-agent/core and original 0519 private natural `$FDFE` savestate:

```sh
cmake -S JP/decomp/legacy/standalone0509 -B build/standalone0509 -DCMAKE_BUILD_TYPE=Release
cmake --build build/standalone0509 --parallel
ctest --test-dir build/standalone0509 --output-on-failure
python3 JP/decomp/tools/audit_scheduler_followup_0520.py "$ORIGINAL_JP_ROM" \
  --mesen /path/to/mesen-agent \
  --natural-FDFE-state /private/natural_stage1_actor15_FDFE.mss \
  --native-replay build/standalone0509/native_followup_replay_0520 \
  --report /tmp/0520_original_scheduler_report.json
```

GitHub CI exercises the public ROM-free native gate, CMake/CTest, preservation archive and Python `py_compile`; independent retail-ROM differential replay is local/private.

**Next source frontier:** `$FE60 JSR $EF93` — original X-indexed `$057C` animation/timer decrement and descriptor lookup, followed by `$FE63` original banked actor callbacks. Other `$BD15/$BD1F/$FE4E/$FE6E` gates still require implementation. No full actor frame, positive collision, renderer or VRC6/PPU/audio parity. **New certified PRG bytes: 0; strict PRG floor 49,504/262,144 (18.8843%); VPP 27/100; last completed certified semantic checkpoint 0508; fixed frontier $FB96 unchanged.**
