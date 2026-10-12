# 0547 — Original NMI state dispatcher connected to native six-script room initialization

This checkpoint extends the **bounded, conditional** Japanese VRC6 6502/native room setup from the fixed-bank game-state entry `$E526` to its authentic fixed-bank NMI state-dispatch routine `$E35C` and original inline `$E7FB` trampoline. It **does not** execute the complete NMI handler, demonstrate reset-to-gameplay reachability, or establish PPU/APU/frame parity.

## Original, authenticated entry and dispatch

The iNES NMI vector (`$FFFA-$FFFB`) is `$E057`. The full NMI handler has a direct `JSR $E35C` at `$E0BF` on its `$1C=0` branch. Earlier NMI work before `$E0BF` involves other original game routines that are **not** emulated by this checkpoint.

The original `$E35C-$E362` state-dispatch entry executes `INC $1B; LDA $18; JSR $E7FB`. `$E7FB-$E813` uses the `JSR` return address as the inline-table base, indexes the table by `2 * state`, restores `Y`, and tail-jumps through `JMP ($0002)`. It does **not** return normally from the dispatcher.

The original 16-state `$E363` pointer table is:

| `$18` index | Target | `$18` index | Target |
| --- | --- | --- | --- |
| 0 | `$E383` | 8 | `$E50E` |
| 1 | `$E436` | 9 | `$E516` |
| 2 | `$E437` | 10 | `$E541` |
| 3 | `$E449` | 11 | `$E549` |
| 4 | `$F390` | 12 | `$E51E` |
| 5 | `$E459` | **13** | **`$E526`** |
| 6 | `$E49B` | 14 | `$E52E` |
| 7 | `$E539` | 15 | `$E531` |

**Conditioned fixture:** set `$18=13, $19=2, $68=0, $07A6=9, $07A0=0..4`. Start authentic 6502 opcode execution at `$E35C` and continue through `$E526`, bank `$0A` inline state dispatch, bank `$0E` object stream loading, and the six original bank0/PRG30 room-init scripts (`0,1,2,6,3,4`) until the original caller returns at `$9000` (a synthetic test harness return). The scenario **does not claim** those RAM selectors are observed in live gameplay.

`$1B` is initialized for each case as `(19 * seed + 31 * room_index) & 255`, then incremented by the original `INC` instruction, including wraparound. Original opcode trace covers all 18 instruction starts in `$E35C..$E362` and `$E7FB..$E813`. Native C++ independently translates the dispatcher, validates the original fixed-bank opcodes/callsite/vector/table, and continues through the existing six-script host path.

## Reproducible tests

Without commercial ROM bytes:

```sh
python3 JP/tools/test_nmi_dispatch_0547.py --smoke
python3 JP/tools/test_postdispatch_0543.py --smoke
```

`test_nmi_dispatch_0547.py --smoke` executes the original dispatcher opcodes in 16 synthetic states and four deliberate corruptions. `test_postdispatch_0543.py --smoke` compiles portable native C++ and checks 1,280 synthetic NMI-stage integrated cases, plus four native corruption rejections; no original media are needed in GitHub Actions.

With the authenticated Japanese original ROM supplied locally, not committed:

```sh
python3 JP/tools/test_nmi_dispatch_0547.py --rom "$ORIGINAL_JP_ROM" --out build/0547_nmi_gcc --cxx g++
python3 JP/tools/test_nmi_dispatch_0547.py --rom "$ORIGINAL_JP_ROM" --out build/0547_nmi_clang --cxx clang++
```

**Local results:** 1,280/1,280 original-6502 vs native-C++ traces match for GCC, and 1,280/1,280 for Clang; original-ROM test also executes all 16 selectors and validates their target addresses. Direct comparison includes the same complete six-script RAM, mapper, video-register, and command-buffer outputs as checkpoint 0546, plus the original NMI inline-dispatch instruction-site trace and `$1B` state counter.

Previous 0540 room-loader, 0541 state chain, 0542 alternate gate, 0546 complete six-script postdispatcher (1,280/1,280), and full 25-bank exact 393,232-byte cartridge rebuild remain passing. The user-supplied original ROM is never placed in the repository or source package.

## Explicitly unresolved

- The original reset (`$E00B`) and complete NMI (`$E057`) handlers are **not** executed here.
- The original game's producer of `$18=13`, `$19=2`, `$68=0`, `$07A6=9` in a live gameplay frame is not established.
- No PPU, APU, NMI/IRQ ordering, DMA or cycle-exact gameplay comparison is claimed.
- ROM-free fixture data are deliberately artificial. Neither a passing synthetic trace nor an exact ROM rebuild certifies semantic gameplay coverage.
- Strict global PRG certification stays **49,504/262,144** and VPP **27/100**; bank `$0A` still includes 2,910 unverified code candidates and 3,684 unresolved bytes.

Next milestone: capture or replay a verified **real reset-to-room selection** through authentic CPU/mapper/PPU state, eliminating the injected `$18=13` assumption and comparing native frame outputs against that captured scenario.
