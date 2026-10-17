# 00 — Scope, Original Sources, Evidence Classes and Preservation Standard

**Status:** ACTIVE; first canonical documentation pass at checkpoint 0507. **Current evidenced build:** immutable JP NES ROM SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`; 393,232 bytes.

## Purpose and audiences

Record what the **shipped Japanese game** actually does, from encoded cartridge bytes to in-memory machine behavior, separately from modern C++ architecture and unproven historical intent. Audience: preservation researchers, recomp authors, emulator testers, NES developers and ROM-hack/mod authors. Primary evidence is the file whose identity is recorded in [ROM_IDENTITY](../docs/ROM_IDENTITY.md); code/data identities are *physical*, not merely CPU addresses.

## Evidence classes (adapted from RLOFT, not a completion rubric)

- **A — BYTE-PROVEN:** exact immutable JP bytes, hash and physical offset, with limited factual claim such as pointer contents or instruction encoding.
- **B — CODE-PROVEN:** exact original 6502 semantics, instruction/operand accounting, mapper context, branch/stack behavior where material, backed by committed audit.
- **C — PRODUCER/CONSUMER-CORROBORATED:** two or more JP source-code/data legs connected with proved selector domain and consumer; no blanket whole-program liveness inferred.
- **D — OFFICIAL/HARDWARE-DOCUMENTED:** MOS 6500, NES/2A03, NESdev, VRC6 hardware constraints. Helpful for instruction/PPU/IRQ behavior, not a substitute for original game flow.
- **E — CROSS-VERSION/COMMUNITY:** JP↔US exact/normalized matches, NSF/disassemblies and external explanations; accelerates naming, never overrides JP.
- **F — TESTED PARITY:** a precisely stated native/local execution or emulator comparison under a documented input universe. **Partial-algorithm exhaustive** tests must never be called whole-frame parity.

Every claim gets an explicit **proof scope**, and may have multiple grades. “UNKNOWN” denotes absent producer, mapper, historical provenance, timing or original design intent. “Structurally classified” is not itself grade B/C. Evidence can be downgraded or corrected without deleting the original checkpoint history.

## Accounting is separate from narrative

At verified checkpoint 0507 the project records **49,404 / 262,144 PRG bytes (18.8461%)** as the strict conservative semantic floor; candidate JP↔US structural correspondence covers 149,607 / 262,144 (57.0705%). [Score rubric](../docs/PROGRESS_METRIC.md) remains **24/100 VPP**, not a percentage of bytes or frames. Whole-PRG raw search is 100% scanned but includes data false positives. Recompute/consult [RESUME_STATE](../analysis/RESUME_STATE.json) for fresher values; **do not hardcode old dashboard values as eternal truths**.

Source-order rule: JP ROM > committed exact audits > machine state > archival prose > external hints. An archive discrepancy is a reason to reopen evidence, **not** permission to adjust ROM bytes or a progress score.

## What must be retained

- Bank-dependent CPU mapping at every external call, physical 8-KiB bank and original file offset.
- Exact operand consumption, array producer bounds, 8-bit wrap/carry/flags, stack/inline dispatch effects.
- Separate source-format preservation from decoded semantic representation; keep unclaimed bytes unclaimed.
- Original quirks **Q**, potentially dormant instructions **D**, legacy/reserved bytes **L**, modern reconstruction corrections **C**, historical/semantic UNKNOWN **U**. See [10](10_QUIRKS_CORRECTIONS_AND_UNKNOWNS.md).
- Host extensions/mods must never silently rewrite original behavior. [11](11_PROGRAMMER_MODDER_REFERENCE.md).

## Update template

**Claim ID / grade / scope**; ROM SHA + raw bank/physical PRG index + CPU entry + operand/table byte range; producer → decoder/handler → observable writes; native translation obligations; exact regression command; open index/mapper/interrupt paths; correction/unknown registry links. Check relative links with [archive auditor](../tools/audit_preservation_archive.py) and update [continuity](../docs/DECOMPILATION_CONTINUITY.md) and [progress](../docs/PROGRESS.md).
