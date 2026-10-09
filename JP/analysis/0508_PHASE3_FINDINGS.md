# CVIII JP — 0508 / Phase 3: Room descriptor execution and NMI predecessor

**Status: PROVISIONAL — no GitHub commit or strict-coverage promotion.** The Japanese ROM is the authority (SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`). Reproduce with `audit_0508_phase3.py` and the same ROM. This document supplements, not replaces, the committed 0507 resume state and the 0508 Phase 1/2 discovery records.

## New exact bounded execution evidence

The raw VRC6 bank `$0A` routine `$B873–$B8A5` is followed under explicit starting conditions `$07A6=00..09`, unrestricted eight-bit `$1E` (buffer index), and incoming ZP `$10` tested at `00/01/FF`. The test interprets the actual JP opcode stream, with mapped CPU reads from raw bank `$0A` (PRG20–21) and fixed PRG31; it follows nested calls through fixed `$E843`, `$E86B` and `$EC70`. Flags, A/X/Y, zero-page/CPU RAM writes, branching, calls and returns on this path are checked. It is **not** a full CPU stack, cycle, PPU, mapper-interrupt, or game-frame emulator.

| Initial `$07A6` | Record source | Effect on `$10` | CPU buffer output | Result |
|---|---|---|---|---|
| `$00–$08` | Nine physical triples `$B8A6–$B8C0`, each third byte `$40` | `$B88D` writes `$40`, `$B898` decrements 64 times, leaving `$00` | 68 writes: `$01`, address low, address high, 64 zero bytes, `$FF`; wrap at eight-bit X is preserved | C=0, `$07A6` increments, `$1E += 68 (mod 256)` |
| `$09` | `$B8C1 = FF` sentinel | no `$10` write; inherited value preserved | no writes | C=1, `$07A6` and `$1E` unchanged |

**7,680 cases passed** = 10 descriptor indices × 256 initial X values × 3 inherited `$10` values. Every output byte write and register/memory postcondition is asserted. Because a nonzero `INC/DEC` loop is interpreted, this verifies both wraparound of X and exact repeated zero-page stores. There is no claim about intervening IRQ writes or frame-state liveness.

## Essential negative bound result

The actual expression `Y = (3 * RAM[$07A6]) & FF` maps **every** eight-bit input to one of 256 distinct source bytes at `$B8A6–$B9A5`. These physical bytes include other code/tables. There are **15** input indices for which the indexed first byte happens to equal `$FF`: `09,1C,2A,2C,2D,2E,30,36,80,84,8D,D4,D6,DA,FB`. These are **not 15 legitimate game records**: they demonstrate why the observed 9+1 descriptor sequence is *not* a proof that live `$07A6` is bounded to `00–09`. A future proof must close actual `$07A6` producers and aliases, or obtain a bounded reference trace.

## Cross-frame NMI candidate continuation

The ROM independently confirms the conditional sequence:

```text
incoming $18=$0C -> fixed $E51E -> VRC6 bank $0A:$AFA4
$19=$13 at $AFA4 -> E7FB pointer $B36B
$B36B -> write $18=$0D; $19=$00
next NMI, if unchanged -> fixed $E526 -> bank $0A:$B4CC
$19=$00 at $B4CC -> E7FB pointer $B570
```

At `$B570` external fixed calls precede `INC $19`; proving their mutation/banking/return behavior and first-level selector liveness is still required. This establishes pointer and source-byte consistency, **not** real execution of `$18=$0C,$19=$13` or absence of cross-frame modification. `$AFA4–$AFA8` is a separate mapped five-byte entry candidate for strict promotion, but it has not been reconciled with the full ledger or committed.

## Coverage and recovery

- **Previously committed baseline:** 49,404 / 262,144 strict PRG bytes = 18.8461%, VPP 24/100, last completed 0507.
- **Phase 3 strict new bytes:** **0 committed**. The mapped five-byte predecessor remains eligible for ledger review, not counted.
- **Fixed PRG31 investigation frontier:** `$FB96`; all six named fixed-bank gaps remain unclaimed.
- **Still open:** full `$18/$19/$68/$07A6` producer domains, first-level dispatcher liveness, bank-return contracts for external callees, `$B8C2,Y` pointer-index bound, full frame-last-writer of `$10` before PRG26 renderer, and full original CPU/PPU/VRC6 trace parity.
- **Before a repository checkpoint:** replay full 0507 native test and checkpoint ROM audit; run `check_resume_frontier.py` in a complete checkout; reconcile strict manifests and recorded hashes; update `JP/PreservationArchive` relevant chapters plus `DISCOVERY_LOG.md`, pass archive audit, update progress/continuity, write `RESUME_STATE.json` last, and verify branch head. This provisional evidence alone must not be marked as 0508 complete.

## Reproduction

```sh
python3 audit_0508_phase3.py 'Akumajou Densetsu (Japan).nes' 0508_phase3_report.json
python3 audit_0508_phase2.py 'Akumajou Densetsu (Japan).nes' 0508_phase2_report.json
python3 audit_0508_expanded.py 'Akumajou Densetsu (Japan).nes' 0508_expanded_report.json
```

Interpreter limitation: only opcodes encountered on the explicitly declared path are implemented; unsupported opcode/address access causes a hard failure. The ROM hash and the exact executed ROM instruction regions are asserted before testing.