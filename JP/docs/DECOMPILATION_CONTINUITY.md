# Akumajou Densetsu decomp/recomp continuity playbook

Durable handoff for `Hyperbog/CVIII-Decomp`, branch `decompilation`.

## Recovery

After interruption:

1. read `docs/INTERRUPTION_RECOVERY.md`, `docs/ACCELERATION_POLICY.md`, `docs/WHOLE_PRG_ATLAS.md`;
2. read `analysis/RESUME_STATE.json` and `docs/PROGRESS.md`;
3. inspect the live branch for commits newer than the state transaction;
4. run `python tools/check_resume_frontier.py <JP ROM>`;
5. run the audit named by `previous_checkpoint_audit`;
6. continue only after both pass.

Authority: JP ROM / observed JP execution -> reproducible JP-ROM audits -> NES/VRC6 hardware docs -> atlas, JP<->US matching and external disassemblies as accelerators. Never commit ROM-equivalent lossless dumps.

JP SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.
US comparison SHA-256 `1c7b2ed2c1fb5839a6764006aa476f5c9d48f99465b6141980f3a5af1dfec0d6`.

## Dashboard

```text
whole JP PRG scanned/indexed                 262144 / 262144 = 100%
strict semantically verified PRG floor        48821 / 262144 = 18.6237%
exact unique JP<->US correspondence           115865 / 262144 = 44.1990%
exact-or-normalized structural candidates     149607 / 262144 = 57.0705%
VPP                                             23 / 100
```

The two newest VPP points are native VRC6 PRG/CHR mapping and native VRC6 IRQ timing. Cross-version percentages remain candidate structural coverage only.

## Semantic chain through 0501

```text
IRQ + fixed NMI + ED46                    -> $10-clean on admitted graphs
raw bank $0C                              -> $10-clean on live admitted graph
raw bank $04 parser + 96/96 roots         -> $10-clean
raw bank $05 parser + 72/72 roots         -> $10-clean
$E7FB / 04FF / 0500 fixed graphs          -> locally $10-clean
0501 fixed scheduler                      -> locally $10-clean
0501 raw bank $09                         -> locally $10-clean
0501 raw bank $0A                         -> locally $10-clean
0501 raw bank $0B object/collision        -> WRITES $10 at 7 verified sites
PRG26 renderer                            -> consumes/persists inherited $10
```

0501 evidence:

```text
analysis/NMI_FIXED_SCHEDULER_BANKED_0501.md
tools/audit_nmi_fixed_scheduler_banked.py
```

0501 result:

```text
fixed PRG31                    161 starts    298 new bytes
raw bank $09                   479 starts   1050 new bytes
raw bank $0A                    57 starts    120 new bytes
raw bank $0B                  1338 starts   2896 new bytes
----------------------------------------------------------
0501                           2035 starts   4364 new bytes
```

Tagged manifest SHA `639e20f7e96e816a40ef4ef7d8585c809ce670ac5384f3c2fabc9a77d275737e`.
Strict floor **48,821 bytes = 18.6237%**.

Scheduler-proven bank roots:

```text
raw $0B: $80E3 $B1F8 $BD11 $8001 $8161 $826C
raw $09: $8001
raw $0A: $84EA
```

`$FE95` shifts `$0565,X` right six times and dispatches via `$E7FB`. `$FE98-$FE9D` contains exactly three pointers `$FE9E,$FEB1,$FEC6`; `$FE9E` is code, not a fourth pointer. Live selector `$03` is still open.

Verified raw-$0B direct `$10` stores:

```text
$B3B6 $B3D2 $B40E $B460 $B65F $B740 $B76C
```

0502 has already sharpened their ordering: all seven are reachable only below scheduler-called `$B1F8`. Fixed `$FDE4` calls `$B1F8` once near the start of each active object slot; later admitted per-slot bank `$09/$0B/$0A` calls are `$10`-clean. Therefore the renderer-facing value is the last `$B1F8` scratch write made by a later active slot that takes one of those paths, or older inherited `$10` if no such path writes it.

## Native VRC6 components

Mapper evidence:

```text
analysis/NATIVE_VRC6_MAPPER.md
src/vrc6_mapper.hpp
src/vrc6_mapper.cpp
tests/vrc6_mapper_test.cpp
```

IRQ evidence:

```text
analysis/NATIVE_VRC6_IRQ.md
src/vrc6_irq.hpp
src/vrc6_irq.cpp
tests/vrc6_irq_test.cpp
```

The mapper implements target PRG RAM/PRG/CHR/CIRAM mapping. The IRQ source implements `$F000/$F001/$F002`, cycle mode and scanline-mode **114,114,113** CPU-cycle cadence, reload/ack behavior and pending IRQ state. Both compile with `-Wall -Wextra -Werror` and pass exact-ROM regression tests. CPU-side IRQ polling/latency, PPU integration and VRC6 audio remain open.

## Cross-version accelerators

Exact matcher: 115,865 unique exact JP bytes (44.1990%), 821 runs, 73 conflicting overlap bytes excluded.

Normalized matcher: 24,014 unique matches; exact-or-normalized union 149,607 bytes (57.0705%); calibration 13,232/13,232 exact-supported starts agree with zero disagreements.

Files:

```text
tools/match_jp_us_exact.py
tools/audit_jp_us_exact_match.py
analysis/JP_US_EXACT_MATCH_SUMMARY.md
tools/match_jp_us_normalized.py
tools/audit_jp_us_normalized_match.py
analysis/JP_US_NORMALIZED_MATCH_SUMMARY.md
```

## Open edges / next checkpoint 0502

Primary: close `$B1F8` collision-sweep architecture and final `$10/$11` writer ordering/value domains. Resolve `$A15A/$A2CC/$A3A9` `$E7FB` sites and `$BD56/$BD64` indirect dispatches when relevant.

Also open: raw-$09 `$E5DA` callees; `$0565>>6` selector `$03`; `$18/$2C/$68` producer closure; `$FAA0-$FAA9`; complete mapper-register inventory; CPU/interrupt trace parity; full native memory/PPU/audio/runtime.

Raw fixed investigation frontier remains `$FB96`; 0501 was noncontiguous from `$FDE4` and mapper-selected callees.

```text
overlap $FB76-$FB95
SHA e4fa5e06e439ca12a84d935eb80224f448276c722399fe76fe0ce60013cc4ee7
fingerprint $FB96-$FBB5
SHA a5437f0f20034ba34d65afeec353d28846a321134061f765814d28eaa3f69157
raw tail $FB96-$FFFF
SHA 0cbfd0aa79f3c7d1db7a756c08c47bfe01cba321900fb8955e77ec8525d38d44
```

Transaction order: analysis -> audit -> exact-ROM run -> progress/continuity -> `RESUME_STATE.json` last -> recovery checker -> branch-head confirmation.
