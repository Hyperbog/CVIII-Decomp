## Mandatory delivery-first rule — applies to the entire Git portfolio

**Scope:** RLOFT, CVIII, Ys, Phantasy Star, and every other repository or workstream. This is a hard instruction for AI coding/research agents, not an optional preference. Existing source-authentication, copyright, safety, branch-ownership, and required acceptance gates remain binding.

1. **Deliver functioning code, not a procession of tests.** Begin with the requested user-visible end state. Identify the causal defect, make the smallest principled production-level correction, and integrate it. Test infrastructure, static inventories, synthetic fixtures, reports, and experimental variants are supporting tools, **not completed features or progress milestones** by themselves.
2. **Hard cap on exploratory loops.** Reuse the code, logs, recordings, and existing tests first. Allow **at most one baseline reproduction and two focused diagnostic experiments per unresolved defect**. Each experiment must decide a specific implementation choice. After that, **stop experimenting**: implement the best source-supported correction, switch to a fundamentally different implementation strategy, or report the precise blocker. Do not create new named stages/checkpoints to evade this limit.
3. **No speculative piles of variants.** Do not keep adjusting constants, offsets, timing, flags, emulator settings, or synthetic tests until one happens to match. Do not build adjacent diagnostic frameworks where direct product implementation is possible. A narrow diagnostic is justified only when it directly changes the next code decision.
4. **One integrated fix, then essential proof.** Validate the changed functionality with a focused regression and the existing relevant end-to-end/CI gates. Preserve independent original-vs-native evidence where required. **After two non-improving implementation/validation attempts, stop that approach**; isolate the blocker and change strategy rather than loop.
5. **Progress means real capability.** Never call a milestone successful merely because tools compile, CI smoke passes, an experimental replay looks better, or a report is committed. Claim “fixed,” “working,” “playable,” or “certified” **only when the required real acceptance behavior passes**. Otherwise say “partial” or “blocked” with exact evidence. Do not inflate source-match or gameplay metrics.
6. **Prioritize the highest-value next action.** When blocked, make one concrete, useful code deliverable if possible, state the exact impediment and necessary next decision, and stop. No busywork, no routine micro-commits, no repetitive status theater, and no requests for new user playthroughs when existing inputs suffice.
7. **Brief completion reporting.** Report what actually changed, the end-to-end result, what remains broken, and the next causal fix. Separate user-performed tests from internal/CI tests. Do not promise work that has not run.

**Non-negotiable principle:** **Fix the real problem. Prove the fix. Move the project forward. Stop the test rabbit hole.** The user must explicitly authorize an extended exploratory investigation beyond the limits above; such authorization never permits weakening mandatory safety, authenticity, or regression checks.

---

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
