# Decompilation progress ledger

## Current status

Work proceeds in bounded, ROM-backed checkpoints. Normal new-ROM budget is **500-5000 genuinely new bytes**. After any interruption read `docs/INTERRUPTION_RECOVERY.md` and `analysis/RESUME_STATE.json` and run `tools/check_resume_frontier.py` before forward work.

Primary metric: **Verified Parity Progress (VPP) = 21 / 100 (21%)**.

VPP is a fixed evidence rubric, not a time estimate or raw-byte percentage. See `docs/PROGRESS_METRIC.md`, `analysis/PROGRESS_SCORE.csv`, and `tools/progress_score.py`.

The 04F7/04F8 operand-boundary recovery hold is repaired. Checkpoint 04F9 now advances the authoritative raw-bank `$04` frontier to **CPU `$B1F0`**.

## Stable foundation

- Exact Japanese `Akumajou Densetsu` Mapper-24/VRC6a ROM identity is locked.
- PRG is modeled as 32 physical 8 KiB banks (`PRG00..PRG31`).
- Fixed vectors: RESET `$E00B`, NMI `$E057`, IRQ `$E0F5`.
- VRC6 PRG bank helpers and fixed/switchable contexts are mapped.
- NMI bank `$0D` call `$8001` resolves to `PRG26:$8001`.
- IRQ raw bank `$01` resolves into `PRG02/PRG03`.

## IRQ / OAM stable results

`PRG02:$9F01-$9F5A` is the exact 45-entry IRQ table for states `$00-$2C`; `$9F5B` is code. `$80` is the high-bit bypass sentinel. `$E118` clears IRQ Control before acknowledge; `$E11D` enters at acknowledge without that clear.

`PRG26:$8001` iterates 28 render slots. Sprite descriptors are full `Y,tile,attribute,X` or compressed `Y,tile,X`; compressed records consume persistent shared ZP `$10`, while full records update it. `$9FA9` is normally reachable and can begin with compressed records, so pre-render `$10` provenance matters.

Native baseline: `src/oam_renderer.*`, `tests/oam_renderer_test.cpp`.

## Pre-render `$10` provenance

- **04F2:** IRQ graph `PRG02/03:$9F99-$A526`, 1422 bytes, preserves `$10`.
- **04F3:** fixed NMI span `PRG31:$E057-$E365`, 783 bytes, preserves `$10`; external dependencies were `$ED46`, raw bank `$0C:$89E2`, and `$E7FB`/inline dispatch.
- **04F4:** `$ED46` graph in `PRG31:$EC00-$EFFF`, 1024 bytes, preserves `$10`.
- **04F5:** raw bank `$0C` / PRG24 `$8000-$91FF`, 4608 bytes, resolved graph `$10`-clean; `$842D` left open under conservative static reachability.
- **04F6:** PRG24 `$9200-$9FFF`, 3584 bytes. Parser/bank state proves `$842D` is not live for bank `$0C`; no host-side bound is added.
- **04F7:** raw bank `$04` parser core `$8001-$87AD` is byte-identical to the audited bank `$0C` alternate-parser core. Resolved graph: 786 accepted instruction starts and no write form capable of modifying/aliasing `$10`. Metadata gives 102 bank-$04 refs / 96 roots, all alternate-parser mode.
- **04F8:** strict recursive stream work closes the first 34 bank-$04 roots through `$A013`, with the 04F7/04F8 operand-boundary repair fully reconciled.
- **04F9:** closes 32 additional bank-$04 roots through `$B1EF`; cumulative closed roots are now 66/96.

## 04F7/04F8 recovery repair

The restart checker found two four-byte `FE FF lo hi` commands whose operands extended beyond their original claimed spans:

```text
04F7 root $9133: $9208 FE FF 33 91 -> operands through $920B
04F8 root $9E85: $A010 FE FF 85 9E -> operands through $A013
```

`tools/audit_nmi_bank04_prg08_tail.py` now asserts complete operand containment before reading any multi-byte command parameter.

Authoritative 04F8 dependency:

```text
raw bank $04 / CPU $920A-$A013
3594 bytes
SHA-256 728c86cd808e178821f7f72d1f0371eb16a5bde3a1dda495543338391a5e7b3c
11 prior root-probe bytes overlap
3583 genuinely new bytes
```

Strict recursive results remain zero decoded `$E7`, zero operand escapes, and zero pointer-target escapes. The first 34 of 96 bank-$04 roots are therefore reconciled and ZP `$10`-safe.

Evidence:

- `analysis/NMI_BANK04_ALT_PARSER_BOUNDARY.md`
- `analysis/NMI_BANK04_PRG08_TAIL.md`
- `tools/audit_nmi_bank04_alt_parser.py`
- `tools/audit_nmi_bank04_prg08_tail.py`

## 04F9 — physical PRG09 middle roots

Recovery began from the committed ready frontier `$A014`; ROM identity, overlap, frontier fingerprint, and the reconciled 04F8 audit all matched.

The largest clean closure within the 5000-new-byte budget is:

```text
raw bank $04 / physical PRG09
CPU $A014-$B1EF
4572 dependency bytes
SHA-256 55e35f223091a0c50beaf7ba0561445cc5c07d11ae83bfe827abcc22aa2d5a5b
32 root bytes already counted as 04F7 mode probes
4540 genuinely new bytes
```

The 32 roots belong to sound IDs `$60,$61,$62,$63,$64,$66`. Strict recursive decoding gives:

```text
abstract parser states:            5869
unique decoded command addresses:  3776
earliest command:                  $A014
latest command:                    $B1EC
FD calls / returns:                9 / 4
FE jumps / loops:                  20 / 62
decoded E7:                        0
operand/path/pointer escapes:      0
```

There are also zero raw `$E7` bytes in the span. Therefore none of these roots can activate handler `$840F` or indirect dispatch `$842D`; the already-audited parser core remains `$10`-clean on this producer domain.

The next root is `$B1F0` (sound `$68`, instrument `$03`). Its recursive dependency reaches through `$B3CB`. Including it in 04F9 would require 5048 dependency bytes / **5015 genuinely new bytes**, so it is deliberately deferred rather than exceeding the checkpoint budget.

After 04F9:

```text
bank-$04 roots total       96
closed                     66
remaining                  30
first unresolved root      $B1F0
```

Evidence:

- `analysis/NMI_BANK04_PRG09_MID.md`
- `tools/audit_nmi_bank04_prg09_mid.py`

**VPP remains 21/100 after 04F9.**

## Current provenance boundary

```text
verified IRQ graph                 -> preserves $10
fixed NMI span $E057-$E365        -> preserves $10
$ED46 helper graph                 -> preserves $10
raw bank $0C / PRG24              -> preserves $10 on live bank-$0C paths
raw bank $04 parser $8001-$87AD   -> preserves $10 on resolved graph
raw bank $04 first 34 roots       -> reconciled; no live $E7
raw bank $04 next 32 roots        -> closed through $B1EF; no live $E7
raw bank $04 remaining 30 roots   -> unresolved, first root $B1F0
raw instrument bank $05           -> unresolved
$E7FB / inline dispatch            -> unresolved
PRG26 renderer                     -> consumes/persists $10 exactly
```

## Unresolved / do not assume

- whether the remaining raw bank `$04` / physical PRG09 streams can activate `$842D` or another `$10`-relevant path;
- whether raw instrument bank `$05` can write/alias `$10`;
- whether `$E7FB` or its inline-dispatch targets can write `$10` before rendering;
- whole-ROM type-transition / selector-frame producer closure;
- higher-level meaning of `$AD` and exact visual meanings of IRQ states.

## Next manageable checkpoint

**04FA — finish raw bank `$04` / physical PRG09 tail.**

Start exactly at CPU `$B1F0`. The remaining raw-bank window is:

```text
$B1F0-$BFFF
3600 contiguous bytes
```

Thirty remaining root-mode probe bytes were already counted in 04F7 and must not be counted again. Carry the strict `FB`/`FD`/`FE` recursive state and require every operand byte to lie inside the accounted dependency span before reading it.

Do not open raw bank `$05` or fixed `$E7FB` in the same checkpoint.
