# 0542 — Original JP bank `$0A` room descriptor gate: both outcomes translated

## Scope

This pass closes **both conditional exits** of the room descriptor decision at
`raw0A:$B873` for the authenticated Japanese Akumajō Densetsu ROM:

- **Non-sentinel** `$07A6 = 0..8`: fixed `$E526` mapper setup → raw `$B4CC` inline
  state dispatch → `$B597/$B689` substate dispatch → `$B6A4` → `$B873` →
  `$E843` descriptor header formatter → `$B894` zero run → `$E86B/$EC70`
  terminator append → `$B89F` index increment → `$B6AD` early return →
  `$B5A2` return to synthetic caller `$9000`.
- **Sentinel** `$07A6=9`: existing 0541 original `$B873/$B8A4` carry-set
  return → `$E785` clear parallel object slots → `$B7F7` bank `$0E` room loader;
  stops at `$B6B4` without pretending downstream code is translated.

The branch explicitly uses the inline pointer tables after `JSR $E7FB`, **not**
an invalid fallthrough through those pointer bytes. CPU PC addresses here are
mapped to authenticated 16 KiB physical VRC6 bank `$0A` or fixed PRG31.

## Verification

JP retail NES SHA-256:
`958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`

Raw physical VRC6 `$0A` SHA-256:
`1460df577d44e114c64fdf34a8837629765f3f6a93d45796fdf81e5ffacb5ed8`

`python3 JP/decomp/tools/test_room_gate_0542.py --smoke`

With original legally supplied JP ROM (not committed to GitHub):

```bash
python3 JP/decomp/tools/test_room_gate_0542.py --rom "$ORIGINAL_JP_ROM" --out /tmp/room_gate_0542
python3 JP/decomp/tools/test_room_gate_0542.py --rom "$ORIGINAL_JP_ROM" --out /tmp/room_gate_0542_clang --cxx clang++
python3 JP/decomp/tools/test_room_state_0541.py --rom "$ORIGINAL_JP_ROM" --out /tmp/state_0541
python3 JP/decomp/tools/test_room_loader_0540.py --rom "$ORIGINAL_JP_ROM"
```

**Original NMOS 6502 opcode execution vs independent native C++:**

| Scope | Cases | GCC | Clang |
| --- | ---: | --- | --- |
| Raw `$0A` nine structural descriptors, all 256 initial-register/flag seeds | 2,304 | PASS | PASS |
| Fixed `$E526` → sentinel gate / `$E785`/bank `$0E` loader (0541 regression) | 1,280 | PASS | PASS |
| Original stand-alone bank `$0E` five-stream loader (0540 regression) | 1,280 | PASS | Optional independent replay |

For 0542, every comparison includes the full original `$0300-$037F`
128-byte output buffer, `$1D/$1E/$5E/$5F/$10/$19/$68/$07A6`, CPU X/Y and
NZC results, mapper state/write/read counts, return PC and stack depth.
The original interpreter actually executes original opcodes at `$E843`,
`$E86B`, `$EC70`, all state dispatches and `$B873`, with its own stack.
The C++ implementation independently reproduces the bounded semantic effects.
All nine source descriptors contain 64 zero-run bytes and are followed by
index 9's `$FF` sentinel. Source pointers are checked, with negative tests
for altered tables, descriptor type/count and invalid input image.

## Evidence limitations

- `$07A6=0..8` is a **structurally indexed candidate domain**, not a proven
  global producer domain or live NMI/state history. Input RAM `$19=2`,
  `$68=0` is deliberately seeded at the start of the test.
- No claim of an actual live Mesen execution capture, PPU/APU effects, IRQ
  timing, cycle fidelity, original cartridge controller history or entire game.
- The **non-sentinel** path correctly skips object clearing/loading.
  The **sentinel** path was already covered by 0541 and remains stopped at
  `$B6B4` where subsequent `$B49A/$FBBB` dispatches are not yet translated.
- Bank `$0A` still has 2,910 *unverified code candidates* and 3,684
  *unresolved* bytes. This checkpoint adds **zero** new strict semantic PRG
  bytes. Overall strict PRG stays 49,504/262,144, VPP 27/100.

## Next bank-level acceptance target

Continue *this same bank*: implement original `$B6B4-$B6E7` follow-on room
initialization and its `$B49A/$FBBB` cross-bank script dispatch with genuine
mapper and return-contract checks. Only claim a native room-state transition
when that downstream path reaches its actual `RTS` and matches original CPU
state, not merely a bounded prefix.
