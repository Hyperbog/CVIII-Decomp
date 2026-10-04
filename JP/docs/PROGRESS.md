# Decompilation progress ledger

## Current status

Work proceeds with large whole-bank/full-PRG discovery sweeps followed by exact JP-ROM-backed semantic promotion. Cross-version correspondence, atlas decodes, external disassemblies and decompilers are accelerators only.

After interruption read `docs/INTERRUPTION_RECOVERY.md`, `docs/ACCELERATION_POLICY.md`, `docs/WHOLE_PRG_ATLAS.md`, `analysis/RESUME_STATE.json`, then run `tools/check_resume_frontier.py` and the audit named by the resume state.

Primary parity metric: **VPP = 22 / 100**. The latest point is CPU/mapper/interrupts rubric item 8: tested native VRC6 PRG/CHR mapper implementation.

Current quantitative dashboard:

```text
whole JP PRG scanned/indexed                 262144 / 262144 = 100%
strict semantically verified PRG floor        48821 / 262144 = 18.6237%
exact unique JP<->US correspondence           115865 / 262144 = 44.1990%
exact-or-normalized structural candidates     149607 / 262144 = 57.0705%
VPP                                             22 / 100
```

The cross-version percentages are structural accelerator coverage, not semantic verification.

## Stable foundation

- JP ROM SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.
- US comparison ROM SHA-256 `1c7b2ed2c1fb5839a6764006aa476f5c9d48f99465b6141980f3a5af1dfec0d6`.
- JP cartridge: 256 KiB PRG, 128 KiB CHR, mapper 24 / VRC6a.
- RESET `$E00B`, NMI `$E057`, IRQ `$E0F5`.
- IRQ dispatcher/state ledger and control-vs-ack behavior reconciled.
- PRG26 OAM renderer exists as faithful native source + regression tests.
- Whole-PRG atlas performs aggressive 256 KiB candidate/xref sweeps.
- JP<->US exact and relocation-normalized correspondence matchers are implemented and audited.
- Native target-game VRC6 PRG/CHR mapper exists as source + regression tests.

## Native Mapper 24 / VRC6 lift

Evidence:

```text
analysis/NATIVE_VRC6_MAPPER.md
src/vrc6_mapper.hpp
src/vrc6_mapper.cpp
tests/vrc6_mapper_test.cpp
```

The mapper implements target-game PRG RAM enable, 16 KiB and 8 KiB switchable PRG windows, fixed PRG31, VRC6a register mirrors, eight CHR bank registers, VRC6 CHR pattern modes, and target CIRAM mirroring behavior. The test suite covers synthetic bank identities and checks the authoritative JP ROM's mapper identity, fixed vectors, and scheduler-proven raw-bank mappings.

VRC6 audio and IRQ timing remain separate open subsystems. The standalone mapper does not yet earn native-runtime memory/PPU integration credit; it earns the explicit CPU/mapper rubric point for native VRC6 PRG/CHR mapper implementation.

## Pre-render shared ZP `$10` provenance

Earlier checkpoints established:

- 04F2 IRQ graph: preserves `$10`.
- 04F3 fixed NMI `$E057-$E365`: preserves `$10`.
- 04F4 `$ED46` fixed helper graph: preserves `$10`.
- 04F5-04F6 raw bank `$0C`: live admitted graph preserves `$10`.
- 04F7-04FA raw bank `$04`: parser + **96/96 roots** preserve `$10`.
- 04FB-04FD raw bank `$05`: parser + **72/72 roots** preserve `$10`; live `$E7` domains ROM-proven.
- 04FE `$E7FB` first-level fixed graph: locally preserves `$10`.
- 04FF nested `$2C` fixed head: 401 instruction starts, **931 new bytes**, locally preserves `$10`.
- 0500 deferred primary + secondary `$68` fixed graph: 414 instruction starts, **982 new bytes**, locally preserves `$10`.

0501 corrected the global model: scheduler-selected raw bank `$0B` object/collision processing intentionally writes `$10`, so the remaining problem is final-writer/value provenance rather than global preservation.

## 0501 — fixed scheduler + proven mapper-selected banked roots

Controlling evidence:

```text
analysis/NMI_FIXED_SCHEDULER_BANKED_0501.md
tools/audit_nmi_fixed_scheduler_banked.py
```

Strict result:

```text
fixed PRG31 graph                 161 instruction starts    298 new bytes
raw bank $09 graph               479 instruction starts   1050 new bytes
raw bank $0A graph                57 instruction starts    120 new bytes
raw bank $0B graph              1338 instruction starts   2896 new bytes
-----------------------------------------------------------------------
0501 total                      2035 instruction starts   4364 new bytes
```

Tagged ordered-manifest SHA-256:
`639e20f7e96e816a40ef4ef7d8585c809ce670ac5384f3c2fabc9a77d275737e`.

The tracked strict PRG floor is **48,821 bytes = 18.6237%**.

The fixed scheduler proves these mapper contexts before traversal:

```text
raw $0B  $80E3
raw $0B  $B1F8
raw $0B  $BD11
raw $09  $8001
raw $0B  $8001
raw $0B  $8161
raw $0B  $826C
raw $0A  $84EA
```

No `$8000-$BFFF` target is followed under guessed mapper state.

### `$FE95` inline dispatch

`$FE8C-$FE95` shifts `$0565,X` right six times then invokes `$E7FB`. The encoded table at `$FE98-$FE9D` contains exactly three pointer pairs:

```text
00 -> $FE9E
01 -> $FEB1
02 -> $FEC6
```

`$FE9E` is executable code and is not a fourth pointer. Arithmetic can produce selector `$03`; its live producer domain remains open.

### Raw-bank `$0B` `$10` writes

Verified direct stores:

```text
$B3B6
$B3D2
$B40E
$B460
$B65F
$B740
$B76C
```

The JP code uses `$10/$11` as coordinate scratch in collision/distance calculations. The exact final writer/value reaching renderer entry remains open.

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

### Exact correspondence

```text
tools/match_jp_us_exact.py
tools/audit_jp_us_exact_match.py
analysis/JP_US_EXACT_MATCH_SUMMARY.md
```

Unique 32-byte US anchors give **115,865 exact unique JP bytes = 44.1990%**, 821 exact runs, with 73 ambiguous overlapping JP bytes excluded.

### Relocation-normalized structural correspondence

```text
tools/match_jp_us_normalized.py
tools/audit_jp_us_normalized_match.py
analysis/JP_US_NORMALIZED_MATCH_SUMMARY.md
```

16-instruction normalized signatures yield:

```text
24014 unique normalized JP<->US candidate matches
68009 JP bytes covered by normalized candidates
149607 exact-or-normalized candidate bytes = 57.0705%
13232 / 13232 exact-supported starts agree on US destination
0 calibration disagreements
```

These are candidate structural correspondences only. JP control flow, mapper state and bytes remain controlling.

## Critical invariants

- JP ROM / observed JP behavior are authoritative.
- US structures and labels remain provisional until JP equivalence is demonstrated.
- Table length is never a selector-domain proof; do not invent clamps for `$18`, `$2C`, `$68`, or `$0565 >> 6`.
- CPU `$8000-$DFFF` targets require proven mapper state.
- Coverage is semantic and exact; unreached bytes remain unclaimed inside raw investigation windows.
- Variable-width streams count every operand byte actually read.
- Lossless ROM-equivalent dumps are generated locally only and never committed.

## Open edges

- exact final-writer/value domain for the seven raw-bank `$0B` `$10` stores;
- raw-$09 indirect / `$E5DA` selected callees and their `$10` behavior;
- raw-$0B `$E7FB` sites `$A15A/$A2CC/$A3A9`;
- raw-$0B indirect jumps `$BD56/$BD64`;
- `$0565 >> 6` selector `$03` live-domain question;
- first-level `$18`, full `$2C`, and full `$68` producer closure;
- `$FAA0-$FAA9` indexed data domain;
- physically unprocessed fixed-tail bytes beginning at raw frontier `$FB96`;
- complete game-specific mapper-register use inventory;
- native IRQ timing, PPU integration, audio, and executable runtime.

## Next checkpoint — 0502

Use the whole-PRG atlas and JP<->US correspondence before narrow searching. Primary semantic target is raw-bank `$0B` final-writer/value closure for `$10/$11`, including callers/returns around the seven verified stores. Resolve `$A15A/$A2CC/$A3A9` `$E7FB` sites and `$BD56/$BD64` indirect dispatches where they affect that domain.

The raw fixed investigation frontier remains `$FB96`: 0501 followed a verified inbound root `$FDE4` noncontiguously rather than claiming `$FB96-$FFFF` by physical contiguity.
