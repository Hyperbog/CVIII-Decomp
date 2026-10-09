# CVIII JP — Checkpoint 0508 / Phase 2 — ROM-backed conditional state evidence

**Status: PROVISIONAL / NOT COMMITTED.** Source is `Akumajou Densetsu (Japan).nes` SHA-256 `958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28`. The exact independent audit is [`audit_0508_phase2.py`](audit_0508_phase2.py) and machine report is [`0508_phase2_report.json`](0508_phase2_report.json). These do not replace `JP/analysis/RESUME_STATE.json` (0507, `status=ready`).

## Reproducible results

- Rechecked the JP ROM header, 32-byte fixed-PRG31 overlap `$FB76–$FB95`, and the fixed frontier fingerprint `$FB96–$FBB5`.
- Rechecked NMI selector `$18=$0C` → fixed `$E51E`, `LDA #$0A; JSR $E2D0; JMP $AFA4`. The mapper helper stores bank value to both `$23` and VRC6 `$8000`. Raw-bank `$0A:$AFA4–$AFA8` (physical PRG21) exactly matches `A5 19 20 FB E7` and SHA-256 `0cbfd39d34523da29edaa6a2dcf5cdb4b62de628d0e5568ea3879d7de5a1c0c7`. This is a **five-byte candidate for strict promotion** following normal ledger/commit audit. The `$18=$0D` → `$E526` → `$B4CC` entry from 0507 is separately reverified; its five bytes have already been counted.
- The 20 encoded pointer words at `$AFA9` contain selector `$19=$13` → `$B36B`. On this **conditional** entry, `$B36B–$B379` copies `$0789` to `$0781`, writes `$18=$0D`, resets `$19=$00` and returns. It does not prove that selector `$13` occurs at runtime.
- The `$B4CC` room dispatcher has encoded selectors `$01` → `$B58C` and `$02` → `$B597`, whose known local transition sets `$68=$00` then advances `$19`. The inner dispatcher `$B689` has encoded `$68=$00` → `$B6A4`.
- `$B6A4` calls `$B873`. That subroutine converts `$07A6` to `Y=(3*RAM[$07A6])&$FF`, compares the first byte at `$B8A6+Y` with `$FF`, and **returns carry set** on the sentinel. Nine observed 3-byte records span `$B8A6–$B8C0`; `$B8C1` is `$FF`. The direct test proves `$07A6=$09` takes the sentinel branch; it does **not** prove an invariant restricting `$07A6` to 0–9. Only after carry set can `$B6A4` proceed through `$E785` and call `$B7F7`.
- On a **nonsentinel** `$B873` path, `$B88D` executes `STA $10` from the descriptor's third byte and the later loop at `$B898` executes `DEC $10` until the conditional branch stops. A fixed call to `$E86B` follows. This is an additional **candidate provenance/writer path for ZP `$10`**, and no final renderer-facing `$10` value or cross-frame ordering is claimed.
- A byte-start scan of **all 262,144 PRG bytes** for *direct absolute* store/RMW encodings to `$07A6` finds three candidates, all in physical PRG21: `$B628` (`STA`), `$B7E0` (`STA`), `$B89F` (`INC`). This is *not* a whole-program producer closure: false-positive instruction starts, indexed or indirect aliases, interrupt and callee effects require follow-up. Three direct `$07A0` encodings are also indexed, with no asserted reachability.
- The four raw-$0A `JSR $E7FB` inline dispatch sites at `$AFA6`, `$B122`, `$B4CE`, `$B68B` were checked for **262,144 selector/saved-Y input pairs** (four sites × 256 × 256), verifying mapped pointer reads, 8-bit ASL selector `$80` aliasing, carry, and final restored-Y Z/N properties. These are tests of a partial address/flag formula, **not** original 6502 stack, cycle, instruction-trace, frame, or native game parity.

## Exact scope / blockers

The independently reproduced 0507 graph was **281 starts / 582 instruction-and-operand bytes**. The earlier 0508 expanded bank sweep classified **935 starts / 2,042 candidate code bytes**, but mapper-state, live `$18/$19/$68` domains and external return paths remain open. The expansion stays **structural only**. In particular, no dispatcher pointer-table width proves a value bound; an out-of-width index can read overlapping code bytes.

The recovered fixed PRG31 raw frontier remains `$FB96`. `$FB96–$FBF5`, `$FC17–$FC1E`, `$FAA0–$FAA9` and the other three existing fixed gaps remain unclaimed. `$B7F7`'s eleven JSRs to fixed `$FB96` and `$B8C2,Y` pointer sources require bank/producer proof. Exhaustive native 0507 regression, complete repository recovery checker, audit preservation archive, and state transaction have **not** been executed against the full repository checkout.

**Accounting:** 5 bytes identified as eligible for further strict promotion, **0 bytes committed**. Official strict floor **49,404 / 262,144 = 18.8461%**, **VPP 24/100**. The 8–16 KiB strict-new-byte target is not met by this evidence.

## Reproduction

```sh
python3 audit_0508_phase2.py 'Akumajou Densetsu (Japan).nes' 0508_phase2_report.json
python3 audit_0508_expanded.py 'Akumajou Densetsu (Japan).nes' 0508_expanded_report.json
```

To make the checkpoint authoritative: place the phase-2 audit and updated 0508 analysis under `JP/`, reproduce `tools/check_resume_frontier.py` and previous `audit_nmi_room_dispatch_0507.py` and `room_state_dispatch_test.cpp`; reconcile byte overlaps and mapped callees; update the affected preservation chapters and discovery log; run `audit_preservation_archive.py`; update progress and continuity; write `RESUME_STATE.json` **last**; validate and verify the branch head before reporting completion.

## Corrected E7FB 8-bit second-INY wrap (0508 bulk trace erratum)

The original ROM's `$E7FB` uses **8-bit Y** for both indirect pointer bytes. For selector `$7F` / `$FF`, the first fetch is at `JSR-return+$FF` and the second `INY` wraps to 0, reading the **last operand byte of `JSR $E7FB`**. The earlier partial `pointer_entry+1` model in this phase and in native `room_state_dispatch.hpp` was wrong at those two selector values. The correct raw-$0A:$B4CE dispatch target is `$E7FB`, not `$20FB`; neither selector is live-proved. The partial model and full-256 native regression are corrected separately. See [bulk trace and C-003 correction](0508_TRACE_CORE_AND_E7FB_CORRECTION.md).
