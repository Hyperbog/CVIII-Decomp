# CVIII JP checkpoint 0508 — large-window foundation (provisional)

**Target:** `Akumajou Densetsu (Japan).nes`, SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.

**Status:** provisional and **not committed** to `Hyperbog/CVIII-Decomp`. Verified recovery ledger stays at 49,404 / 262,144 bytes (18.8461%), VPP 24/100. This document does not supersede `JP/analysis/RESUME_STATE.json` (last completed checkpoint 0507).

## Bounded workload and results

- All **16,384 bytes** of physical PRG20–21 (VRC6 raw bank `$0A`, mapped CPU `$8000–$BFFF`) were examined as potential 6502 opcode starts. **12,074** were syntactically valid official-instruction starts and **1,740** were candidate control-flow starts. These figures intentionally include false positives from data bytes.
- Both NMI fixed entry selectors were checked byte-for-byte: `$18=$0C` maps fixed `$E51E → raw-$0A:$AFA4`; `$18=$0D` maps `$E526 → raw-$0A:$B4CC`. The first-level NMI table is at fixed `$E363`.
- Reproduced checkpoint 0507's conditional raw-$0A graph of **281 instructions / 582 operand-and-opcode bytes** and its exact range fingerprint.
- The expanded conditional CFG seeded with the two fixed mapped entries and their four nested `$E7FB` inline tables contains **935 candidate instruction starts / 2,042 candidate instruction bytes**, **14 disjoint code spans**, **four inline pointer tables / 65 pointer words**. Every decoded instruction is official, none overlaps another opcode/operand, and inline pointer literals are excluded from code. Relative to the earlier 0507 graph, **1,460 additional candidate instruction bytes** are classified. **None** are promoted merely by structural decoding.

## New bounded semantic mechanisms

1. `$AFA4: LDA $19; JSR $E7FB` is **five bytes** with proven physical mapping from fixed `$E51E`, exactly paralleling the already accounted `$B4CC` entry. This is an identified **potential five-byte strict addition**, not yet admitted to the machine ledger.
2. The `$AFA9` table contains 20 encoded words. Entry `$13` points to `$B36B`, which writes `$18=$0D` and `$19=$00`. This is an **if-selected state transition**, not evidence that index `$13` actually runs.
3. The `$B11F` nested selector reads `$0783` and dispatches using a separate 22-word inline table at `$B125`. `$B11B–$B11E` supplies four local values (`00 03 10 13`), but `$0782` and subsequent `$0783` state changes require independent bounds.
4. `$B873` reads three-byte records through `Y = (3 * RAM[$07A6]) & $FF`, checks the first record byte for `$FF`, and returns carry set on the sentinel. The nine records at `$B8A6–$B8C0` are followed by `$FF` at `$B8C1`. This does **not** globally restrict `$07A6` to 0–9 or justify `$B8C2` pointer-table bounds.

## Blockers before strict promotions

- First-level `$18=$0C` live entry and predecessor `$19=$13` reachability are not established. Neither the 20-, 22-, 12-, nor 11-pointer table width proves a selector bound.
- All cross-frame writes to `$18/$19/$68/$0782/$0783/$07A0/$07A6` and callee effects need closure.
- `$B7F7` calls fixed `$FB96` eleven times; a bank switch temporarily reads bank `$0E` then restores `$0A`, and indexed `$B8C2` pointer provenance remains open.
- Full `JP/tools/check_resume_frontier.py` and the prior native regression must be replayed from the complete repository before any committed 0508 handoff. The independent 0507 graph and ROM-hash checks **have** passed in this foundation audit.

**Reproduce:** Place `audit_0508_expanded.py` in repository `JP/tools/`, alongside the existing `audit_nmi_fixed_scheduler_banked.py`, and run:

```sh
python3 JP/tools/audit_0508_expanded.py '/path/to/Akumajou Densetsu (Japan).nes' 0508_expanded_report.json
```

Do **not** advance `RESUME_STATE.json`, strict-byte coverage, or VPP until the full evidence/archive/progress/audit transaction is complete. The 8–16 KiB **new strict bytes** target remains aspirational; the 16 KiB processed here is a discovery sweep, not 16 KiB of proven game behavior.