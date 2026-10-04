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

If the state is blocked/provisional, repair only the recorded boundary/dependency. Forward work starts only from a committed `ready` state. Every consumed operand byte in a variable-width stream command must lie inside the claimed semantic dependency span. Verification overlaps never count as new coverage.

`tools/check_resume_frontier.py` supports both switchable raw VRC6 16 KiB mappings and explicit physical 8 KiB PRG mappings, so a resume may safely cross from `$8000-$BFFF` banked data into fixed `PRG31:$E000-$FFFF` without pretending CPU addresses are contiguous.

## Objective and evidence hierarchy

Faithfully reverse engineer the Japanese NES release of **Akumajou Densetsu** into an evidence-accountable native PC decompilation/recompilation. Preserve original behavior before QoL/mod changes.

Evidence order:

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

Each user `continue` means one bounded checkpoint, normally 500-5000 genuinely new ROM bytes. Preserve exact 6502/VRC6/shared-zero-page semantics, add reproducible evidence, update progress/continuity, update `analysis/RESUME_STATE.json` **last**, then run the recovery checker and confirm branch head.

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
- **04F7:** raw bank `$04` common parser code is `$10`-clean.
- **04F8:** first 34 bank-`$04` roots reconciled through `$A013` under strict operand accounting.
- **04F9:** next 32 bank-`$04` roots closed through `$B1EF`.
- **04FA:** final 30 bank-`$04` roots closed through `$BE7D`; **96/96 bank-`$04` roots closed**.
- **04FB:** first 19 bank-`$05` roots closed through `$9A6A`, including live `$E7` producer-domain proof.
- **04FC:** next 25 bank-`$05` roots closed through `$AD96`.
- **04FD:** final 28 bank-`$05` roots closed through `$BF05`; **72/72 bank-`$05` roots closed**.

## Critical stream-audit invariant

Two earlier `FE FF lo hi` commands crossed old checkpoint boundaries:

```text
$9208: FE FF 33 91 -> $9133; operands through $920B
$A010: FE FF 85 9E -> $9E85; operands through $A013
```

All stream audits must assert operand containment before reading operands. Raw `$FF` is not a terminator proxy. Carry `FB` loop-anchor, context-sensitive `FD` call/return, and `FE` counted/absolute-pointer state.

The old 04F7/04F8 recovery hold is resolved; `docs/INTERRUPTION_RECOVERY.md` was corrected in 04FD so it no longer describes that historical repair as an active block.

## Raw bank `$04` closure

All 96/96 bank-`$04` roots are closed and preserve shared ZP `$10`. Final dependency: `$B1F0-$BE7D`, 3214 bytes, 3184 genuinely new; zero decoded `$E7`, zero operand/path/pointer escapes.

## Raw bank `$05` common parser

`$8001-$87AD` in raw bank `$05` is byte-identical to the audited bank-$04 common core:

```text
1965 bytes
SHA-256 e2c3ff3d7e9f96b598610a8028f5b92a606fac7f9acb2977811146fa145fdb67
```

Metadata domain:

```text
references       84
roots            72
first root       $87AE
last root        $BEE8
parser mode      alternate for all refs
```

### 04FB — bank `$05` head

```text
$87AE-$9A6A
4797 genuinely new bytes
SHA-256 58f4a24e41ba95766529e1eaa531c63fc666ca51abc668ec4eb3ba3f4e50eb6b
19 roots closed
```

Nine unique live `$E7` sites have producer high nibbles exactly `$0,$5,$8`; all index valid `$8430-$8443` pairs and resolve to audited `$8444`.

### 04FC — bank `$05` middle

```text
$9A6B-$AD96
4908 genuinely new bytes
SHA-256 3d34329fd18b7c713f1fe35206868f1b6c0bdfb6127f664410a60fd54a8c46f0
25 roots closed
```

31 metadata refs share 25 roots. Strict result: 7105 states, 4221 unique commands, 22/22 FD calls/returns, 23 FE jumps, 56 FE loops, zero operand/path/pointer escapes. Live `$E7` producer high nibble is exactly `$0`, dispatching to audited `$8444`.

### 04FD — bank `$05` tail / complete

Authoritative dependency:

```text
raw bank $05 / physical PRG11
$AD97-$BF05
4463 genuinely new bytes
SHA-256 30f4e1640f97c342886a4d5f1a652cbfda41102abbd4760501bcd2915b474a72
```

34 metadata references share 28 roots from sounds `$57,$58,$59,$5B,$69,$6B`.

```text
states                  5346
unique commands         3433
latest command          $BF05
FD call/return          28 / 28
FE jump/loop            15 / 43
operand/path escapes    0
pointer-target escapes  0
```

Thirteen unique decoded `$E7` commands produce parameter high nibbles exactly `$0,$2,$8`. Each selects an in-range `$8430-$8443` pair and resolves to audited `$8444`. This is producer-domain proof from JP ROM data, not a generic host-side `$842D` bound.

After 04FD:

```text
bank-$05 total       72
closed               72
remaining             0
```

Evidence:

- `analysis/NMI_BANK05_PRG11_TAIL.md`
- `tools/audit_nmi_bank05_prg11_tail.py`

## Current provenance boundary

```text
verified IRQ graph                 -> preserves $10
fixed NMI span $E057-$E365        -> preserves $10
$ED46 helper graph                 -> preserves $10
live raw bank $0C / PRG24         -> preserves $10
raw bank $04 parser + 96/96 roots -> preserves $10
raw bank $05 parser + 72/72 roots -> preserves $10
fixed PRG31 $E7FB / inline        -> unresolved
PRG26 renderer                     -> consumes/persists $10 exactly
```

VPP remains **21/100**.

## Next checkpoint

**04FE — fixed `PRG31:$E7FB` / inline dispatch.**

Start exactly at fixed `PRG31:$E7FB`. The not-yet-accounted fixed-bank interval before already-audited 04F4 coverage is:

```text
$E7FB-$EBFF
1029 contiguous bytes
```

Requirements:

- verify the switchable bank `$05:$BEC6-$BF05` recovery overlap and the fixed `PRG31:$E7FB-$E81A` fingerprint;
- treat `PRG31:$E000-$FFFF` as an explicit fixed 8 KiB physical mapping, not a raw 16 KiB VRC6 bank;
- decode actual 6502 control flow and any inline-dispatch data from `$E7FB`;
- reuse prior fixed-bank coverage `$E057-$E365` and `$EC00-$EFFF` when reached instead of counting it again;
- follow any genuinely new dependency beyond `$EBFF` only as needed within the normal byte budget;
- preserve exact stack/flags/indirect-address behavior and shared ZP `$10` semantics;
- update `RESUME_STATE.json` last.

## User-facing handoff prompt

> Continue the faithful Akumajou Densetsu decomp/recomp on branch `decompilation`. First read `docs/INTERRUPTION_RECOVERY.md`, `docs/ACCELERATION_POLICY.md`, and `analysis/RESUME_STATE.json`, then run `tools/check_resume_frontier.py` against the exact JP ROM. Use external tools/disassemblies aggressively as accelerators, but JP-ROM evidence controls. Current target: 04FE, fixed `PRG31:$E7FB` / inline dispatch. Reuse already-audited fixed-bank spans and count only genuinely new bytes.
