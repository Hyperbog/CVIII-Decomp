# 0546: Six original foreign room-initialization scripts translated in bounded native replay

**Target:** authenticated Japanese Akumajō Densetsu PRG/VRC6; original SHA-256
`958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.
**Original runtime scope:** fixed `$E526` entry, original bank `$0A` room state `$19=2/$68=0/$07A6=9`, five structurally bounded indices `$07A0=0..4`, and original post-loader dispatch `$B6B4..$B6E7` returning through `$B5A2` to synthetic caller `$9000`.
**Result:** all six foreign-call IDs `{0,1,2,6,3,4}` now execute authentic original NMOS-6502 in the reference replay and independent C++ semantic translations in full-PRG mode; **no neutral/opaque callback on either side**.

## What changed beyond 0545

- **ID 3 (fixed PRG30 `$D03C..$D0CC`):** execute `$C900` and `$C905` bank selectors through the original fixed-bank `$C94B` 15-byte bank table; explicitly map physical bank `$07`/`$08` using the original `$E2D0` helper, read nested pointer structures using original bank-dependent ROM data and the fixed `$D8F9/$D953` tables, run original `$D449..$D474`, set RAM `$08..$0E`, `$4D/$4E`, `$65`, `$6E`, `$5A..$5D`, `$70`, then return through the authentic `$FBC9` mapping trampoline.
- **ID 4 (fixed PRG30 `$D0CD..$D149`):** translate the original `$65`, `$6E`, `$53/$54` comparisons and 6502 shift/rotate arithmetic into native C++, including the equality case that still writes RAM `$78`. Runs through real original `RTS` and the shared mapping trampoline.
- Native post-loader mode accepts a **256-KiB original PRG image** as an extra input, cross-checks its raw physical bank `$00/$0A/$0E` against the explicit separate bank inputs, rejects truncated/conflicting images, and replays scripts 3 and 4. ROM-free synthetic fixtures without that image remain intentionally labeled **mocked** at IDs 3/4 and cannot masquerade as authenticated parity.
- Reference emulator extended to the two original fixed-bank routines, their zero-page indirect loads, the mapped bank selector and 6502 `ASL/ROL/LSR/ROR`, signed branch, and CMP effects. Record per-case original mapper writes and all relevant RAM fields; native/reference comparison is field-by-field.

## Authenticated opcode/data region fingerprints (SHA-256)

| Physical region | CPU addresses [start,end) | SHA-256 |
|---|---|---|
| fixed PRG30 script3 | `$D03C..$D0CD` | `d5e1328814195466ff52bf9bc8695513ba5bd08d7f2f6c44bbf10439cccf60ac` |
| fixed PRG30 script4 | `$D0CD..$D14A` | `dfb4ad1f66dbc43839ef9f2c73d973804089f1f65a249a44fe057e224c91a7f3` |
| fixed PRG30 mapper selector | `$C900..$C94B` | `e82f4c346073fc6f9c193f41b33e897731b4fbcb422d2d8fe6b5b5acf9cad3ed` |
| fixed PRG30 pointer helper | `$D449..$D475` | `e92e2f99d26e0c6309adae41f07417e1d6c995345d519009edbcad3f4717ea28` |
| physical raw bank `$07` (16KiB) | `$8000..$C000` | `3728a0d3ea3efb82236cd738664ddc4696da75a1140e58eaf85bc2b66ce31446` |
| physical raw bank `$08` (16KiB) | `$8000..$C000` | `7390cac816d84a3937b6515c8e11769bd99e6ae356aafa2c92eb75583bf0960e` |

## Verification and real limits

**GCC:** 1,280/1,280 original-6502 vs. native C++ exact trace comparison, no neutral callbacks.
**Clang:** 1,280/1,280 original-6502 vs. native C++ exact trace comparison, no neutral callbacks.
Five bounded room indices and 256 initial CPU seeds; original script3 mapped physical raw `$08` for indices 0,1,3 and `$07` for 2,4, **twice per call**. Script4 `RAM[$65]` stayed `0` for those five room indices; **its negative-bit path has not been execution-verified**. The reference covers 43 original instruction starts in D03C-D0CC, 36 in D0CD-D149 and 35 in selected helper blocks (union over five original bounded rooms, not an exhaustive whole-bank CFG).

ROM-free synthetic smoke runs the existing 1,280-case fixture with visibly **mocked** scripts 3/4, plus an independent full-PRG artificial fixture and rejected short/mismatched inputs. Synthetic mode is not counted as original ROM parity. An original ROM must be supplied privately for authenticated replay. Previous 0540/0541/0542 native regressions and 0538 exact 393,232-byte 25-bank roundtrip pass unchanged.

```sh
python3 JP/tools/test_postdispatch_0543.py --smoke
python3 JP/tools/test_postdispatch_0543.py --rom "$ORIGINAL_JP_ROM" --cxx g++
python3 JP/tools/test_postdispatch_0543.py --rom "$ORIGINAL_JP_ROM" --cxx clang++
```

**Not proved:** reset/NMI/frame path reaching this input state, all room-index and special `$34=$0D/$0E` cases, full 6502 CPU flag-state equivalence, PPU/VRC6 register timing, full gameplay, or completed bank `$0A`. Source classifications remain 2,330 historically audited bytes, 2,910 candidate-code bytes, 7,460 structurally mapped data bytes and 3,684 unresolved bank bytes. Global strict PRG evidence stays **49,504/262,144**, VPP **27/100**. Native behavior parity for this bounded path is not a whole-game decompilation.
