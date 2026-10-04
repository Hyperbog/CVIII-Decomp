# Decompilation progress ledger

## Current status

Work proceeds in ROM-backed semantic checkpoints. Large whole-bank/full-PRG discovery sweeps are encouraged, but candidate decodes become verified coverage only when JP-ROM control flow, producer domains, mapper context, parser semantics, or runtime evidence justify the exact bytes.

After interruption read `docs/INTERRUPTION_RECOVERY.md`, `docs/ACCELERATION_POLICY.md`, `docs/WHOLE_PRG_ATLAS.md`, `analysis/RESUME_STATE.json`, then run `tools/check_resume_frontier.py`.

Primary metric: **Verified Parity Progress (VPP) = 21 / 100**. This is an evidence rubric, not raw byte coverage.

**0500 is complete after an accounting repair.** The earlier 933-byte draft omitted the explicit `$F800` fallthrough boundary carried from 04FF. The controlling audit now seeds `$F800` and proves **414 instruction starts / 982 genuinely new semantic bytes**, while preserving shared ZP `$10` locally.

## Stable foundation

- JP ROM SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.
- PRG 256 KiB, CHR 128 KiB, mapper 24 / VRC6a.
- RESET `$E00B`, NMI `$E057`, IRQ `$E0F5`.
- VRC6 switchable/fixed PRG model established.
- IRQ dispatcher and raw bank `$01` state table reconciled.
- PRG26 `$8001` OAM renderer baseline implemented and tested.
- Whole-PRG atlas performs aggressive 256 KiB candidate/xref sweeps without promoting false-positive data decodes.
- Recovery tooling verifies switchable-bank and fixed-bank frontiers.

## Pre-render shared ZP `$10` provenance

- 04F2 IRQ graph: preserves `$10`.
- 04F3 fixed NMI `$E057-$E365`: preserves `$10`.
- 04F4 `$ED46` fixed helper graph: preserves `$10`.
- 04F5-04F6 raw bank `$0C`: live graph preserves `$10`.
- 04F7-04FA raw bank `$04`: parser + **96/96 roots** preserve `$10`.
- 04FB-04FD raw bank `$05`: parser + **72/72 roots** preserve `$10`; live `$E7` domains ROM-proven.
- 04FE `$E7FB` first-level fixed graph: preserves `$10`.
- 04FF nested `$2C` fixed head: 401 instruction starts, **931 new bytes**, preserves `$10`.
- 0500 deferred primary + secondary `$68` fixed graph: 414 instruction starts, **982 new bytes**, preserves `$10` locally.

## Critical invariants

- JP ROM / observed JP behavior are authoritative.
- US disassembly, CDL, Ghidra, decompilers and atlas results are accelerators only.
- Table length is never a selector-domain proof; do not invent clamps for `$18`, `$2C`, `$68`.
- CPU `$8000-$DFFF` targets require proven VRC6 mapper state.
- Coverage is semantic and exact; unreached bytes remain unclaimed even inside a raw investigation interval.
- Variable-width streams require every operand byte actually read to be inside the claimed dependency span.

## Raw-bank closures

Bank `$04`: **96/96 roots closed**. Final 04FA dependency `$B1F0-$BE7D`, 3184 genuinely new bytes after prior probes.

Bank `$05`: **72/72 roots closed**:

```text
04FB $87AE-$9A6A   4797 new
04FC $9A6B-$AD96   4908 new
04FD $AD97-$BF05   4463 new
```

## Fixed-dispatch chain

### 04FE

`$E7FB-$E813` is a stack-return-address inline tail dispatcher writing only `$00-$03`. The first-level NMI selector is `$18`; nested state `$04` reaches `$F390`, loads `$2C`, and dispatches through the 32 pointer pairs at `$F39D-$F3DC`.

04FE: **957 genuinely new bytes**, ordered manifest SHA:
`a672f908a238bea20902fc40c5417622bdb9af675cda3b982a6f0ce494ebad32`.

### 04FF

26 nested `$2C` roots entering `$F3DD-$F7FF` were admitted. Exact result:

```text
instruction starts 401
new bytes          931
manifest SHA       2e8b703b970ca2f1eae61f5fd1a4850da6b8e5d4af1a894fb8075657299ae0d4
```

It deliberately left `$F706-$F712`, `$F724-$F738`, `$F782-$F791`, `$F7B7-$F7CE` unclaimed and handed an explicit fallthrough boundary at `$F800` to 0500.

### 0500 — corrected secondary `$68` graph

Deferred primary states:

```text
$08 -> $F965
$0B -> $F831
$0C -> $F839
$0D -> $F841
$0E -> $F841
$10 -> $F849
```

`$F849: LDA $68 / JSR $E7FB` has 16 encoded targets at `$F84E-$F86D`. Entries `$0C-$0F` target the four former 04FF gaps, so those gaps are now admitted by real pointer-table control flow.

`$F965: LDA $68 / JSR $E7FB` has 10 encoded targets at `$F96A-$F97D`. Neither table length is treated as a live selector bound.

Corrected 0500 roots:

```text
F800 F831 F839 F841 F849 F965
```

Strict result:

```text
instruction starts                414
reachable store/RMW instructions   82
indexed write/RMW forms             9
direct/indexed ZP $10 aliases       0
genuinely new semantic bytes      982
```

Exact new-byte manifest:

```text
F706-F712    13   8745c6e3d3acdd90bf3b1cafaf32f9e981a606070ba5d2b365cace8f56fa3025
F724-F738    21   41cad7c7b722c299f4111083f871fd996a0cfa517bd990d3b37ddce6ac30072e
F782-F791    16   17bbb4663de8e617686c27ab5ad5554a69c0062d9c8bff1d353fd6487028546b
F7B7-F7CE    24   0d93fcf865fdae96f01a0640e3769924b558f1cb0aaa0dbe7d2fedfdf17462be
F800-FA9F   672   6dea651f93c64d59355c4180907677d367bb705ed84cbfa6ec59da79009028a8
FAAA-FB95   236   5d32479e3af38c5477b4a3c076b3c3d0a0bd07f4c572a35a115bd6e347720402
```

Ordered manifest SHA:
`fdc1a53db0ee18ca5e70188d2c8b31d1b350c91d011f72fddb4b6fcb7434984e`.

`$FB31-$FB36` is exact six-byte ROM data proven by the bounded Y=0..5 loop. `$FAA0-$FAA9` remains unclaimed pending `$62/$054E` index-domain proof.

Reachable `$2C` mutations: `$F736,$F78F,$F7CC,$F962,$FB77`.

Reachable `$68` mutations: `$F706,$F72F,$F78D,$F874,$F896,$F8AE,$F8E6,$F916,$F957,$F9B4,$F9D0,$F9FC,$F9FF,$FAB7,$FAD7,$FB04`.

Controlling evidence:

- `analysis/NMI_FIXED_68_DISPATCH.md`
- `tools/audit_nmi_fixed_68_dispatch.py`

The previous 933-byte 0500 result is superseded because it failed to seed `$F800`.

## Whole-PRG acceleration

Use before narrow searching:

```text
tools/build_whole_prg_atlas.py
tools/query_whole_prg_atlas.py
tools/audit_whole_prg_atlas.py
analysis/WHOLE_PRG_ATLAS_MANIFEST.json
analysis/WHOLE_PRG_FOCUS_SUMMARY.md
```

Lossless bank dumps are generated locally only, never committed.

## Current provenance boundary

```text
verified IRQ graph                    -> preserves $10
fixed NMI span $E057-$E365           -> preserves $10
$ED46 helper graph                    -> preserves $10
raw bank $0C / PRG24                 -> preserves $10 on live paths
raw bank $04 parser + 96/96 roots    -> preserves $10
raw bank $05 parser + 72/72 roots    -> preserves $10
$E7FB + first-level fixed graph       -> preserves $10
04FF nested fixed head                -> preserves $10
0500 secondary $68 fixed graph        -> preserves $10 locally
$18 producer domain                   -> unresolved
full $2C producer/alias closure       -> unresolved
full $68 producer/alias closure       -> unresolved
mapper-dependent exits                -> unresolved
PRG26 renderer                        -> consumes/persists $10 exactly
```

VPP remains **21/100**.

## Next checkpoint — 0501

Raw fixed-bank frontier: `$FB96`.

```text
initial raw window    $FB96-$FFFF   1130 bytes
SHA-256               0cbfd0aa79f3c7d1db7a756c08c47bfe01cba321900fb8955e77ec8525d38d44

verification overlap  $FB76-$FB95     32 bytes
SHA-256               e4fa5e06e439ca12a84d935eb80224f448276c722399fe76fe0ce60013cc4ee7

frontier fingerprint  $FB96-$FBB5     32 bytes
SHA-256               a5437f0f20034ba34d65afeec353d28846a321134061f765814d28eaa3f69157
```

Only still-unclaimed bytes below the raw frontier: `$FAA0-$FAA9` (10 bytes).

0501 should sweep the remaining fixed tail, classify the `$FE95: JSR $E7FB` atlas candidate from real control flow, reconcile exact data dependencies, and continue `$18/$2C/$68` producer plus mapper-state closure.
