# CVIII JP — Checkpoint 0508 Phase 8: bounded room-state-zero RAM initialization

**Status:** PROVISIONAL ROM-backed local instruction execution. **Not** a reset-to-NMI live-state proof, completed checkpoint, or strict coverage promotion. Japanese source NES SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`; mapper 24 / VRC6a. Original ROM bytes control the conclusions.

## Newly resolved conditional initialization

Phase 7 establishes the conditional two-dispatch transition `fixed $E51E -> raw $0A:$AFA4 -> $B36B`, writing `$18=$0D`, `$19=0`, `$0781=$0789`; the subsequent fixed `$E526 -> raw $0A:$B4CC` dispatch at state `$19=0` selects raw bank `$0A:$B570`. **The current phase begins only at that `$B570` entry, conditional on that initial state and mapper setting.** It does not derive the initial `$18=$0C/$19=$13` from RESET or prove an uninterrupted frame.

Original code:

```asm
B570  JSR $E2C4            ; fixed: LDA #$1E; STA $C000; RTS
B573  JSR $E616            ; $21=$20; $6A/$43/$40/$6F=0
B576  LDA $21
B578  STA $B003            ; record bus write, do not infer larger audio/mapper state
B57B  LDA $0781
B57E  PHA
B57F  JSR $E7B6            ; bulk RAM clear
B582  PLA
B583  STA $0781            ; restore original room field
B586  JSR $EB82            ; **audit stops before this call body**
```

Fixed `$E7B6-$E7FA` uses bounded indexed loops and is covered by earlier fixed-bank instruction evidence. Its distinct RAM write ranges are shown below as half-open CPU addresses:

| RAM interval | Bytes | Mechanism |
|---|---:|---|
| `$004D-$00DF` | 147 | `STA $00,X`, X=$4D..$DF |
| `$00F0-$00F7` | 8 | `STA $F0,X`, X=$00..$07 |
| `$0300-$03BF` | 192 | `STA $0300,X`, X=$00..$BF |
| `$0400-$04FF` | 256 | `STA $0400,X`, X=$00..$FF |
| `$0500-$05FF` | 256 | `STA $0500,X`, X=$00..$FF |
| `$0600-$069F` | 160 | `STA $0600,X`, X=$00..$9F |
| `$06E0-$06FF` | 32 | `STA $0600,X`, X=$E0..$FF |
| `$0700-$07F5` | 246 | `STA $0700,X`, X=$00..$F5 |
| **Total** | **1297** | Distinct zero-valued RAM writes inside `$E7B6` |

**Important exception:** `$0781` lies in the last interval. The caller saves it on the 6502 stack and restores it after the bulk clear; `$0781` is **not** zero at the end of this prefix unless it was zero on entry. `$0789`, `$07A0`, `$07A6` and `$68` are zero at the audit stop. `$07F6` is outside the clear loop, and `$06A0` and `$03C0` are preserved; ROM-locked boundary assertions detect off-by-one decoding. `$18=$0D`, `$19=0` and tracked bank byte `$23=$0A` remain unchanged. Other fixed routines `$E616/$E2C4` have their explicit side effects; `$E2C4` writes `$C000=$1E`, and the caller writes `$B003=$20`. The partial CPU models those as ordered bus events without claiming cycle-accurate PPU/audio behavior.

## Reproducible bounded execution

Run:

```sh
python3 JP/decomp/tools/audit_0508_phase8.py '/path/to/Akumajou Densetsu (Japan).nes' 0508_phase8_report.json
```

`JP/decomp/tools/audit_0508_phase8.py` verifies the complete JP image and exact instruction bytes at `$B570`, `$E2C4`, `$E616`, and `$E7B6`; implements ROM-fetched 2A03-compatible conditional 6502 stack, branch, zero-page-wrap and indexed writes; halts *after the JSR at `$B586` transfers to `$EB82` but before executing `$EB82`*. It hard-fails if an unsupported opcode or unknown bus write occurs, if stack return bytes are wrong, if specified clearing bounds change, or if room state/mapper history diverges.

**768 cases** (256 seeds × three incoming `$0781` variants), each 3,937 executed instructions. The original `$0781` is restored in all cases; checks cover each of 1,297 individually cleared addresses and three excluded boundary witnesses. Every case records `$C000=$1E` then `$B003=$20`, and halts at `$EB82` with the parent and `$B588` continuation return addresses correctly stacked.

Previous 0508 predecessor, expanded, Phase 2, 3, 4, 5, 6 and 7 ROM audits were also rerun successfully before publication. **The 768 tests are partial CPU execution, not original/reference-emulator trace parity.**

## Proof boundaries and next research

- **R-001 OPEN:** State-zero entry is only conditionally established through Phase 7, which itself assumes `$18=$0C/$19=$13` is live. No whole-reset producer and no complete intervening NMI/IRQ/frame trace.
- **R-002 OPEN but narrowed:** This explicitly initializes `$07A0` and `$07A6` to zero on the selected branch. All subsequent writers and their ordering must still be reconciled, including external fixed `$EB82`, alternate bank-$01 `$BB57`, and the room progression `$B7DE`. Never treat `$07A0=00..04` as a global bound merely from this initialization or a five-word pointer table.
- **R-004 OPEN:** Scratch `$10` is included in `$E7B6`'s `$4D..$DF` clear? **No**: `$10` is below that span and is not written by `$E7B6` itself. This audit does not close the renderer last-writer provenance.
- `$EB82` is not executed, so no claim about that routine's modifications, indirect ROM reads, register state or later `$B589 INC $19` is made.
- Neither `$B570-$B588` nor newly interpreted room-loader bytes are credited to strict semantic coverage in this **research** phase. **New strict PRG bytes: zero; cumulative 49,404 / 262,144 (18.8461%); VPP 24/100; fixed PRG31 frontier `$FB96`; machine recovery checkpoint remains 0507**. The 8–16 KiB new-byte ambition is not met.

Keep this audit/report and prose in Git; do not commit the ROM, generated lossless bank listing, or temporary emulator dumps.