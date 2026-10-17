# 0541: Original fixed `$E526` -> bank `$0A` room-state dispatcher -> native room-loader bridge

## Delivered execution path

This original-ROM-backed checkpoint closes one **conditionally entered, multi-routine
state-chain** up to its next unresolved behavior at bank `$0A` CPU `$B6B4`.
It is not a complete state-machine, full frame or game port.

Initial conditions are explicit: `$19=2` (room state), `$68=0` (substate),
`$07A6=9` (end-of-room descriptor sentinel), `$07A0=0..4` (five bounded stream
indices), and 256 different register/flag and filled-object-slot fixtures.
Entry `$E526` is a fixed-bank routine; the evidence proves its local behavior,
**not** that real NMI/gameplay ever supplies this complete condition.

Execution performed by the original-opcode reference interpreter:

1. Fixed `$E526: LDA #$0A; JSR $E2D0` sets mapper `$8000=0A`, then
   `JMP $B4CC` to physical bank 0A.
2. `$B4CC` calls the fixed `$E7FB` **inline-tail** dispatcher. The return
   address is consumed as a pointer to the inline state table; state 2 indexes
   original word at `$B4D5` -> `$B597`.
3. `$B597` calls `$B689`, whose own `$E7FB` inline-tail dispatcher reads
   substate 0 -> original word at `$B68E` -> `$B6A4`.
4. `$B6A4` calls `$B873`, and index `$07A6=9` selects the verified `$FF`
   descriptor at `$B8C1`. Thus the gate returns carry set via `$B8A4`, without
   invoking the other room descriptor/allocator path.
5. `$B6AE` calls fixed `$E785` to clear all **eight parallel object fields
   for slots 1..22**. Source-backed native translation does the same.
6. `$B6B1` calls `$B7F7`, which reads original bank 0E through `$FB96`
   and fixed mapper helper `$E2D0`. The trace checks all ordered mapped
   addresses and byte values, CPU flags, loaded fields, RAM state and mapper
   writes. Execution halts at `$B6B4`, before later unknown setup routines.

## A regression found and repaired

Earlier 0540 isolated fixtures initialized `$07A6=0`. The native C++ loader
also forced `$07A6=0`, but **the original `$B7F7-$B872` routine does not alter
this field**. In the new integrated sentinel condition `$07A6=9`, the old
native translation diverges. The C++ `load()` now preserves this field.
A permanent ROM-free nonzero `$07A6` assertion prevents reintroduction.

## Verification

- Original Japanese iNES SHA-256:
  `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`
- Original physical bank 0A SHA-256:
  `1460df577d44e114c64fdf34a8837629765f3f6a93d45796fdf81e5ffacb5ed8`
- Original physical bank 0E SHA-256:
  `9fc30168f3eca751de893aac2af31b5f4c40b8dcdcde1ad70b9614c607c29bb5`
- GCC 12/Clang C++17 exact compared original-opcode versus native translation:
  **1,280 / 1,280** frames matched, five indices * 256 synthetic seeds.
- Pre-existing standalone `$B7F7` path: **1,280 / 1,280** still passes
  under both GCC and Clang after the RAM field fix.
- Synthetic-bank ROM-free smoke (1280 cases) checks nonzero `$07A6`
  preservation, first/last mapped reads, all 22 object slot field tuples,
  reference inline dispatch target, sentinel gate and CPU stack exit.
- Negative tests reject three altered inline-dispatch/sentinel sites,
  a truncated bank image, unsupported CLI mode, and an altered retail ROM.
- No original commercial ROM is included in the repository or the CI.

Run from repository root:

```shell
python3 JP/decomp/tools/test_room_state_0541.py --smoke
python3 JP/decomp/tools/test_room_state_0541.py --rom "$ORIGINAL_JP_ROM" --out /tmp/jp-0541
python3 JP/decomp/tools/test_room_state_0541.py --rom "$ORIGINAL_JP_ROM" --out /tmp/jp-0541-clang --cxx clang++
```

## Evidence boundaries and next bank-completion gate

This is a **conditional bounded trace**, not an authenticated frame/NMI
liveness proof; `$19=2`, `$68=0`, `$07A6=9`, `$07A0=0..4` are explicitly
fixture-supplied. The code **after `$B6B4` is not yet translated**; other
`$B873` paths (indices 0..8) need native handling of `$E843` and `$E86B`.
No PPU, APU, IRQ, 8-bit timing or full-game parity is claimed. No new strict
source-certified PRG bytes or VPP points are claimed. The bank-wide 0538
candidate/unknown partition remains unchanged. Continue this *same bank*
through its remaining room descriptor and object initialization paths.
