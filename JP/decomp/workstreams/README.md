# Japanese Castlevania III — two independent workstreams

This repository contains **an already playable, owner-tested Japanese NESRecomp C11 native game** and **a separate, partially completed original-ROM semantic decompilation**. They have different goals, acceptance tests, and metrics.

| Workstream | Primary output | Authoritative status | Meaning of progress |
| --- | --- | --- | --- |
| [Native recompilation and Enhanced Edition](../../recomp/workstreams/native-recompilation/README.md) | Owner-built Windows game, launcher, saves, debug stage/partner tools, optional presentation enhancements | [Product state](../../recomp/workstreams/native-recompilation/PRODUCT_STATE.json); [Enhanced status](../../recomp/docs/ENHANCED_CURRENT_STATUS.md) | The game runs and its player-facing features work under owner and CI testing |
| [Semantic decompilation / verified source recovery](semantic-decompilation/README.md) | Source-accurate 6502 code/data interpretation, native C11/C++ subsystem lifts, original/reference replay and certification | [Evidence state](semantic-decompilation/EVIDENCE_STATE.json); [original checkpoint](../analysis/RESUME_STATE.json); [VPP score](../analysis/PROGRESS_SCORE.csv) | Independently certified semantic coverage and a fixed rubric; **not** how playable the game is |

**The native recompilation does not require 100% semantic decompilation to run the original game.** Conversely, compiling a source-parity helper into the game target does not make it an active gameplay replacement.

[Machine-readable per-file ownership](WORKSTREAMS.json) identifies representative product, research and shared files, including the mixed legacy `JP/decomp/analysis` and `JP/recomp/native/enhanced` directories. It does not pretend every historical file has already moved.

## Existing paths deliberately preserved

- Product runtime and packaging: `JP/decomp/tools/`, active host parts of `JP/decomp/tools/`, and `JP/decomp/tools/`.
- Source research: [new JP/decomp/](../), including the four 0525/0526 hand-assembled 6502 fragments in `JP/decomp/asm/` and historical 0509/0510 native experiments in `JP/decomp/legacy/`, plus current research files in `JP/decomp/tools/`, `JP/decomp/tools/`, `JP/decomp/tools/`, and research parts of `JP/decomp/tools/` and `JP/decomp/tools/`.
- The old `JP/recomp/` assembly naming collision is resolved: [JP/recomp/](../../recomp/) is now reserved for the **existing playable product**; current build code still lives at stable `JP/decomp/tools/` and `JP/decomp/tools/` paths.
- Common archive, original ROM identity and rules remain at their historical paths.

These paths have extensive CMake, workflow, source-script, report, and Markdown dependencies. This first separation is **non-destructive**: it creates two canonical workstream status areas and a checked index instead of blindly moving source assets and breaking builds. A later physical move requires a specific dependency graph, mechanical reference rewrite, and clean Windows/Linux/source-regression gates.

Run `python3 JP/decomp/tools/audit_workstreams.py` (or `python3 JP/decomp/tools/test_workstreams.py`) to validate that product QA is not represented as VPP, the semantic counters still reconcile, and all tracked source paths exist.
