# CVIII JP — checkpoint 0508, Phase 5: complete conditional room-data streams and banked return

**Status:** ROM-verified **conditional local execution**, provisional checkpoint (not committed). This does not advance the strict semantic PRG ledger. Source: `Akumajou Densetsu (Japan).nes`, SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`, mapper 24 (VRC6a).

## Recovery and regression

The original JP-ROM file hash, fixed PRG31 `$FB76–$FB95` overlap hash `e4fa5e06e439ca12a84d935eb80224f448276c722399fe76fe0ce60013cc4ee7`, and fixed `$FB96–$FBB5` frontier hash `a5437f0f20034ba34d65afeec353d28846a321134061f765814d28eaa3f69157` match the committed 0507 recovery state. The five available provisional 0508 Python audits and the locally reconstructed/rebuilt equivalent of the 0507 native room-dispatch test pass. This is **not** a claim that the repository's complete original recovery/archive audit suite was run.

## Physical ROM mapping and bounded machine sequence

Given raw VRC6 bank `$0A` at CPU `$8000–$BFFF` and a room index `$07A0` in `$00–$04`:

1. Raw `$0A:$B7F7–$B872` fetches a little-endian pointer from `$B8C2 + ((2*$07A0)&$FF)`, stores it in ZP `$08/$09`, and initializes object slot X=1.
2. Each `JSR $FB96` enters fixed PRG31 (`$FB96–$FBA4`), loads raw bank `$0E` through fixed `$E2D0` (write both ZP `$23` and VRC6 `$8000`), performs an actual `LDA ($08),Y`, saves the byte, restores raw bank `$0A` through `$E2D0`, restores A, and returns. 6502 stack push/pop/JSR/RTS are modeled, not merely an address formula.
3. `$B7F7` parses four header bytes: byte0 high/low nibbles into `$34/$35`, byte1 high/low nibbles into `$36/$54` (and bit0 into `$72`), byte2 into `$07A1`, and byte3 into `$054E`.
4. Starting at stream offset 4, each five-byte object record is copied into `$048C,X`, `$0400,X`, `$0438,X`, `$041C,X`, `$04A8,X`, and the corresponding `$054E,X` is set to 1. X increments per record. A single `$FF` record-marker byte ends the loop. The final comparison gives C=1, Z=1, N=0.

Pointer source: raw `$0A` / physical PRG21, CPU `$B8C2–$B8CB` (10 bytes, SHA-256 `38adbfe530adae4b238ccb265162d91938bb0f2010d6d35b1564fa44ed98c3f3`). Actual data source: raw `$0E` / physical PRG29, CPU `$BE8B–$BF39` (175 bytes, SHA-256 `977745b341cfa56056be96e454d2e49e5d91084b798e82b1a1e819dcfcdab479`). The five streams are contiguous and nonoverlapping **in physical ROM**, despite the pointer ordering.

| `$07A0` | Stream CPU address (raw `$0E`) | Header bytes | Objects | Source bytes |
|---|---|---|---:|---:|
| `$00` | `$BEA4–$BEDA` | `41 20 01 01` | 10 | 55 |
| `$01` | `$BEDB–$BF02` | `11 01 00 02` | 7 | 40 |
| `$02` | `$BF03–$BF1B` | `81 03 01 03` | 4 | 25 |
| `$03` | `$BE8B–$BEA3` | `21 02 00 00` | 4 | 25 |
| `$04` | `$BF1C–$BF39` | `B1 02 00 00` | 5 | 30 |
| **Total** | `$BE8B–$BF39` | | **30** | **175** |

## Bounded execution tests

`audit_0508_phase5.py` asserts source instruction signatures against the immutable ROM, implements only the official 6502 instructions needed by this exact call sequence, and hard-fails on unmapped memory reads/writes, unsupported instructions, invalid bank values, incomplete stack returns, or long loops.

Across **5 room indices × 256 initial A/X/Y/flag configurations = 1,280 complete loader executions**, it checks all five source stream boundaries and object records; the exact six header/loop fields; the resulting object arrays and active flags; unchanged `$07A0`, `$07A6`, and ZP `$10`; restoration of `$23=$0A`, mapper bank `$0A`, and stack pointer `$FD`; and the final sentinel flags.

Aggregate totals: **47,360** actual mapped indirect data reads from raw bank `$0E`, paired with **94,720** mapper `$8000` writes ($0E then $0A). A helper invocation is counted *every time* the loader loop executes its call sites; it is not confused with the **11 distinct static JSR $FB96 sites** in the ROM.

## Proof limits and outstanding research

- **R-001:** No producer or frame trace yet proves `$18=$0D` or `$19` selected state executes from reset. The predecessor `$18=$0C` and `$19=$13` are conditional.
- **R-002:** The complete **five-input conditional parser** is now tested, but the `$07A0` *global live input range* is not proved. In particular, raw bank `$01:$BB57` can load values over four into `$07A0`; no clamp is justified. Other raw `$0E` bytes outside the five streams are not classified by this audit.
- **R-004:** The `$B7F7` bounded execution itself preserves incoming ZP `$10`. This does not prove the frame's final shared `$10` writer, nor does it rule out IRQ interleaving during temporary bank `$0E` selection.
- **Other:** CPU cycle count, interrupts, PPU/APU side effects, game-frame reachability, and a complete native reset-to-render trace have not been executed or certified. Data-stream parsing under *conditional inputs* does not justify adding 175 strict semantic PRG bytes under the project's producer-domain policy.

**Accounting:** zero newly promoted bytes in phase 5. The authoritative last committed checkpoint is **0507**; strict PRG lower bound **49,404/262,144 = 18.8461%**, VPP **24/100**, PRG31 raw fixed frontier `$FB96`. No GitHub modifications and no change to `JP/analysis/RESUME_STATE.json`.

## Reproduce

```sh
python3 audit_0508_phase5.py 'Akumajou Densetsu (Japan).nes' 0508_phase5_report.json
```

Next: trace actual producer→dispatch liveness of `$07A0` and `$18/$19`, plus IRQ bank preservation before deciding if fixed `$FB96` and the 175-byte raw-bank `$0E` structure meet strict promotion requirements. Then replay the complete committed 0507 audit suite, recovery checker and preservation archive audit before a checkpoint-0508 GitHub state transaction.