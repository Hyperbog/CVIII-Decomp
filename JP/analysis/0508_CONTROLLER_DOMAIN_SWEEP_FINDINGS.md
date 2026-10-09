# Checkpoint 0508: Bulk artificial-input selector-domain sweep (completed probes)

**Status: PROVISIONAL original Japanese-ROM instruction execution under declared artificial PPU/NMI/controller conditions; NOT live gameplay, not full-cycle reference parity, not checkpoint 0508 completion.** Authoritative ROM SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`. Mapper24 VRC6a. Strict new ROM bytes **0**; prior cumulative **49,404/262,144 (18.8461%)**, VPP **24/100**, fixed PRG31 frontier `$FB96`, last completed checkpoint **0507**.

## Distinct executed batch scopes

This phase extends [the 900-NMI synthetic Start-input regression](0508_CONTROLLER_START_NMI_FINDINGS.md) with an **independent 16-pattern 300-NMI census** and **one longer 1200-NMI successful trace**. Both completed and produced deterministic JSON, runnable Python source and original-instruction counts. The additional attempted combined three-schedule 1200-NMI regression timed out and is **not** listed among passing results or used to prove spacing invariance.

### A. 16 button patterns × 300 artificially triggered NMIs

`JP/tools/probe_controller_patterns_0508.py` executes original RESET and 300 manual NMIs per pattern, with PPU status `$80` during reset, `$00` afterward, controller input provided before each NMI and **zero** main-loop instructions between injections. It runs ROM instructions, not a table-only interpretation.

Patterns: no buttons, A, B, Select, Start, Up, Down, Left, Right held continuously; held A+Start, held Select+Start; a Start press only on NMI1; a Start press only on NMI20; Start pulses every 30 NMIs; Start then A; alternating A/B/Start input cadence.

Measured **16 scenarios, 4,800 injected NMIs, 15,019,406 original ROM CPU instruction steps**. Observed first-level selector `$18` across all patterns was **`{00,02,0A}`**. Only **Start pulse every 30** and **A/B/Start cadence** explored beyond `$18=00` to `$18=02` and `$0A` during these 300 injections. A single Start press at NMI20 led through `$19=01,02,03,04` then back to `$19=00`. Held Start from NMI1 did **not** produce the same transition: state one had not yet become active when the initial button edge occurred. This is a bounded synthetic finding, not a proof of original game controller timing.

### B. Extended successful Start-pulse trace: 1,200 artificial NMIs

`JP/tools/probe_long_start_0508.py` supplies a one-injection Start press when `(manual_NMI % 30)==1`, with `$2002=$00` during NMIs, no scheduled IRQ and no idle-loop instructions between injections. Result: **2,966,527 original instructions** (including reset) and **1,200 NMIs**, no unsupported instruction failure; 17 state/room-input transition records.

Selected first-level transitions:

| Artificial NMI | RAM `$18` | RAM `$19` | Bounded interpretation |
|---:|---:|---:|---|
| 1 | `$00` | `$01` | Initial title path |
| 31 | `$00` | `$02` | Synthetic Start presses trigger progress |
| 61 | `$00` | `$05` | Pre-transition state |
| 189 | `$02` | `$00` | First-level selector changes |
| 190 | `$0A` | `$00` | Higher selector state, not the room `$0C/$0D` |
| 362 | `$09` | `$00` | Different first-level handler |
| 391 | `$03` | `$02` | Transition to another handler |
| 392 | `$04` | `$00` | State remains `$04` through artificial NMI1200 |

Observed first-level domain for the extended run **`{00,02,03,04,09,0A}`**. Neither `$18=$0C` nor `$18=$0D` occurred in this finite test; absence does **not** establish nonreachability in real hardware/playthroughs. The globally valid `$07A0/$07A6` room-index producer bounds remain unproved, and the room-loader carry gate is not newly certified.

## Combined completed exploratory evidence

The **two completed independent batches** sum to **6,000 injected NMIs** and **17,985,933 original instruction steps**. This number does not include prior 450-NMI zero-input or 900-NMI Start-input tests, nor overlapping reruns; step counts are not unique PRG-byte counts. Code execution depends on fake timing/PPU input and a simplified controller bus; no reference-emulator comparison or real 2A03 NMI/IRQ scheduling was made. Larger runs are discovery accelerators and state-producer witnesses under their exact assumptions only.

## Follow-up / acceptance criteria

- Upgrade to reference emulator or cycle-timed PPU/IRQ/input scheduling; capture an actual consistent controller trace and CPU/RAM/mapper state through the transitions.
- Study actual fixed NMI first-level states `$02`, `$0A`, `$09`, `$03`, `$04` from the observed conditional path, then identify route to `$0C/$0D` without constructing that route artificially.
- Reconcile live script/room/stage pointer domains, including bank `$0A/$0E` data, with existing byte ledger only after original-state provenance is proved.
- Preservation/archive records remain research, not a static or native parity completion claim; tasks R-001, R-002 and R-006 remain open.

Reproduction uses the exact ROM file and the committed controller-enabled `JP/tools/trace_6502_vrc6_0508.py`:

```sh
python3 JP/tools/probe_controller_patterns_0508.py 'Akumajou Densetsu (Japan).nes'
python3 JP/tools/probe_long_start_0508.py 'Akumajou Densetsu (Japan).nes'
```

Both scripts print summaries and write their deterministic reports into `/mnt/data` in this research environment. For portable repository execution, their output destination should be parameterized in follow-up; this does not affect the original instruction semantics. Generated reports are included in Git. Do not commit the ROM.
