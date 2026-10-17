# Checkpoint 0543 — Japanese raw0A post-loader dispatch, native replay

## Full caller scope, without overstating callback coverage

The active target remains **the entire original 16 KiB PRG bank raw `$0A`**.
This checkpoint connects the already authenticated fixed `$E526` -> state `$19=2`,
substate `$68=0`, descriptor sentinel `$07A6=9` -> object loading path
through the entire original subsequent caller:

`raw0A:$B6B4–$B6E7` -> `raw0A:$B49A` -> `fixed31:$FBBB` ->
foreign script target -> `fixed31:$FBC9` -> `raw0A:$B4EE` ->
`raw0A:$B6E7` -> `raw0A:$B597/$B5A2` -> original synthetic `$9000` return.

All opcode bytes, selectors, original CPU execution and physical bank identities
come from user-supplied original Japanese ROM SHA256
`958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.
**No original ROM is committed.**

## Six original cross-bank dispatch calls

The actual original bytecode in `$B6C0–$B6E1` performs 6 `JSR $B49A` calls,
with IDs `[0, 1, 2, 6, 3, 4]`. The 3-byte little-endian
pointer/physical-bank table begins at raw0A:`$B4B1`.

| ID | CPU target | ROM mapping | Native treatment | Status |
|---:|---|---|---|---|
| 0 | `$84A0` | raw bank `$00` | explicit neutral RTS callback | **Unimplemented foreign body** |
| 1 | `$8001` | raw bank `$00` | `LDY $054E` / bounded lookup / stores `$38/$39` | Original script opcode parity |
| 2 | `$8013` | raw bank `$00` | explicit neutral RTS callback | **Unimplemented foreign body** |
| 6 | `$8F3E` | raw bank `$00` | stores `$3C=40`, `$3F=43` | Original script opcode parity |
| 3 | `$D03C` | fixed bank PRG30 `$C000–$DFFF` | explicit neutral RTS callback | **Unimplemented foreign body** |
| 4 | `$D0CD` | fixed bank PRG30 `$C000–$DFFF` | explicit neutral RTS callback | **Unimplemented foreign body** |

The fixed bank remains mapped at `$C000–$DFFF` even when mapper raw bank `$00`
is selected at `$8000–$BFFF`. The original `$FBBB` trampoline makes the
physical bank `$00` selection by `JSR $E2D0`, pushes a special return address,
then jumps indirectly through zero page `$16/$17`. A callee `RTS` enters the
original fixed-bank restore stub `$FBC9` which maps raw `$0A` and `RTS` back to
the script caller. Six map/restore pairs are compared, including exact ordered
mapper writes, destination addresses, pointer ZP bytes, bank context, stack
pointer at callee entry, and `$3F` at call entry.

The four neutral callbacks are deliberate **test doubles only**: the CPU side
pops the *authentic* 6502 stack frame while the native side skips the unported
body. Comparison of caller return state **cannot certify behavior** of those
four scripts. Calls 1 and 6 execute authentic original instruction bytes in the
reference interpreter and distinct native C++ translations.

## Reproducibility

From a checkout with the user's original JP ROM:

```sh
python3 JP/decomp/tools/test_postdispatch_0543.py --smoke
python3 JP/decomp/tools/test_postdispatch_0543.py --rom "$ORIGINAL_JP_ROM" \
  --out build/0543-postdispatch-gcc --cxx g++
python3 JP/decomp/tools/test_postdispatch_0543.py --rom "$ORIGINAL_JP_ROM" \
  --out build/0543-postdispatch-clang --cxx clang++
```

The generated report includes original and host JSONL traces, trace diff and
first-divergence information. Results on the authenticated original:
**1,280/1,280 matching cases for each of GCC and Clang**, five locally
bounded stream IDs times 256 seed register/flag configurations. The bridge
reaches `$B5A2` and restores the original test caller stack (`SP=$FD`), raw
bank `$0A`, ZP `$23=$0A`, `$68=1` and original `$07A6=9`.

ROM-free CI checks 1,280 synthetic host cases and **seven negative inputs**:
tampered early and unused pointer-table records, wrong raw bank, modified
final pointer, disallowed stream header selector, short raw-bank image and bad
CLI mode. Original ROM test rejects a modified original ROM by SHA256.

The previous 0540 loader, 0541 prefix, 0542 non-sentinel branch and 0538
whole-cartridge 393232-byte exact reconstruction all passed locally.

## Strict limitations / next bank work

- Original state `$19=2`, `$68=0`, `$07A6=9` and room index 0..4 are seeded
  by a bounded test fixture: **not globally proven live gameplay states**.
- Four foreign script bodies `0,2,3,4` remain unimplemented and use test
  callbacks. The test does **not** reconstruct the actual graphics, room
  initialization, PPU/APU/IRQ effects, timing or entire original game.
- 2,910 bank `$0A` *candidate instruction* bytes and 3,684 *unresolved* bytes
  remain unpromoted. Strict semantic PRG remains 49,504 / 262,144, VPP 27/100;
  no new strict credit claimed.
- The next complete-system step is to translate and test the remaining four
  original script bodies with their actual code, memory, and hardware side
  effects and remove the test doubles one by one; then verify mapper-aware
  frame liveness in an original emulator.
