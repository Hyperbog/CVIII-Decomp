# Semantic decompilation — partial original-source certification

**This is the research/source-reconstruction workstream, not the status of the existing playable native NESRecomp game.**

The original Japanese Mapper24 game is being reconstructed as independently understandable, source-faithful game data and code, plus increasingly reusable C11/C++ game-specific routines. Results require explicit physical PRG bank mapping, authenticated original bytes, mapped original-opcode or independent reference execution, and the historical strict PRG/VPP evidence rules.

## Current canonical research certificates

- **VPP: 31/100** on the fixed source-reconstruction rubric. [Scoring documentation](../../docs/PROGRESS_METRIC.md) and [machine-readable CSV](../../analysis/PROGRESS_SCORE.csv).
- **Strict verified PRG: 49,504/262,144 bytes (18.8843%)** in the historical original-source certificate. It is **not** the proportion of the original game playable through the native recompilation.
- Last strict semantic checkpoint **0508**, fixed PRG31 first unresolved frontier **$FB96**. [Recovery state](../../analysis/RESUME_STATE.json); [evidence ledger](../../analysis/NATIVE_EVIDENCE_LEDGER.json).
- Recent JP0657–JP0659 source work spans room data structures, conditional 6502/native state replay and private resource extraction. Dormant helpers may be compiled into the native host without replacing its live game execution. [Most recent evidence](../../analysis/0659_ORIGINAL_BANKED_ROOM_OBJECTS_AND_STAGE_EXTRACTOR.md).

The **score sources remain canonical at their existing stable paths**. Do not create a parallel, independently editable score counter in this folder; this workstream's [machine-readable index](EVIDENCE_STATE.json) points to them.

## Where to continue research

- [Continuity and handoff](../../docs/DECOMPILATION_CONTINUITY.md), [historical checkpoint ledger](../../docs/PROGRESS.md), [source certification rubric](../../docs/PROGRESS_METRIC.md).
- [Original independent reference emulator evidence](../../analysis/0508_MESEN_FIXED_LIVE_PROOF.md) and [strict evidence gate](../../tools/audit_native_evidence_ledger.py).
- [Room-loader source lift](../../native/enhanced/cviii_room_stream_0659.c), [original-opcode/native replay](../../tools/jp_room_stream_0659.py) and [private stage resource encoder](../../tools/jp_room_resources_0659.py).
- [Formal most recent VPP decision](../../analysis/0659_FORMAL_VPP_STAGE_FORMAT_AND_EXTRACTION_DECISION.md).
- [Native source-recovery regression workflow](../../../.github/workflows/jp-native-regressions.yml).

## What these metrics do not say

Neither **31/100 VPP** nor **18.8843% strict PRG** means the existing native executable is only 31% or 18.8843% playable. The full original game code runs through the native recompilation's 6502/VRC6 hardware abstraction while independently readable source replacement progresses in parallel. Native gameplay owner acceptance and Enhanced release QA are tracked [separately](../native-recompilation/README.md).

No strict physical PRG bytes are promoted because a conditional 6502 source test passes; an independent natural-gameplay trace, physical overlap reconciliation and semantic proof are separate requirements.
