# 0548: Original JP reset-to-NMI boundary — authenticated CPU, scripted hardware

## Main result

Checkpoint 0547 used an injected `$18=13` at fixed-bank `$E35C` to exercise the already-translated full six-script room path. Checkpoint 0548 **removes that injected state** and executes original CPU instruction bytes from the JP reset vector `$E00B`.

For the authenticated original JP iNES image (SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`), the deterministic but *synthetically clocked* reference harness observes:

| Boundary | Observed | Evidence class |
| --- | --- | --- |
| Reset vector | `$E00B` | Authenticated original ROM bytes |
| Boot initialization completed | `$E04B` after 6,419 executed 6502 instructions | Original instruction execution under scripted I/O |
| NMI vector | `$E057` | Authenticated original ROM bytes |
| NMI scheduler callsite | `$E0BF: JSR $E35C` after total 6,905 instructions | Original instruction execution |
| `$18` at initial scheduler call | **`$00`**, not `$0D` (13) | RAM state produced by reset execution |
| `$1C` at initial scheduler call | `$01` (re-entry guard raised) | Original instruction execution |
| mapped 16K PRG bank at call | `$0C` | Scripted VRC6 CPU bus mapping of original mapper writes |
| First NMI fully returned | `$E0D6: RTI` after total 11,740 instructions | Original CPU execution under scripted I/O |
| `$18` on NMI return | `$00` | No state-13 reachability demonstrated |
| `$1C` on NMI return | `$00` | Original handler cleared re-entry guard |
| Mapped 16K bank after return | `$0D` | Original mapper writes under modeled bus |

Original state-dispatch table `$E363` selects `$E383` when `$18=0` and `$E526` when `$18=13`. Both offsets are from authenticated ROM bytes. The new reset/NMI replay observes `$E383` in the original CPU instruction trace. The previously compiled `$E526` room path remains **conditional and not yet proven reachable from reset**.

For additional limited exploration, an **artificial schedule of 80 NMIs** (120 original main-loop instructions between synthetic interrupts) remains in `$18=0`; `$19` changes from 0 to 1. This is *not 80 real frames* and cannot establish that the game stays in state 0 on actual hardware. It is useful only as a scoped diagnostic and negative check against automatically claiming state 13.

## Exact execution boundary and intentionally unsupported behaviors

`replay_reset_0548.py` executes original 6502 opcodes, stack/call/return, branches and zero-page RAM, PRG-bank mapping and fixed-bank reads. It rejects unknown opcodes and incorrect ROM hashes. The interface uses a 151-entry official opcode table; this is an instruction-level test interpreter, **not a certified emulator**.

- PPU `$2002` status returns **0 on first poll and `$80` on subsequent polls** to satisfy reset's two vblank waits; this is an invented test source, **not a console timing model**.
- The first NMI is inserted at the main-loop boundary; subsequent NMIs, when requested, are also scripted. No PPU-cycle, DMC, OAM DMA stall, or IRQ/frame scheduling fidelity is asserted.
- PPU `$2007` reads return zero; controller `$4016` returns no-buttons; unsupported APU reads are logged as unmodeled. ROM contents are never modified and game media are not embedded in source or CI.
- No native C++ implementation of reset or state-0 handler is claimed. The native C++ room path proven in 0546–0547 remains separate and conditional.
- No strict PRG certification credit. The bank `$0A` candidate/unresolved counts and global strict coverage are unchanged.

## Reproduction

```sh
python3 JP/tools/test_reset_0548.py
python3 JP/tools/test_reset_0548.py --rom "$ORIGINAL_JP_ROM" --out /tmp/jp_0548_reset.json
python3 JP/tools/replay_reset_0548.py --rom "$ORIGINAL_JP_ROM" --through-first-nmi --out /tmp/jp_0548_first_nmi.json
python3 JP/tools/replay_reset_0548.py --rom "$ORIGINAL_JP_ROM" --synthetic-frames 80 --out /tmp/jp_0548_synthetic_nmis.json
```

The ROM-free tests exercise CPU addressing, carry/borrow, stack discipline, NMOS indirect-JMP page wrap, NMI/RTI, unknown-opcode rejection and source authentication rejection. The optional original-ROM tests assert the bounded reset/NMI observations and 80 scripted NMI results. Neither test contains original ROM data.

## Next correctness gate

A real reset-to-state-13 reachability claim requires **emulator-observed frame traces** with authentic VBlank/PPU, controllers, timing, original physical PRG mapping, game input conditions, and write provenance for RAM `$18`. Instrument MesenCE or another cycle-aware NES+VRC6 reference before marking an observed game transition as live; compare trace against this synthetic CPU baseline and the verified native `$E526` room path. If it diverges, investigate the first mismatching memory or mapper event, **not** mutate test golden results.
