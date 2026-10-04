# Decompilation progress ledger

## Current status

Work proceeds in ROM-backed semantic checkpoints with large whole-bank/full-PRG discovery sweeps. Candidate decodes and cross-version matches become verified coverage only when JP-ROM control flow, producer domains, mapper context, parser semantics, or runtime evidence justify the exact bytes.

After interruption read `docs/INTERRUPTION_RECOVERY.md`, `docs/ACCELERATION_POLICY.md`, `docs/WHOLE_PRG_ATLAS.md`, `analysis/RESUME_STATE.json`, then run `tools/check_resume_frontier.py`.

Primary parity metric: **VPP = 21 / 100**. This is a coarse evidence rubric, not a byte-progress meter.

Current quantitative dashboard:

```text
whole JP PRG scanned/indexed                 262144 / 262144 = 100%
strict semantically verified PRG floor        48821 / 262144 = 18.6237%
exact unique JP<->US correspondence           115865 / 262144 = 44.1990%
exact-or-normalized structural candidates     149607 / 262144 = 57.0705%
```

The last two are accelerators only; they do not promote semantic verification.

## Stable foundation

- JP ROM SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.
- US comparison ROM SHA-256 `1c7b2ed2c1fb5839a6764006aa476f5c9d48f99465b6141980f3a5af1dfec0d6`.
- PRG 256 KiB, CHR 128 KiB, JP mapper 24 / VRC6a.
- RESET `$E00B`, NMI `$E057`, IRQ `$E0F5`.
- VRC6 switchable/fixed PRG model established.
- IRQ dispatcher and raw bank `$01` state table reconciled.
- PRG26 `$8001` OAM renderer baseline implemented and tested.
- Whole-PRG atlas performs aggressive 256 KiB candidate/xref sweeps.
- Recovery tooling verifies switchable-bank and fixed-bank frontiers.

## Pre-render shared ZP `$10` provenance

Earlier checkpoints established:

- 04F2 IRQ graph: preserves `$10`.
- 04F3 fixed NMI `$E057-$E365`: preserves `$10`.
- 04F4 `$ED46` fixed helper graph: preserves `$10`.
- 04F5-04F6 raw bank `$0C`: live graph preserves `$10`.
- 04F7-04FA raw bank `$04`: parser + **96/96 roots** preserve `$10`.
- 04FB-04FD raw bank `$05`: parser + **72/72 roots** preserve `$10`; live `$E7` domains ROM-proven.
- 04FE `$E7FB` first-level fixed graph: locally preserves `$10`.
- 04FF nested `$2C` fixed head: 401 instruction starts, **931 new bytes**, locally preserves `$10`.
- 0500 deferred primary + secondary `$68` fixed graph: 414 instruction starts, **982 new bytes**, locally preserves `$10`.

0501 changes the model: the scheduler-selected raw bank `$0B` object/collision graph contains seven real reachable `STA $10` sites, so `$10` is not globally preserved. It is reused as collision/distance coordinate scratch before the renderer later consumes its inherited value.

## 0501 — fixed scheduler + mapper-selected banked roots

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

The tracked strict PRG floor advances from `44,457` to **48,821 bytes = 18.6237%**.

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

`$FE9E` is executable code and must not be swallowed as a fictitious fourth pointer. Arithmetic can produce selector `$03`; its live producer domain remains open.

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

Cross-version structural comparison supports their role as collision/distance scratch, but JP bytes/control flow remain controlling. The exact final writer/value reaching renderer entry remains open.

## Cross-version acceleration

### Exact correspondence

Tools:

```text
tools/match_jp_us_exact.py
tools/audit_jp_us_exact_match.py
analysis/JP_US_EXACT_MATCH_SUMMARY.md
```

Unique 32-byte US anchors produce:

```text
115865 exact unique JP bytes
44.1990% of PRG
821 exact correspondence runs
73 overlapping ambiguous JP bytes excluded
```

High-correspondence banks include PRG16 99.85%, PRG12 98.06%, PRG13 97.44%, PRG17 93.04%, PRG15 89.18%.

### Relocation-normalized structural correspondence

Tools:

```text
tools/match_jp_us_normalized.py
tools/audit_jp_us_normalized_match.py
analysis/JP_US_NORMALIZED_MATCH_SUMMARY.md
```

A 16-instruction normalized signature zeros branch displacements, JSR/JMP destinations, and ROM operands >= `$8000` while preserving opcode bytes, immediates, and RAM/I/O operands.

Result:

```text
24014 unique normalized JP<->US candidate matches
68009 JP bytes covered by normalized candidates
149607 bytes covered by exact-or-normalized candidates = 57.0705%
calibration on exact-supported starts: 13232 / 13232 agree, 0 disagree
```

These remain candidate structural evidence, not semantic verification.

## Critical invariants

- JP ROM / observed JP behavior are authoritative.
- US disassembly, US ROM matches, CDL, Ghidra, decompilers and atlas results are accelerators only.
- Table length is never a selector-domain proof; do not invent clamps for `$18`, `$2C`, `$68`, or `$0565 >> 6`.
- CPU `$8000-$DFFF` targets require proven mapper state.
- Coverage is semantic and exact; unreached bytes remain unclaimed inside raw investigation windows.
- Variable-width streams require every operand byte actually read to be inside the claimed dependency span.
- Lossless ROM-equivalent dumps are generated locally only and never committed.

## Current provenance boundary

```text
verified IRQ / fixed NMI / sound-side predecessors  -> preserve $10
fixed scheduler local graph                         -> preserves $10
raw bank $09 local graph                            -> preserves $10
raw bank $0A local graph                            -> preserves $10
raw bank $0B object/collision graph                  -> WRITES $10 at 7 verified sites
renderer                                             -> consumes/persists inherited $10 exactly
```

Still open:

- exact final-writer/value domain for the seven raw-bank `$0B` `$10` stores;
- raw-$09 indirect / `$E5DA` selected callees;
- raw-$0B `$E7FB` dispatch sites `$A15A/$A2CC/$A3A9`;
- raw-$0B indirect jumps `$BD56/$BD64`;
- first-level `$18`, full `$2C`, and full `$68` producer closure;
- `$0565 >> 6` selector `$03` live-domain question;
- `$FAA0-$FAA9` indexed data domain;
- physically unprocessed fixed-tail bytes beginning at raw frontier `$FB96`.

VPP remains **21/100**.

## Next checkpoint — 0502

Use the whole-PRG atlas and JP<->US correspondence first. Primary semantic target is the raw-bank `$0B` final-writer/value problem for `$10/$11`, including callers/returns around the seven verified stores. Secondary target is to resolve the three raw-$0B `$E7FB` dispatches and indirect object-dispatch edges where mapper context is already proven.

The raw fixed investigation frontier remains `$FB96` because 0501 followed the first verified inbound root `$FDE4` noncontiguously rather than claiming `$FB96-$FFFF` by physical contiguity.
