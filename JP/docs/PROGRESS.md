# Decompilation progress ledger

## Current status

Work proceeds in bounded, ROM-backed checkpoints. Normal new-ROM budget is **500-5000 genuinely new bytes**. After any interruption read `docs/INTERRUPTION_RECOVERY.md` and `analysis/RESUME_STATE.json` and run `tools/check_resume_frontier.py` before forward work.

Primary metric: **Verified Parity Progress (VPP) = 21 / 100 (21%)**.

VPP is a fixed evidence rubric, not a time estimate or raw-byte percentage. See `docs/PROGRESS_METRIC.md`, `analysis/PROGRESS_SCORE.csv`, and `tools/progress_score.py`.

The 04F7/04F8 operand-boundary recovery hold has been repaired. The authoritative forward frontier is now **CPU `$A014`** in raw bank `$04` / physical PRG09.

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
- **04F8:** recursive stream work closes the first 34 bank-$04 roots after strict operand-boundary repair, described below.

## 04F7/04F8 recovery repair

The restart checker correctly blocked forward work after finding that two four-byte `FE FF lo hi` commands read operands just beyond their old claimed spans:

```text
04F7 root $9133:
$9208: FE FF 33 91
       operands extend through $920B

04F8 root $9E85:
$A010: FE FF 85 9E
       operands extend through $A013
```

`tools/audit_nmi_bank04_prg08_tail.py` now asserts that every multi-byte decoded command has all parameter bytes inside the claimed semantic span before any operand is read.

### Revalidated 04F7 boundary

04F7 byte coverage remains unchanged:

```text
CPU $8000-$9209
4618 contiguous bytes
+ 73 isolated root-mode probes
= 4691 new bytes
```

The final 04F7 root cycle is semantically revalidated through operand overlap `$920A-$920B`, whose byte coverage belongs to 04F8.

Strict recursive result for the 23 prior roots:

```text
abstract parser states:     2819
unique command addresses:   2169
latest command:             $9208
decoded E7:                 0
operand/pointer escapes:    0
```

Thus the substantive 04F7 safety result remains valid.

### Reconciled 04F8 dependency

Authoritative span:

```text
raw bank $04 / CPU $920A-$A013
3594 bytes
SHA-256 728c86cd808e178821f7f72d1f0371eb16a5bde3a1dda495543338391a5e7b3c
11 prior root-probe bytes overlap
3583 genuinely new bytes
```

For the 11 04F8 roots:

```text
abstract parser states:     3312
unique command addresses:   3025
earliest command:           $920C
latest command:             $A010
decoded E7:                 0
operand escapes:            0
pointer-target escapes:     0
```

The final cycle `$A010: FE FF 85 9E -> $9E85` is fully contained through `$A013`.

Therefore the first **34 of 96** bank-$04 roots are reconciled and ZP `$10`-safe. **62 roots remain**, beginning at `$A014`.

Evidence:

- `analysis/NMI_BANK04_ALT_PARSER_BOUNDARY.md`
- `analysis/NMI_BANK04_PRG08_TAIL.md`
- `tools/audit_nmi_bank04_alt_parser.py`
- `tools/audit_nmi_bank04_prg08_tail.py`

**VPP remains 21/100.**

## Current provenance boundary

```text
verified IRQ graph                 -> preserves $10
fixed NMI span $E057-$E365        -> preserves $10
$ED46 helper graph                 -> preserves $10
raw bank $0C / PRG24              -> preserves $10 on live bank-$0C paths
raw bank $04 parser $8001-$87AD   -> preserves $10 on resolved graph
raw bank $04 first 23 roots       -> reconciled; no live $E7
raw bank $04 next 11 roots        -> reconciled through $A013; no live $E7
raw bank $04 remaining 62 roots   -> unresolved, first root $A014
raw instrument bank $05           -> unresolved
$E7FB / inline dispatch            -> unresolved
PRG26 renderer                     -> consumes/persists $10 exactly
```

## Unresolved / do not assume

- whether later raw bank `$04` / physical PRG09 streams can activate `$842D` or another `$10`-relevant path;
- whether raw instrument bank `$05` can write/alias `$10`;
- whether `$E7FB` or its inline-dispatch targets can write `$10` before rendering;
- whole-ROM type-transition / selector-frame producer closure;
- higher-level meaning of `$AD` and exact visual meanings of IRQ states.

## Next manageable checkpoint

**04F9 — continue raw bank `$04` / physical PRG09 from `$A014`.**

Use an initial bounded window `$A014-$B1FF` (4588 contiguous bytes). Root-probe bytes already counted by 04F7 must not be counted again.

Carry the recursive `FB` loop-anchor, `FD` call/return, and `FE` counted/absolute-pointer state. Every multi-byte command must pass strict operand-in-span checks before reading parameters. Prove pointer-target closure rather than using raw `$FF` as a terminator proxy.

Do not open raw bank `$05` or fixed `$E7FB` in the same checkpoint.
