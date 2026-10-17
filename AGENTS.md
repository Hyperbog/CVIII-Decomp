# Agent rules for CVIII-Decomp (NES Japanese and North American cartridges)

**Two separate Japanese workstreams:** [existing playable NESRecomp Enhanced Edition](JP/recomp/workstreams/native-recompilation/README.md) and [partial semantic source decompilation](JP/decomp/workstreams/semantic-decompilation/README.md). [Per-file ownership](JP/decomp/workstreams/WORKSTREAMS.json) separates player-tested product functionality from independent source VPP/PRG certification. **VPP and strict PRG are not native-game playability percentages.** Retain historic build paths and ledger paths until an audited atomic migration. Run `python3 JP/decomp/tools/audit_workstreams.py` when changing boundaries.

**Universal, cross-platform mod-forward requirement:** Read and apply [MOD_FORWARD_METHODOLOGY.md](MOD_FORWARD_METHODOLOGY.md) to all new runtime, asset, UI, audio, gameplay, settings, save, and tooling work. It applies equally to DOS, NES, SNES, SMS, Genesis/Mega Drive, and future projects. Preserve vanilla gameplay as the default reference; add stable IDs, replaceable data, validated registries, and editor-ready formats without pretending unsupported mod interfaces are already implemented.

Use [SharedDecomp/AGENT_RULES.md](SharedDecomp/AGENT_RULES.md) and the executable [evidence/replay gates](SharedDecomp/README.md). The active whole-bank target is Japanese VRC6 physical raw0A; other regions must not be substituted for small byte-count wins.

1. Never claim that original ROM roundtrip, candidate 6502 disassembly, or local routine parity equals a fully decompiled or playable native game.
2. Do not invent liveness or promote static instruction guesses. Track physical VRC6 PRG identity, mapper registers and CPU-visible alias in every CFG/trace claim.
3. Keep original licensed Japanese and North American ROMs out of commits/CI. Only compare against user-supplied original SHA-authenticated files locally.
4. Require exact bank/full-cart reconstruction and independent original-6502 versus compiled-host replay before marking a translated routine as tested. Prove PPU/APU/VRC6 event parity separately.
5. Never inflate strict historical PRG certificates when converting already documented bytes into readable source; preserve VPP scoring separately.
6. For bank0A, start at `JP/decomp/analysis/0539_NATIVE_RECOMP_WORKFLOW_FINDINGS.md` and the 0538 whole-bank atlas; resolve candidate code/data, genuine entry liveness, mapper context and native room-loader behavior before moving to another bank.
