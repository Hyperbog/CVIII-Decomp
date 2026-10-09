# Akumajou Densetsu — Preservation Engineering Archive

**Target:** Japanese Akumajou Densetsu, mapper 24 / Konami VRC6a. **Status:** ACTIVE — incomplete technical reconstruction, not certified complete.

This is the canonical, reader-oriented subsystem archive for historical preservation, faithful recompilation, native runtime work, tooling, and future modders. Inspired by the **chapter/evidence/UNKNOWN/certification separation** in the connected [RLOFT PreservationArchive](https://github.com/Hyperbog/RLOFT/tree/code1-decompilation/PreservationArchive); these pages contain **NES-specific original research**, not imported RLOFT game facts.

**Source hierarchy:** immutable [JP ROM identity](../docs/ROM_IDENTITY.md) → ROM-locked committed audits and verified instruction/operand/data manifests → reproducible native and trace tests (scoped to what they test) → official NES/MOS hardware documentation → US-version disassembly and structural hints. The ROM controls disagreements. This repository must not distribute a ROM image or lossless byte-equivalent dump.

## Chapters

| Chapter | Subject | Status |
|---|---|---|
| [00](00_SCOPE_EVIDENCE_AND_SOURCE_BASELINE.md) | Scope, evidence grades, preservation protocol | active |
| [01](01_CARTRIDGE_PRG_CHR_MAPPER.md) | Immutable cartridge identity, VRC6 banks/mapper | partial |
| [02](02_CPU_RESET_NMI_IRQ_DISPATCH.md) | Reset, NMI, IRQ, banked dispatchers | partial |
| [03](03_PPU_OAM_SPRITE_PIPELINE.md) | Object sprite descriptors, OAM, PPU contract | partial |
| [04](04_OBJECT_SCHEDULER_COLLISION_SCRATCH.md) | Object iteration, scratch state, collision | partial |
| [05](05_AI_SCRIPT_AND_ACTION_VM.md) | AI script records, live actions, handler table | partial |
| [06](06_ROOMS_STAGE_WORLD_STATE.md) | Room load/state machine and missing world model | partial |
| [07](07_AUDIO_STREAMS_VRC6_APU.md) | Audio parsers, metadata roots, sound unknowns | partial |
| [08](08_NATIVE_RECOMP_AND_PARITY_CONTRACTS.md) | Native components, behavior/pixel/timing tests | partial |
| [09](09_DISCOVERY_ATLASES_AND_JP_US_MATCHING.md) | Whole-ROM atlas, candidate confidence, matching | audited tool baseline |
| [10](10_QUIRKS_CORRECTIONS_AND_UNKNOWNS.md) | Q/D/L/C/U register and contradictions | active |
| [11](11_PROGRAMMER_MODDER_REFERENCE.md) | Physical address notation, safe extension contracts | preliminary |
| [12](12_OPEN_RESEARCH_AND_CERTIFICATION_SCOPE.md) | Open proofs, documentation audit, future certification | active |

## Editing rule

Every material discovery receives (1) exact JP physical-bank and CPU address context, (2) evidence grade, (3) known algorithm/side effects, (4) caveats, (5) link to a reproducible audit/source/test, (6) specific native compatibility consequence, and (7) an UNKNOWN/quirk/correction entry if relevant. Update the responsible chapter **during the same checkpoint**, then progress/continuity and machine resume state **last**. A candidate table is not executable proof. A tested helper is not a bootable native game. Historical static documentation completion, verified PRG-byte coverage, VPP, and frame/runtime parity are **different measures**.

Historical checkpoint evidence stays in [analysis](../analysis/) and [docs](../docs/); this archive summarizes it rather than rewriting those logs. [Interruption recovery](../docs/INTERRUPTION_RECOVERY.md) remains authoritative for transactions. Audit local archive links/chapters using `python3 JP/tools/audit_preservation_archive.py` from repo root.
