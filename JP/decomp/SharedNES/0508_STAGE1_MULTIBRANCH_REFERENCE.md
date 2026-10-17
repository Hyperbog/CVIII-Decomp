# 0508 — Original-JP Stage 1 multi-branch reference experiment

**Real Mesen2 v2.1.1 (independent upstream source), authenticated original JP VRC6 ROM.** Reproducible inputs: [private replay script](../tools/run_mesen_stage1_branches_0508.sh). Machine-readable [hash/count report](../analysis/0508_MESEN_STAGE1_MULTIBRANCH_SUMMARY.json). No commercial ROM, screenshot, savestate, CDL or full instruction stream is committed.

## Experimental structure (do not add fork frame counts as a contiguous playthrough)

Original introduction/name-entry/prayer/Stage 1 route: **520+220+360=1,100 consecutively resumed frames**. Four independent **1,200-frame** forks from its Stage 1 snapshot: idle, right held, right with ten A jump pulses, right with twelve B whip pulses. Three further independent **1,200-frame** forks from the right+jump snapshot: continued right with jump pulses, right with alternating whip/jump, right+A held. This makes **10 reference jobs and 9,500 total simulated frame executions**, of which only the first **1,100** belong to the shared nondivergent start. The right+jump route reached **playable BLK 1-02** in the actual screenshot, manually inspected. No scene-recognition model or native game frame parity is inferred.

## Physical PRG cumulative observations

| Independent reference observations | Previous 1,100 frames | 10-run union | Difference |
|---|---:|---:|---:|
| Executed code/operand CODE bit positions | 12,885 | **16,772** | **+3,887** |
| Data DATA bit positions | 7,890 | **11,765** | **+3,875** |
| Previously certified 0501 code bytes re-observed | 463 | **1,157** | +694 observed, **zero new strict credit** |

Physical PRG coverage includes bank00 and raw PRG pairs 0B, 0E, plus fixed PRG31: **bank23 +719** new observed code bytes; **PRG31 +816**; **PRG28 +630**; **PRG22 +424**; **PRG20 +312**. Physical bank sums, private file/CDL/report hashes and 10-branch original RAM state samples are in the machine-readable report.

Specific original game-state observations: First-level RAM `$18=$04` remains the normal Stage 1 gameplay state during most forks; `$19` visibly reaches `$03` in the deeper right+jump continuations and `$68` cycles through values `$00-$09`. Earlier synthetic "stuck at 04" interpretations were a **harness-liveness limitation**, not evidence that the real game cannot progress. The room-loader selector `$18=$0C/$0D` still was **not** observed; it remains separately OPEN.

## Cross-edition structural acceleration

Run the [16-byte exact US matcher](../tools/audit_mesen_stage1_crossedition_0508.py) against legally provided JP and US ROMs using only independent Japanese physical CODE flags. Of **263** at-least-16-byte contiguous CODE-marked runs (15,382 CODE positions), **3,165** source positions occur in unique exact 16-byte US windows, and **350** have ambiguous-only exact matches. Eleven of twelve complete run-byte matches are unique in the US PRG. The code-mask SHA-256 is `3b4b3437016c1bde90b7f87c93d49fc29f3a89fc2566c248919a41197cb0137c`; the unique exact-match mask SHA-256 is `290defc9ef88b905a7360d62b2244259e8477cbb945235e3defcac6b0161c875`.

**These remain discovery candidates**: no US MMC5 bank-context, control-flow equivalence, register state or full instruction alignment is implied. No candidate count here increases strict verified Japanese PRG bytes or VPP.

## New narrow strict result

The same independently executed original traces now support **100 actual fixed PRG31 code bytes**, but only after the separate ROM/hash/decoder/gap-and-callee proof in [the independent 0508 certification note](../analysis/0508_MESEN_FIXED_LIVE_PROOF.md). All other observed code remains noncredited until equivalent evidence and exact previous-ledger overlap accounting exist.

Re-run no-ROM parser/lineage tests: `python3 JP/decomp/tests/test_mesen_stage1_branch_0508.py`. Future passes should improve Stage 1-02 level route/input variants and original-vs-native trace parity, not infer game completeness from code-data volume.
