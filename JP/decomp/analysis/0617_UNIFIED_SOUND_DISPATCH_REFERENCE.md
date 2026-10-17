# JP0617 — Unified original sound command → selected driver branch

**Status:** ROM-backed source and synthetic reference-parser tests PASS. A real independent original-Mesen2 capture was NOT obtained; no gameplay liveness or audio parity is claimed.

## Corrected source-level capture model

The original Japanese Mapper 24 ROM has raw bank $0C:$8850 STA $EF; $8852 CMP #$6F. Sampling the command at **$8852** reads original RAM $EF *after* the original A store and avoids relying on unverified Mesen Lua CPU register-table field names. The entry is restricted to tracked PRG bank $23==$0C and fixed-wrapper marker $26==$FF.

JP0616's separate callbacks did not establish that one original command produced one terminal decision. They could also misinterpret the **normal metadata path**: commands $50–$6E execute JSR $87AE at $885D and then continue at **$8860**. $885D is therefore an intermediate reset phase, not an independent terminal. The reset can modify original $0109, $019E and $06DD state; the new verifier intentionally does not demand that these memory values stay constant on the metadata path.

The unified [Lua observer](../tools/mesen_jp_sound_decisions_0617.lua) maintains a monotonic request ID and records precisely one driver terminal:

| Command | Phase | Driver terminal |
|---|---|---|
| $00–$4F with $0109==$50 and A>=$06 | None | low_return at $884F |
| Other $00–$4F | None | low_install at $8860 |
| $50–$6E | metadata JSR $87AE at $885D | meta_install at $8860 after return |
| $6F–$FF with old $019E>=$05 and (A-$6F)<old $019E | None | dmc_return at $8922 |
| Other $6F–$FF | None | dmc_program at $8928 |

It logs incoming command, original low-state guard $0109, DMC priority $019E and $06DD counter, and the corresponding decision-boundary state. Reset and state-loaded events are distinguished. The observer rejects nested/orphan requests and truncated logging. Execution of the original DMC-programming path is **not** evidence that all chip registers were written or that sound was audible.

## Proof and validation

[JP0617's fail-closed parser](../tools/jp_sound_decision_reference_0617.py) uses the existing original ROM SHA-256 and specific opcode witnesses from JP0616, and requires the previously SHA-pinned Mesen2 v2.1.1 agent/core before processing an actual independent reference. It validates positive emulator completion, callback errors, sequential IDs, intermediate metadata phase, single terminal per entry, branch predicate, DMC priority and $06DD changes, including 8-bit counter wrap.

An optional --native-dir performs original-to-native **command sequence only** comparison against an authenticated JP0614 **single power-on epoch**. The JP0614 native request CSV lacks original sound RAM $0109 and $019E snapshots, so request/terminal acceptance or rejected events cannot be compared to it directly. Native command equality also requires *matched user inputs, reset state, region and run duration* and proves neither voice ownership nor audio PCM parity.

Locally verified: synthetic Mesen JSONL with five command classes and two boundary records, and eleven negative cases; Python syntax compilation. The JP0616 prior source/ROM tests were rerun on the uploaded original Japanese ROM: 131,072 combinatorial state inputs and eight deliberate damaged-ROM witnesses PASS. Neither test is a real independent gameplay trace.

Original ROM SHA-256: 958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28. No original ROM/savestate/sound data or copyrighted external runtime is committed.

## Owner-only reproduction

1. Run the synthetic tests: python3 JP/decomp/tools/jp_sound_decision_reference_0617.py --smoke
2. Run the original branch witness: python3 JP/decomp/tools/jp_sound_priority_paths_0616.py YOUR_JP_ROM --self-test
3. In a private directory, run the **SHA-pinned** Mesen2 agent with original JP ROM, known controller inputs and JP/decomp/tools/mesen_jp_sound_decisions_0617.lua. Save its private JSONL.
4. Run jp_sound_decision_reference_0617.py --rom YOUR_JP_ROM --emulator YOUR_MESEN_BIN_DIR --mesen-stdout YOUR_JSONL --json YOUR_PRIVATE_REPORT.json. Add --native-dir YOUR_PRIVATE_ALPHA_DIR only for a matching one-epoch native session. Do not commit those files.

**Open R-007:** actual original Mesen2 execution, matched native request ingress, earlier producer triggers, accepted/rejected sound *liveness*, register writes and music/SFX/PCM ownership. The Lua callback's behavior on the pinned Mesen agent has not yet been verified.

**No progress promotion:** verified strict semantic PRG 49,504/262,144 (18.8843%), VPP 27/100, certified checkpoint 0508, fixed frontier $FB96. RESUME_STATE.json remains unchanged.
