# 0518 — Source coverage reconciliation and formal VPP scoring decision

**Certified result:** VPP advances **26 → 27/100** from an additional original-gameplay movement/collision architecture point. Gameplay advances **2 → 3/25**; movement/physics/collision **1 → 2/4**. No changes to other category weights or earned values. **Strict PRG remains 49,504/262,144 (18.8843%), last completed semantic checkpoint 0508, fixed frontier FB96.**

## Original physical ROM source-byte accounting

The [25-window manifest](0518_NATIVE_COVERAGE_WINDOWS.json) spans **1,365 deduplicated physical PRG bytes**, authenticated against original JP ROM SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`. The [reproducer](../tools/audit_native_coverage_0518.py) compares physical-byte positions with **only** the [0501 certified manifest](../SharedNES/JP_0501_CERTIFIED_REGIONS.json) (31 original source regions, 4,364 certified bytes) and 0508's four independently certified fixed-bank additions (100 bytes).

| Classification | Distinct source bytes | Credit |
|---|---:|---|
| Tracked native provenance, 0510–0517 | 1,365 | Inventory, not new certification |
| Already in 0501 certified manifest | 546 | 0 new |
| Already in 0508 additions, not 0501 | 78 | 0 new |
| Outside **these two** manifests | **741** | **Not globally proven novel** |
| Newly promoted strict PRG | **0** | Requires complete prior ledger reconciliation |

The missing historical 0502–0507 admitted regions and all other strict manifests must be deduplicated before claiming any of the 741. The 0501 file is **not** the entirety of the 49,504-byte cumulative certificate. The 0510 native `$FF06–$FF55` tracking window contains 80 physical bytes, but 0508 certified **only** `$FF06–$FF11` (12) and `$FF14–$FF55` (66): `$FF12–$FF13` (original `A9 01`) are not claimed. Likewise, original 0516 radius/offset data absent from the 0501 reference cannot be assumed globally new.

The source-audit CLI is ROM-free for public CI (`python3 JP/tools/audit_native_coverage_0518.py`). With the user's original private JP ROM, `python3 JP/tools/audit_native_coverage_0518.py --rom /path/to/JP.nes` checks every one of 25 source-window hashes, 31 old certified-region hashes and four 0508 hashes. It also checks the VPP CSV/resume-state score and refuses overlapping local windows. No proprietary bytes are committed.

## Newly earned fixed-rubric gameplay milestone

Gameplay's earlier first movement/physics/collision point was for the **isolated** source-backed collision scratch/distance architecture and native exact 8-bit math, as recorded in [0502](NMI_BANK0B_COLLISION_ZP10_0502.md). That earlier point stays untouched.

The independently different **second** movement/physics/collision point is for a **connected reusable native actor processing subsystem**, not for another count of an isolated helper: 0514 actor admission `$B1F8`, 0515 collision gate `$B217`, 0516 original `$B339/$80B3/$80C1` distance with indexed game radius tables, and 0517 carry-dependent collision-result plus empty follower scan `$B235/$B29D–$B31F`, returning to the fixed scheduler at `$FDFE`. Original Stage 1 Mesen naturally executes **91 original 6502 instructions** from `$B1F8` through `$FDFE` for one type-$3D actor. [The structured C++ composition](../src/actor_collision_result_0517.cpp), [independent original-ROM replay](../tools/audit_actor_collision_tail_0517.py), and [machine results](0517_actor_collision_tail_report.json) agree on **1,792/1,792 non-stack RAM bytes** and A/X/Y/P at the end. This represents a reusable connected gameplay structure and meets the rubric's partial architectural-credit rule.

**Limits:** The two natural 0517 replay windows overlap the *same* actor event, not independent actors. The naturally reached collision branch is no contact; positive-contact results and additional branch boundaries `$B243/$B27C/$B2A8` are only synthetically exercised or unimplemented. The code does not run a full original actor scheduler frame, input/controller, original native PPU/CHR, APU/VRC6 or complete collision/physics across the game. No points are added for player control, AI, combat, native-runtime integrated-frame, stage/world, rendering or validation/trace beyond what was already earned. Further movement/collision points remain open.

## Recovery

Continue original fixed `$FDFE→$FE00` actor update and bounded `$B243/$B27C/$B2A8` helpers, and separately build the **complete** 0500–0508 certified physical PRG interval union. A VPP evidence award is independent of PRG byte accounting. This 0518 review changes **neither** the certified last-completed semantic checkpoint **0508** nor its physical frontier **FB96**.
