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

`tools/check_resume_frontier.py` supports mapper-bank domain transitions: the pre-frontier overlap and the next-frontier fingerprint may identify different raw VRC6 banks. Do not fake CPU-address contiguity across a bank transition.

## Objective and controlling evidence

Faithfully reverse engineer the Japanese NES release of **Akumajou Densetsu** into an evidence-accountable native PC decompilation/recompilation. Preserve original behavior first; QoL/mod work comes later.

ROM bytes are controlling evidence. Hardware documentation, public disassemblies, emulator behavior, NSF/M3U data, names, decompiler output, and hypotheses are secondary. Never commit the source ROM.

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

## Acceleration policy

Read `docs/ACCELERATION_POLICY.md`.

Use external resources aggressively to reduce identification time: NESdev, CDL/traces, Ghidra/NES tooling, `retrodisasm`, decompilers, `nesrecomp`, NSF metadata, and especially the existing Castlevania III disassembly in `cyneprepou4uk/NES-Games-Disassembly`.

The Japanese ROM always wins disagreements. US-version symbols/structures are candidate annotations until JP bytes and JP call/data flow verify equivalence. US mapper/audio behavior must not be transplanted into the VRC6 JP version. Dynamic traces prove observed execution, not global non-reachability.

Planned reusable accelerators include a normalized JP<->US routine/table matcher, whole-PRG reference atlas, RAM-symbol confidence map, trace import, and parity harnesses.

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

- **04F2:** IRQ graph preserves `$10`.
- **04F3:** fixed NMI `$E057-$E365` preserves `$10`; external dependencies are `$ED46`, raw bank `$0C:$89E2`, and `$E7FB`.
- **04F4:** `$ED46` graph preserves `$10`.
- **04F5:** raw bank `$0C` resolved graph is `$10`-clean; `$842D` left open conservatively.
- **04F6:** bank/parser state proves `$842D` is not live for bank `$0C`.
- **04F7:** raw bank `$04` parser core `$8001-$87AD` is byte-identical to audited bank `$0C` core; resolved graph is `$10`-clean. Bank `$04` metadata: 102 refs / 96 roots, all alternate-parser mode.
- **04F8:** first 34 bank-$04 roots are reconciled through `$A013` with strict operand accounting.
- **04F9:** next 32 roots are closed through `$B1EF`.
- **04FA:** final 30 roots are closed through semantic dependency `$BE7D`; bank `$04` is now **96/96 roots closed**.

## Reconciled 04F7/04F8 boundary

The recovery checker found two four-byte commands whose operands extended beyond old recorded spans:

```text
9208: FE FF 33 91 -> $9133
A010: FE FF 85 9E -> $9E85
```

The hardened stream audits require every multi-byte command's entire parameter footprint to lie inside its claimed semantic span before any operand is read.

04F8 authoritative dependency:

```text
CPU $920A-$A013
3594 bytes
SHA-256 728c86cd808e178821f7f72d1f0371eb16a5bde3a1dda495543338391a5e7b3c
11 prior root-probe bytes overlap
3583 genuinely new bytes
```

## 04F9

```text
raw bank $04 / physical PRG09
CPU $A014-$B1EF
4572 dependency bytes
SHA-256 55e35f223091a0c50beaf7ba0561445cc5c07d11ae83bfe827abcc22aa2d5a5b
32 prior root-mode probe bytes overlap
4540 genuinely new bytes
32 roots closed
states 5869; unique commands 3776; decoded E7 0
```

## 04FA — complete bank `$04`

Authoritative dependency:

```text
raw bank $04 / physical PRG09
CPU $B1F0-$BE7D
3214 dependency bytes
SHA-256 a7f0a8308ed9335b27de8eaf3df440f0d28cd6f57fb97e4123222e3116fc5f55
30 prior root-mode probe bytes overlap
3184 genuinely new bytes
```

36 metadata references / 30 distinct roots from sounds `$5F,$68,$6A,$6C,$6D,$6E` close with:

```text
states:                  3426
unique commands:         2595
latest command:          $BE7D
FD call/return:           20 / 20
FE jump/loop:             17 / 16
decoded E7:              0
operand/path escapes:     0
pointer-target escapes:   0
```

`$B81A == $E7` is only the pointer-low operand of `$B818: FE FF E7 B7 -> $B7E7`. `$BFEB == $E7` lies beyond all reachable bank-$04 commands/operands. Thus no bank-$04 root reaches `$840F/$842D`.

Result:

```text
bank-$04 roots total       96
closed                     96
remaining                   0
```

Evidence:

- `analysis/NMI_BANK04_PRG09_TAIL.md`
- `tools/audit_nmi_bank04_prg09_tail.py`

Do not add a host-side bound to `$842D`.

## Current provenance boundary

```text
verified IRQ graph                 -> preserves $10
fixed NMI span $E057-$E365        -> preserves $10
$ED46 helper graph                 -> preserves $10
live raw bank $0C / PRG24         -> preserves $10
raw bank $04 parser + all roots   -> preserves $10; 96/96 roots closed
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

**04FB — raw instrument bank `$05` / physical PRG10-PRG11.**

ROM metadata already establishes:

```text
bank-$05 references:       84
distinct roots:            72
first root:                $87AE
last root:                 $BEE8
```

All 84 bank-$05 references initialize alternate-parser mode under the same ROM rule, and raw bank `$05:$8001-$87AD` is byte-identical to the already-audited bank-$04 alternate-parser core.

Initial bounded window:

```text
$87AE-$99FF
4690 contiguous bytes
```

04FB should first assert parser-core identity and the exact metadata domain, then recursively close the largest root set fitting the normal 500-5000 genuinely-new-byte budget. Keep strict operand-in-span checks and pointer-target closure. If `$E7` is decoded, investigate its live parameter/domain; do not assume bank `$05` matches bank `$04` data behavior merely because the parser code matches.

Do not open fixed `$E7FB` in the same checkpoint.

## User-facing handoff prompt

> Continue the faithful Akumajou Densetsu decomp/recomp on branch `decompilation`. First read `docs/INTERRUPTION_RECOVERY.md`, `docs/ACCELERATION_POLICY.md`, and `analysis/RESUME_STATE.json`, then run `tools/check_resume_frontier.py` against the exact JP ROM. Resume only from the committed ready frontier. Use external disassemblies/CDL/tools aggressively as secondary accelerators, but Japanese-ROM evidence controls. Preserve exact 6502/VRC6/shared-ZP semantics, require full operand-in-span accounting, count only genuinely new bytes, update `RESUME_STATE.json` last, and commit one bounded checkpoint. Current target: 04FB, raw bank `$05` from CPU `$87AE`.
