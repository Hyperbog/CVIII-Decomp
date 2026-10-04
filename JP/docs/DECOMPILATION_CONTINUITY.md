# Akumajou Densetsu decomp/recomp continuity playbook

Durable handoff for `Hyperbog/CVIII-Decomp`.

## Mandatory interruption recovery

After any timeout, thread/token limit, tool interruption, crash, model/context switch, long pause, or uncertain partial checkpoint, **do not resume from chat memory**.

Read:

- `docs/INTERRUPTION_RECOVERY.md`
- `analysis/RESUME_STATE.json`

Then run:

```text
python tools/check_resume_frontier.py <authoritative JP ROM.nes>
```

If the state is blocked/provisional, repair only the recorded affected boundary/dependency. Do not start nominal forward work until the checker reports a ready frontier.

For variable-length instructions or streams, a claimed dependency span must include every operand/parameter byte actually read, not just the command byte.

## Objective and controlling evidence

Faithfully reverse engineer the Japanese NES release of **Akumajou Densetsu** into an evidence-accountable native PC decompilation/recompilation. Preserve original behavior first; QoL/mod work comes later.

ROM bytes are controlling evidence. Hardware documentation, public disassemblies, emulator behavior, NSF/M3U data, names, and hypotheses are secondary. Never commit the source ROM.

Target ROM:

- size `393232` (`0x60010`)
- SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`
- PRG 256 KiB, CRC32 `BA6BDD6A`
- CHR 128 KiB, CRC32 `BF15255C`
- Mapper 24 / Konami VRC6a

Primary metric: **VPP = 21/100**.

## Checkpoint / fidelity policy

Each user `continue` means one bounded checkpoint:

- normally **500-5000 genuinely new ROM bytes**;
- expand only to close the same question;
- account separately for already-counted overlap/probe bytes;
- add reproducible audit/evidence artifacts;
- update progress/handoff and VPP only if earned;
- update `analysis/RESUME_STATE.json` last;
- confirm branch head before reporting.

Never guess code/data boundaries, producer domains, or semantics. Track physical PRG bank + CPU address. Preserve 6502 widths, flags, wrapping, stack/interrupt behavior and shared zero page. Preserve VRC6 bank/IRQ semantics. Never add host-side bounds/defaults without producer proof. Keep `$10` as shared NES RAM.

## Stable cartridge / interrupt facts

VRC6 CPU map:

- `$6000-$7FFF`: PRG RAM
- `$8000-$BFFF`: switchable 16 KiB PRG ROM
- `$C000-$DFFF`: switchable 8 KiB PRG ROM
- `$E000-$FFFF`: fixed PRG31

Vectors: RESET `$E00B`, NMI `$E057`, IRQ `$E0F5`.

NMI bank `$0D` call `$8001` = `PRG26:$8001`. IRQ raw bank `$01` = PRG02/PRG03. IRQ table is exactly `PRG02:$9F01-$9F5A`, 45 states `$00-$2C`; `$9F5B` is code. `$80` is high-bit bypass. `$E118` clears IRQ Control before acknowledge; `$E11D` enters at acknowledge without that clear.

## Stable OAM / sprite facts

Read `analysis/PRG26_SPRITE_FORMAT.md`, `analysis/SPRITE_MASTER_TABLES.csv`, `analysis/OAM_OBJECT_FIELDS.csv`, `analysis/ZP10_OAM_STATE.md`, and `analysis/PRG26_9FA9_INCOMING_ATTR.md` before renderer changes.

`PRG26:$8001` iterates 28 render slots. Descriptors are full `Y,tile,attribute,X` or compressed `Y,tile,X`; compressed records consume persistent ZP `$10`. Full records update `$10`. OAM-full executes non-local `PLA; PLA; RTS`.

Native baseline: `src/oam_renderer.*`, `tests/oam_renderer_test.cpp`.

`$9FA9` is normally reachable and can begin with compressed records. 04F1 proved it consumes variable inherited `$10`, so pre-render provenance must remain exact.

## Pre-render `$10` provenance

- **04F2:** IRQ graph `PRG02/03:$9F99-$A526`, preserves `$10`.
- **04F3:** fixed NMI `$E057-$E365`, preserves `$10`; external dependencies `$ED46`, raw bank `$0C:$89E2`, `$E7FB`.
- **04F4:** `$ED46` graph preserves `$10`.
- **04F5:** raw bank `$0C` resolved graph is `$10`-clean; `$842D` left open conservatively.
- **04F6:** bank/parser state proves `$842D` is not live for bank `$0C`.
- **04F7:** raw bank `$04` parser core `$8001-$87AD` is byte-identical to audited bank `$0C` core; resolved graph is `$10`-clean. Bank `$04` metadata: 102 refs / 96 roots, all alternate-parser mode.
- **04F8:** first 34 bank-$04 roots are now fully reconciled under strict recursive stream decoding.

## Reconciled 04F7/04F8 boundary

The recovery checker found two four-byte commands whose operands extended beyond the old recorded spans:

```text
9208: FE FF 33 91 -> $9133
A010: FE FF 85 9E -> $9E85
```

The hardened audit now requires every multi-byte command's entire parameter footprint to lie inside its claimed semantic span before any operand is read.

### 04F7

Byte coverage remains exactly:

```text
CPU $8000-$9209
4618 contiguous bytes
+ 73 isolated root probes
= 4691 new bytes
```

Semantic closure of root `$9133` uses 04F8-owned operand overlap `$920A-$920B`.

Strict recheck of the 23 roots:

```text
states:                2819
unique commands:       2169
latest command:        $9208
decoded E7:            0
operand escapes:       0
pointer-target escapes: 0
```

### 04F8

Authoritative dependency span:

```text
CPU $920A-$A013
3594 bytes
SHA-256 728c86cd808e178821f7f72d1f0371eb16a5bde3a1dda495543338391a5e7b3c
11 prior root-probe bytes overlap
3583 genuinely new bytes
```

The 11 04F8 roots revalidate as:

```text
states:                3312
unique commands:       3025
latest command:        $A010
decoded E7:            0
operand escapes:       0
pointer-target escapes: 0
```

The final command `$A010: FE FF 85 9E` is fully contained through `$A013`.

Result:

```text
bank-$04 roots total       96
closed after 04F7/04F8     34
remaining                  62
first unresolved root      $A014
```

Evidence:

- `analysis/NMI_BANK04_ALT_PARSER_BOUNDARY.md`
- `analysis/NMI_BANK04_PRG08_TAIL.md`
- `tools/audit_nmi_bank04_prg08_tail.py`

Do not add a host-side bound to `$842D`.

## Current provenance boundary

```text
verified IRQ graph                 -> preserves $10
fixed NMI span $E057-$E365        -> preserves $10
$ED46 helper graph                 -> preserves $10
live raw bank $0C / PRG24         -> preserves $10
raw bank $04 parser $8001-$87AD   -> preserves $10 on resolved graph
raw bank $04 first 34 roots       -> reconciled; no live $E7
raw bank $04 remaining 62 roots   -> unresolved, first root $A014
raw instrument bank $05           -> unresolved
$E7FB / inline dispatch            -> unresolved
PRG26 renderer                     -> consumes/persists $10 exactly
```

VPP remains **21/100**.

## Repository workflow

Repository: `Hyperbog/CVIII-Decomp`

Working branch: `decompilation`

Primary hardware reference: NESdev Wiki. ROM bytes control game behavior.

Mandatory restart artifacts:

- `docs/INTERRUPTION_RECOVERY.md`
- `analysis/RESUME_STATE.json`
- `tools/check_resume_frontier.py`

## Current next checkpoint

**04F9 — raw bank `$04` / physical PRG09 continuation.**

Start exactly at CPU `$A014`. Initial bounded window:

```text
$A014-$B1FF
4588 contiguous bytes
```

Subtract any root-mode probe bytes already counted in 04F7 from exact new-byte coverage.

Carry `FB` loop-anchor, `FD` call/return, and `FE` counted/absolute-pointer state. Every multi-byte command must pass strict operand-in-span checks before operands are read. Prove pointer-target closure. Do not treat raw `$FF` as a terminator proxy.

Do not open raw bank `$05` or fixed `$E7FB` in the same checkpoint.

## User-facing handoff prompt

> Continue the faithful Akumajou Densetsu decomp/recomp on branch `decompilation`. First read `docs/INTERRUPTION_RECOVERY.md` and `analysis/RESUME_STATE.json` and run `tools/check_resume_frontier.py` against the exact JP ROM. The 04F7/04F8 boundary repair is reconciled; resume only from the committed ready frontier. Preserve exact 6502/VRC6/shared-ZP semantics, require full operand-in-span accounting for variable-length streams, count only genuinely new bytes, update `RESUME_STATE.json` last, and commit one bounded checkpoint. Current target: 04F9, raw bank `$04` from CPU `$A014`.
