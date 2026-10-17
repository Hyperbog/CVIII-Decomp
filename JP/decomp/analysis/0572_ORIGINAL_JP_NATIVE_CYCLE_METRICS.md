# JP 0572 — original-ROM cycle runner records native/interpreted execution metrics

Previously `nesrecomp_cycle_0568.py` considered an external C11
runner's return code zero sufficient to report a successful
bounded launch. That could hide interpreter-only activity or a
misaddressed instruction loop, as the earlier synthetic
0569/0570 fixture demonstrated.

The cycle-output parser in `check_cycle_stats_0571.py` now has
two deliberately separate interfaces:

- `parse(stdout, expected_frames)` extracts true reported frames,
  total CPU cycles, native CPU cycles and interpreted ROM/RAM
  instructions. It does **not** assume a minimum native fraction.
- `check(stdout, frames)` additionally requires at least 99%
  native CPU cycles, zero interpreted instructions and a minimum
  cycle count **only** for the corrected synthetic VRC6 ROM.

The authenticated retail-JP local runner `nesrecomp_cycle_0568.py`
now *requires* the external cycle compiler/runner to report the
expected frame count and parseable CPU statistics. It writes
`cpu_execution` into private `jp_cycle_0568.json` with the
observed C compilation fraction and interpreter counts. A ROM
that compiles yet interprets most of its CPU cycles is now
clearly labeled rather than silently presented as native success.

`test` smoke includes a deliberate 574/86958 native-cycle,
5-interpreted-ROM fixture: `parse` accepts it as a measured
original-style result, while `check` rejects it as insufficient
for the synthetic high-native threshold. Actual original Japanese
ROM traces, screen pixels, gameplay correctness and Mesen frame
parity are **not** certified by this runner alone.

VPP27/100, strict49,504/262,144, historically compiled sites4261.
