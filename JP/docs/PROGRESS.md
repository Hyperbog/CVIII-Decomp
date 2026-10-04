# Decompilation progress ledger

## Current status

Work proceeds in bounded, ROM-backed checkpoints. Normal new-ROM budget is **500-5000 genuinely new bytes**. After any interruption read `docs/INTERRUPTION_RECOVERY.md`, `docs/ACCELERATION_POLICY.md`, and `analysis/RESUME_STATE.json`, then run `tools/check_resume_frontier.py` against the authoritative JP ROM.

Primary metric: **Verified Parity Progress (VPP) = 21 / 100 (21%)**. VPP is an evidence rubric, not raw-byte coverage or a time estimate.

Checkpoint **04FD closes the entire raw-bank `$05` sound-stream producer domain: 72/72 roots are now reconciled and ZP `$10`-safe.** The remaining pre-render dependency is fixed `PRG31:$E7FB` / inline dispatch.

## Stable foundation

- Exact JP ROM identity and 32 physical 8 KiB PRG-bank model are locked.
- Vectors: RESET `$E00B`, NMI `$E057`, IRQ `$E0F5`.
- VRC6 PRG bank helpers and fixed/switchable contexts are mapped.
- IRQ raw bank `$01` and its exact 45-entry state table are reconciled.
- NMI bank `$0D` renderer call `$8001` resolves to `PRG26:$8001`.
- Native OAM renderer baseline exists in `src/oam_renderer.*` with regression tests.
- Recovery tooling now verifies both switchable 16 KiB VRC6-bank frontiers and explicit fixed 8 KiB PRG mappings such as `PRG31:$E000-$FFFF`.

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
- **04FC:** next 25 bank-`$05` roots closed through `$AD96`; cumulative bank `$05` closure 44/72.
- **04FD:** final 28 bank-`$05` roots closed through semantic dependency `$BF05`; bank `$05` is **72/72 roots closed** and preserves `$10`.

## Operand-boundary invariant

Variable-width stream commands must have every consumed operand byte inside the claimed semantic dependency span before any operand is read. Raw `$FF` is not a generic terminator proxy. Preserve recursive `FB` loop-anchor, context-sensitive `FD` call/return, and `FE` counted/absolute-pointer state.

This invariant was introduced after recovery caught two `FE FF lo hi` commands whose operand bytes crossed earlier checkpoint boundaries. The historical 04F7/04F8 hold is resolved; `docs/INTERRUPTION_RECOVERY.md` now records it as repaired rather than active.

## Raw bank `$04` complete

All 96/96 raw-bank `$04` roots are closed. The final 04FA dependency was `$B1F0-$BE7D`, 3214 bytes, of which 3184 were genuinely new. Strict recursive decoding found no live `$E7` dispatch and no operand/path/pointer escapes. The complete bank-`$04` producer domain preserves shared ZP `$10`.

## Raw bank `$05` common parser

Raw bank `$05:$8001-$87AD` is byte-identical to the audited bank-$04 common parser core:

```text
1965 bytes
SHA-256 e2c3ff3d7e9f96b598610a8028f5b92a606fac7f9acb2977811146fa145fdb67
```

Metadata gives 84 references / 72 roots, all alternate-parser mode.

### 04FB — head

```text
$87AE-$9A6A
4797 genuinely new bytes
SHA-256 58f4a24e41ba95766529e1eaa531c63fc666ca51abc668ec4eb3ba3f4e50eb6b
19 roots closed
```

Nine unique live `$E7` sites produce following-byte high nibbles exactly `$0,$5,$8`; all select valid `$8430-$8443` table pairs and dispatch to audited `$8444`.

### 04FC — middle

```text
$9A6B-$AD96
4908 genuinely new bytes
SHA-256 3d34329fd18b7c713f1fe35206868f1b6c0bdfb6127f664410a60fd54a8c46f0
25 roots closed
```

Strict result: 7105 abstract states, 4221 unique commands, 22/22 FD calls/returns, 23 FE jumps, 56 FE loops, zero operand/path/pointer escapes. Three live `$E7` sites have producer high nibble exactly `$0` and dispatch to audited `$8444`.

### 04FD — tail / complete bank `$05`

Authoritative dependency:

```text
raw bank $05 / physical PRG11
CPU $AD97-$BF05
4463 genuinely new bytes
SHA-256 30f4e1640f97c342886a4d5f1a652cbfda41102abbd4760501bcd2915b474a72
```

The final 34 metadata references share 28 distinct roots across sounds `$57,$58,$59,$5B,$69,$6B`.

```text
abstract parser states:            5346
unique decoded command addresses:  3433
earliest command:                  $AD97
latest command:                    $BF05
FD calls / returns:                28 / 28
FE jumps / loops:                  15 / 43
operand/path escapes:              0
pointer-target escapes:            0
```

There are 21 raw `$E7` bytes in the dependency, 13 of which are decoded `$E7` commands. Their following-byte values produce high nibbles exactly `$0,$2,$8`; all are within the ten-entry `$8430-$8443` producer domain and resolve to already-audited `$8444`.

No host-side bound is added at `$842D`; safety is proved from the actual JP-ROM producer values.

After 04FD:

```text
bank-$05 roots total       72
closed                     72
remaining                   0
```

Evidence:

- `analysis/NMI_BANK05_PRG11_TAIL.md`
- `tools/audit_nmi_bank05_prg11_tail.py`

**VPP remains 21/100** because fixed `PRG31:$E7FB` / inline-dispatch closure is still required before the transitive NMI-helper rubric item can be reconsidered.

## Acceleration policy

Use NESdev, existing Castlevania III disassemblies, CDL/traces, Ghidra, `retrodisasm`, decompilers, `nesrecomp`, NSF metadata, and automated JP↔US matching aggressively as secondary accelerators. The Japanese ROM and reproducible parity evidence remain authoritative; external labels and structural matches stay provisional until reconciled against JP bytes/control/data flow.

## Current provenance boundary

```text
verified IRQ graph                 -> preserves $10
fixed NMI span $E057-$E365        -> preserves $10
$ED46 helper graph                 -> preserves $10
raw bank $0C / PRG24              -> preserves $10 on live paths
raw bank $04 parser + 96/96 roots -> preserves $10
raw bank $05 parser + 72/72 roots -> preserves $10
fixed PRG31 $E7FB / inline        -> unresolved
PRG26 renderer                     -> consumes/persists $10 exactly
```

## Next manageable checkpoint

**04FE — fixed `PRG31:$E7FB` / inline dispatch.**

The next genuinely unprocessed fixed-bank interval before already-audited 04F4 coverage is:

```text
CPU $E7FB-$EBFF
1029 contiguous bytes
```

Start exactly at `$E7FB` in physical PRG31. Follow actual 6502 control/data dependencies, reuse already-audited fixed-bank spans (`$E057-$E365` and `$EC00-$EFFF`) as prior coverage when reached, and count only genuinely new bytes. The recovery checker now supports the switchable-bank → fixed-PRG31 domain transition directly.
