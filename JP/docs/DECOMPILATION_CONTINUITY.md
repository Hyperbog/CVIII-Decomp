# Akumajou Densetsu decomp/recomp continuity playbook

Durable handoff for `Hyperbog/CVIII-Decomp`, branch `decompilation`.

## Mandatory recovery

After any interruption:

1. read `docs/INTERRUPTION_RECOVERY.md`, `docs/ACCELERATION_POLICY.md`, and `docs/WHOLE_PRG_ATLAS.md`;
2. read `analysis/RESUME_STATE.json` and current progress;
3. fetch the live branch head and inspect commits newer than the state checkpoint;
4. run `python tools/check_resume_frontier.py <JP ROM>`;
5. run the audit named by `previous_checkpoint_audit`;
6. resume only after both pass.

Authority remains: JP ROM / observed JP execution -> reproducible JP-ROM audits -> NES/VRC6 hardware docs -> generated atlas and external sources as accelerators. Never commit the ROM or a lossless ROM-equivalent listing.

JP ROM SHA-256: `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.
US comparison ROM SHA-256: `1c7b2ed2c1fb5839a6764006aa476f5c9d48f99465b6141980f3a5af1dfec0d6`.

## Current dashboard

```text
whole JP PRG scanned/indexed                 262144 / 262144 = 100%
strict semantically verified PRG floor        48821 / 262144 = 18.6237%
exact unique JP<->US correspondence           115865 / 262144 = 44.1990%
exact-or-normalized structural candidates     149607 / 262144 = 57.0705%
VPP                                             21 / 100
```

Cross-version percentages are accelerator/classification coverage, not semantic verification.

## Stable chain through 0500

```text
IRQ + fixed NMI + ED46                    -> $10-clean on admitted graphs
raw bank $0C                              -> $10-clean on live admitted graph
raw bank $04 parser + 96/96 roots         -> $10-clean
raw bank $05 parser + 72/72 roots         -> $10-clean
$E7FB first-level fixed graph             -> locally $10-clean
04FF nested $2C head                      -> locally $10-clean
0500 secondary $68 graph                  -> locally $10-clean
PRG26 renderer                            -> consumes/persists inherited $10
```

0500 controlling result: 414 instruction starts, 982 genuinely new bytes, manifest SHA `fdc1a53db0ee18ca5e70188d2c8b31d1b350c91d011f72fddb4b6fcb7434984e`.

## 0501 — fixed scheduler and proven mapper-selected callees

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

Strict tracked PRG floor is now **48,821 bytes = 18.6237%**.

The fixed scheduler proves these mapper contexts before traversal:

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

No `$8000-$BFFF` target was traversed under guessed bank state.

### `$FE95` dispatch

`$FE8C-$FE95` loads `$0565,X`, shifts right six times, then calls `$E7FB`. `$FE98-$FE9D` contains exactly three encoded pointer pairs:

```text
00 -> $FE9E
01 -> $FEB1
02 -> $FEC6
```

`$FE9E` is executable code and is not a fourth pointer. Arithmetic selector `$03` is possible; its live producer domain is still open.

### Critical `$10` correction

Raw banks `$09` and `$0A` are locally `$10`-clean, but the scheduler-selected raw-bank `$0B` graph intentionally writes zero-page `$10` at seven verified sites:

```text
$B3B6  $B3D2  $B40E  $B460  $B65F  $B740  $B76C
```

The surrounding JP code and reconciled US structure identify `$10/$11` as collision/distance coordinate scratch. Therefore the provenance question is no longer “does every predecessor preserve `$10`?” It is “which raw-$0B site is the final live writer, what value domain does it produce, and what value reaches the renderer?”

Current model:

```text
earlier NMI/audio predecessors     -> preserve $10
fixed scheduler                    -> locally preserves $10
raw bank $09                       -> locally preserves $10
raw bank $0A                       -> locally preserves $10
raw bank $0B object/collision      -> writes $10 at 7 verified sites
renderer                           -> consumes/persists inherited $10
```

## Cross-version acceleration

Exact matcher:

```text
tools/match_jp_us_exact.py
tools/audit_jp_us_exact_match.py
analysis/JP_US_EXACT_MATCH_SUMMARY.md
```

32-byte unique-anchor baseline: 115,865 exact unique JP bytes (44.1990%), 821 exact runs, 73 ambiguous overlapping bytes excluded.

Relocation-normalized matcher:

```text
tools/match_jp_us_normalized.py
tools/audit_jp_us_normalized_match.py
analysis/JP_US_NORMALIZED_MATCH_SUMMARY.md
```

16-instruction normalization preserves opcodes/immediates/RAM operands and masks branches, call/jump targets, and ROM addresses. It yields 24,014 unique candidates and 149,607 exact-or-normalized candidate bytes (57.0705%). On 13,232 starts independently supported by the exact baseline, the normalized US destination agrees 13,232/13,232 with zero disagreements.

Use these as locators and naming/structure hints only; JP bytes, control flow and mapper state remain authoritative.

## Open edges after 0501

1. exact final-writer/value domain for the seven raw-$0B `$10` stores;
2. raw-$09 indirect / `$E5DA` selected callees and their `$10` behavior;
3. raw-$0B `$E7FB` dispatch sites `$A15A/$A2CC/$A3A9`;
4. raw-$0B indirect jumps `$BD56/$BD64`;
5. `$0565>>6` selector `$03` live-domain question;
6. first-level `$18`, full `$2C`, and full `$68` producer closure;
7. `$FAA0-$FAA9` indexed ROM-data domain;
8. physically unprocessed fixed-tail bytes beginning at the raw frontier `$FB96`.

## Next checkpoint — 0502

Use the atlas and JP<->US correspondence before narrow searching. Primary target is raw-bank `$0B` final-writer/value closure for `$10/$11`, including control-flow ordering and return paths from the seven verified stores to fixed scheduler/render entry. Resolve the `$A15A/$A2CC/$A3A9` `$E7FB` sites and `$BD56/$BD64` indirect dispatches where they affect that domain.

The raw fixed investigation frontier deliberately remains `$FB96`: 0501 advanced noncontiguous semantic coverage from verified inbound root `$FDE4` and mapper-selected callees; it did not claim `$FB96-$FFFF` by physical contiguity.

Recovery bytes remain:

```text
verification overlap $FB76-$FB95
SHA-256 e4fa5e06e439ca12a84d935eb80224f448276c722399fe76fe0ce60013cc4ee7

frontier fingerprint $FB96-$FBB5
SHA-256 a5437f0f20034ba34d65afeec353d28846a321134061f765814d28eaa3f69157

raw tail $FB96-$FFFF
SHA-256 0cbfd0aa79f3c7d1db7a756c08c47bfe01cba321900fb8955e77ec8525d38d44
```

Checkpoint transaction remains: analysis -> audit -> exact-ROM run -> progress/continuity -> `RESUME_STATE.json` last -> recovery checker -> branch-head confirmation.
