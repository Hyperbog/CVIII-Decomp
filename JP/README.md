# Japanese Castlevania III — native recompilation and semantic source recovery

This branch contains **two distinct deliverables** for Japanese *Akumajou Densetsu* (Mapper 24 / Konami VRC6a). The original, SHA-authenticated Japanese cartridge is never committed.

## Source folders, in migration

The canonical folder labels are now **[decomp/](decomp/)** (original
6502 source reconstruction) and **[recomp/](recomp/)** (existing playable
NESRecomp Enhanced product). JP0662 moved the old CPU/actor demos to
`decomp/legacy/`, and the old `JP/recomp` assembly snippets to
`decomp/asm/`. All historical source was preserved, build references
updated, and original game logic left untouched.

**JP0663 root-level physical migration is complete.** existing active
`JP/recomp/native`, `JP/decomp/tools`, `JP/decomp/analysis`, `JP/decomp/docs`,
`JP/decomp/src` and `JP/decomp/tests` still hold canonical build/research files.
Do not delete or bulk rename them; dependent scripts and CI must first
be rewritten and regression-tested. [Directory audit and staged
migration limits](decomp/README.md).

## Choose the correct workstream

| Goal | Start here | Status/metric |
| --- | --- | --- |
| **Run or improve the existing playable native game** | [Native recompilation / Enhanced Edition](recomp/workstreams/native-recompilation/README.md) | Owner-tested Windows C11/NESRecomp/SDL2 baseline, local ROM-authenticated build kit, save states, debugging stage/companion selection, optional sprite-flicker presentation |
| **Reconstruct original routines into independently readable source** | [Semantic decompilation](decomp/workstreams/semantic-decompilation/README.md) | Partial semantic VPP **31/100**, strict original-source PRG **49,504/262,144 (18.8843%)**; these metrics **do not measure playable-game completion** |

[Workstream overview and non-destructive migration policy](decomp/workstreams/README.md) · [Machine-readable ownership](decomp/workstreams/WORKSTREAMS.json) · [Boundary audit](decomp/tools/audit_workstreams.py)

### Native game — already running

The [product status](recomp/docs/ENHANCED_CURRENT_STATUS.md) and [Alpha build-and-play instructions](recomp/release/alpha/README_ALPHA.md) cover the existing owner-tested native recompilation. The source records owner gameplay through Stage 4-0A, including Sypha and character switching, and confirms the earlier graphics issue resolved. Native save states, F10 checkpoint/companion tools and the opt-in sprite compositor are implemented with specific owner QA limits documented in those pages.

**Do not reinterpret the semantic rubric's “native runtime” subscore as a statement that the NESRecomp game lacks a CPU, video, input, sound or executable.** That subscore belongs to the *separate independent source-recovery rubric*.

### Semantic research — partial by design

[Research progress rubric](decomp/docs/PROGRESS_METRIC.md), [historical decompilation log](decomp/docs/PROGRESS.md), [continuity and certified frontier](decomp/docs/DECOMPILATION_CONTINUITY.md), and [original-ROM evidence state](decomp/analysis/RESUME_STATE.json) measure source understanding, bounded C11/C++ lifts and independently certified PRG byte coverage. These proofs may be useful for future modding, but a dormant semantic helper is not automatically a live runtime feature.

### Shared rules

Active work remains on branch `decompilation`. [Original ROM identity](decomp/docs/ROM_IDENTITY.md), [universal mod-forward development policy](../MOD_FORWARD_METHODOLOGY.md) and [contributor rules](../AGENTS.md) apply to both. The Enhanced Edition is the sole public product direction; original gameplay must remain the default behavioral reference. No unimplemented mod/editor interface is implied by the existence of source research.

Legacy code and research files have not been moved to avoid breaking their CMake, test and historical-document references; newly written status and indices have separate workstream ownership with a ROM-free audit.
