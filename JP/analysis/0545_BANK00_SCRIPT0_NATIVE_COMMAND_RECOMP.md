# 0545 — Original JP bank-$00 script 0 fully exercised under bounded room startup

**Status:** Native semantic translation of the **entire script-0 return path** for all
five structurally valid source rooms, **not** proof of game-frame reachability,
cycle parity, or native reimplementation of scripts 3 and 4.

## Original code, not fabricated callbacks

In the original six-call raw-bank-$0A room initializer (IDs `0,1,2,6,3,4`),
script **0** enters physical raw PRG bank `$00` at CPU `$84A0`.
Its original 6502 instruction stream calls `$EC54` (which sets bank `$00` via
`$E2CA`, calls raw `$966F`, restores the prior bank via `$E62D`), the original
`$8480` two-stage room pointer decoder, and `$852F` (two further `$EC54` calls).
It writes the original `$0300` command stream and uses ROM-indexed two-dimensional
record tables `$86DF`, `$87DB`, and `$8929` to write video-command bytes into
`$02F4,X` and `$02F0,X`. These writes can overlap previously emitted command
bytes, so write **order** matters. All mapper writes associated with the helper
are captured separately from the six outer bank-zero/restored-bank mapper calls.

Authenticated original ROM SHA-256:
`958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.

| Original CPU block | Bytes | SHA-256 |
| --- | ---: | --- |
| raw00 `$84A0-$8511` | 114 | `2ba95131ee48d3ae4f90611e43b09e9e98eb6b540a4dcfd4ff6fb56557b5f30c` |
| raw00 `$8480-$849F` | 32 | `cb4b703cd1904b5545a70d63bbacae383e9174e18d3b04065ebebbdfd1fa30c5` |
| raw00 `$852F-$853C` | 14 | `28972833ea3ce47ddd789c34d4afc8ac990dfccec580b317bc199d0f28593a8a` |
| raw00 `$966F-$96B8` | 74 | `865d66d67f565897ce1c9918454ba6c6303a56d0229f9e9054509a7d58598655` |
| fixed31 `$EC54-$EC7A` | 39 | `9ad6266504d8b5b361050a74f0e13ecb56b944e86d327fd02de2583dcfc78f8c` |
| fixed31 `$E2CA-$E2D5` | 12 | `077b2331fe884703a221ad3a91a2b07a69129db981fb060b0b2a4df74dcc4fc6` |
| fixed31 `$E62D-$E632` | 6 | `8e3606562a89374cd3159f61e9db1785ccb7846f93d521aca62dbd9df3b0a81a` |

## Original-versus-native execution evidence

`replay_postdispatch_0543.py` **executes original opcodes** through script 0,
including `JSR` / `RTS` stack behavior, conditional branches, 6502 flag changes,
zero-page indirect memory accesses and bank-changing `$E2D0` calls. The reference
runs through its original return path, then scripts 1, 2, 6 and the existing
explicit neutral callbacks for 3 and 4, stopping at the actual `$B5A2` return.
The C++ implementation **independently interprets the original data formats**
in `dispatch_bank00_script0_commands`, which is not a copy of the reference CPU
execution loop. Each ROM-indexed command record is checked for bounds, termination
and output overflow.

**GCC:** 1,280/1,280 cases, original JP ROM, first divergence: none.
**Clang:** 1,280/1,280 cases, original JP ROM, first divergence: none.

Coverage: five structurally bounded rooms, 256 original initial-register/flag
seeds for each, 148 distinct traced original instruction starts across room
indices in the script-0 call chain, including fixed helper entries.
Per case: **94 internal raw-$00 mapper write events**, original command cursor
`$1E=48`, original `$0300-$037F` command bytes, `$02E0-$02FF` output bytes,
selected zero-page fields, six outer bank-switch/restoration pairs, eight video
register write events from script 2, and caller return state all match.

ROM-free CI: `test_postdispatch_0543.py --smoke` compiles native C++ and exercises
1,280 generated-index fixtures with **10 negative cases**, including invalid
script-0 pointer, unterminated/overflowing synthetic stream, malformed room
pointer and short bank image. No copyrighted game images in source or CI.

```sh
python3 JP/tools/test_postdispatch_0543.py --smoke
python3 JP/tools/test_postdispatch_0543.py --rom "$ORIGINAL_JP_ROM" --cxx g++
python3 JP/tools/test_postdispatch_0543.py --rom "$ORIGINAL_JP_ROM" --cxx clang++
```

The 0538 exact 16KiB bank and 393,232-byte cartridge rebuild, plus native
0540–0542 ROM-backed regressions, pass unchanged.

## Remaining authentic boundaries

Scripts **3** (`PRG30:$D03C`) and **4** (`PRG30:$D0CD`) are still neutral test
callbacks on both reference/native sides, **not reconstructed**. The original
fixed helper/PPU command buffer effects are compared, not a frame-accurate PPU
renderer. `$19=2, $68=0, $07A6=9` is a controlled conditional startup case;
actual reset/NMI gameplay reachability remains **unproved**.

Strict PRG evidence remains **49,504/262,144**; VPP **27/100**; raw0A
originally audited 2,330 source bytes, 2,910 unverified instruction candidates,
7,460 structurally typed data, and 3,684 unresolved bytes. No new strict
code/data credit from this native replacement.
