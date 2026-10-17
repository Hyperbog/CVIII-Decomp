# JP 0571 — pinned upstream C11 mapper24 native-cycle verification

The corrected synthetic VRC6 cartridge (0570) was compiled and
executed for three frames by the pinned external `mstan/nesrecomp`
C11 cycle backend. Its GitHub Actions runner printed:

```
mode=native frames=3 cycles=86958 native_cycles=86951 (100.0%)
  interpreted: ROM 0 (0.0%)  RAM 0 (0.0%)
```

Those numbers represent approximately 99.99195% native
**CPU cycles in the wholly artificial test cartridge** and zero
fallback interpreter instructions. They do **not** prove the
commercial Japanese game's frames, sprites, audio or gameplay.

The 0569 synthetic workflow previously accepted exit status zero
alone. `JP/decomp/tools/check_cycle_stats_0571.py` now fails unless:
- exactly three simulated frames are reported,
- native CPU execution is at least 99% of total CPU cycles,
- zero ROM and RAM interpreter fallbacks are reported, and
- sufficient total cycles ran (at least 10,000 per frame).

A ROM-free negative regression mutates frame count, native
cycle ratio, ROM and RAM fallback counters, and missing statistics
to ensure the checker fails closed. The GitHub Actions workflow
parses the real upstream headless stdout instead of merely
trusting its process exit.

**Next source-backed milestone:** privately execute authenticated
retail JP mapper24 ROM with `nesrecomp_cycle_0568.py`, record the
native/interpret cycle split and first divergent original-game
frame, and compare independently against Mesen. The private
game ROM remains off public CI, and the upstream engine stays
an external PolyForm Noncommercial 1.0.0 dependency.

Historical strict PRG 49,504/262,144; VPP27/100;
prior 4,261 original compiled opcode sites unchanged.
