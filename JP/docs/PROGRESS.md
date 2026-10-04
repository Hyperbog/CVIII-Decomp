# Decompilation progress ledger

## Current status

Work proceeds in bounded, ROM-backed checkpoints. Normal new-ROM budget is **500-5000 genuinely new bytes**. After any interruption read `docs/INTERRUPTION_RECOVERY.md`, `docs/ACCELERATION_POLICY.md`, and `analysis/RESUME_STATE.json`, then run `tools/check_resume_frontier.py` against the authoritative JP ROM.

Primary metric: **Verified Parity Progress (VPP) = 21 / 100 (21%)**. VPP is an evidence rubric, not raw-byte coverage or a time estimate.

**04FF is complete as a bounded fixed-bank checkpoint.** It closes the 26 nested `$2C` roots whose entrypoints lie in `PRG31:$F3DD-$F7FF`: 401 instruction starts and **931 genuinely new instruction/operand bytes**, with no direct/indexed/indirect write capable of aliasing shared ZP `$10`. Complete `$2C` producer closure is intentionally carried into 0500.

## Stable foundation

- Exact JP ROM identity and 32 physical 8 KiB PRG-bank model are locked.
- Vectors: RESET `$E00B`, NMI `$E057`, IRQ `$E0F5`.
- VRC6 PRG bank helpers and fixed/switchable contexts are mapped.
- IRQ raw bank `$01` and its exact 45-entry state table are reconciled.
- NMI bank `$0D` renderer call `$8001` resolves to `PRG26:$8001`.
- Native OAM renderer baseline exists in `src/oam_renderer.*` with regression tests.
- Recovery tooling verifies switchable 16 KiB VRC6-bank and fixed 8 KiB PRG frontiers.

## Pre-render shared ZP `$10` provenance

- **04F2:** IRQ graph preserves `$10`.
- **04F3:** fixed NMI `$E057-$E365` preserves `$10`; external dependencies identified.
- **04F4:** `$ED46` fixed helper graph preserves `$10`.
- **04F5-04F6:** raw bank `$0C` live graph preserves `$10`.
- **04F7-04FA:** raw bank `$04` parser + all **96/96** roots preserve `$10`.
- **04FB-04FD:** raw bank `$05` parser + all **72/72** roots preserve `$10`, including ROM-proven live `$E7` producer domains.
- **04FE:** fixed `$E7FB` inline dispatcher + conservative first-level fixed graph preserve `$10`; `$18`, nested state, and banked exits remain open.
- **04FF:** admitted 26-root nested fixed graph preserves `$10`; unresolved callees are not assumed safe.

## Critical invariants

Variable-width commands/instructions are not closed unless every consumed operand byte is covered or explicit prior coverage. Raw `$FF` is not a generic stream terminator. For `$E7FB`, table size is **not** a producer-domain bound: do not invent host clamps for `$18`, `$2C`, or `$68`.

Coverage is semantic. Bytes physically between reached instructions are not counted unless the checkpoint actually consumes them as code/operands or explicitly justified data.

## Raw-bank closures

Bank `$04`: **96/96 roots closed**. Final 04FA dependency `$B1F0-$BE7D`, 3184 genuinely new bytes after prior probes.

Bank `$05`: **72/72 roots closed**:

```text
04FB $87AE-$9A6A   4797 new   19 roots
04FC $9A6B-$AD96   4908 new   25 roots
04FD $AD97-$BF05   4463 new   28 roots
```

No host-side `$842D` clamp is introduced; all live bank-$05 `$E7` producer values are ROM-proven.

## 04FE — fixed `$E7FB` first-level dispatch

`$E7FB-$E813` is a stack-return-address inline tail dispatcher. It writes only `$00-$03`, and its NMI call at `$E360` indexes a 16-entry inline table from `$18`. Conservatively decoding all 16 encoded targets yields 435 fixed instruction starts, one nested `$E7FB` at `$F39A`, and 21 mapper-dependent banked exits. After indexed-write reconciliation the fixed graph is `$10`-safe.

The nested call uses selector `$2C`; its 32 encoded pointer pairs occupy `$F39D-$F3DC`. 04FE contributed **957 genuinely new fixed bytes**, ordered-manifest SHA-256:

```text
a672f908a238bea20902fc40c5417622bdb9af675cda3b982a6f0ce494ebad32
```

## 04FF — bounded nested `$2C` fixed head

Raw investigation window:

```text
PRG31 $F3DD-$F7FF
1059 raw bytes
SHA-256 72918e40813310fe3f967790d9b77e344a0f2ede92d12942d95c23849084b1b6
```

Twenty-six distinct nested-table targets enter this window. Six encoded entries are carried forward:

```text
$08 -> $F965
$0B -> $F831
$0C -> $F839
$0D -> $F841
$0E -> $F841
$10 -> $F849
```

Strict admitted graph:

```text
instruction starts                    401
unknown official opcodes                0
unique consumed new bytes             931
reachable store/RMW instructions       46
indexed/indirect store/RMW forms         0
dependency/boundary exits             136
```

Exact manifest:

```text
F3DD-F6AD   721   371c27c08f71624463d2c63097938a30fa57253bd073d2554d454111708f6852
F6E4-F705    34   cd2f26e03fcfab69f12aec4fbe3ff9571f8a2633b3c84eb4365a0d8e777378c5
F713-F723    17   4bc45df46fbab59efc9b70eb7d577001b8474818f921b86e618b43c4653c8300
F739-F781    73   b8cc2cdf6b04eb86ff7693b53c006afb6710098252d7a921e199c22355d462ac
F792-F7B6    37   b564a74ff4c6ba3a55b76472c1462ff1b915f0c333c8dc54ccae3b9a76d1e5e1
F7CF-F7FF    49   13b6de6ba1671ce00afec40ee8b7886d6ed9126a6261b5a090a15f0cc73b1574
```

Ordered-manifest SHA-256:

```text
2e8b703b970ca2f1eae61f5fd1a4850da6b8e5d4af1a894fb8075657299ae0d4
```

Unclaimed/prior bytes remain explicit:

```text
F6AE-F6E3   54 bytes   prior 04FE
F706-F712   13 bytes   unreached
F724-F738   21 bytes   unreached
F782-F791   16 bytes   unreached
F7B7-F7CE   24 bytes   unreached
```

The four unreached gaps total 74 bytes and are **not** 04FF coverage. Secondary `$68` dispatch evidence in 0500 may admit some or all of them.

04FF finds 16 explicit local `$2C` mutations; its bounded local constant/INC transitions stay inside the encoded `$00-$1F` family, but that is not yet the whole-domain producer proof.

Evidence:

- `analysis/NMI_FIXED_2C_HEAD.md`
- `tools/audit_nmi_fixed_2c_head.py`
- `analysis/NMI_FIXED_2C_PREFIX.md` records the superseded broad accounting.

## Current provenance boundary

```text
verified IRQ graph                    -> preserves $10
fixed NMI span $E057-$E365           -> preserves $10
$ED46 helper graph                    -> preserves $10
raw bank $0C / PRG24                 -> preserves $10 on live paths
raw bank $04 parser + 96/96 roots    -> preserves $10
raw bank $05 parser + 72/72 roots    -> preserves $10
$E7FB + first-level fixed graph       -> preserves $10
04FF 26-root fixed head               -> preserves $10; 931 new bytes
$18 selector producer domain          -> unresolved
full $2C producer/target closure      -> unresolved
secondary $68 dispatch domains        -> unresolved
mapper-dependent exits                -> unresolved
PRG26 renderer                        -> consumes/persists $10 exactly
```

**VPP remains 21/100** because complete transitive pre-render NMI-helper closure is still open.

## Next checkpoint — 0500

Continue fixed PRG31 from raw investigation frontier `$F800`.

```text
initial raw window  $F800-$FBFF   1024 bytes
SHA-256             f3090b53f174f15eeacad0d9e042efd95ff93ed6b4bfd706ba233ee5f588c86a

verification overlap $F7E0-$F7FF  32 bytes
SHA-256              6966c228f397fb1a390562bc871d382f624397bd65f06bb301774b085e7759d1

frontier fingerprint $F800-$F81F  32 bytes
SHA-256              322b459da91a43e13712821aba143184801a6b9e6c91e0047f9826846a957f24
```

0500 should reconcile the deferred `$F831/$F839/$F841/$F849/$F965` primary targets, prove the two `$68` selector domains from JP producers, admit the four 04FF gaps only through actual control flow, and continue the whole-ROM `$2C` writer/alias audit. Mapper-dependent `$8000-$DFFF` targets remain opaque until actual VRC6 bank state is proven.