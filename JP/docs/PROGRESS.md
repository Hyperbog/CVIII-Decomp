# Decompilation progress ledger

## Current status

Work proceeds in bounded, ROM-backed checkpoints. Large whole-bank/full-PRG discovery sweeps are encouraged, but verified coverage is promoted only when JP-ROM control flow, producer domains, mapper context, parser semantics, or runtime evidence justify the exact consumed bytes.

After any interruption read `docs/INTERRUPTION_RECOVERY.md`, `docs/ACCELERATION_POLICY.md`, `docs/WHOLE_PRG_ATLAS.md`, and `analysis/RESUME_STATE.json`, then run `tools/check_resume_frontier.py` against the authoritative JP ROM.

Primary metric: **Verified Parity Progress (VPP) = 21 / 100 (21%)**. VPP is an evidence rubric, not raw-byte coverage or a time estimate.

**0500 is complete.** It closes the deferred fixed-bank primary roots and the two visible `$68` secondary-dispatch structures as a bounded local graph: 395 instruction starts, 875 instruction/operand bytes, 58 explicitly justified table/data bytes, and **933 genuinely new bytes** total. The admitted graph preserves shared ZP `$10`. Complete `$18/$2C/$68` producer closure and mapper-selected callees remain open.

## Stable foundation

- Exact JP ROM identity and 32 physical 8 KiB PRG-bank model are locked.
- Vectors: RESET `$E00B`, NMI `$E057`, IRQ `$E0F5`.
- Mapper 24 / VRC6a fixed and switchable PRG contexts are mapped.
- IRQ raw bank `$01` and its exact 45-entry state table are reconciled.
- NMI bank `$0D` renderer call `$8001` resolves to `PRG26:$8001`.
- Native OAM renderer baseline exists in `src/oam_renderer.*` with regression tests.
- Whole-PRG atlas tooling performs aggressive 256 KiB discovery sweeps and global RAM/control-flow queries without promoting false-positive candidate decodes.
- Recovery tooling verifies switchable 16 KiB VRC6-bank and fixed 8 KiB PRG frontiers.

## Pre-render shared ZP `$10` provenance

- **04F2:** IRQ graph preserves `$10`.
- **04F3:** fixed NMI `$E057-$E365` preserves `$10`; external dependencies identified.
- **04F4:** `$ED46` fixed helper graph preserves `$10`.
- **04F5-04F6:** raw bank `$0C` live graph preserves `$10`.
- **04F7-04FA:** raw bank `$04` parser + all **96/96** roots preserve `$10`.
- **04FB-04FD:** raw bank `$05` parser + all **72/72** roots preserve `$10`, including ROM-proven live `$E7` producer domains.
- **04FE:** fixed `$E7FB` inline dispatcher + conservative first-level fixed graph preserve `$10`; selector domains/banked exits remain open.
- **04FF:** 26 admitted nested `$2C` roots in `$F3DD-$F7FF` preserve `$10`; **931 new bytes**.
- **0500:** deferred primary roots plus both visible secondary `$68` dispatch structures preserve `$10` locally; **933 new bytes**.

## Critical invariants

- ROM bytes and observed JP behavior are authoritative.
- External US disassembly/CDL/Ghidra/decompilers are accelerators only.
- Table length is never a selector-domain proof: no invented clamps for `$18`, `$2C`, or `$68`.
- No CPU `$8000-$DFFF` edge may be traversed under guessed VRC6 mapper state.
- Coverage is semantic: raw bytes between reached instructions are not counted unless actually consumed as code/operands or explicitly justified data.
- Variable-width streams/instructions require all consumed operand bytes inside the claimed semantic dependency.

## Raw-bank closures

Bank `$04`: **96/96 roots closed**. Final 04FA dependency `$B1F0-$BE7D`, 3184 genuinely new bytes after prior probes.

Bank `$05`: **72/72 roots closed**:

```text
04FB $87AE-$9A6A   4797 new   19 roots
04FC $9A6B-$AD96   4908 new   25 roots
04FD $AD97-$BF05   4463 new   28 roots
```

No host-side `$842D` clamp is introduced; all live bank-$05 `$E7` producer values are ROM-proven.

## Fixed-dispatch checkpoints

### 04FE — `$E7FB` ABI and first-level fixed graph

`$E7FB-$E813` is a stack-return-address inline tail dispatcher writing only `$00-$03`. NMI `$E35E: LDA $18 / $E360: JSR $E7FB` uses 16 encoded pointers at `$E363-$E382`. Conservatively decoding all encoded first-level targets yielded 435 fixed instruction starts, one nested `$E7FB` at `$F39A`, and 21 mapper-dependent banked exits. The fixed graph is `$10`-safe after indexed-write reconciliation.

Nested state `$04` reaches `$F390`, loads `$2C`, and dispatches through 32 encoded pointers at `$F39D-$F3DC`. 04FE contributed **957 new bytes**, manifest SHA `a672f908a238bea20902fc40c5417622bdb9af675cda3b982a6f0ce494ebad32`.

### 04FF — nested `$2C` fixed head

04FF admitted the 26 nested-table targets entering `$F3DD-$F7FF` and strictly decoded 401 instruction starts / **931 genuinely new bytes**. Ordered manifest SHA:

```text
2e8b703b970ca2f1eae61f5fd1a4850da6b8e5d4af1a894fb8075657299ae0d4
```

Four gaps totaling 74 bytes were deliberately left unclaimed until real secondary-dispatch evidence appeared:

```text
F706-F712   13
F724-F738   21
F782-F791   16
F7B7-F7CE   24
```

### 0500 — secondary `$68` dispatch graph

Deferred primary entries were:

```text
$08 -> $F965
$0B -> $F831
$0C -> $F839
$0D -> $F841
$0E -> $F841
$10 -> $F849
```

`$F849` is `LDA $68 / JSR $E7FB`; `$F84E-$F86D` encodes 16 pointers. Entries `$0C-$0F` target exactly `$F706/$F724/$F782/$F7B7`, so all four 04FF gaps are now legitimately admitted.

`$F965` is a second `LDA $68 / JSR $E7FB`; `$F96A-$F97D` encodes 10 pointers. Neither 16 nor 10 is treated as a live `$68` bound.

Strict result:

```text
instruction starts                   395
instruction/operand bytes            875
explicit table/data bytes             58
  F84E-F86D                           32
  F96A-F97D                           20
  FB31-FB36 bounded loop data          6
genuinely new semantic bytes         933
```

Exact new-byte manifest:

```text
F706-F712    13   8745c6e3d3acdd90bf3b1cafaf32f9e981a606070ba5d2b365cace8f56fa3025
F724-F738    21   41cad7c7b722c299f4111083f871fd996a0cfa517bd990d3b37ddce6ac30072e
F782-F791    16   17bbb4663de8e617686c27ab5ad5554a69c0062d9c8bff1d353fd6487028546b
F7B7-F7CE    24   0d93fcf865fdae96f01a0640e3769924b558f1cb0aaa0dbe7d2fedfdf17462be
F831-FA9F   623   eb0859ea4906556aa18192c14d446c9968b56eda1d0d27ad70138f292d9cd9fe
FAAA-FB95   236   5d32479e3af38c5477b4a3c076b3c3d0a0bd07f4c572a35a115bd6e347720402
```

Ordered-manifest SHA-256:

```text
a4ae2796d32ef639940c58f0160af79b8eab8cf80347a998af0ae9c4bab3e44a
```

The local graph has no direct/indexed/indirect write capable of aliasing `$10`. Reachable absolute-indexed writes use bases only in `$0300-$057C`.

Newly admitted `$2C` mutations are `$F736,$F78F,$F7CC,$F962,$FB77`; `$F736/$F78F` restore saved state, `$F7CC` writes `$16`, and `$F962/$FB77` write `$03`.

Newly admitted `$68` mutations are 16 `INC $68` sites: `$F706,$F72F,$F78D,$F874,$F896,$F8AE,$F8E6,$F916,$F957,$F9B4,$F9D0,$F9FC,$F9FF,$FAB7,$FAD7,$FB04`.

Evidence:

- `analysis/NMI_FIXED_68_DISPATCH.md`
- `tools/audit_nmi_fixed_68_dispatch.py`

## Whole-PRG acceleration layer

Use `tools/build_whole_prg_atlas.py`, `tools/query_whole_prg_atlas.py`, and `tools/audit_whole_prg_atlas.py` before repeated narrow byte searches. The atlas scans all 262,144 PRG bytes and records provisional control-flow/RAM-access candidates. Full lossless bank dumps are generated locally only and never committed because they are equivalent to ROM content.

Current atlas includes 35 raw `JSR $E7FB` patterns and focused candidate indexes for `$10/$18/$2C/$68`.

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
$18 selector producer domain          -> unresolved
full $2C producer/alias closure       -> unresolved
full $68 producer/alias closure       -> unresolved
mapper-dependent exits                -> unresolved
PRG26 renderer                        -> consumes/persists $10 exactly
```

**VPP remains 21/100** because complete transitive NMI-helper/bank-context closure is still open.

## Next checkpoint — 0501

Raw fixed-bank frontier advances to `$FB96`. The remaining fixed tail is:

```text
initial raw window   $FB96-$FFFF   1130 bytes
SHA-256              0cbfd0aa79f3c7d1db7a756c08c47bfe01cba321900fb8955e77ec8525d38d44

verification overlap $FB76-$FB95   32 bytes
SHA-256              e4fa5e06e439ca12a84d935eb80224f448276c722399fe76fe0ce60013cc4ee7

frontier fingerprint $FB96-$FBB5   32 bytes
SHA-256              a5437f0f20034ba34d65afeec353d28846a321134061f765814d28eaa3f69157
```

Still-unclaimed bytes below the raw frontier remain explicit:

```text
F800-F830   49 bytes
FAA0-FAA9   10 bytes
```

`$FAA0-$FAA9` are indexed ROM-data candidates whose `$62/$054E` index domains are not yet fully proven.

0501 should sweep the remaining fixed tail, classify the raw `$E7FB` candidate at `$FE95`, continue global `$18/$2C/$68` producer/alias reconciliation using the atlas, and resolve banked callees only under proven VRC6 state.
