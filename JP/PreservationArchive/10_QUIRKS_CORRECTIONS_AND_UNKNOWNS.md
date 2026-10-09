# 10 — Original Quirks, Dormant Paths, Residual Data, Corrections and UNKNOWNs

**Status:** ACTIVE register. Inspired by the **Q/D/L/C/U** separation in RLOFT; only JP-grounded facts belong in the original-game quirk categories.

| Class | Meaning | Documentation action |
|---|---|---|
| Q | Demonstrated unusual shipped-original behavior | preserve, regression-test, optional fix only behind a mod flag |
| D | Encoded executable/handler capability with no proved live producer | keep candidate, do not invent activation |
| L | Residual, shared-format, aliased or unused original data | retain raw bytes/boundaries |
| C | Correction of *our* modern reconstruction, audit or prose | record prior error and remedy; never call it an original game bug |
| U | Unresolved original producer, intent, timing or historical fact | bounded UNKNOWN with a concrete proof target |

## Active records

**Q-001 — Inline tail dispatch uses stack return address as data** (B): fixed $E7FB pops original JSR return bytes and JMPs through $0002 to an inline target. This is deliberate, not invalid stack code. Correct final flag effects in the native address lift, including preserved incoming Y. [Dispatcher proof](../analysis/NMI_FIXED_E7FB_DISPATCH.md).

**Q-002 — Sprite attributes persist across compressed descriptors** (B): compressed sprite records can consume inherited ZP $10 instead of a freshly initialized attribute. Native renderers must not zero it at entry. [OAM state](../analysis/ZP10_OAM_STATE.md). Exact prior collision/frame writer still unresolved U-003.

**L-001 — Action-table region aliases script pointers** (A): mechanical action $9E table word at $BEA3 is simultaneously script-pointer data and resolves to fallback record $BF79. It is not a proof of a live handler. [Action atlas](../analysis/RAW0B_ACTION_DISPATCH_ATLAS.md).

**D-001 — Structural but unproved script IDs $24/$25/$26** (E/A): record actions $5D/$5F/$89 mechanically select handlers and some fixed $FC17 sites. No live producer yet, and four tempting immediate constants were not direct script-ID stores. [0507](../analysis/NMI_BANK0A_ROOM_DISPATCH_0507.md).

**U-001 — NMI selector $18**: 16 encoded first-level pointer words do not by themselves bound or activate selector $0D. [Fixed E7FB](../analysis/NMI_FIXED_E7FB_DISPATCH.md).

**U-002 — Room-state $19 / secondary $68 across frames**: fixed $E526 bank mapping is proved; 12 pointers and state1→state2 local protocol do not prove uninterrupted values or carry prechecks. [0507](../analysis/NMI_BANK0A_ROOM_DISPATCH_0507.md).

**U-003 — Renderer-entry ZP $10 last writer**: seven bank-$0B collision writes and five fixed FC1F writes are identified; whole-program timing and last qualifying writer unknown. [Collision](../analysis/NMI_BANK0B_COLLISION_ZP10_0502.md), [fixed probe](../analysis/RAW0B_AI_SCRIPT_SEED_0504.md).

**U-004 — $FD62,Y indexed source**: Y comes from two coordinate-derived paths; no complete live bound on $54/$14. Potential source range FD62–FE61 includes code bytes and must be read through a mapped bus. [0505](../analysis/FIXED_TILE_PROBE_0505.md).

**U-005 — Original hardware/audio trace parity**: native mapper IRQ and standalone algorithms tested, but complete CPU/PPU/frame/audio traces and historical original-device tolerances not certified. [08](08_NATIVE_RECOMP_AND_PARITY_CONTRACTS.md).

**C-001 — Former 0500 byte count corrected from 933 to 982**: previous bookkeeping omitted $F800-$F830 inherited fallthrough. This was a *decomp accounting repair*, **not a ROM defect**. [Continuity](../docs/DECOMPILATION_CONTINUITY.md).

**C-002 — Alternative $FE95 pointer-table boundary clarified**: source arithmetic permits selector 3, but the encoded table only has three pointer words before $FE9E executable bytes. Do not retroactively treat $FE9E-$FE9F as a fourth word. This is a reconstruction boundary caution, not proof of a shipped bug. [0501](../analysis/NMI_FIXED_SCHEDULER_BANKED_0501.md).

## Future handling

For every new record add reproducible ROM address, evidence grade, whether actual gameplay reachability is proved, a minimal regression, and whether a correction affected already counted bytes. Do not infer an original-game quirk from a test failure in newly written C++ alone.

**U-002 supplementary 0508 evidence (not closure):** the [Phase 6 IRQ write-set audit](../analysis/0508_PHASE6_FINDINGS.md) excludes the admitted 45-state IRQ graph as a modifier of $18/$19/$68, $07A0/$07A6 or $08/$09. It does not eliminate NMI and non-IRQ game-state writers, nor prove live room dispatch. Phase 4's bank-$01:$BB57 conditional $07A0>04 values remain an unresolved producer-domain counterexample, not a verified out-of-range room load.
