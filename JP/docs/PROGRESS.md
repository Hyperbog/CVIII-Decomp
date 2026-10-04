# Decompilation progress ledger

## Current status

Work proceeds in bounded, ROM-backed checkpoints. Normal new-ROM budget is **500-5000 genuinely new bytes**. After any interruption read `docs/INTERRUPTION_RECOVERY.md`, `docs/ACCELERATION_POLICY.md`, and `analysis/RESUME_STATE.json`, then run `tools/check_resume_frontier.py` against the authoritative JP ROM.

Primary metric: **Verified Parity Progress (VPP) = 21 / 100 (21%)**. VPP is an evidence rubric, not raw-byte coverage or a time estimate.

Checkpoint **04FB closes the first 19/72 raw-bank `$05` sound-stream roots through CPU `$9A6A`**. Unlike bank `$04`, bank `$05` has live `$E7` commands; their actual producer domain has now been bounded and proven safe for this checkpoint.

## Stable foundation

- Exact JP ROM identity and 32 physical 8 KiB PRG-bank model are locked.
- Vectors: RESET `$E00B`, NMI `$E057`, IRQ `$E0F5`.
- VRC6 PRG bank helpers and fixed/switchable contexts are mapped.
- IRQ raw bank `$01` and its 45-entry state table are reconciled.
- NMI bank `$0D` renderer call `$8001` resolves to `PRG26:$8001`.
- Native OAM renderer baseline exists in `src/oam_renderer.*` with regression tests.

## Pre-render shared ZP `$10` provenance

- **04F2:** IRQ graph `PRG02/03:$9F99-$A526`, 1422 bytes, preserves `$10`.
- **04F3:** fixed NMI `PRG31:$E057-$E365`, 783 bytes, preserves `$10`; external dependencies identified.
- **04F4:** `$ED46` fixed helper graph, 1024 bytes, preserves `$10`.
- **04F5:** raw bank `$0C` / PRG24 `$8000-$91FF`, 4608 bytes; resolved graph `$10`-clean, `$842D` left conservatively open.
- **04F6:** bank/parser state proves `$842D` is unreachable for live bank-`$0C` stream data.
- **04F7:** raw bank `$04` alternate-parser core `$8001-$87AD` is byte-identical to the audited bank-`$0C` core; resolved graph has 786 accepted instruction starts and no write form capable of aliasing `$10`.
- **04F8:** first 34 bank-`$04` roots reconciled through `$A013` after strict operand-boundary repair.
- **04F9:** next 32 bank-`$04` roots closed through `$B1EF`.
- **04FA:** final 30 bank-`$04` roots closed through `$BE7D`; bank `$04` is **96/96 roots closed** and preserves `$10`.
- **04FB:** first 19 bank-`$05` roots closed through `$9A6A`; live `$E7` producer domain is bounded to safe `$842D` table entries.

## Operand-boundary invariant

Variable-width stream commands must have every consumed operand byte inside the claimed semantic dependency span before any operand is read. This rule was introduced after the 04F7/04F8 recovery checker caught two `FE FF lo hi` commands whose operands crossed earlier span boundaries.

Do not use raw `$FF` as a generic terminator proxy; preserve recursive `FB` loop-anchor, `FD` call/return, and `FE` counted/absolute-pointer state.

## 04FA — completed bank `$04`

Authoritative final bank-`$04` tail:

```text
CPU $B1F0-$BE7D
3214 dependency bytes
30 prior root-probe bytes overlap
3184 genuinely new bytes
SHA-256 a7f0a8308ed9335b27de8eaf3df440f0d28cd6f57fb97e4123222e3116fc5f55
```

Strict result: 3426 abstract states, 2595 unique commands, zero decoded `$E7`, zero operand/path/pointer escapes. All **96/96** bank-`$04` roots preserve shared ZP `$10`.

Evidence:

- `analysis/NMI_BANK04_PRG09_TAIL.md`
- `tools/audit_nmi_bank04_prg09_tail.py`

## 04FB — bank `$05` PRG10 head

Recovery crossed cleanly into raw bank `$05`. The executable parser core `$8001-$87AD` is byte-identical to the audited bank-`$04` core:

```text
1965 bytes
SHA-256 e2c3ff3d7e9f96b598610a8028f5b92a606fac7f9acb2977811146fa145fdb67
```

The exact metadata domain is 84 references / 72 distinct roots, all alternate-parser mode, from `$87AE` through `$BEE8`.

The largest clean first closure within budget is:

```text
raw bank $05 / physical PRG10
CPU $87AE-$9A6A
4797 dependency bytes
4797 genuinely new bytes
SHA-256 58f4a24e41ba95766529e1eaa531c63fc666ca51abc668ec4eb3ba3f4e50eb6b
```

It closes 19 references / 19 roots from sounds `$50-$53`:

```text
states:                  6437
unique commands:         3992
latest command:          $9A67
FD call/return:           26 / 26
FE jump/loop:             13 / 38
operand/path escapes:     0
pointer-target escapes:   0
```

Nine unique decoded `$E7` command sites have following-byte values `$50,$58,$55,$80,$02`; the producer high-nibble domain is exactly `$0,$5,$8`. The common handler computes the `$842D` pointer-table index from that high nibble. All are inside the ten-entry `$8430-$8443` table, whose entries all point to `$8444`. `$8444` is already in the audited ZP-`$10`-clean parser graph.

This proves the live 04FB `$E7` paths safe from the ROM producer domain; it does **not** add a host-side bound to `$842D`.

The next root `$9A6B` requires data through `$9B69`; including it would require **5052 genuinely new bytes**, so it is deferred.

After 04FB:

```text
bank-$05 roots total       72
closed                     19
remaining                  53
next unresolved root       $9A6B
```

Evidence:

- `analysis/NMI_BANK05_PRG10_HEAD.md`
- `tools/audit_nmi_bank05_prg10_head.py`

**VPP remains 21/100** because the remaining 53 bank-`$05` roots and fixed `$E7FB` inline dispatch are still open.

## Acceleration policy

Use NESdev, existing Castlevania III disassemblies, CDL/traces, Ghidra, `retrodisasm`, decompilers, `nesrecomp`, NSF metadata, and automated JP↔US matching aggressively as secondary accelerators. The Japanese ROM and reproducible parity evidence remain authoritative; external labels and structural matches are provisional until reconciled against JP bytes/control/data flow.

## Current provenance boundary

```text
verified IRQ graph                 -> preserves $10
fixed NMI span $E057-$E365        -> preserves $10
$ED46 helper graph                 -> preserves $10
raw bank $0C / PRG24              -> preserves $10 on live paths
raw bank $04 parser + 96/96 roots -> preserves $10
raw bank $05 first 19/72 roots    -> preserves $10 through $9A6A
raw bank $05 remaining 53 roots   -> unresolved, first $9A6B
$E7FB / inline dispatch            -> unresolved
PRG26 renderer                     -> consumes/persists $10 exactly
```

## Next manageable checkpoint

**04FC — continue raw bank `$05` from `$9A6B`.**

Suggested initial bounded window:

```text
CPU $9A6B-$ACBC
4690 contiguous bytes
```

Carry the same strict recursive stream state and explicit `$E7` producer-domain proof. Do not assume later `$E7` parameters have the 04FB domain; derive them from the actual later roots. Do not open fixed `$E7FB` in the same checkpoint.
