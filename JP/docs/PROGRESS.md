# Decompilation progress ledger

## Current status

Work proceeds in bounded, ROM-backed checkpoints. Normal new-ROM budget is **500-5000 genuinely new bytes**. After any interruption read `docs/INTERRUPTION_RECOVERY.md`, `docs/ACCELERATION_POLICY.md`, and `analysis/RESUME_STATE.json`, then run `tools/check_resume_frontier.py` against the authoritative JP ROM.

Primary metric: **Verified Parity Progress (VPP) = 21 / 100 (21%)**. VPP is an evidence rubric, not raw-byte coverage or a time estimate.

Checkpoint **04FC closes the next 25 raw-bank `$05` roots through CPU `$AD96`**. Cumulative bank-`$05` closure is now **44/72 roots**.

## Stable foundation

- Exact JP ROM identity and 32 physical 8 KiB PRG-bank model are locked.
- Vectors: RESET `$E00B`, NMI `$E057`, IRQ `$E0F5`.
- VRC6 PRG bank helpers and fixed/switchable contexts are mapped.
- IRQ raw bank `$01` and its exact 45-entry state table are reconciled.
- NMI bank `$0D` renderer call `$8001` resolves to `PRG26:$8001`.
- Native OAM renderer baseline exists in `src/oam_renderer.*` with regression tests.

## Pre-render shared ZP `$10` provenance

- **04F2:** IRQ graph `PRG02/03:$9F99-$A526`, 1422 bytes, preserves `$10`.
- **04F3:** fixed NMI `PRG31:$E057-$E365`, 783 bytes, preserves `$10`; external dependencies identified.
- **04F4:** `$ED46` fixed helper graph, 1024 bytes, preserves `$10`.
- **04F5:** raw bank `$0C` / PRG24 `$8000-$91FF`, 4608 bytes; resolved graph `$10`-clean, `$842D` conservatively left open.
- **04F6:** bank/parser state proves `$842D` is unreachable for live bank-`$0C` stream data.
- **04F7:** raw bank `$04` alternate-parser core `$8001-$87AD` is byte-identical to the audited bank-`$0C` core; resolved graph has 786 accepted instruction starts and no write form capable of aliasing `$10`.
- **04F8:** first 34 bank-`$04` roots reconciled through `$A013` after strict operand-boundary repair.
- **04F9:** next 32 bank-`$04` roots closed through `$B1EF`.
- **04FA:** final 30 bank-`$04` roots closed through `$BE7D`; bank `$04` is **96/96 roots closed** and preserves `$10`.
- **04FB:** first 19 bank-`$05` roots closed through `$9A6A`; live `$E7` producer domain proven safe.
- **04FC:** next 25 bank-`$05` roots closed through `$AD96`; cumulative bank `$05` closure **44/72**.

## Operand-boundary invariant

Variable-width stream commands must have every consumed operand byte inside the claimed semantic dependency span before any operand is read. Raw `$FF` is not a generic terminator proxy. Preserve recursive `FB` loop-anchor, context-sensitive `FD` call/return, and `FE` counted/absolute-pointer state.

This invariant was introduced after recovery caught two `FE FF lo hi` commands whose operand bytes crossed earlier checkpoint boundaries.

## Raw bank `$04` complete

All 96/96 raw-bank `$04` roots are closed. The final 04FA dependency was `$B1F0-$BE7D`, 3214 bytes, of which 3184 were genuinely new. Strict recursive decoding found no live `$E7` dispatch and no operand/path/pointer escapes. The complete bank-`$04` producer domain preserves shared ZP `$10`.

## 04FB — bank `$05` head

Raw bank `$05:$8001-$87AD` is byte-identical to the audited bank-$04 common parser core:

```text
1965 bytes
SHA-256 e2c3ff3d7e9f96b598610a8028f5b92a606fac7f9acb2977811146fa145fdb67
```

Metadata gives 84 references / 72 roots, all alternate-parser mode.

04FB dependency:

```text
$87AE-$9A6A
4797 genuinely new bytes
SHA-256 58f4a24e41ba95766529e1eaa531c63fc666ca51abc668ec4eb3ba3f4e50eb6b
19 roots closed
```

Nine unique live `$E7` sites produce following-byte high nibbles exactly `$0,$5,$8`; all select valid `$8430-$8443` table pairs and dispatch to audited `$8444`. No host-side bound is added at `$842D`.

## 04FC — bank `$05` middle

The clean bounded dependency is:

```text
raw bank $05 / PRG10-PRG11
CPU $9A6B-$AD96
4908 genuinely new bytes
SHA-256 3d34329fd18b7c713f1fe35206868f1b6c0bdfb6127f664410a60fd54a8c46f0
```

It closes 31 metadata references sharing 25 distinct roots across sound IDs `$53,$54,$55,$56,$57,$5C`.

Strict recursive result:

```text
abstract parser states:            7105
unique decoded command addresses:  4221
earliest command:                  $9A6B
latest command:                    $AD96
FD calls / returns:                22 / 22
FE jumps / loops:                  23 / 56
operand/path escapes:              0
pointer-target escapes:            0
```

Exactly three raw `$E7` bytes occur in the dependency span, and all three are decoded commands:

```text
$9F5C -> $09
$A950 -> $0E
$AA13 -> $0D
```

Their producer high-nibble domain is exactly `$0`. The common `$840F/$842D` handler therefore selects the first in-range pointer pair at `$8430-$8431`, which resolves to already-audited `$8444`. These paths preserve `$10` from actual ROM producer values; no host-side bounds check is introduced.

The next root `$AD97` reaches through `$AE2D`; including it would make the checkpoint **5059 new bytes**, so 04FC deliberately stops at `$AD96`.

After 04FC:

```text
bank-$05 roots total       72
closed                     44
remaining                  28
next unresolved root       $AD97
```

Evidence:

- `analysis/NMI_BANK05_PRG10_MID.md`
- `tools/audit_nmi_bank05_prg10_mid.py`

**VPP remains 21/100** because the remaining 28 bank-`$05` roots and fixed `$E7FB` inline dispatch are still open.

## Acceleration policy

Use NESdev, existing Castlevania III disassemblies, CDL/traces, Ghidra, `retrodisasm`, decompilers, `nesrecomp`, NSF metadata, and automated JP↔US matching aggressively as secondary accelerators. The Japanese ROM and reproducible parity evidence remain authoritative; external labels and structural matches stay provisional until reconciled against JP bytes/control/data flow.

## Current provenance boundary

```text
verified IRQ graph                 -> preserves $10
fixed NMI span $E057-$E365        -> preserves $10
$ED46 helper graph                 -> preserves $10
raw bank $0C / PRG24              -> preserves $10 on live paths
raw bank $04 parser + 96/96 roots -> preserves $10
raw bank $05 first 44/72 roots    -> preserves $10 through $AD96
raw bank $05 remaining 28 roots   -> unresolved, first $AD97
$E7FB / inline dispatch            -> unresolved
PRG26 renderer                     -> consumes/persists $10 exactly
```

## Next manageable checkpoint

**04FD — continue raw bank `$05` from `$AD97`.**

Initial bounded window:

```text
CPU $AD97-$BFE8
4690 contiguous bytes
```

The remaining metadata roots end at `$BEE8`, but semantic dependencies must still be proved rather than inferred from root addresses. Carry the strict recursive stream state and derive every later `$E7` parameter domain from actual producer bytes. Do not open fixed `$E7FB` in the same checkpoint.
