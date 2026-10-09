# Checkpoint 0508 — 32 KiB bulk raw-bank $0A/$0E provenance and reset-clear audit

**Status: PROVISIONAL, 2026-10-09.** This is a bulk two-bank discovery/physical-byte manifest and a bounded original-ROM reset-loop execution witness, **not a completed semantic checkpoint, native emulator trace, or extra 2,505 verified ROM bytes**. Source: supplied JP Akumajou Densetsu, iNES mapper 24 (VRC6a), 393,232 bytes; SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`.

## Physical scope and reproducibility

- Full raw PRG bank **$0A**, physical PRG20/21, 16,384 bytes; SHA-256 `1460df577d44e114c64fdf34a8837629765f3f6a93d45796fdf81e5ffacb5ed8`.
- Full raw PRG bank **$0E**, physical PRG28/29, 16,384 bytes; SHA-256 `9fc30168f3eca751de893aac2af31b5f4c40b8dcdcde1ad70b9614c607c29bb5`.
- Additional **256 KiB physical PRG** all-offset direct-RAM-write encoding sweep. Complete fixed-bank PRG31 `$FB76–FB95` overlap SHA `e4fa5e06e439ca12a84d935eb80224f448276c722399fe76fe0ce60013cc4ee7`; `$FB96–FBB5` frontier SHA `a5437f0f20034ba34d65afeec353d28846a321134061f765814d28eaa3f69157`.
- Replay the previously committed `audit_0508_expanded.py` and `audit_0508_phase5.py` to preserve their original 281/582 predecessor and 1,280 5-stream/30-object mapped-bus regressions; do not redissect known roots as newly covered territory.

To replay: `python3 JP/tools/audit_0508_bulk_0a0e.py "Akumajou Densetsu (Japan).nes" JP/analysis/0508_bulk_0a0e_report.json`. The tool depends only on earlier committed 0508 audit modules. The report is deterministic.

## Explicit bank-domain byte ledger

| Domain | Physical bank(s) | Code/data class | Unique bytes | Coverage status |
|---|---:|---|---:|---|
| Previously audited scheduler from raw $0A:$84EA | PRG20 | 57 starts, 120 operand bytes; indirect exit at $8520 | 120 | **Already credited by 0501; never count again** |
| Two fixed-mapped NMI entry roots plus conditional inline handler graph | PRG21 | 935 official instruction starts / 2,042 byte-complete code+operands | 2,042 | **Conditional**; selector liveness, banked callees not closed |
| Four `JSR $E7FB` inline dispatch tables | PRG21 | 65 encoded pointers x 2 bytes | 130 | **Conditional table data**; table width is not a proven selector bound |
| Nine 3-byte descriptors plus `$B8C1:$FF` terminator | PRG21 | 27 descriptor bytes + 1 sentinel | 28 | **Conditional resource data** |
| Five `$B8C2–B8CB` room-index source pointers | PRG21 | Five little-endian words | 10 | **Conditionally bounded input** `$07A0=0..4` only |
| Five room object streams in raw $0E:$BE8B–BF39 | PRG29 | 4-byte headers + 30 five-byte objects + five $FF endings | 175 | **Conditional mapper-read data** |
| **All distinct classified bytes** | PRG20/21/29 | Prior admitted and candidate combined | **2,505** | **0 new strict bytes this batch** |

All tagged intervals have explicit physical identities and asserted disjointness. Only **120** of these 2,505 are specifically confirmed previously credited by the 0501 scheduler. The other **2,385** are candidate classifications, not an assertion they are all fresh/uncovered versus the whole committed ledger. The graph in PRG21 must not be reclassified as live from table shape or partial CPU tests.

## Whole-PRG writer candidate counts

The all-offset scanner inventories **direct, non-indexed encoded write/RMW patterns** to shared room RAM. It rejects encodings that would cross an 8 KiB physical-bank boundary and does not claim arbitrary start offsets represent instructions:

| Watched RAM | Encoded starts across PRG | Explicitly bounded absolute sites |
|---|---:|---|
| `$18` | 75 | Multiple physical banks; many starts are table/operand data |
| `$19` | 113 | Multiple physical banks |
| `$68` | 105 | Multiple physical banks |
| `$07A0` | **3** | PRG01:$A09B STA, PRG03:$BB5E STA, PRG21:$B7E3 INC |
| `$07A6` | **3** | PRG21:$B628 STA, $B7E0 STA, $B89F INC |

Zero-page indexed writes (`STA $xx,X`), indirect writes, absolute-index aliases, stack side effects, and any live effect from separately mapped copies are **outside** this count. The restricted census does not prove absence of other writes. Bank $01:$BB5E has a candidate producer outside the five loader indices, so the five pointer entries do not imply a global `$07A0≤4` invariant.

## New bounded original RESET code execution

Fixed RESET `$E00B` waits on `$2002` for VBlank. After `$E017: LDX #$FF; TXS`, the two fixed helpers `$E16C` and `$E151` do not change X; the original instructions `$E020–E034` zero memory through `STA ($00),Y` and loop `$0000–$07FF` in eight pages. Under that **entry precondition**, 32 distinct initial RAM seeds were fully stepped through the 6502 loop:

- 6,174 original instructions per seed, **197,568** total; exactly **2,048** zero-valued indirect stores per seed, **65,536** total.
- The RAM region `$0002–07FF` is zero at the cutpoint. Zero page `$00/$01` ends as `00 08`, because it is a working pointer, not a persistent zero.
- In particular **`$18=$19=$68=$07A0=$07A6=$00`** after the loop, independent of the incoming RAM seed.
- This is a substantial initial-producer fact not supplied by eleven conditional room-state tests. It does **not** prove PPU/VBlank timing, how any later handler progresses from `$18=0` to `$18=$0C`, or frame-level liveness. The remainder of RESET and intervening NMI must be traced.

The ROM's fixed `$E551–E557` routine is `INC $18; LDA #$00; STA $19; RTS`. Therefore a **conditional** incoming `$18=$0B` becomes `$18=$0C,$19=0`, but this does not prove the `$0B` state is actually reached. The entire 256 KiB PRG has **zero raw exact matches** for `A9 0C 85 18` and `A9 0C 8D 18 00`. This only rules out those exact contiguous immediate-store encodings, **not** a table-derived or calculated source of `$18=0C`.

## Progress and next bulk proof

- Strict newly promoted unique PRG: **0**. Cumulative authoritative **49,404 / 262,144 = 18.8461%**, VPP **24/100**.
- Last completed recovery checkpoint remains **0507**; fixed PRG31 `$FB96` remains first unprocessed tail byte, with prior holes unclaimed. Bulk discovery does not itself earn PRG or VPP credit.
- Next batch should attach a repeatable reset-to-first-NMI and subsequent NMI/IRQ trace (2A03/VRC6a memory-bus/PPU) to the **entire graph**, then close source predicates for `$18:0→0C→0D`, `$19` state 0–19, `$68`, `$07A0/$07A6`, and `$B6A4` carry before promotion. Reuse earlier bank-$0E data-parser and sound-call return tests.
- Do not commit the raw ROM, disassemblies of all 16 KiB, or lossless data dumps. Commit the tool, compact report and this evidence note; keep RESUME_STATE at 0507 until a completed reconciled checkpoint.
