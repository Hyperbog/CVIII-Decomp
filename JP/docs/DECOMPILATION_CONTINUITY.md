# Akumajou Densetsu decomp/recomp continuity playbook

Durable handoff for `Hyperbog/CVIII-Decomp`.

## Mandatory interruption recovery

After any timeout, chat/thread limit, token limit, tool interruption, crash, model/context switch, long pause, or uncertain partial checkpoint, **do not resume from chat memory**. Read `docs/INTERRUPTION_RECOVERY.md` and `analysis/RESUME_STATE.json` first, compare current branch history against the recorded checkpoint state, and run:

```text
python tools/check_resume_frontier.py <authoritative JP ROM.nes>
```

If `RESUME_STATE.json` is blocked/provisional, do not start the nominal next checkpoint. Repair only the recorded affected boundary/dependency, then reconcile the audit, analysis, progress, continuity, and resume state. The overlap is verification-only and must never be counted again as new coverage.

After the recovery gate passes, read this file, `docs/PROGRESS.md`, `docs/PROGRESS_METRIC.md`, and `docs/ROM_IDENTITY.md`, and confirm the current `decompilation` branch head.

## Objective and controlling evidence

Faithfully reverse engineer the Japanese NES release of **Akumajou Densetsu** into an evidence-accountable native PC decompilation/recompilation. Preserve original behavior first; QoL/mod work comes later.

ROM bytes are controlling evidence. Hardware documentation, public disassemblies, emulator behavior, NSF/M3U data, names, and hypotheses are secondary. Never commit the source ROM.

Target ROM:

- size `393232` (`0x60010`)
- SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`
- PRG 256 KiB, CRC32 `BA6BDD6A`
- CHR 128 KiB, CRC32 `BF15255C`
- Mapper 24 / Konami VRC6a

Primary metric: **VPP = 21/100**. It is evidence-based, not a labor estimate or raw-byte percentage.

## Checkpoint / fidelity policy

Each user `continue` means one bounded checkpoint:

- normally **500-5000 genuinely new ROM bytes**;
- expand only to close the same question and never silently exceed the budget;
- account separately for already-counted overlap/probe bytes;
- add reproducible audit/evidence artifacts;
- update progress/handoff and VPP only if earned;
- update `analysis/RESUME_STATE.json` last;
- commit and confirm branch head before reporting.

Never guess code/data boundaries, producer domains, or semantics. Track physical PRG bank + CPU address. Preserve 6502 widths, flags, wrapping, stack/interrupt behavior and shared zero page. Preserve VRC6 bank/IRQ semantics. Never extend a table merely because following bytes decode plausibly. Do not invent host-side bounds/defaults until producer domains are proved. Keep `$10` as shared NES RAM. No original ROM bytes in Git.

For variable-length instructions/streams, a claimed dependency span must include every operand/parameter byte actually read, not just the opcode/command byte.

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

`PRG26:$8001` iterates 28 render slots. Descriptors are full `Y,tile,attribute,X` or compressed `Y,tile,X`; compressed records consume persistent ZP `$10`. Full records update `$10`. OAM-full executes non-local `PLA; PLA; RTS`. Native baseline: `src/oam_renderer.*`, `tests/oam_renderer_test.cpp`.

`$9FA9` is normally reachable: checkpoints 04D-04E6 traced selector `$10` + frame `$14` to primary type `$08`; 04F1 proved its first three compressed sprites consume variable inherited `$10`, not a constant initializer.

## Pre-render `$10` provenance

- **04F2:** IRQ graph `PRG02/03:$9F99-$A526`, 1422 bytes, preserves `$10`.
- **04F3:** fixed NMI span `PRG31:$E057-$E365`, 783 bytes, preserves `$10`; external dependencies were `$ED46`, raw bank `$0C:$89E2`, and `$E7FB`/inline dispatch.
- **04F4:** `$ED46` graph in `PRG31:$EC00-$EFFF`, 1024 bytes, preserves `$10`.
- **04F5:** raw bank `$0C` / PRG24 `$8000-$91FF`, 4608 bytes, closed a conservative graph except `$842D`; all resolved writes are `$10`-clean.
- **04F6:** PRG24 `$9200-$9FFF`, 3584 bytes. `$842D` was proved to be a bank/parser-state over-approximation for bank `$0C`, not a missing local bounds check. Fixed `$E1AF` loads `$06D3,X`, banks it in, then jumps CPU `$8001`. Parser mode is bit 0 of `$011B,X`; initialization is from first stream byte + instrument index and later direct writers preserve bit 0. Bank `$0C`: 139 instrument refs, 125 roots, only five alternate-parser refs, all immediate `$FF` roots; all raw `$E7` bytes belong to main-parser roots. Evidence: `analysis/NMI_BANK0C_PARSER_MODE.md`, `tools/audit_nmi_bank0c_parser_mode.py`.
- **04F7:** raw bank `$04`. The parser executable core `$8001-$87AD` is byte-identical to the audited bank `$0C` alternate-parser core. Resolved graph: 786 accepted instruction starts and no write form capable of modifying/aliasing ZP `$10`. Metadata gives 102 bank-$04 refs / 96 roots; all initialize alternate-parser mode. This parser-core result remains valid.
- **04F8 stream work:** the recursive `FB`/`FD`/`FE` decoder corrected the earlier mistaken use of first raw `$FF` as a terminator proxy and found no live `$E7` in the investigated roots. The restart overlap subsequently exposed dependency-span accounting defects at the 04F7/04F8 boundary, described below.

## Current integrity hold — mandatory before further decompilation

`analysis/RESUME_STATE.json` is intentionally marked `BLOCKED_REPAIR_REQUIRED`. **Do not begin 04F9.**

Two boundary reads must be reconciled:

```text
04F7 root $9133:
$9208: FE FF 33 91
       command reads operand bytes $920A-$920B beyond old 04F7 span

04F8 root $9E85:
$A010: FE FF 85 9E
       command reads operand bytes $A012-$A013 beyond recorded 04F8 span
```

Do not redo the bank-$04 parser core or broad already-investigated root set. Harden `tools/audit_nmi_bank04_prg08_tail.py` so every multi-byte decoded command asserts all operand bytes are inside the accounted span, then recursively revalidate only the affected boundary/root cycles.

Candidate corrected 04F8 dependency, not authoritative until the hardened audit passes:

```text
CPU $920A-$A013
half-open [$920A,$A014)
3594 bytes
SHA-256 728c86cd808e178821f7f72d1f0371eb16a5bde3a1dda495543338391a5e7b3c
11 bytes overlap 04F7 mode probes
candidate 3583 genuinely new bytes
candidate next unresolved root $A014
```

VPP remains **21/100**. No credited rubric point depends on the disputed boundary accounting.

## Current provenance boundary

```text
verified IRQ graph                 -> preserves $10
fixed NMI span $E057-$E365        -> preserves $10
$ED46 helper graph                 -> preserves $10
live raw bank $0C / PRG24         -> preserves $10
raw bank $04 parser $8001-$87AD   -> preserves $10 on resolved graph
04F7/04F8 stream closures          -> PROVISIONAL only at affected boundary cycles
raw instrument bank $05           -> unresolved
$E7FB / inline dispatch            -> unresolved
PRG26 renderer                     -> consumes/persists $10 exactly
```

Do not add a host-side bound to `$842D`; its physical table remains ten entries at `$8430-$8443`.

## Repository workflow

Repository: `Hyperbog/CVIII-Decomp`

Working branch: `decompilation`

Primary hardware reference: NESdev Wiki. ROM bytes control game behavior.

Mandatory restart artifacts:

- `docs/INTERRUPTION_RECOVERY.md`
- `analysis/RESUME_STATE.json`
- `tools/check_resume_frontier.py`

## Current next action

**RECOVERY REPAIR — do not start 04F9 yet.**

1. Run `tools/check_resume_frontier.py <ROM.nes>`; it must hard-stop because the state is blocked while still verifying the candidate repair bytes.
2. Harden/re-run `tools/audit_nmi_bank04_prg08_tail.py` with strict operand-in-span checks.
3. Revalidate root `$9133` through `$9208: FE FF 33 91` including `$920A-$920B`, and the 04F8 roots through `$A010: FE FF 85 9E` including `$A012-$A013`.
4. Reconcile `analysis/NMI_BANK04_PRG08_TAIL.md`, `docs/PROGRESS.md`, this file, and `analysis/RESUME_STATE.json`.
5. Only after all checks pass, mark state `ready` at the first unresolved root (candidate `$A014`) and then begin 04F9 without redoing earlier ground.

## User-facing handoff prompt

> Continue the faithful Akumajou Densetsu decomp/recomp on branch `decompilation`. FIRST read `docs/INTERRUPTION_RECOVERY.md` and `analysis/RESUME_STATE.json` and run `tools/check_resume_frontier.py` against the exact JP ROM. Current state is intentionally BLOCKED: repair only the narrow 04F7/04F8 stream-boundary accounting (`$9208` operands through `$920B`, `$A010` operands through `$A013`) using strict operand-in-span assertions. Do not redo the bank-$04 parser core or earlier closed graphs. Reconcile audit/analysis/progress/continuity/state, then mark the frontier ready at the first unresolved root (candidate `$A014`) before starting 04F9. Preserve exact 6502/VRC6/shared-ZP semantics and count only genuinely new bytes.
