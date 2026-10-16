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


**U-001 / U-002, 0508 Phase 7 refinement (still OPEN):** With synthetic parent stack and incoming `$18=$0C,$19=$13`, ROM execution of raw `$0A:$B36B` sets `$18=$0D,$19=0`. A second independent NMI entry with no intervening writer then dispatches to `$B570`, as verified by 65,536 two-entry tests. This establishes a *conditional* original-ROM state transition, **not** live reset-to-NMI producer provenance; unresolved values beyond encoded table widths must not be clamped. [ROM-backed audit and caveats](../analysis/0508_PHASE7_FINDINGS.md).

**U-002 extension (0508 Phase 8, bounded evidence):** State-zero raw `$0A:$B570` calls fixed `$E7B6`, which clears `$07A0/$07A6/$0789/$68` in a synthetic-entry original-instruction execution; the caller restores saved `$0781` afterward. This closes **only the local initialization prefix**. The later fixed `$EB82` callee, actual reset-to-state-zero reachability, and subsequent producer/interrupt ordering remain UNKNOWN. [Phase 8 audit](../analysis/0508_PHASE8_FINDINGS.md). This is not a claimed shipped-game bug or a live value-domain clamp.

**U-002 extension (0508 Phase 9, still OPEN):** fixed `$EB82` interprets `$EC1D-$EC46` and, after 2,048 zero-value PPUDATA writes, returns through raw `$0A:$B589` to increment `$19` to one on the *conditional* state-zero branch. Local `$07A0/$07A6/$68` remain zero; global reachability and future writers are still unproved. [Phase 9 test and limits](../analysis/0508_PHASE9_FINDINGS.md). **No original-game quirk or code defect is asserted.** The PPUCTRL increment-32 test demonstrates repeated destination addresses, so do not equate port-write count with distinct cleared VRAM cells.

**U-006 — Sound-parser return and saved-bank scratch:** [Phase 10](../analysis/0508_PHASE10_FINDINGS.md) proves the conditional room-state-one command $6B executes raw-bank-$0C:$87AE sound reset, stopping at $8860 with $23=$0C and $25=$0A. It does **not** execute the remainder of $8850 or prove eventual RTS and preserved $25. A *synthetic* return alone proves the original fixed $E249 suffix would restore $0A and permit $19 to advance to 2. This is an open proof dependency, not a demonstrated original-game bug.


**U-002 / R-002 Phase 11 refinement — sound return no longer hypothetical:** [Phase 11](../analysis/0508_PHASE11_FINDINGS.md) executes all six bank-$05 first-byte instrument reads for command $6B and a real RTS through fixed E249 into room $19=2. This replaces **only** Phase 10's explicitly synthetic RTS assumption for the bounded state-one entry. Initial live seed, adjacent NMI ordering, and subsequent state-two carry gate remain UNKNOWN; no evidence of a shipped game bug or native audio parity.


**C-003 — Native/partial E7FB high-pointer read wrap corrected (0508 bulk)**: fixed `$E7FB` uses 8-bit `INY` twice when consuming an inline table word. For selectors `$7F/$FF`, the high read wraps to **Y=0** and fetches the JSR return-address byte, not `low-pointer-address+1`. At raw `$0A:$B4CE`, the actual conditional target is `$E7FB`; the old native address-only lift incorrectly returned `$20FB`. Corrected [C++ implementation](../src/room_state_dispatch.hpp), [65,536-case C++ test](../tests/room_state_dispatch_test.cpp), [original-instruction test and proof](../analysis/0508_TRACE_CORE_AND_E7FB_CORRECTION.md), and [Phase 2 erratum](../analysis/0508_PHASE2_FINDINGS.md). This is a **modern reconstruction correction**, not a proven live original-game glitch or extra PRG credit.


**U-002 supplement (JP0634):** The original raw01:$B87A → $B919 → $BAEF → $BB57 candidate route contains a real unsigned $30 clamp to $11 before the nine-cell table read. This is conditional source proof, **not** a universal observed selector domain or crossbank raw0A room-loader predecessor. Alternative entries, NMI/IRQ writes and runtime reachability remain unknown. [Source audit](../analysis/0634_RAW01_SELECTOR_PARENT_CFG.md). Do not classify the earlier conditional $35→$FF63 pointer as an observed gameplay bug.
