# Akumajou Densetsu decomp/recomp continuity playbook

Durable handoff for `Hyperbog/CVIII-Decomp`, branch `decompilation`.

## Mandatory recovery

After any interruption:

1. read `docs/INTERRUPTION_RECOVERY.md`, `docs/ACCELERATION_POLICY.md`, and `docs/WHOLE_PRG_ATLAS.md`;
2. read `analysis/RESUME_STATE.json` and `docs/PROGRESS.md`;
3. fetch the live branch head and inspect commits newer than the state checkpoint;
4. run `python tools/check_resume_frontier.py <JP ROM>`;
5. run the audit named by `previous_checkpoint_audit`;
6. resume only after both pass.

Authority order: JP ROM / observed JP execution -> reproducible JP-ROM audits -> NES/VRC6 hardware docs -> atlas, JP<->US correspondence and external sources as accelerators. Never commit the ROM or a lossless ROM-equivalent listing.

JP ROM SHA-256: `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.
US comparison ROM SHA-256: `1c7b2ed2c1fb5839a6764006aa476f5c9d48f99465b6141980f3a5af1dfec0d6`.

## Current dashboard

```text
whole JP PRG scanned/indexed                 262144 / 262144 = 100%
strict semantically verified PRG floor        48821 / 262144 = 18.6237%
exact unique JP<->US correspondence           115865 / 262144 = 44.1990%
exact-or-normalized structural candidates     149607 / 262144 = 57.0705%
VPP                                             22 / 100
```

The latest VPP point is the tested native VRC6 PRG/CHR mapper. Cross-version percentages remain accelerator/classification coverage, not semantic verification.

## Stable semantic chain

```text
IRQ + fixed NMI + ED46                    -> $10-clean on admitted graphs
raw bank $0C                              -> $10-clean on live admitted graph
raw bank $04 parser + 96/96 roots         -> $10-clean
raw bank $05 parser + 72/72 roots         -> $10-clean
$E7FB first-level fixed graph             -> locally $10-clean
04FF nested $2C head                      -> locally $10-clean
0500 secondary $68 graph                  -> locally $10-clean
0501 fixed scheduler                      -> locally $10-clean
0501 raw bank $09                         -> locally $10-clean
0501 raw bank $0A                         -> locally $10-clean
0501 raw bank $0B object/collision        -> WRITES $10 at 7 verified sites
PRG26 renderer                            -> consumes/persists inherited $10
```

## 0501 — fixed scheduler and mapper-selected callees

Evidence:

```text
analysis/NMI_FIXED_SCHEDULER_BANKED_0501.md
tools/audit_nmi_fixed_scheduler_banked.py
```

Exact result:

```text
fixed PRG31                    161 starts    298 new bytes
raw bank $09                   479 starts   1050 new bytes
raw bank $0A                    57 starts    120 new bytes
raw bank $0B                  1338 starts   2896 new bytes
----------------------------------------------------------
0501                           2035 starts   4364 new bytes
```

Tagged ordered-manifest SHA-256:
`639e20f7e96e816a40ef4ef7d8585c809ce670ac5384f3c2fabc9a77d275737e`.

Strict tracked PRG floor: **48,821 bytes = 18.6237%**.

Scheduler-proven mapper roots:

```text
raw $0B -> $80E3
raw $0B -> $B1F8
raw $0B -> $BD11
raw $09 -> $8001
raw $0B -> $8001
raw $0B -> $8161
raw $0B -> $826C
raw $0A -> $84EA
```

The fixed `$FE95` dispatcher shifts `$0565,X` right six times and invokes `$E7FB`. `$FE98-$FE9D` contains exactly three encoded pointers: `$FE9E,$FEB1,$FEC6`; `$FE9E` is executable code, not a fourth pointer. Selector `$03` remains a producer-domain question.

Verified raw-$0B direct `$10` stores:

```text
$B3B6 $B3D2 $B40E $B460 $B65F $B740 $B76C
```

The remaining provenance problem is which of these is the final live writer/value before renderer entry.

## Native VRC6 mapper

Evidence:

```text
analysis/NATIVE_VRC6_MAPPER.md
src/vrc6_mapper.hpp
src/vrc6_mapper.cpp
tests/vrc6_mapper_test.cpp
```

Implemented/tested target-game behavior:

- PRG RAM enable at `$B003` bit 7;
- switchable 16 KiB `$8000-$BFFF` and 8 KiB `$C000-$DFFF` PRG;
- fixed PRG31 `$E000-$FFFF`;
- VRC6a A0/A1/A12-A15 mapper-register mirrors;
- eight CHR bank registers and pattern modes;
- target-game CIRAM V/H/one-screen mapping;
- exact-ROM regression checks for mapper identity, fixed vectors and 0501 raw-bank mappings.

IRQ timing and VRC6 audio are intentionally separate and remain open. The mapper earns CPU/mapper rubric item 8 but does not yet earn full native-runtime memory/PPU integration credit.

## Cross-version acceleration

Exact matcher:

```text
tools/match_jp_us_exact.py
tools/audit_jp_us_exact_match.py
analysis/JP_US_EXACT_MATCH_SUMMARY.md
```

Result: **115,865 exact unique JP bytes = 44.1990%**, 821 exact runs, 73 conflicting-overlap JP bytes excluded.

Normalized matcher:

```text
tools/match_jp_us_normalized.py
tools/audit_jp_us_normalized_match.py
analysis/JP_US_NORMALIZED_MATCH_SUMMARY.md
```

Result: **24,014 unique normalized matches**, **149,607 exact-or-normalized candidate bytes = 57.0705%**. Calibration against exact-supported starts is **13,232/13,232 agreeing, 0 disagreeing**.

Use these for location/naming/structure hints only; JP bytes, producer domains and mapper state control semantic promotion.

## Open edges after 0501

1. exact final-writer/value domain for the seven raw-$0B `$10` stores;
2. raw-$09 indirect / `$E5DA` selected callees;
3. raw-$0B `$E7FB` dispatch sites `$A15A/$A2CC/$A3A9`;
4. raw-$0B indirect jumps `$BD56/$BD64`;
5. `$0565>>6` selector `$03` live-domain question;
6. first-level `$18`, full `$2C`, and full `$68` producer closure;
7. `$FAA0-$FAA9` indexed ROM-data domain;
8. physically unprocessed fixed-tail bytes beginning at raw frontier `$FB96`;
9. complete mapper-register-use inventory;
10. native IRQ timing, PPU integration, audio and executable runtime.

## Next semantic checkpoint — 0502

Use atlas and JP<->US correspondence first. Primary target: raw-bank `$0B` final-writer/value closure for `$10/$11`, including control-flow ordering and returns from the seven verified stores toward fixed scheduler/render entry. Resolve `$A15A/$A2CC/$A3A9` `$E7FB` sites and `$BD56/$BD64` indirect dispatches where they affect that domain.

The raw fixed investigation frontier deliberately remains `$FB96`: 0501 advanced noncontiguous semantic coverage from `$FDE4` and mapper-selected callees; it did not claim `$FB96-$FFFF` by physical contiguity.

Recovery bytes:

```text
verification overlap $FB76-$FB95
SHA-256 e4fa5e06e439ca12a84d935eb80224f448276c722399fe76fe0ce60013cc4ee7

frontier fingerprint $FB96-$FBB5
SHA-256 a5437f0f20034ba34d65afeec353d28846a321134061f765814d28eaa3f69157

raw tail $FB96-$FFFF
SHA-256 0cbfd0aa79f3c7d1db7a756c08c47bfe01cba321900fb8955e77ec8525d38d44
```

Transaction order: analysis -> audit -> exact-ROM run -> progress/continuity -> `RESUME_STATE.json` last -> recovery checker -> branch-head confirmation.
