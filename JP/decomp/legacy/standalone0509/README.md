# ROM-independent native actor/OAM technical preview (0509)

This is a **compiled, runnable, ROM-independent subsystem preview**, **not**
Castlevania III gameplay, a playable decompilation, or a pixel-accurate NES PPU.
It deliberately uses a procedure-generated two-object sample and procedure-
generated CHR tiles; no original retail PRG, CHR, enemy logic, music, physics,
ROM banks, screenshots or savestates are embedded or read at runtime.

It does execute **three independently reconstructed game-specific mechanisms**:

* `actor_slot_0509.cpp`: source-authenticated fixed JP `$FF06-$FF14` vacant
  actor-slot scan, `$FF15-$FF23` four-field clearing and `$FF24-$FF55`
  eighteen-field clearing. No invented writes to `$054E,X` or `$0400,X`.
* `oam_renderer.cpp`: already-audited JP raw bank `$0D:$8001` sprite-set
  pointer reads, 8-bit frame offsets, compressed record/attribute reuse,
  rotated OAM indexing and unused-slot filling.
* `collision_math.hpp`: previously audited JP raw bank `$0B` 8-bit coordinate
  deltas, with wraparound and strict less-than distance tests.

A small host-side scene harness supplies **synthetic** actor positions, fake
pointer tables and fake 2bpp tiles. Its demonstration input rules, movement,
contact counter, fake backdrop and RGB palette are **not** reverse-engineered
game behavior. Its software OAM presenter decodes 8x8 planar sprite patterns,
H/V flips, NES OAM Y+1 convention, transparency, OAM priority order and an
8-sprites-per-scanline limit. It does **not** reproduce the PPU background,
sprite-zero hit, scroll, true palettes, 8x16 modes, rendering/IRQ bus timing or
other original-game behavior.

## Build and run without any ROM

```sh
cmake -S JP/decomp/legacy/standalone0509 -B build/standalone0509 -DCMAKE_BUILD_TYPE=Release
cmake --build build/standalone0509 --parallel
ctest --test-dir build/standalone0509 --output-on-failure
build/standalone0509/cviii-standalone-preview 120 R /tmp/native_sprite_preview.ppm
```

The preview CLI takes exactly three arguments: number of frames `0..10000`,
a nonempty **cyclic** input-character pattern, and an output `.ppm` path.
Inputs: `R` move right, `L` move left, `J` show raised player tile, `X` remove
synthetic enemy (through the original 18-field helper, plus **explicit
host-owned** visibility/occupied updates), `.` idle. This is a deterministic
batch preview, not interactive player control. Output is a 256x240 binary PPM.

`120 R` reproducibility golden: PPM SHA-256
`8fa8089375dc5c1bd9cb1bbb40af6a2670019f33a6f049252c8c06c08e9867d4`.
The RGB buffer FNV-1a-64 is `1722600615a58168` (hex); the initial fixture
FNV decimal is `12363773589731306269`.

## Test and proof boundary

`actor_slot_0509_test.cpp` exhausts **all 4096** occupancy bitmaps for 12 scan
slots; runs the original 4-field and 18-field address writes across all 256 X
values; explicitly checks no unrelated RAM mutation. `standalone_scene_0509_test.cpp`
checks actual original OAM assembly inputs/outputs, a 120-step deterministic
frame sequence, source actor cleanup, exact procedural RGB golden and consistent
replay. CTest has three ROM-free tests. CMake Release assertions are deliberately
enabled with `#undef NDEBUG` in both test entrypoints.

With a privately supplied original Japanese ROM, additionally run:

```sh
python3 JP/decomp/tools/audit_actor_slot_0509.py "$ORIGINAL_JP_ROM" /tmp/actor_slot_hash_only.json
```

That hash-locks the original fixed `$FF06-$FF11` and `$FF14-$FF55` source bytes
and decodes every `$FF15/$FF24` write operand, ensuring the native field list
is not inferred from game conventions. The original bytes were **already
strict-certified in checkpoint 0508**. Therefore **zero new strict PRG bytes
and zero new VPP points** are earned by this demo. This is a stepping stone to
real frame-state conversion and reconstructed object-state gameplay, not a
substitute for those tasks.
