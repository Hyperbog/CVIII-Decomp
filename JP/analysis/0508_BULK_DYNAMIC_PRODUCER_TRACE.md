# Checkpoint 0508 — bulk synthetic CPU physical-byte/producer manifest and controller fork

**Status: PROVISIONAL original Japanese-ROM instruction-level evidence. NOT a live reference-emulator/console trace, a verified global input-domain proof, or a completed strict-coverage checkpoint.**

JP ROM: 393,232 bytes, SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`; Mapper 24 / VRC6a. This is one multi-bank execution research batch, not a series of single-routine phase claims.

## Exact workload and ROM-fetched physical coverage

`JP/tools/audit_0508_dynamic_producer_manifest.py` executes entire official-opcode instructions of the original ROM with the previously tested 0508 mapped 2A03 bus/CPU. It indexes fetched opcodes **and all their operand bytes** by physical 8 KiB bank, plus all mapped PRG ROM reads and RAM producer sites. Three input scenarios under manually injected NMI and synthetic PPUSTATUS:

| Synthetic controller policy | NMIs | Original instruction executions | Distinct executed instruction/code operand bytes |
|---|---:|---:|---:|
| start30 | 1,200 | 2,966,527 | 10,771 |
| abstart | 300 | 647,426 | 5,305 |
| none | 300 | 1,055,395 | 3,793 |

**Aggregate:** 1,800 manually injected NMIs and 4,669,348 original instruction executions. **Physical union**: 11,127 bytes fetched as executed instruction/operands and 16,718 distinct PRG ROM bytes read for *any* purpose (includes code/operand fetches). Neither number is a strict PRG ledger increment; the union is not the sum of scenario counts.

### Full 1,200-NMI path: physical 8 KiB bank manifest

| Physical PRG 8K bank | Executed instruction/operand bytes | All ROM read bytes | Distinct instruction starts | Executions |
|---|---:|---:|---:|---:|
| `$00` | 992 | 1,368 | 491 | 95,459 |
| `$03` | 1,081 | 2,715 | 499 | 25,950 |
| `$04` | 70 | 70 | 39 | 64,908 |
| `$05` | 13 | 446 | 7 | 4,836 |
| `$08` | 1,032 | 1,080 | 479 | 8,494 |
| `$09` | 0 | 130 | 0 | 0 |
| `$0A` | 1,307 | 2,172 | 606 | 79,829 |
| `$0B` | 0 | 78 | 0 | 0 |
| `$0F` | 41 | 47 | 24 | 24 |
| `$10` | 0 | 584 | 0 | 0 |
| `$14` | 335 | 375 | 169 | 17,030 |
| `$15` | 0 | 13 | 0 | 0 |
| `$16` | 140 | 140 | 64 | 28,730 |
| `$17` | 138 | 160 | 67 | 25,162 |
| `$18` | 1,714 | 1,898 | 768 | 463,634 |
| `$19` | 0 | 735 | 0 | 0 |
| `$1A` | 316 | 351 | 164 | 1,138,238 |
| `$1B` | 114 | 217 | 62 | 62 |
| `$1C` | 429 | 434 | 212 | 54,653 |
| `$1D` | 45 | 46 | 22 | 9,680 |
| `$1E` | 750 | 768 | 390 | 26,206 |
| `$1F` | 2,254 | 2,360 | 1,047 | 923,632 |

**Physical-mask fingerprints:** union code/operand `07447cf32e73780cc5380d7f60249e46e7d2c1be40c29983f1d590e04242e3ff`; union all-PRG-read `ae41bf822c05d5d73c4dcd6f8f3a0f48ed5fd7483a0f1b3e16ad1e337e498094`. Both are SHA-256 of a 262,144-byte 0/1 membership mask, *not* lossless PRG source data. The report includes scenario-specific digests, bank rows and producer site counts.

## New ROM-executed RAM producer provenance (under exact synthetic conditions)

The trace records the source instruction PC and mapper-selected bank for *each actual RAM write*. First-level selector `$18` was written by fixed `$E02A` during RESET, fixed `$E551` (`INC $18`), fixed `$E558` (`STA $18`), and raw bank `$01:$A627` (`STA $18` or equivalent ROM-decoded write). All these addresses are dynamic instruction witnesses, not raw byte-pattern guesses. Observed values were `{00,02,03,04,09,0A}`. `$19` has additional per-state writer sites recorded in the report; its full global domain remains OPEN.

The 1,200-NMI path wrote `$07A0` at fixed `$E02A`, fixed `$E7CD`, raw bank `$01:$AA3E`; and `$07A6` at fixed `$E02A/$E7CD`. In these specific tests both index values stayed `$00` after the relevant writes. **Do not infer an upper bound from that fact:** the other raw bank `$01:$BB57` indexed producer and raw bank `$0A:$B7DE` increment can execute under different states. No state `$18=$0C/$0D` occurred.

### Synthetic first-level state sequence

In the 1,200-NMI periodic Start scenario, the notable transitions were: `NMI189: $18=02`, `NMI190: $18=0A`, `NMI362: $18=09`, `NMI391: $18=03`, `NMI392: $18=04`. `$2C` subsequently advances through `01,02,03` by NMI407. The ROM itself provides the state change through the fixed helper `$E551: INC $18; LDA #0; STA $19; RTS` and `$E558: STA $18; JMP $E553`. Exact producer sites for other paths are listed in the deterministic report.

## Controlled fork from the `$18=04` synthetic state

`JP/tools/audit_0508_state04_controller_branch.py` runs the same JP ROM through synthetic NMI392, checks `$18=04/$19=00/$07A0=00/$07A6=00`, then clones the complete RAM/CPU/mapper state (discarding only historic output-register logs). **19 independent controller policies** each execute **120 further manually triggered NMIs**, for **2,280 further NMIs** and **7,132,248 additional original-instruction executions**. Policies cover held A/B/Select/Start/directions, Start/A/direction pulses, and combination/alternating patterns.

All 19 runs completed without unsupported opcodes or stack failures; **no run entered first-level `$18=$0C/$0D`**. The associated `$2C` selector often progresses `0→1→2→3`; a held Start can keep `$2C=0`. This finite synthetic branch search is **not** proof `$0C/$0D` are impossible in real gameplay.

The ROM-locked guard at fixed `$F6AE` is `A5 1F 05 2E 05 1D 05 A8 D0 2B`, i.e. `LDA $1F; ORA $2E; ORA $1D; ORA $A8; BNE $F6E3`. It may bypass the subsequent Start-bit (`$F8 & $10`) test when any guarded byte is nonzero. This explains a *conditional* gate, not complete stage-four liveness or a proven reason the artificial trace stays in state 04. Because original frame/NMI/PPU timing is synthetic and interrupt IRQ is omitted, do not assert a global dead end.

## Replication and promotion limits

```sh
python3 JP/tools/audit_0508_dynamic_producer_manifest.py '/path/to/Akumajou Densetsu (Japan).nes' report.json --scenarios start30:1200,abstart:300,none:300
python3 JP/tools/audit_0508_state04_controller_branch.py '/path/to/Akumajou Densetsu (Japan).nes' state04_report.json --nmis 120
```

Both tools assert the immutable JP ROM hash, exercise actual mapper-aware 6502 instructions, and generate reproducible JSON. The dynamic manifest validates the three existing instruction-count baselines (2,966,527; 647,426; 1,055,395). The branch search also asserts exact ROM bytes of `$F6AE` and `$E551` and a stack-stable fork anchor.

**Do not credit the newly observed 11,127 instruction/operand bytes as verified progress**: most of the path is under manually scheduled NMIs, fake `$2002` readiness and an input bus model without a cycle-correct PPU or mapper IRQ. It also overlaps older 49,404-byte admitted coverage, and no authoritative physical byte ledger subtraction or hardware trace was performed. VPP remains **24/100**; strict PRG floor **49,404/262,144 = 18.8461%**, fixed PRG31 frontier `$FB96`, completed recovery checkpoint **0507**. R-001, R-002 and R-006 remain OPEN.

**Next large subsystem batch:** Improve reference-timed CPU/PPU/NMI/IRQ behavior or obtain a recorded original emulator trace, join the actual $18=$0C/$19=$13 producer to the room graph (or refute it in a bounded scenario), and then reconcile mapped bank-$0A/$0E dependency bytes with the strict manifest. Preserve all newly generated evidence in Git; never commit original ROM bytes or lossless PRG listings.
