# Decompilation progress ledger

## Current status

Work proceeds in bounded, ROM-backed checkpoints. Normal new-ROM budget is **500-5000 genuinely new bytes**. After any interruption read `docs/INTERRUPTION_RECOVERY.md`, `docs/ACCELERATION_POLICY.md`, and `analysis/RESUME_STATE.json`, then run `tools/check_resume_frontier.py` against the authoritative JP ROM.

Primary metric: **Verified Parity Progress (VPP) = 21 / 100 (21%)**. VPP is an evidence rubric, not raw-byte coverage or a time estimate.

Checkpoint **04FE resolves the fixed `PRG31:$E7FB` inline-dispatch mechanism and proves its first-level fixed-bank graph preserves shared ZP `$10`.** Complete transitive closure is still open because the `$18` and nested `$2C` selector producer domains and 21 banked exits have not yet been reconciled.

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

## Critical stream/dispatch invariants

Variable-width stream commands must have every consumed operand byte inside the claimed semantic dependency span before any operand is read. Raw `$FF` is not a generic terminator proxy. Preserve `FB` loop anchors, context-sensitive `FD` call/return, and `FE` counted/absolute-pointer state.

For `$E7FB`, table size is **not** a selector-domain proof. Do not infer a host-side clamp for `$18` or `$2C` merely because the encoded first-level and nested tables contain 16 and 32 entries respectively.

## Raw bank `$04` complete

All 96/96 roots are closed. Final 04FA dependency: `$B1F0-$BE7D`, 3214 bytes, 3184 genuinely new. Zero decoded `$E7` and zero operand/path/pointer escapes.

## Raw bank `$05` complete

`$8001-$87AD` is byte-identical to the audited bank-$04 common parser core. Metadata contains 84 references / 72 roots, all alternate-parser mode.

- **04FB:** `$87AE-$9A6A`, 4797 new bytes, 19 roots.
- **04FC:** `$9A6B-$AD96`, 4908 new bytes, 25 roots.
- **04FD:** `$AD97-$BF05`, 4463 new bytes, final 28 roots.

Bank `$05` is **72/72 roots closed**. The final 04FD tranche has 5346 abstract states, 3433 unique commands, 28/28 FD calls/returns, 15 FE jumps, 43 FE loops, and zero operand/path/pointer escapes. Its 13 decoded `$E7` commands have high-nibble domain exactly `$0,$2,$8`, all selecting in-range `$8430-$8443` entries that resolve to audited `$8444`.

## 04FE — fixed `$E7FB` first-level dispatch

`$E7FB-$E813` is an inline tail dispatcher. It doubles A, preserves Y in `$03`, pops the caller's JSR return address into `$00/$01`, reads a little-endian pointer from the caller's bytes at `return+1+2*A`, restores Y, and executes `JMP ($0002)`. The dispatcher itself writes only `$00-$03`.

The NMI call at `$E360` loads A from `$18`. Its inline table at `$E363-$E382` has 16 encoded pointers:

```text
00 E383  01 E436  02 E437  03 E449
04 F390  05 E459  06 E49B  07 E539
08 E50E  09 E516  0A E541  0B E549
0C E51E  0D E526  0E E52E  0F E531
```

A conservative decode from all 16 targets yields:

```text
fixed instruction starts   435
unknown opcodes               0
nested E7FB sites              1  ($F39A)
external banked exits         21
```

No direct store/RMW reaches ZP `$10`. Reachable indexed ZP writes are limited by ROM-proven X domains:

```text
E7BA STA $00,X  -> X $28/$4D .. $DF
E7F3 STA $F0,X  -> X $00 .. $07
E82A STA $00,X  -> X=$00 at reachable callers
E82E INC $01,X  -> X=$00 at reachable callers
```

Therefore the resolved first-level **fixed** graph preserves `$10`.

First-level entry `$04` reaches `$F390`, which performs a nested dispatch with `A=$2C`. Its 32 encoded pointer pairs occupy `$F39D-$F3DC`; `$F3DD` is code (`A9 02`). This proves the structural boundary only. The live `$2C` producer domain remains unresolved.

04FE exact genuinely-new fixed coverage is **957 bytes**, stored as an explicit noncontiguous manifest. Ordered-manifest SHA-256:

```text
a672f908a238bea20902fc40c5417622bdb9af675cda3b982a6f0ce494ebad32
```

Evidence:

- `analysis/NMI_FIXED_E7FB_DISPATCH.md`
- `tools/audit_nmi_fixed_e7fb_dispatch.py`

## Current provenance boundary

```text
verified IRQ graph                    -> preserves $10
fixed NMI span $E057-$E365           -> preserves $10
$ED46 helper graph                    -> preserves $10
raw bank $0C / PRG24                 -> preserves $10 on live paths
raw bank $04 parser + 96/96 roots    -> preserves $10
raw bank $05 parser + 72/72 roots    -> preserves $10
$E7FB + first-level fixed graph       -> preserves $10
$18 selector producer domain          -> unresolved
nested $2C selector/target graph      -> unresolved; table ends $F3DC
21 mapper-dependent banked exits      -> unresolved
PRG26 renderer                        -> consumes/persists $10 exactly
```

**VPP remains 21/100** because the complete transitive pre-render NMI-helper closure is not yet proven.

## Next manageable checkpoint

**04FF — continue fixed PRG31 at `$F3DD` and resolve the nested `$2C` dispatch domain/graph.**

Initial bounded interval:

```text
CPU $F3DD-$F7FF
1059 contiguous bytes
```

Recovery overlap is the 64-byte nested table `$F39D-$F3DC`, SHA-256 `81d06cd79d64c3d4cfe14bbefa851e74e748536f723636abaf82870ec065d22f`. Frontier fingerprint `$F3DD-$F3FC` has SHA-256 `65d47f163ffad5ca20903cece8606c76416ceb5cb8edba99780be720730f08aa`.

04FF must reuse every 04FE manifest range as prior coverage, prove the actual `$2C` producer domain rather than infer it from the 32-entry table, and resolve mapper state before following any `$8000-$BFFF` external target.
