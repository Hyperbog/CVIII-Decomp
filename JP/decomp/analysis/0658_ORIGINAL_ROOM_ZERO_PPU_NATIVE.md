# JP0658 — Original Japanese room state-zero RAM + PPU clear, native C11 parity

**Source authority:** owner-supplied Japanese *Akumajou Densetsu*
iNES Mapper24/VRC6, exactly 393,232 bytes,
SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.
This pass reconstructs a **full connected conditional room initialization
transaction**, not another pointer index: physical raw 16KiB PRG bank0A
`$B570–$B58B` selects fixed PRG31 helpers for room RAM reset,
the entire nametable reset-data interpreter, and returns with
`$19=1`. Original game/NSF assets are never shipped.

## Original routine closure, with independently pinned bytes

| Physical original source | CPU interval (inclusive) | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| raw 16KiB PRG0A (mapper condition) | $B570–$B58B | 28 | `93e1bf0880ea31d9c31e161e7d9e965dbbef0b290e48a14da232e5ed8c731708` |
| fixed 8KiB PRG31 | $E2C4–$E2C9 | 6 | `4a9672995666573a7e4d5a3a02bc4df52437b91e2fdf79a2551d55586236dd4a` |
| fixed 8KiB PRG31 | $E616–$E624 | 15 | `a1d890373fd26cc5f723317baf8eb678e6f4a21506db5376502de55de30e2131` |
| fixed 8KiB PRG31 | $E7B6–$E7FA | 69 | `a0553ee342963dc596ed48638067d5558d87a32b02649b429b18b6ebba5a1966` |
| fixed 8KiB PRG31 | $E16C–$E181 | 22 | `a0d8fb637f811579a693e598ae89a9db5c81054459ea254e32cb62760aa8aa04` |
| fixed 8KiB PRG31 | $E827–$E830 | 10 | `fe9dab3a7ce1bb29399af19923cf2e12165f9d17a0ed4bd6bebce71da6410060` |
| fixed 8KiB PRG31 | $EB82–$EBF6 | 117 | `e69aaaa7f343f00621a23d78aab2b018057a6ba29ac50d07aa1c34bc8ed287e8` |
| fixed 8KiB PRG31 | $ED89–$ED8E | 6 | `411ae3d34e7db4cc16edabd13701b0be0b67839c03cff09dc448693fb9aec613` |
| **fixed ROM data** PRG31 | $EC1D–$EC46 | **42** | `7500a17666fbd773b53c9d784e06ab1b1b12ffaa817c2d1ccae99a6c7a53054f` |

**273 original opcode/operand source bytes across eight disjoint
regions** plus **42 byte original PPU command stream** are joined
in this tested execution graph. All were previously source-indexed
and independently bounded in 0508 Phases 8/9 and other fixed-bank
work. Source mapping: raw0A only when $23=$0A for $8000–$BFFF;
$E000–$FFFF is physical fixed PRG31. This is a **conditional
source-program execution**, not a witnessed RESET-to-room Mesen
gameplay trajectory.

## Actual original behavior reconstructed

The $B570 entry initializes the room state:

- Fixed $E2C4 outputs mapper $C000=$1E, preserving the tracked
  bank $23=$0A; fixed $E616 writes $21=$20,
  $6A=$43=$40=$6F=0, and the caller outputs $B003=$20.
- Fixed $E7B6 writes **exactly 1,297 separate RAM addresses** to
  zero: $004D–$00DF, $00F0–$00F7,
  $0300–$03BF, $0400–$05FF,
  $0600–$069F, $06E0–$06FF, $0700–$07F5.
  The saved $0781 is restored after it is cleared.
  $07A0/$07A6/$0789 become zero; $07F6,
  $06A0 and $03C0 are **not** zeroed.
- The real $EB82 interpreter reads the pointer pair at
  $EBF7/$EBF8, resets the PPU address latch via $2002 reads
  and streams $EC1D–$EC46. Each initial PPU target is
  supplied **little-endian** in source but written high-byte
  first to $2006. A $7F opcode changes target.
  Each positive repeat count writes its following value to
  $2007 the specified number of times; the interpreter also
  supports literal high-bit commands. The $FF byte terminates.
- The original JP data yields **1,024 ordered PPUDATA writes**
  nominally at $2000–$23FF, then **1,024 more**
  nominally at $2400–$27FF: **2,048 events total**.
  If $2000 PPUCTRL increment bit 2 is set, each write instead
  increments VRAM address by 32, not 1, with 14-bit address
  wrapping. Do **not** claim 2,048 unique tile locations in
  that alternate increment mode. Final pointer $00/$01=$EC46,
  repeat scratch $02=$40, $FC/$FD=0.
- Original $ED89 restores PPUCTRL from $FF, then raw0A
  $B589 increments state byte $19 to **1** and returns.
  PPUSTATUS is fixed to zero in this explicitly bounded
  source-level comparison; there is **no PPU cycle, DMA,
  rendering or IRQ model**.

## Native implementation and replay results

- `JP/recomp/native/enhanced/cviii_room_ppu_stream_0658.h/.c`:
  portable C11 2,048-event PPU transfer planner driven by
  a caller-supplied **authenticated original physical fixed bank31**,
  preserving source stream/address bytes and increment mode.
  No original ROM arrays embedded.
- `JP/recomp/native/enhanced/cviii_room_state0_0658.h/.c`:
  complete room-state-zero *semantic memory/postcondition*
  calculator, returning 2KiB RAM, ordered PPU events, and
  mapper/audio register event plans. It refuses wrong input
  sizes, absent pointers, invalid room state or unbounded source,
  leaving the output unchanged on failure. The CPU stack
  page is explicitly **not simulated**.
- `JP/recomp/native/enhanced/cviii_room_state0_test_0658.c`:
  **512 fully synthetic** invented-stream scenario tests
  covering 256 RAM seeds × both 1/32 VRAM increments,
  checking 1,792 nonstack RAM bytes, all 2,048 ordered events,
  the $0781 preservation, 1,297 clear spans, both external
  register writes, source termination and fail-closed negatives.
  This fixture uses invented nonzero PPU data and invented
  VRAM addresses, **not bytes from the Japanese game**.
- `JP/decomp/tools/jp_room_clear_0658.py`:
  SHA-authenticates all eight original ROM code regions,
  the original 42-byte stream, raw physical bank0A and full JP
  ROM; invokes the committed **original opcode-fetched 6502**
  reference from `audit_0508_phase9.py`, including its
  `audit_0508_phase8.py` CPU predecessor. Compares complete
  1,792 nonstack RAM bytes, 2,048 ordered PPUDATA events,
  PPUCTRL/PPUMASK/PPUADDR event order, $C000/$B003 register
  writes, room state, source pointer and returns.
  The user ROM is never added to GitHub Actions.

**Locally against the original JP ROM**, an independently
instruction-fetched private 6502 replay of the same full
$B570 → $EB82 → $B58B path matched C11 for **512/512 cases**,
**5,392,384 authentic opcode steps**, **917,504 nonstack RAM-byte
comparisons** and **1,048,576 ordered PPUDATA event comparisons**.
Original step budget is **10,532 instructions per case**.
An additional isolated $EB82-only replay passed 256 more
original-opcode/native cases (6,593 original instructions each).
GCC/Clang strict C11 builds, Clang ASan+UBSan, 512-case
synthetic C11 suite and Python ROM-free smoke passed locally.

**Owner-private reproduction:**

```sh
python3 JP/decomp/tools/jp_room_clear_0658.py --smoke
cc -std=c11 -O2 -Wall -Wextra -Werror -pedantic -DNDEBUG \
  JP/recomp/native/enhanced/cviii_room_ppu_stream_0658.c \
  JP/recomp/native/enhanced/cviii_room_state0_0658.c \
  JP/recomp/native/enhanced/cviii_room_state0_test_0658.c -o /tmp/jp0658-test
/tmp/jp0658-test
cc -std=c11 -O2 -shared -fPIC \
  JP/recomp/native/enhanced/cviii_room_ppu_stream_0658.c \
  JP/recomp/native/enhanced/cviii_room_state0_0658.c -o /tmp/libjp0658.so
python3 JP/decomp/tools/jp_room_clear_0658.py \
  --rom "/private/Akumajou Densetsu (Japan).nes" \
  --native-lib /tmp/libjp0658.so --seeds 256
```

## Certification boundary

**This work adds real native C11 room-state initialization and
two-nametable PPU register transfer planning, not just a static
table or pointer catalog.** Its entire source is previously
accounted in historical 0508 research, and the comparison is
**conditional original-6502 opcode replay with synthetic RAM
initial states**, not an original-Mesen *natural gameplay*
witness. Native routines are compiled but **dormant**:
no live game RAM, mapper/audio, PPU, input, sprite, save or
rendered frame is changed by the commit. No actual original
pixel output or CPU-cycle/PPU-bus phase parity is proven.

Under the fixed VPP rubric, a proven *nametable reset* is
not a full background nametable **update/rendering pipeline**,
nor a natural room-transition engine. Therefore **VPP stays
29/100** (Stage/world 1/20, Rendering/PPU 5/10).
Strict semantics-certified PRG **49,504/262,144 (18.8843%)**,
independent original Mesen checkpoint **0508**, fixed PRG31
frontier **$FB96**, R-001/R-002 **OPEN**. No points, ROM
bytes or complete playable feature are falsely credited.
