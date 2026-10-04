# Decompilation progress ledger

## Current status

Work proceeds in bounded, ROM-backed checkpoints. Normal new-ROM budget is **500-5000 genuinely new bytes**. After any interruption read `docs/INTERRUPTION_RECOVERY.md`, `docs/ACCELERATION_POLICY.md`, and `analysis/RESUME_STATE.json`, then run `tools/check_resume_frontier.py` against the authoritative JP ROM.

Primary metric: **Verified Parity Progress (VPP) = 21 / 100 (21%)**. VPP is an evidence rubric, not raw-byte coverage or a time estimate.

**04FF is still blocked/in progress.** Its first bounded subgraph is now durable: 26 nested `$2C` roots entering fixed `PRG31:$F3DD-$F7FF` consume **931 genuinely new instruction/operand bytes**, preserve shared ZP `$10` locally, and expose 16 explicit fixed-side `$2C` mutations. Full `$2C` producer closure is still open because six primary states, secondary `$68` dispatchers, and fixed/banked callees remain unresolved under their actual mapper contexts.

## Stable foundation

- Exact JP ROM identity and 32 physical 8 KiB PRG-bank model are locked.
- Vectors: RESET `$E00B`, NMI `$E057`, IRQ `$E0F5`.
- VRC6 PRG bank helpers and fixed/switchable contexts are mapped.
- IRQ raw bank `$01` and its exact 45-entry state table are reconciled.
- NMI bank `$0D` renderer call `$8001` resolves to `PRG26:$8001`.
- Native OAM renderer baseline exists in `src/oam_renderer.*` with regression tests.
- Recovery tooling verifies both switchable 16 KiB VRC6-bank frontiers and explicit fixed 8 KiB PRG mappings.

## Pre-render shared ZP `$10` provenance

- **04F2:** IRQ graph `PRG02/03:$9F99-$A526`, 1422 bytes, preserves `$10`.
- **04F3:** fixed NMI `PRG31:$E057-$E365`, 783 bytes, preserves `$10`; external dependencies identified.
- **04F4:** `$ED46` fixed helper graph, 1024 bytes, preserves `$10`.
- **04F5-04F6:** raw bank `$0C` graph and parser-mode proof close its live paths as `$10`-safe.
- **04F7-04FA:** raw bank `$04` parser plus all **96/96** roots are closed and preserve `$10` under strict operand accounting.
- **04FB-04FD:** raw bank `$05` parser plus all **72/72** roots are closed and preserve `$10`; every live `$E7` producer domain is derived from actual JP-ROM bytes.
- **04FE:** fixed `$E7FB` dispatcher and conservative first-level fixed target graph preserve `$10`; selector domains and banked exits remain open.
- **04FF partial:** the admitted 26-root `$F3DD-$F7FF` fixed graph preserves `$10`; transitive callee effects remain open.

## Critical invariants

Variable-width stream commands must have every consumed operand byte inside the claimed semantic dependency span before any operand is read. Raw `$FF` is not a generic terminator proxy. Preserve `FB` loop anchors, context-sensitive `FD` call/return, and `FE` counted/absolute-pointer state.

For `$E7FB`, table size is **not** a selector-domain proof. Do not infer a host-side clamp for `$18`, `$2C`, or later `$68` selectors from encoded table size.

Coverage accounting is semantic: physical bytes are counted as new only when the committed checkpoint actually consumes them as instructions/operands or explicitly justified data. A raw interval is not automatically coverage merely because admitted code lies on both sides of an unreached gap.

## Raw-bank closures

Bank `$04`: **96/96 roots closed**. Final 04FA dependency `$B1F0-$BE7D`, 3184 genuinely new bytes after prior probes.

Bank `$05`: **72/72 roots closed**:

```text
04FB $87AE-$9A6A   4797 new   19 roots
04FC $9A6B-$AD96   4908 new   25 roots
04FD $AD97-$BF05   4463 new   28 roots
```

All live bank-$05 `$E7` parameter domains index legitimate `$8430-$8443` entries and dispatch to audited `$8444`; no host-side `$842D` clamp is introduced.

## 04FE — fixed `$E7FB` first-level dispatch

`$E7FB-$E813` is an inline tail dispatcher. It doubles A, preserves Y in `$03`, pops the caller's JSR return address into `$00/$01`, reads a little-endian pointer from the caller's inline bytes, restores Y, and executes `JMP ($0002)`. It writes only `$00-$03`.

The NMI caller at `$E360` loads A from `$18`. Its 16-entry table at `$E363-$E382` reaches a conservative fixed graph of 435 official instruction starts, zero unknown opcodes, one nested `$E7FB` site at `$F39A`, and 21 mapper-dependent banked exits. After X-domain reconciliation, no reachable fixed write can alias `$10`.

The nested dispatcher uses `$2C` and its 32 pointer pairs occupy `$F39D-$F3DC`; `$F3DD` is executable code. 04FE contributed **957 genuinely new fixed PRG31 bytes**, ordered-manifest SHA-256 `a672f908a238bea20902fc40c5417622bdb9af675cda3b982a6f0ce494ebad32`.

## 04FF partial — nested `$2C` fixed head

Raw investigation window:

```text
PRG31 $F3DD-$F7FF
1059 raw bytes
SHA-256 72918e40813310fe3f967790d9b77e344a0f2ede92d12942d95c23849084b1b6
```

The nested table has 26 distinct root addresses entering this window. Six encoded entries are deferred:

```text
$08 -> $F965
$0B -> $F831
$0C -> $F839
$0D -> $F841
$0E -> $F841
$10 -> $F849
```

Strict decoding of only the admitted 26 roots yields:

```text
instruction starts                     401
unknown official opcodes                 0
unique consumed instruction bytes      931
indexed/indirect zero-page writes        0
direct local $2C writers                16
dependency/boundary exits              136
```

Exact genuinely-new manifest:

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

The raw bytes not claimed by this graph remain explicit:

```text
F6AE-F6E3   54 bytes   prior 04FE coverage
F706-F712   13 bytes   not reached by the admitted roots
F724-F738   21 bytes   not reached
F782-F791   16 bytes   not reached
F7B7-F7CE   24 bytes   not reached
```

The previous 1005-byte prefix accounting is superseded because it counted those final four unreached gaps merely from physical contiguity. `analysis/NMI_FIXED_2C_PREFIX.md` now records the correction and `tools/audit_nmi_fixed_nested_prefix.py` redirects to the stricter audit.

Explicit local `$2C` writers are `$F3FF,$F443,$F486,$F4BF,$F4CF,$F4DC,$F4F3,$F5CF,$F629,$F635,$F64F,$F6FB,$F716,$F775,$F7B4,$F7DB`. ROM-local constant stores remain inside the encoded state family; conservative INC-root association reaches at most entry `$1C -> $1D` locally. This is **not** a transitive producer bound because out-of-window fixed and mapper-selected callees can still mutate `$2C`.

Evidence:

- `analysis/NMI_FIXED_2C_HEAD.md` — controlling
- `tools/audit_nmi_fixed_2c_head.py` — controlling audit
- `analysis/04FF_WORKING_NOTE.md` — active hold

## Current provenance boundary

```text
verified IRQ graph                    -> preserves $10
fixed NMI span $E057-$E365           -> preserves $10
$ED46 helper graph                    -> preserves $10
raw bank $0C / PRG24                 -> preserves $10 on live paths
raw bank $04 parser + 96/96 roots    -> preserves $10
raw bank $05 parser + 72/72 roots    -> preserves $10
$E7FB + first-level fixed graph       -> preserves $10
04FF 26-root fixed head               -> preserves $10 locally; 931 new bytes
$18 selector producer domain          -> unresolved
full $2C producer/target closure       -> unresolved
secondary $68 dispatch domains        -> unresolved
mapper-dependent fixed/banked exits   -> unresolved
PRG26 renderer                        -> consumes/persists $10 exactly
```

**VPP remains 21/100** because complete transitive pre-render NMI-helper closure is not yet proven.

## Active 04FF hold / next bounded investigation

`analysis/RESUME_STATE.json` remains **blocked at `$F3DD`**. Do not promote a `$F800` linear frontier yet: 04FF is a semantic state-machine closure, not a simple contiguous byte sweep.

The next useful raw window for the deferred fixed targets is:

```text
$F800-$FBFF   1024 raw bytes
SHA-256 f3090b53f174f15eeacad0d9e042efd95ff93ed6b4bfd706ba233ee5f588c86a
```

Useful alignment checks:

```text
$F7C0-$F7FF  SHA-256 0654eeccd284ba39d016f954cdfbe17b34b7218a1afe2bc6eca799a2713a13f7
$F800-$F81F  SHA-256 322b459da91a43e13712821aba143184801a6b9e6c91e0047f9826846a957f24
```

Continue 04FF by reconciling the deferred primary entries at `$F831/$F839/$F841/$F849/$F965`, the `$68`-indexed dispatches they expose, and mapper-selected callees that can affect `$2C`/`$10`. Only after those dependencies produce a safe semantic frontier should `RESUME_STATE.json` return to `ready`.
