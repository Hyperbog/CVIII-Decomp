# Decompilation progress ledger

## Current status

Work proceeds in bounded, ROM-backed checkpoints. Normal new-ROM budget is **500-5000 genuinely new bytes**. After any interruption read `docs/INTERRUPTION_RECOVERY.md`, `docs/ACCELERATION_POLICY.md`, and `analysis/RESUME_STATE.json`, then run `tools/check_resume_frontier.py` against the authoritative JP ROM.

Primary metric: **Verified Parity Progress (VPP) = 21 / 100 (21%)**. VPP is an evidence rubric, not raw-byte coverage or a time estimate.

Checkpoint **04FF closes the fixed `PRG31:$F3DD-$F7FF` nested-dispatch prefix and enumerates every local `$2C` write reachable from the 26 nested targets entering that interval.** All constant local producers are inside the encoded `$00-$1F` state family and the local graph has no indexed/indirect zero-page write that can hide a `$2C` alias. Complete `$2C` producer closure is still open because 136 exits leave the prefix and are not assumed to preserve `$2C` or shared ZP `$10`.

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
- **04FF:** fixed nested prefix `$F3DD-$F7FF` is decoded conservatively; local `$2C` producers are enumerated, but transitive callee effects remain open.

## Critical invariants

Variable-width stream commands must have every consumed operand byte inside the claimed semantic dependency span before any operand is read. Raw `$FF` is not a generic terminator proxy. Preserve `FB` loop anchors, context-sensitive `FD` call/return, and `FE` counted/absolute-pointer state.

For `$E7FB`, table size is **not** a selector-domain proof. Do not infer a host-side clamp for `$18` or `$2C` merely because the encoded first-level and nested tables contain 16 and 32 entries respectively.

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

## 04FF — nested `$2C` fixed prefix

Dependency interval:

```text
PRG31 $F3DD-$F7FF
1059 dependency bytes
SHA-256 72918e40813310fe3f967790d9b77e344a0f2ede92d12942d95c23849084b1b6
```

04FE already counted `$F6AE-$F6E3` (54 bytes), so 04FF contributes exactly **1005 genuinely new bytes**:

```text
$F3DD-$F6AD   721 bytes
$F6E4-$F7FF   284 bytes
ordered new-manifest SHA-256
257dfb57d710e3eb4ea9e4ff1d4d168901e65dc3afc7c1c6054c1c5d2548e51a
```

Of the nested table's 32 entries, 26 unique target addresses begin inside this prefix. Conservative in-prefix decoding yields:

```text
instruction starts                    401
unknown official opcodes                0
indexed/indirect zero-page writes       0
direct $2C writers                     16
deferred exits                         136
  JSR                                  124
  JMP                                    9
  branch                                 2
  fallthrough                            1
```

The explicit local `$2C` writers are at `$F3FF,$F443,$F486,$F4BF,$F4CF,$F4DC,$F4F3,$F5CF,$F629,$F635,$F64F,$F6FB,$F716,$F775,$F7B4,$F7DB`. Constant stores produce only `$01,$02,$07,$09,$0A,$0F,$10,$13`; root-associated INC sites are locally compatible with the `$00-$1F` table family. External callees are still allowed to mutate `$2C`, so this is not yet a complete producer-domain proof.

Evidence:

- `analysis/NMI_FIXED_2C_PREFIX.md`
- `tools/audit_nmi_fixed_nested_prefix.py`

## Current provenance boundary

```text
verified IRQ graph                    -> preserves $10
fixed NMI span $E057-$E365           -> preserves $10
$ED46 helper graph                    -> preserves $10
raw bank $0C / PRG24                 -> preserves $10 on live paths
raw bank $04 parser + 96/96 roots    -> preserves $10
raw bank $05 parser + 72/72 roots    -> preserves $10
$E7FB + first-level fixed graph       -> preserves $10
nested fixed prefix $F3DD-$F7FF       -> local $2C writers mapped; transitive exits open
$18 selector producer domain          -> unresolved
full $2C producer/target closure       -> unresolved
mapper-dependent banked exits         -> unresolved
PRG26 renderer                        -> consumes/persists $10 exactly
```

**VPP remains 21/100** because complete transitive pre-render NMI-helper closure is not yet proven.

## Next manageable checkpoint

**0500 — continue fixed PRG31 from `$F800`.**

Initial bounded interval:

```text
CPU $F800-$FBFF
1024 contiguous bytes
```

Recovery overlap:

```text
$F7C0-$F7FF  64 bytes
SHA-256 0654eeccd284ba39d016f954cdfbe17b34b7218a1afe2bc6eca799a2713a13f7
```

Frontier fingerprint:

```text
$F800-$F81F  32 bytes
SHA-256 322b459da91a43e13712821aba143184801a6b9e6c91e0047f9826846a957f24
```

0500 should cover the remaining nested entrypoints `$F831/$F839/$F841/$F849/$F965`, continue `$2C` producer reconciliation, subtract any prior 04FE/04FF overlap, and resolve actual mapper state before traversing `$8000-$BFFF` calls.
