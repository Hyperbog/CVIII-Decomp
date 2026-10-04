# Akumajou Densetsu decomp/recomp continuity playbook

Durable handoff for `Hyperbog/CVIII-Decomp`, branch `decompilation`.

## Mandatory interruption recovery

After any timeout, token/thread limit, crash, model/context switch, long pause, or uncertain partial checkpoint, **do not resume from chat memory**.

Read:

- `docs/INTERRUPTION_RECOVERY.md`
- `docs/ACCELERATION_POLICY.md`
- `analysis/RESUME_STATE.json`

Then run:

```text
python tools/check_resume_frontier.py <authoritative JP ROM.nes>
```

If the state is blocked/provisional, repair only the recorded boundary/dependency. Forward work starts only from a committed `ready` state.

For variable-length instructions/streams, every operand byte actually read must lie inside the claimed semantic dependency span. Verification overlaps never count as new coverage.

## Objective and evidence hierarchy

Faithfully reverse engineer the Japanese NES release of **Akumajou Densetsu** into an evidence-accountable native PC decompilation/recompilation. Preserve original behavior before QoL/mod changes.

Controlling evidence order:

1. authoritative JP ROM bytes and observed JP execution;
2. reproducible ROM-backed audits/traces/native parity tests;
3. hardware documentation such as NESdev;
4. external disassemblies, CDL, decompilers, NSF metadata, Ghidra, `retrodisasm`, `nesrecomp`, and cross-version matching as accelerators;
5. hypotheses/semantic labels remain provisional until JP reconciliation.

Never commit the source ROM.

Target ROM:

```text
size       393232 / 0x60010
SHA-256    958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28
PRG        256 KiB, CRC32 BA6BDD6A
CHR        128 KiB, CRC32 BF15255C
mapper     24 / Konami VRC6a
```

Primary metric: **VPP = 21/100**. VPP is not raw byte coverage or remaining labor.

## Checkpoint policy

Each user `continue` means one bounded checkpoint:

- normally 500-5000 genuinely new ROM bytes;
- expand only to close the same coherent question;
- preserve exact 6502/VRC6/shared-zero-page semantics;
- add reproducible audit/evidence artifacts;
- update progress and continuity;
- update `analysis/RESUME_STATE.json` **last**;
- run the recovery checker and confirm branch head before reporting.

Never guess code/data boundaries, producer domains, indirect-dispatch bounds, or host-side defaults.

## Stable cartridge / interrupt / renderer facts

VRC6 CPU windows:

```text
$6000-$7FFF PRG RAM
$8000-$BFFF switchable 16 KiB PRG
$C000-$DFFF switchable 8 KiB PRG
$E000-$FFFF fixed PRG31
```

Vectors: RESET `$E00B`, NMI `$E057`, IRQ `$E0F5`.

NMI bank `$0D` call `$8001` = `PRG26:$8001`. IRQ raw bank `$01` = PRG02/PRG03. IRQ table is exactly `PRG02:$9F01-$9F5A`, 45 states `$00-$2C`; `$9F5B` is code. `$80` is the high-bit bypass. `$E118` clears IRQ Control before acknowledge; `$E11D` enters at acknowledge without that clear.

`PRG26:$8001` iterates 28 render slots. Full sprite records are `Y,tile,attribute,X`; compressed records are `Y,tile,X` and consume persistent shared ZP `$10`. Full records update `$10`. OAM-full can execute non-local `PLA; PLA; RTS`.

Native baseline: `src/oam_renderer.*`, `tests/oam_renderer_test.cpp`.

## Pre-render `$10` provenance history

- **04F2:** IRQ graph preserves `$10`.
- **04F3:** fixed NMI `$E057-$E365` preserves `$10`; external dependencies identified.
- **04F4:** `$ED46` graph preserves `$10`.
- **04F5:** raw bank `$0C` resolved graph is `$10`-clean; `$842D` conservatively left open.
- **04F6:** bank/parser state proves `$842D` is not live for bank `$0C` stream data.
- **04F7:** raw bank `$04` parser core `$8001-$87AD` is byte-identical to audited bank `$0C` code; resolved graph is `$10`-clean.
- **04F8:** first 34 bank-`$04` roots reconciled through `$A013` under strict operand accounting.
- **04F9:** next 32 bank-`$04` roots closed through `$B1EF`.
- **04FA:** final 30 bank-`$04` roots closed through `$BE7D`; **96/96 bank-`$04` roots closed**.
- **04FB:** first 19 bank-`$05` roots closed through `$9A6A`, including a live `$E7` producer-domain proof.

## Critical 04F7/04F8 recovery lesson

Two `FE FF lo hi` commands crossed old claimed boundaries:

```text
$9208: FE FF 33 91 -> $9133; operands through $920B
$A010: FE FF 85 9E -> $9E85; operands through $A013
```

All stream audits now assert operand containment before reading operands. Raw `$FF` is not a terminator proxy; carry `FB` loop-anchor, context-sensitive `FD` call/return, and `FE` counted/absolute-pointer state.

## 04FA — complete raw bank `$04`

Authoritative final dependency:

```text
raw bank $04 / PRG09
$B1F0-$BE7D
3214 dependency bytes
30 prior root-probe bytes overlap
3184 genuinely new bytes
SHA-256 a7f0a8308ed9335b27de8eaf3df440f0d28cd6f57fb97e4123222e3116fc5f55
```

Strict result: 3426 states, 2595 unique commands, zero decoded `$E7`, zero operand/path/pointer escapes. All 96/96 bank-`$04` roots preserve `$10`.

Evidence: `analysis/NMI_BANK04_PRG09_TAIL.md`, `tools/audit_nmi_bank04_prg09_tail.py`.

## 04FB — raw bank `$05` PRG10 head

Recovery transitioned to raw bank `$05` / PRG10-PRG11. Parser code `$8001-$87AD` is byte-identical to the audited bank-`$04` core:

```text
1965 bytes
SHA-256 e2c3ff3d7e9f96b598610a8028f5b92a606fac7f9acb2977811146fa145fdb67
```

Metadata domain:

```text
bank-$05 references       84
distinct roots            72
first root                $87AE
last root                 $BEE8
parser mode               alternate for all 84 refs
```

Authoritative 04FB dependency:

```text
raw bank $05 / PRG10
$87AE-$9A6A
4797 genuinely new bytes
SHA-256 58f4a24e41ba95766529e1eaa531c63fc666ca51abc668ec4eb3ba3f4e50eb6b
```

19 references / 19 distinct roots from sound IDs `$50-$53` close with:

```text
states                  6437
unique commands         3992
latest command          $9A67
FD call/return          26 / 26
FE jump/loop            13 / 38
operand/path escapes    0
pointer-target escapes  0
```

### Live `$E7` result

Nine unique decoded `$E7` command sites occur in 04FB. Their following-byte values are drawn from `$50,$58,$55,$80,$02`; the high-nibble producer domain is exactly `$0,$5,$8`.

The common handler at `$840F` masks that high nibble and doubles it to index pointer pairs at `$8430-$8443`. All three proven high nibbles are in range. The ten ROM entries all point to `$8444`, which belongs to the already-audited ZP-`$10`-clean common-code graph.

Therefore the first 19 bank-`$05` roots preserve `$10`. This is a producer-domain proof and does **not** justify adding a generic host-side bound at `$842D`.

The next root `$9A6B` requires bytes through `$9B69`; including it from the 04FB start would require 5052 new bytes, so the clean checkpoint boundary is `$9A6A`.

After 04FB:

```text
bank-$05 total       72 roots
closed               19
remaining            53
next root            $9A6B
```

Evidence:

- `analysis/NMI_BANK05_PRG10_HEAD.md`
- `tools/audit_nmi_bank05_prg10_head.py`

## Current provenance boundary

```text
verified IRQ graph                 -> preserves $10
fixed NMI span $E057-$E365        -> preserves $10
$ED46 helper graph                 -> preserves $10
live raw bank $0C / PRG24         -> preserves $10
raw bank $04 parser + 96/96 roots -> preserves $10
raw bank $05 first 19/72 roots    -> preserves $10 through $9A6A
raw bank $05 remaining 53 roots   -> unresolved, first $9A6B
$E7FB / inline dispatch            -> unresolved
PRG26 renderer                     -> consumes/persists $10 exactly
```

VPP remains **21/100**.

## Next checkpoint

**04FC — continue raw bank `$05` from CPU `$9A6B`.**

Suggested initial window:

```text
$9A6B-$ACBC
4690 contiguous bytes
```

Requirements:

- start exactly at `$9A6B` in raw bank `$05`;
- carry strict `FB`/`FD`/`FE` state and full operand containment;
- derive later `$E7` parameter domains from the actual producer roots; do not reuse the 04FB domain by assumption;
- prove all pointer targets stay inside the accounted semantic span;
- keep `$842D` unbounded in host code unless the complete producer domain proves otherwise;
- do not open fixed `$E7FB` in 04FC;
- update `RESUME_STATE.json` last.

## User-facing handoff prompt

> Continue the faithful Akumajou Densetsu decomp/recomp on branch `decompilation`. First read `docs/INTERRUPTION_RECOVERY.md`, `docs/ACCELERATION_POLICY.md`, and `analysis/RESUME_STATE.json`, then run `tools/check_resume_frontier.py` against the exact JP ROM. Use external tools/disassemblies aggressively as accelerators, but JP-ROM evidence controls. Current target: 04FC, raw bank `$05` from `$9A6B`; preserve strict operand accounting and derive every live `$E7` producer domain from ROM data.
