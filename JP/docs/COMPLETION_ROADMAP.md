# CVIII Japanese ROM — subsystem progress and completion roadmap

**Status: ACTIVE PLAN, NOT A COMPLETION CERTIFICATE.** Originally baselined 2026-10-09 after provisional 0508 Phase 11; score updated after the first green native CI gate on 2026-10-09. Authoritative score: [PROGRESS_SCORE.csv](../analysis/PROGRESS_SCORE.csv) and [PROGRESS_METRIC.md](PROGRESS_METRIC.md). Byte ledger/recovery source: [RESUME_STATE.json](../analysis/RESUME_STATE.json).

## Audited progress

| VPP subsystem | Earned / possible | Subsystem % | Main remaining obligation |
|---|---:|---:|---|
| ROM foundation/cartridge | 4/5 | 80.0% | Complete mapper-register usage inventory |
| CPU/mapper/interrupts | 8/10 | 80.0% | NMI transitive closure and reference CPU/interrupt traces |
| Rendering/PPU | 5/10 | 50.0% | Background, CHR, frame goldens and integrated rendering |
| Gameplay/objects/physics | 2/25 | 8.0% | Player, combat, common AI and bosses |
| Stage/world/progression | 0/20 | 0.0% | Room formats, transitions, maps, routes, menus, endings |
| Audio | 1/12 | 8.3% | Driver/data, native APU+VRC6, sound events and parity |
| Native runtime/platform | 1/10 | 10.0% | Integrated bus, CPU, PPU, input, sound and playable build |
| Validation/tooling | 5/8 | 62.5% | Independent 8,991-state NROM CPU golden test and CI earned; JP VRC6/IRQ trace and frame goldens remain |
| **Weighted overall verified parity** | **26/100** | **26.0%** | **74 fixed-rubric points not yet earned** |

VPP is a fixed milestone/evidence rubric, **not** an estimate of labor or a calendar forecast. The unweighted average of category percentages is not the overall score. Different metric: **49,504 / 262,144 = 18.8843%** strictly verified PRG; **212,740** bytes uncredited. Whole-PRG mechanical indexing is 100%; JP/US exact-or-normalized structural candidates are 149,607/262,144 (57.0705%), **not semantic coverage**.

### Subsystem detail within incomplete major areas

- Gameplay 2/25: object dispatcher **1/5 (20%)**, player state **0/4**, movement/physics/collision **1/4 (25%)**, combat **0/4**, common enemy AI **0/4**, bosses **0/4**.
- World 0/20: room formats **0/5**, scrolling/transitions **0/4**, environmental/collision maps **0/4**, route progression **0/3**, menus/password/ending **0/2**, deterministic stage extraction **0/2**.
- Audio 1/12: NSF/ROM correlation **1/1**, driver **0/3**, data formats **0/2**, native APU+VRC6 **0/3**, event mapping **0/2**, register/output parity **0/1**.
- Native 1/10: isolated native OAM component **1/1**; CPU core **0/3**, memory/mapper/PPU integration **0/2**, frame/input **0/1**, audio backend **0/1**, playable executable **0/1**, package **0/1**.

## Stalled checkpoint 0508 — diagnosis

Research Phases 1–11 are committed and preserve real, reproducible JP-ROM evidence: conditional NMI selection, room-index initialization, bounded room streams, IRQ bank preservation, PPU zero stream, and natural sound command $6B return. **However, these phases earned 0 strict PRG bytes and 0 VPP points.** The live starting selector and inter-frame RAM producer domains still are not proved, while several fixed-bank dependencies were already counted. Eleven narrow research slices without advancing any key metric signal a workflow bottleneck; another series of isolated handlers is not an adequate response.

## Throughput/commit policy effective immediately

1. **Switch from single-routine slices to whole subsystem and bank batches.** Each primary batch should cover at least one connected **16 KiB raw PRG bank / two physical 8 KiB banks** in discovery, and multiple related banks (32–64 KiB) when justified. Reuse the [whole-PRG atlas](WHOLE_PRG_ATLAS.md), cross-version matchers and earlier ROM-audited graphs rather than repeating them.
2. **Target 8–16 KiB genuinely new semantic PRG bytes per evidence-supported checkpoint**, but never impose a fictitious byte quota. Candidate/discovery bytes must be reported separately; promoted bytes require byte-complete instructions/data, mapper-state proof, input-producer domain proof and overlap subtraction. A real zero-byte outcome is preferable to false credit.
3. **Put execution provenance before more local closure.** Immediate shared blocker: reset/frame-derived selectors $18/$19/$68, indices $07A0/$07A6, state-two $B597/$B6A4 carry and room-loader bank context. Build original-state CPU/mapper trace evidence to close these edges in bulk.
4. **Commit every substantial batch directly to the decompilation Git branch** with audit, deterministic report, proven addresses/byte manifest, limitations, native tests and archive updates. Commit provisional evidence too, explicitly labeled. Verify remote HEAD and exact blobs before calling it preserved.
5. **Record at every batch:** total physical PRG bytes explored, candidate-only bytes, strict unique new bytes/PRG %, category VPP delta, newly proved producers/closed R-IDs, regression/trace sample counts, Git commit and next blocker.
6. **Automatic priority pivot:** two consecutive substantive batches with zero promoted bytes and zero VPP mean stop drilling one callee at a time and prioritize a new producer/trace/runtime capability. The already completed eleven zero-credit slices trigger that pivot now.
7. For a finished semantic checkpoint, reconcile preservation/archive/progress, re-run the predecessor audit and physical overlap, then update machine [RESUME_STATE.json](../analysis/RESUME_STATE.json) **LAST**. Provisional research commits do not rewrite the last completed recovery checkpoint.

## Completion roadmap with objective exit criteria

Milestones represent dependency/acceptance order, **not calendar promises**; independent bank research may run in parallel.

| Order | Bulk delivery | Planned sweep and acceptance gate | VPP area enabled |
|---|---|---|---|
| **M1: Trace and liveness** | Reset-to-NMI and several-frame 2A03/VRC6 mapped execution; whole-PRG producer xrefs | Replayable reference register/stack/RAM/mapper traces establish or refute actual $18=$0C/$19=$13 initialization and inter-frame $07A0/$07A6/$68 producers | CPU/mapper; validation |
| **M2: Room-loader closure** | Entire raw bank $0A (16 KiB), raw $0E source streams, fixed $FB96; state-two $B597/$B689/$B6A4 and $B873/$B7F7/$B7DE | Prove carry gate, live room-index bound and bank restoration; exact unique code/data byte manifests and native loader parity | CPU NMI; stage/rooms |
| **M3: Stage/world database** | Bulk multi-bank room/stage/tile/collision and route tables; stage map extraction | Proven pointer domains; reproducible stage-resource extractor; reference transition/scroll/route checks; account for menus/endings | Stage/world (20 available) |
| **M4: Gameplay and actors** | Bulk raw bank $0B AI/action/script producers plus player/movement/weapon/enemy/boss bank families | Live script/action producer closure; complete player and object-state traces, collision, weapon, boss and AI golden tests | Gameplay (23 available) |
| **M5: Rendering and PPU** | Sprite/OAM, ZP $10 producer ordering, CHR, backgrounds and raster/scroll behavior | Reproducible 256-byte OAM and image/frame goldens across typical and edge scenes | Rendering (5 available) |
| **M6: Sound and output** | Banked song/SFX records, full audio scheduler, APU and VRC6 native mixer | Golden game-event/register traces and representative audio PCM matches; preserve parser loop semantics | Audio (11 available) |
| **M7: Executable/runtime** | Integrated CPU/static-recomp path, memory, mapper, PPU, deterministic input/frame loop and sound | Playable native build across stages/routes, portable packaging and CI regressions | Native runtime (9 available) |
| **M8: End-to-end parity** | Multi-route reference input scripts, NMI/IRQ/DMA edge cases, audiovisual frame tests and certification scope | ROM-grounded documented full-feature parity with unresolved issues explicitly bounded; all score criteria earned before 100% | Remaining validation and subsystem items |

### Immediate next work: M1 + M2 as ONE large discovery/verification batch

Reuse committed [Phase 11](../analysis/0508_PHASE11_FINDINGS.md) and predecessor audits as modules. Sweep **complete raw bank $0A plus raw bank $0E room source dependencies**; derive a reset/frame selector witness or explicitly document its missing predicate; execute state-two and loader gates with mapper/IRQ interactions; classify complete affected code/data spans. Commit a consolidated multi-bank manifest, audit, report and relevant native tests; then reconcile the strict ledger against the already-counted bytes. Do not create a twelfth one-function micro-phase as a substitute for this batch.

**Completion definition:** Overall 100 VPP requires all fixed criteria with committed evidence, integrated playable native game and actual reference frame/audio/CPU traces; it cannot be inferred from ROM scanning, decompilation labels, partial 6502 tests, US structural matches or narrative archive volume. Authentic original developer source recovery is a separate evidence-dependent historical task.


**Progress change (2026-10-09):** First green [native regression CI](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/37993214808) earned the fixed validation CI milestone: validation 3/8→4/8, weighted total 24→25/100. Game world remains 0/20 and strict PRG coverage remains 49,404 bytes. The preceding Phase 1–11 zero-credit stall diagnosis is historical and remains valid.


**Progress change (2026-10-09):** [Nintendulator CPU golden trace](https://github.com/Hyperbog/CVIII-Decomp/actions/runs/38010689051) passes all 8,991 NROM instruction register/status/stack/cycle states. One of two validation trace-harness points earned, validation 4/8→5/8, weighted VPP 25→26. Original Japanese VRC6/gameplay parity and strict PRG byte promotion remain open; last semantic checkpoint 0507 unchanged.


**0508 strict-progress correction (2026-10-10):** Independent original-Mesen Stage 1-02 gameplay evidence and instruction-aligned fixed PRG31 source proof admitted **100 nonoverlapping bytes**, moving strict JP PRG to **49,504/262,144 (18.8843%)**. VPP remains **26/100**. This does not resolve the separate live NMI room-$0D producer domain or make the 16,772 Mesen-observed code bytes all certifiable. See [certificate](../analysis/0508_MESEN_FIXED_LIVE_PROOF.md) and [frame-branch census](../SharedNES/0508_STAGE1_MULTIBRANCH_REFERENCE.md).
