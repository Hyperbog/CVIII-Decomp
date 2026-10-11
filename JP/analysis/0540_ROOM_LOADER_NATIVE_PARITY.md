# 0540 — Native translation of original JP room-object loader (bank raw0A)

## Outcome

The original bank `$0A` routine `$B7F7-$B872` has an independently compiled
portable C++ semantic translation (`JP/native/room0a/room_loader_native.cpp`).
It processes the five indexed room streams at pointers stored in bank raw0A
`$B8C2-$B8CB`, reading stream records from original physical raw bank `$0E`
through the logically mapped `$FB96`/`$E2D0` helper path.

All **1,280 = 5 room indices × 256 seeded initial-register/flag cases** pass
independent execution comparison with a deliberately constrained interpreter
running the **original 6502 instruction bytes**, not the same C++ algorithm.
The five source streams contain **30 five-byte object records** in all.
Original physical bank identities and complete retail JP ROM are SHA-256
authenticated. Original commercial bytes are never committed.

## What the comparison actually checks

Each case compares the room index and initial seed, seven header/RAM fields,
stream pointer, object count, complete array of per-object six-RAM-field
results, mapping-back-to-bank-0A state, total bank-switch writes, read count,
**each ordered mapped bank0E read address and byte value**, last/first read,
final X, observed carry/zero/negative flags and selected zero-page/room RAM.
A single mutated mapped-read trace, object count, or mapper-write count is
rejected at the exact divergent case; mismatched original-ROM SHA is rejected.

The reference interpreter executes `JSR`, `RTS`, the original `$FB96` indirect
ROM reads and `$E2D0` mapper writes, including stack effects. The native
translation reads through an explicit bank-switching semantic boundary; it
is **not** a CPU emulator and does not generate actual NES bus cycles.

## Reproduction

With `g++`, Python 3.10+, and repository checkout:

```sh
python3 JP/tools/test_room_loader_0540.py --smoke
# Uses user-supplied original JP ROM, not present in public GitHub CI:
python3 JP/tools/test_room_loader_0540.py --rom "$ORIGINAL_JP_ROM"
# Generate full machine-readable original/native trace + first-divergence report:
python3 JP/tools/replay_room_loader_0540.py --rom "$ORIGINAL_JP_ROM" --out /tmp/cviii-room-replay
```

The complete original cartridge remains covered by existing source-builder
and full-bank exact-roundtrip regressions. The new translation neither changes
nor inflates historical strict PRG semantic classification metrics.

## Limits and subsequent integration

This **does not** prove that `$07A0` can only be 0..4 during actual gameplay,
or that fixed-bank callers reach this routine with the expected VRC6 mapper
state. It does not reproduce interrupt timing, PPU/APU/VRC6 audio, graphics,
other state transitions or entire-game runtime parity.

Next integration step: bind this tested native room-loader routine into the
original NMI scheduler/room-state progression with a mapper-qualified original
execution trace and executable native game-state harness. Keep the active
full-bank `$0A` workstream open for 2,910 uncertain opcode candidates and
3,684 unresolved source bytes.
