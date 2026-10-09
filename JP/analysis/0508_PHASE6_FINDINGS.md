# CVIII JP — 0508 Phase 6: interrupt-side preservation of room-loader inputs

**Status:** ROM-backed **bounded static IRQ-graph proof**, not a completed 0508 checkpoint or live room-trace certificate. Target is the supplied JP NES image (393,232 bytes, SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`). No new strict PRG bytes, VPP points, or frontier movement are claimed.

## Question and result

Can an ordinary IRQ in the already-proven 04F2 handler state domain overwrite `$FB96`'s ZP `$08/$09` source pointer, `$07A0/$07A6` room indices, `$18/$19/$68` state, `$10` shared scratch, `$54`, or the tracked PRG-bank byte `$23`?

**ROM-backed answer for this exact admitted IRQ domain: no.** Raw VRC6 bank `$01` maps physical PRG02/03 at `$8000-$BFFF` during the IRQ. All 45 encoded IRQ table slots lead to the 38 unique 04F2 handler roots or common fixed exit `$E118`. The independent 0508 audit decodes 558 unique handler instruction starts, 138 write/RMW instructions, 23 local helper starts and 49 fixed helper starts. All identified indirect/indexed **write** forms that could reach those watched RAM bytes are ruled out; two `STA $0789,X` sites have bounded X domains.

| Original JP CPU address | Producer / effect | Scope |
|---|---|---|
| Fixed PRG31 `$E100-$E104` | `LDA #$01; JSR $E2D2` writes `$8000` **without modifying** RAM `$23` | IRQ entry, bank $01 |
| Fixed PRG31 `$E120-$E124` | `LDA $23; JSR $E2D0`: restores PRG bank from tracked byte | IRQ common exit |
| PRG03 `$A323-$A32D` | `LDX #$02`, then `STA $0789,X`, decrement to zero | X=$02,$01,$00; writes `$078B-$0789` |
| PRG03 `$A4A0-$A4AA` | `LDX #$07`, then `STA $0789,X`, decrement to zero | X=$07..$00; writes `$0790-$0789` |
| PRG02 `$9F5B-$9F8A` | Local IRQ helper touches `$0780/$0781`, ZP `$00/$01/$3D` | Includes `$9F87` wrap branch; table begins `$9F8B` |
| Fixed PRG31 `$E2FA-$E35B` | IRQ external helper closure changes CHR/PPU mapper registers, not listed room RAM | No indexed RAM writers |

The IRQ prologue `$E0F5-$E0FF` saves A/X/Y and ZP `$00/$01`; the common exit `$E125-$E130` restores the saved values before RTI. In particular, an IRQ in the **temporarily selected bank `$0E`** portion of the `$FB96` helper restores bank `$0E` (as tracked by `$23`) before resuming the interrupted instructions. If interrupted when `$23=$0A`, it restores `$0A`. This is a **conditional compositional interrupt invariant**, not a cycle-timed emulator trace.

## Critical control-flow boundaries

- At PRG03 `$A302-$A309`, `AND #$03` establishes Z for a BEQ/BNE pair. The two branches exhaust the flag cases; raw `$A30A-$A30F` are inline data and are **not traversed as instructions**.
- The local helper `$9F5B` branches to `$9F87` when its `$FF` cursor sentinel is encountered. `$9F87: LDY #$01` forces `$9F89: BNE $9F7B`; the apparent `$9F8B` fallthrough is **data**, not code. Both positive and negative branch paths were accounted for.
- `$A328` and `$A4A5` are the only two indexed handler **write** sites. Their ROM-local loop bounds exclude `$07A0` and `$07A6`, despite a naïve `base + any X` calculation giving possible aliases.

## Limits and follow-up

1. This reuses the proven 04F2 `$6A` dispatch domain and its 38 handler roots; it does not prove arbitrary bit-pattern selectors (including out-of-domain states) are impossible or that NMI cannot occur during an IRQ.
2. The IRQ-side preservation does not resolve **R-001** (`$18/$19/$68` gameplay liveness), **R-002** (which `$07A0` producers feed the room loader), or **R-004** (the last pre-render `$10` writer). The raw bank-$01 routine `$BB57` may write `$07A0` under its *own* call conditions and is **not** an admitted IRQ handler root merely because IRQ also maps bank `$01`.
3. No full 6502 timing, PPU/APU trace, DMA contention, nested interrupts, native full-frame parity, or live room-index upper bound was claimed.
4. This audit reuses previously counted 04F2 PRG bytes, plus previously known fixed code. **Strict newly promoted PRG bytes: zero; cumulative 49,404/262,144 (18.8461%); VPP 24/100; checkpoint 0507 remains machine-resume state; PRG31 frontier `$FB96`.**

## Reproduction

```sh
python3 JP/tools/audit_0508_phase6.py 'Akumajou Densetsu (Japan).nes' 0508_phase6_report.json
```

The audit first verifies the exact immutable whole-ROM hash and the prior IRQ handler span hash, then reconstructs the handler/helper CFGs and addresses every write. It makes no assumption that all ROM bytes decode to executable instructions. A local replay of the six prior Phase 1–5 audits and the 65,536-case native 0507 room-state test also passed before publishing this finding; this does not represent the repository's complete recovery/preservation test suite.
